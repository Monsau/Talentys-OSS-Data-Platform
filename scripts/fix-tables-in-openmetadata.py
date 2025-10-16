#!/usr/bin/env python3
"""
Script pour réenregistrer les tables Dremio dans OpenMetadata avec les noms corrects
"""

import requests
import json
import time

# Configuration OpenMetadata
OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0JvdCI6dHJ1ZSwic3ViIjoiaW5nZXN0aW9uLWJvdCIsImlhdCI6MTczMzgyMjQxOCwiZW1haWwiOiJpbmdlc3Rpb24tYm90QG9wZW5tZXRhZGF0YS5vcmciLCJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsImV4cCI6MTg5MTU4OTYxOH0.QLs-kn5cJ4Y3gMy3e30-11hR2PK1ZRDSsOd41S77rWzvmIz4gsgOiE2aZ1JQ6n-z9eJ3X0SN9cNa6M6jfh-wd2ZXOzqI7EejuC7PIWU2v81r0GE26OM_JKHsPn1n7y4IrLgM8_ZzZlZJMU0z5-YZ0evh-xDXwNOyHRSZB8sLjpIlz2fOyYLlLaUdFHcQvmVyHJIQYBEGZRzb2RVDbNDUaY_n4OhpVN4gVRmxiHH9r8JOhUqMHmDd3qzSiZK3F4dKWh6Mv2zlzXFQ2gqLg0kSqYq_I6Q4P8KpZeRwBr3-r1xzfIQW3kQRwD0f8V4r_5eE8VL6LvJ8WxVZKqE8xL0A4g"
SERVICE_NAME = "dremio_dbt_service"

HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# Variable globale pour stocker l'ID du service
SERVICE_ID = None


def get_service():
    """Récupérer l'ID du service"""
    global SERVICE_ID
    response = requests.get(
        f"{OPENMETADATA_URL}/v1/services/databaseServices/name/{SERVICE_NAME}",
        headers=HEADERS
    )
    if response.status_code == 200:
        SERVICE_ID = response.json()['id']
        return SERVICE_ID
    else:
        print(f"   ⚠️ Erreur {response.status_code}: {response.text}")
        return None


def delete_entity(endpoint, name):
    """Supprimer une entité par son FQN"""
    fqn = f"{SERVICE_NAME}.{name}"
    try:
        response = requests.delete(
            f"{OPENMETADATA_URL}{endpoint}/name/{fqn}?hardDelete=true&recursive=true",
            headers=HEADERS
        )
        if response.status_code in [200, 404]:
            return True
        return False
    except:
        return False


