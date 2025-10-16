# 🚀 Quick Start Guide - Dremio + dbt Platform

## One-Command Deployment

```bash
python3 deploy_platform.py
```

That's it! ☕ Grab a coffee while the platform deploys (~10 minutes).

---

## What Gets Deployed?

### 🐳 Services (Docker)
- **Dremio 26 OSS** - Data lakehouse platform
- **PostgreSQL 15** - Business database (customers, orders)
- **Elasticsearch 7.17** - Application logs & events
- **MinIO** - Object storage (sales data)

### 📊 Data
- **1,000** customers
- **10,000** orders
- **60,000** Elasticsearch documents (logs, events, metrics)
- **50,000** MinIO sales records

### 🔧 dbt Models
- **7** staging models
- **5** mart models (dimensions & facts)
- **40** data quality tests
- **1,040** rows in `fct_business_overview` (multi-source KPIs)

---

## Prerequisites

### Required
- **Docker** & **Docker Compose**
- **Python 3.11+**
- **8GB RAM** minimum
- **10GB disk space**

### Optional
- PostgreSQL client (`psql`) - for manual queries
- `curl` / `httpie` - for API testing

### Check Prerequisites

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python
python3 --version

# Check available RAM
free -h  # Linux
vm_stat  # macOS
```

---

## Step-by-Step Deployment

### 1️⃣ Clone/Setup Project

```bash
cd /path/to/project
```

### 2️⃣ Configure (Optional)

Edit `config.env` to customize:
```bash
# Change default passwords
DREMIO_PASSWORD=your_secure_password
POSTGRES_PASSWORD=your_secure_password
MINIO_SECRET_KEY=your_secure_key

# Adjust data volumes
DATA_CUSTOMERS=5000
DATA_ORDERS=50000
```

### 3️⃣ Run Deployment

```bash
python3 deploy_platform.py
```

The script will:
1. ✅ Check prerequisites
2. ✅ Start Docker services
3. ✅ Create Python virtual environment
4. ✅ Setup PostgreSQL database
5. ✅ Generate test data
6. ✅ Configure Dremio sources
7. ✅ Setup dbt project
8. ✅ Run dbt models
9. ✅ Run dbt tests
10. ✅ Generate deployment report

---

## Manual Deployment (Alternative)

### Start Services

```bash
docker-compose up -d
```

Wait ~2 minutes for services to be ready.

### Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Generate Data

```bash
python3 scripts/generate_all_data.py
```

### Load Data to Sources

```bash
# PostgreSQL
python3 scripts/load_postgres_data.py

# Elasticsearch
python3 scripts/load_elasticsearch_data.py

# MinIO
python3 scripts/load_minio_data.py
```

### Configure Dremio Sources

1. Open http://localhost:9047
2. Login: `dremio` / `dremio123`
3. Add sources:
   - PostgreSQL: `PostgreSQL_BusinessDB`
   - Elasticsearch: `elasticsearch`
   - MinIO: `minio_sales`

### Run dbt

```bash
cd dbt
dbt debug  # Test connection
dbt run    # Build models
dbt test   # Run tests
```

---

## Access Your Platform

### 🌐 Web UIs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dremio** | http://localhost:9047 | `dremio` / `dremio123` |
| **MinIO Console** | http://localhost:9001 | `minioadmin` / `minioadmin123` |
| **Elasticsearch** | http://localhost:9200 | (no auth) |

### 🔌 Direct Connections

```bash
# PostgreSQL
psql -h localhost -p 5432 -U postgres -d business_db
# Password: postgres123

# Elasticsearch
curl http://localhost:9200/_cat/indices

# MinIO (using mc client)
mc alias set local http://localhost:9000 minioadmin minioadmin123
mc ls local/sales_data
```

---

## Verify Deployment

### Check Services

```bash
# All services running
docker-compose ps

# Dremio
curl http://localhost:9047

# Elasticsearch
curl http://localhost:9200/_cluster/health

# MinIO
curl http://localhost:9000/minio/health/live
```

### Check Data

```bash
# PostgreSQL
psql -h localhost -U postgres -d business_db -c "SELECT COUNT(*) FROM customers;"

