#!/usr/bin/env python3
"""Force refresh of Elasticsearch source using correct API v3 endpoint"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"
ES_SOURCE_ID = "f2befe5f-c877-4b27-8e39-b4616189c170"

# Authenticate
print("1️⃣ Authenticating...")
response = requests.post(
    f"{DREMIO_URL}/apiv2/login",
    json={"userName": "admin", "password": "admin123"}
)
token = response.json()["token"]
print(f"✅ Authenticated")

headers = {
    "Authorization": f"_dremio{token}",
    "Content-Type": "application/json"
}

# Method 1: Try POST /api/v3/catalog/{id}/refresh
print("\n2️⃣ Method 1: POST /api/v3/catalog/{id}/refresh...")
try:
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog/{ES_SOURCE_ID}/refresh",
        headers=headers,
        json={}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201, 204]:
        print("✅ Refresh initiated!")
    else:
        print(f"⚠️  Status {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Method 2: Try PUT /api/v3/catalog/{id}/refresh
print("\n3️⃣ Method 2: PUT /api/v3/catalog/{id}/refresh...")
try:
    response = requests.put(
        f"{DREMIO_URL}/api/v3/catalog/{ES_SOURCE_ID}/refresh",
        headers=headers,
        json={}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201, 204]:
        print("✅ Refresh initiated!")
    else:
        print(f"⚠️  Status {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Method 3: Try GET elasticsearch to see children
print("\n4️⃣ Method 3: GET /api/v3/catalog/{id} to see children...")
try:
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog/{ES_SOURCE_ID}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        children = data.get("children", [])
        print(f"✅ Found {len(children)} children")
        
        if children:
            print("\nChildren:")
            for child in children[:10]:  # Show first 10
                print(f"  - {child.get('path', [])} (type: {child.get('type')})")
        else:
            print("⚠️  No children found - metadata not loaded yet")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Wait and check again
print("\n5️⃣ Waiting 5 seconds then checking again...")
time.sleep(5)

try:
    response = requests.get(
        f"{DREMIO_URL}/api/v3/catalog/{ES_SOURCE_ID}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        children = data.get("children", [])
        print(f"✅ Now found {len(children)} children")
        
        if children:
            target_indices = ["application_logs", "user_events", "performance_metrics"]
            found = []
            
            print("\nLooking for target indices:")
            for child in children:
                path = child.get("path", [])
                if len(path) > 1 and path[1] in target_indices:
                    found.append(path[1])
                    print(f"  ✅ {path[1]}")
            
            print(f"\n📊 Found {len(found)}/3 target indices")
            
            if len(found) == 3:
                print("\n🎉 SUCCESS! All indices are visible!")
                print("\n📝 Next step: Create VDS")
                print("   python scripts/create_es_vds_fixed.py")
            else:
                missing = [idx for idx in target_indices if idx not in found]
                print(f"\n⚠️  Missing indices: {missing}")
                print("\n📝 Manual refresh needed in Dremio UI:")
                print("   http://localhost:9047 → Sources → elasticsearch → Refresh (⟳)")
        else:
            print("\n❌ Still no children found")
            print("\n📝 MANUAL ACTION REQUIRED:")
            print("   1. Open http://localhost:9047")
            print("   2. Click on 'elasticsearch' source")
            print("   3. Click the Refresh button (⟳ icon)")
            print("   4. Wait 30-60 seconds")
            print("   5. Re-run this script to verify")
except Exception as e:
    print(f"❌ Error: {e}")
