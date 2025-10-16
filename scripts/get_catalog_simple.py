#!/usr/bin/env python3
"""Simple script to get Elasticsearch source ID and refresh it"""

import requests
import json

DREMIO_URL = "http://localhost:9047"

# Authenticate
print("1. Authenticating...")
response = requests.post(
    f"{DREMIO_URL}/apiv2/login",
    json={"userName": "admin", "password": "admin123"}
)
token = response.json()["token"]
print(f"✅ Token: {token[:20]}...")

headers = {"Authorization": f"_dremio{token}"}

# Get catalog
print("\n2. Getting catalog...")
response = requests.get(f"{DREMIO_URL}/api/v3/catalog", headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    catalog = response.json()
    print(f"✅ Catalog retrieved")
    print(json.dumps(catalog, indent=2))
