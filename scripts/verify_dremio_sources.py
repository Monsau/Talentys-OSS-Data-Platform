#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifier toutes les sources et espaces Dremio
"""
import requests
import json

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def main():
    # Login
    print("[i] Connexion à Dremio...")
    auth_response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD},
        timeout=10
    )
    
    if auth_response.status_code != 200:
        print(f"[X] Erreur login: {auth_response.status_code}")
        return
    
    token = auth_response.json()["token"]
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    print("[OK] Connecté à Dremio\n")
    
    # Méthode 1: /api/v3/catalog
    print("=== API V3 CATALOG ===")
    response = requests.get(f"{DREMIO_URL}/api/v3/catalog", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json().get('data', [])
        print(f"Total items: {len(data)}")
        for item in data:
            entity_type = item.get('entityType', 'unknown')
            path = item.get('path', ['unknown'])
            name = path[0] if path else 'unknown'
            print(f"  - {name} (type: {entity_type})")
    else:
        print(f"[X] Erreur: {response.status_code}")
    
    # Méthode 2: /apiv2/sources
    print("\n=== API V2 SOURCES ===")
    response = requests.get(f"{DREMIO_URL}/apiv2/sources", headers=headers, timeout=10)
    if response.status_code == 200:
        sources = response.json().get('sources', [])
        print(f"Total sources: {len(sources)}")
        for source in sources:
            print(f"  - {source.get('name')} (type: {source.get('type')})")
    else:
        print(f"[X] Erreur: {response.status_code}")
    
    # Méthode 3: /apiv2/spaces
    print("\n=== API V2 SPACES ===")
    response = requests.get(f"{DREMIO_URL}/apiv2/spaces", headers=headers, timeout=10)
    if response.status_code == 200:
        spaces = response.json().get('spaces', [])
        print(f"Total spaces: {len(spaces)}")
        for space in spaces:
            print(f"  - {space.get('name')}")
    else:
        print(f"[X] Erreur: {response.status_code}")

if __name__ == "__main__":
    main()
