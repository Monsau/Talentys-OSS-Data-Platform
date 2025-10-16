#!/usr/bin/env python3
"""
Create Elasticsearch VDS using SQL API directly.
This bypasses the need for metadata refresh by using direct SQL queries.
"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"

def authenticate():
    """Get Dremio token"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def create_vds_via_sql(token, vds_name, source_table, limit=10000):
    """Create VDS using SQL API"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    sql = f"CREATE VDS raw.{vds_name} AS SELECT * FROM elasticsearch.{source_table} LIMIT {limit}"
    
    print(f"\n📝 Creating VDS: {vds_name}")
    print(f"   SQL: {sql}")
    
    try:
        # Submit SQL job
        response = requests.post(
            f"{DREMIO_URL}/apiv2/sql",
            headers=headers,
            json={"sql": sql}
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to submit: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        job_id = response.json().get("id")
        print(f"   ⏳ Job submitted: {job_id}")
        
        # Wait for job completion
        for attempt in range(30):  # 30 seconds max
            time.sleep(1)
            
            job_response = requests.get(
                f"{DREMIO_URL}/apiv2/job/{job_id}",
                headers=headers
            )
            
            if job_response.status_code == 200:
                job_data = job_response.json()
                job_state = job_data.get("jobState")
                
                if job_state == "COMPLETED":
                    print(f"   ✅ VDS created successfully!")
                    return True
                elif job_state == "FAILED":
                    error_msg = job_data.get("errorMessage", "Unknown error")
                    print(f"   ❌ Job failed: {error_msg}")
                    return False
                elif job_state in ["RUNNING", "STARTING", "ENQUEUED"]:
                    print(f"   ⏳ Job state: {job_state} (attempt {attempt+1}/30)")
                else:
                    print(f"   ⚠️  Unknown state: {job_state}")
        
        print(f"   ❌ Timeout waiting for job completion")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_vds_exists(token, vds_name):
    """Verify VDS was created by querying it"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    sql = f"SELECT COUNT(*) as count FROM raw.{vds_name}"
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/apiv2/sql",
            headers=headers,
            json={"sql": sql}
        )
        
        if response.status_code != 200:
            return False
        
        job_id = response.json().get("id")
        
        # Wait for query
        for _ in range(10):
            time.sleep(1)
            job_response = requests.get(
                f"{DREMIO_URL}/apiv2/job/{job_id}",
                headers=headers
            )
            
            if job_response.status_code == 200:
                job_state = job_response.json().get("jobState")
                
                if job_state == "COMPLETED":
                    # Get results
                    results_response = requests.get(
                        f"{DREMIO_URL}/apiv2/job/{job_id}/results",
                        headers=headers
                    )
                    
                    if results_response.status_code == 200:
                        rows = results_response.json().get("rows", [])
                        if rows:
                            count = rows[0].get("count", 0)
                            print(f"   ✅ Verified: {count} rows in {vds_name}")
                            return True
                elif job_state == "FAILED":
                    return False
        
        return False
    except:
        return False

def main():
    print("=" * 70)
    print("🚀 CREATE ELASTICSEARCH VDS VIA SQL API")
    print("=" * 70)
    
    # 1. Authenticate
    print("\n1️⃣ Authenticating...")
    try:
        token = authenticate()
        print("✅ Authenticated successfully")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # 2. Define VDS to create
    vds_mappings = [
        ("es_application_logs", "application_logs"),
        ("es_user_events", "user_events"),
        ("es_performance_metrics", "performance_metrics")
    ]
    
    # 3. Create each VDS
    print(f"\n2️⃣ Creating {len(vds_mappings)} VDS...")
    
    results = []
    for vds_name, source_table in vds_mappings:
        success = create_vds_via_sql(token, vds_name, source_table)
        results.append((vds_name, success))
        time.sleep(2)  # Wait between creations
    
    # 4. Verify VDS
    print(f"\n3️⃣ Verifying VDS...")
    verified_count = 0
    
    for vds_name, created in results:
        if created:
            print(f"\n🔍 Verifying {vds_name}...")
            if verify_vds_exists(token, vds_name):
                verified_count += 1
    
    # 5. Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    created_count = sum(1 for _, success in results if success)
    
    print(f"\n📝 VDS Creation Results:")
    for vds_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {status}: {vds_name}")
    
    print(f"\n📈 Statistics:")
    print(f"   Created: {created_count}/{len(vds_mappings)}")
    print(f"   Verified: {verified_count}/{created_count}")
    
    if created_count == len(vds_mappings) and verified_count == created_count:
        print("\n🎉 SUCCESS! All VDS created and verified!")
        print("\n📝 Next steps:")
        print("   1. Run dbt: wsl bash -c 'cd /mnt/c/projets/dremiodbt && source venv/bin/activate && ./run_dbt.sh'")
        print("   2. Run tests: wsl bash -c 'cd /mnt/c/projets/dremiodbt/dbt && source ../venv/bin/activate && dbt test'")
        print("   3. Generate docs: wsl bash -c 'cd /mnt/c/projets/dremiodbt && ./generate_dbt_docs.sh'")
        print("\n🎯 Project will be 100% complete!")
    elif created_count > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {created_count}/{len(vds_mappings)} VDS created")
        print("\n📝 Manual action required for failed VDS:")
        print("   Open http://localhost:9047 → SQL Runner")
        print("   Execute the failed CREATE VDS statements manually")
    else:
        print("\n❌ FAILED: No VDS created")
        print("\n📝 Possible issues:")
        print("   1. Elasticsearch source not accessible from Dremio")
        print("   2. Indices not indexed/visible in Elasticsearch")
        print("   3. Network connectivity issue")
        print("\n📝 Try:")
        print("   1. Check ES connection: docker exec dremio curl elasticsearch:9200/_cat/indices")
        print("   2. Refresh source in Dremio UI: http://localhost:9047 → Sources → elasticsearch → Refresh")
        print("   3. Re-run this script")

if __name__ == "__main__":
    main()
