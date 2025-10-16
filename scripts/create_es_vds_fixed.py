#!/usr/bin/env python3
"""
Script pour créer les VDS Elasticsearch avec SQL correct
Contourne le problème du mot réservé 'timestamp'
"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

def get_auth_token():
    """Obtenir un token d'authentification"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    )
    response.raise_for_status()
    return response.json()["token"]

def get_headers(token):
    return {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }

def wait_for_indices(token):
    """Attendre que les indices ES soient visibles"""
    print("\n⏳ Attente que les indices Elasticsearch soient scannés...")
    headers = get_headers(token)
    
    for attempt in range(6):  # 6 tentatives de 10 secondes = 1 minute
        try:
            response = requests.post(
                f"{DREMIO_URL}/api/v3/sql",
                headers=headers,
                json={"sql": "SHOW TABLES IN elasticsearch"}
            )
            
            if response.status_code == 200:
                job = response.json()
                job_id = job.get('id')
                
                # Attendre les résultats
                time.sleep(2)
                
                results_response = requests.get(
                    f"{DREMIO_URL}/api/v3/job/{job_id}/results",
                    headers=headers
                )
                
                if results_response.status_code == 200:
                    results = results_response.json()
                    rows = results.get('rows', [])
                    
                    # Chercher nos 3 indices
                    found_indices = [row.get('TABLE_NAME') for row in rows]
                    target_indices = ['application_logs', 'user_events', 'performance_metrics']
                    
                    if all(idx in found_indices for idx in target_indices):
                        print(f"✅ Les 3 indices cibles trouvés : {target_indices}")
                        return True
                    else:
                        print(f"   Tentative {attempt + 1}/6 : {len([i for i in target_indices if i in found_indices])}/3 indices trouvés")
        except Exception as e:
            print(f"   Erreur tentative {attempt + 1}: {str(e)}")
        
        if attempt < 5:
            time.sleep(10)
    
    print("⚠️  Timeout : les indices ne sont pas tous visibles, on continue quand même...")
    return False

def create_vds_via_ctas(token, vds_name, vds_path, sql_query):
    """Créer une VDS en utilisant CREATE VDS AS (CTAS)"""
    print(f"\n📊 Création de {'.'.join(vds_path)}...")
    headers = get_headers(token)
    
    # Créer via CTAS
    ctas_sql = f"CREATE VDS {'.'.join(vds_path)} AS {sql_query}"
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            headers=headers,
            json={"sql": ctas_sql}
        )
        
        if response.status_code in [200, 201]:
            job = response.json()
            job_id = job.get('id')
            
            # Attendre la fin du job
            for _ in range(30):
                time.sleep(1)
                status_response = requests.get(
                    f"{DREMIO_URL}/api/v3/job/{job_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    job_status = status_response.json()
                    state = job_status.get('jobState')
                    
                    if state == 'COMPLETED':
                        print(f"   ✅ VDS créée avec succès")
                        return True
                    elif state in ['FAILED', 'CANCELLED']:
                        error_msg = job_status.get('errorMessage', 'Unknown error')
                        if 'already exists' in error_msg.lower():
                            print(f"   ℹ️  VDS existe déjà")
                            return True
                        else:
                            print(f"   ❌ Échec: {error_msg}")
                            return False
            
            print("   ⏱️  Timeout")
            return False
        else:
            error = response.json() if response.content else {}
            if 'already exists' in str(error).lower():
                print(f"   ℹ️  VDS existe déjà")
                return True
            print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        if 'already exists' in str(e).lower():
            print(f"   ℹ️  VDS existe déjà")
            return True
        print(f"   ❌ Erreur: {str(e)}")
        return False

def main():
    print("="*70)
    print("🎯 CRÉATION AUTOMATIQUE DES VDS ELASTICSEARCH")
    print("="*70)
    
    try:
        # Authentification
        print("\n🔐 Authentification Dremio...")
        token = get_auth_token()
        print("✅ Authentifié")
        
        # Attendre les indices
        indices_ready = wait_for_indices(token)
        
        # Définir les VDS avec SQL SELECT * pour éviter les problèmes de colonnes
        vds_definitions = [
            {
                "name": "es_application_logs",
                "path": ["raw", "es_application_logs"],
                "sql": """
                    SELECT * 
                    FROM elasticsearch.application_logs 
                    LIMIT 10000
                """
            },
            {
                "name": "es_user_events",
                "path": ["raw", "es_user_events"],
                "sql": """
                    SELECT * 
                    FROM elasticsearch.user_events 
                    LIMIT 10000
                """
            },
            {
                "name": "es_performance_metrics",
                "path": ["raw", "es_performance_metrics"],
                "sql": """
                    SELECT * 
                    FROM elasticsearch.performance_metrics 
                    LIMIT 10000
                """
            }
        ]
        
        # Créer les VDS
        print("\n📊 Création des VDS...")
        success_count = 0
        
        for vds_def in vds_definitions:
            if create_vds_via_ctas(token, vds_def["name"], vds_def["path"], vds_def["sql"]):
                success_count += 1
                time.sleep(2)  # Pause entre chaque création
        
        print("\n" + "="*70)
        print("✅ CRÉATION DES VDS TERMINÉE")
        print("="*70)
        print(f"\n📊 Résumé:")
        print(f"   • VDS créées/existantes: {success_count}/{len(vds_definitions)}")
        print(f"\n🌐 Vérifier dans Dremio: http://localhost:9047")
        print("   → Espaces → raw → Chercher 'es_*'")
        
        return success_count == len(vds_definitions)
        
    except Exception as e:
        print(f"\n❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
