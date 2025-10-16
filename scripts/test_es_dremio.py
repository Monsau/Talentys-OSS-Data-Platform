#!/usr/bin/env python3
"""Test Elasticsearch queries in Dremio"""

import requests
import time

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def query_dremio(token, sql):
    """Execute a query"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/sql",
        json={"sql": sql},
        headers=headers
    )
    
    if response.status_code != 200:
        return None, f"Error {response.status_code}: {response.text[:200]}"
    
    job = response.json()
    job_id = job.get("id")
    
    # Wait for completion
    for _ in range(10):
        result_resp = requests.get(
            f"{DREMIO_URL}/api/v3/job/{job_id}/results",
            headers=headers
        )
        if result_resp.status_code == 200:
            return result_resp.json(), None
        time.sleep(0.5)
    
    return None, "Timeout"

def main():
    token = get_token()
    print("✓ Token obtained\n")
    
    queries = [
        "SELECT * FROM elasticsearch.application_logs LIMIT 1",
        "SELECT * FROM elasticsearch.user_events LIMIT 1",
        "SHOW TABLES IN elasticsearch",
    ]
    
    for sql in queries:
        print(f"Query: {sql}")
        result, error = query_dremio(token, sql)
        if error:
            print(f"  ✗ {error}\n")
        else:
            print(f"  ✓ Success")
            if result.get("rowCount"):
                print(f"    Rows: {result['rowCount']}")
                if result.get("rows"):
                    print(f"    Sample: {result['rows'][0] if result['rows'] else 'Empty'}")
            print()

if __name__ == "__main__":
    main()
