#!/usr/bin/env python3
"""
Create a single VDS in Dremio via SQL API
Usage: python create_single_vds.py <vds_name> <source_table>
"""

import sys
import requests
import time

DREMIO_URL = "http://localhost:9047"

def create_single_vds(vds_name, source_table):
    """Create a single VDS"""
    
    # Authenticate
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    token = response.json()["token"]
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    sql = f"CREATE VDS raw.{vds_name} AS SELECT * FROM elasticsearch.{source_table} LIMIT 10000"
    
    print(f"Creating VDS: {vds_name}")
    
    # Submit SQL
    response = requests.post(
        f"{DREMIO_URL}/apiv2/sql",
        headers=headers,
        json={"sql": sql}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.text}")
        return False
    
    job_id = response.json().get("id")
    print(f"Job submitted: {job_id}")
    
    # Wait for completion
    for _ in range(30):
        time.sleep(1)
        
        job_response = requests.get(
            f"{DREMIO_URL}/apiv2/job/{job_id}",
            headers=headers
        )
        
        if job_response.status_code == 200:
            job_state = job_response.json().get("jobState")
            
            if job_state == "COMPLETED":
                print(f"✅ VDS created: {vds_name}")
                return True
            elif job_state == "FAILED":
                error = job_response.json().get("errorMessage", "Unknown")
                print(f"❌ Job failed: {error}")
                return False
    
    print(f"❌ Timeout")
    return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_single_vds.py <vds_name> <source_table>")
        print("Example: python create_single_vds.py es_application_logs application_logs")
        sys.exit(1)
    
    vds_name = sys.argv[1]
    source_table = sys.argv[2]
    
    success = create_single_vds(vds_name, source_table)
    sys.exit(0 if success else 1)
