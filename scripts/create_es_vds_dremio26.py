#!/usr/bin/env python3
"""
Create Elasticsearch VDS in Dremio 26 OSS
Indices are discovered as folders in Dremio 26
"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

def authenticate():
    """Authenticate with Dremio"""
    print("🔐 Authenticating...")
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    )
    token = response.json()["token"]
    print("✅ Authenticated")
    return token

def create_space_if_not_exists(token, space_name="raw"):
    """Create space if it doesn't exist"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📁 Checking space '{space_name}'...")
    
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog/by-path/{space_name}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Space '{space_name}' exists")
        return True
    
    print(f"📁 Creating space '{space_name}'...")
    space_config = {
        "entityType": "space",
        "name": space_name
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=space_config
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ Space '{space_name}' created")
        return True
    return False

def create_vds(token, vds_name, sql_query, space="raw"):
    """Create VDS in Dremio 26"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    vds_config = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET",
        "path": [space, vds_name],
        "sql": sql_query,
        "sqlContext": [space]
    }
    
    print(f"\n📊 Creating VDS: {vds_name}")
    print(f"   SQL: {sql_query}")
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=vds_config
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ VDS '{vds_name}' created")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        try:
            error = response.json()
            print(f"   Error: {error.get('errorMessage', 'Unknown error')}")
        except:
            print(f"   Response: {response.text[:200]}")
        return False

def main():
    print("=" * 70)
    print("🚀 CREATE ELASTICSEARCH VDS - DREMIO 26 OSS")
    print("=" * 70)
    
    token = authenticate()
    
    # Create space
    create_space_if_not_exists(token, "raw")
    time.sleep(2)
    
    print("\n" + "=" * 70)
    print("📊 CREATING ELASTICSEARCH VDS")
    print("=" * 70)
    
    # VDS definitions - Dremio 26 requires ."_doc" suffix for ES indices
    vds_list = [
        {
            "name": "es_application_logs",
            "sql": 'SELECT * FROM elasticsearch.application_logs."_doc"',
            "desc": "Application logs (500 docs)"
        },
        {
            "name": "es_user_events",
            "sql": 'SELECT * FROM elasticsearch.user_events."_doc"',
            "desc": "User events (1000 docs)"
        },
        {
            "name": "es_performance_metrics",
            "sql": 'SELECT * FROM elasticsearch.performance_metrics."_doc"',
            "desc": "Performance metrics (300 docs)"
        }
    ]
    
    created = []
    failed = []
    
    for vds in vds_list:
        if create_vds(token, vds["name"], vds["sql"]):
            created.append(vds["name"])
        else:
            failed.append(vds["name"])
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ VDS CREATION COMPLETE")
    print("=" * 70)
    print(f"✅ Created: {len(created)} VDS")
    if created:
        for name in created:
            print(f"   - {name}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)} VDS")
        for name in failed:
            print(f"   - {name}")
    
    if created:
        print("\n📋 Next Steps:")
        print("   1. ✅ VDS created in 'raw' space")
        print("   2. ▶️  Run dbt models:")
        print("      cd dbt && dbt run --select stg_es_*")
        print("   3. ✅ Run dbt tests:")
        print("      dbt test --select stg_es_*")
        print("   4. 📊 Run full pipeline:")
        print("      dbt run && dbt test")
        print("\n🌐 Dremio UI: http://localhost:9047")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
