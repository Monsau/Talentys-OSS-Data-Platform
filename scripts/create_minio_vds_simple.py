#!/usr/bin/env python3
"""
Script simple pour créer uniquement les VDS MinIO dans Dremio.
Suppose que la source MinIO_Storage existe déjà.
"""

import requests
import time

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def authenticate():
    """S'authentifier"""
    print("🔑 Authentification...")
    
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD},
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json().get("token")
        print("✅ Authentifié")
        return {
            "Authorization": f"_dremio{token}",
            "Content-Type": "application/json"
        }
    else:
        print(f"❌ Erreur: {response.status_code}")
        return None

def execute_sql(headers, sql):
    """Exécuter du SQL"""
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            json={"sql": sql},
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            return True, "OK"
        else:
            return False, f"{response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def create_vds(headers, space, name, sql):
    """Créer un VDS"""
    print(f"\n📊 Création '{space}.{name}'...")
    
    # D'abord, supprimer si existe
    drop_sql = f'DROP VIEW IF EXISTS "{space}"."{name}"'
    execute_sql(headers, drop_sql)
    
    # Créer le VDS
    create_sql = f'CREATE VDS "{space}"."{name}" AS {sql}'
    success, msg = execute_sql(headers, create_sql)
    
    if success:
        print(f"✅ '{space}.{name}' créé")
        return True
    else:
        print(f"❌ Erreur: {msg}")
        return False

def main():
    print("=" * 70)
    print("🚀 CRÉATION DES VDS MINIO")
    print("=" * 70)
    
    headers = authenticate()
    if not headers:
        return False
    
    # Liste des VDS à créer
    vds_definitions = [
        {
            "space": "raw",
            "name": "minio_sales",
            "sql": '''
                SELECT 
                    CAST(sale_id AS INTEGER) as sale_id,
                    sale_date,
                    category,
                    product_name,
                    CAST(quantity AS INTEGER) as quantity,
                    CAST(unit_price AS DOUBLE) as unit_price,
                    CAST(discount AS DOUBLE) as discount,
                    region
                FROM "MinIO_Storage"."raw-data".sales."sales_2024.csv"
            '''
        },
        {
            "space": "raw",
            "name": "minio_customers_external",
            "sql": '''
                SELECT *
                FROM "MinIO_Storage"."raw-data".external.customers."customers_external.csv"
            '''
        },
        {
            "space": "analytics",
            "name": "sales_by_region",
            "sql": '''
                SELECT 
                    region,
                    category,
                    COUNT(*) as total_sales,
                    SUM(quantity) as total_quantity,
                    ROUND(SUM(quantity * unit_price * (1 - discount)), 2) as total_revenue,
                    ROUND(AVG(unit_price), 2) as avg_price
                FROM raw.minio_sales
                GROUP BY region, category
                ORDER BY total_revenue DESC
            '''
        },
        {
            "space": "analytics",
            "name": "top_products",
            "sql": '''
                SELECT 
                    category,
                    product_name,
                    COUNT(*) as sale_count,
                    SUM(quantity) as total_qty,
                    ROUND(SUM(quantity * unit_price * (1 - discount)), 2) as revenue
                FROM raw.minio_sales
                GROUP BY category, product_name
                ORDER BY revenue DESC
                LIMIT 20
            '''
        }
    ]
    
    success_count = 0
    for vds in vds_definitions:
        if create_vds(headers, vds["space"], vds["name"], vds["sql"]):
            success_count += 1
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print(f"📋 RÉSUMÉ: {success_count}/{len(vds_definitions)} VDS créés")
    print("=" * 70)
    
    if success_count > 0:
        print("\n📊 VDS disponibles:")
        print("   - raw.minio_sales")
        print("   - raw.minio_customers_external")
        print("   - analytics.sales_by_region")
        print("   - analytics.top_products")
        print("\n🔗 http://localhost:9047")
    
    return success_count > 0

if __name__ == "__main__":
    main()
