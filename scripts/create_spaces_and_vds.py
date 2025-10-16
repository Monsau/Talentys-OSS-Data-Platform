"""Create Dremio spaces and VDS"""
import requests
import time

DREMIO_URL = "http://localhost:9047"

def login():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"] if response.status_code == 200 else None

def create_space(token, space_name):
    """Create a space in Dremio"""
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
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
        return True, "Created"
    elif response.status_code == 409:
        return True, "Already exists"
    else:
        return False, f"Error {response.status_code}"

def create_vds(token, space, name, sql):
    """Create VDS"""
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    vds_config = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET",
        "path": [space, name],
        "sql": sql,
        "sqlContext": ["@admin"]
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=vds_config
    )
    
    if response.status_code in [200, 201]:
        return True, "Created"
    elif response.status_code == 409:
        return True, "Already exists"
    else:
        return False, f"Error {response.status_code}"

def main():
    print("=" * 60)
    print("CREATE SPACES + VDS - DREMIO")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Authenticated\n")
    
    # Create spaces
    print("STEP 1: Creating spaces...")
    spaces = ["raw", "staging", "analytics", "marts"]
    
    for space in spaces:
        success, msg = create_space(token, space)
        status = "✅" if success else "❌"
        print(f"  {status} {space}: {msg}")
    
    time.sleep(2)
    
    # Create VDS
    print("\nSTEP 2: Creating VDS in 'raw' space...")
    
    vds_list = [
        ("raw", "customers", 'SELECT * FROM "PostgreSQL_BusinessDB".public.customers'),
        ("raw", "orders", 'SELECT * FROM "PostgreSQL_BusinessDB".public.orders'),
        ("raw", "minio_sales", 'SELECT * FROM "MinIO_Storage"."sales-data"'),
        ("raw", "es_logs", 'SELECT * FROM "Elasticsearch_Logs".application_logs'),
        ("raw", "es_events", 'SELECT * FROM "Elasticsearch_Logs".user_events'),
        ("raw", "es_metrics", 'SELECT * FROM "Elasticsearch_Logs".system_metrics'),
    ]
    
    success_count = 0
    for space, name, sql in vds_list:
        success, msg = create_vds(token, space, name, sql)
        status = "✅" if success else "❌"
        print(f"  {status} {space}.{name}: {msg}")
        if success:
            success_count += 1
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Spaces: {len(spaces)} created/verified")
    print(f"✅ VDS: {success_count}/{len(vds_list)} created")
    print("\n💡 Test with:")
    print("   SELECT * FROM raw.minio_sales LIMIT 10;")
    print("   SELECT * FROM raw.es_logs LIMIT 10;")

if __name__ == "__main__":
    main()
