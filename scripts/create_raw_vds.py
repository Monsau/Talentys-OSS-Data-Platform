#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créer tous les VDS (Virtual Datasets) dans l'espace raw
pour que dbt puisse les utiliser
"""
import requests
import time

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """S'authentifier et obtenir le token"""
    print("🔐 Authentification...")
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["token"]
        print("✅ Authentification réussie")
        return token
    else:
        print(f"❌ Erreur authentification: {response.status_code}")
        return None

def create_vds(token, space, name, sql):
    """Créer un VDS"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
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
            json=vds_config
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✅ {space}.{name}")
            return True
        elif response.status_code == 409:
            print(f"  ℹ️ {space}.{name} (existe déjà)")
            return True
        else:
            print(f"  ❌ {space}.{name}: {response.status_code}")
            print(f"     {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ {space}.{name}: {e}")
        return False

def main():
    print("="*60)
    print("🚀 CRÉATION DES VDS DANS L'ESPACE RAW")
    print("="*60)
    
    token = get_auth_token()
    if not token:
        return
    
    print("\n📋 Création des VDS...")
    
    # VDS PostgreSQL
    print("\n🐘 PostgreSQL:")
    vds_list = [
        ("raw", "customers", 'SELECT * FROM "PostgreSQL_BusinessDB".public.customers'),
        ("raw", "orders", 'SELECT * FROM "PostgreSQL_BusinessDB".public.orders'),
        ("raw", "products", 'SELECT * FROM "PostgreSQL_BusinessDB".public.products'),
    ]
    
    # VDS Elasticsearch
    print("\n🔍 Elasticsearch:")
    vds_list.extend([
        ("raw", "es_logs", 'SELECT * FROM "Elasticsearch_Logs"."application_logs"."_doc"'),
        ("raw", "es_events", 'SELECT * FROM "Elasticsearch_Logs"."user_events"."_doc"'),
        ("raw", "es_metrics", 'SELECT * FROM "Elasticsearch_Logs"."performance_metrics"."_doc"'),
    ])
    
    # VDS MinIO
    print("\n🗂️ MinIO:")
    vds_list.extend([
        ("raw", "minio_sales", 'SELECT * FROM "MinIO_Storage"."sales-data"'),
    ])
    
    # Créer tous les VDS
    success_count = 0
    for space, name, sql in vds_list:
        if create_vds(token, space, name, sql):
            success_count += 1
        time.sleep(0.5)
    
    # Résumé
    print("\n" + "="*60)
    print("📋 RÉSUMÉ")
    print("="*60)
    print(f"VDS créés: {success_count}/{len(vds_list)}")
    print("\n🌐 Interface Dremio: http://localhost:9047")
    print("🔑 Credentials: admin/admin123")
    print("\n✅ dbt peut maintenant utiliser 'raw.customers', 'raw.orders', etc.")

if __name__ == "__main__":
    main()
