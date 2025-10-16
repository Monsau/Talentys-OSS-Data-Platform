"""Quick test of MinIO data access via VDS"""
import requests
import time

DREMIO_URL = "http://localhost:9047"

def login():
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": "admin", "password": "admin123"}
    )
    return response.json()["token"] if response.status_code == 200 else None

def execute_sql(token, sql, description):
    """Execute SQL and return results"""
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    print(f"\n🔍 {description}")
    print(f"   SQL: {sql[:80]}...")
    
    # Submit job
    response = requests.post(
        f"{DREMIO_URL}/api/v3/sql",
        headers=headers,
        json={"sql": sql}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        return False
    
    job_id = response.json().get("id")
    print(f"   Job: {job_id[:8]}...", end="", flush=True)
    
    # Wait for completion
    for i in range(20):
        time.sleep(0.5)
        status_response = requests.get(f"{DREMIO_URL}/api/v3/job/{job_id}", headers=headers)
        
        if status_response.status_code == 200:
            state = status_response.json().get("jobState")
            if state == "COMPLETED":
                row_count = status_response.json().get("rowCount", 0)
                print(f" ✅ {row_count} rows")
                return True
            elif state in ["FAILED", "CANCELLED"]:
                error = status_response.json().get("errorMessage", "Unknown")
                print(f" ❌ {state}: {error[:60]}")
                return False
    
    print(" ⏱️ Timeout")
    return False

def main():
    print("=" * 70)
    print("TEST MINIO ACCESS VIA VDS")
    print("=" * 70)
    
    token = login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Authenticated")
    
    # Test queries
    tests = [
        ("Count all sales", "SELECT COUNT(*) FROM raw.minio_sales"),
        ("Sales 2023", "SELECT COUNT(*) FROM raw.minio_sales_2023"),
        ("Sales 2024", "SELECT COUNT(*) FROM raw.minio_sales_2024"),
        ("Sample data", "SELECT * FROM raw.minio_sales LIMIT 5"),
        ("PostgreSQL customers", "SELECT COUNT(*) FROM raw.customers"),
        ("PostgreSQL orders", "SELECT COUNT(*) FROM raw.orders"),
    ]
    
    results = []
    for description, sql in tests:
        success = execute_sql(token, sql, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n✅ {success_count}/{len(results)} queries successful\n")
    
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    if success_count == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("   MinIO data is fully accessible via Dremio VDS")
    else:
        print("\n⚠️ Some tests failed")

if __name__ == "__main__":
    main()
