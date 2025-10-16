#!/usr/bin/env python3
"""
Cree source MinIO S3 dans Dremio 26
"""

import requests
import json

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def authenticate():
    """Authentification Dremio"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD},
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json().get("token")
        return {
            "Authorization": f"_dremio{token}",
            "Content-Type": "application/json"
        }
    return None


def check_source_exists(headers, source_name):
    """Verifie si source existe"""
    try:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            sources = response.json().get("data", [])
            for source in sources:
                if source.get('path', [None])[0] == source_name:
                    print(f"✓ Source '{source_name}' existe deja (ID: {source.get('id')})")
                    return source.get('id')
        return None
    except Exception as e:
        print(f"Erreur check: {e}")
        return None


def create_minio_source(headers):
    """Cree source MinIO S3"""
    
    source_name = "minio_sales"
    
    # Verifier si existe
    existing_id = check_source_exists(headers, source_name)
    if existing_id:
        return existing_id
    
    # Configuration MinIO pour Dremio 26
    config = {
        "name": source_name,
        "type": "S3",
        "config": {
            "credentialType": "ACCESS_KEY",
            "accessKey": "minio_admin",
            "accessSecret": "minio_password",
            "secure": False,
            "externalBucketList": ["sales-data"],
            "enableAsync": True,
            "compatibilityMode": True,
            "enableFileStatusCheck": True,
            "rootPath": "/",
            "defaultCtasFormat": "PARQUET",
            "isPartitionInferenceEnabled": True,
            "isCachingEnabled": True,
            "maxCacheSpacePct": 100,
            "propertyList": [
                {"name": "fs.s3a.endpoint", "value": "minio:9000"},
                {"name": "fs.s3a.path.style.access", "value": "true"},
                {"name": "dremio.s3.compat", "value": "true"}
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
        },
        "accelerationGracePeriodMs": 10800000,
        "accelerationRefreshPeriodMs": 3600000,
        "accelerationNeverExpire": False,
        "accelerationNeverRefresh": False
    }
    
    print(f"\n[1/2] Creation source '{source_name}'...")
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=config,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            source_id = response.json().get("id")
            print(f"✓ Source '{source_name}' creee (ID: {source_id})")
            return source_id
        else:
            print(f"✗ Erreur creation: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None


def verify_source(headers, source_name):
    """Verifie que la source est accessible"""
    print(f"\n[2/2] Verification source '{source_name}'...")
    
    try:
        # Lister le contenu de la source
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{source_name}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Source accessible")
            print(f"  Type: {data.get('type')}")
            print(f"  ID: {data.get('id')}")
            
            # Lister les buckets/folders
            children = data.get('children', [])
            if children:
                print(f"  Buckets/Folders:")
                for child in children[:5]:
                    print(f"    - {child.get('path', ['?'])[-1]}")
            else:
                print(f"  (Aucun bucket visible - verifier configuration)")
            
            return True
        else:
            print(f"✗ Source non accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Exception verification: {e}")
        return False


def main():
    print("=" * 70)
    print("CREATION SOURCE MINIO DANS DREMIO")
    print("=" * 70)
    
    # Auth
    headers = authenticate()
    if not headers:
        print("✗ Authentification echouee")
        return
    
    print("✓ Authentifie")
    
    # Creer source
    source_id = create_minio_source(headers)
    if not source_id:
        print("\n✗ Echec creation source")
        return
    
    # Verifier
    success = verify_source(headers, "minio_sales")
    
    print("\n" + "=" * 70)
    if success:
        print("✓ SOURCE MINIO CREEE ET ACCESSIBLE")
        print("\nAcces Dremio:")
        print("  http://localhost:9047")
        print("  Datasets > minio_sales > sales-data")
    else:
        print("✗ PROBLEME AVEC LA SOURCE")
        print("\nVerifier:")
        print("  1. MinIO tourne: docker ps | grep minio")
        print("  2. Bucket existe: http://localhost:9001")
        print("  3. Credentials: minio_admin / minio_password")
    print("=" * 70)


if __name__ == "__main__":
    main()
