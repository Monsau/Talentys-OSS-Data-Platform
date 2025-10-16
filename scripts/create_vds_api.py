#!/usr/bin/env python3
"""Create VDS via Catalog API for MinIO"""

import requests

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def main():
    print("=== Creating MinIO VDS via Catalog API ===\n")
    
    token = get_token()
    print("✓ Token obtained\n")
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Create VDS in analytics space
    vds_config = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET",
        "path": ["analytics", "minio_sales_data"],
        "sql": 'SELECT * FROM minio_sales."sales-data"',
        "sqlContext": ["@dremio"]
    }
    
    print("Creating VDS...")
    print(f"  Path: analytics.minio_sales_data")
    print(f"  SQL: {vds_config['sql']}\n")
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=vds_config
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("✓ VDS created successfully!")
        print(f"  ID: {result.get('id')}")
        print(f"  Path: {'.'.join(result.get('path', []))}")
    else:
        print(f"✗ Error {response.status_code}")
        print(f"  {response.text[:500]}")

if __name__ == "__main__":
    main()
