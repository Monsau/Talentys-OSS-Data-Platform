#!/usr/bin/env python3
"""Check Elasticsearch catalog structure in Dremio"""

import requests

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def explore_catalog(token, source_id, path=[]):
    """Recursively explore catalog"""
    headers = {"Authorization": f"_dremio{token}"}
    
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog/{source_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        return
    
    data = response.json()
    children = data.get("children", [])
    
    for child in children:
        child_path = child.get("path", [])
        child_type = child.get("type")
        child_id = child.get("id")
        
        indent = "  " * len(child_path)
        print(f"{indent}- {'.'.join(child_path)} (type: {child_type})")
        
        # Recurse if container
        if child_type == "CONTAINER" and child_id:
            explore_catalog(token, child_id, child_path)

def main():
    print("=== Elasticsearch Catalog Structure ===\n")
    
    token = get_token()
    print("✓ Token obtained\n")
    
    # Get catalog
    headers = {"Authorization": f"_dremio{token}"}
    response = requests.get(f"{DREMIO_URL}/api/v3/catalog", headers=headers)
    catalog = response.json()
    
    # Find Elasticsearch source
    for item in catalog.get("data", []):
        path = item.get("path", [])
        if path and path[0].lower() == "elasticsearch":
            print(f"Found: {path[0]}")
            print(f"ID: {item.get('id')}")
            print(f"Type: {item.get('type')}\n")
            
            print("Children:")
            explore_catalog(token, item.get("id"))
            break

if __name__ == "__main__":
    main()
