#!/usr/bin/env python3
"""Create a VDS (View) in Dremio for sales-data with a clean name"""

import requests
import time

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def execute_sql(token, sql):
    """Execute SQL and wait for completion"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Submit query
    response = requests.post(
        f"{DREMIO_URL}/api/v3/sql",
        json={"sql": sql},
        headers=headers
    )
    
    if response.status_code != 200:
        return False, response.text
    
    job = response.json()
    job_id = job.get("id")
    
    # Wait for completion
    for _ in range(15):
        result = requests.get(
            f"{DREMIO_URL}/api/v3/job/{job_id}",
            headers=headers
        )
        if result.status_code == 200:
            state = result.json().get("jobState")
            if state == "COMPLETED":
                return True, "Success"
            elif state in ["FAILED", "CANCELED"]:
                error_msg = result.json().get("errorMessage", "Failed")
                return False, error_msg
        time.sleep(0.5)
    
    return False, "Timeout"

def main():
    token = get_token()
    print("✓ Token obtained\n")
    
    # Create VDS in analytics.raw space with clean SQL
    sql = '''
    CREATE OR REPLACE VDS analytics.raw.minio_sales AS
    SELECT * FROM minio_sales."sales-data"
    '''
    
    print(f"Creating VDS...")
    print(f"SQL: {sql.strip()}\n")
    
    success, msg = execute_sql(token, sql)
    if success:
        print(f"✓ VDS created successfully!")
        print(f"  Access via: analytics.raw.minio_sales")
    else:
        print(f"✗ Error: {msg[:300]}")

if __name__ == "__main__":
    main()
