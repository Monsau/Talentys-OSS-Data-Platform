#!/usr/bin/env python3
"""
Configure OpenSearch source in Dremio
OpenSearch is 100% compatible with Elasticsearch connector in Dremio
"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"

def authenticate():
    """Authenticate with Dremio"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    )
    return response.json()["token"]

def create_opensearch_source(token):
    """Create OpenSearch source in Dremio"""
    
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # OpenSearch configuration (uses ELASTIC type in Dremio)
    source_config = {
        "entityType": "source",
        "name": "opensearch",
        "type": "ELASTIC",  # Dremio uses ELASTIC type for both ES and OpenSearch
        "config": {
            "hostList": [
                {
                    "hostname": "opensearch",
                    "port": 9200
                }
            ],
            "authenticationType": "ANONYMOUS",  # No authentication (DISABLE_SECURITY_PLUGIN=true)
            "sslEnabled": False,
            "showHiddenIndices": False,
            "showIdColumn": False,
            "scrollSize": 4000,
            "readTimeoutMillis": 60000,
            "scrollTimeoutMillis": 300000,
            "usePainless": True,
            "useWhitelist": False,
            "scriptsEnabled": True,
            "allowPushdownOnNormalizedOrAnalyzedFields": True,
            "warnOnRowCountMismatch": False
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 60000,  # 1 minute (faster refresh)
            "datasetRefreshAfterMs": 60000,
            "datasetExpireAfterMs": 180000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": False
        }
    }
    
    print("\n📝 Creating OpenSearch source in Dremio...")
    print(f"   Configuration: {json.dumps(source_config['config'], indent=2)}")
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=source_config
    )
    
    if response.status_code in [200, 201]:
        source_data = response.json()
        source_id = source_data.get('id')
        print(f"\n✅ OpenSearch source created successfully!")
        print(f"   Source ID: {source_id}")
        print(f"   Name: {source_data.get('name')}")
        return source_id
    else:
        print(f"\n❌ Failed to create source: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def wait_for_metadata_scan(token, source_id, max_wait=120):
    """Wait for OpenSearch metadata to be scanned"""
    
    headers = {"Authorization": f"_dremio{token}"}
    
    print(f"\n⏳ Waiting for metadata scan (max {max_wait}s)...")
    
    for i in range(max_wait // 5):
        time.sleep(5)
        
        try:
            response = requests.get(
                f"{DREMIO_URL}/api/v3/catalog/{source_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                children = data.get('children', [])
                
                if children:
                    print(f"\n✅ Found {len(children)} indices!")
                    
                    # List indices
                    target_indices = ['application_logs', 'user_events', 'performance_metrics']
                    found_indices = []
                    
                    for child in children:
                        path = child.get('path', [])
                        if len(path) > 1:
                            index_name = path[1]
                            if index_name in target_indices:
                                found_indices.append(index_name)
                                print(f"   ✅ {index_name}")
                    
                    if len(found_indices) == 3:
                        print(f"\n🎉 All 3 target indices found!")
                        return True
                    else:
                        missing = [idx for idx in target_indices if idx not in found_indices]
                        print(f"\n⚠️  Missing indices: {missing}")
                        print(f"   Waiting... (attempt {i+1}/{max_wait//5})")
                else:
                    print(f"   No indices yet (attempt {i+1}/{max_wait//5})")
        except Exception as e:
            print(f"   Error checking: {e}")
    
    print(f"\n⚠️  Timeout waiting for indices to appear")
    return False

def main():
    print("=" * 70)
    print("🚀 CONFIGURE OPENSEARCH IN DREMIO")
    print("=" * 70)
    
    try:
        # 1. Authenticate
        print("\n1️⃣ Authenticating with Dremio...")
        token = authenticate()
        print("✅ Authenticated")
        
        # 2. Create OpenSearch source
        print("\n2️⃣ Creating OpenSearch source...")
        source_id = create_opensearch_source(token)
        
        if not source_id:
            print("\n❌ Failed to create OpenSearch source")
            return False
        
        # 3. Wait for metadata scan
        print("\n3️⃣ Waiting for metadata scan...")
        if wait_for_metadata_scan(token, source_id):
            print("\n✅ OpenSearch source ready!")
            
            print("\n📝 Next steps:")
            print("   1. Create VDS: python scripts/create_opensearch_vds.py")
            print("   2. Run dbt: ./run_dbt.sh")
            print("   3. Generate docs: ./generate_dbt_docs.sh")
            
            return True
        else:
            print("\n⚠️  Metadata scan incomplete")
            print("\n📝 Manual action:")
            print("   1. Open http://localhost:9047")
            print("   2. Go to Sources → opensearch")
            print("   3. Wait for indices to appear (auto-refresh in 1 min)")
            print("   4. If not visible, click Refresh button")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
