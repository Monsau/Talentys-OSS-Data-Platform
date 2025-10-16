#!/usr/bin/env python3
"""
Script pour vérifier toutes les ressources disponibles dans Dremio
et comparer avec ce qui est chargé dans OpenMetadata
"""
import requests
import json

DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASS = "admin123"

OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"

def get_dremio_token():
    """Obtenir un token d'authentification Dremio"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": DREMIO_USER, "password": DREMIO_PASS},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Erreur authentification Dremio: {response.status_code}")
        return None

def list_dremio_catalog(token, path=None):
    """Lister le catalogue Dremio récursivement"""
    headers = {"Authorization": f"_dremio{token}"}
    
    if path:
        url = f"{DREMIO_URL}/api/v3/catalog/by-path/{path}"
    else:
        url = f"{DREMIO_URL}/api/v3/catalog"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def explore_dremio_recursively(token, path=None, level=0):
    """Explorer Dremio récursivement et afficher la structure"""
    catalog = list_dremio_catalog(token, path)
    
    if not catalog:
        return []
    
    resources = []
    indent = "  " * level
    
    # Obtenir les données actuelles
    data = catalog.get("data", [catalog])
    
    for item in data:
        entity_type = item.get("entityType", "UNKNOWN")
        item_path = item.get("path", [])
        item_name = ".".join(item_path) if item_path else item.get("name", "?")
        
        # Déterminer l'icône selon le type
        if entity_type == "space":
            icon = "SPACE"
        elif entity_type == "source":
            icon = "SOURCE"
        elif entity_type == "folder":
            icon = "FOLDER"
        elif entity_type in ["dataset", "table"]:
            icon = "TABLE"
        elif entity_type == "file":
            icon = "FILE"
        else:
            icon = entity_type
        
        print(f"{indent}[{icon}] {item_name}")
        
        resources.append({
            "path": item_path,
            "name": item_name,
            "type": entity_type
        })
        
        # Explorer les enfants si c'est un conteneur
        if entity_type in ["space", "source", "folder"]:
            children = item.get("children", [])
            for child in children:
                child_path = child.get("path", [])
                if child_path:
                    child_resources = explore_dremio_recursively(
                        token, 
                        "/".join(child_path),
                        level + 1
                    )
                    resources.extend(child_resources)
    
    return resources

def list_openmetadata_tables():
    """Lister les tables du service dremio_dbt_service"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{OPENMETADATA_URL}/v1/tables?service=dremio_dbt_service&limit=100",
        headers=headers
    )
    
    if response.status_code == 200:
        tables = response.json().get("data", [])
        return [t.get("fullyQualifiedName") for t in tables]
    return []

def main():
    print("=" * 80)
    print("Analyse des ressources Dremio vs OpenMetadata")
    print("=" * 80)
    
    # 1. Explorer Dremio
    print("\n[1] RESSOURCES DREMIO")
    print("-" * 80)
    token = get_dremio_token()
    if not token:
        print("Impossible de se connecter à Dremio")
        return
    
    dremio_resources = explore_dremio_recursively(token)
    
    # Compter par type
    spaces = [r for r in dremio_resources if r["type"] == "space"]
    sources = [r for r in dremio_resources if r["type"] == "source"]
    tables = [r for r in dremio_resources if r["type"] in ["dataset", "table"]]
    
    print(f"\nRésumé Dremio:")
    print(f"  - Spaces: {len(spaces)}")
    print(f"  - Sources: {len(sources)}")
    print(f"  - Tables/Datasets: {len(tables)}")
    print(f"  - Total ressources: {len(dremio_resources)}")
    
    # 2. Vérifier OpenMetadata
    print("\n[2] TABLES CHARGÉES DANS OPENMETADATA (dremio_dbt_service)")
    print("-" * 80)
    om_tables = list_openmetadata_tables()
    
    for table_fqn in om_tables:
        print(f"  - {table_fqn}")
    
    print(f"\nTotal: {len(om_tables)} tables")
    
    # 3. Comparaison
    print("\n[3] ANALYSE")
    print("-" * 80)
    
    # Tables Dremio qui devraient être chargées
    dremio_table_names = [r["name"] for r in tables]
    
    print(f"\nTables dans Dremio: {len(tables)}")
    for t in tables[:10]:  # Afficher les 10 premières
        print(f"  - {t['name']}")
    if len(tables) > 10:
        print(f"  ... et {len(tables) - 10} autres")
    
    print(f"\nTables chargées dans OpenMetadata: {len(om_tables)}")
    
    # Vérifier la couverture
    if len(om_tables) < len(tables):
        print(f"\nATTENTION: Le connecteur charge seulement {len(om_tables)} tables")
        print(f"           Il manque {len(tables) - len(om_tables)} tables de Dremio")
        print("\nLe connecteur actuel charge MANUELLEMENT:")
        print("  - raw.raw.customers")
        print("  - raw.raw.orders")
        print("  - staging.staging.stg_customers")
        print("  - staging.staging.stg_orders")
        print("  - $scratch.marts.dim_customers")
        print("  - $scratch.marts.fct_orders")
        print("\nIl NE charge PAS automatiquement toutes les ressources Dremio.")
    else:
        print("\nLe connecteur semble charger toutes les tables Dremio.")
    
    print("\n" + "=" * 80)
    print("RECOMMANDATION:")
    print("=" * 80)
    print("""
Pour que le connecteur charge AUTOMATIQUEMENT toutes les ressources Dremio:

1. Créer un script d'ingestion automatique qui :
   - Se connecte à l'API Dremio
   - Liste tous les spaces, sources, folders, tables
   - Les enregistre dans OpenMetadata via l'API

2. OU utiliser l'ingestion dbt qui capture les modèles dbt
   (mais ne capture pas les sources Dremio non utilisées par dbt)

3. Le script actuel (register-tables-in-openmetadata.py) enregistre
   UNIQUEMENT les tables définies en dur dans le code.
   
CONCLUSION: Le connecteur actuel est MANUEL et PARTIEL.
    """)

if __name__ == "__main__":
    main()
