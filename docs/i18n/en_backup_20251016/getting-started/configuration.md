# Configuration Guide

**Version**: 3.2.0  
**Last Updated**: 2025-10-16  
**Language**: English

---

## Overview

This guide covers the configuration of all platform components including Airbyte, Dremio, dbt, Apache Superset, PostgreSQL, MinIO, and Elasticsearch. Proper configuration ensures optimal performance, security, and integration between services.

```mermaid
graph LR
    A[Environment Variables] --> B[Docker Compose]
    B --> C[Service Configuration]
    C --> D[Network Setup]
    D --> E[Volume Management]
    E --> F[Security Settings]
    F --> G[Integration Config]
    G --> H[Production Ready]
    
    style H fill:#90EE90
    style A fill:#87CEEB
```

---

## Configuration Files

### Primary Configuration Files

```
dremiodbt/
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── docker-compose.yml             # Main services
├── docker-compose-airbyte.yml     # Airbyte services
├── dbt/
│   └── dbt_project.yml           # dbt configuration
├── config/
│   ├── dremio.conf               # Dremio settings
│   ├── superset_config.py        # Superset settings
│   └── i18n/
│       └── config.json           # Internationalization
└── scripts/
    └── configure_platform.py      # Automated configuration
```

---

## Environment Variables

### Core Settings

Create or edit `.env` file in project root:

```bash
#================================================
# PROJECT CONFIGURATION
#================================================

PROJECT_NAME=dremiodbt
ENVIRONMENT=production  # development, staging, production
VERSION=3.2.0

#================================================
# DOCKER NETWORK
#================================================

NETWORK_NAME=dremio_network
NETWORK_DRIVER=bridge

#================================================
# POSTGRESQL DATABASE
#================================================

POSTGRES_VERSION=16
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=dremio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ChangeMe123!  # CHANGE IN PRODUCTION

# Connection pool settings
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_SHARED_BUFFERS=256MB

#================================================
# DREMIO DATA LAKEHOUSE
#================================================

DREMIO_VERSION=24.0
DREMIO_HTTP_PORT=9047
DREMIO_FLIGHT_PORT=32010
DREMIO_FABRIC_PORT=45678

# Admin credentials
DREMIO_ADMIN_USER=admin
DREMIO_ADMIN_PASSWORD=Admin123!  # CHANGE IN PRODUCTION
DREMIO_ADMIN_EMAIL=admin@example.com

# Memory settings
DREMIO_MAX_MEMORY_GB=8
DREMIO_MAX_DIRECT_MEMORY_GB=8

# Performance
DREMIO_DIST_MASTER_ENABLED=true
DREMIO_DIST_EXECUTOR_ENABLED=true

#================================================
# AIRBYTE DATA INTEGRATION
#================================================

AIRBYTE_VERSION=0.50.33
AIRBYTE_HTTP_PORT=8000
AIRBYTE_API_PORT=8001

# Airbyte configuration
AIRBYTE_WORKSPACE_ROOT=/tmp/airbyte_local
AIRBYTE_LOCAL_ROOT=/tmp/airbyte_local
AIRBYTE_WEBAPP_URL=http://localhost:8000

# Database for Airbyte
AIRBYTE_DB_HOST=airbyte-db
AIRBYTE_DB_PORT=5432
AIRBYTE_DB_NAME=airbyte
AIRBYTE_DB_USER=airbyte
AIRBYTE_DB_PASSWORD=AirbytePass123!  # CHANGE IN PRODUCTION

# Temporal
TEMPORAL_HOST=airbyte-temporal:7233

#================================================
# APACHE SUPERSET BI
#================================================

SUPERSET_VERSION=3.0.1
SUPERSET_HTTP_PORT=8088

# Admin credentials
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=Admin123!  # CHANGE IN PRODUCTION
SUPERSET_ADMIN_EMAIL=admin@example.com
SUPERSET_ADMIN_FIRSTNAME=Admin
SUPERSET_ADMIN_LASTNAME=User

# Secret key (generate with: openssl rand -base64 42)
SUPERSET_SECRET_KEY=YOUR_SECRET_KEY_HERE  # CHANGE IN PRODUCTION

# Database
SUPERSET_DB_USER=superset
SUPERSET_DB_PASSWORD=SupersetPass123!  # CHANGE IN PRODUCTION

#================================================
# MINIO OBJECT STORAGE
#================================================

MINIO_VERSION=latest
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001

# Root credentials
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=MinioAdmin123!  # CHANGE IN PRODUCTION

# Buckets
MINIO_DEFAULT_BUCKET=datalake
MINIO_RAW_BUCKET=raw-data
MINIO_PROCESSED_BUCKET=processed-data

#================================================
# ELASTICSEARCH SEARCH ENGINE
#================================================

ELASTIC_VERSION=8.15.0
ELASTIC_HTTP_PORT=9200
ELASTIC_TRANSPORT_PORT=9300

# Security
ELASTIC_PASSWORD=ElasticPass123!  # CHANGE IN PRODUCTION
ELASTIC_SECURITY_ENABLED=true

# Memory
ELASTIC_JAVA_OPTS=-Xms1g -Xmx1g

#================================================
# DBT TRANSFORMATION
#================================================

DBT_PROFILES_DIR=./dbt
DBT_TARGET=prod  # dev, staging, prod
DBT_THREADS=4

#================================================
# LOGGING
#================================================

LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json, text
LOG_OUTPUT=file  # console, file, both

#================================================
# MONITORING
#================================================

ENABLE_METRICS=true
METRICS_PORT=9090
ENABLE_TRACING=false

#================================================
# BACKUP
#================================================

BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # 2 AM daily
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=backups
```

