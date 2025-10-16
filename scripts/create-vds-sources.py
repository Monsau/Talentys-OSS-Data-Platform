#!/usr/bin/env python3
"""
Script pour créer des VDS (Virtual Dataset) dans Dremio
"""
import requests
import json

DREMIO_URL = "http://localhost:9047"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """Connexion à Dremio"""
    payload = {
        "userName": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Échec de connexion: {response.status_code}")

def create_vds(token, space, dataset_name, sql):
    """Créer un Virtual Dataset"""
    payload = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET",
        "path": [space, dataset_name],
        "sql": sql,
        "sqlContext": [space]
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"_dremio{token}"
        }
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ VDS créé: {space}.{dataset_name}")
        return True
    elif response.status_code == 409:
        print(f"   ℹ️ VDS existe déjà: {space}.{dataset_name}")
        return True
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   Message: {response.text[:300]}")
        return False

def main():
    print("=" * 60)
    print("🔧 Création des datasets sources (VDS)")
    print("=" * 60)
    
    # Connexion
    print("\n🔐 Connexion...")
    token = login()
    print("✅ Connecté")
    
    # Créer les VDS avec SELECT VALUES
    print("\n📊 Création du VDS customers...")
    sql_customers = """
    SELECT * FROM (VALUES
        (1, 'Alice Dupont', 'alice@example.com', TIMESTAMP '2024-01-01 00:00:00'),
        (2, 'Bob Martin', 'bob@example.com', TIMESTAMP '2024-01-02 00:00:00'),
        (3, 'Charlie Durand', 'charlie@example.com', TIMESTAMP '2024-01-03 00:00:00'),
        (4, 'Diana Petit', 'diana@example.com', TIMESTAMP '2024-01-04 00:00:00'),
        (5, 'Ethan Moreau', 'ethan@example.com', TIMESTAMP '2024-01-05 00:00:00')
    ) AS t(customer_id, customer_name, email, created_at)
    """
    create_vds(token, "raw", "customers", sql_customers)
    
    print("\n📦 Création du VDS orders...")
    sql_orders = """
    SELECT * FROM (VALUES
        (101, 1, 150.00, 'completed', TIMESTAMP '2024-02-01 00:00:00'),
        (102, 1, 75.50, 'completed', TIMESTAMP '2024-02-05 00:00:00'),
        (103, 2, 200.00, 'pending', TIMESTAMP '2024-02-10 00:00:00'),
        (104, 3, 50.00, 'completed', TIMESTAMP '2024-02-15 00:00:00'),
        (105, 4, 300.00, 'completed', TIMESTAMP '2024-02-20 00:00:00'),
        (106, 5, 125.00, 'cancelled', TIMESTAMP '2024-02-25 00:00:00')
    ) AS t(order_id, customer_id, amount, status, order_date)
    """
    create_vds(token, "raw", "orders", sql_orders)
    
    print("\n" + "=" * 60)
    print("✅ Datasets sources créés !")
    print("=" * 60)
    print("\n📋 VDS disponibles:")
    print("   - raw.customers (5 lignes)")
    print("   - raw.orders (6 lignes)")
    print("\n🚀 Prêt pour dbt run !")

if __name__ == "__main__":
    main()
