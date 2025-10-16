#!/usr/bin/env python3
"""Drop existing tables in Dremio"""

import requests

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def drop_table(token, path):
    """Drop a table by path"""
    headers = {"Authorization": f"_dremio{token}"}
    encoded_path = path.replace("/", "%2F").replace("$", "%24")
    url = f"{DREMIO_URL}/api/v3/catalog/by-path/{encoded_path}"
    
    response = requests.delete(url, headers=headers)
    if response.status_code in [200, 204, 404]:
        print(f"  ✓ Dropped (or not found): {path}")
        return True
    else:
        print(f"  ✗ Error dropping {path}: {response.status_code}")
        return False

def main():
    token = get_token()
    print("✓ Token obtained\n")
    
    tables = [
        "$scratch/marts/fct_orders",
        "$scratch/marts/dim_customers",
        "$scratch/marts/fct_platform_health",
        "$scratch/marts/fct_sales_minio",
        "$scratch/marts/fct_business_overview",
    ]
    
    print("Dropping existing tables...")
    for table in tables:
        drop_table(token, table)
    
    print("\n✓ Done - Ready for dbt run --full-refresh")

if __name__ == "__main__":
    main()
