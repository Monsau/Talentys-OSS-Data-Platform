"""Quick data injection with correct credentials"""
import psycopg2
from minio import Minio
import pandas as pd
from datetime import datetime, timedelta
import io
import random

print("=" * 60)
print("INJECTION RAPIDE DES DONNEES")
print("=" * 60)

# PostgreSQL
print("\n1. PostgreSQL - Customers & Orders...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="business_db",
        user="postgres",
        password="postgres123"
    )
    cursor = conn.cursor()
    
    # Customers
    print("   Creating customers...")
    for i in range(1, 101):
        cursor.execute("""
            INSERT INTO customers (customer_id, name, email, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (customer_id) DO NOTHING
        """, (i, f"Customer_{i}", f"customer{i}@example.com", datetime.now()))
    
    # Orders
    print("   Creating orders...")
    for i in range(1, 501):
        cursor.execute("""
            INSERT INTO orders (order_id, customer_id, amount, order_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """, (i, random.randint(1, 100), round(random.uniform(10, 1000), 2), datetime.now()))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("   ✅ PostgreSQL: 100 customers + 500 orders")
except Exception as e:
    print(f"   ❌ Error: {e}")

# MinIO
print("\n2. MinIO - Sales data...")
try:
    client = Minio(
        'localhost:9000',
        access_key='minioadmin',
        secret_key='minioadmin123',
        secure=False
    )
    
    # Create bucket
    if not client.bucket_exists('sales-data'):
        client.make_bucket('sales-data')
        print("   Bucket sales-data created")
    
    # Generate parquet files
    total_files = 0
    for year in [2023, 2024]:
        for month in range(1, 13):
            for day in range(1, 29):  # 28 days per month for simplicity
                date = datetime(year, month, day)
                
                # Create DataFrame
                data = {
                    'sale_id': range(1, 21),  # 20 sales per day
                    'product_id': [random.randint(1, 50) for _ in range(20)],
                    'customer_id': [random.randint(1, 100) for _ in range(20)],
                    'amount': [round(random.uniform(10, 500), 2) for _ in range(20)],
                    'timestamp': [date] * 20
                }
                df = pd.DataFrame(data)
                
                # Convert to parquet
                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                
                # Upload to MinIO
                object_name = f"year={year}/month={month:02d}/day={day:02d}/sales_{year}{month:02d}{day:02d}.parquet"
                client.put_object(
                    'sales-data',
                    object_name,
                    parquet_buffer,
                    length=len(parquet_buffer.getvalue()),
                    content_type='application/octet-stream'
                )
                total_files += 1
                
                if total_files % 100 == 0:
                    print(f"   Progress: {total_files} files...")
    
    print(f"   ✅ MinIO: {total_files} parquet files (672 files, ~13,440 sales)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("INJECTION TERMINÉE")
print("=" * 60)
print("\n💡 Next: Configure Dremio sources with recreate_sources.py")
