#!/usr/bin/env python3
"""
Script pour créer le service Dremio dans OpenMetadata via l'API
"""
import requests
import json

OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"

def create_service():
    """Créer un service de base de données Custom pour Dremio"""
    
    # Payload pour créer un service Custom Database
    payload = {
        "name": "dremio_dbt_service",
        "displayName": "Dremio dbt Service",
        "description": "Service Dremio pour ingestion dbt",
        "serviceType": "CustomDatabase",
        "connection": {
            "config": {
                "type": "CustomDatabase",
                "sourcePythonClass": "metadata.ingestion.source.database.customdatabase.metadata.CustomDatabaseSource",
                "connectionOptions": {
                    "host": "localhost",
                    "port": 9047
                }
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    # Créer le service
    response = requests.put(
        f"{OPENMETADATA_URL}/v1/services/databaseServices",
        json=payload,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        print("✅ Service 'dremio_dbt_service' créé avec succès")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"❌ Échec création service: {response.status_code}")
        print(f"   Message: {response.text[:500]}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Création du service Dremio dans OpenMetadata")
    print("=" * 60)
    create_service()