# Elasticsearch
curl http://localhost:9200/application_logs/_count

# Dremio (via dbt)
cd dbt && dbt run --select stg_customers
```

### Check dbt Models

```bash
cd dbt

# Run all models
dbt run

# Expected output:
# - 12/12 models PASS ✅
# - ~1 minute runtime

# Run tests
dbt test

# Expected output:
# - 36/40 tests PASS ✅ (90%)
```

---

## Query Your Data

### Via Dremio UI

1. Open http://localhost:9047
2. Navigate to **$scratch.marts**
3. Click any table (e.g., `fct_business_overview`)
4. Run queries:

```sql
-- Daily business overview
SELECT 
    business_date,
    combined_revenue,
    combined_transactions,
    platform_errors,
    conversion_rate,
    error_severity
FROM "$scratch".marts.fct_business_overview
WHERE business_date >= CURRENT_DATE - 7
ORDER BY business_date DESC;

-- Customer orders
SELECT 
    c.customer_name,
    COUNT(*) as order_count,
    SUM(o.amount) as total_spent
FROM "$scratch".marts.dim_customers c
JOIN "$scratch".marts.fct_orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY total_spent DESC
LIMIT 10;
```

### Via dbt

```bash
cd dbt

# Compile and show SQL
dbt compile --select fct_business_overview

# Run specific model
dbt run --select fct_business_overview

# Run with dependencies
dbt run --select +fct_business_overview+
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker resources
docker system df

# Check logs
docker-compose logs dremio
docker-compose logs postgres
docker-compose logs elasticsearch

# Restart services
docker-compose down
docker-compose up -d
```

### Dremio Not Accessible

```bash
# Check Dremio logs
docker-compose logs dremio | tail -100

# Wait longer (first start takes ~2 minutes)
sleep 120

# Check port
netstat -an | grep 9047
```

### dbt Connection Fails

```bash
cd dbt

# Test connection
dbt debug

# Common issues:
# 1. Dremio not ready → wait and retry
# 2. Wrong credentials → check profiles.yml
# 3. Sources not configured → check Dremio UI
```

### Data Not Loading

```bash
# Check generated data
ls -lh generated_data/

# Reload PostgreSQL data
python3 scripts/load_postgres_data.py

# Check Elasticsearch indices
curl http://localhost:9200/_cat/indices

# Check MinIO bucket
docker exec -it $(docker ps -qf name=minio) mc ls /data/sales_data/
```

---

## Clean Up

### Stop Services (Keep Data)

```bash
docker-compose stop
```

### Remove Everything

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (⚠️ deletes all data)
docker-compose down -v

# Remove generated data
rm -rf generated_data/

# Remove dbt artifacts
cd dbt && rm -rf target/ logs/ dbt_packages/
```

---

## Next Steps

### 📊 Explore Data
- Open Dremio UI and browse sources
- Query `$scratch.marts` tables
- Create custom VDS (Virtual Data Sets)

### 🔧 Customize dbt Models
- Add new staging models: `dbt/models/staging/`
- Create new marts: `dbt/models/marts/`
- Run: `dbt run --select <your_model>`

### 📈 Add More Data
- Edit `config.env` volumes
- Rerun: `python3 scripts/generate_all_data.py`
- Refresh sources in Dremio

### 🚀 Production Deployment
- Review `docker-compose.yml` for production settings
- Change default passwords
- Configure backups
- Setup monitoring

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         DREMIO                              │
│                   (Data Lakehouse)                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │Elasticsearch │  │    MinIO     │    │
│  │   (RDBMS)    │  │  (NoSQL)     │  │  (Object)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQL
                            ▼
                    ┌───────────────┐
                    │      DBT      │
                    │ (Transform)   │
                    └───────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐   ┌──────────┐
     │ Staging  │    │  Marts   │   │  Tests   │
     │ (7 models)│    │(5 models)│   │   (40)   │
     └──────────┘    └──────────┘   └──────────┘
```

---

## Support

- **Documentation**: See `DBT_COMPLETION_REPORT.md`
- **Logs**: Check `deployment.log`
- **Issues**: Review `TROUBLESHOOTING.md`

---

**🎉 Happy Data Engineering!**
