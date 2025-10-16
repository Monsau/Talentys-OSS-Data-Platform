"""
╔════════════════════════════════════════════════════════════╗
║     ORCHESTRATION COMPLETE - DATA PLATFORM AUTO-BUILD      ║
║                                                            ║
║  Déploie l'infrastructure complète automatiquement:        ║
║  - Dremio + PostgreSQL + MinIO + Elasticsearch             ║
║  - dbt (models + tests)                                    ║
║  - Apache Superset                                         ║
║  - Synchronisation Dremio → PostgreSQL                     ║
║  - Dashboards automatiques                                 ║
╚════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

# Fix encodage Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class DataPlatformOrchestrator:
    """Orchestrateur complet de la plateforme de données"""
    
    def __init__(self, workspace_path):
        self.workspace = Path(workspace_path)
        self.venv_path = self.workspace / "venv_dremio_311"
        self.python_exe = self.venv_path / "Scripts" / "python.exe"
        self.steps_completed = []
        self.steps_failed = []
        
    def log(self, message, level="INFO"):
        """Log avec timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")
    
    def run_command(self, command, description, cwd=None, check=True):
        """Exécute une commande shell"""
        self.log(f"{description}...", "INFO")
        try:
            if isinstance(command, str):
                result = subprocess.run(
                    command, 
                    shell=True, 
                    cwd=cwd or self.workspace,
                    capture_output=True,
                    text=True,
                    check=check
                )
            else:
                result = subprocess.run(
                    command,
                    cwd=cwd or self.workspace,
                    capture_output=True,
                    text=True,
                    check=check
                )
            
            if result.returncode == 0:
                self.log(f"{description} - OK", "SUCCESS")
                return True, result.stdout
            else:
                self.log(f"{description} - FAILED: {result.stderr}", "ERROR")
                return False, result.stderr
        except Exception as e:
            self.log(f"{description} - EXCEPTION: {str(e)}", "ERROR")
            return False, str(e)
    
    def check_prerequisites(self):
        """Vérifie les prérequis"""
        self.log("Vérification des prérequis", "INFO")
        
        # Docker
        success, _ = self.run_command("docker --version", "Docker installé", check=False)
        if not success:
            self.log("Docker n'est pas installé", "ERROR")
            return False
        
        # Docker Compose
        success, _ = self.run_command("docker-compose --version", "Docker Compose installé", check=False)
        if not success:
            self.log("Docker Compose n'est pas installé", "ERROR")
            return False
        
        # Python
        success, _ = self.run_command("python --version", "Python installé", check=False)
        if not success:
            self.log("Python n'est pas installé", "ERROR")
            return False
        
        self.log("Tous les prérequis sont satisfaits", "SUCCESS")
        self.steps_completed.append("Prerequisites")
        return True
    
    def deploy_infrastructure(self):
        """Déploie l'infrastructure Docker"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 1: DÉPLOIEMENT INFRASTRUCTURE DOCKER", "INFO")
        self.log("═" * 60, "INFO")
        
        # Arrêter les conteneurs existants
        self.run_command("docker-compose down", "Arrêt des conteneurs existants", check=False)
        
        # Démarrer l'infrastructure principale
        success, _ = self.run_command(
            "docker-compose up -d",
            "Démarrage Dremio + PostgreSQL + MinIO + Elasticsearch + Superset + Airflow"
        )
        if not success:
            self.steps_failed.append("Infrastructure")
            return False
        
        # Démarrer Airbyte
        self.log("Démarrage Airbyte...", "INFO")
        success, _ = self.run_command(
            "docker-compose -f docker-compose.yml -f docker-compose-airbyte.yml up -d",
            "Lancement Airbyte (Data Integration)",
            check=False
        )
        if not success:
            self.log("Airbyte n'a pas démarré (optionnel, continuons)", "WARNING")
        
        # Attendre que les services soient prêts
        self.log("Attente du démarrage des services (60 secondes)...", "INFO")
        time.sleep(60)
        
        # Vérifier que les conteneurs tournent
        success, output = self.run_command("docker ps", "Vérification des conteneurs")
        if not success or "dremio" not in output:
            self.steps_failed.append("Infrastructure")
            return False
        
        self.steps_completed.append("Infrastructure")
        return True
    
    def deploy_superset(self):
        """Déploie Apache Superset"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 2: DÉPLOIEMENT APACHE SUPERSET", "INFO")
        self.log("═" * 60, "INFO")
        
        success, _ = self.run_command(
            "docker-compose -f docker-compose-superset.yml up -d",
            "Démarrage Apache Superset"
        )
        if not success:
            self.steps_failed.append("Superset")
            return False
        
        # Attendre que Superset soit prêt
        self.log("Attente du démarrage de Superset (30 secondes)...", "INFO")
        time.sleep(30)
        
        self.steps_completed.append("Superset")
        return True
    
    def setup_dbt_environment(self):
        """Configure l'environnement dbt"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 3: CONFIGURATION ENVIRONNEMENT DBT", "INFO")
        self.log("═" * 60, "INFO")
        
        # Vérifier si le venv existe
        if not self.venv_path.exists():
            self.log("Environnement virtuel non trouvé, création...", "WARNING")
            success, _ = self.run_command(
                "python -m venv venv_dremio_311",
                "Création du venv"
            )
            if not success:
                self.steps_failed.append("dbt Environment")
                return False
        
        # Installer les dépendances
        pip_exe = self.venv_path / "Scripts" / "pip.exe"
        success, _ = self.run_command(
            f'"{pip_exe}" install -r requirements.txt',
            "Installation des dépendances Python"
        )
        if not success:
            self.steps_failed.append("dbt Environment")
            return False
        
        self.steps_completed.append("dbt Environment")
        return True
    
    def run_dbt_models(self):
        """Exécute les modèles dbt"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 4: EXÉCUTION MODELES DBT", "INFO")
        self.log("═" * 60, "INFO")
        
        dbt_path = self.workspace / "dbt"
        dbt_exe = self.venv_path / "Scripts" / "dbt.exe"
        
        # dbt debug
        self.run_command(
            f'"{dbt_exe}" debug',
            "Vérification configuration dbt",
            cwd=dbt_path,
            check=False
        )
        
        # dbt run
        success, _ = self.run_command(
            f'"{dbt_exe}" run --select phase3_all_in_one',
            "Exécution du modèle phase3_all_in_one",
            cwd=dbt_path
        )
        if not success:
            self.steps_failed.append("dbt Models")
            return False
        
        # dbt test
        success, _ = self.run_command(
            f'"{dbt_exe}" test',
            "Exécution des tests dbt",
            cwd=dbt_path
        )
        if not success:
            self.log("Tests dbt ont échoué mais on continue", "WARNING")
        
        self.steps_completed.append("dbt Models")
        return True
    
    def sync_dremio_to_postgres(self):
        """Synchronise Dremio vers PostgreSQL"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 5: SYNCHRONISATION DREMIO → POSTGRESQL", "INFO")
        self.log("═" * 60, "INFO")
        
        script_path = self.workspace / "scripts" / "sync_dremio_realtime.py"
        
        if not script_path.exists():
            self.log("Script de sync introuvable", "ERROR")
            self.steps_failed.append("Dremio Sync")
            return False
        
        success, _ = self.run_command(
            f'"{self.python_exe}" "{script_path}"',
            "Synchronisation des données Dremio"
        )
        if not success:
            self.steps_failed.append("Dremio Sync")
            return False
        
        self.steps_completed.append("Dremio Sync")
        return True
    
    def populate_superset(self):
        """Peuple Superset avec les dashboards"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 6: CRÉATION DASHBOARDS SUPERSET", "INFO")
        self.log("═" * 60, "INFO")
        
        # Dashboard 1: PostgreSQL
        script_path = self.workspace / "scripts" / "populate_superset.py"
        if script_path.exists():
            success, _ = self.run_command(
                f'"{self.python_exe}" "{script_path}"',
                "Création Dashboard 1 (PostgreSQL)"
            )
            if not success:
                self.log("Dashboard 1 échoué mais on continue", "WARNING")
        
        # Dashboard 2: Dremio
        script_path = self.workspace / "scripts" / "rebuild_dremio_dashboard.py"
        if script_path.exists():
            success, _ = self.run_command(
                f'"{self.python_exe}" "{script_path}"',
                "Création Dashboard 2 (Dremio)"
            )
            if not success:
                self.log("Dashboard 2 échoué mais on continue", "WARNING")
        
        self.steps_completed.append("Superset Dashboards")
        return True
    
    def generate_opendata_dashboard(self):
        """Génère le dashboard Open Data HTML"""
        self.log("═" * 60, "INFO")
        self.log("ÉTAPE 7: GÉNÉRATION DASHBOARD OPEN DATA", "INFO")
        self.log("═" * 60, "INFO")
        
        script_path = self.workspace / "scripts" / "generate_opendata_dashboard.py"
        
        if not script_path.exists():
            self.log("Script Open Data introuvable, skip", "WARNING")
            return True
        
        success, _ = self.run_command(
            f'"{self.python_exe}" "{script_path}"',
            "Génération du dashboard HTML Open Data"
        )
        if not success:
            self.log("Dashboard Open Data échoué mais on continue", "WARNING")
        else:
            self.steps_completed.append("Open Data Dashboard")
        
        return True
    
    def print_summary(self):
        """Affiche le résumé final"""
        self.log("═" * 60, "INFO")
        self.log("RÉSUMÉ DU DÉPLOIEMENT", "INFO")
        self.log("═" * 60, "INFO")
        
        print("\n✅ ÉTAPES COMPLÉTÉES:")
        for step in self.steps_completed:
            print(f"   ✅ {step}")
        
        if self.steps_failed:
            print("\n❌ ÉTAPES ÉCHOUÉES:")
            for step in self.steps_failed:
                print(f"   ❌ {step}")
        
        print("\n📊 DASHBOARDS DISPONIBLES:")
        print("   • Dremio UI: http://localhost:9047 (admin/admin123)")
        print("   • Superset Dashboard 1: http://localhost:8088/superset/dashboard/1/")
        print("   • Superset Dashboard 2 (Dremio): http://localhost:8088/superset/dashboard/2/")
        print("   • Open Data HTML: file:///c:/projets/dremiodbt/opendata/dashboard.html")
        
        print("\n🔄 SYNCHRONISATION:")
        print("   • Manuel: python scripts\\sync_dremio_realtime.py")
        print("   • Auto: python scripts\\sync_dremio_realtime.py --continuous 5")
        
        print("\n📄 DOCUMENTATION:")
        print("   • SUPERSET_DREMIO_FINAL.md (guide complet)")
        print("   • PHASE3_COMPLETE_SUMMARY.md")
        
        print("\n" + "═" * 60)
        if not self.steps_failed:
            print("🎉 DÉPLOIEMENT COMPLET RÉUSSI!")
        else:
            print("⚠️ DÉPLOIEMENT PARTIEL - Vérifiez les erreurs ci-dessus")
        print("═" * 60 + "\n")
    
    def orchestrate(self):
        """Orchestre le déploiement complet"""
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║       DATA PLATFORM AUTO-BUILD ORCHESTRATION               ║
║                                                            ║
║  Déploiement automatique complet de la plateforme          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        start_time = time.time()
        
        # 0. Prérequis
        if not self.check_prerequisites():
            self.log("Prérequis non satisfaits, arrêt", "ERROR")
            return False
        
        # 1. Infrastructure Docker
        if not self.deploy_infrastructure():
            self.log("Déploiement infrastructure échoué", "ERROR")
            self.print_summary()
            return False
        
        # 2. Apache Superset
        if not self.deploy_superset():
            self.log("Déploiement Superset échoué", "ERROR")
            # Continue quand même
        
        # 3. Environnement dbt
        if not self.setup_dbt_environment():
            self.log("Configuration dbt échouée", "ERROR")
            # Continue quand même
        
        # 4. Modèles dbt
        if not self.run_dbt_models():
            self.log("Exécution dbt échouée", "ERROR")
            # Continue quand même
        
        # 5. Sync Dremio
        if not self.sync_dremio_to_postgres():
            self.log("Synchronisation Dremio échouée", "ERROR")
            # Continue quand même
        
        # 6. Dashboards Superset
        self.populate_superset()
        
        # 7. Dashboard Open Data
        self.generate_opendata_dashboard()
        
        # Résumé final
        elapsed = time.time() - start_time
        self.log(f"Temps total: {elapsed:.1f} secondes", "INFO")
        self.print_summary()
        
        return len(self.steps_failed) == 0


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Orchestration complète de la plateforme de données"
    )
    parser.add_argument(
        "--workspace",
        default=r"c:\projets\dremiodbt",
        help="Chemin vers le workspace"
    )
    parser.add_argument(
        "--skip-infrastructure",
        action="store_true",
        help="Skip le déploiement de l'infrastructure Docker"
    )
    
    args = parser.parse_args()
    
    orchestrator = DataPlatformOrchestrator(args.workspace)
    
    try:
        success = orchestrator.orchestrate()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
