#!/usr/bin/env python3
"""
Script complet pour configurer Dremio avec PostgreSQL ET MinIO
Basé sur setup_dremio_complete.py avec ajout de la source MinIO et VDS associés
"""

import requests
import json
import time
from datetime import datetime

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def setup_dremio_admin():
    """Configure l'utilisateur admin initial de Dremio"""
    print("🔧 Configuration utilisateur admin Dremio...")
    
    setup_data = {
        "firstName": "Admin",
        "lastName": "User", 
        "email": "admin@dremio.local",
        "createdAt": int(time.time() * 1000),
        "userName": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.put(
            f"{DREMIO_URL}/apiv2/bootstrap/firstuser",
            json=setup_data,
            timeout=15
        )
        
        if response.status_code in [200, 409]:
            print("✅ Utilisateur admin configuré")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ Utilisateur admin existe déjà")
            return True
        else:
            print(f"❌ Erreur configuration: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def authenticate_dremio():
    """S'authentifier auprès de Dremio"""
    print("🔑 Authentification Dremio...")
    
    auth_data = {
        "userName": USERNAME, 
        "password": PASSWORD
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/apiv2/login",
            json=auth_data,
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("token")
            print("✅ Authentification réussie")
            return f"_dremio{token}"
        else:
            print(f"❌ Erreur auth: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def create_postgresql_source(headers):
    """Crée la source PostgreSQL"""
    print("\n🐘 Création source PostgreSQL...")
    
    postgres_source = {
        "name": "PostgreSQL_Business",
        "type": "POSTGRES", 
        "config": {
            "hostname": "postgres",
            "port": 5432,
            "databaseName": "business_data",
            "username": "dbt_user",
            "password": "dbt_password",
            "authenticationType": "MASTER",
            "useSsl": False
        },
        "metadataRefresh": {
            "datasetDiscovery": True,
            "autoPromoteDatasets": True
        }
    }
    
    try:
        response = requests.put(
            f"{DREMIO_URL}/apiv2/source/{postgres_source['name']}",
            json=postgres_source,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source PostgreSQL créée")
            return True
        elif response.status_code == 409:
            print("ℹ️ Source PostgreSQL existe déjà")
            return True
        else:
            print(f"❌ Erreur PostgreSQL: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def create_minio_source(headers):
    """Crée la source MinIO S3"""
    print("\n🗂️ Création source MinIO S3...")
    
    s3_source = {
        "name": "MinIO_Storage",
        "type": "S3",
        "config": {
            "accessKey": "minio_admin",
            "accessSecret": "minio_password", 
            "secure": False,
            "externalBucketList": ["raw-data", "staging-data", "analytics-data"],
            "propertyList": [
                {"name": "fs.s3a.endpoint", "value": "http://minio:9000"},
                {"name": "fs.s3a.path.style.access", "value": "true"},
                {"name": "fs.s3a.connection.ssl.enabled", "value": "false"}
            ]
        }
    }
    
    try:
        response = requests.put(
            f"{DREMIO_URL}/apiv2/source/{s3_source['name']}",
            json=s3_source,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source MinIO créée")
            # Attendre que Dremio découvre les fichiers
            print("⏳ Découverte des fichiers MinIO (15s)...")
            time.sleep(15)
            return True
        elif response.status_code == 409:
            print("ℹ️ Source MinIO existe déjà")
            return True
        else:
            print(f"❌ Erreur MinIO: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def refresh_source(headers, source_name):
    """Force le refresh d'une source pour découvrir les nouveaux fichiers"""
    print(f"🔄 Refresh de la source '{source_name}'...")
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/apiv2/source/{source_name}/refresh",
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            print(f"✅ Source '{source_name}' rafraîchie")
            return True
        else:
            print(f"⚠️ Refresh '{source_name}': {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur refresh: {e}")
        return False

def create_spaces(headers):
    """Crée les espaces Dremio"""
    print("\n🏢 Création des espaces...")
    
    spaces = [
        {"name": "raw", "description": "Raw data from sources"},
        {"name": "staging", "description": "Cleaned and prepared data"}, 
        {"name": "marts", "description": "Business-ready analytical data"},
        {"name": "analytics", "description": "Advanced analytics and reports"}
    ]
    
    success_count = 0
    
    for space in spaces:
        try:
            # Vérifier si l'espace existe
            check_response = requests.get(
                f"{DREMIO_URL}/api/v3/catalog/by-path/{space['name']}",
                headers=headers,
                timeout=10
            )
            
            if check_response.status_code == 200:
                print(f"ℹ️ Espace '{space['name']}' existe déjà")
                success_count += 1
                continue
            
            # Créer l'espace
            space_data = {
                "entityType": "space",
                "name": space["name"],
                "path": [space["name"]]
            }
            
            response = requests.post(
                f"{DREMIO_URL}/api/v3/catalog",
                json=space_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Espace '{space['name']}' créé")
                success_count += 1
            else:
                print(f"⚠️ Espace '{space['name']}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur espace '{space['name']}': {str(e)}")
    
    return success_count > 0

def execute_sql(headers, sql, context=None):
    """Exécute une requête SQL dans Dremio"""
    try:
        payload = {"sql": sql}
        if context:
            payload["context"] = context
        
        response = requests.post(
            f"{DREMIO_URL}/api/v3/sql",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, str(e)

def create_vds_via_sql(headers, space, vds_name, sql_query):
    """Crée un VDS en utilisant CREATE VIEW"""
    print(f"📊 Création VDS '{space}.{vds_name}'...")
    
    create_sql = f'CREATE VDS "{space}"."{vds_name}" AS {sql_query}'
    
    success, result = execute_sql(headers, create_sql, context=[space])
    
    if success:
        print(f"✅ VDS '{space}.{vds_name}' créé")
        return True
    else:
        # Si le VDS existe déjà, essayer de le remplacer
        if "already exists" in str(result).lower():
            print(f"ℹ️ VDS '{space}.{vds_name}' existe déjà")
            return True
        else:
            print(f"❌ Erreur création VDS: {result}")
            return False

def create_minio_vds(headers):
    """Crée des VDS basés sur les fichiers MinIO"""
    print("\n📊 Création des VDS MinIO...")
    
    vds_list = [
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
            "name": "top_selling_products",
            "sql": '''
                SELECT 
                    category,
                    product_name,
                    COUNT(*) as sale_count,
                    SUM(quantity) as total_quantity_sold,
                    ROUND(SUM(quantity * unit_price * (1 - discount)), 2) as total_revenue
                FROM raw.minio_sales
                GROUP BY category, product_name
                ORDER BY total_revenue DESC
                LIMIT 20
            '''
        }
    ]
    
    success_count = 0
    for vds_def in vds_list:
        if create_vds_via_sql(headers, vds_def["space"], vds_def["name"], vds_def["sql"]):
            success_count += 1
    
    return success_count

def main():
    """Configuration complète de Dremio"""
    print("=" * 80)
    print("🚀 CONFIGURATION COMPLÈTE DREMIO (PostgreSQL + MinIO)")
    print("=" * 80)
    print(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Étape 1: Configuration admin
    if not setup_dremio_admin():
        print("❌ Impossible de configurer l'admin, arrêt")
        return False
    
    time.sleep(2)
    
    # Étape 2: Authentification
    headers = {}
    auth_token = authenticate_dremio()
    if auth_token:
        headers["Authorization"] = auth_token
        headers["Content-Type"] = "application/json"
    else:
        print("❌ Authentification échouée, arrêt")
        return False
    
    # Étape 3: Créer les sources
    print("\n📡 Configuration des sources...")
    pg_success = create_postgresql_source(headers)
    minio_success = create_minio_source(headers)
    
    # Étape 4: Refresh des sources pour découvrir les données
    if minio_success:
        refresh_source(headers, "MinIO_Storage")
    
    # Étape 5: Créer les espaces
    print("\n🏢 Configuration des espaces...")
    spaces_success = create_spaces(headers)
    
    # Étape 6: Créer les VDS MinIO
    if minio_success and spaces_success:
        print("\n⏳ Attente de la disponibilité des sources (5s)...")
        time.sleep(5)
        minio_vds_count = create_minio_vds(headers)
    else:
        minio_vds_count = 0
    
    # Résumé
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 80)
    
    print(f"✅ Admin configuré: Oui")
    print(f"✅ Source PostgreSQL: {'Oui' if pg_success else 'Non'}")
    print(f"✅ Source MinIO: {'Oui' if minio_success else 'Non'}")
    print(f"✅ Espaces créés: {'Oui' if spaces_success else 'Non'}")
    print(f"✅ VDS MinIO créés: {minio_vds_count}/4")
    
    print(f"\n🌐 Accès Dremio: http://localhost:9047")
    print(f"🔑 Credentials: admin/admin123")
    
    if minio_success:
        print(f"\n📊 Données MinIO disponibles:")
        print(f"   - raw.minio_sales (ventes)")
        print(f"   - raw.minio_customers_external (clients externes)")
        print(f"   - analytics.sales_by_region (agrégation par région)")
        print(f"   - analytics.top_selling_products (top produits)")
    
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    main()
