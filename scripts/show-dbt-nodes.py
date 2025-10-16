#!/usr/bin/env python3
"""
Script pour afficher les résultats des nœuds dbt ingérés dans OpenMetadata
"""
import requests
import json

OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JWT_TOKEN}"
}

def list_tables():
    """Lister toutes les tables du service"""
    response = requests.get(
        f"{OPENMETADATA_URL}/v1/tables?service=dremio_dbt_service&limit=100",
        headers=headers
    )
    
    if response.status_code == 200:
        tables = response.json().get("data", [])
        print(f"\nTables trouvées: {len(tables)}")
        for table in tables:
            fqn = table.get("fullyQualifiedName", "")
            desc = table.get("description", "")
            print(f"   - {fqn}")
            if desc:
                print(f"     Description: {desc}")
        return tables
    else:
        print(f"Erreur: {response.status_code}")
        return []

def show_lineage(table_fqn):
    """Afficher le lineage d'une table"""
    response = requests.get(
        f"{OPENMETADATA_URL}/v1/lineage/table/name/{table_fqn}?upstreamDepth=3&downstreamDepth=3",
        headers=headers
    )
    
    if response.status_code == 200:
        lineage = response.json()
        nodes = lineage.get("nodes", [])
        edges = lineage.get("edges", [])
        
        print(f"\nLineage pour {table_fqn}:")
        print(f"   Nœuds: {len(nodes)}")
        print(f"   Liens: {len(edges)}")
        
        for edge in edges:
            from_entity = edge.get("fromEntity", {}).get("fullyQualifiedName", "?")
            to_entity = edge.get("toEntity", {}).get("fullyQualifiedName", "?")
            print(f"   {from_entity} -> {to_entity}")
        
        return lineage
    else:
        print(f"   Pas de lineage trouvé ({response.status_code})")
        return None

def main():
    print("=" * 70)
    print("Résultats de l'ingestion dbt dans OpenMetadata")
    print("=" * 70)
    
    tables = list_tables()
    
    if tables:
        print("\n" + "=" * 70)
        print("Vérification du lineage")
        print("=" * 70)
        
        # Vérifier le lineage des tables marts
        for table in tables:
            fqn = table.get("fullyQualifiedName", "")
            if "marts" in fqn:
                show_lineage(fqn)
    
    print("\n" + "=" * 70)
    print("Résumé du projet")
    print("=" * 70)
    print("""
Infrastructure:
   - Dremio 26.0 (Community Edition)
   - OpenMetadata 1.9.7
   - dbt-core 1.10.8 avec dbt-dremio 1.9.0
   - Python 3.12.3 + openmetadata-ingestion 1.9.7

Données:
   - raw.customers (5 lignes) - VDS Dremio
   - raw.orders (6 lignes) - VDS Dremio
   - staging.stg_customers (5 lignes) - Vue dbt
   - staging.stg_orders (6 lignes) - Vue dbt
   - marts.dim_customers (5 lignes) - Table dbt
   - marts.fct_orders (6 lignes) - Table dbt

OpenMetadata:
   - Service: dremio_dbt_service (CustomDatabase)
   - 3 databases: raw, staging, $scratch
   - 3 schemas: raw, staging, marts
   - 6 tables avec métadonnées complètes

Accès:
   - Dremio UI: http://localhost:9047
   - OpenMetadata UI: http://localhost:8585
   - dbt docs: dbt docs generate && dbt docs serve

Credentials:
   - Dremio: dremio_user / dremio_pass123
   - OpenMetadata: (voir JWT token dans les configs)
    """)

if __name__ == "__main__":
    main()
