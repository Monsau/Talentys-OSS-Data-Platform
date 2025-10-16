#!/usr/bin/env python3
"""Check MinIO tables in Dremio catalog"""

import requests

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def main():
    token = get_token()
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Get catalog
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers
    )
    
    catalog = response.json()
    
    # Find MinIO source
    for item in catalog.get("data", []):
        path = item.get("path", [])
        if path and "minio" in path[0].lower():
            print(f"Found: {path}")
            print(f"  ID: {item.get('id')}")
            print(f"  Type: {item.get('type')}")
            
            # Get children
            source_id = item.get("id")
            children_resp = requests.get(
                f"{DREMIO_URL}/api/v3/catalog/{source_id}",
                headers=headers
            )
            if children_resp.status_code == 200:
                source_info = children_resp.json()
                print(f"  Children:")
                for child in source_info.get("children", []):
                    child_path = child.get("path", [])
                    print(f"    - {'.'.join(child_path)}")

if __name__ == "__main__":
    main()
