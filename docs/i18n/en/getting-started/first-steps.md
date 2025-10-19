# Getting Started with the Data Platform

**Version**: 3.2.0  
**Last updated**: 2025-10-16  
**Language**: French

---

## Overview

This tutorial walks you through your first interactions with the data platform, from connecting to services to building your first data pipeline with Airbyte, Dremio, dbt, and Superset.

```mermaid
graph LR
    A[Accéder aux Services] --> B[Configurer Airbyte]
    B --> C[Connecter Dremio]
    C --> D[Créer Modèles dbt]
    D --> E[Construire Tableau de Bord]
    E --> F[Pipeline Complet]
    
    style F fill:#90EE90
    style A fill:#87CEEB
```

**Estimated time**: 60-90 minutes

---

## Prerequisites

Before you begin, make sure that:

- ✅ All services are installed and running
- ✅ You can access web interfaces
- ✅ Python virtual environment is enabled
- ✅ Basic understanding of SQL

**Check that the services are working:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Step 1: Access All Services

### Service URLs

| Services | URL | Default Credentials |
|---------|----------|------------------------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / password |
| **Dremio** | http://localhost:9047 | admin/admin123 |
| **Superset** | http://localhost:8088 | admin / admin |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### First Connection

**Airbyte:**
1. Open http://localhost:8000
2. Complete the setup wizard
3. Set workspace name: “Production”
4. Override preferences (later configuration possible)

**Dremio:**
1. Open http://localhost:9047
2. Create an administrator user on first access:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `admin123`
3. Click on “Get Started”

**Superset:**
1. Open http://localhost:8088
2. Log in with default credentials
3. Change password: Settings → User Info → Reset Password

---

## Step 2: Configure Your First Data Source in Airbyte

### Create a PostgreSQL Source

**Scenario**: Extract data from a PostgreSQL database.

1. **Navigate to Sources**
   - Click on “Sources” in the left menu
   - Click on “+ New source”

2. **Select PostgreSQL**
   - Search for “PostgreSQL”
   - Click on the “PostgreSQL” connector

3. **Configure Connection**
   ```yaml
   Source name: Production PostgreSQL
   Host: postgres
   Port: 5432
   Database: dremio_db
   Username: postgres
   Password: postgres123
   SSL Mode: prefer
   Replication Method: Standard
   ```

4. **Test and Save**
   - Click on “Set up source”
   - Wait for the connection test
   - Source created ✅

### Create Sample Data (Optional)

If you don't have any data yet, create example tables:

```sql
-- Se connecter à PostgreSQL
docker exec -it postgres psql -U postgres -d dremio_db

-- Créer des tables exemples
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    amount DECIMAL(10,2),
    status VARCHAR(20),
    order_date DATE DEFAULT CURRENT_DATE
);

-- Insérer des données exemples
INSERT INTO customers (name, email, country) VALUES
    ('John Doe', 'john@example.com', 'USA'),
    ('Jane Smith', 'jane@example.com', 'UK'),
    ('Carlos Garcia', 'carlos@example.com', 'Spain'),
    ('Marie Dubois', 'marie@example.com', 'France'),
    ('Yuki Tanaka', 'yuki@example.com', 'Japan');

INSERT INTO orders (customer_id, amount, status) VALUES
    (1, 150.00, 'completed'),
    (1, 250.00, 'completed'),
    (2, 300.00, 'pending'),
    (3, 120.00, 'completed'),
    (4, 450.00, 'completed'),
    (5, 200.00, 'shipped');

-- Vérifier les données
SELECT * FROM customers;
SELECT * FROM orders;
```

---

## Step 3: Configure MinIO S3 Destination

### Create a Destination

1. **Navigate to Destinations**
   - Click on “Destinations” in the left menu
   - Click on “+ New destination”

2. **Select S3**
   - Search for “S3”
   - Click on the “S3” connector

3. **Configure MinIO as S3**
   ```yaml
   Destination name: MinIO Data Lake
   S3 Bucket Name: datalake
   S3 Bucket Path: raw-data
   S3 Bucket Region: us-east-1
   S3 Endpoint: http://minio:9000
   Access Key ID: minioadmin
   Secret Access Key: minioadmin123
   
   Output Format:
     Format Type: Parquet
     Compression: GZIP
     Block Size (Row Group Size): 128 MB
   ```

4. **Test and Save**
   - Click on “Set up destination”
   - Connection test should pass ✅

---

