#!/usr/bin/env python3
"""
Script pour créer des VDS Elasticsearch via des requêtes SQL dans Dremio
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

def execute_sql(token, sql):
    """Exécuter une requête SQL dans Dremio"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    payload = {"sql": sql}
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            job = response.json()
            job_id = job.get('id')
            print(f"   Job ID: {job_id}")
            
            # Attendre la fin du job
            for _ in range(30):  # Max 30 secondes
                time.sleep(1)
                status_response = requests.get(
                    f"{DREMIO_URL}/api/v3/job/{job_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    job_status = status_response.json()
                    state = job_status.get('jobState')
                    
                    if state == 'COMPLETED':
                        print("   ✅ Requête terminée avec succès")
                        return True
                    elif state in ['FAILED', 'CANCELLED']:
                        print(f"   ❌ Requête échouée: {state}")
                        return False
            
            print("   ⏱️ Timeout")
            return False
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

def check_elasticsearch_indices(token):
    """Vérifier les indices Elasticsearch disponibles"""
    print("\n🔍 Vérification des indices Elasticsearch...")
    
    sql = 'SHOW TABLES IN elasticsearch'
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            headers=headers,
            json={"sql": sql}
        )
        
        if response.status_code in [200, 201]:
            job = response.json()
            job_id = job.get('id')
            
            # Attendre et récupérer les résultats
            time.sleep(2)
            
            results_response = requests.get(
                f"{DREMIO_URL}/api/v3/job/{job_id}/results",
                headers=headers
            )
            
            if results_response.status_code == 200:
                results = results_response.json()
                rows = results.get('rows', [])
                
                if rows:
                    print(f"✅ {len(rows)} indices trouvés:")
                    for row in rows:
                        table_name = row.get('TABLE_NAME', 'Unknown')
                        print(f"   - {table_name}")
                    return [row.get('TABLE_NAME') for row in rows]
                else:
                    print("⚠️  Aucun indice trouvé")
                    return []
        else:
            print(f"⚠️  Erreur: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return []

def create_space_if_not_exists(token, space_name):
    """Créer un espace s'il n'existe pas"""
    print(f"\n📁 Vérification de l'espace '{space_name}'...")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Vérifier si l'espace existe
    try:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{space_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ L'espace '{space_name}' existe déjà")
            return True
        else:
            print(f"📊 Création de l'espace '{space_name}'...")
            
            space_config = {
                "entityType": "space",
                "name": space_name
            }
            
            create_response = requests.post(
                f"{DREMIO_URL}/api/v3/catalog",
                headers=headers,
                json=space_config
            )
            
            if create_response.status_code in [200, 201]:
                print(f"✅ Espace '{space_name}' créé")
                return True
            else:
                print(f"❌ Erreur création espace: {create_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def create_vds(token, vds_name, space_name, sql_query):
    """Créer une VDS"""
    print(f"\n📊 Création VDS '{space_name}.{vds_name}'...")
    print(f"   SQL: {sql_query[:80]}...")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    vds_config = {
        "entityType": "dataset",
        "path": [space_name, vds_name],
        "type": "VIRTUAL_DATASET",
        "sql": sql_query,
        "sqlContext": [space_name]
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=vds_config
        )
        
        if response.status_code in [200, 201]:
            print("✅ VDS créée avec succès")
            return True
        elif response.status_code == 409:
            print("⚠️  VDS existe déjà")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def main():
    print("="*70)
    print("🎯 CRÉATION DES VDS ELASTICSEARCH DANS DREMIO")
    print("="*70)
    
    try:
        # Authentification
        print("\n🔐 Authentification...")
        token = get_auth_token()
        print("✅ Authentifié")
        
        # Attendre que les indices soient scannés
        print("\n⏳ Attente du scan des indices Elasticsearch (15 secondes)...")
        time.sleep(15)
        
        # Vérifier les indices disponibles
        indices = check_elasticsearch_indices(token)
        
        # Créer l'espace 'raw' s'il n'existe pas
        create_space_if_not_exists(token, "raw")
        
        # Définir les VDS à créer
        vds_definitions = [
            {
                "name": "es_application_logs",
                "space": "raw",
                "sql": """
                    SELECT 
                        timestamp,
                        level,
                        service,
                        message,
                        user_id,
                        request_id,
                        duration_ms,
                        status_code
                    FROM elasticsearch.application_logs
                """
            },
            {
                "name": "es_user_events",
                "space": "raw",
                "sql": """
                    SELECT 
                        timestamp,
                        event_type,
                        user_id,
                        session_id,
                        page,
                        action,
                        device,
                        browser
                    FROM elasticsearch.user_events
                """
            },
            {
                "name": "es_performance_metrics",
                "space": "raw",
                "sql": """
                    SELECT 
                        timestamp,
                        metric_name,
                        service,
                        value,
                        unit,
                        host,
                        environment
                    FROM elasticsearch.performance_metrics
                """
            }
        ]
        
        # Créer les VDS
        print("\n📊 Création des VDS...")
        success_count = 0
        
        for vds_def in vds_definitions:
            if create_vds(token, vds_def["name"], vds_def["space"], vds_def["sql"]):
                success_count += 1
        
        print("\n" + "="*70)
        print("✅ CRÉATION DES VDS TERMINÉE")
        print("="*70)
        print(f"\n📊 Résumé:")
        print(f"   • Indices Elasticsearch trouvés: {len(indices)}")
        print(f"   • VDS créées avec succès: {success_count}/{len(vds_definitions)}")
        print(f"\n🌐 Vérifier dans Dremio: http://localhost:9047")
        print("   → Espaces → raw → es_application_logs, es_user_events, es_performance_metrics")
        
    except Exception as e:
        print(f"\n❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
