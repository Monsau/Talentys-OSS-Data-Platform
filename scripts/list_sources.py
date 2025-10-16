#!/usr/bin/env python3
"""
Liste les sources Dremio et vérifie MinIO
"""

import requests
import json

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def authenticate():
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

def list_sources(headers):
    """Lister toutes les sources"""
    print("📡 SOURCES DREMIO:\n")
    
    try:
        response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            sources = response.json().get("data", [])
            for source in sources:
                print(f"✓ {source.get('name')} ({source.get('type')})")
                print(f"  ID: {source.get('id')}")
                if source.get('name') == 'MinIO_Storage':
                    print(f"  Config: {json.dumps(source.get('config', {}), indent=4)}")
            return len(sources)
        else:
            print(f"❌ Erreur: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Exception: {e}")
        return 0

def main():
    print("=" * 70)
    headers = authenticate()
    if not headers:
        print("❌ Auth failed")
        return
    
    count = list_sources(headers)
    print(f"\n📋 Total: {count} sources")
    print("=" * 70)

if __name__ == "__main__":
    main()
