"""Verify MinIO data and source configuration"""
from minio import Minio
import requests

print("=" * 60)
print("VERIFICATION MINIO + DREMIO")
print("=" * 60)

# 1. Check MinIO bucket and data
print("\n1️⃣ Verification du bucket MinIO...")
try:
    client = Minio(
        'localhost:9000',
        access_key='minioadmin',
        secret_key='minioadmin123',
        secure=False
    )
    
    bucket_name = 'sales-data'
    
    if client.bucket_exists(bucket_name):
        objects = list(client.list_objects(bucket_name, recursive=True))
        print(f"✅ Bucket '{bucket_name}' existe")
        print(f"   Fichiers: {len(objects)}")
        
        if objects:
            print("\n   Exemples (5 premiers):")
            for i, obj in enumerate(objects[:5]):
                print(f"   - {obj.object_name} ({obj.size} bytes)")
        else:
            print("   ⚠️ AUCUN FICHIER dans le bucket!")
    else:
        print(f"❌ Bucket '{bucket_name}' n'existe pas")
        
except Exception as e:
    print(f"❌ Erreur MinIO: {e}")

# 2. Check Dremio MinIO source
print("\n2️⃣ Verification de la source Dremio 'MinIO_Storage'...")
try:
    # Login
    login_response = requests.post(
        "http://localhost:9047/apiv2/login",
        json={"userName": "admin", "password": "admin123"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Cannot login to Dremio: {login_response.status_code}")
    else:
        token = login_response.json().get("token")
        headers = {"Authorization": f"_dremio{token}"}
        
        # Get sources
        sources_response = requests.get(
            "http://localhost:9047/apiv2/sources",
            headers=headers,
            timeout=10
        )
        
        if sources_response.status_code == 200:
            sources = sources_response.json().get("data", [])
            minio_source = next((s for s in sources if s.get("name") == "MinIO_Storage"), None)
            
            if minio_source:
                print("✅ Source 'MinIO_Storage' existe")
                print(f"   Type: {minio_source.get('type')}")
                config = minio_source.get('config', {})
                print(f"   Access Key: {config.get('accessKey', 'N/A')}")
                print(f"   External Buckets: {config.get('externalBucketList', [])}")
                
                # Try to refresh metadata
                print("\n3️⃣ Rafraichissement des métadonnées...")
                refresh_url = f"http://localhost:9047/apiv2/source/MinIO_Storage/refresh"
                refresh_response = requests.post(refresh_url, headers=headers, timeout=30)
                
                if refresh_response.status_code in [200, 204]:
                    print("✅ Métadonnées rafraichies")
                else:
                    print(f"⚠️ Refresh status: {refresh_response.status_code}")
                    
            else:
                print("❌ Source 'MinIO_Storage' n'existe pas dans Dremio")
        else:
            print(f"❌ Cannot get sources: {sources_response.status_code}")
            
except Exception as e:
    print(f"❌ Erreur Dremio: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC:")
print("=" * 60)
print("\nSi le bucket MinIO est vide:")
print("  -> Exécuter: python scripts/build_complete_ecosystem.py")
print("     (Step 7 génère les données MinIO)")
print("\nSi la source Dremio n'affiche rien:")
print("  1. Vérifier que externalBucketList contient 'sales-data'")
print("  2. Rafraîchir les métadonnées dans l'UI Dremio")
print("  3. Vérifier les credentials (minioadmin/minioadmin123)")
