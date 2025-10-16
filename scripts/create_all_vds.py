"""Create all Virtual Datasets (VDS) in Dremio for easier access"""
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

def create_vds(token, space, name, sql):
    """Create a VDS in the specified space"""
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    vds_config = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET",
        "path": [space, name],
        "sql": sql,
        "sqlContext": ["@admin"]
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=vds_config,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return True, "Created"
        elif response.status_code == 409:
            return True, "Already exists"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("CREATE ALL VDS - DREMIO")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Authenticated\n")
    
    # Define all VDS to create
    vds_list = [
        # Raw space - direct mappings
        ("raw", "customers", 'SELECT * FROM "PostgreSQL_BusinessDB".public.customers'),
        ("raw", "orders", 'SELECT * FROM "PostgreSQL_BusinessDB".public.orders'),
        ("raw", "minio_sales", 'SELECT * FROM "MinIO_Storage"."sales-data"'),
        ("raw", "minio_sales_2023", 'SELECT * FROM "MinIO_Storage"."sales-data" WHERE "year" = \'2023\''),
        ("raw", "minio_sales_2024", 'SELECT * FROM "MinIO_Storage"."sales-data" WHERE "year" = \'2024\''),
        
        # Analytics space - aggregated views
        ("analytics", "sales_by_year", '''
            SELECT 
                "year",
                COUNT(*) as num_sales,
                SUM(CAST("amount" AS DOUBLE)) as total_amount
            FROM "MinIO_Storage"."sales-data"
            GROUP BY "year"
        '''),
        ("analytics", "customer_orders", '''
            SELECT 
                c.customer_id,
                c.name,
                COUNT(o.order_id) as order_count
            FROM "PostgreSQL_BusinessDB".public.customers c
            LEFT JOIN "PostgreSQL_BusinessDB".public.orders o 
                ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name
        '''),
        ("analytics", "sales_summary", '''
            SELECT 
                "year",
                "month",
                COUNT(*) as daily_sales,
                MIN(CAST("amount" AS DOUBLE)) as min_amount,
                MAX(CAST("amount" AS DOUBLE)) as max_amount,
                AVG(CAST("amount" AS DOUBLE)) as avg_amount
            FROM "MinIO_Storage"."sales-data"
            GROUP BY "year", "month"
        '''),
    ]
    
    print(f"Creating {len(vds_list)} VDS...\n")
    
    results = []
    for space, name, sql in vds_list:
        print(f"🔨 {space}.{name}...", end=" ")
        success, message = create_vds(token, space, name, sql)
        results.append((space, name, success, message))
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for _, _, success, _ in results if success)
    print(f"\nTotal: {success_count}/{len(results)} VDS created/verified\n")
    
    # Group by space
    spaces = {}
    for space, name, success, _ in results:
        if space not in spaces:
            spaces[space] = []
        if success:
            spaces[space].append(name)
    
    for space, names in spaces.items():
        print(f"📁 {space}/ ({len(names)} VDS)")
        for name in names:
            print(f"   - {name}")
    
    print("\n💡 Access VDS in SQL:")
    print('   SELECT * FROM raw.minio_sales LIMIT 10;')
    print('   SELECT * FROM analytics.sales_by_year;')
    print("\n🌐 Dremio UI: http://localhost:9047")

if __name__ == "__main__":
    main()
