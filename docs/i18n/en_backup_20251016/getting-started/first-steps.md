# First Steps with the Data Platform

**Version**: 3.2.0  
**Last Updated**: 2025-10-16  
**Language**: English

---

## Overview

This tutorial guides you through your first interactions with the data platform, from connecting to services to creating your first data pipeline with Airbyte, Dremio, dbt, and Superset.

```mermaid
graph LR
    A[Access Services] --> B[Configure Airbyte]
    B --> C[Connect Dremio]
    C --> D[Create dbt Models]
    D --> E[Build Dashboard]
    E --> F[Complete Pipeline]
    
    style F fill:#90EE90
    style A fill:#87CEEB
```

**Estimated Time**: 60-90 minutes

---

## Prerequisites

Before starting, ensure:

- ✅ All services are installed and running
- ✅ You can access the web interfaces
- ✅ Python virtual environment is activated
- ✅ Basic understanding of SQL

**Verify services are running:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Step 1: Access All Services

### Service URLs

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / password |
| **Dremio** | http://localhost:9047 | admin / admin123 |
| **Superset** | http://localhost:8088 | admin / admin |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### First Login

**Airbyte:**
1. Open http://localhost:8000
2. Complete setup wizard
3. Set workspace name: "Production"
4. Skip preferences (can configure later)

**Dremio:**
1. Open http://localhost:9047
2. Create admin user on first access:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `admin123`
3. Click "Get Started"

**Superset:**
1. Open http://localhost:8088
2. Login with default credentials
3. Change password: Settings → User Info → Reset Password

---

## Step 2: Configure Your First Data Source in Airbyte

### Create PostgreSQL Source

**Scenario**: Extract data from a PostgreSQL database.

1. **Navigate to Sources**
   - Click "Sources" in left menu
   - Click "+ New source"

2. **Select PostgreSQL**
   - Search for "PostgreSQL"
   - Click "PostgreSQL" connector

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
   - Click "Set up source"
   - Wait for connection test
   - Source created ✅

### Create Sample Data (Optional)

If you don't have data yet, create sample tables:

```sql
-- Connect to PostgreSQL
docker exec -it postgres psql -U postgres -d dremio_db

-- Create sample tables
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

-- Insert sample data
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

-- Verify data
SELECT * FROM customers;
SELECT * FROM orders;
```

---

## Step 3: Configure MinIO S3 Destination

### Create Destination

1. **Navigate to Destinations**
   - Click "Destinations" in left menu
   - Click "+ New destination"

2. **Select S3**
   - Search for "S3"
   - Click "S3" connector

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
   - Click "Set up destination"
   - Connection test should pass ✅

---

## Step 4: Create Your First Connection

### Link Source to Destination

1. **Navigate to Connections**
   - Click "Connections" in left menu
   - Click "+ New connection"

2. **Select Source**
   - Choose "Production PostgreSQL"
   - Click "Use existing source"

3. **Select Destination**
   - Choose "MinIO Data Lake"
   - Click "Use existing destination"

4. **Configure Sync**
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
   # We'll use dbt for transformations
   ```

6. **Save and Sync**
   - Click "Set up connection"
   - Click "Sync now" to run first sync
   - Monitor sync progress

### Monitor Sync

```mermaid
sequenceDiagram
    participant PG as PostgreSQL
    participant AB as Airbyte Worker
    participant S3 as MinIO S3
    
    AB->>PG: 1. Extract: SELECT * FROM customers
    PG->>AB: 2. Return data (5 rows)
    AB->>AB: 3. Transform to Parquet
    AB->>S3: 4. Upload to datalake/raw-data/
    
    AB->>PG: 5. Extract: SELECT * FROM orders WHERE order_date > last_sync
    PG->>AB: 6. Return new data
    AB->>AB: 7. Transform to Parquet
    AB->>S3: 8. Upload to datalake/raw-data/
    
    Note over AB: Sync Complete ✅
```

**Check sync status:**
- Status should show "Succeeded" (green)
- Records synced: ~11 (5 customers + 6 orders)
- View logs for details

---

## Step 5: Connect Dremio to MinIO

### Add S3 Source in Dremio

1. **Navigate to Sources**
   - Open http://localhost:9047
   - Click "Add Source" (+ icon)

2. **Select S3**
   - Choose "Amazon S3"
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
   - Click "Save"
   - Dremio will scan MinIO buckets

### Browse Data

1. **Navigate to MinIOLake source**
   - Expand "MinIOLake"
   - Expand "datalake" bucket
   - Expand "raw-data" folder
   - See "production_public" folder

2. **Preview Data**
   - Click on "customers" folder
   - Click on Parquet file
   - Click "Preview" to see data
   - Data should match PostgreSQL ✅

### Create Virtual Dataset

1. **Query Data**
   ```sql
   -- In Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Save as VDS**
   - Click "Save View As"
   - Name: `vw_customers`
   - Space: `@admin` (your space)
   - Click "Save"

3. **Format Data** (optional)
   - Click on `vw_customers`
   - Use UI to rename columns, change types
   - Example: Rename `customer_id` to `id`

---

## Step 6: Create dbt Models

### Initialize dbt Project

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Navigate to dbt directory
cd dbt

# Test connection
dbt debug

# Should show: "All checks passed!"
```

### Create Source Definition

**File**: `dbt/models/sources.yml`

```yaml
version: 2

sources:
  - name: airbyte_raw
    description: Raw data from Airbyte syncs
    database: MinIOLake.datalake."raw-data".production_public
    tables:
      - name: customers
        description: Customer master data
        columns:
          - name: customer_id
            description: Unique customer identifier
            tests:
              - unique
              - not_null
          - name: email
            tests:
              - unique
              - not_null
      
      - name: orders
        description: Order transactions
        columns:
          - name: order_id
            description: Unique order identifier
            tests:
              - unique
              - not_null
          - name: customer_id
            description: Foreign key to customers
            tests:
              - not_null
              - relationships:
                  to: source('airbyte_raw', 'customers')
                  field: customer_id
