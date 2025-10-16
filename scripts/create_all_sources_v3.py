#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer toutes les sources Dremio (PostgreSQL, MinIO, Elasticsearch)
en utilisant l'API v3 qui fonctionne avec Dremio 26
"""
import requests
import time

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """S'authentifier et obtenir le token"""
    print("🔐 Authentification...")
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["token"]
        print("✅ Authentification réussie")
        return token
    else:
        print(f"❌ Erreur authentification: {response.status_code}")
        return None

def create_postgresql_source(token):
    """Créer la source PostgreSQL"""
    print("\n🐘 Création source PostgreSQL...")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    source_config = {
        "entityType": "source",
        "name": "PostgreSQL_BusinessDB",
        "type": "POSTGRES",
        "config": {
            "hostname": "dremio-postgres",
            "port": 5432,
            "databaseName": "business_db",
            "username": "postgres",
            "password": "postgres123",
            "authenticationType": "MASTER",
            "useSsl": False
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 3600000,
            "datasetRefreshAfterMs": 3600000,
            "datasetExpireAfterMs": 10800000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": True
        }
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=source_config
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source PostgreSQL créée")
            return True
        elif response.status_code == 409:
            print("ℹ️ Source PostgreSQL existe déjà")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_minio_source(token):
    """Créer la source MinIO S3"""
    print("\n🗂️ Création source MinIO...")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    source_config = {
        "entityType": "source",
        "name": "MinIO_Storage",
        "type": "S3",
        "config": {
            "credentialType": "ACCESS_KEY",
            "accessKey": "minioadmin",
            "accessSecret": "minioadmin123",
            "secure": False,
            "externalBucketList": ["sales-data"],
            "enableAsync": False,
            "compatibilityMode": True,
            "rootPath": "/",
            "propertyList": [
                {"name": "fs.s3a.endpoint", "value": "http://dremio-minio:9000"},
                {"name": "fs.s3a.path.style.access", "value": "true"},
                {"name": "fs.s3a.connection.ssl.enabled", "value": "false"}
            ]
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 3600000,
            "datasetRefreshAfterMs": 3600000,
            "datasetExpireAfterMs": 10800000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": True
        }
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=source_config
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source MinIO créée")
            return True
        elif response.status_code == 409:
            print("ℹ️ Source MinIO existe déjà")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_elasticsearch_source(token):
    """Créer la source Elasticsearch"""
    print("\n🔍 Création source Elasticsearch...")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    source_config = {
        "entityType": "source",
        "name": "Elasticsearch_Logs",
        "type": "ELASTIC",
        "config": {
            "hostList": [
                {
                    "hostname": "dremio-elasticsearch",
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
            "autoPromoteDatasets": True
        }
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=source_config
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source Elasticsearch créée")
            return True
        elif response.status_code == 409:
            print("ℹ️ Source Elasticsearch existe déjà")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("="*60)
    print("🚀 CRÉATION DES SOURCES DREMIO")
    print("="*60)
    
    # Authentification
    token = get_auth_token()
    if not token:
        print("\n❌ Impossible de continuer sans authentification")
        return
    
    # Créer les sources
    print("\n📡 Création des sources de données...")
    
    pg_ok = create_postgresql_source(token)
    time.sleep(2)
    
    minio_ok = create_minio_source(token)
    time.sleep(2)
    
    es_ok = create_elasticsearch_source(token)
    
    # Résumé
    print("\n" + "="*60)
    print("📋 RÉSUMÉ")
    print("="*60)
    print(f"PostgreSQL: {'✅' if pg_ok else '❌'}")
    print(f"MinIO:      {'✅' if minio_ok else '❌'}")
    print(f"Elasticsearch: {'✅' if es_ok else '❌'}")
    print("\n🌐 Interface Dremio: http://localhost:9047")
    print("🔑 Credentials: admin/admin123")

if __name__ == "__main__":
    main()