### Security Best Practices

**Generate secure passwords:**
```bash
# Generate random password (32 characters)
openssl rand -base64 32

# Generate secret key for Superset
openssl rand -base64 42
```

**Never commit sensitive data:**
```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore

# Use .env.example for documentation
cp .env .env.example
# Remove sensitive values from .env.example
```

---

## Service Configuration

### 1. PostgreSQL Configuration

#### Connection Settings

**File**: `config/postgres.conf`

```ini
# Connection Settings
max_connections = 200
superuser_reserved_connections = 3

# Memory Settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB

# Query Tuning
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_statement = 'mod'
log_duration = on

# Autovacuum
autovacuum = on
autovacuum_max_workers = 3
```

#### Create Databases

```sql
-- Connect to PostgreSQL
psql -U postgres -h localhost

-- Create databases
CREATE DATABASE dremio_db;
CREATE DATABASE superset_db;
CREATE DATABASE airbyte_db;

-- Create users
CREATE USER dremio WITH PASSWORD 'DremioPass123!';
CREATE USER superset WITH PASSWORD 'SupersetPass123!';
CREATE USER airbyte WITH PASSWORD 'AirbytePass123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dremio_db TO dremio;
GRANT ALL PRIVILEGES ON DATABASE superset_db TO superset;
GRANT ALL PRIVILEGES ON DATABASE airbyte_db TO airbyte;
```

### 2. Dremio Configuration

#### Memory Settings

**File**: `config/dremio.conf`

```hocon
paths: {
  local: "/opt/dremio/data"
  dist: "file:///opt/dremio/data/pdfs"
}

services: {
  coordinator.enabled: true
  coordinator.master.enabled: true
  executor.enabled: true
}

provisioning: {
  yarn: {
    enabled: false
  }
}

# Memory allocation
services.coordinator.master.heap: "4g"
services.coordinator.master.direct_memory: "8g"
services.executor.heap: "4g"
services.executor.direct_memory: "8g"

# Web server
services.coordinator.web.port: 9047
services.coordinator.web.ssl.enabled: false

# Client endpoints
services.coordinator.client.port: 31010
services.flight.endpoint.port: 32010

# Executor settings
services.executor.cache.path.local: "/opt/dremio/data/cache"
services.executor.cache.pct.max: 70
```

#### Data Sources Configuration

```yaml
# config/dremio-sources.yaml
sources:
  - name: PostgreSQL
    type: POSTGRES
    config:
      hostname: postgres
      port: 5432
      database: dremio_db
      username: dremio
      password: ${POSTGRES_PASSWORD}
    
  - name: MinIO
    type: S3
    config:
      accessKey: ${MINIO_ROOT_USER}
      accessSecret: ${MINIO_ROOT_PASSWORD}
      endpoint: minio:9000
      secure: false
      buckets:
        - datalake
        - raw-data
        - processed-data
```

