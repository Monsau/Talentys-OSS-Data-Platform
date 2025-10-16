#!/usr/bin/env python3
"""
Teste les VDS MinIO créés dans Dremio
"""

import requests

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def authenticate():
    """Authentification"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD},
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json().get("token")
        return {
            "Authorization": f"_dremio{token}",
            "Content-Type": "application/json"
        }
    return None

def test_vds(headers, sql, name):
    """Tester un VDS"""
    print(f"\n🧪 Test: {name}")
    print(f"   SQL: {sql[:80]}...")
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            json={"sql": sql},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            row_count = len(result.get("rows", []))
            print(f"✅ OK - {row_count} lignes")
            if row_count > 0:
                print(f"   Échantillon: {result['rows'][0]}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("=" * 70)
    print("🧪 TEST DES VDS MINIO")
    print("=" * 70)
    
    headers = authenticate()
    if not headers:
        print("❌ Authentification échouée")
        return False
    
    tests = [
        ("raw.minio_sales", 'SELECT COUNT(*) as cnt FROM raw.minio_sales'),
        ("raw.minio_customers_external", 'SELECT COUNT(*) as cnt FROM raw.minio_customers_external'),
        ("analytics.sales_by_region", 'SELECT * FROM analytics.sales_by_region LIMIT 3'),
        ("analytics.top_products", 'SELECT * FROM analytics.top_products LIMIT 3'),
    ]
    
    success_count = 0
    for name, sql in tests:
        if test_vds(headers, sql, name):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"📋 RÉSULTAT: {success_count}/{len(tests)} tests réussis")
    print("=" * 70)
    
    return success_count == len(tests)

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
