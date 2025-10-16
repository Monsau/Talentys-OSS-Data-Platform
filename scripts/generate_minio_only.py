#!/usr/bin/env python3
"""
Generateur MinIO Parquet uniquement - 1,095 fichiers
Structure partitionnee year/month/day
"""

from minio import Minio
import pyarrow as pa
import pyarrow.parquet as pq
import random
import datetime
from io import BytesIO

MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minio_admin',
    'secret_key': 'minio_password',
    'secure': False
}

def generate_parquet_files(start_date='2022-01-01', end_date='2024-12-31'):
    """Genere fichiers Parquet partitionnes par date"""
    print(f"Generation de fichiers Parquet (2022-2024)...")
    print(f"Structure: sales-data/year=YYYY/month=MM/day=DD/*.parquet")
    print()
    
    client = Minio(**MINIO_CONFIG)
    
    # Creer bucket si necessaire
    bucket_name = 'sales-data'
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"[OK] Bucket '{bucket_name}' cree")
    
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    total_files = 0
    total_records = 0
    current_date = start
    
    while current_date <= end:
        year = current_date.year
        month = current_date.month
        day = current_date.day
        
        # Saisonnalite: plus de ventes en Q4
        if month in [11, 12]:
            num_sales = random.randint(50, 150)  # Black Friday, Noel
        elif month in [1, 7]:
            num_sales = random.randint(30, 80)   # Soldes
        else:
            num_sales = random.randint(10, 50)   # Normal
        
        # Generer donnees ventes pour ce jour
        sales_data = []
        for _ in range(num_sales):
            sale = {
                'sale_id': f"{year}{month:02d}{day:02d}_{random.randint(1000, 9999)}",
                'customer_id': random.randint(1, 1000),
                'product_id': random.randint(1, 500),
                'quantity': random.randint(1, 10),
                'unit_price': round(random.uniform(5, 500), 2),
                'total_amount': 0,  # Calcule apres
                'sale_date': current_date.strftime('%Y-%m-%d'),
                'payment_method': random.choice(['credit_card', 'paypal', 'bank_transfer', 'cash']),
                'store_id': random.randint(1, 20),
                'region': random.choice(['North', 'South', 'East', 'West', 'Central'])
            }
            sale['total_amount'] = round(sale['quantity'] * sale['unit_price'], 2)
            sales_data.append(sale)
        
        # Creer table PyArrow
        table = pa.table({
            'sale_id': [s['sale_id'] for s in sales_data],
            'customer_id': [s['customer_id'] for s in sales_data],
            'product_id': [s['product_id'] for s in sales_data],
            'quantity': [s['quantity'] for s in sales_data],
            'unit_price': [s['unit_price'] for s in sales_data],
            'total_amount': [s['total_amount'] for s in sales_data],
            'sale_date': [s['sale_date'] for s in sales_data],
            'payment_method': [s['payment_method'] for s in sales_data],
            'store_id': [s['store_id'] for s in sales_data],
            'region': [s['region'] for s in sales_data]
        })
        
        # Ecrire Parquet en memoire
        buffer = BytesIO()
        pq.write_table(table, buffer, compression='snappy')
        buffer.seek(0)
        
        # Upload vers MinIO avec structure partitionnee
        object_name = f"year={year}/month={month:02d}/day={day:02d}/sales_{year}{month:02d}{day:02d}.parquet"
        
        client.put_object(
            bucket_name,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        total_files += 1
        total_records += len(sales_data)
        
        # Progress tous les 100 fichiers
        if total_files % 100 == 0:
            print(f"   [Progress] {total_files} fichiers, {total_records} ventes")
        
        current_date += datetime.timedelta(days=1)
    
    print()
    print(f"[OK] {total_files} fichiers Parquet crees")
    print(f"[OK] {total_records} ventes generees")
    return total_files, total_records


def verify_minio_data():
    """Verifie les donnees MinIO"""
    print()
    print("Verification structure MinIO...")
    
    client = Minio(**MINIO_CONFIG)
    bucket_name = 'sales-data'
    
    # Compter fichiers
    objects = client.list_objects(bucket_name, recursive=True)
    file_count = sum(1 for _ in objects)
    
    print(f"   Bucket: {bucket_name}")
    print(f"   Fichiers: {file_count}")
    
    # Exemples de chemins
    objects = client.list_objects(bucket_name, recursive=True)
    print()
    print("   Exemples de fichiers:")
    for i, obj in enumerate(objects):
        if i < 5:
            print(f"     - {obj.object_name} ({obj.size} bytes)")
        else:
            break
    
    return file_count


if __name__ == '__main__':
    print("=" * 60)
    print("GENERATEUR MINIO PARQUET - Version Rapide")
    print("=" * 60)
    print()
    
    try:
        files, records = generate_parquet_files('2022-01-01', '2024-12-31')
        verified_files = verify_minio_data()
        
        print()
        print("=" * 60)
        print("SUCCES - MinIO alimente")
        print("=" * 60)
        print(f"Fichiers Parquet: {files}")
        print(f"Ventes totales:   {records}")
        print(f"Periode:          2022-2024 (3 ans)")
        print(f"Structure:        year=YYYY/month=MM/day=DD/*.parquet")
        print()
        print("Verification:")
        print("  curl http://localhost:9001/minio/sales-data/")
        print("  ou MinIO Console: http://localhost:9001")
        print()
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
