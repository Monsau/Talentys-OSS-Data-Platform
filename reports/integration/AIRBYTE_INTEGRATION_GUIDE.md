# 🚀 INTÉGRATION AIRBYTE - GUIDE COMPLET

**Date**: 15 octobre 2025  
**Objectif**: Ajouter Airbyte comme couche d'ingestion de données

---

## 🎯 Pourquoi Airbyte ?

### Avantages
- ✅ **300+ connecteurs** (APIs, DBs, SaaS, Files)
- ✅ **Interface UI intuitive** (no-code configuration)
- ✅ **Sync incrémentales** (CDC, timestamps, cursors)
- ✅ **Orchestration native** avec scheduling
- ✅ **Intégration Airflow** (déjà dans ta stack)
- ✅ **Stockage dans MinIO** (logs + data staging)
- ✅ **Open-source** (version communautaire gratuite)

### Position dans l'architecture

```
Sources externes        Airbyte           Destinations
─────────────────      ─────────        ──────────────
PostgreSQL    ───┐                    ┌──> MinIO (Parquet)
MySQL         ───┤                    │
MongoDB       ───┤──> [AIRBYTE] ──────┼──> PostgreSQL
APIs REST     ───┤    (Ingestion)     │
Google Sheets ───┤                    └──> Elasticsearch
Salesforce    ───┘                    
                                            │
                                            ↓
                                        [DREMIO]
                                      (Query Engine)
                                            │
                                            ↓
                                          [dbt]
                                       (Transform)
```

---

## 📦 Installation

### Option 1: Démarrage avec la stack existante

```powershell
# Démarrer TOUT (stack principale + Airbyte)
docker-compose -f docker-compose.yml -f docker-compose-airbyte.yml up -d

# Vérifier les services
docker ps | Select-String "airbyte"
```

### Option 2: Démarrage séparé

```powershell
# 1. Démarrer la stack principale d'abord
docker-compose up -d

# 2. Attendre que tout soit prêt (90s)
Start-Sleep -Seconds 90

# 3. Démarrer Airbyte
docker-compose -f docker-compose-airbyte.yml up -d

# 4. Vérifier Airbyte
docker-compose -f docker-compose-airbyte.yml ps
```

---

## 🔧 Configuration initiale

### 1. Accéder à l'interface Airbyte

**URL**: http://localhost:8000

**Première connexion**:
- Pas de login requis (version OSS)
- Configuration automatique au premier accès

### 2. Créer le bucket MinIO pour Airbyte

```powershell
# Via mc (MinIO Client)
docker exec dremio-minio mc alias set myminio http://localhost:9000 minioadmin minioadmin123
docker exec dremio-minio mc mb myminio/airbyte-logs
docker exec dremio-minio mc mb myminio/airbyte-staging

# Vérifier
docker exec dremio-minio mc ls myminio/
```

Ou via l'interface MinIO:
- http://localhost:9001 (minioadmin / minioadmin123)
- Créer buckets: `airbyte-logs` et `airbyte-staging`

### 3. Initialiser la base de données Airbyte

```powershell
# Se connecter à PostgreSQL
docker exec -it dremio-postgres psql -U postgres

# Créer la base Airbyte (si pas auto-créée)
CREATE DATABASE airbyte;
\q
```

---

## 📊 Cas d'usage: Connecteurs utiles

### 🔹 Connecteur 1: PostgreSQL → MinIO (Parquet)

**Use case**: Exporter les données business vers le Data Lake

**Configuration**:
1. Source: PostgreSQL
   - Host: `dremio-postgres`
   - Port: `5432`
   - Database: `business_db`
   - User: `postgres`
   - Password: `postgres123`

2. Destination: S3 (MinIO)
   - Endpoint: `http://minio:9000`
   - Bucket: `airbyte-staging`
   - Access Key: `minioadmin`
   - Secret: `minioadmin123`
   - Format: Parquet
   - Path: `postgres-sync/`

3. Stream Configuration:
   - Tables: `customers`, `orders`
   - Sync mode: `Incremental - Append`
   - Cursor: `updated_at` (ou `id`)

### 🔹 Connecteur 2: API REST → PostgreSQL

**Use case**: Ingérer des données d'API externe

**Configuration**:
1. Source: Custom REST API
   - URL: `https://api.exemple.com/data`
   - Auth: Bearer Token
   - Pagination: Cursor-based

2. Destination: PostgreSQL
   - Host: `dremio-postgres`
   - Port: `5432`
   - Database: `business_db`
   - Schema: `external_data`

### 🔹 Connecteur 3: Google Sheets → MinIO

**Use case**: Ingérer des données manuelles

**Configuration**:
1. Source: Google Sheets
   - Spreadsheet URL
   - OAuth credentials

2. Destination: S3 (MinIO)
   - Bucket: `airbyte-staging`
   - Format: JSON ou CSV
   - Path: `google-sheets/`

