#!/usr/bin/env python3
"""
Script pour enregistrer les tables Dremio dans OpenMetadata via l'API
Cela permet de créer les entités de base pour que le lineage dbt fonctionne
"""
import requests
import json

OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"

SERVICE_NAME = "dremio_dbt_service"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JWT_TOKEN}"
}

def create_database(database_name, description=""):
    """Créer une base de données (space Dremio)"""
    payload = {
        "name": database_name,
        "displayName": database_name,
        "description": description,
        "service": f"{SERVICE_NAME}"
    }
    
    response = requests.put(
        f"{OPENMETADATA_URL}/v1/databases",
        json=payload,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        fqn = response.json().get("fullyQualifiedName", f"{SERVICE_NAME}.{database_name}")
        print(f"[OK] Database '{database_name}' créée (FQN: {fqn})")
        return response.json()
    else:
        print(f"  Avertissement Database '{database_name}': {response.status_code} - {response.text[:200]}")
        return None

def create_schema(database_fqn, schema_name, description=""):
    """Créer un schéma dans une base de données"""
    payload = {
        "name": schema_name,
        "displayName": schema_name,
        "description": description,
        "database": database_fqn
    }
    
    response = requests.put(
        f"{OPENMETADATA_URL}/v1/databaseSchemas",
        json=payload,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        fqn = response.json().get("fullyQualifiedName", f"{database_fqn}.{schema_name}")
        print(f"  [OK] Schema '{schema_name}' créé (FQN: {fqn})")
        return response.json()
    else:
        print(f"    Avertissement Schema '{schema_name}': {response.status_code} - {response.text[:200]}")
        return None

def create_table(schema_fqn, table_name, columns, description=""):
    """Créer une table avec ses colonnes"""
    payload = {
        "name": table_name,
        "displayName": table_name,
        "description": description,
        "tableType": "Regular",
        "columns": columns,
        "databaseSchema": schema_fqn
    }
    
    response = requests.put(
        f"{OPENMETADATA_URL}/v1/tables",
        json=payload,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        fqn = response.json().get("fullyQualifiedName", f"{schema_fqn}.{table_name}")
        print(f"    [OK] Table '{table_name}' créée avec {len(columns)} colonnes (FQN: {fqn})")
        return response.json()
    else:
        print(f"      Erreur Table '{table_name}': {response.status_code}")
        print(f"         {response.text[:300]}")
        return None

def main():
    print("=" * 70)
    print("🔧 Enregistrement des tables Dremio dans OpenMetadata")
    print("=" * 70)
    
    # Structure des données
    # raw database/space
    print("\n📁 Création database 'raw'...")
    create_database("raw", "Espace Dremio pour données brutes")
    
    print("  📂 Création schema 'raw'...")
    create_schema(f"{SERVICE_NAME}.raw", "raw", "Schema pour tables sources")
    
    # Tables sources
    print("    📊 Création table 'customers'...")
    customers_columns = [
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Primary key"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer name"},
        {"name": "email", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer email"},
        {"name": "created_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Creation date"}
    ]
    create_table(f"{SERVICE_NAME}.raw.raw", "customers", customers_columns, "Table des clients")
    
    print("    📊 Création table 'orders'...")
    orders_columns = [
        {"name": "order_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Primary key"},
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Foreign key to customers"},
        {"name": "amount", "dataType": "DOUBLE", "dataTypeDisplay": "double", "description": "Order amount"},
        {"name": "status", "dataType": "VARCHAR", "dataLength": 50, "dataTypeDisplay": "varchar(50)", "description": "Order status"},
        {"name": "order_date", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Order date"}
    ]
    create_table(f"{SERVICE_NAME}.raw.raw", "orders", orders_columns, "Table des commandes")
    
    # staging database/space
    print("\n📁 Création database 'staging'...")
    create_database("staging", "Espace Dremio pour données staging")
    
    print("  📂 Création schema 'staging'...")
    create_schema(f"{SERVICE_NAME}.staging", "staging", "Schema pour vues staging")
    
    # Tables staging
    print("    📊 Création table 'stg_customers'...")
    stg_customers_columns = [
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Primary key"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer name"},
        {"name": "email", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer email"},
        {"name": "created_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Creation date"},
        {"name": "updated_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Update date"}
    ]
    create_table(f"{SERVICE_NAME}.staging.staging", "stg_customers", stg_customers_columns, "Staging: customers")
    
    print("    📊 Création table 'stg_orders'...")
    stg_orders_columns = [
        {"name": "order_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Primary key"},
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Foreign key"},
        {"name": "order_date", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Order date"},
        {"name": "amount", "dataType": "DOUBLE", "dataTypeDisplay": "double", "description": "Order amount"},
        {"name": "status", "dataType": "VARCHAR", "dataLength": 50, "dataTypeDisplay": "varchar(50)", "description": "Order status"},
        {"name": "created_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Creation date"}
    ]
    create_table(f"{SERVICE_NAME}.staging.staging", "stg_orders", stg_orders_columns, "Staging: orders")
    
    # $scratch database (marts)
    print("\n📁 Création database '$scratch'...")
    create_database("$scratch", "Espace Dremio scratch pour tables marts")
    
    print("  📂 Création schema 'marts'...")
    create_schema(f"{SERVICE_NAME}.$scratch", "marts", "Schema pour tables marts")
    
    # Tables marts
    print("    📊 Création table 'dim_customers'...")
    dim_customers_columns = [
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Primary key"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer name"},
        {"name": "email", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer email"},
        {"name": "first_order_date", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "First order date"},
        {"name": "most_recent_order_date", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Most recent order"},
        {"name": "number_of_orders", "dataType": "BIGINT", "dataTypeDisplay": "bigint", "description": "Total orders"}
    ]
    create_table(f"{SERVICE_NAME}.$scratch.marts", "dim_customers", dim_customers_columns, "Dimension: customers with order metrics")
    
    print("    📊 Création table 'fct_orders'...")
    fct_orders_columns = [
        {"name": "order_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Primary key"},
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int", "description": "Foreign key"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataLength": 255, "dataTypeDisplay": "varchar(255)", "description": "Customer name"},
        {"name": "order_date", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp", "description": "Order date"},
        {"name": "amount", "dataType": "DOUBLE", "dataTypeDisplay": "double", "description": "Order amount"},
        {"name": "status", "dataType": "VARCHAR", "dataLength": 50, "dataTypeDisplay": "varchar(50)", "description": "Order status"}
    ]
    create_table(f"{SERVICE_NAME}.$scratch.marts", "fct_orders", fct_orders_columns, "Fact table: orders with customer info")
    
    print("\n" + "=" * 70)
    print("✅ Structure complète créée dans OpenMetadata !")
    print("=" * 70)
    print("\n📋 Résumé:")
    print("   • 3 databases: raw, staging, $scratch")
    print("   • 3 schemas: raw, staging, marts")
    print("   • 6 tables avec colonnes et descriptions")
    print("\n🔗 Accéder à OpenMetadata: http://localhost:8585")
    print("\n🚀 Prochaine étape:")
    print("   Relancer l'ingestion dbt pour créer le lineage:")
    print("   metadata ingest -c openmetadata/ingestion/dbt-ingestion.yaml")

if __name__ == "__main__":
    main()
