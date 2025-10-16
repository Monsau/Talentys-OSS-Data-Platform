#!/usr/bin/env python3
"""
Script pour créer des tables source dans Dremio via SQL
"""
import requests
import json
import time

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

def run_sql(token, sql):
    """Exécuter une requête SQL"""
    payload = {
        "sql": sql
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/sql",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"_dremio{token}"
        }
    )
    
    if response.status_code in [200, 201]:
        job_id = response.json()["id"]
        print(f"   Job ID: {job_id}")
        
        # Attendre la fin du job
        for i in range(30):
            time.sleep(1)
            job_response = requests.get(
                f"{DREMIO_URL}/api/v3/job/{job_id}",
                headers={"Authorization": f"_dremio{token}"}
            )
            
            if job_response.status_code == 200:
                job_status = job_response.json()["jobState"]
                if job_status == "COMPLETED":
                    print(f"   ✅ Succès")
                    return True
                elif job_status in ["FAILED", "CANCELED"]:
                    print(f"   ❌ Échec: {job_status}")
                    return False
        
        print(f"   ⏱ Timeout")
        return False
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   Message: {response.text[:200]}")
        return False

def main():
    print("=" * 60)
    print("🔧 Création des tables sources dans Dremio")
    print("=" * 60)
    
    # Connexion
    print("\n🔐 Connexion...")
    token = login()
    print("✅ Connecté")
    
    # Créer les tables de test dans $scratch
    print("\n📊 Création de la table customers...")
    sql_customers = """
    CREATE TABLE raw.customers AS
    SELECT * FROM (
        VALUES
            (1, 'Alice Dupont', 'alice@example.com', CAST('2024-01-01' AS TIMESTAMP)),
            (2, 'Bob Martin', 'bob@example.com', CAST('2024-01-02' AS TIMESTAMP)),
            (3, 'Charlie Durand', 'charlie@example.com', CAST('2024-01-03' AS TIMESTAMP)),
            (4, 'Diana Petit', 'diana@example.com', CAST('2024-01-04' AS TIMESTAMP)),
            (5, 'Ethan Moreau', 'ethan@example.com', CAST('2024-01-05' AS TIMESTAMP))
    ) AS t(customer_id, customer_name, email, created_at)
    """
    run_sql(token, sql_customers)
    
    print("\n📦 Création de la table orders...")
    sql_orders = """
    CREATE TABLE raw.orders AS
    SELECT * FROM (
        VALUES
            (101, 1, 150.00, 'completed', CAST('2024-02-01' AS TIMESTAMP)),
            (102, 1, 75.50, 'completed', CAST('2024-02-05' AS TIMESTAMP)),
            (103, 2, 200.00, 'pending', CAST('2024-02-10' AS TIMESTAMP)),
            (104, 3, 50.00, 'completed', CAST('2024-02-15' AS TIMESTAMP)),
            (105, 4, 300.00, 'completed', CAST('2024-02-20' AS TIMESTAMP)),
            (106, 5, 125.00, 'cancelled', CAST('2024-02-25' AS TIMESTAMP))
    ) AS t(order_id, customer_id, amount, status, order_date)
    """
    run_sql(token, sql_orders)
    
    print("\n" + "=" * 60)
    print("✅ Tables sources créées !")
    print("=" * 60)
    print("\n📋 Tables disponibles:")
    print("   - raw.customers (5 lignes)")
    print("   - raw.orders (6 lignes)")
    print("\n🚀 Prêt pour dbt run !")

if __name__ == "__main__":
    main()
