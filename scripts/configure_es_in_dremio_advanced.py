#!/usr/bin/env python3
"""
Script avancé pour configurer Elasticsearch dans Dremio
Utilise l'API REST interne de Dremio
"""

import requests
import json
import time
from urllib.parse import quote

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

def get_auth_token():
    """Obtenir un token d'authentification Dremio"""
    print("🔐 Authentification Dremio...")
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    token = response.json()["token"]
    print("✅ Authentification réussie")
    return token

def get_headers(token):
    """Générer les headers pour les requêtes"""
    return {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }

def check_source_exists(token, source_name):
    """Vérifier si une source existe déjà"""
    print(f"\n🔍 Vérification de l'existence de la source '{source_name}'...")
    headers = get_headers(token)
    
    try:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{quote(source_name)}",
            headers=headers
        )
        if response.status_code == 200:
            print(f"⚠️  La source '{source_name}' existe déjà")
            return True, response.json()
        else:
            print(f"✅ La source '{source_name}' n'existe pas encore")
            return False, None
    except Exception as e:
        print(f"✅ La source n'existe pas (erreur: {str(e)})")
        return False, None

def delete_source(token, source_id, source_tag):
    """Supprimer une source existante"""
    print(f"\n🗑️  Suppression de la source existante...")
    headers = get_headers(token)
    
    try:
        response = requests.delete(
            f"{DREMIO_URL}/api/v3/catalog/{source_id}",
            headers=headers,
            params={"tag": source_tag}
        )
        if response.status_code in [200, 204]:
            print("✅ Source supprimée avec succès")
            time.sleep(2)  # Attendre que la suppression soit effective
            return True
        else:
            print(f"⚠️  Erreur lors de la suppression: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def create_elasticsearch_source(token):
    """Créer une source Elasticsearch dans Dremio"""
    print("\n📊 Création de la source Elasticsearch...")
    
    headers = get_headers(token)
    
    # Configuration Elasticsearch pour Dremio
    source_config = {
        "entityType": "source",
        "name": "elasticsearch",
        "type": "ELASTIC",
        "config": {
            "hostList": [
                {
                    "hostname": "elasticsearch",
                    "port": 9200
                }
            ],
            "authenticationType": "ANONYMOUS",
            "scrollSize": 4000,
            "scrollTimeoutMillis": 60000,
            "usePainless": True,
            "useWhitelist": False,
            "showHiddenIndices": False,
            "showIdColumn": False,
            "readTimeoutMillis": 60000,
            "scriptsEnabled": True,
            "allowPushdownOnNormalizedOrAnalyzedFields": True
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 3600000,
            "datasetRefreshAfterMs": 3600000,
            "datasetExpireAfterMs": 10800000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": False
        },
        "accelerationRefreshPeriod": 3600000,
        "accelerationGracePeriod": 10800000
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=source_config
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Source Elasticsearch créée avec succès")
            print(f"   ID: {result.get('id', 'N/A')}")
            return result
        else:
            print(f"❌ Erreur lors de la création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def refresh_source_metadata(token, source_name):
    """Rafraîchir les métadonnées d'une source"""
    print(f"\n🔄 Rafraîchissement des métadonnées de '{source_name}'...")
    headers = get_headers(token)
    
    try:
        # D'abord, obtenir l'ID de la source
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{quote(source_name)}",
            headers=headers
        )
        
        if response.status_code == 200:
            source = response.json()
            source_id = source.get('id')
            
            # Rafraîchir les métadonnées
            refresh_response = requests.post(
                f"{DREMIO_URL}/api/v3/catalog/{source_id}/refresh",
                headers=headers
            )
            
            if refresh_response.status_code in [200, 204]:
                print("✅ Métadonnées rafraîchies")
                return True
            else:
                print(f"⚠️  Erreur rafraîchissement: {refresh_response.status_code}")
        else:
            print(f"⚠️  Source non trouvée: {response.status_code}")
        
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def list_elasticsearch_contents(token, source_name):
    """Lister le contenu de la source Elasticsearch"""
    print(f"\n📋 Contenu de la source '{source_name}'...")
    headers = get_headers(token)
    
    try:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{quote(source_name)}",
            headers=headers
        )
        
        if response.status_code == 200:
            source = response.json()
            children = source.get('children', [])
            
            if children:
                print(f"\n✅ {len(children)} indices trouvés:")
                for child in children:
                    child_path = child.get('path', [])
                    child_name = child_path[-1] if child_path else 'Unknown'
                    child_type = child.get('type', 'Unknown')
                    print(f"   - {child_name} ({child_type})")
                return children
            else:
                print("⚠️  Aucun indice trouvé (attendre quelques secondes...)")
                return []
        else:
            print(f"❌ Erreur: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return []

def create_vds_from_elasticsearch(token, index_name, vds_name, vds_path):
    """Créer une VDS depuis un indice Elasticsearch"""
    print(f"\n📊 Création VDS '{vds_name}' depuis '{index_name}'...")
    headers = get_headers(token)
    
    vds_config = {
        "entityType": "dataset",
        "path": vds_path,
        "type": "VIRTUAL_DATASET",
        "sql": f'SELECT * FROM elasticsearch."{index_name}"',
        "sqlContext": ["elasticsearch"]
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=vds_config
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ VDS '{vds_name}' créée")
            return True
        else:
            print(f"⚠️  Erreur création VDS: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def main():
    print("="*70)
    print("🔧 CONFIGURATION AVANCÉE ELASTICSEARCH DANS DREMIO")
    print("="*70)
    
    try:
        # Authentification
        token = get_auth_token()
        
        # Vérifier si la source existe déjà
        exists, existing_source = check_source_exists(token, "elasticsearch")
        
        if exists:
            source_id = existing_source.get('id')
            source_tag = existing_source.get('tag')
            
            print("\n⚠️  Options:")
            print("   1. Supprimer et recréer")
            print("   2. Garder et rafraîchir")
            
            # Pour l'automatisation, on rafraîchit
            print("\n➡️  Mode automatique: rafraîchissement de la source existante")
            refresh_source_metadata(token, "elasticsearch")
        else:
            # Créer la source
            source = create_elasticsearch_source(token)
            
            if source:
                # Attendre que les indices soient scannés
                print("\n⏳ Attente du scan des indices (10 secondes)...")
                time.sleep(10)
                
                # Rafraîchir les métadonnées
                refresh_source_metadata(token, "elasticsearch")
                
                # Attendre encore un peu
                time.sleep(5)
        
        # Lister les indices
        children = list_elasticsearch_contents(token, "elasticsearch")
        
        # Créer des VDS pour nos indices personnalisés
        target_indices = ["application_logs", "user_events", "performance_metrics"]
        
        if children:
            print("\n📊 Création des VDS pour les indices personnalisés...")
            
            for index_name in target_indices:
                # Vérifier si l'indice existe
                index_exists = any(
                    child.get('path', [])[-1] == index_name 
                    for child in children
                )
                
                if index_exists:
                    vds_name = f"es_{index_name}"
                    vds_path = ["raw", vds_name]
                    create_vds_from_elasticsearch(token, index_name, vds_name, vds_path)
                else:
                    print(f"⚠️  Indice '{index_name}' non trouvé")
        
        print("\n" + "="*70)
        print("✅ CONFIGURATION TERMINÉE")
        print("="*70)
        print("\n📋 Résumé:")
        print(f"   • Source Elasticsearch: {'✅ Configurée' if exists or source else '❌ Échec'}")
        print(f"   • Indices trouvés: {len(children)}")
        print(f"   • VDS créées: À vérifier dans Dremio")
        print(f"\n🌐 Interface Dremio: http://localhost:9047")
        print("   → Vérifier dans 'Sources' → 'elasticsearch'")
        print("   → Vérifier dans 'Spaces' → 'raw' pour les VDS")
        
    except Exception as e:
        print(f"\n❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