---

## 🔄 Intégration avec Airflow

### Créer un DAG Airflow pour orchestrer Airbyte

```python
# Fichier: airflow/dags/airbyte_sync_dag.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'airbyte_postgres_to_minio',
    default_args=default_args,
    description='Sync PostgreSQL to MinIO via Airbyte',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
)

# Sync customers table
sync_customers = AirbyteTriggerSyncOperator(
    task_id='sync_customers',
    airbyte_conn_id='airbyte_connection',
    connection_id='<your-connection-id>',  # From Airbyte UI
    asynchronous=False,
    timeout=3600,
    wait_seconds=30,
    dag=dag,
)

# Sync orders table
sync_orders = AirbyteTriggerSyncOperator(
    task_id='sync_orders',
    airbyte_conn_id='airbyte_connection',
    connection_id='<your-connection-id>',
    asynchronous=False,
    timeout=3600,
    wait_seconds=30,
    dag=dag,
)

# Trigger dbt after sync
from airflow.operators.bash import BashOperator

run_dbt = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /path/to/dbt && dbt run',
    dag=dag,
)

# Orchestration
sync_customers >> sync_orders >> run_dbt
```

---

## 🔍 Monitoring et logs

### 1. Logs Airbyte

**Dans l'UI**: http://localhost:8000 → Jobs → Logs

**Via Docker**:
```powershell
# Logs du worker
docker logs airbyte-worker -f

# Logs du serveur
docker logs airbyte-server -f

# Logs Temporal (workflow engine)
docker logs airbyte-temporal -f
```

### 2. Logs stockés dans MinIO

**Bucket**: `airbyte-logs`

**Structure**:
```
airbyte-logs/
├── job-123/
│   ├── attempt-1/
│   │   ├── logs.log
│   │   └── metadata.json
│   └── attempt-2/
└── job-124/
```

**Accès**:
- Via MinIO Console: http://localhost:9001
- Via mc: `docker exec dremio-minio mc ls myminio/airbyte-logs/`

### 3. Métriques dans Airbyte UI

- **Records synced**: Nombre d'enregistrements
- **Bytes synced**: Volume de données
- **Duration**: Temps d'exécution
- **Status**: Success / Failed / Running

---

## 🎯 Scénario complet d'intégration

### Objectif: Pipeline end-to-end avec Airbyte

```
┌──────────────────────────────────────────────────────────┐
│ ÉTAPE 1: INGESTION (Airbyte)                            │
├──────────────────────────────────────────────────────────┤
│ Source: PostgreSQL (business_db)                         │
│ ├─ customers (10,000 rows)                               │
│ └─ orders (50,000 rows)                                  │
│                                                           │
│ Destination: MinIO (airbyte-staging)                     │
│ ├─ postgres-sync/customers/*.parquet                     │
│ └─ postgres-sync/orders/*.parquet                        │
│                                                           │
│ Fréquence: Toutes les 6 heures (incremental)            │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ ÉTAPE 2: CATALOGAGE (Dremio)                            │
├──────────────────────────────────────────────────────────┤
│ Source MinIO: airbyte-staging                            │
│ ├─ VDS: raw.airbyte_customers                            │
│ └─ VDS: raw.airbyte_orders                               │
│                                                           │
│ SQL Query: SELECT * FROM raw.airbyte_customers           │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ ÉTAPE 3: TRANSFORMATION (dbt)                           │
├──────────────────────────────────────────────────────────┤
│ Models:                                                  │
│ ├─ staging.stg_customers (clean + type)                 │
│ ├─ staging.stg_orders (clean + type)                    │
│ └─ marts.customer_metrics (aggregation)                 │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ ÉTAPE 4: METADATA (OpenMetadata)                        │
├──────────────────────────────────────────────────────────┤
│ Lineage:                                                 │
│ PostgreSQL → Airbyte → MinIO → Dremio → dbt             │
│                                                           │
│ Documentation auto-générée                               │
└──────────────────────────────────────────────────────────┘
```

---

## 📝 Script d'intégration automatique

Créons un script pour tout configurer automatiquement :

