#!/usr/bin/env python3
"""
Force Elasticsearch metadata refresh in Dremio using multiple API endpoints.
Tries various methods to make the indices visible.
"""

import requests
import time
import json
from requests.auth import HTTPBasicAuth

# Configuration
DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"
ES_SOURCE_NAME = "elasticsearch"

def get_auth_token():
    """Authenticate and get token"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    )
    response.raise_for_status()
    return response.json()["token"]

def get_source_id(token, source_name):
    """Get source ID by name"""
    headers = {"Authorization": f"_dremio{token}"}
    response = requests.get(f"{DREMIO_URL}/apiv2/source", headers=headers)
    response.raise_for_status()
    
    for source in response.json().get("data", []):
        if source.get("name") == source_name:
            return source.get("id")
    return None

def method_1_refresh_metadata(token, source_id):
    """Method 1: PUT /catalog/{id}/refresh"""
    print("\n🔄 Method 1: Trying PUT /catalog/{id}/refresh...")
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            f"{DREMIO_URL}/api/v3/catalog/{source_id}/refresh",
            headers=headers,
            json={"names": [ES_SOURCE_NAME]}
        )
        
        if response.status_code in [200, 204]:
            print("✅ Method 1: Refresh initiated successfully")
            return True
        else:
            print(f"❌ Method 1 failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Method 1 error: {e}")
        return False

def method_2_refresh_source(token, source_id):
    """Method 2: POST /source/{id}/refresh"""
    print("\n🔄 Method 2: Trying POST /source/{id}/refresh...")
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/apiv2/source/{source_id}/refresh",
            headers=headers,
            json={}
        )
        
        if response.status_code in [200, 204]:
            print("✅ Method 2: Refresh initiated successfully")
            return True
        else:
            print(f"❌ Method 2 failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Method 2 error: {e}")
        return False

def method_3_update_source_config(token, source_id):
    """Method 3: Update source config to trigger rescan"""
    print("\n🔄 Method 3: Trying to update source config...")
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get current config
        response = requests.get(f"{DREMIO_URL}/apiv2/source/{source_id}", headers=headers)
        response.raise_for_status()
        source_config = response.json()
        
        # Modify config to force rescan
        if "config" in source_config:
            source_config["config"]["allowPushdownOnNormalizedOrAnalyzedFields"] = True
            source_config["config"]["warnOnRowCountMismatch"] = True
            
            # Update source
            response = requests.put(
                f"{DREMIO_URL}/apiv2/source/{source_id}",
                headers=headers,
                json=source_config
            )
            
            if response.status_code in [200, 204]:
                print("✅ Method 3: Source config updated successfully")
                return True
            else:
                print(f"❌ Method 3 failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Method 3 error: {e}")
        return False

def method_4_sql_query(token):
    """Method 4: Execute SQL queries to trigger metadata loading"""
    print("\n🔄 Method 4: Trying SQL queries to trigger metadata...")
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    queries = [
        "SHOW TABLES IN elasticsearch",
        "SHOW SCHEMAS LIKE 'elasticsearch'",
        "SELECT * FROM elasticsearch.application_logs LIMIT 1",
        "SELECT * FROM elasticsearch.user_events LIMIT 1",
        "SELECT * FROM elasticsearch.performance_metrics LIMIT 1"
    ]
    
    success_count = 0
    for query in queries:
        try:
            response = requests.post(
                f"{DREMIO_URL}/apiv2/sql",
                headers=headers,
                json={"sql": query}
            )
            
            if response.status_code == 200:
                job_id = response.json().get("id")
                print(f"✅ Query submitted: {query[:50]}... (Job: {job_id})")
                success_count += 1
            else:
                print(f"⚠️  Query failed: {query[:50]}... - {response.status_code}")
        except Exception as e:
            print(f"⚠️  Query error: {query[:50]}... - {e}")
    
    return success_count > 0

def check_indices_visible(token):
    """Check if ES indices are now visible"""
    print("\n🔍 Checking if indices are visible...")
    headers = {"Authorization": f"_dremio{token}"}
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/apiv2/sql",
            headers=headers,
            json={"sql": "SHOW TABLES IN elasticsearch"}
        )
        
        if response.status_code == 200:
            job_id = response.json().get("id")
            
            # Wait for job completion
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
                            print(f"✅ Found {len(rows)} tables in elasticsearch source")
                            
                            target_indices = ["application_logs", "user_events", "performance_metrics"]
                            found_indices = []
                            
                            for row in rows:
                                table_name = row.get("TABLE_NAME", "")
                                if table_name in target_indices:
                                    found_indices.append(table_name)
                                    print(f"   ✅ {table_name}")
                            
                            return len(found_indices)
                    elif job_state == "FAILED":
                        print(f"❌ Query failed: {job_response.json().get('errorMessage', 'Unknown error')}")
                        return 0
        
        return 0
    except Exception as e:
        print(f"❌ Error checking indices: {e}")
        return 0

def main():
    print("=" * 70)
    print("🔧 FORCE ELASTICSEARCH METADATA REFRESH IN DREMIO")
    print("=" * 70)
    
    # 1. Authenticate
    print("\n1️⃣ Authenticating with Dremio...")
    try:
        token = get_auth_token()
        print("✅ Authenticated successfully")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # 2. Get source ID
    print(f"\n2️⃣ Getting source ID for '{ES_SOURCE_NAME}'...")
    try:
        source_id = get_source_id(token, ES_SOURCE_NAME)
        if source_id:
            print(f"✅ Source ID: {source_id}")
        else:
            print(f"❌ Source '{ES_SOURCE_NAME}' not found")
            return
    except Exception as e:
        print(f"❌ Failed to get source ID: {e}")
        return
    
    # 3. Try multiple refresh methods
    print(f"\n3️⃣ Attempting to refresh metadata using 4 different methods...")
    
    methods_tried = []
    methods_tried.append(("Method 1: Catalog refresh", method_1_refresh_metadata(token, source_id)))
    time.sleep(2)
    
    methods_tried.append(("Method 2: Source refresh", method_2_refresh_source(token, source_id)))
    time.sleep(2)
    
    methods_tried.append(("Method 3: Config update", method_3_update_source_config(token, source_id)))
    time.sleep(2)
    
    methods_tried.append(("Method 4: SQL queries", method_4_sql_query(token)))
    
    # 4. Wait for metadata to refresh
    print("\n4️⃣ Waiting 10 seconds for metadata to refresh...")
    time.sleep(10)
    
    # 5. Check if indices are visible
    print("\n5️⃣ Checking if indices are now visible...")
    visible_count = check_indices_visible(token)
    
    # 6. Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    print("\nMethods tried:")
    for method_name, success in methods_tried:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {status}: {method_name}")
    
    print(f"\n📈 Indices visible: {visible_count}/3")
    
    if visible_count == 3:
        print("\n🎉 SUCCESS! All 3 indices are now visible!")
        print("\n📝 Next step: Run create_es_vds_fixed.py to create VDS")
        print("   python scripts/create_es_vds_fixed.py")
    elif visible_count > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {visible_count}/3 indices visible")
        print("   Try refreshing again or use manual refresh in Dremio UI")
    else:
        print("\n❌ FAILED: No indices visible yet")
        print("\n📝 Manual action required:")
        print("   1. Open http://localhost:9047")
        print("   2. Go to Sources → elasticsearch")
        print("   3. Click the Refresh button (⟳)")
        print("   4. Wait 30 seconds")
        print("   5. Check if indices appear")

if __name__ == "__main__":
    main()
