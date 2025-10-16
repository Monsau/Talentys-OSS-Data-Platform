#!/usr/bin/env python3
"""Drop existing tables in Dremio via SQL"""

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
    for _ in range(10):
        result = requests.get(
            f"{DREMIO_URL}/api/v3/job/{job_id}",
            headers=headers
        )
        if result.status_code == 200:
            state = result.json().get("jobState")
            if state == "COMPLETED":
                return True, "Success"
            elif state in ["FAILED", "CANCELED"]:
                return False, result.json().get("errorMessage", "Failed")
        time.sleep(0.5)
    
    return False, "Timeout"

def main():
    token = get_token()
    print("✓ Token obtained\n")
    
    tables = [
        '"$scratch".marts.fct_orders',
        '"$scratch".marts.dim_customers',
        '"$scratch".marts.fct_platform_health',
        '"$scratch".marts.fct_sales_minio',
        '"$scratch".marts.fct_business_overview',
    ]
    
    print("Dropping existing tables via SQL...")
    for table in tables:
        sql = f"DROP TABLE IF EXISTS {table}"
        print(f"  Executing: {sql}")
        success, msg = execute_sql(token, sql)
        if success:
            print(f"    ✓ Success")
        else:
            print(f"    ⚠ {msg[:100]}")
    
    print("\n✓ Done - Ready for dbt run")

if __name__ == "__main__":
    main()
