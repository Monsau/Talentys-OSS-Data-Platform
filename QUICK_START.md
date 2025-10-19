# 🚀 Quick Start Guide - Data Platform v1.0 (AI-Ready)

## 📦 One-Command Launch

### Option 1: Automatic Orchestration (Recommended)

Use the **orchestrate_platform.py** script for automatic deployment with all configurations:

```bash
# Windows PowerShell - Full deployment (Data Platform + AI)
$env:PYTHONIOENCODING="utf-8"
python -u orchestrate_platform.py

# Linux/Mac - Full deployment
python orchestrate_platform.py

# Skip AI services (Data Platform only)
python orchestrate_platform.py --skip-ai
```

**What it does:**
- ✅ Checks prerequisites (Docker, Docker Compose, Python)
- ✅ Starts all Docker services (Dremio, PostgreSQL, MinIO, Elasticsearch)
- ✅ Launches Airbyte for data integration
- ✅ **Deploys AI services (Ollama LLM + Milvus + RAG API + Chat UI)**
- ✅ Configures dbt environment
- ✅ Runs dbt models and tests
- ✅ Synchronizes Dremio data to PostgreSQL
- ✅ Creates Superset dashboards automatically
- ✅ Generates Open Data dashboard
- ✅ **Sets up local LLM (Llama 3.1) for AI-powered insights**

**Options:**
```bash
# Show help
python orchestrate_platform.py --help

# Skip infrastructure deployment (if already running)
python orchestrate_platform.py --skip-infrastructure

# Skip AI services deployment
python orchestrate_platform.py --skip-ai

# Custom workspace path
python orchestrate_platform.py --workspace /path/to/workspace
```

### Option 2: Manual Docker Launch

Start services manually:

```bash
# Start full stack (Data Platform + AI Services)
docker-compose -f docker-compose.yml -f docker-compose-airbyte-stable.yml -f docker-compose-ai.yml up -d

# Start data platform only (no AI)
docker-compose -f docker-compose.yml -f docker-compose-airbyte-stable.yml up -d

# Start main stack only (minimal)
docker-compose up -d
```

---

## 🌐 Access Services

### Data Platform

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airbyte** | http://localhost:8000 | airbyte / password |
| **Dremio** | http://localhost:9047 | admin / admin123 |
| **Superset** | http://localhost:8088 | admin / admin |
| **Airflow** | http://localhost:8080 | airflow / airflow |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin |
| **OpenMetadata** | http://localhost:8585 | admin / admin |

### AI Services (NEW)

| Service | URL | Description |
|---------|-----|-------------|
| **AI Chat UI** | http://localhost:8501 | 💬 Ask questions about your data in natural language |
| RAG API | http://localhost:8002 | 🔌 REST API for AI queries |
| RAG API Docs | http://localhost:8002/docs | 📖 Interactive API documentation |
| Ollama LLM | http://localhost:11434 | 🤖 Local language model server (Llama 3.1) |
| Milvus Vector DB | localhost:19530 | 🧠 Semantic search database (gRPC) |
| Embedding Service | http://localhost:8001 | 🔢 Text-to-vector conversion service |

---

## 🤖 AI Services - Ask Questions About Your Data

### Step 1: Access AI Chat UI

Open your browser and navigate to **http://localhost:8501**

The Chat UI provides:
- 💬 Natural language interface to query your data
- 📚 Automatic context retrieval from your databases
- 🔍 Source attribution showing where answers come from
- 📤 **Document upload (PDF, Word, Excel, CSV, JSON, TXT, Markdown)** - NEW!
- 🎨 Interactive data ingestion controls

### Step 2: Ingest Your Data

Before asking questions, you need to ingest data into the vector database.

#### Option A: Upload Documents (NEW - Easiest for Files!)

1. Open **http://localhost:8501**
2. Look for the **"📤 Upload Documents"** section in the sidebar
3. **Upload your files:**
   - Click "Choose files to upload" or drag & drop
   - Supported formats: **PDF, Word (.docx), Excel (.xlsx), CSV, JSON, TXT, Markdown**
   - Add optional metadata:
     - Source/Category: e.g., "product-docs", "customer-feedback"
     - Tags: e.g., "Q4, sales, confidential"
   - Click **"🚀 Upload & Ingest Documents"**

4. **Files are automatically processed:**
   - Text extracted based on file type
   - Split into chunks for better context
   - Converted to vectors and stored in Milvus
   - Ready for querying immediately!

**Example Use Cases:**
- 📄 Upload product manuals (PDF)
- 📊 Upload sales reports (Excel)
- 📝 Upload policy documents (Word)
- 📋 Upload customer feedback (CSV)
- 🔧 Upload API documentation (Markdown)

#### Option B: Ingest from Database

