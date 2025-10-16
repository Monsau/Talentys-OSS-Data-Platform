#!/usr/bin/env python3
"""Create VDS for MinIO sales-data in analytics space"""

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
        return False, f"Submit error: {response.status_code} - {response.text[:200]}"
    
    job = response.json()
    job_id = job.get("id")
    
    # Wait for completion
    for attempt in range(20):
        time.sleep(0.5)
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
    
    return False, "Timeout"

def main():
    print("=== Creating MinIO VDS ===\n")
    
    token = get_token()
    print("✓ Token obtained\n")
    
    # Create analytics space if not exists
    print("1. Creating analytics space (if not exists)...")
    sql = "CREATE SPACE IF NOT EXISTS analytics"
    success, msg = execute_sql(token, sql)
    if success:
        print("  ✓ Space ready\n")
    else:
        print(f"  ⚠️ {msg[:100]}\n")
    
    # Create VDS for sales-data
    print("2. Creating VDS for MinIO sales-data...")
    sql = '''
    CREATE OR REPLACE VDS analytics.minio_sales_data AS
    SELECT * FROM minio_sales."sales-data"
    '''
    
    print(f"   SQL: {sql.strip()}")
    success, msg = execute_sql(token, sql)
    
    if success:
        print("\n✓ VDS created successfully!")
        print("  Access via: analytics.minio_sales_data")
        print("\nTest query:")
        test_sql = "SELECT COUNT(*) as total FROM analytics.minio_sales_data"
        print(f"  {test_sql}")
        success2, msg2 = execute_sql(token, test_sql)
        if success2:
            print("  ✓ VDS is accessible")
        else:
            print(f"  ⚠️ {msg2[:100]}")
    else:
        print(f"\n✗ Error: {msg[:300]}")

if __name__ == "__main__":
    main()
