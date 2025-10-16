#!/usr/bin/env python3
import requests
import json

DREMIO_URL = "http://localhost:9047"
token = "of8vc45q4muejn5qk364elbmft"

headers = {
    "Authorization": f"_dremio{token}",
    "Content-Type": "application/json"
}

# Test direct query
sql = 'SELECT * FROM elasticsearch.application_logs LIMIT 5'
print(f"Testing query: {sql}")

response = requests.post(
    f"{DREMIO_URL}/api/v3/sql",
    headers=headers,
    json={"sql": sql}
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
