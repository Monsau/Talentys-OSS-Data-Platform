#!/usr/bin/env python3
"""Check actual Elasticsearch field mapping in Dremio"""

import requests
import time

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def query_es_sample(token):
    """Query Elasticsearch to see actual field names"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    queries = [
        "SELECT * FROM elasticsearch.application_logs LIMIT 1",
        "SELECT * FROM elasticsearch.user_events LIMIT 1",
        "SELECT * FROM elasticsearch.performance_metrics LIMIT 1",
    ]
    
    for sql in queries:
        print(f"\n{sql}")
        print("-" * 60)
        
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            json={"sql": sql},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"✗ Error: {response.status_code}")
            continue
        
        job = response.json()
        job_id = job.get("id")
        
        # Wait for job completion
        for attempt in range(30):
            time.sleep(1)
            
            result_resp = requests.get(
                f"{DREMIO_URL}/api/v3/job/{job_id}",
                headers=headers
            )
            
            if result_resp.status_code == 200:
                job_info = result_resp.json()
                state = job_info.get("jobState")
                
                if state == "COMPLETED":
                    # Get results
                    results_resp = requests.get(
                        f"{DREMIO_URL}/api/v3/job/{job_id}/results",
                        headers=headers
                    )
                    if results_resp.status_code == 200:
                        results = results_resp.json()
                        if results.get("schema"):
                            print("✓ Schema:")
                            for field in results["schema"]:
                                print(f"  - {field.get('name')}")
                        if results.get("rows"):
                            print(f"✓ Sample row: {results['rows'][0]}")
                    break
                elif state in ["FAILED", "CANCELED"]:
                    error = job_info.get("errorMessage", "Unknown error")
                    print(f"✗ Query failed: {error[:200]}")
                    break

def main():
    print("=== Elasticsearch Field Mapping in Dremio ===")
    token = get_token()
    print("✓ Token obtained")
    
    query_es_sample(token)

if __name__ == "__main__":
    main()
