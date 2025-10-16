#!/usr/bin/env python3
"""Query Elasticsearch via Dremio to see actual fields"""

import requests
import time

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def query_and_get_schema(token, sql):
    """Execute query and return schema"""
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
        return None, f"Error {response.status_code}"
    
    job = response.json()
    job_id = job.get("id")
    
    # Wait for completion
    for _ in range(20):
        time.sleep(0.5)
        result_resp = requests.get(
            f"{DREMIO_URL}/api/v3/job/{job_id}/results",
            headers=headers
        )
        if result_resp.status_code == 200:
            results = result_resp.json()
            schema = results.get("schema", [])
            rows = results.get("rows", [])
            return {"schema": schema, "rows": rows}, None
    
    return None, "Timeout"

def main():
    print("=== Elasticsearch Fields in Dremio ===\n")
    
    token = get_token()
    print("✓ Token obtained\n")
    
    queries = [
        ("application_logs", 'SELECT * FROM elasticsearch.application_logs."_doc" LIMIT 1'),
        ("user_events", 'SELECT * FROM elasticsearch.user_events."_doc" LIMIT 1'),
        ("performance_metrics", 'SELECT * FROM elasticsearch.performance_metrics."_doc" LIMIT 1'),
    ]
    
    for index_name, sql in queries:
        print(f"=== {index_name} ===")
        print(f"SQL: {sql}\n")
        
        result, error = query_and_get_schema(token, sql)
        if error:
            print(f"✗ {error}\n")
            continue
        
        print("Fields:")
        for field in result["schema"]:
            field_name = field.get("name")
            field_type = field.get("type", {}).get("name", "unknown")
            print(f"  - {field_name} ({field_type})")
        
        if result["rows"]:
            print(f"\nSample row (first 5 fields):")
            row = result["rows"][0]
            for i, field in enumerate(result["schema"][:5]):
                field_name = field.get("name")
                print(f"  {field_name}: {row.get(field_name, 'NULL')}")
        
        print()

if __name__ == "__main__":
    main()
