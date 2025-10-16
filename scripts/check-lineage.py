#!/usr/bin/env python3
"""
Script pour afficher et analyser le lineage dans OpenMetadata
"""
import requests
import json

OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JWT_TOKEN}"
}

def get_lineage(table_fqn):
    """Récupérer le lineage d'une table"""
    url = f"{OPENMETADATA_URL}/v1/lineage/table/name/{table_fqn}"
    params = {"upstreamDepth": 3, "downstreamDepth": 3}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text[:200]}")
        return None

def display_lineage(lineage_data, table_name):
    """Afficher le lineage de manière lisible"""
    if not lineage_data:
        print(f"\nAucun lineage trouvé pour {table_name}")
        return
    
    print(f"\n{'='*80}")
    print(f"LINEAGE POUR: {table_name}")
    print('='*80)
    
    # Entité principale
    entity = lineage_data.get("entity", {})
    print(f"\nTable principale:")
    print(f"  - Type: {entity.get('type', 'N/A')}")
    print(f"  - FQN: {entity.get('fullyQualifiedName', 'N/A')}")
    
    # Nœuds
    nodes = lineage_data.get("nodes", [])
    print(f"\nNœuds du lineage: {len(nodes)}")
    for node in nodes:
        print(f"  - [{node.get('type', 'N/A')}] {node.get('fullyQualifiedName', 'N/A')}")
    
    # Edges (liens)
    upstream_edges = lineage_data.get("upstreamEdges", [])
    downstream_edges = lineage_data.get("downstreamEdges", [])
    total_edges = len(upstream_edges) + len(downstream_edges)
    print(f"\nLiens (edges): {total_edges}")
    
    if upstream_edges or downstream_edges:
        print("\nRelations upstream (sources):")
        for edge in upstream_edges:
            # Les edges peuvent être des strings ou des objets
            if isinstance(edge, str):
                print(f"  -> {edge}")
            else:
                from_entity = edge.get("fromEntity", {})
                to_entity = edge.get("toEntity", {})
                from_fqn = from_entity.get("fullyQualifiedName", edge) if isinstance(from_entity, dict) else str(from_entity)
                to_fqn = to_entity.get("fullyQualifiedName", "?") if isinstance(to_entity, dict) else str(to_entity)
                print(f"  {from_fqn} -> {to_fqn}")
        
        print("\nRelations downstream (consommateurs):")
        for edge in downstream_edges:
            if isinstance(edge, str):
                print(f"  -> {edge}")
            else:
                from_entity = edge.get("fromEntity", {})
                to_entity = edge.get("toEntity", {})
                from_fqn = from_entity.get("fullyQualifiedName", "?") if isinstance(from_entity, dict) else str(from_entity)
                to_fqn = to_entity.get("fullyQualifiedName", edge) if isinstance(to_entity, dict) else str(to_entity)
                print(f"  {from_fqn} -> {to_fqn}")
    else:
        print("\n  Aucun lien trouvé")
        print("  Raison possible:")
        print("    - Les modèles dbt n'ont pas été exécutés")
        print("    - Les tables sources n'existent pas dans OpenMetadata")
        print("    - Le manifest.json dbt ne contient pas les relations")
    
    # Column lineage
    col_lineage = lineage_data.get("columnLineage", [])
    if col_lineage:
        print(f"\nLineage au niveau colonne: {len(col_lineage)}")
        for cl in col_lineage[:5]:  # Afficher les 5 premiers
            from_col = cl.get("fromColumns", [])
            to_col = cl.get("toColumns", [])
            print(f"  {from_col} -> {to_col}")

def main():
    print("="*80)
    print("ANALYSE DU LINEAGE - TABLES DBT")
    print("="*80)
    
    # Tables à vérifier
    tables_to_check = [
        "dremio_dbt_service.$scratch.marts.fct_orders",
        "dremio_dbt_service.$scratch.marts.dim_customers",
        "dremio_dbt_service.staging.staging.stg_orders",
        "dremio_dbt_service.staging.staging.stg_customers",
        "dremio_dbt_service.raw.customers",
        "dremio_dbt_service.raw.orders"
    ]
    
    for table_fqn in tables_to_check:
        lineage = get_lineage(table_fqn)
        display_lineage(lineage, table_fqn)
    
    print("\n" + "="*80)
    print("RECOMMANDATIONS POUR AMÉLIORER LE LINEAGE")
    print("="*80)
    print("""
1. VÉRIFIER QUE LES TABLES SOURCES EXISTENT:
   - Les tables référencées dans les modèles dbt doivent être enregistrées
     dans OpenMetadata avec le même FQN que dans le manifest.json
   
2. UTILISER LE MACRO source() DANS DBT:
   - Au lieu de: FROM raw.customers
   - Utiliser: FROM {{ source('raw', 'customers') }}
   - Cela permet à dbt de tracer le lineage correctement

3. SYNCHRONISER LES NOMS:
   - Le manifest.json dbt utilise: raw_space.customers
   - Mais les tables sont enregistrées comme: dremio_dbt_service.raw.raw.customers
   - Il faut aligner les noms pour que le lineage fonctionne

4. RÉGÉNÉRER LES ARTEFACTS DBT:
   cd dbt
   dbt run
   dbt docs generate
   
5. RÉINGÉRER LES MÉTADONNÉES:
   metadata ingest -c openmetadata/ingestion/dbt-ingestion.yaml

6. ALTERNATIVE - LINEAGE MANUEL VIA API:
   Le connecteur auto-sync peut être étendu pour créer le lineage
   manuellement via l'API OpenMetadata en analysant les dépendances dbt.
    """)

if __name__ == "__main__":
    main()