## Step 4: Create Your First Connection

### Link Source to Destination

1. **Navigate to Connections**
   - Click on “Connections” in the left menu
   - Click on “+ New connection”

2. **Select Source**
   - Choose “PostgreSQL Production”
   - Click on “Use existing source”

3. **Select Destination**
   - Choose “MinIO Data Lake”
   - Click on “Use existing destination”

4. **Configure Synchronization**
   ```yaml
   Connection name: PostgreSQL → MinIO
   Replication frequency: Every 24 hours at 02:00
   Destination Namespace: Custom format
     Format: production_${SOURCE_NAMESPACE}
   
   Streams to sync:
     ☑ customers
       Sync mode: Full Refresh | Overwrite
       Primary key: customer_id
       Cursor field: created_at
       
     ☑ orders
       Sync mode: Incremental | Append
       Primary key: order_id
       Cursor field: order_date
   ```

5. **Normalization**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Backup and Synchronize**
   - Click on “Set up connection”
   - Click on “Sync now” to execute the first synchronization
   - Monitor sync progress

### Monitor Synchronization

```mermaid
sequenceDiagram
    participant PG as PostgreSQL
    participant AB as Airbyte Worker
    participant S3 as MinIO S3
    
    AB->>PG: 1. Extraction: SELECT * FROM customers
    PG->>AB: 2. Retour données (5 lignes)
    AB->>AB: 3. Transformation en Parquet
    AB->>S3: 4. Téléversement vers datalake/raw-data/
    
    AB->>PG: 5. Extraction: SELECT * FROM orders WHERE order_date > last_sync
    PG->>AB: 6. Retour nouvelles données
    AB->>AB: 7. Transformation en Parquet
    AB->>S3: 8. Téléversement vers datalake/raw-data/
    
    Note over AB: Synchronisation Terminée ✅
```

**Check sync status:**
- Status should show "Succeeded" (green)
- Synchronized records: ~11 (5 customers + 6 orders)
- See logs for details

---

## Step 5: Connect Dremio to MinIO

### Add an S3 Source in Dremio

1. **Navigate to Sources**
   - Open http://localhost:9047
   - Click on “Add Source” (+ icon)

2. **Select S3**
   - Choose “Amazon S3”
   - Configure as MinIO:

```yaml
General:
  Name: MinIOLake

Connection:
  Authentication: AWS Access Key
  AWS Access Key: minioadmin
  AWS Secret Key: minioadmin123
  
  Encrypt connection: No
  
Advanced Options:
  Connection Properties:
    fs.s3a.path.style.access: true
    fs.s3a.endpoint: minio:9000
    dremio.s3.compat: true
  
  Root Path: /
  
  Enable compatibility mode: Yes
```

3. **Test and Save**
   - Click on “Save”
   - Dremio will analyze MinIO buckets

### Browse Data

1. **Navigate to MinIOLake source**
   - Develop “MinIOLake”
   - Develop the "datalake" bucket
   - Expand the "raw-data" folder
   - See the "production_public" folder

2. **Preview Data**
   - Click on the “customers” folder
   - Click on the Parquet file
   - Click on “Preview” to see the data
   - Data must match PostgreSQL ✅

### Create a Virtual Dataset

1. **Query Data**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Save as VDS**
   - Click on “Save View As”
   - Name: `vw_customers`
   - Space: `@admin` (your space)
   - Click on “Save”

3. **Format Data** (optional)
   - Click on `vw_customers`
   - Use the interface to rename columns, change types
   - Example: Rename `customer_id` to `id`

---

## Step 6: Create dbt Templates

### Initialize the dbt Project

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate  # Windows

# Naviguer vers le répertoire dbt
cd dbt

# Tester la connexion
dbt debug

# Devrait afficher: "All checks passed!"
```

### Create Source Definition

**File**: `dbt/models/sources.yml`

```yaml
version: 2

sources:
  - name: airbyte_raw
    description: Données brutes des synchronisations Airbyte
    database: MinIOLake.datalake."raw-data".production_public
    tables:
      - name: customers
        description: Données maîtres clients
        columns:
          - name: customer_id
            description: Identifiant unique du client
            tests:
              - unique
              - not_null
          - name: email
            tests:
              - unique
              - not_null
      
      - name: orders
        description: Transactions de commandes
        columns:
          - name: order_id
            description: Identifiant unique de la commande
            tests:
              - unique
              - not_null
          - name: customer_id
            description: Clé étrangère vers customers
            tests:
              - not_null
              - relationships:
                  to: source('airbyte_raw', 'customers')
                  field: customer_id