```

### Create Staging Model

**File**: `dbt/models/staging/stg_customers.sql`

```sql
-- Staging model: Clean and standardize customer data

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
-- Staging model: Clean and standardize order data

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
    where amount > 0  -- Data quality filter
)

select * from cleaned
```

### Create Mart Model

**File**: `dbt/models/marts/fct_customer_orders.sql`

```sql
-- Fact table: Customer order summary

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
# Run all models
dbt run

# Should see:
# Completed successfully
# Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve  # Opens browser at localhost:8080
```

### Verify in Dremio

```sql
-- Check staging views
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Check mart table
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Step 7: Create Dashboard in Superset

### Add Dremio Database

1. **Navigate to Databases**
   - Open http://localhost:8088
   - Click "Data" → "Databases"
   - Click "+ Database"

2. **Select Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Success
   ```

3. **Click "Connect"**

### Create Dataset

1. **Navigate to Datasets**
   - Click "Data" → "Datasets"
   - Click "+ Dataset"

2. **Configure Dataset**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Click "Create Dataset and Create Chart"**

### Create Charts

#### Chart 1: Customer Segments (Pie Chart)

```yaml
Chart Type: Pie Chart
Datasource: fct_customer_orders

Dimensions:
  - customer_segment

Metrics:
  - COUNT(customer_id)

Filters: None

Chart Options:
  Show Labels: Yes
  Show Legend: Yes
```

#### Chart 2: Revenue by Country (Bar Chart)

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

#### Chart 3: Customer Metrics (Big Number)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Customers

Chart Options:
  Number Format: ,d
```

### Create Dashboard

1. **Navigate to Dashboards**
   - Click "Dashboards"
   - Click "+ Dashboard"

2. **Configure Dashboard**
   ```yaml
   Title: Customer Analytics
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Add Charts**
   - Drag and drop created charts
   - Arrange in grid layout:
     ```
     [ Total Customers    ]
     [ Segments ] [ Revenue by Country ]
     ```

4. **Add Filters** (optional)
   - Click "Add Filter"
   - Filter by: country_code
   - Apply to all charts

5. **Save Dashboard**

---

## Step 8: Verify Complete Pipeline

### End-to-End Test

```mermaid
graph LR
    A[PostgreSQL<br/>Source Data] -->|Airbyte Sync| B[MinIO S3<br/>Raw Data]
    B -->|Dremio Query| C[dbt<br/>Transformations]
    C -->|Write Back| D[Dremio<br/>Marts]
    D -->|SQL Query| E[Superset<br/>Dashboard]
    
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
   - Open Airbyte UI
   - Go to "PostgreSQL → MinIO" connection
   - Click "Sync now"
   - Wait for completion ✅

3. **Run dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **Refresh Superset Dashboard**
   - Open dashboard
   - Click "Refresh" button
   - New data should appear ✅

### Verify Data Flow

```sql
-- In Dremio SQL Runner

-- 1. Check raw data from Airbyte
SELECT COUNT(*) as raw_customers
FROM MinIOLake.datalake."raw-data".production_public.customers;
-- Should return: 7

-- 2. Check staging view
SELECT COUNT(*) as staged_customers
FROM "@admin".staging.stg_customers;
-- Should return: 7

-- 3. Check mart table
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

To change:
1. Open connection in Airbyte
2. Go to "Settings" tab
3. Update "Replication frequency"
4. Save

### Schedule dbt Runs

**Option 1: Cron Job (Linux)**
```bash
# Edit crontab
crontab -e

# Add dbt run at 2:30 AM daily (after Airbyte sync)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Option 2: Python Script**

**File**: `scripts/run_pipeline.py`
```python
#!/usr/bin/env python3
"""
Automated pipeline execution
Runs dbt models after Airbyte sync
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_dbt():
    """Run dbt models"""
    dbt_dir = Path(__file__).parent.parent / 'dbt'
    
    logger.info("Running dbt models...")
    result = subprocess.run(
        ['dbt', 'run'],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("dbt run completed successfully")
        return True
    else:
        logger.error(f"dbt run failed: {result.stderr}")
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

Congratulations! You've built a complete end-to-end data pipeline. 🎉

### Learn More

1. **Advanced Airbyte** - [Airbyte Integration Guide](../guides/airbyte-integration.md)
2. **Dremio Optimization** - [Dremio Setup Guide](../guides/dremio-setup.md)
3. **Complex dbt Models** - [dbt Development Guide](../guides/dbt-development.md)
4. **Advanced Dashboards** - [Superset Dashboards Guide](../guides/superset-dashboards.md)
5. **Data Quality** - [Data Quality Guide](../guides/data-quality.md)

### Troubleshooting

If you encounter issues, see:
- [Troubleshooting Guide](../guides/troubleshooting.md)
- [Installation Guide](installation.md#troubleshooting)
- [Configuration Guide](configuration.md)

---

## Summary

You've successfully:

- ✅ Accessed all 7 platform services
- ✅ Configured Airbyte source (PostgreSQL)
- ✅ Configured Airbyte destination (MinIO S3)
- ✅ Created first Airbyte connection
- ✅ Connected Dremio to MinIO
- ✅ Created dbt models (staging + marts)
- ✅ Built Superset dashboard
- ✅ Verified end-to-end data flow
- ✅ Automated pipeline execution

**Your data platform is now operational!** 🚀

---

**First Steps Guide Version**: 3.2.0  
**Last Updated**: 2025-10-16  
**Maintained By**: Data Platform Team
