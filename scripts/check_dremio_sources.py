#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifier les sources et espaces dans Dremio
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
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    print("[OK] Connecté à Dremio\n")
    
    # Lister les sources
    print("=== SOURCES ===")
    sources_response = requests.get(f"{DREMIO_URL}/apiv2/sources", headers=headers, timeout=10)
    if sources_response.status_code == 200:
        sources = sources_response.json().get('data', [])
        for source in sources:
            print(f"  - {source.get('name')} (type: {source.get('type')})")
    
    print("\n=== ESPACES ===")
    spaces_response = requests.get(f"{DREMIO_URL}/apiv2/spaces", headers=headers, timeout=10)
    if spaces_response.status_code == 200:
        spaces = spaces_response.json().get('data', [])
        for space in spaces:
            print(f"  - {space.get('name')}")
    
    print("\n=== CATALOG (racine) ===")
    catalog_response = requests.get(f"{DREMIO_URL}/apiv2/catalog", headers=headers, timeout=10)
    if catalog_response.status_code == 200:
        catalog = catalog_response.json().get('data', [])
        for item in catalog:
            item_type = item.get('containerType', item.get('type', 'unknown'))
            print(f"  - {item.get('path', ['unknown'])[0]} ({item_type})")

if __name__ == "__main__":
    main()
