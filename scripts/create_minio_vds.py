#!/usr/bin/env python3
"""
Script pour créer la source MinIO dans Dremio et créer des VDS basés sur les fichiers S3.
"""

import requests
import json
import time

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def authenticate():
    """S'authentifier et obtenir le token"""
    print("🔑 Authentification Dremio...")
    
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD},
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json().get("token")
        print("✅ Authentification réussie")
        return {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    else:
        print(f"❌ Erreur d'authentification: {response.status_code}")
        return None

def create_minio_source(headers):
    """Créer la source MinIO dans Dremio"""
    print("\n🗂️ Création de la source MinIO...")
    
    source_config = {
        "name": "MinIO_Storage",
        "type": "S3",
        "config": {
            "credentialType": "ACCESS_KEY",
            "accessKey": "minio_admin",
            "accessSecret": "minio_password",
            "secure": False,
            "externalBucketList": ["raw-data", "staging-data", "analytics-data"],
            "enableAsync": True,
            "compatibilityMode": True,
            "propertyList": [
                {"name": "fs.s3a.endpoint", "value": "minio:9000"},
                {"name": "fs.s3a.path.style.access", "value": "true"},
                {"name": "fs.s3a.connection.ssl.enabled", "value": "false"},
                {"name": "fs.s3a.aws.credentials.provider", "value": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"}
            ]
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "datasetDefinitionRefreshAfterMs": 3600000,
            "datasetDefinitionExpireAfterMs": 10800000,
            "namesRefreshMs": 3600000,
            "datasetUpdateMode": "PREFETCH_QUERIED"
        }
    }
    
    try:
        # Vérifier si la source existe déjà
        check_response = requests.get(
            f"{DREMIO_URL}/api/v3/catalog/by-path/MinIO_Storage",
            headers=headers,
            timeout=10
        )
        
        if check_response.status_code == 200:
            print("ℹ️ Source MinIO_Storage existe déjà")
            source_id = check_response.json().get("id")
            return source_id
        
        # Créer la source
        response = requests.post(
            f"{DREMIO_URL}/apiv2/source/MinIO_Storage",
            json=source_config,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            source_id = response.json().get("id")
            print(f"✅ Source MinIO créée (ID: {source_id})")
            
            # Attendre que la source soit prête
            print("⏳ Attente de la synchronisation de la source...")
            time.sleep(5)
            
            return source_id
        else:
            print(f"❌ Erreur création source: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def create_vds_from_csv(headers, vds_name, source_path, space="raw"):
    """Créer un VDS à partir d'un fichier CSV dans MinIO"""
    
    sql = f'''
    SELECT * 
    FROM {source_path}
    '''
    
    return create_vds(headers, vds_name, sql, space)

def create_vds_from_json(headers, vds_name, source_path, space="raw"):
    """Créer un VDS à partir d'un fichier JSON dans MinIO"""
    
    sql = f'''
    SELECT 
        t.*
    FROM TABLE(
        {source_path}(type => 'json')
    ) AS t
    '''
    
    return create_vds(headers, vds_name, sql, space)

def create_vds(headers, vds_name, sql, space="raw"):
    """Créer un VDS générique"""
    print(f"\n📊 Création VDS '{space}.{vds_name}'...")
    
    vds_data = {
        "path": [space, vds_name],
        "type": "VIRTUAL_DATASET",
        "sql": sql,
        "sqlContext": [space]
    }
    
    try:
        # Essayer de créer le VDS
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            json=vds_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ VDS '{space}.{vds_name}' créé")
            return True
        elif response.status_code == 409:
            print(f"ℹ️ VDS '{space}.{vds_name}' existe déjà")
            return True
        else:
            print(f"❌ Erreur création VDS: {response.status_code}")
            print(f"   SQL: {sql}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def promote_dataset(headers, dataset_path):
    """Promouvoir un dataset pour qu'il soit utilisable"""
    try:
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog/by-path/{dataset_path}/refresh",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print(f"✅ Dataset '{dataset_path}' promu")
            return True
        else:
            return False
    except:
        return False

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🚀 CONFIGURATION SOURCE MINIO + VDS")
    print("=" * 70)
    
    # Authentification
    headers = authenticate()
    if not headers:
        print("❌ Impossible de continuer sans authentification")
        return False
    
    # Créer la source MinIO
    source_id = create_minio_source(headers)
    if not source_id:
        print("⚠️ Impossible de créer la source MinIO")
    
    # Attendre un peu pour que Dremio découvre les fichiers
    print("\n⏳ Attente de la découverte des fichiers (10s)...")
    time.sleep(10)
    
    # Créer les VDS à partir des fichiers MinIO
    print("\n" + "=" * 70)
    print("📊 CRÉATION DES VDS À PARTIR DES FICHIERS MINIO")
    print("=" * 70)
    
    vds_definitions = [
        {
            "name": "minio_sales",
            "sql": 'SELECT * FROM "MinIO_Storage"."raw-data".sales."sales_2024.csv"',
            "space": "raw",
            "description": "Données de ventes depuis MinIO"
        },
        {
            "name": "minio_inventory",
            "sql": '''
                SELECT 
                    warehouse_id,
                    product_category,
                    sku,
                    quantity_available,
                    quantity_reserved,
                    reorder_point,
                    last_updated
                FROM TABLE(
                    "MinIO_Storage"."raw-data".inventory."inventory_snapshot.json"(type => 'json')
                ) AS t
            ''',
            "space": "raw",
            "description": "Données d'inventaire depuis MinIO (JSON)"
        },
        {
            "name": "minio_customers_external",
            "sql": 'SELECT * FROM "MinIO_Storage"."raw-data".external.customers."customers_external.csv"',
            "space": "raw",
            "description": "Données clients externes depuis MinIO"
        },
        {
            "name": "sales_summary",
            "sql": '''
                SELECT 
                    category,
                    region,
                    COUNT(*) as total_sales,
                    SUM(quantity * unit_price * (1 - discount)) as total_revenue,
                    AVG(unit_price) as avg_price
                FROM "MinIO_Storage"."raw-data".sales."sales_2024.csv"
                GROUP BY category, region
            ''',
            "space": "analytics",
            "description": "Résumé des ventes par catégorie et région"
        },
        {
            "name": "inventory_status",
            "sql": '''
                SELECT 
                    warehouse_id,
                    product_category,
                    SUM(quantity_available) as total_available,
                    SUM(quantity_reserved) as total_reserved,
                    SUM(quantity_available - quantity_reserved) as available_for_sale
                FROM TABLE(
                    "MinIO_Storage"."raw-data".inventory."inventory_snapshot.json"(type => 'json')
                ) AS t
                GROUP BY warehouse_id, product_category
            ''',
            "space": "analytics",
            "description": "État de l'inventaire agrégé par entrepôt et catégorie"
        }
    ]
    
    success_count = 0
    for vds_def in vds_definitions:
        if create_vds(headers, vds_def["name"], vds_def["sql"], vds_def["space"]):
            success_count += 1
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Source MinIO: {'Créée/Existante' if source_id else 'Échec'}")
    print(f"✅ VDS créés: {success_count}/{len(vds_definitions)}")
    
    print("\n📊 VDS disponibles:")
    print("   - raw.minio_sales (ventes depuis MinIO CSV)")
    print("   - raw.minio_inventory (inventaire depuis MinIO JSON)")
    print("   - raw.minio_customers_external (clients externes)")
    print("   - analytics.sales_summary (agrégations ventes)")
    print("   - analytics.inventory_status (état inventaire)")
    
    print("\n🔗 Accès Dremio: http://localhost:9047")
    print("🔑 Credentials: admin/admin123")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
