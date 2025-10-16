"""Test SQL query on MinIO data in Dremio"""
import requests
import json
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

def execute_sql(token, sql):
    """Execute SQL query via Dremio API"""
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    # Submit job
    job_payload = {
        "sql": sql
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/sql",
        headers=headers,
        json=job_payload
    )
    
    if response.status_code != 200:
        return False, f"Error {response.status_code}: {response.text[:300]}"
    
    job_data = response.json()
    job_id = job_data.get("id")
    
    if not job_id:
        return False, "No job ID returned"
    
    # Wait for job completion
    print(f"   Job ID: {job_id}")
    print("   Waiting for completion...", end="", flush=True)
    
    for i in range(30):  # Max 30 seconds
        time.sleep(1)
        print(".", end="", flush=True)
        
        status_response = requests.get(
            f"{DREMIO_URL}/api/v3/job/{job_id}",
            headers=headers
        )
        
        if status_response.status_code == 200:
            job_status = status_response.json()
            state = job_status.get("jobState")
            
            if state == "COMPLETED":
                print(" ✅")
                row_count = job_status.get("rowCount", 0)
                return True, f"Success - {row_count} rows"
            elif state in ["FAILED", "CANCELLED"]:
                print(" ❌")
                error = job_status.get("errorMessage", "Unknown error")
                return False, f"Job {state}: {error}"
    
    print(" ⏱️")
    return False, "Timeout waiting for job completion"

def main():
    print("=" * 60)
    print("TEST SQL - MINIO DATA IN DREMIO")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Authentifié\n")
    
    queries = [
        ("PostgreSQL - customers", 'SELECT COUNT(*) FROM "PostgreSQL_BusinessDB".public.customers'),
        ("PostgreSQL - orders", 'SELECT COUNT(*) FROM "PostgreSQL_BusinessDB".public.orders'),
        ("MinIO - sales-data", 'SELECT COUNT(*) FROM "MinIO_Storage"."sales-data"'),
        ("MinIO - avec partition", 'SELECT COUNT(*) FROM "MinIO_Storage"."sales-data" WHERE "year" = \'2023\''),
        ("Elasticsearch - application_logs", 'SELECT COUNT(*) FROM "Elasticsearch_Logs".application_logs'),
    ]
    
    results = []
    
    for name, sql in queries:
        print(f"\n🔍 Test: {name}")
        print(f"   SQL: {sql[:70]}...")
        success, message = execute_sql(token, sql)
        results.append((name, success, message))
        
        status = "✅" if success else "❌"
        print(f"   {status} {message}")
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    for name, success, message in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")
    
    print("\n💡 Si MinIO fonctionne, les données SONT accessibles!")
    print("   Le problème d'API listing est un bug Dremio 26")

if __name__ == "__main__":
    main()