### 3. Airbyte Configuration

#### Workspace Settings

**File**: `config/airbyte/config.yaml`

```yaml
# Airbyte workspace configuration
workspace:
  id: default
  name: "Default Workspace"
  slug: "default"
  
# Default sync settings
sync:
  frequency: "manual"  # manual, hourly, daily, weekly
  normalization: true
  dbt_execution: false

# Connection defaults
connection:
  namespace_definition: "destination"
  namespace_format: "${SOURCE_NAMESPACE}"
  prefix: ""

# Resource limits
resources:
  cpu_limit: "2.0"
  memory_limit: "2Gi"
  cpu_request: "0.5"
  memory_request: "512Mi"
```

#### Common Sources Configuration

**PostgreSQL Source:**
```json
{
  "sourceDefinitionId": "decd338e-5647-4c0b-adf4-da0e75f5a750",
  "connectionConfiguration": {
    "host": "postgres",
    "port": 5432,
    "database": "source_db",
    "username": "readonly_user",
    "password": "${SOURCE_DB_PASSWORD}",
    "ssl": false,
    "replication_method": {
      "method": "Standard"
    }
  }
}
```

**S3 Destination (MinIO):**
```json
{
  "destinationDefinitionId": "4816b78f-1489-44c1-9060-4b19d5fa9362",
  "connectionConfiguration": {
    "s3_bucket_name": "datalake",
    "s3_bucket_path": "airbyte-data",
    "s3_endpoint": "http://minio:9000",
    "access_key_id": "${MINIO_ROOT_USER}",
    "secret_access_key": "${MINIO_ROOT_PASSWORD}",
    "format": {
      "format_type": "Parquet"
    }
  }
}
```

### 4. dbt Configuration

#### Project Configuration

**File**: `dbt/dbt_project.yml`

```yaml
name: 'dremio_dbt'
version: '1.0.0'
config-version: 2

# Profile configuration
profile: 'dremio'

# Model paths
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

# Output directory
target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

# Model configurations
models:
  dremio_dbt:
    # Staging models
    staging:
      +materialized: view
      +schema: staging
      
    # Intermediate models
    intermediate:
      +materialized: view
      +schema: intermediate
      
    # Mart models
    marts:
      +materialized: table
      +schema: marts
      
    # Quality tests
    +tests:
      - not_null
      - unique

# Seeds
seeds:
  dremio_dbt:
    +schema: seeds
    +quote_columns: false

# Documentation
docs-paths: ["docs"]

# Variables
vars:
  start_date: '2024-01-01'
  end_date: '2025-12-31'
```

#### Profile Configuration

**File**: `dbt/profiles.yml`

```yaml
dremio:
  target: prod
  outputs:
    dev:
      type: dremio
      threads: 4
      host: localhost
      port: 32010
      use_ssl: false
      username: dremio_user
      password: ${DREMIO_PASSWORD}
      database: "Samples"
      schema: "dbt_dev"
      
    staging:
      type: dremio
      threads: 4
      host: localhost
      port: 32010
      use_ssl: false
      username: dremio_user
      password: ${DREMIO_PASSWORD}
      database: "Production"
      schema: "dbt_staging"
      
    prod:
      type: dremio
      threads: 8
      host: localhost
      port: 32010
      use_ssl: false
      username: dremio_user
      password: ${DREMIO_PASSWORD}
      database: "Production"
      schema: "dbt_prod"
```

### 5. Apache Superset Configuration

#### Application Settings

**File**: `config/superset_config.py`

```python
"""
Apache Superset configuration for Dremio integration
"""
import os
from celery.schedules import crontab

# Secret key for session management
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')

# Database connection
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{os.environ.get('SUPERSET_DB_USER')}:"
    f"{os.environ.get('SUPERSET_DB_PASSWORD')}@postgres:5432/superset_db"
)

# Dremio connection
DREMIO_CONNECTION = (
    f"dremio+flight://{os.environ.get('DREMIO_ADMIN_USER')}:"
    f"{os.environ.get('DREMIO_ADMIN_PASSWORD')}@dremio:32010"
)

# Flask-AppBuilder configuration
AUTH_TYPE = 1  # Database authentication
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"

# Async queries
SUPERSET_WEBSERVER_TIMEOUT = 300
SUPERSET_CELERY_BEAT_SCHEDULE = {
    'cache-warmup': {
        'task': 'cache-warmup',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
        'kwargs': {},
    },
}

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
}

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_RBAC': True,
}

# Row limit
ROW_LIMIT = 50000
VIZ_ROW_LIMIT = 10000
```

