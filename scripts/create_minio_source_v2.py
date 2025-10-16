#!/usr/bin/env python3
"""
Creation source MinIO dans Dremio 26 - API v2
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


def create_minio_source_v2(headers):
    """Cree source MinIO avec API v2"""
    
    source_name = "minio_sales"
    
    source_config = {
        "entityType": "source",
        "name": source_name,
        "type": "S3",
        "config": {
            "accessKey": "minio_admin",
            "accessSecret": "minio_password",
            "secure": False,
            "externalBucketList": ["sales-data"],
            "compatibilityMode": True,
            "credentialType": "ACCESS_KEY",
            "propertyList": [
                {"name": "fs.s3a.endpoint", "value": "minio:9000"},
                {"name": "fs.s3a.path.style.access", "value": "true"},
                {"name": "dremio.s3.compat", "value": "true"}
            ]
        }
    }
    
    print(f"\n[1/2] Creation source '{source_name}'...")
    print(f"  Endpoint: minio:9000 (via propertyList)")
    print(f"  Buckets: {source_config['config']['externalBucketList']}")
    
    try:
        # POST pour creation - API v3
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=source_config,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Source '{source_name}' creee avec succes")
            return True
        else:
            print(f"✗ Erreur: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def verify_source(headers, source_name):
    """Verifie que la source est visible"""
    print(f"\n[2/2] Verification source '{source_name}'...")
    
    try:
        # Methode 1: Via catalog API v3
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{source_name}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Source visible dans le catalog")
            print(f"  ID: {data.get('id')}")
            print(f"  Type: {data.get('type')}")
            
            # Verifier children
            children = data.get('children', [])
            if children:
                print(f"  Buckets visibles: {len(children)}")
                for child in children[:3]:
                    path = child.get('path', [])
                    print(f"    - {path[-1] if path else 'Unknown'}")
            else:
                print(f"  (Pas de buckets encore visibles - attendre refresh)")
            
            return True
        else:
            print(f"✗ Source non accessible via catalog: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def refresh_source(headers, source_name):
    """Force le refresh de la source pour voir les donnees"""
    print(f"\n[3/3] Refresh metadata source '{source_name}'...")
    
    try:
        # POST refresh
        response = requests.post(
            f"{DREMIO_URL}/apiv2/source/{source_name}/refresh",
            headers=headers,
            timeout=60
        )
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Metadata refresh lance")
            return True
        else:
            print(f"⚠ Refresh status: {response.status_code}")
            return True  # Pas bloquant
            
    except Exception as e:
        print(f"⚠ Exception refresh (non-bloquant): {e}")
        return True


def main():
    print("=" * 70)
    print("CREATION SOURCE MINIO - API v2")
    print("=" * 70)
    
    # Auth
    headers = authenticate()
    if not headers:
        print("✗ Authentification echouee")
        return 1
    
    print("✓ Authentifie")
    
    # Creer source
    success = create_minio_source_v2(headers)
    if not success:
        print("\n✗ Echec creation source")
        return 1
    
    # Verifier
    verify_source(headers, "minio_sales")
    
    # Refresh metadata
    refresh_source(headers, "minio_sales")
    
    print("\n" + "=" * 70)
    print("✓ SOURCE MINIO CONFIGUREE")
    print("\nPour voir les donnees dans Dremio UI:")
    print("  1. Ouvrir http://localhost:9047")
    print("  2. Aller dans 'Datasets'")
    print("  3. Cliquer sur 'minio_sales'")
    print("  4. Cliquer sur 'sales-data'")
    print("  5. Voir la structure partitionnee year=.../month=.../day=...")
    print("\nAttendre 1-2 minutes pour le metadata refresh complet")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())
