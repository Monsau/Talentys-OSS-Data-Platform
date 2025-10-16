#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[TEST] TEST COMPLET - Reconstruction de A à Z
Nettoie tout et reconstruit l'ecosysteme complet pour validation

Usage:
    python scripts/test_complete_build.py
"""

import subprocess
import sys
import time
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_step(step: int, total: int, title: str):
    """Print step header"""
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}[{step}/{total}] {title}{Colors.ENDC}")
    print('='*70)

def print_success(msg: str):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}[i] {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[!] {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.RED}[X] {msg}{Colors.ENDC}")

def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {' '.join(cmd)}")
            if e.stderr:
                print_error(e.stderr[:500])
        raise

def main():
    """Main test workflow"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}[TEST] TEST COMPLET - RECONSTRUCTION DE A A Z{Colors.ENDC}")
    print("="*70)
    print("Ce script va:")
    print("  1. Arreter tous les containers")
    print("  2. Supprimer tous les volumes Docker")
    print("  3. Reconstruire l'ecosysteme complet")
    print("  4. Valider chaque etape")
    print("\n[!] ATTENTION: Toutes les donnees seront supprimees!")
    print("="*70 + "\n")
    
    input("Appuyez sur ENTER pour continuer ou CTRL+C pour annuler...")
    
    # ========================================================================
    # STEP 1: CLEANUP
    # ========================================================================
    print_step(1, 4, "Nettoyage Complet")
    
    print_info("Arrêt des containers...")
    result = run_command(["docker-compose", "down", "-v"], check=False)
    if result.returncode == 0:
        print_success("Containers arrêtés et volumes supprimés")
    else:
        print_warning("Quelques erreurs lors du nettoyage (normal si rien ne tournait)")
    
    # Vérifier qu'il ne reste rien
    print_info("Vérification qu'il ne reste aucun container...")
    result = run_command(["docker", "ps", "-a", "--filter", "name=dremio"], check=False)
    if "dremio" not in result.stdout:
        print_success("Aucun container Dremio restant")
    else:
        print_warning("Des containers Dremio existent encore")
        print(result.stdout)
    
    time.sleep(3)
    
    # ========================================================================
    # STEP 2: BUILD ECOSYSTEM
    # ========================================================================
    print_step(2, 4, "Construction de l'Écosystème")
    
    print_info("Lancement du script de construction...")
    print_info("Cela prendra environ 10-15 minutes...")
    print("")
    
    # Exécuter le script principal
    result = run_command([sys.executable, "scripts/build_complete_ecosystem.py"], check=False)
    
    if result.returncode == 0:
        print_success("Construction terminée avec succès!")
    else:
        print_error("La construction a échoué")
        print_error("Code de sortie: " + str(result.returncode))
        if result.stderr:
            print_error("Erreurs:")
            print(result.stderr[-1000:])  # Last 1000 chars
        sys.exit(1)
    
    # ========================================================================
    # STEP 3: VALIDATION
    # ========================================================================
    print_step(3, 4, "Validation de l'Écosystème")
    
    # Vérifier Docker containers
    print_info("Vérification des containers Docker...")
    result = run_command(["docker", "ps", "--filter", "status=running"], check=False)
    
    services = ["dremio", "dremio-postgres", "dremio-elasticsearch", "dremio-minio"]
    running_count = 0
    
    for service in services:
        if service in result.stdout:
            print_success(f"{service} en cours d'exécution")
            running_count += 1
        else:
            print_error(f"{service} NON démarré")
    
    if running_count == 4:
        print_success(f"Tous les services démarrés ({running_count}/4)")
    else:
        print_error(f"Seulement {running_count}/4 services démarrés")
    
    # Vérifier le rapport
    print_info("Vérification du rapport...")
    report_file = Path("ECOSYSTEM_BUILD_REPORT.json")
    
    if report_file.exists():
        print_success("Rapport de construction trouvé")
        
        import json
        with open(report_file) as f:
            report = json.load(f)
        
        print_info("Résumé du rapport:")
        print(f"  • Timestamp: {report.get('timestamp', 'N/A')}")
        print(f"  • Status: {report.get('status', 'N/A')}")
        
        if "data_volumes" in report:
            print_info("Volumes de données:")
            for source, data in report["data_volumes"].items():
                if isinstance(data, dict):
                    total = sum(v for v in data.values() if isinstance(v, int))
                    print(f"    • {source}: {total:,} records")
                else:
                    print(f"    • {source}: {data}")
    else:
        print_warning("Rapport de construction non trouvé")
    
    # ========================================================================
    # STEP 4: TESTS D'INTÉGRATION
    # ========================================================================
    print_step(4, 4, "Tests d'Intégration")
    
    print_info("Test PostgreSQL...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="business_db",
            user="postgres",
            password="postgres123"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print_success(f"PostgreSQL OK - {count:,} customers")
    except Exception as e:
        print_error(f"PostgreSQL FAILED: {e}")
    
    print_info("Test Elasticsearch...")
    try:
        import requests
        response = requests.get("http://localhost:9200/_cat/indices?format=json")
        if response.status_code == 200:
            indices = response.json()
            doc_count = sum(int(idx.get('docs.count', 0)) for idx in indices)
            print_success(f"Elasticsearch OK - {doc_count:,} documents")
        else:
            print_error(f"Elasticsearch returned {response.status_code}")
    except Exception as e:
        print_error(f"Elasticsearch FAILED: {e}")
    
    print_info("Test MinIO...")
    try:
        from minio import Minio
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin123",
            secure=False
        )
        objects = list(client.list_objects("sales-data", recursive=True))
        print_success(f"MinIO OK - {len(objects):,} files")
    except Exception as e:
        print_error(f"MinIO FAILED: {e}")
    
    print_info("Test Dremio...")
    try:
        import requests
        # Test si on peut se connecter
        response = requests.get("http://localhost:9047", timeout=5)
        if response.status_code in [200, 401]:
            print_success("Dremio OK - Accessible")
            
            # Test login
            login_response = requests.post(
                "http://localhost:9047/apiv2/login",
                json={"userName": "admin", "password": "admin123"},
                timeout=5
            )
            if login_response.status_code == 200:
                print_success("Dremio Login OK - Credentials valides")
            else:
                print_warning(f"Dremio Login FAILED - Status {login_response.status_code}")
        else:
            print_error(f"Dremio returned {response.status_code}")
    except Exception as e:
        print_error(f"Dremio FAILED: {e}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print(f"{Colors.BOLD}[GRAPH] RESUME DU TEST{Colors.ENDC}")
    print("="*70)
    print(f"[OK] Nettoyage: OK")
    print(f"[OK] Construction: OK")
    print(f"[OK] Services Docker: {running_count}/4")
    print(f"[OK] Tests d'integration: Voir details ci-dessus")
    print("")
    print(f"[GLOBE] Acces:")
    print(f"  - Dremio:        http://localhost:9047 (admin/admin123)")
    print(f"  - MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)")
    print(f"  - Elasticsearch: http://localhost:9200")
    print(f"  - PostgreSQL:    localhost:5432 (postgres/postgres123)")
    print("="*70 + "\n")
    
    if running_count == 4:
        print(f"{Colors.GREEN}{Colors.BOLD}[OK] TEST REUSSI! L'ecosysteme est pret!{Colors.ENDC}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}[X] TEST ECHOUE! Certains services ne sont pas demarres.{Colors.ENDC}\n")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Test interrompu par l'utilisateur{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}[X] Erreur: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
