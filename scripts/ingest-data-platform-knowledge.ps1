# Ingest Data Platform Knowledge into RAG System
# This script loads information about your data sources, datasets, and structure into the AI assistant

Write-Host "`n=== DATA PLATFORM KNOWLEDGE INGESTION ===" -ForegroundColor Cyan
Write-Host "Loading information into AI assistant...`n"

$ragApiUrl = "http://localhost:8002"

# ============================================
# 1. Data Platform Overview
# ============================================
Write-Host "[1/6] Ingesting data platform overview..." -ForegroundColor Yellow

$platformOverview = @'
DATA PLATFORM OVERVIEW

Platform Name: Dremio Data Platform
Version: Production v1.0
Status: Operational
Access URL: http://localhost:9047

Architecture:
- Analytics Engine: Dremio (port 9047)
- Storage Layer: MinIO S3-compatible storage (ports 9000-9001)
- Metadata Store: PostgreSQL (port 5432)
- Search Engine: Elasticsearch (ports 9200-9300)
- Catalog: Apache Polaris Iceberg (port 8181)

Data Governance:
- OpenMetadata integration available
- Lineage tracking enabled
- Data quality monitoring active

AI Services:
- Chat UI: http://localhost:8501
- RAG API: http://localhost:8002
- Embedding Service: http://localhost:8001
- LLM: Llama 3.1 (via Ollama on port 11434)
- Vector Database: Milvus (port 19530)
'@

