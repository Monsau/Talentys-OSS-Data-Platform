#!/usr/bin/env python3
"""
Script pour forcer le rafraîchissement de la source Elasticsearch
et attendre que les indices soient visibles
"""

import requests
import time

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

def get_auth_token():
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

def get_source_id(token):
    """Obtenir l'ID de la source elasticsearch"""
    headers = get_headers(token)
    
    try:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/elasticsearch",
            headers=headers
        )
        
        if response.status_code == 200:
            source = response.json()
            return source.get('id'), source.get('tag')
        return None, None
    except Exception as e:
        print(f"Erreur: {e}")
        return None, None

def refresh_source(token, source_id):
    """Forcer le rafraîchissement des métadonnées"""
    print(f"\n🔄 Rafraîchissement forcé de la source elasticsearch...")
    headers = get_headers(token)
    
    try:
        # Option 1: Refresh metadata
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog/{source_id}/refresh",
            headers=headers,
            json={"refreshPolicy": "FULL"}
        )
        
        if response.status_code in [200, 202, 204]:
            print("   ✅ Rafraîchissement lancé")
            return True
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    return False

def promote_datasets(token):
    """Promouvoir les datasets Elasticsearch en les rendant visibles"""
    print(f"\n📊 Tentative de promotion des datasets...")
    headers = get_headers(token)
    
    indices = ['application_logs', 'user_events', 'performance_metrics']
    
    for index in indices:
        try:
            # Essayer de promouvoir le dataset
            response = requests.post(
                f"{DREMIO_URL}/api/v3/catalog",
                headers=headers,
                json={
                    "entityType": "dataset",
                    "path": ["elasticsearch", index],
                    "type": "PROMOTED"
                }
            )
            
            if response.status_code in [200, 201, 409]:
                print(f"   ✅ {index} promu ou déjà existant")
            else:
                print(f"   ⚠️  {index}: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  {index}: {e}")

def check_indices(token):
    """Vérifier si les indices sont maintenant visibles"""
    print(f"\n🔍 Vérification des indices...")
    headers = get_headers(token)
    
    try:
        # Essayer une requête SQL simple
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            headers=headers,
            json={"sql": "SELECT * FROM elasticsearch.application_logs LIMIT 1"}
        )
        
        if response.status_code == 200:
            job = response.json()
            job_id = job.get('id')
            
            # Attendre un peu
            time.sleep(3)
            
            # Vérifier le statut
            status_response = requests.get(
                f"{DREMIO_URL}/api/v3/job/{job_id}",
                headers=headers
            )
            
            if status_response.status_code == 200:
                job_status = status_response.json()
                state = job_status.get('jobState')
                
                if state == 'COMPLETED':
                    print("   ✅ Les indices sont accessibles !")
                    return True
                else:
                    print(f"   ⚠️  État: {state}")
        else:
            print(f"   ⚠️  Requête SQL échouée: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Erreur: {e}")
    
    return False

def main():
    print("="*70)
    print("🔧 RAFRAÎCHISSEMENT SOURCE ELASTICSEARCH")
    print("="*70)
    
    try:
        # Auth
        print("\n🔐 Authentification...")
        token = get_auth_token()
        print("✅ Authentifié")
        
        # Obtenir l'ID de la source
        print("\n📋 Recherche de la source elasticsearch...")
        source_id, source_tag = get_source_id(token)
        
        if not source_id:
            print("❌ Source elasticsearch non trouvée !")
            print("   La source doit être créée d'abord.")
            return False
        
        print(f"✅ Source trouvée (ID: {source_id})")
        
        # Rafraîchir
        refresh_source(token, source_id)
        
        # Attendre
        print("\n⏳ Attente du scan (30 secondes)...")
        time.sleep(30)
        
        # Promouvoir les datasets
        promote_datasets(token)
        
        # Vérifier
        time.sleep(5)
        indices_visible = check_indices(token)
        
        if indices_visible:
            print("\n" + "="*70)
            print("✅ SUCCÈS - Les indices Elasticsearch sont accessibles")
            print("="*70)
            print("\n📋 Vous pouvez maintenant:")
            print("   1. Exécuter create_es_vds_fixed.py")
            print("   2. Ou créer les VDS manuellement dans Dremio UI")
            return True
        else:
            print("\n" + "="*70)
            print("⚠️  ATTENTION - Les indices ne sont pas encore visibles")
            print("="*70)
            print("\n📋 Action manuelle requise:")
            print("   1. Ouvrir http://localhost:9047")
            print("   2. Aller dans Sources → elasticsearch")
            print("   3. Cliquer sur l'icône Refresh (⟳)")
            print("   4. Attendre 1-2 minutes")
            print("   5. Relancer ce script ou create_es_vds_fixed.py")
            return False
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
