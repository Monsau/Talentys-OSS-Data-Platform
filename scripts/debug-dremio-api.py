#!/usr/bin/env python3
"""
Debug: Explorer l'API Dremio pour comprendre la structure
"""
import requests
import json

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASS = "admin123"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASS}
    )
    return response.json()["token"]

def explore_api(token, path=None):
    headers = {"Authorization": f"_dremio{token}"}
    
    if path:
        url = f"{DREMIO_URL}/api/v3/catalog/by-path/{path}"
    else:
        url = f"{DREMIO_URL}/api/v3/catalog"
    
    print(f"\n{'='*80}")
    print(f"URL: {url}")
    print('='*80)
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    print(json.dumps(data, indent=2)[:2000])  # Premiers 2000 caractères
    
    return data

# Tester
token = get_token()
print("TOKEN OBTENU")

# Catalogue racine
root = explore_api(token)

# Explorer le space "raw"
print("\n\nEXPLORATION DU SPACE 'raw':")
raw = explore_api(token, "raw")

# Vérifier s'il y a des children
if "children" in raw:
    print(f"\n\nChildren trouvés: {len(raw['children'])}")
    for child in raw.get("children", []):
        print(f"  - {child.get('path', 'NO PATH')} [{child.get('type', 'NO TYPE')}]")
