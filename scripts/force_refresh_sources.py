"""Force refresh of all Dremio sources to make them visible"""
import requests
import time

DREMIO_URL = "http://localhost:9047"

def login():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["token"]
    return None

def refresh_source(token, source_name):
    """Refresh a source using API v2"""
    headers = {"Authorization": f"_dremio{token}"}
    
    print(f"\n🔄 Rafraîchissement: {source_name}...")
    
    # Method 1: Try API v2 refresh
    url = f"{DREMIO_URL}/apiv2/source/{source_name}/refresh"
    response = requests.post(url, headers=headers, timeout=30)
    
    if response.status_code in [200, 204]:
        print(f"   ✅ Refresh réussi (API v2)")
        return True
    elif response.status_code == 404:
        print(f"   ⚠️ Source introuvable dans API v2")
        
        # Method 2: Try to get and update via API v3
        url_v3 = f"{DREMIO_URL}/api/v3/catalog/by-path/{source_name}"
        get_response = requests.get(url_v3, headers=headers, timeout=10)
        
        if get_response.status_code == 200:
            source_data = get_response.json()
            source_id = source_data.get("id")
            
            print(f"   ℹ️ Source trouvée dans API v3 (ID: {source_id})")
            
            # Try refresh with ID
            refresh_url = f"{DREMIO_URL}/api/v3/catalog/{source_id}/refresh"
            refresh_response = requests.post(
                refresh_url, 
                headers=headers,
                json={"refreshDataset": True, "force": True},
                timeout=60
            )
            
            if refresh_response.status_code in [200, 204]:
                print(f"   ✅ Refresh réussi (API v3 avec ID)")
                return True
            else:
                print(f"   ❌ Refresh échoué: {refresh_response.status_code}")
                if refresh_response.text:
                    print(f"      {refresh_response.text[:200]}")
        else:
            print(f"   ❌ Source introuvable: {get_response.status_code}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        if response.text:
            print(f"      {response.text[:200]}")
    
    return False

def main():
    print("=" * 60)
    print("FORCE REFRESH - DREMIO SOURCES")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ Login échoué")
        return
    
    print("✅ Authentification OK\n")
    
    sources = [
        "PostgreSQL_BusinessDB",
        "MinIO_Storage",
        "Elasticsearch_Logs"
    ]
    
    results = {}
    for source in sources:
        results[source] = refresh_source(token, source)
        time.sleep(2)  # Wait between refreshes
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    for source, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {source}")
    
    print("\n💡 Attendez 10-15 secondes puis vérifiez dans l'UI Dremio:")
    print("   http://localhost:9047")

if __name__ == "__main__":
    main()
