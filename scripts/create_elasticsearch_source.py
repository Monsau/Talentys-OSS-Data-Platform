#!/usr/bin/env python3
"""
Script pour créer une source Elasticsearch dans Dremio
et vérifier la connexion
"""

import requests
import json

DREMIO_URL = "http://localhost:9047/apiv2"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

ES_HOST = "elasticsearch"  # Nom du conteneur Docker
ES_PORT = 9200

def get_auth_token():
    """Obtenir un token d'authentification Dremio"""
    response = requests.post(
        f"{DREMIO_URL}/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    )
    response.raise_for_status()
    return response.json()["token"]

def create_elasticsearch_source(token):
    """Créer une source Elasticsearch dans Dremio"""
    print("📊 Création de la source Elasticsearch dans Dremio...")
    
    # Configuration de la source Elasticsearch
    source_config = {
        "name": "elasticsearch",
        "type": "ELASTIC",
        "config": {
            "hostList": [{"hostname": ES_HOST, "port": ES_PORT}],
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
        }
    }
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Essayer de créer la source
        response = requests.post(
            f"{DREMIO_URL}/catalog",
            headers=headers,
            json=source_config
        )
        
        if response.status_code == 200:
            print("✅ Source Elasticsearch créée avec succès")
            return response.json()
        elif response.status_code == 409:
            print("⚠️  La source 'elasticsearch' existe déjà")
            # Récupérer la source existante
            response = requests.get(
                f"{DREMIO_URL}/catalog/by-path/elasticsearch",
                headers=headers
            )
            return response.json()
        else:
            print(f"❌ Erreur lors de la création de la source: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def list_elasticsearch_indices(token):
    """Lister les indices Elasticsearch visibles dans Dremio"""
    print("\n📋 Listing des indices Elasticsearch dans Dremio...")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Récupérer le contenu de la source elasticsearch
        response = requests.get(
            f"{DREMIO_URL}/catalog/by-path/elasticsearch",
            headers=headers
        )
        
        if response.status_code == 200:
            source = response.json()
            print(f"✅ Source trouvée: {source.get('path', [])}")
            
            # Lister les enfants (indices)
            if 'children' in source:
                print(f"\n📊 Indices disponibles ({len(source['children'])}):")
                for child in source['children']:
                    print(f"   - {child['path'][-1]}")
            else:
                print("   Aucun indice trouvé (ils peuvent prendre quelques secondes à apparaître)")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

def main():
    print("="*60)
    print("🔍 CONFIGURATION ELASTICSEARCH DANS DREMIO")
    print("="*60)
    
    # Authentification
    print("\n🔐 Authentification Dremio...")
    try:
        token = get_auth_token()
        print("✅ Authentification réussie")
    except Exception as e:
        print(f"❌ Erreur d'authentification: {str(e)}")
        return
    
    # Créer la source
    source = create_elasticsearch_source(token)
    
    # Attendre un peu pour que les indices soient scannés
    if source:
        print("\n⏳ Attente du scan des indices (5 secondes)...")
        import time
        time.sleep(5)
        
        # Lister les indices
        list_elasticsearch_indices(token)
    
    print("\n" + "="*60)
    print("✅ Configuration terminée")
    print("="*60)
    print("\n📋 Prochaines étapes:")
    print("   1. Vérifier les indices dans l'interface Dremio")
    print("   2. Créer des VDS depuis les indices Elasticsearch")
    print("   3. Intégrer dans les modèles dbt")
    print(f"\n🌐 Interface Dremio: http://localhost:9047")

if __name__ == "__main__":
    main()
