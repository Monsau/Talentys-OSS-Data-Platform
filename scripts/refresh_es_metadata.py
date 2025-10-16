#!/usr/bin/env python3
"""Refresh Elasticsearch source metadata in Dremio"""

import requests
import time

DREMIO_URL = "http://localhost:9047"

def get_token():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"]

def get_source_id(token, source_name):
    """Get source ID by name"""
    headers = {"Authorization": f"_dremio{token}"}
    
    response = requests.get(f"{DREMIO_URL}/api/v3/catalog", headers=headers)
    catalog = response.json()
    
    for item in catalog.get("data", []):
        path = item.get("path", [])
        if path and path[0].lower() == source_name.lower():
            return item.get("id")
    return None

def refresh_metadata(token, source_id):
    """Trigger metadata refresh"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Trigger refresh
    response = requests.post(
        f"{DREMIO_URL}/api/v3/source/{source_id}/refresh",
        headers=headers,
        json={}
    )
    
    if response.status_code in [200, 202]:
        print(f"  ✓ Refresh triggered")
        return True
    else:
        print(f"  ✗ Error: {response.status_code} - {response.text[:200]}")
        return False

def main():
    print("=== Elasticsearch Metadata Refresh ===\n")
    
    token = get_token()
    print("✓ Token obtained\n")
    
    # Get Elasticsearch source ID
    print("Searching for Elasticsearch source...")
    es_id = get_source_id(token, "elasticsearch")
    
    if not es_id:
        print("✗ Elasticsearch source not found in catalog")
        print("  Available sources:")
        
        headers = {"Authorization": f"_dremio{token}"}
        response = requests.get(f"{DREMIO_URL}/api/v3/catalog", headers=headers)
        for item in response.json().get("data", []):
            path = item.get("path", [])
            if path:
                print(f"    - {path[0]}")
        return
    
    print(f"✓ Found Elasticsearch source: {es_id}\n")
    
    # Trigger refresh
    print("Triggering metadata refresh...")
    if refresh_metadata(token, es_id):
        print("\n✓ Metadata refresh initiated")
        print("  Note: Refresh is asynchronous, may take 1-2 minutes")
        print("\nWaiting 10 seconds...")
        time.sleep(10)
        print("✓ Done - Metadata should be refreshed soon")
    else:
        print("\n⚠️ Refresh may have failed, but continuing...")

if __name__ == "__main__":
    main()