```

### Create a Staging Template

**File**: `dbt/models/staging/stg_customers.sql`

```sql
-- Modèle de staging: Nettoyer et standardiser les données clients

{{ config(
    materialized='view',
    schema='staging'
) }}

with source as (
    select * from {{ source('airbyte_raw', 'customers') }}
),

cleaned as (
    select
        customer_id,
        trim(name) as customer_name,
        lower(trim(email)) as email,
        upper(trim(country)) as country_code,
        created_at,
        current_timestamp() as dbt_loaded_at
    from source
)

select * from cleaned
```

**File**: `dbt/models/staging/stg_orders.sql`

```sql
-- Modèle de staging: Nettoyer et standardiser les données de commandes

{{ config(
    materialized='view',
    schema='staging'
) }}

with source as (
    select * from {{ source('airbyte_raw', 'orders') }}
),

cleaned as (
    select
        order_id,
        customer_id,
        amount,
        lower(trim(status)) as order_status,
        order_date,
        current_timestamp() as dbt_loaded_at
    from source
    where amount > 0  -- Filtre de qualité des données
)

select * from cleaned
```

### Create a Mart Template

**File**: `dbt/models/marts/fct_customer_orders.sql`

```sql
-- Table de faits: Résumé des commandes clients

{{ config(
    materialized='table',
    schema='marts'
) }}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_metrics as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount) as total_spent,
        avg(amount) as avg_order_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        sum(case when order_status = 'completed' then 1 else 0 end) as completed_orders
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.country_code,
        c.created_at as customer_since,
        
        coalesce(m.total_orders, 0) as total_orders,
        coalesce(m.total_spent, 0) as lifetime_value,
        coalesce(m.avg_order_value, 0) as avg_order_value,
        m.first_order_date,
        m.last_order_date,
        coalesce(m.completed_orders, 0) as completed_orders,
        
        datediff('day', m.last_order_date, current_date()) as days_since_last_order,
        
        case
            when m.total_orders >= 5 then 'VIP'
            when m.total_orders >= 2 then 'Regular'
            else 'New'
        end as customer_segment
        
    from customers c
    left join customer_metrics m on c.customer_id = m.customer_id
)

select * from final
```

### Run dbt Models

```bash
# Exécuter tous les modèles
dbt run

# Devrait afficher:
# Completed successfully
# Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3

# Exécuter les tests
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve  # Ouvre le navigateur sur localhost:8080
```

### Check in Dremio

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Step 7: Create a Dashboard in Superset

### Add Dremio Database

1. **Navigate to Databases**
   - Open http://localhost:8088
   - Click on “Data” → “Databases”
   - Click on “+ Database”

2. **Select Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **Click on “Connect”**

### Create a Dataset

1. **Navigate to Datasets**
   - Click on “Data” → “Datasets”
   - Click on “+ Dataset”

2. **Configure the Dataset**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Click on “Create Dataset and Create Chart”**

### Create Charts

#### Chart 1: Customer Segments (Circular Diagram)

```yaml
Chart Type: Pie Chart
Datasource: fct_customer_orders

Dimensions:
  - customer_segment

Metrics:
  - COUNT(customer_id)

Filters: Aucun

Chart Options:
  Show Labels: Yes
  Show Legend: Yes
```

#### Chart 2: Income by Country (Bar Chart)

```yaml
Chart Type: Bar Chart
Datasource: fct_customer_orders

Dimensions:
  - country_code

Metrics:
  - SUM(lifetime_value)

Sort by: SUM(lifetime_value) DESC
Limit: 10

Chart Options:
  Show Labels: Yes
  Color Scheme: Superset Colors
```

#### Chart 3: Customer Metrics (Large Number)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Create the Dashboard

1. **Navigate to Dashboards**
   - Click on “Dashboards”
   - Click on “+ Dashboard”

2. **Configure the Dashboard**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Add Graphics**
   - Drag and drop the created graphics
   - Organize in a grid:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Add Filters** (optional)
   - Click on “Add Filter”
   - Filter by: country_code
   - Apply to all charts

5. **Save the Dashboard**

---

## Step 8: Check the Complete Pipeline

### End-to-End Testing

```mermaid
graph LR
    A[PostgreSQL<br/>Données Source] -->|Sync Airbyte| B[MinIO S3<br/>Données Brutes]
    B -->|Requête Dremio| C[dbt<br/>Transformations]
    C -->|Écriture| D[Dremio<br/>Marts]
    D -->|Requête SQL| E[Superset<br/>Tableau de Bord]
    
    style A fill:#336791,color:#fff
    style B fill:#C72E49,color:#fff
    style C fill:#FF694B,color:#fff
    style D fill:#FDB515
    style E fill:#20A7C9,color:#fff
