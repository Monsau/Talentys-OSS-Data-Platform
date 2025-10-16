#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour executer dbt et voir les transformations dans Dremio
"""
import os
import sys
import subprocess
import logging
import requests
import time
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DbtDremioExecutor:
    def __init__(self):
        self.dbt_dir = Path("c:/projets/dremiodbt/dbt")
        self.dremio_url = "http://localhost:9047"
        self.wsl_project_path = "/mnt/c/projets/dremiodbt"
        self.wsl_dbt_dir = f"{self.wsl_project_path}/dbt"
        
        # Find dbt executable (WSL only)
        self.dbt_cmd = self._find_dbt_command()
    
    def _run_wsl_command(self, dbt_args, timeout=120):
        """Execute a dbt command via WSL"""
        # Build WSL command: wsl -e bash -c "cd /path && source venv/bin/activate && dbt <args>"
        dbt_cmd_str = " ".join(dbt_args)
        bash_cmd = f"cd {self.wsl_dbt_dir} && source {self.wsl_project_path}/venv/bin/activate && dbt {dbt_cmd_str}"
        
        cmd = ["wsl", "-e", "bash", "-c", bash_cmd]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result
        
    def _find_dbt_command(self):
        """Find the dbt command - WSL ONLY with Linux venv"""
        # FORCE WSL with Linux venv Python
        wsl_venv_python = "wsl"
        wsl_project_path = "/mnt/c/projets/dremiodbt"
        wsl_dbt_cmd = f"{wsl_project_path}/venv/bin/python"
        
        # Test if WSL is available and venv exists
        try:
            result = subprocess.run(
                ["wsl", "test", "-f", f"{wsl_project_path}/venv/bin/python", "&&", "echo", "OK"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if "OK" in result.stdout:
                logger.info(f"[i] Using WSL with venv: {wsl_dbt_cmd}")
                # Return WSL command that will execute dbt via venv Python
                return ["wsl", "-e", "bash", "-c"]
        except Exception as e:
            logger.error(f"[X] WSL not available or venv not found: {e}")
        
        logger.warning("[!] dbt not found - will attempt installation in WSL")
        return None
        
    def check_dbt_installation(self):
        """Verifier que dbt est installe dans WSL"""
        if self.dbt_cmd is None:
            logger.error("[X] dbt not found - attempting installation...")
            return False
            
        try:
            result = self._run_wsl_command(["--version"], timeout=10)
            if result.returncode == 0:
                logger.info(f"[OK] dbt installed: {result.stdout.strip()}")
                return True
            else:
                logger.error("[X] dbt non installe ou non accessible")
                return False
        except FileNotFoundError:
            logger.error("[X] WSL non trouve")
            return False
        except Exception as e:
            logger.error(f"[X] Error checking dbt: {e}")
            return False
    
    def install_dbt_dremio(self):
        """Installer le plugin dbt-dremio dans WSL venv"""
        logger.info("[i] Installation du plugin dbt-dremio dans WSL...")
        try:
            # Install in WSL venv
            bash_cmd = f"cd {self.wsl_project_path} && source venv/bin/activate && pip install dbt-core dbt-dremio"
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", bash_cmd],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                logger.info("[OK] Plugin dbt-dremio installe dans WSL")
                # Re-detect dbt command after installation
                self.dbt_cmd = self._find_dbt_command()
                return True
            else:
                logger.error(f"[X] Erreur installation dbt-dremio: {result.stderr[:200]}")
                return False
        except Exception as e:
            logger.error(f"[X] Erreur installation: {e}")
            return False
    
    def test_dbt_connection(self):
        """Tester la connexion dbt vers Dremio"""
        if self.dbt_cmd is None:
            logger.error("[X] dbt command not available")
            return False
            
        logger.info("[i] Test de la connexion dbt vers Dremio...")
        try:
            result = self._run_wsl_command(["debug"], timeout=30)
            logger.info("Resultat dbt debug:")
            logger.info(result.stdout[:500])  # First 500 chars
            if result.stderr:
                logger.warning(f"Warnings: {result.stderr[:200]}")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"[X] Erreur test connexion: {e}")
            return False
    
    def run_dbt_models(self):
        """Executer les modeles dbt via WSL"""
        if self.dbt_cmd is None:
            logger.error("[X] dbt command not available")
            return False
            
        logger.info("=== EXECUTION DES MODELES DBT ===")
        try:
            # dbt deps (si necessaire)
            logger.info("[i] Installation des dependances dbt...")
            self._run_wsl_command(["deps"], timeout=30)
            
            # dbt run
            logger.info("[i] Execution des modeles dbt...")
            result = self._run_wsl_command(["run"], timeout=120)
            
            logger.info("Sortie dbt run:")
            logger.info(result.stdout[:1000])  # First 1000 chars
            
            if result.stderr:
                logger.warning(f"Erreurs/Warnings: {result.stderr[:500]}")
            
            if result.returncode == 0:
                logger.info("[OK] Modeles dbt executes avec succes")
                return True
            else:
                logger.error(f"[X] Erreur execution dbt: code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("[X] dbt run timeout (120s)")
            return False
        except Exception as e:
            logger.error(f"[X] Erreur execution dbt: {e}")
            return False
    
    def run_dbt_tests(self):
        """Executer les tests dbt via WSL"""
        if self.dbt_cmd is None:
            logger.error("[X] dbt command not available")
            return False
            
        logger.info("=== EXECUTION DES TESTS DBT ===")
        try:
            result = self._run_wsl_command(["test"], timeout=60)
            
            logger.info("Resultat des tests dbt:")
            logger.info(result.stdout[:1000])  # First 1000 chars
            
            if result.stderr:
                logger.warning(f"Erreurs/Warnings tests: {result.stderr[:500]}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("[X] dbt test timeout (60s)")
            return False
        except Exception as e:
            logger.error(f"[X] Erreur tests dbt: {e}")
            return False
    
    def check_dremio_objects(self):
        """Verifier les objets crees dans Dremio"""
        logger.info("=== VERIFICATION DES OBJETS DANS DREMIO ===")
        
        try:
            # Authentification Dremio
            auth_response = requests.post(f"{self.dremio_url}/apiv2/login", 
                                        json={"userName": "admin", "password": "admin123"},
                                        timeout=10)
            
            if auth_response.status_code != 200:
                logger.error("[X] Impossible de se connecter a Dremio")
                return False
            
            token = auth_response.json()["token"]
            headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
            
            # Verifier les espaces
            spaces_response = requests.get(f"{self.dremio_url}/apiv2/spaces", headers=headers, timeout=10)
            if spaces_response.status_code == 200:
                spaces = spaces_response.json()
                logger.info("Espaces Dremio disponibles:")
                for space in spaces.get('data', []):
                    space_name = space.get('name', 'N/A')
                    logger.info(f"   - {space_name}")
                    
                    # Essayer de lister les objets dans l'espace analytics
                    if space_name == 'analytics':
                        catalog_response = requests.get(
                            f"{self.dremio_url}/api/v3/catalog/by-path/analytics",
                            headers=headers,
                            timeout=10
                        )
                        if catalog_response.status_code == 200:
                            catalog_data = catalog_response.json()
                            children = catalog_data.get('children', [])
                            if children:
                                logger.info(f"   Objets dans {space_name}:")
                                for child in children:
                                    obj_name = child.get('path', ['N/A'])[-1] if child.get('path') else 'N/A'
                                    obj_type = child.get('type', 'N/A')
                                    logger.info(f"     - {obj_name} ({obj_type})")
            
            # Tester une requete sur un modele dbt
            test_queries = [
                "SELECT COUNT(*) as count FROM analytics.dim_customers",
                "SELECT customer_segment, COUNT(*) as count FROM analytics.dim_customers GROUP BY customer_segment"
            ]
            
            for sql in test_queries:
                try:
                    query_response = requests.post(
                        f"{self.dremio_url}/apiv2/sql",
                        headers=headers,
                        json={"sql": sql},
                        timeout=30
                    )
                    if query_response.status_code == 200:
                        result = query_response.json()
                        rows = result.get('rows', [])
                        logger.info(f"[OK] Requete reussie: {sql}")
                        logger.info(f"   Resultat: {rows[0] if rows else 'Aucun resultat'}")
                    else:
                        logger.warning(f"[!] Requete echouee: {sql}")
                except:
                    logger.warning(f"[!] Erreur requete: {sql}")
            
            return True
            
        except Exception as e:
            logger.error(f"[X] Erreur verification Dremio: {e}")
            return False
    
    def generate_dbt_docs(self):
        """Generer la documentation dbt via WSL"""
        if self.dbt_cmd is None:
            logger.error("[X] dbt command not available")
            return False
            
        logger.info("=== GENERATION DE LA DOCUMENTATION DBT ===")
        try:
            result = self._run_wsl_command(["docs", "generate"], timeout=60)
            
            if result.returncode == 0:
                logger.info("[OK] Documentation dbt generee")
                
                # Demarrer le serveur de documentation (en arriere-plan)
                logger.info("Demarrage du serveur de documentation dbt...")
                logger.info("[i] Documentation dbt disponible sur: http://localhost:8080")
                logger.info("   (Executez 'wsl -e bash -c \"cd /mnt/c/projets/dremiodbt/dbt && source ../venv/bin/activate && dbt docs serve\"' pour y acceder)")
                return True
            else:
                logger.error(f"[X] Erreur generation documentation: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("[X] dbt docs generate timeout (60s)")
            return False
        except Exception as e:
            logger.error(f"[X] Erreur generation docs: {e}")
            return False
    
    def run_complete_workflow(self):
        """Executer le workflow complet dbt + verification Dremio"""
        logger.info("[ROCKET] DEMARRAGE DU WORKFLOW DBT + DREMIO")
        
        success_steps = 0
        total_steps = 6
        
        try:
            # 1. Verifier dbt
            if self.check_dbt_installation():
                success_steps += 1
            else:
                logger.info("[i] Installation de dbt...")
                if self.install_dbt_dremio():
                    success_steps += 1
            
            # 2. Tester connexion
            if self.dbt_cmd and self.test_dbt_connection():
                success_steps += 1
            
            # 3. Executer modeles
            if self.dbt_cmd and self.run_dbt_models():
                success_steps += 1
            
            # 4. Executer tests
            if self.dbt_cmd and self.run_dbt_tests():
                success_steps += 1
            
            # 5. Verifier objets Dremio
            if self.check_dremio_objects():
                success_steps += 1
            
            # 6. Generer documentation
            if self.dbt_cmd and self.generate_dbt_docs():
                success_steps += 1
            
            logger.info(f"\n" + "="*60)
            logger.info(f"[OK] WORKFLOW TERMINE: {success_steps}/{total_steps} etapes reussies")
            logger.info("="*60)
            
            if success_steps >= 4:
                logger.info("[TARGET] DBT + DREMIO INTEGRATION OPERATIONNELLE!")
                logger.info("[CHART] Vous pouvez maintenant voir les transformations dbt dans Dremio")
                logger.info("[GLOBE] Interface Dremio: http://localhost:9047")
                logger.info("[BOOKS] Documentation dbt: Executez 'dbt docs serve' dans le dossier dbt")
                return True
            else:
                logger.warning("[!] Integration partiellement fonctionnelle")
                return False
            
        except Exception as e:
            logger.error(f"[X] ERREUR WORKFLOW: {e}")
            return False

if __name__ == "__main__":
    executor = DbtDremioExecutor()
    success = executor.run_complete_workflow()
    sys.exit(0 if success else 1)