$body = @{
    texts = @($platformOverview)
    metadata = @(
        @{
            source = "platform_overview"
            type = "documentation"
            category = "architecture"
            timestamp = (Get-Date -Format "o")
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "$ragApiUrl/ingest/bulk" -Method POST -Body $body -ContentType "application/json" | Out-Null
Write-Host "  ✓ Platform overview loaded" -ForegroundColor Green

# ============================================
# 2. Available Data Sources
# ============================================
Write-Host "[2/6] Ingesting data sources information..." -ForegroundColor Yellow

$dataSources = @'
AVAILABLE DATA SOURCES

1. MinIO Storage (MinIO_Storage)
   - Type: S3-compatible object storage
   - Status: Available and healthy
   - Access: http://localhost:9001
   - Credentials: minioadmin / minioadmin123
   - Location: c:\projets\dremiodbt\minio\sample-data\
   
2. PostgreSQL Database (dremio-postgres)
   - Type: Relational database
   - Status: Running and healthy
   - Port: 5432
   - Database: business_db
   - Credentials: postgres / postgres123
   
3. Elasticsearch
   - Type: Search and analytics engine
   - Status: Running and healthy
   - Ports: 9200 (HTTP), 9300 (Transport)
   
Connection Information:
- All sources accessible via Dremio UI at http://localhost:9047
- Use SQL queries to access data across all sources
- Data federation enabled for cross-source queries
'@

$body = @{
    texts = @($dataSources)
    metadata = @(
        @{
            source = "data_sources"
            type = "documentation"
            category = "data_sources"
            timestamp = (Get-Date -Format "o")
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "$ragApiUrl/ingest/bulk" -Method POST -Body $body -ContentType "application/json" | Out-Null
Write-Host "  ✓ Data sources loaded" -ForegroundColor Green

# ============================================
# 3. Available Datasets
# ============================================
Write-Host "[3/6] Ingesting datasets information..." -ForegroundColor Yellow

$datasets = @'
AVAILABLE DATASETS

1. ANALYTICS SUMMARY (analytics_summary.json)
   - Format: JSON
   - Location: MinIO_Storage/sample-data/
   - Content: Q1 2025 sales and operational metrics
   - Fields: sales_metrics, product_performance, customer_segments, operational_metrics
   - Size: Comprehensive business intelligence data
   
2. TRANSACTIONS 2025 (transactions_2025.csv)
   - Format: CSV
   - Location: MinIO_Storage/sample-data/
   - Period: January-February 2025
   - Fields: transaction_id, customer_id, transaction_date, amount, currency, payment_method, status
   - Content: Real-time transaction records with multiple currencies (USD, EUR, GBP, SEK, CZK, CHF)
   
3. CUSTOMERS (customers_external.csv)
   - Format: CSV
   - Location: MinIO_Storage/sample-data/
   - Fields: id, name, email, phone, address, city, country, company, job_title, created_at
   - Content: Multi-language customer database (French, Japanese, Chinese, Arabic)
   
4. PRODUCTS CATALOG (products_catalog.csv)
   - Format: CSV
   - Location: MinIO_Storage/sample-data/
   - Fields: id, name, description, price, category, created_at, language
   - Content: Multi-language product descriptions with pricing
   
5. INVENTORY DETAILED (inventory_detailed.csv)
   - Format: CSV
   - Location: MinIO_Storage/sample-data/
   - Fields: Product inventory and stock management data
   - Content: Warehouse utilization, stock levels, fulfillment metrics

Query Examples:
SELECT * FROM MinIO_Storage."sample-data"."analytics_summary" LIMIT 10;
SELECT * FROM MinIO_Storage."sample-data"."transactions_2025" WHERE transaction_type = 'purchase';
SELECT customer_id, SUM(amount) as total FROM MinIO_Storage."sample-data"."transactions_2025" GROUP BY customer_id;
'@

$body = @{
    texts = @($datasets)
    metadata = @(
        @{
            source = "datasets"
            type = "documentation"
            category = "datasets"
            timestamp = (Get-Date -Format "o")
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "$ragApiUrl/ingest/bulk" -Method POST -Body $body -ContentType "application/json" | Out-Null
Write-Host "  ✓ Datasets information loaded" -ForegroundColor Green

# ============================================
# 4. Sales Data (2025 Q1)
# ============================================
Write-Host "[4/6] Ingesting sales data (2025)..." -ForegroundColor Yellow

$salesData = @'
SALES DATA - Q1 2025

TOTAL REVENUE: $7,259,247.55 USD

Regional Breakdown:

1. North America
   - Countries: USA, Canada
   - Revenue: $2,456,789.50
   - Orders: 15,234
   - Average Order Value: $161.25
   - Top Categories: Electronics, Furniture, Sports

2. Europe
   - Countries: France, Germany, UK, Italy, Spain
   - Revenue: $3,567,890.25
   - Orders: 22,456
   - Average Order Value: $158.90
   - Top Categories: Electronics, Appliances, Clothing

3. Asia Pacific
   - Countries: Japan, Korea, Singapore, Australia
   - Revenue: $1,234,567.80
   - Orders: 9,876
   - Average Order Value: $125.05
   - Top Categories: Electronics, Books, Sports

Best Selling Products:
1. SKU-PHONE-002: $1,637,766.00 revenue (2,340 units sold)
2. SKU-LAPTOP-001: $1,566,350.95 revenue (1,205 units sold)
3. SKU-MONITOR-006: $513,144.44 revenue (856 units sold)

Trending Products (Growth Rate):
1. SKU-WATCH-010: +45.6% growth
2. SKU-YOGA-009: +38.2% growth
3. SKU-DESK-008: +32.1% growth

Customer Segments:
- Platinum: 245 customers, $2,890.45 avg spend, 95.2% retention
- Gold: 1,234 customers, $1,567.89 avg spend, 87.5% retention
- Silver: 3,456 customers, $890.23 avg spend, 72.3% retention
- Bronze: 5,678 customers, $345.67 avg spend, 58.9% retention

NOTE: Historical data for 2023 is NOT available in the current dataset.
Only 2025 data is present (Q1 2025 and ongoing transactions).
'@

$body = @{
    texts = @($salesData)
    metadata = @(
        @{
            source = "sales_data_2025"
            type = "business_data"
            category = "sales"
            period = "2025-Q1"
            timestamp = (Get-Date -Format "o")
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "$ragApiUrl/ingest/bulk" -Method POST -Body $body -ContentType "application/json" | Out-Null
Write-Host "  ✓ Sales data (2025) loaded" -ForegroundColor Green

# ============================================
# 5. Operational Metrics
# ============================================
Write-Host "[5/6] Ingesting operational metrics..." -ForegroundColor Yellow

$operationalMetrics = @'
OPERATIONAL METRICS - Q1 2025

Inventory Management:
- Total Products: 15,234 SKUs
- Low Stock Items: 89 products
- Out of Stock: 12 products
- Warehouse Utilization: 78.5%

Fulfillment Performance:
- Average Processing Time: 24.5 hours
- Same-Day Delivery Rate: 23.8%
- Next-Day Delivery Rate: 67.2%
- Return Rate: 4.2%

Payment Methods Distribution:
- Credit Card: Primary method
- PayPal: Available
- Bank Transfer: Available
- Debit Card: Available
- Regional methods: Swish (Sweden), Twint (Switzerland), Multibanco (Portugal), iDEAL (Netherlands), Sofort (Germany)

Transaction Status Distribution:
- Completed: Majority
- Pending: Some
- Failed: Minimal
- Refunds: Tracked

Data Quality:
- Data freshness: Real-time
- Data completeness: High
- Data accuracy: Validated
- Last updated: October 2025
'@

$body = @{
    texts = @($operationalMetrics)
    metadata = @(
        @{
            source = "operational_metrics"
            type = "business_data"
            category = "operations"
            period = "2025-Q1"
            timestamp = (Get-Date -Format "o")
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "$ragApiUrl/ingest/bulk" -Method POST -Body $body -ContentType "application/json" | Out-Null
Write-Host "  ✓ Operational metrics loaded" -ForegroundColor Green

# ============================================
# 6. How to Use the Platform
# ============================================
Write-Host "[6/6] Ingesting usage guidelines..." -ForegroundColor Yellow

$usageGuide = @'
HOW TO USE THE DATA PLATFORM

Accessing Data:
1. Dremio UI: Navigate to http://localhost:9047
2. Login with credentials: admin / admin123
3. Browse data sources in the left panel
4. Click on MinIO_Storage to see available datasets

Running SQL Queries:
- Click "New Query" button in Dremio
- Write SQL using standard syntax
- Example: SELECT * FROM MinIO_Storage."sample-data"."transactions_2025" WHERE amount > 500
- Execute with Run button or Ctrl+Enter

Analyzing Data:
- Use SQL aggregations: SUM, AVG, COUNT, GROUP BY
- Join across sources using standard SQL JOIN syntax
- Create virtual datasets for reusable queries
- Export results to CSV/Excel

AI Assistant Features:
- Ask questions in natural language
- Get insights from your data
- Upload documents (PDF, Word, Excel) to expand knowledge base
- Supported formats: PDF, DOCX, XLSX, CSV, TXT, JSON

Common Questions:
Q: "What are the sales of 2023?"
A: 2023 data is not available. Only 2025 data (Q1 and ongoing) exists.

Q: "Show me total revenue by region"
A: North America: $2.46M, Europe: $3.57M, Asia Pacific: $1.23M (Q1 2025)

Q: "Which products are selling best?"
A: Top 3 are SKU-PHONE-002 ($1.64M), SKU-LAPTOP-001 ($1.57M), SKU-MONITOR-006 ($0.51M)

Q: "What payment methods are available?"
A: Credit card, PayPal, bank transfer, and regional methods (Swish, Twint, Multibanco, iDEAL, Sofort)

Data Upload:
- Use Chat UI sidebar to upload documents
- Supported: PDF, Word, Excel, CSV, Text
- Documents are stored in MinIO (S3)
- Content is indexed for AI search
'@

$body = @{
    texts = @($usageGuide)
    metadata = @(
        @{
            source = "usage_guide"
            type = "documentation"
            category = "help"
            timestamp = (Get-Date -Format "o")
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "$ragApiUrl/ingest/bulk" -Method POST -Body $body -ContentType "application/json" | Out-Null
Write-Host "  ✓ Usage guidelines loaded" -ForegroundColor Green

# ============================================
# Verification
# ============================================
Write-Host "`n[Verification] Testing RAG system..." -ForegroundColor Yellow

$testQuery = @{
    question = "What data sources are available?"
    top_k = 3
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "$ragApiUrl/query" -Method POST -Body $testQuery -ContentType "application/json"
$result = $response.Content | ConvertFrom-Json

Write-Host "`nTest Query: What data sources are available?"
Write-Host "Sources Found: $($result.sources.Count)" -ForegroundColor $(if ($result.sources.Count -gt 0) { "Green" } else { "Red" })

if ($result.sources.Count -gt 0) {
    Write-Host "`nRAG system is working!" -ForegroundColor Green
    Write-Host "Answer preview: $($result.answer.Substring(0, [Math]::Min(200, $result.answer.Length)))..." -ForegroundColor Cyan
} else {
    Write-Host "`nNo sources found - ingestion may have failed" -ForegroundColor Yellow
}

Write-Host "`n=== INGESTION COMPLETE ===" -ForegroundColor Green
Write-Host "Knowledge base loaded with:"
Write-Host "  - Platform overview and architecture"
Write-Host "  - Data sources and connection info"
Write-Host "  - Available datasets and schemas"
Write-Host "  - Sales data 2025 Q1"
Write-Host "  - Operational metrics"
Write-Host "  - Usage guidelines"
Write-Host "`nYour AI assistant is now ready to answer questions!"
Write-Host "Try asking in the Chat UI at http://localhost:8501"
Write-Host "  - What are the sales of 2025"
Write-Host "  - What data sources do I have"
Write-Host "  - Show me the best selling products"
Write-Host "  - How do I query my data"
Write-Host ""
