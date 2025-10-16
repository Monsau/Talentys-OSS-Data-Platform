"""Delete and recreate all Dremio sources properly"""
import requests
import time

DREMIO_URL = "http://localhost:9047"

def login():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["token"]
    return None

def delete_source_if_exists(token, source_name):
    """Delete source if it exists"""
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    print(f"\n🔍 Vérification: {source_name}")
    
    # Try to get source
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog/by-path/{source_name}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        source_id = data.get("id")
        source_tag = data.get("tag")
        
        print(f"   ⚠️ Source existe (ID: {source_id})")
        print(f"   🗑️ Suppression...")
        
        # Delete it
        delete_response = requests.delete(
            f"{DREMIO_URL}/api/v3/catalog/{source_id}",
            headers=headers,
            params={"tag": source_tag}
        )
        
        if delete_response.status_code in [200, 204]:
            print(f"   ✅ Supprimée")
            time.sleep(2)
            return True
        else:
            print(f"   ❌ Erreur suppression: {delete_response.status_code}")
            return False
    else:
        print(f"   ℹ️ N'existe pas")
        return True

def create_postgresql(token):
    """Create PostgreSQL source"""
    print("\n🐘 Création: PostgreSQL_BusinessDB")
    
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    config = {
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
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=config
    )
    
    if response.status_code in [200, 201]:
        print("   ✅ Créée")
        return True
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   {response.text[:300]}")
        return False

def create_minio(token):
    """Create MinIO source"""
    print("\n🗂️ Création: MinIO_Storage")
    
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    config = {
        "entityType": "source",
        "name": "MinIO_Storage",
        "type": "S3",
        "config": {
            "credentialType": "ACCESS_KEY",
            "accessKey": "minioadmin",
            "accessSecret": "minioadmin123",
            "secure": False,
            "externalBucketList": ["sales-data"],
            "enableAsync": True,
            "compatibilityMode": True,
            "rootPath": "/",
            "defaultCtasFormat": "PARQUET",
            "isPartitionInferenceEnabled": True,
            "requesterPays": False,
            "propertyList": [
                {
                    "name": "fs.s3a.path.style.access",
                    "value": "true"
                },
                {
                    "name": "fs.s3a.endpoint",
                    "value": "dremio-minio:9000"
                },
                {
                    "name": "dremio.s3.compat",
                    "value": "true"
                }
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
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=config
    )
    
    if response.status_code in [200, 201]:
        print("   ✅ Créée")
        return True
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   {response.text[:300]}")
        return False

def create_elasticsearch(token):
    """Create Elasticsearch source"""
    print("\n🔍 Création: Elasticsearch_Logs")
    
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    config = {
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
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=config
    )
    
    if response.status_code in [200, 201]:
        print("   ✅ Créée")
        return True
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   {response.text[:300]}")
        return False

def verify_sources(token):
    """Verify all sources are visible"""
    print("\n" + "=" * 60)
    print("VÉRIFICATION")
    print("=" * 60)
    
    headers = {"Authorization": f"_dremio{token}"}
    
    # Check API v2
    print("\n📋 API v2 - /apiv2/sources")
    response = requests.get(f"{DREMIO_URL}/apiv2/sources", headers=headers)
    if response.status_code == 200:
        sources = response.json().get("data", [])
        print(f"   Total: {len(sources)}")
        for src in sources:
            print(f"   - {src.get('name')} ({src.get('type')})")
    
    # Check direct access
    print("\n🔗 Accès direct")
    for name in ["PostgreSQL_BusinessDB", "MinIO_Storage", "Elasticsearch_Logs"]:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{name}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            children = data.get("children", [])
            print(f"   ✅ {name} - {len(children)} enfants")
        else:
            print(f"   ❌ {name} - Error {response.status_code}")

def main():
    print("=" * 60)
    print("RECREATE ALL DREMIO SOURCES")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Authentifié\n")
    
    # Delete existing sources
    print("ÉTAPE 1: SUPPRESSION")
    print("-" * 60)
    for source in ["PostgreSQL_BusinessDB", "MinIO_Storage", "Elasticsearch_Logs"]:
        delete_source_if_exists(token, source)
        time.sleep(1)
    
    # Recreate sources
    print("\nÉTAPE 2: CRÉATION")
    print("-" * 60)
    
    results = {}
    results["PostgreSQL"] = create_postgresql(token)
    time.sleep(2)
    
    results["MinIO"] = create_minio(token)
    time.sleep(2)
    
    results["Elasticsearch"] = create_elasticsearch(token)
    time.sleep(2)
    
    # Verify
    verify_sources(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print("\n💡 Ouvrez Dremio UI: http://localhost:9047")
    print("   Les sources devraient maintenant être visibles!")

if __name__ == "__main__":
    main()
