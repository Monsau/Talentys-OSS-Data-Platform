#!/usr/bin/env python3
"""
Script pour créer les buckets MinIO et y déposer des données d'exemple.
"""

import json
import csv
import io
from minio import Minio
from minio.error import S3Error
from datetime import datetime, timedelta
import random

# Configuration MinIO
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minio_admin"
MINIO_SECRET_KEY = "minio_password"

def create_minio_client():
    """Créer le client MinIO"""
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def create_buckets(client):
    """Créer les buckets nécessaires"""
    buckets = ["raw-data", "staging-data", "analytics-data"]
    
    print("🗂️ Création des buckets MinIO...")
    for bucket in buckets:
        try:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"✅ Bucket '{bucket}' créé")
            else:
                print(f"ℹ️ Bucket '{bucket}' existe déjà")
        except S3Error as e:
            print(f"❌ Erreur création bucket '{bucket}': {e}")

def generate_sales_data():
    """Générer des données de ventes au format CSV"""
    categories = ["Electronics", "Books", "Clothing", "Home & Garden", "Toys"]
    products = {
        "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Camera"],
        "Books": ["Fiction", "Science", "History", "Biography", "Self-Help"],
        "Clothing": ["Shirt", "Pants", "Dress", "Jacket", "Shoes"],
        "Home & Garden": ["Furniture", "Decor", "Tools", "Plants", "Lighting"],
        "Toys": ["Action Figure", "Board Game", "Puzzle", "Doll", "Building Set"]
    }
    
    sales = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(1, 401):  # 400 ventes
        category = random.choice(categories)
        product = random.choice(products[category])
        sale_date = base_date + timedelta(days=random.randint(0, 365))
        
        sales.append({
            "sale_id": i,
            "sale_date": sale_date.strftime("%Y-%m-%d"),
            "category": category,
            "product_name": product,
            "quantity": random.randint(1, 10),
            "unit_price": round(random.uniform(10, 500), 2),
            "discount": round(random.uniform(0, 0.3), 2),
            "region": random.choice(["North", "South", "East", "West", "Central"])
        })
    
    return sales

def generate_inventory_data():
    """Générer des données d'inventaire au format JSON"""
    warehouses = ["WH-001", "WH-002", "WH-003", "WH-004"]
    categories = ["Electronics", "Books", "Clothing", "Home & Garden", "Toys"]
    
    inventory = []
    
    for wh in warehouses:
        for i, cat in enumerate(categories, start=1):
            inventory.append({
                "warehouse_id": wh,
                "product_category": cat,
                "sku": f"SKU-{wh[-3:]}-{i:03d}",
                "quantity_available": random.randint(50, 500),
                "quantity_reserved": random.randint(0, 100),
                "reorder_point": random.randint(20, 100),
                "last_updated": datetime.now().isoformat()
            })
    
    return inventory

def upload_csv_to_minio(client, bucket, object_name, data, fieldnames):
    """Upload CSV data to MinIO"""
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    try:
        client.put_object(
            bucket,
            object_name,
            io.BytesIO(csv_bytes),
            len(csv_bytes),
            content_type="text/csv"
        )
        print(f"✅ Fichier '{object_name}' uploadé dans '{bucket}' ({len(data)} lignes)")
        return True
    except S3Error as e:
        print(f"❌ Erreur upload '{object_name}': {e}")
        return False

def upload_json_to_minio(client, bucket, object_name, data):
    """Upload JSON data to MinIO"""
    json_str = json.dumps(data, indent=2)
    json_bytes = json_str.encode('utf-8')
    
    try:
        client.put_object(
            bucket,
            object_name,
            io.BytesIO(json_bytes),
            len(json_bytes),
            content_type="application/json"
        )
        print(f"✅ Fichier '{object_name}' uploadé dans '{bucket}' ({len(data)} objets)")
        return True
    except S3Error as e:
        print(f"❌ Erreur upload '{object_name}': {e}")
        return False

def create_parquet_sample(client):
    """Créer un exemple de fichier Parquet (nécessite pandas et pyarrow)"""
    try:
        import pandas as pd
        
        # Données d'exemple pour le web logs
        logs_data = {
            "timestamp": [datetime.now() - timedelta(hours=i) for i in range(100)],
            "user_id": [f"user_{random.randint(1, 50)}" for _ in range(100)],
            "page": [random.choice(["/home", "/products", "/cart", "/checkout", "/profile"]) for _ in range(100)],
            "duration_seconds": [random.randint(5, 300) for _ in range(100)],
            "device": [random.choice(["desktop", "mobile", "tablet"]) for _ in range(100)]
        }
        
        df = pd.DataFrame(logs_data)
        
        # Convertir en Parquet
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_bytes = parquet_buffer.getvalue()
        
        client.put_object(
            "raw-data",
            "web_logs/logs.parquet",
            io.BytesIO(parquet_bytes),
            len(parquet_bytes),
            content_type="application/octet-stream"
        )
        print(f"✅ Fichier 'web_logs/logs.parquet' uploadé dans 'raw-data' ({len(df)} lignes)")
        return True
        
    except ImportError:
        print("⚠️ Pandas/PyArrow non disponible, skip fichier Parquet")
        return False
    except Exception as e:
        print(f"❌ Erreur création Parquet: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 SETUP MINIO - DONNÉES D'EXEMPLE")
    print("=" * 60)
    
    try:
        # Créer le client MinIO
        client = create_minio_client()
        print("✅ Connexion MinIO établie")
        
        # Créer les buckets
        create_buckets(client)
        
        # Générer et uploader les données de ventes (CSV)
        print("\n📊 Génération des données de ventes...")
        sales_data = generate_sales_data()
        upload_csv_to_minio(
            client,
            "raw-data",
            "sales/sales_2024.csv",
            sales_data,
            ["sale_id", "sale_date", "category", "product_name", "quantity", "unit_price", "discount", "region"]
        )
        
        # Générer et uploader les données d'inventaire (JSON)
        print("\n📦 Génération des données d'inventaire...")
        inventory_data = generate_inventory_data()
        upload_json_to_minio(
            client,
            "raw-data",
            "inventory/inventory_snapshot.json",
            inventory_data
        )
        
        # Créer un fichier Parquet (optionnel)
        print("\n📄 Génération des logs web (Parquet)...")
        create_parquet_sample(client)
        
        # Liste des fichiers créés
        print("\n" + "=" * 60)
        print("📋 FICHIERS CRÉÉS DANS MINIO")
        print("=" * 60)
        
        for bucket in ["raw-data", "staging-data", "analytics-data"]:
            print(f"\n🗂️ Bucket: {bucket}")
            try:
                objects = client.list_objects(bucket, recursive=True)
                for obj in objects:
                    print(f"   - {obj.object_name} ({obj.size} bytes)")
            except S3Error:
                print(f"   (vide)")
        
        print("\n✅ Setup MinIO terminé avec succès!")
        print(f"🌐 Console MinIO: http://localhost:9001")
        print(f"🔑 Credentials: {MINIO_ACCESS_KEY}/{MINIO_SECRET_KEY}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