def create_database(database_name, description=""):
    """Créer une database dans OpenMetadata"""
    payload = {
        "name": database_name,
        "displayName": database_name,
        "description": description,
        "service": f"{SERVICE_NAME}"
    }
    
    response = requests.put(
        f"{OPENMETADATA_URL}/v1/databases",
        headers=HEADERS,
        data=json.dumps(payload)
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Database '{database_name}' créée")
        return response.json()
    else:
        print(f"   ⚠️ Database '{database_name}': {response.status_code}")
        return None


def create_schema(database_fqn, schema_name, description=""):
    """Créer un schema dans OpenMetadata"""
    payload = {
        "name": schema_name,
        "displayName": schema_name,
        "description": description,
        "database": database_fqn
    }
    
    response = requests.put(
        f"{OPENMETADATA_URL}/v1/databaseSchemas",
        headers=HEADERS,
        data=json.dumps(payload)
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Schema '{schema_name}' créé")
        return response.json()
    else:
        print(f"   ⚠️ Schema '{schema_name}': {response.status_code}")
        return None


def create_table(schema_fqn, table_name, columns, description=""):
    """Créer une table dans OpenMetadata"""
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
        headers=HEADERS,
        data=json.dumps(payload)
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Table '{table_name}' créée")
        return response.json()
    else:
        print(f"   ⚠️ Table '{table_name}': {response.status_code}")
        return None


def main():
    print("=" * 70)
    print("🔧 Réenregistrement des tables Dremio dans OpenMetadata (noms corrects)")
    print("=" * 70)
    
    # 1. Récupérer le service
    print("\n🔍 Récupération du service...")
    if not get_service():
        print("❌ Service non trouvé")
        return
    print(f"   ✅ Service trouvé: {SERVICE_ID}")
    
    # 2. Nettoyer les anciennes entités (optionnel)
    print("\n🗑️  Nettoyage des anciennes entités...")
    delete_entity("/v1/databases", "scratch")
    delete_entity("/v1/databases", "$scratch")
    print("   ✅ Nettoyage effectué")
    time.sleep(1)
    
    # 3. Créer la database 'raw' (correcte)
    print("\n📁 Création de la database 'raw'...")
    db_raw = create_database("raw", "Espace Dremio pour les données sources")
    if not db_raw:
        print("❌ Échec création database raw")
        return
    time.sleep(0.5)
    
    # 4. Créer le schema 'raw_space' (pas 'raw' !) dans raw
    print("\n📂 Création du schema 'raw_space' dans 'raw'...")
    schema_raw = create_schema(f"{SERVICE_NAME}.raw", "raw_space", "Espace sources dans Dremio (défini dans dbt schema.yml)")
    if not schema_raw:
        print("❌ Échec création schema raw_space")
        return
    time.sleep(0.5)
    
    # 5. Créer les tables sources dans raw.raw_space
    print("\n📊 Création des tables sources...")
    
    customers_columns = [
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "email", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "created_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp"}
    ]
    
    create_table(
        f"{SERVICE_NAME}.raw.raw_space",
        "customers",
        customers_columns,
        "Table des clients"
    )
    time.sleep(0.5)
    
    orders_columns = [
        {"name": "order_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "order_date", "dataType": "DATE", "dataTypeDisplay": "date"},
        {"name": "amount", "dataType": "DECIMAL", "dataTypeDisplay": "decimal"}
    ]
    
    create_table(
        f"{SERVICE_NAME}.raw.raw_space",
        "orders",
        orders_columns,
        "Table des commandes"
    )
    time.sleep(0.5)
    
    # 6. Créer la database 'staging' (correcte)
    print("\n📁 Création de la database 'staging'...")
    db_staging = create_database("staging", "Espace Dremio pour les données staging")
    if not db_staging:
        print("❌ Échec création database staging")
        return
    time.sleep(0.5)
    
    # 7. Créer le schema 'staging' dans staging
    print("\n📂 Création du schema 'staging' dans 'staging'...")
    schema_staging = create_schema(f"{SERVICE_NAME}.staging", "staging", "Couche staging")
    if not schema_staging:
        print("❌ Échec création schema staging")
        return
    time.sleep(0.5)
    
    # 8. Créer les tables staging
    print("\n📊 Création des tables staging...")
    
    stg_customers_columns = [
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "email", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "created_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp"},
        {"name": "updated_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp"}
    ]
    
    create_table(
        f"{SERVICE_NAME}.staging.staging",
        "stg_customers",
        stg_customers_columns,
        "Vue staging des clients"
    )
    time.sleep(0.5)
    
    stg_orders_columns = [
        {"name": "order_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "order_date", "dataType": "DATE", "dataTypeDisplay": "date"},
        {"name": "amount", "dataType": "DECIMAL", "dataTypeDisplay": "decimal"},
        {"name": "updated_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp"}
    ]
    
    create_table(
        f"{SERVICE_NAME}.staging.staging",
        "stg_orders",
        stg_orders_columns,
        "Vue staging des commandes"
    )
    time.sleep(0.5)
    
    # 9. Créer la database '$scratch' (avec le $ !) pour marts
    print("\n📁 Création de la database '$scratch'...")
    db_scratch = create_database("$scratch", "Espace Dremio temporaire (système)")
    if not db_scratch:
        print("❌ Échec création database $scratch")
        return
    time.sleep(0.5)
    
    # 10. Créer le schema 'marts' dans $scratch
    print("\n📂 Création du schema 'marts' dans '$scratch'...")
    schema_marts = create_schema(f"{SERVICE_NAME}.$scratch", "marts", "Couche marts (tables finales)")
    if not schema_marts:
        print("❌ Échec création schema marts")
        return
    time.sleep(0.5)
    
    # 11. Créer les tables marts
    print("\n📊 Création des tables marts...")
    
    dim_customers_columns = [
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "email", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "created_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp"},
        {"name": "updated_at", "dataType": "TIMESTAMP", "dataTypeDisplay": "timestamp"},
        {"name": "total_orders", "dataType": "BIGINT", "dataTypeDisplay": "bigint"},
        {"name": "total_amount", "dataType": "DECIMAL", "dataTypeDisplay": "decimal"}
    ]
    
    create_table(
        f"{SERVICE_NAME}.$scratch.marts",
        "dim_customers",
        dim_customers_columns,
        "Dimension clients avec agrégations"
    )
    time.sleep(0.5)
    
    fct_orders_columns = [
        {"name": "order_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_id", "dataType": "INT", "dataTypeDisplay": "int"},
        {"name": "customer_name", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "email", "dataType": "VARCHAR", "dataTypeDisplay": "varchar", "dataLength": 255},
        {"name": "order_date", "dataType": "DATE", "dataTypeDisplay": "date"},
        {"name": "amount", "dataType": "DECIMAL", "dataTypeDisplay": "decimal"}
    ]
    
    create_table(
        f"{SERVICE_NAME}.$scratch.marts",
        "fct_orders",
        fct_orders_columns,
        "Fait des commandes avec informations clients"
    )
    
    print("\n" + "=" * 70)
    print("✅ Toutes les tables ont été réenregistrées avec les noms corrects !")
    print("=" * 70)
    print("\n📋 Structure créée:")
    print("   📁 raw")
    print("      📂 raw_space")
    print("         📊 customers")
    print("         📊 orders")
    print("   📁 staging")
    print("      📂 staging")
    print("         📊 stg_customers")
    print("         📊 stg_orders")
    print("   📁 $scratch")
    print("      📂 marts")
    print("         📊 dim_customers")
    print("         📊 fct_orders")
    print("\n🔗 Prochaine étape: Relancer l'ingestion dbt pour créer le lineage")
    print("   Commande: metadata ingest -c openmetadata/ingestion/dbt-ingestion.yaml")
    print("\n🌐 Accéder à OpenMetadata: http://localhost:8585")


if __name__ == "__main__":
    main()
