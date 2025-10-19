# 🔌 API Documentation

Documentation des APIs de la plateforme Data Platform v3.3.1

## 📑 Table des Matières

- [Dremio API](#dremio-api)
- [Airbyte API](#airbyte-api)
- [dbt Cloud API](#dbt-cloud-api)
- [OpenMetadata API](#openmetadata-api)
- [Superset API](#superset-api)
- [Exemples d'Intégration](#exemples-dintégration)

---

## 🗄️ Dremio API

### Configuration de Base

```python
from dremio_connector.clients import DremioClient

# Connexion à Dremio
client = DremioClient(
    host="localhost",
    port=9047,
    username="admin",
    password="admin123"
)
```

### Requêtes SQL

```python
# Exécuter une requête
result = client.execute_query("""
    SELECT * FROM @dremio.CustomerData
    LIMIT 10
""")

# Récupérer les résultats
for row in result:
    print(row)
```

### Gestion des Sources

```python
# Lister les sources
sources = client.list_sources()

# Créer une nouvelle source
client.create_source({
    "name": "PostgreSQL_Production",
    "type": "POSTGRES",
    "config": {
        "hostname": "db.example.com",
        "port": 5432,
        "database": "production"
    }
})
```

### Endpoints Principaux

- `POST /api/v3/sql` - Exécuter des requêtes SQL
- `GET /api/v3/catalog` - Parcourir le catalogue
- `GET /api/v3/catalog/{id}` - Obtenir un objet spécifique
- `POST /api/v3/catalog` - Créer un nouvel objet
- `PUT /api/v3/catalog/{id}` - Mettre à jour un objet
- `DELETE /api/v3/catalog/{id}` - Supprimer un objet

📖 **Documentation officielle** : [Dremio REST API](https://docs.dremio.com/current/reference/api/)

---

## 🔄 Airbyte API

### Configuration de Base

```python
import requests

# Configuration Airbyte
AIRBYTE_URL = "http://localhost:8000/api/v1"

headers = {
    "Content-Type": "application/json"
}
```

### Gestion des Connexions

```python
# Lister les connexions
response = requests.get(
    f"{AIRBYTE_URL}/connections/list",
    headers=headers
)

# Créer une connexion
connection_config = {
    "name": "PostgreSQL to Dremio",
    "sourceId": "source-postgres-id",
    "destinationId": "destination-dremio-id",
    "syncCatalog": {...}
}

response = requests.post(
    f"{AIRBYTE_URL}/connections/create",
    json=connection_config,
    headers=headers
)
```

### Déclenchement de Synchronisation

```python
# Lancer une synchronisation
sync_response = requests.post(
    f"{AIRBYTE_URL}/connections/sync",
    json={"connectionId": "connection-id"},
    headers=headers
)

# Vérifier le statut
job_id = sync_response.json()["job"]["id"]
status = requests.get(
    f"{AIRBYTE_URL}/jobs/get",
    json={"id": job_id},
    headers=headers
)
```

### Endpoints Principaux

- `POST /api/v1/sources/list` - Lister les sources
- `POST /api/v1/destinations/list` - Lister les destinations
- `POST /api/v1/connections/list` - Lister les connexions
- `POST /api/v1/connections/sync` - Déclencher une synchronisation
- `POST /api/v1/jobs/list` - Lister les jobs

📖 **Documentation officielle** : [Airbyte API Reference](https://airbyte.com/docs/api-documentation)

---

## 🔨 dbt Cloud API

### Configuration de Base

```python
import requests

# Configuration dbt Cloud
DBT_CLOUD_URL = "https://cloud.getdbt.com/api/v2"
DBT_CLOUD_TOKEN = "your-token-here"

headers = {
    "Authorization": f"Token {DBT_CLOUD_TOKEN}",
    "Content-Type": "application/json"
}
```

### Gestion des Runs

```python
# Déclencher un run
response = requests.post(
    f"{DBT_CLOUD_URL}/accounts/{account_id}/jobs/{job_id}/run/",
    headers=headers,
    json={"cause": "API Trigger"}
)

# Vérifier le statut d'un run
run_id = response.json()["data"]["id"]
status = requests.get(
    f"{DBT_CLOUD_URL}/accounts/{account_id}/runs/{run_id}/",
    headers=headers
)
```

### Récupération des Artefacts

```python
# Récupérer manifest.json
manifest = requests.get(
    f"{DBT_CLOUD_URL}/accounts/{account_id}/runs/{run_id}/artifacts/manifest.json",
    headers=headers
)

# Récupérer catalog.json
catalog = requests.get(
    f"{DBT_CLOUD_URL}/accounts/{account_id}/runs/{run_id}/artifacts/catalog.json",
    headers=headers
)
```

### Endpoints Principaux

- `GET /api/v2/accounts/{account_id}/jobs/` - Lister les jobs
- `POST /api/v2/accounts/{account_id}/jobs/{job_id}/run/` - Déclencher un run
- `GET /api/v2/accounts/{account_id}/runs/{run_id}/` - Obtenir le statut d'un run
- `GET /api/v2/accounts/{account_id}/runs/{run_id}/artifacts/{path}` - Récupérer les artefacts

📖 **Documentation officielle** : [dbt Cloud API](https://docs.getdbt.com/dbt-cloud/api-v2)

---

## 📊 OpenMetadata API

### Configuration de Base

```python
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)

# Configuration OpenMetadata
server_config = OpenMetadataConnection(
    hostPort="http://localhost:8585/api",
    authProvider="openmetadata",
    securityConfig=OpenMetadataJWTClientConfig(
        jwtToken="your-jwt-token"
    ),
)

metadata = OpenMetadata(server_config)
```

### Gestion des Entités

```python
# Récupérer une table
from metadata.generated.schema.entity.data.table import Table

table = metadata.get_by_name(
    entity=Table,
    fqn="dremio.CustomerData"
)

# Créer/Mettre à jour une description
table.description = "Table des données clients"
metadata.create_or_update(table)
```

### Lineage

```python
# Ajouter du lineage
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge

lineage_request = AddLineageRequest(
    edge=EntitiesEdge(
        fromEntity=source_table_fqn,
        toEntity=target_table_fqn,
        lineageDetails={
            "sqlQuery": "SELECT * FROM source",
            "source": "dbt"
        }
    )
)

metadata.add_lineage(lineage_request)
```

### Endpoints Principaux

- `GET /api/v1/tables` - Lister les tables
- `GET /api/v1/tables/name/{fqn}` - Obtenir une table par FQN
- `PUT /api/v1/tables` - Créer/Mettre à jour une table
- `PUT /api/v1/lineage` - Ajouter du lineage
- `GET /api/v1/lineage/table/name/{fqn}` - Obtenir le lineage d'une table

📖 **Documentation officielle** : [OpenMetadata API](https://docs.open-metadata.org/sdk/python)

---

## 📈 Superset API

### Configuration de Base

```python
import requests

# Configuration Superset
SUPERSET_URL = "http://localhost:8088"

# Authentification
login_response = requests.post(
    f"{SUPERSET_URL}/api/v1/security/login",
    json={
        "username": "admin",
        "password": "admin",
        "provider": "db"
    }
)

access_token = login_response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

### Gestion des Dashboards

```python
# Lister les dashboards
dashboards = requests.get(
    f"{SUPERSET_URL}/api/v1/dashboard/",
    headers=headers
)

# Créer un dashboard
new_dashboard = {
    "dashboard_title": "Sales Dashboard",
    "slug": "sales-dashboard",
    "published": True
}

response = requests.post(
    f"{SUPERSET_URL}/api/v1/dashboard/",
    json=new_dashboard,
    headers=headers
)
```

### Exécution de Requêtes

```python
# Exécuter une requête SQL
query_response = requests.post(
    f"{SUPERSET_URL}/api/v1/sqllab/execute/",
    json={
        "database_id": 1,
        "sql": "SELECT * FROM sales LIMIT 10",
        "schema": "public"
    },
    headers=headers
)
```

### Endpoints Principaux

- `POST /api/v1/security/login` - Authentification
- `GET /api/v1/dashboard/` - Lister les dashboards
- `POST /api/v1/dashboard/` - Créer un dashboard
- `GET /api/v1/chart/` - Lister les graphiques
- `POST /api/v1/sqllab/execute/` - Exécuter une requête

📖 **Documentation officielle** : [Superset API](https://superset.apache.org/docs/api)

---

## 🔗 Exemples d'Intégration

### Pipeline Complet : PostgreSQL → Dremio → Superset

```python
from dremio_connector.clients import DremioClient
import requests

# 1. Synchronisation Airbyte (PostgreSQL → Dremio)
airbyte_response = requests.post(
    "http://localhost:8000/api/v1/connections/sync",
    json={"connectionId": "postgres-to-dremio"},
    headers={"Content-Type": "application/json"}
)

# 2. Attendre la fin de la synchronisation
job_id = airbyte_response.json()["job"]["id"]
# ... polling du statut ...

# 3. Créer une vue dans Dremio
dremio = DremioClient(host="localhost", port=9047)
dremio.execute_query("""
    CREATE VIEW sales_summary AS
    SELECT 
        customer_id,
        SUM(amount) as total_sales,
        COUNT(*) as order_count
    FROM @dremio.sales
    GROUP BY customer_id
""")

# 4. Rafraîchir le cache Superset
superset_token = "..."  # Obtenir le token d'authentification
requests.post(
    "http://localhost:8088/api/v1/dataset/refresh",
    json={"datasource_id": 1},
    headers={"Authorization": f"Bearer {superset_token}"}
)
```

### Ingestion OpenMetadata depuis Dremio

```python
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from dremio_connector.clients import DremioClient

# Connexion aux services
dremio = DremioClient(host="localhost", port=9047)
metadata = OpenMetadata(server_config)

# Récupérer les tables depuis Dremio
tables = dremio.list_tables()

# Ingérer dans OpenMetadata
for table in tables:
    # Créer l'entité Table
    table_entity = create_table_entity(table)
    metadata.create_or_update(table_entity)
    
    # Ajouter le profiling
    profile_data = dremio.get_table_profile(table.name)
    metadata.ingest_profile_data(table_entity, profile_data)
```

---

## 📚 Ressources Additionnelles

- **Exemples de code** : [/examples](../../examples/)
- **Tests d'intégration** : [/tests](../../tests/)
- **Configuration** : [/config](../../config/)
- **Guide technique** : [../guides/TECHNICAL_DOCUMENTATION.md](../guides/TECHNICAL_DOCUMENTATION.md)

---

## 🔐 Sécurité & Authentification

### Bonnes Pratiques

1. **Jamais de secrets en dur** dans le code
2. **Variables d'environnement** pour les tokens/mots de passe
3. **Rotation régulière** des tokens d'API
4. **HTTPS obligatoire** en production
5. **Rate limiting** sur les appels API

### Exemple avec Variables d'Environnement

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration sécurisée
DREMIO_HOST = os.getenv("DREMIO_HOST")
DREMIO_USER = os.getenv("DREMIO_USER")
DREMIO_PASSWORD = os.getenv("DREMIO_PASSWORD")
DBT_CLOUD_TOKEN = os.getenv("DBT_CLOUD_TOKEN")
OPENMETADATA_JWT = os.getenv("OPENMETADATA_JWT")
```

---

**[← Retour à la documentation](../README.md)**