### 6. MinIO Configuration

#### Bucket Setup

```bash
# Create buckets
docker exec -it minio mc mb /data/datalake
docker exec -it minio mc mb /data/raw-data
docker exec -it minio mc mb /data/processed-data
docker exec -it minio mc mb /data/backups

# Set bucket policies
docker exec -it minio mc policy set download /data/datalake
docker exec -it minio mc policy set upload /data/raw-data
```

#### Access Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": ["*"]
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::datalake/*",
        "arn:aws:s3:::datalake"
      ]
    }
  ]
}
```

### 7. Elasticsearch Configuration

**File**: `config/elasticsearch.yml`

```yaml
cluster.name: "dremio-search-cluster"
node.name: "node-1"

network.host: 0.0.0.0
http.port: 9200

# Security
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: false
xpack.security.http.ssl.enabled: false

# Memory
bootstrap.memory_lock: true

# Discovery
discovery.type: single-node
```

---

## Network Configuration

### Docker Network

**File**: `docker-compose.yml` (network section)

```yaml
networks:
  dremio_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
          gateway: 172.25.0.1
```

### Service Communication

```mermaid
graph TB
    subgraph "External Access"
        U[Users/Applications]
    end
    
    subgraph "Docker Network: dremio_network"
        A[Airbyte :8000]
        D[Dremio :9047/:31010/:32010]
        S[Superset :8088]
        P[PostgreSQL :5432]
        M[MinIO :9000]
        E[Elasticsearch :9200]
        
        A <-->|Data Sync| M
        A <-->|Metadata| P
        D <-->|Query| P
        D <-->|Storage| M
        D <-->|Search| E
        S <-->|Arrow Flight| D
        S <-->|Metadata| P
    end
    
    U -->|HTTP| A
    U -->|HTTP| D
    U -->|HTTP| S
```

---

## Volume Management

### Persistent Volumes

**File**: `docker-compose.yml` (volumes section)

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./docker-volume/db-data
      
  dremio_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/dremio
      
  minio_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/minio
      
  airbyte_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/airbyte
      
  elastic_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/elasticsearch
```

### Backup Strategy

```bash
# Backup script
#!/bin/bash

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/${BACKUP_DATE}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup PostgreSQL
docker exec postgres pg_dumpall -U postgres > "${BACKUP_DIR}/postgres.sql"

# Backup Dremio metadata
docker exec dremio tar czf - /opt/dremio/data > "${BACKUP_DIR}/dremio_data.tar.gz"

# Backup MinIO
docker exec minio mc mirror /data "${BACKUP_DIR}/minio"

# Upload to S3
aws s3 sync "${BACKUP_DIR}" "s3://backups/${BACKUP_DATE}/"
```

---

## Automated Configuration

### Configuration Script

**File**: `scripts/configure_platform.py`

```python
#!/usr/bin/env python3
"""
Automated platform configuration script
Configures all services with optimal settings
"""

import os
import sys
from pathlib import Path

def configure_all_services():
    """Configure all platform services"""
    
    print("Configuring Data Platform...")
    
    # 1. Configure PostgreSQL
    configure_postgresql()
    
    # 2. Configure Dremio
    configure_dremio()
    
    # 3. Configure Airbyte
    configure_airbyte()
    
    # 4. Configure Superset
    configure_superset()
    
    # 5. Configure MinIO
    configure_minio()
    
    print("Configuration complete!")

if __name__ == '__main__':
    configure_all_services()
```

**Run configuration:**
```bash
python scripts/configure_platform.py
```

---

## Next Steps

After configuration:

1. **Verify Settings** - Run health checks
2. **First Steps** - See [First Steps Guide](first-steps.md)
3. **Set Up Airbyte** - See [Airbyte Integration](../guides/airbyte-integration.md)
4. **Configure Dremio** - See [Dremio Setup](../guides/dremio-setup.md)

---

**Configuration Guide Version**: 3.2.0  
**Last Updated**: 2025-10-16  
**Maintained By**: Data Platform Team