```python
# scripts/setup_airbyte_integration.py

import requests
import time
import json

AIRBYTE_API = "http://localhost:8001/api/v1"

def wait_for_airbyte():
    """Wait for Airbyte to be ready"""
    print("Waiting for Airbyte...")
    for i in range(60):
        try:
            response = requests.get(f"{AIRBYTE_API}/health")
            if response.status_code == 200:
                print("✅ Airbyte is ready!")
                return True
        except:
            pass
        time.sleep(2)
    return False

def create_workspace():
    """Create default workspace"""
    data = {
        "name": "Dremio Integration",
        "email": "admin@example.com"
    }
    response = requests.post(f"{AIRBYTE_API}/workspaces", json=data)
    workspace_id = response.json()["workspaceId"]
    print(f"✅ Workspace created: {workspace_id}")
    return workspace_id

def create_postgres_source(workspace_id):
    """Create PostgreSQL source"""
    data = {
        "workspaceId": workspace_id,
        "name": "PostgreSQL BusinessDB",
        "sourceDefinitionId": "...",  # PostgreSQL connector ID
        "connectionConfiguration": {
            "host": "dremio-postgres",
            "port": 5432,
            "database": "business_db",
            "username": "postgres",
            "password": "postgres123",
            "ssl": False
        }
    }
    response = requests.post(f"{AIRBYTE_API}/sources", json=data)
    source_id = response.json()["sourceId"]
    print(f"✅ PostgreSQL source created: {source_id}")
    return source_id

def create_minio_destination(workspace_id):
    """Create MinIO (S3) destination"""
    data = {
        "workspaceId": workspace_id,
        "name": "MinIO Data Lake",
        "destinationDefinitionId": "...",  # S3 connector ID
        "connectionConfiguration": {
            "s3_bucket_name": "airbyte-staging",
            "s3_bucket_path": "postgres-sync",
            "s3_bucket_region": "us-east-1",
            "s3_endpoint": "http://minio:9000",
            "access_key_id": "minioadmin",
            "secret_access_key": "minioadmin123",
            "format": {
                "format_type": "Parquet"
            }
        }
    }
    response = requests.post(f"{AIRBYTE_API}/destinations", json=data)
    dest_id = response.json()["destinationId"]
    print(f"✅ MinIO destination created: {dest_id}")
    return dest_id

def create_connection(workspace_id, source_id, destination_id):
    """Create sync connection"""
    data = {
        "name": "PostgreSQL → MinIO",
        "sourceId": source_id,
        "destinationId": destination_id,
        "scheduleType": "cron",
        "scheduleData": {
            "cron": {
                "cronExpression": "0 */6 * * *",  # Every 6 hours
                "cronTimeZone": "UTC"
            }
        },
        "syncCatalog": {
            "streams": [
                {
                    "stream": {"name": "customers"},
                    "config": {
                        "syncMode": "incremental",
                        "destinationSyncMode": "append",
                        "cursorField": ["id"]
                    }
                },
                {
                    "stream": {"name": "orders"},
                    "config": {
                        "syncMode": "incremental",
                        "destinationSyncMode": "append",
                        "cursorField": ["id"]
                    }
                }
            ]
        }
    }
    response = requests.post(f"{AIRBYTE_API}/connections", json=data)
    connection_id = response.json()["connectionId"]
    print(f"✅ Connection created: {connection_id}")
    return connection_id

def main():
    print("=== AIRBYTE INTEGRATION SETUP ===\n")
    
    if not wait_for_airbyte():
        print("❌ Airbyte not ready")
        return
    
    workspace_id = create_workspace()
    source_id = create_postgres_source(workspace_id)
    dest_id = create_minio_destination(workspace_id)
    connection_id = create_connection(workspace_id, source_id, dest_id)
    
    print("\n=== SETUP COMPLETE ===")
    print(f"Workspace: {workspace_id}")
    print(f"Source: {source_id}")
    print(f"Destination: {dest_id}")
    print(f"Connection: {connection_id}")
    print("\n✅ Airbyte is configured!")
    print(f"UI: http://localhost:8000")

if __name__ == "__main__":
    main()
```

---

## 🚀 Démarrage rapide

### Commandes rapides

```powershell
# 1. Démarrer la stack complète
docker-compose -f docker-compose.yml -f docker-compose-airbyte.yml up -d

# 2. Attendre 2 minutes
Start-Sleep -Seconds 120

# 3. Vérifier que tout tourne
docker ps | Select-String "airbyte"

# 4. Accéder à l'UI
Start-Process "http://localhost:8000"

# 5. Configuration manuelle dans l'UI
#    - Créer Source (PostgreSQL)
#    - Créer Destination (S3/MinIO)
#    - Créer Connection avec sync schedule
```

---

## 📊 Ports utilisés

| Service | Port | Description |
|---------|------|-------------|
| Airbyte UI | 8000 | Interface web |
| Airbyte API | 8001 | API REST |
| Connector Builder | 8003 | Build custom connectors |
| Temporal | 7233 | Workflow engine (gRPC) |

---

## 🎯 Prochaines étapes

1. ✅ Démarrer Airbyte avec la stack
2. ⏳ Configurer première source (PostgreSQL)
3. ⏳ Configurer destination (MinIO)
4. ⏳ Créer connexion avec sync
5. ⏳ Tester sync manuelle
6. ⏳ Configurer scheduling
7. ⏳ Intégrer avec Airflow
8. ⏳ Ajouter dans OpenMetadata lineage

---

**Document créé le**: 15 octobre 2025  
**Par**: AI Assistant  
**Status**: ✅ PRÊT POUR INTÉGRATION
