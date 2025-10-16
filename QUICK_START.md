# 🚀 Quick Start Guide - Data Platform v1.0

## 📦 One-Command Launch

### Option 1: Automatic Orchestration (Recommended)

Use the **orchestrate_platform.py** script for automatic deployment with all configurations:

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
python -u orchestrate_platform.py

# Linux/Mac
python orchestrate_platform.py
```

**What it does:**
- ✅ Checks prerequisites (Docker, Docker Compose, Python)
- ✅ Starts all Docker services (Dremio, PostgreSQL, MinIO, Elasticsearch)
- ✅ Launches Airbyte for data integration
- ✅ Configures dbt environment
- ✅ Runs dbt models and tests
- ✅ Synchronizes Dremio data to PostgreSQL
- ✅ Creates Superset dashboards automatically
- ✅ Generates Open Data dashboard

**Options:**
```bash
# Show help
python orchestrate_platform.py --help

# Skip infrastructure deployment (if already running)
python orchestrate_platform.py --skip-infrastructure

# Custom workspace path
python orchestrate_platform.py --workspace /path/to/workspace
```

### Option 2: Manual Docker Launch

Start services manually:

```bash
# Start main stack
docker-compose up -d

# Start with Airbyte
docker-compose -f docker-compose.yml -f docker-compose-airbyte-stable.yml up -d
```

---

## 🌐 Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airbyte** | http://localhost:8000 | Setup wizard |
| **Dremio** | http://localhost:9047 | Create account |
| **Superset** | http://localhost:8088 | admin / admin |
| **Airflow** | http://localhost:8080 | airflow / airflow |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin |
| **OpenMetadata** | http://localhost:8585 | admin / admin |

---

## 🔌 Dremio PostgreSQL Proxy

Connect any PostgreSQL client to Dremio:

```bash
# psql
psql -h localhost -p 31010 -U <your-dremio-username>

# Python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    user="your-dremio-username",
    password="your-dremio-password",
    database="Dremio"
)
```

---

## 🔄 Airbyte - Data Integration

**Access**: http://localhost:8000

### Quick Setup

1. **Create Source** (e.g., PostgreSQL):
   - Host: `dremio-postgres`
   - Port: `5432`
   - Database: `business_db`
   - User: `postgres`
   - Password: `postgres123`

2. **Create Destination** (e.g., MinIO S3):
   - Endpoint: `http://dremio-minio:9000`
   - Access Key: `minioadmin`
   - Secret Key: `minioadmin`
   - Bucket: `datalake`
   - Path: `bronze/<source>/`

3. **Create Connection**:
   - Select streams/tables
   - Choose sync mode (Full Refresh / Incremental / CDC)
   - Set schedule (manual, hourly, daily, etc.)

### Sync Modes

- **Full Refresh**: Complete data reload
- **Incremental Append**: Only new/changed records (requires cursor field)
- **CDC**: Real-time change capture (for databases)

---

## 🏔️ Dremio - Lakehouse

**Access**: http://localhost:9047

### Quick Setup

1. **Create Account** (first time)
2. **Add Sources**:
   - PostgreSQL: `dremio-postgres:5432`
   - MinIO S3: `http://dremio-minio:9000`
   - Elasticsearch: `http://dremio-elasticsearch:9200`

3. **Query Data**:
```sql
-- Query from PostgreSQL
SELECT * FROM postgres.business_db.customers LIMIT 10;

-- Query from MinIO (Parquet files)
SELECT * FROM s3.bronze.sales.sales_data LIMIT 10;

-- Join across sources
SELECT 
    c.customer_name,
    s.total_amount
FROM postgres.business_db.customers c
JOIN s3.bronze.sales.sales_data s ON c.id = s.customer_id;
```

---

## 📊 End-to-End Data Pipeline

### Example: E-commerce Analytics

```
1. SOURCE DATA (PostgreSQL)
   ├── customers (id, name, email, country)
   ├── orders (id, customer_id, order_date, total)
   └── products (id, name, category, price)

2. AIRBYTE → Extract & Load
   ├── Sync to MinIO S3 (Bronze layer)
   │   └── s3://datalake/bronze/ecommerce/
   │       ├── customers/
   │       ├── orders/
   │       └── products/
   └── Sync mode: Incremental (every 6 hours)

3. DREMIO → Query & Transform
   ├── Mount MinIO as data source
   ├── Create Virtual Datasets
   └── Apply Reflections (query acceleration)

4. DBT → Transform (Silver → Gold)
   ├── models/silver/
   │   ├── stg_customers.sql (cleaned)
   │   ├── stg_orders.sql (cleaned)
   │   └── stg_products.sql (cleaned)
   └── models/gold/
       ├── dim_customers.sql (dimension)
       ├── dim_products.sql (dimension)
       └── fact_orders.sql (fact table)

5. SUPERSET → Visualize
   ├── Connect to Dremio (port 31010)
   ├── Create datasets from Gold layer
   └── Build dashboards
       ├── Sales Overview
       ├── Customer Analytics
       └── Product Performance

6. AIRFLOW → Orchestrate
   └── DAG: ecommerce_pipeline
       ├── Trigger Airbyte sync
       ├── Wait for completion
       ├── Run dbt transformations
       └── Refresh Superset dashboards
```

---

## 📈 Typical Workflows

### 1. Batch ETL (Daily/Hourly)
```
Airbyte (Full Refresh) 
  → MinIO Bronze
  → Dremio Query
  → dbt Transform
  → Superset Dashboard
```

### 2. Real-time CDC
```
Database (CDC enabled)
  → Airbyte (CDC mode)
  → MinIO Bronze
  → Dremio (live query)
  → Superset (auto-refresh)
```

### 3. Data Lake Analytics
```
Multiple Sources
  → Airbyte
  → MinIO (Parquet/Iceberg)
  → Dremio (federated queries)
  → BI Tools
```

---

## 🛠️ Maintenance

### Check Status
```bash
docker ps
```

### View Logs
```bash
docker logs <container_name>
```

### Restart Service
```bash
docker restart <container_name>
```

### Stop All
```bash
docker-compose -f docker-compose.yml -f docker-compose-airbyte-stable.yml down
```

### Clean Restart
```bash
docker-compose down -v  # Remove volumes
docker-compose -f docker-compose.yml -f docker-compose-airbyte-stable.yml up -d
```

---

## 📚 Documentation

- **Full Guide**: [PLATFORM_STATUS.md](PLATFORM_STATUS.md)
- **README**: [README.md](README.md) (18 languages)
- **Architecture**: [docs/diagrams/](docs/diagrams/)
- **Examples**: [examples/](examples/)

---

## 🌐 Repository

**GitHub**: https://github.com/Monsau/data-platform-iso-opensource  
**Version**: 1.0.0  
**License**: MIT  
**Author**: Mustapha Fonsau (mfonsau@talentys.eu)  
**Organization**: [Talentys](https://talentys.eu)

---

**Ready to go!** 🎉
