#!/usr/bin/env python3
"""
Create Elasticsearch VDS directly via SQL API
Bypasses metadata discovery issues by creating VDS with explicit SQL
"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

def authenticate():
    """Authenticate with Dremio"""
    print("🔐 Authenticating with Dremio...")
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    )
    token = response.json()["token"]
    print("✅ Authenticated")
    return token

def execute_sql(token, sql):
    """Execute SQL query in Dremio"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "sql": sql
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/sql",
        headers=headers,
        json=payload
    )
    
    return response

def create_vds_from_sql(token, vds_name, sql_query, path=["raw"]):
    """Create a VDS using SQL definition"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Create VDS
    vds_config = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET",
        "path": path + [vds_name],
        "sql": sql_query,
        "sqlContext": path
    }
    
    print(f"📝 Creating VDS: {vds_name}")
    print(f"   SQL: {sql_query[:100]}...")
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=vds_config
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ VDS '{vds_name}' created successfully")
        return True
    else:
        print(f"❌ Failed to create VDS: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def create_space_if_not_exists(token, space_name="raw"):
    """Create space if it doesn't exist"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📁 Checking space '{space_name}'...")
    
    # Check if space exists
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog/by-path/{space_name}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Space '{space_name}' already exists")
        return True
    
    # Create space
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
    else:
        print(f"⚠️  Could not create space: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🚀 CREATE ELASTICSEARCH VDS - DIRECT SQL METHOD")
    print("=" * 60)
    
    # Authenticate
    token = authenticate()
    
    # Create space
    create_space_if_not_exists(token, "raw")
    
    # Wait a bit
    time.sleep(2)
    
    print("\n📊 Creating Elasticsearch VDS...")
    
    # VDS definitions with direct ES table references
    vds_definitions = [
        {
            "name": "es_application_logs",
            "sql": 'SELECT * FROM elasticsearch.application_logs',
            "description": "Application logs from Elasticsearch"
        },
        {
            "name": "es_user_events",
            "sql": 'SELECT * FROM elasticsearch.user_events',
            "description": "User events from Elasticsearch"
        },
        {
            "name": "es_performance_metrics",
            "sql": 'SELECT * FROM elasticsearch.performance_metrics',
            "description": "Performance metrics from Elasticsearch"
        }
    ]
    
    success_count = 0
    failed_count = 0
    
    for vds_def in vds_definitions:
        try:
            if create_vds_from_sql(
                token,
                vds_def["name"],
                vds_def["sql"],
                path=["raw"]
            ):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ Error creating VDS {vds_def['name']}: {str(e)}")
            failed_count += 1
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ VDS CREATION COMPLETE")
    print("=" * 60)
    print(f"✅ Created: {success_count} VDS")
    print(f"❌ Failed: {failed_count} VDS")
    
    if success_count > 0:
        print("\n📋 Next steps:")
        print("   1. Verify VDS in Dremio UI: http://localhost:9047")
        print("   2. Run dbt models: cd dbt && dbt run")
        print("   3. Run dbt tests: dbt test")
    
    return success_count == len(vds_definitions)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
