#!/usr/bin/env python3
"""
Script de configuration automatique de Dremio avec environnement complet.

Configure :
- Utilisateur admin initial
- Sources PostgreSQL et MinIO
- Espaces et structures de données
"""

import requests
import json
import time
from datetime import datetime

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
            "http://localhost:9047/apiv2/bootstrap/firstuser",
            json=setup_data,
            timeout=15
        )
        
        if response.status_code in [200, 409]:  # 409 = déjà configuré
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
        "userName": "admin", 
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:9047/apiv2/login",
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
    print("🐘 Création source PostgreSQL...")
    
    postgres_source = {
        "name": "PostgreSQL_Business",
        "type": "POSTGRES", 
        "config": {
            "hostname": "postgres",
            "port": 5432,
            "databaseName": "business_data",
            "username": "dbt_user",  # Utiliser dbt_user qui existe
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
        response = requests.post(
            "http://localhost:9047/apiv2/source",
            json=postgres_source,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source PostgreSQL créée")
            return True
        else:
            print(f"❌ Erreur PostgreSQL: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def create_minio_source(headers):
    """Crée la source MinIO S3"""
    print("🗂️ Création source MinIO S3...")
    
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
        response = requests.post(
            "http://localhost:9047/apiv2/source",
            json=s3_source,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print("✅ Source MinIO créée")
            return True
        else:
            print(f"❌ Erreur MinIO: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def create_spaces(headers):
    """Crée les espaces Dremio"""
    print("🏢 Création des espaces...")
    
    spaces = [
        {"name": "raw", "description": "Raw data from sources"},
        {"name": "staging", "description": "Cleaned and prepared data"}, 
        {"name": "marts", "description": "Business-ready analytical data"},
        {"name": "sandbox", "description": "Experimental workspace"}
    ]
    
    success_count = 0
    
    for space in spaces:
        space_data = {
            "name": space["name"],
            "description": space["description"],
            "type": "SPACE"
        }
        
        try:
            response = requests.post(
                "http://localhost:9047/apiv2/space",
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

def create_sample_vds(headers):
    """Crée des VDS d'exemple"""
    print("📊 Création VDS d'exemple...")
    
    # VDS simple dans raw
    vds_queries = [
        {
            "name": "raw.customer_summary", 
            "sql": """
            SELECT 
                customer_id,
                first_name || ' ' || last_name as full_name,
                email,
                city,
                country,
                created_at
            FROM "PostgreSQL_Business".public.customers
            """,
            "path": ["raw", "customer_summary"]
        },
        {
            "name": "staging.customer_orders",
            "sql": """
            SELECT 
                c.customer_id,
                c.first_name || ' ' || c.last_name as customer_name,
                c.email,
                o.order_id,
                o.order_date,
                o.total_amount,
                o.status
            FROM "PostgreSQL_Business".public.customers c
            LEFT JOIN "PostgreSQL_Business".public.orders o ON c.customer_id = o.customer_id
            """,
            "path": ["staging", "customer_orders"]  
        }
    ]
    
    success_count = 0
    
    for vds in vds_queries:
        vds_data = {
            "name": vds["name"],
            "sql": vds["sql"],
            "path": vds["path"]
        }
        
        try:
            # Créer le dataset virtuel
            response = requests.post(
                "http://localhost:9047/apiv2/dataset/tmp/new_untitled_sql",
                json={"sql": vds["sql"]},
                headers=headers,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ VDS '{vds['name']}' préparé")
                success_count += 1
            else:
                print(f"⚠️ VDS '{vds['name']}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur VDS '{vds['name']}': {str(e)}")
    
    return success_count > 0

def main():
    """Configuration complète de Dremio"""
    print("=" * 60)
    print("🚀 CONFIGURATION AUTOMATIQUE DREMIO")
    print("=" * 60)
    print(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Étape 1: Configuration admin
    if not setup_dremio_admin():
        print("❌ Impossible de configurer l'admin, arrêt")
        return False
    
    # Étape 2: Authentification
    headers = {}
    auth_token = authenticate_dremio()
    if auth_token:
        headers["Authorization"] = auth_token
    else:
        print("❌ Authentification échouée, arrêt")
        return False
    
    # Étape 3: Créer les sources
    print("\n📡 Configuration des sources...")
    pg_success = create_postgresql_source(headers)
    minio_success = create_minio_source(headers)
    
    # Étape 4: Créer les espaces
    print("\n🏢 Configuration des espaces...")
    spaces_success = create_spaces(headers)
    
    # Étape 5: VDS d'exemple (si PostgreSQL OK)
    if pg_success:
        print("\n📊 Création des VDS d'exemple...")
        vds_success = create_sample_vds(headers)
    else:
        vds_success = False
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 60)
    
    print(f"✅ Admin configuré: {'Oui' if True else 'Non'}")
    print(f"✅ Source PostgreSQL: {'Oui' if pg_success else 'Non'}")
    print(f"✅ Source MinIO: {'Oui' if minio_success else 'Non'}")
    print(f"✅ Espaces créés: {'Oui' if spaces_success else 'Non'}")
    print(f"✅ VDS d'exemple: {'Oui' if vds_success else 'Non'}")
    
    print(f"\n🌐 Accès Dremio: http://localhost:9047")
    print(f"🔑 Credentials: admin/admin123")
    
    if pg_success:
        print(f"\n📊 Données disponibles:")
        print(f"   - PostgreSQL_Business.public.customers")
        print(f"   - PostgreSQL_Business.public.orders") 
        print(f"   - PostgreSQL_Business.public.products")
        print(f"   - raw.customer_summary (VDS)")
        print(f"   - staging.customer_orders (VDS)")
    
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    main()