```

### Add New Data

1. **Insert new records in PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Trigger Airbyte sync**
   - Open the Airbyte interface
   - Go to the connection "PostgreSQL → MinIO"
   - Click on “Sync now”
   - Wait for the end ✅

3. **Run dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **Refresh the Superset Dashboard**
   - Open the dashboard
   - Click on the “Refresh” button
   - New data should appear ✅

### Check Data Flow

```sql
-- Dans Dremio SQL Runner

-- 1. Vérifier les données brutes d'Airbyte
SELECT COUNT(*) as raw_customers
FROM MinIOLake.datalake."raw-data".production_public.customers;
-- Devrait retourner: 7

-- 2. Vérifier la vue de staging
SELECT COUNT(*) as staged_customers
FROM "@admin".staging.stg_customers;
-- Devrait retourner: 7

-- 3. Vérifier la table mart
SELECT
    customer_segment,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_revenue
FROM "@admin".marts.fct_customer_orders
GROUP BY customer_segment
ORDER BY total_revenue DESC;
```

---

## Step 9: Automate the Pipeline

### Schedule Airbyte Sync

Already configured to run every 24 hours at 02:00.

To edit:
1. Open connection in Airbyte
2. Go to the “Settings” tab
3. Update “Replication frequency”
4. Save

### Schedule dbt Executions

**Option 1: Cron Job (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Option 2: Python Script**

**File**: `scripts/run_pipeline.py`
```python
#!/usr/bin/env python3
"""
Exécution automatisée du pipeline
Exécute les modèles dbt après la synchronisation Airbyte
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_dbt():
    """Exécuter les modèles dbt"""
    dbt_dir = Path(__file__).parent.parent / 'dbt'
    
    logger.info("Exécution des modèles dbt...")
    result = subprocess.run(
        ['dbt', 'run'],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("Exécution dbt terminée avec succès")
        return True
    else:
        logger.error(f"Échec exécution dbt: {result.stderr}")
        return False

if __name__ == '__main__':
    success = run_dbt()
    exit(0 if success else 1)
```

### Schedule with Docker Compose

**File**: `docker-compose.scheduler.yml`
```yaml
version: '3.8'

services:
  dbt-scheduler:
    image: ghcr.io/dbt-labs/dbt-core:1.10.0
    volumes:
      - ./dbt:/usr/app/dbt
    command: >
      sh -c "while true; do
        dbt run --profiles-dir /usr/app/dbt;
        sleep 3600;
      done"
    networks:
      - dremio_network
```

---

## Next Steps

Congratulations! You have built a complete end-to-end data pipeline. 🎉

### Learn More

1. **Airbyte Advanced** - [Airbyte Integration Guide](../guides/airbyte-integration.md)
2. **Dremio Optimization** - [Dremio Setup Guide](../guides/dremio-setup.md)
3. **Complex dbt Models** - [dbt Development Guide](../guides/dbt-development.md)
4. **Advanced Dashboards** - [Superset Dashboards Guide](../guides/superset-dashboards.md)
5. **Data Quality** - [Data Quality Guide](../guides/data-quality.md)

### Troubleshooting

If you have problems, see:
- [Troubleshooting Guide](../guides/troubleshooting.md)
- [Installation Guide](installation.md#troubleshooting)
- [Configuration Guide](configuration.md)

---

## Summary

You have successfully:

- ✅ Access the 7 services of the platform
- ✅ Configure an Airbyte source (PostgreSQL)
- ✅ Configure an Airbyte destination (MinIO S3)
- ✅ Create your first Airbyte connection
- ✅ Connect Dremio to MinIO
- ✅ Create dbt templates (staging + marts)
- ✅ Build a Superset Dashboard
- ✅ Check end-to-end data flow
- ✅ Automate pipeline execution

**Your data platform is now operational!** 🚀

---

**First Steps Guide Version**: 3.2.0  
**Last Updated**: 2025-10-16  
**Maintained By**: Data Platform Team