1. Open **http://localhost:8501**
2. Look for the **"📥 Ingest from Database"** section in the sidebar
3. **Ingest from PostgreSQL:**
   - Table name: `customers` (or any table from your PostgreSQL)
   - Text column: `description` (column containing text data)
   - Metadata columns: `customer_id,name,segment` (comma-separated)
   - Click **"Ingest PostgreSQL"**

4. **Ingest from Dremio:**
   - SQL query: `SELECT * FROM "PostgreSQL"."public"."customers"`
   - Text column: `description`
   - Click **"Ingest Dremio"**

#### Option C: Via API (Programmatic)

**Upload Document via API:**

```bash
# Upload a PDF file
curl -X POST http://localhost:8002/upload/document \
  -F "file=@/path/to/document.pdf" \
  -F "source=technical-docs" \
  -F "tags=manual,v1.0"

# Upload Excel file
curl -X POST http://localhost:8002/upload/document \
  -F "file=@/path/to/report.xlsx" \
  -F "source=quarterly-report" \
  -F "tags=Q4,finance,2024"
```

**Ingest from Database via API:**

```bash
# Ingest PostgreSQL table
curl -X POST http://localhost:8002/ingest/postgres \
  -H "Content-Type: application/json" \
  -d '{
    "table": "customers",
    "text_column": "description",
    "metadata_columns": ["customer_id", "name", "segment"]
  }'

# Ingest Dremio query
curl -X POST http://localhost:8002/ingest/dremio \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "SELECT * FROM \"PostgreSQL\".\"public\".\"products\"",
    "text_column": "product_description"
  }'

# Check available models
curl http://localhost:8002/models
```

#### Option C: Automatic Ingestion (Scheduled)

The Data Ingestion Service automatically ingests configured tables every hour/day/week.

Edit `ai-services/data-ingestion/ingestion.py` to configure tables:

```python
TABLES_TO_INGEST = [
    {
        "table": "customers",
        "text_column": "description",
        "metadata_columns": ["customer_id", "name"],
        "schedule": "daily"  # "hourly", "daily", or "weekly"
    }
]
```

### Step 3: Ask Questions

Once data is ingested, you can ask questions in natural language:

**Example Questions:**

- "What are our top-performing products based on sales data?"
- "Show me customer segments with the highest revenue"
- "Are there any data quality issues in the orders table?"
- "Generate a SQL query to find customers who purchased in the last 30 days"
- "Explain the ETL pipeline for sales data"
- "What trends do you see in our quarterly revenue?"
- "Which products have the most returns?"

**Via Chat UI (http://localhost:8501):**

1. Type your question in the chat input
2. Click Send or press Enter
3. View the AI-generated answer with sources
4. Expand source documents to see retrieved context

**Via API:**

```bash
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key trends in our sales data?",
    "top_k": 5,
    "model": "llama3.1",
    "temperature": 0.7
  }'
```

**Via Python:**

```python
import httpx

response = httpx.post(
    "http://localhost:8002/query",
    json={
        "question": "What are our top customers?",
        "top_k": 5,
        "model": "llama3.1"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])} documents")
for source in result['sources']:
    print(f"  - {source['text'][:100]}... (score: {source['score']})")
```

### LLM Models Available

The platform includes **Llama 3.1** (8B parameters) by default. You can download additional models:

| Model | Size | Best For | Download Command |
|-------|------|----------|------------------|
| **llama3.1** | ~5GB | General purpose, high quality | Pre-installed ✅ |
| mistral | ~4GB | Fast inference, coding tasks | `docker exec ollama ollama pull mistral` |
| phi3 | ~2GB | Lightweight, quick responses | `docker exec ollama ollama pull phi3` |
| codellama | ~4GB | Code generation | `docker exec ollama ollama pull codellama` |

**Switch models in Chat UI:**
- Use the model selector in the sidebar
- Adjust temperature (0.0 = deterministic, 1.0 = creative)
- Change top_k (number of context documents to retrieve)

### Troubleshooting AI Services

**Issue: "Ollama not responding"**
```bash
# Check if Ollama is running
docker ps | grep ollama

# Restart Ollama
docker restart ollama

# Check Ollama logs
docker logs ollama
```

**Issue: "No data found in vector database"**
- Make sure you've ingested data first (see Step 2 above)
- Check RAG API logs: `docker logs rag-api`
- Verify Milvus is running: `docker ps | grep milvus`

**Issue: "Slow LLM responses"**
- Consider using a smaller model (phi3 instead of llama3.1)
- Enable GPU acceleration (see `docker-compose-ai.yml`)
- Reduce `top_k` parameter to retrieve fewer documents

**Check AI service health:**
```bash
# RAG API health check
curl http://localhost:8002/health

# Embedding service health
curl http://localhost:8001/health

# Ollama models list
docker exec ollama ollama list

# Milvus statistics
curl http://localhost:9091/metrics
```

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
