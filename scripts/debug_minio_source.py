"""Debug MinIO source in Dremio - check all APIs"""
import requests
import json

print("=" * 60)
print("DEBUG: MINIO SOURCE IN DREMIO")
print("=" * 60)

# Login
print("\n1️⃣ Login...")
login_response = requests.post(
    "http://localhost:9047/apiv2/login",
    json={"userName": "admin", "password": "admin123"},
    timeout=10
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json().get("token")
headers = {"Authorization": f"_dremio{token}"}
print("✅ Login OK")

# Check API v2 sources
print("\n2️⃣ API v2 - /apiv2/sources")
sources_response = requests.get(
    "http://localhost:9047/apiv2/sources",
    headers=headers,
    timeout=10
)

if sources_response.status_code == 200:
    sources = sources_response.json().get("data", [])
    print(f"   Total sources: {len(sources)}")
    for src in sources:
        print(f"   - {src.get('name')} (type: {src.get('type')})")
        
    minio = next((s for s in sources if s.get("name") == "MinIO_Storage"), None)
    if minio:
        print("\n   ✅ MinIO_Storage trouvé dans API v2")
        print(f"   Config: {json.dumps(minio.get('config', {}), indent=2)}")
    else:
        print("\n   ❌ MinIO_Storage PAS trouvé dans API v2")
else:
    print(f"   ❌ Error: {sources_response.status_code}")

# Check API v3 catalog
print("\n3️⃣ API v3 - /api/v3/catalog")
catalog_response = requests.get(
    "http://localhost:9047/api/v3/catalog",
    headers=headers,
    timeout=10
)

if catalog_response.status_code == 200:
    catalog = catalog_response.json().get("data", [])
    print(f"   Total items: {len(catalog)}")
    
    sources_v3 = [item for item in catalog if item.get("entityType") == "source"]
    print(f"   Sources: {len(sources_v3)}")
    for src in sources_v3:
        print(f"   - {src.get('path', ['unknown'])[0]}")
        
    minio_v3 = next((s for s in sources_v3 if "MinIO" in str(s.get("path", []))), None)
    if minio_v3:
        print("\n   ✅ MinIO_Storage trouvé dans API v3")
        print(f"   Path: {minio_v3.get('path')}")
        print(f"   ID: {minio_v3.get('id')}")
    else:
        print("\n   ❌ MinIO_Storage PAS trouvé dans API v3")
else:
    print(f"   ❌ Error: {catalog_response.status_code}")

# Try to get MinIO_Storage directly
print("\n4️⃣ Direct access - /api/v3/catalog/by-path/MinIO_Storage")
direct_response = requests.get(
    "http://localhost:9047/api/v3/catalog/by-path/MinIO_Storage",
    headers=headers,
    timeout=10
)

if direct_response.status_code == 200:
    minio_direct = direct_response.json()
    print("   ✅ MinIO_Storage accessible directement")
    print(f"   Type: {minio_direct.get('type')}")
    print(f"   Entity Type: {minio_direct.get('entityType')}")
    
    # Check children (buckets)
    children = minio_direct.get("children", [])
    print(f"\n   Enfants (buckets): {len(children)}")
    for child in children:
        print(f"   - {child.get('path', ['unknown'])[-1]}")
        
    if not children:
        print("   ⚠️ AUCUN BUCKET visible dans la source MinIO!")
        print("   -> Besoin de rafraîchir les métadonnées")
        
elif direct_response.status_code == 404:
    print("   ❌ MinIO_Storage n'existe pas (404)")
else:
    print(f"   ❌ Error: {direct_response.status_code} - {direct_response.text[:200]}")

# Try to refresh metadata
print("\n5️⃣ Rafraîchissement des métadonnées...")
refresh_response = requests.post(
    "http://localhost:9047/api/v3/catalog/MinIO_Storage/refresh",
    headers=headers,
    json={"refreshDataset": True, "force": True},
    timeout=60
)

if refresh_response.status_code in [200, 204]:
    print("   ✅ Refresh déclenché")
elif refresh_response.status_code == 404:
    print("   ❌ Source not found for refresh")
else:
    print(f"   ⚠️ Status: {refresh_response.status_code}")
    if refresh_response.text:
        print(f"   Response: {refresh_response.text[:200]}")

print("\n" + "=" * 60)
