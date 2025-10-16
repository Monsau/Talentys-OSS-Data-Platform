#!/usr/bin/env python3
"""Test MinIO path in Dremio"""

import requests
import sys

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def test_query(token, query):
    """Execute a SQL query"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    payload = {"sql": query}
    response = requests.post(f"{DREMIO_URL}/api/v3/sql", json=payload, headers=headers)
    
    if response.status_code == 200:
        job = response.json()
        job_id = job.get("id")
        print(f"✓ Query success: {query[:80]}")
        return True
    else:
        print(f"✗ Query failed: {response.status_code}")
        print(f"  Error: {response.text[:200]}")
        return False

def main():
    token = get_token()
    print(f"✓ Token obtained\n")
    
    # Test different path formats
    queries = [
        'SELECT * FROM minio_sales."sales-data" LIMIT 1',
        "SELECT * FROM minio_sales.\"sales-data\" LIMIT 1",
        'SELECT * FROM minio_sales.[sales-data] LIMIT 1',
        'SELECT * FROM minio_sales.sales_data LIMIT 1',
        'SHOW TABLES IN minio_sales',
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
        test_query(token, query)

if __name__ == "__main__":
    main()
