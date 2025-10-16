# Apache Superset Dashboard Guide

**Version**: 3.2.0  
**Last Updated**: October 16, 2025  
**Language**: English

## Table of Contents

1. [Overview](#overview)
2. [Initial Setup](#initial-setup)
3. [Connecting Data Sources](#connecting-data-sources)
4. [Creating Charts](#creating-charts)
5. [Building Dashboards](#building-dashboards)
6. [Advanced Features](#advanced-features)
7. [Security and Permissions](#security-and-permissions)
8. [Performance Optimization](#performance-optimization)
9. [Embedding and Sharing](#embedding-and-sharing)
10. [Best Practices](#best-practices)

---

## Overview

Apache Superset is a modern, enterprise-ready business intelligence web application that enables users to explore and visualize data through intuitive dashboards and charts.

### Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **SQL IDE** | Interactive SQL editor with autocomplete | Ad-hoc analysis |
| **Rich Visualizations** | 50+ chart types | Diverse data representation |
| **Dashboard Builder** | Drag-and-drop interface | Easy dashboard creation |
| **Caching** | Query result caching | Fast load times |
| **Security** | Row-level security, role-based access | Data governance |
| **Alerts** | Automated email/Slack notifications | Proactive monitoring |

### Architecture Integration

```mermaid
graph LR
    A[User Browser] --> B[Superset Web]
    B --> C[Superset Database<br/>PostgreSQL]
    B --> D{Data Sources}
    
    D --> E[Dremio<br/>Arrow Flight]
    D --> F[PostgreSQL]
    D --> G[Elasticsearch]
    
    E --> H[MinIO S3<br/>Data Lake]
    
    B --> I[Cache Layer<br/>Redis]
    
    style A fill:#e1f5ff
    style B fill:#20A7C9,color:#fff
    style C fill:#336791,color:#fff
    style E fill:#FDB515
    style H fill:#C72E49,color:#fff
    style I fill:#DC382D,color:#fff
```

---

## Initial Setup

### First Login

Access Superset at `http://localhost:8088`:

```
Default Credentials:
Username: admin
Password: admin
```

**Security Note**: Change the default password immediately after first login.

### Initial Configuration

```bash
# Inside Superset container
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@company.com \
  --password your_secure_password

# Initialize database
superset db upgrade

# Load example data (optional)
superset load_examples

# Initialize roles and permissions
superset init
```

### Configuration File

```python
# superset_config.py

# Flask App Configuration
SECRET_KEY = 'your-secret-key-here'  # Change this!
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Database Configuration
SQLALCHEMY_DATABASE_URI = 'postgresql://superset:superset@postgres:5432/superset'

# Cache Configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
}

# Results Backend (for async queries)
RESULTS_BACKEND = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_results_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 2,
}

# Feature Flags
FEATURE_FLAGS = {
    'ALERT_REPORTS': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_RBAC': True,
    'EMBEDDABLE_CHARTS': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
}

# Row Limit for SQL Lab
SQL_MAX_ROW = 100000
SUPERSET_WEBSERVER_TIMEOUT = 60

# Enable async queries
SUPERSET_CELERY_WORKERS = 4
```

---

## Connecting Data Sources

### Connect to Dremio

#### Step 1: Install Dremio Database Driver

```bash
# Install Arrow Flight SQL connector
pip install pyarrow adbc-driver-flightsql
```

#### Step 2: Add Dremio Database

```
UI → Settings → Database Connections → + Database
```

**Configuration**:
```json
{
  "database_name": "Dremio",
  "sqlalchemy_uri": "dremio+flight://admin:password@localhost:32010/datalake",
  "expose_in_sqllab": true,
  "allow_ctas": true,
  "allow_cvas": true,
  "allow_dml": false,
  "extra": {
    "engine_params": {
      "connect_args": {
        "use_encryption": false
      }
    },
    "metadata_params": {},
    "metadata_cache_timeout": 86400,
    "schemas_allowed_for_csv_upload": []
  }
}
```

#### Step 3: Test Connection

```sql
-- Test query in SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Connect to PostgreSQL

```json
{
  "database_name": "PostgreSQL",
  "sqlalchemy_uri": "postgresql://postgres:postgres@postgres:5432/datawarehouse",
  "expose_in_sqllab": true,
  "allow_ctas": true,
  "allow_cvas": true,
  "extra": {
    "metadata_cache_timeout": 3600,
    "engine_params": {
      "pool_size": 10,
      "pool_recycle": 3600
    }
  }
}
```

### Connect to Elasticsearch

```json
{
  "database_name": "Elasticsearch",
  "sqlalchemy_uri": "elasticsearch+http://elasticsearch:9200",
  "expose_in_sqllab": true,
  "allow_ctas": false,
  "allow_cvas": false,
  "extra": {
    "metadata_cache_timeout": 600
  }
}
```

---

## Creating Charts

### Chart Creation Workflow

```mermaid
sequenceDiagram
    participant User
    participant Superset
    participant Database
    participant Cache
    
    User->>Superset: Select dataset
    User->>Superset: Choose chart type
    User->>Superset: Configure metrics & filters
    Superset->>Cache: Check cache
    
    alt Cache Hit
        Cache-->>Superset: Return cached data
    else Cache Miss
        Superset->>Database: Execute query
        Database-->>Superset: Return results
        Superset->>Cache: Store results
    end
    
    Superset->>User: Render visualization
    User->>Superset: Save chart
```

### Chart Type Selection

| Chart Type | Best For | Example Use Case |
|------------|----------|------------------|
| **Line Chart** | Trends over time | Daily revenue trend |
| **Bar Chart** | Comparisons | Revenue by product category |
| **Pie Chart** | Part-to-whole | Market share by region |
| **Table** | Detailed data | Customer list with metrics |
| **Big Number** | Single metric | Total YTD revenue |
| **Heatmap** | Pattern detection | Sales by day/hour |
| **Scatter Plot** | Correlations | Customer value vs frequency |
| **Sankey Diagram** | Flow analysis | User journey paths |

### Example: Line Chart (Revenue Trend)

#### Step 1: Create Dataset

```
UI → Data → Datasets → + Dataset
```

**Configuration**:
- **Database**: Dremio
- **Schema**: Production.Marts
- **Table**: mart_daily_revenue

#### Step 2: Create Chart

```
UI → Charts → + Chart → Line Chart
```

**Settings**:
```yaml
Dataset: mart_daily_revenue

Query:
  Metrics:
    - SUM(total_revenue) AS "Total Revenue"
  Dimensions:
    - revenue_date
  Filters:
    - revenue_date >= 2025-01-01
  Row Limit: 365

Customize:
  X Axis: revenue_date
  Y Axis: Total Revenue
  Rolling Average: 7 days
  Show Data Points: Yes
  Line Style: Smooth
  Color Scheme: Superset Default
```

**SQL Generated**:
```sql
SELECT 
    revenue_date AS "Date",
    SUM(total_revenue) AS "Total Revenue"
FROM Production.Marts.mart_daily_revenue
WHERE revenue_date >= '2025-01-01'
GROUP BY revenue_date
ORDER BY revenue_date
LIMIT 365
```

### Example: Bar Chart (Top Customers)

```yaml
Chart Type: Bar Chart

Dataset: mart_customer_lifetime_value

Query:
  Metrics:
    - lifetime_value AS "Lifetime Value"
  Dimensions:
    - full_name AS "Customer"
  Filters:
    - customer_status = 'Active'
  Sort By: lifetime_value DESC
  Row Limit: 10

Customize:
  Orientation: Horizontal
  Show Values: Yes
  Color: By Metric
  Bar Width: 0.8
```

### Example: Pivot Table

```yaml
Chart Type: Pivot Table

Dataset: fct_orders

Query:
  Metrics:
    - SUM(total_amount) AS "Revenue"
    - COUNT(*) AS "Order Count"
    - AVG(total_amount) AS "Avg Order Value"
  
  Rows:
    - DATE_TRUNC('month', order_date) AS "Month"
  
  Columns:
    - customer_segment
  
  Filters:
    - order_date >= 2025-01-01
    - status = 'COMPLETED'

Customize:
  Show Totals: Row & Column
  Conditional Formatting:
    Revenue > 100000: Green
    Revenue < 50000: Red
```

### Example: Big Number with Trend

```yaml
Chart Type: Big Number with Trendline

Dataset: mart_daily_revenue

Query:
  Metric: SUM(total_revenue)
  Time Column: revenue_date
  Time Range: Last 30 days
  Compare To: Previous Period

Customize:
  Number Format: $,.2f
  Show Trend: Yes
  Trend Calculation: Week over Week
  Color Positive: Green
  Color Negative: Red
```

---

## Building Dashboards

### Dashboard Creation Process

```mermaid
flowchart TB
    A[Create Dashboard] --> B[Add Charts]
    B --> C[Arrange Layout]
    C --> D[Add Filters]
    D --> E[Configure Interactions]
    E --> F[Set Refresh Schedule]
    F --> G[Publish Dashboard]
    
    style A fill:#20A7C9,color:#fff
    style G fill:#4CAF50,color:#fff
```

### Step 1: Create Dashboard

```
UI → Dashboards → + Dashboard
```

**Dashboard Settings**:
```yaml
Title: Customer Analytics Dashboard
Owners: [analytics_team]
Color Scheme: Superset Default
JSON Metadata:
  refresh_frequency: 300  # 5 minutes
  timed_refresh_immune_slices: []
  expanded_slices: {}
  filter_scopes: {}
  default_filters: "{}"
  color_scheme: ""
```

### Step 2: Add Charts

Drag and drop charts from the left panel or create new ones:

```
+ → Existing Chart → Select chart
+ → Create New Chart → Choose type
```

### Step 3: Layout Design

**Grid System**:
- 12 columns wide
- Charts snap to grid
- Drag to resize and reposition

**Example Layout**:
```
┌────────────────────────────────────────────────────┐
│  Big Number: Total Revenue  │  Big Number: Orders  │
│         (6 columns)          │      (6 columns)     │
├─────────────────────────────┴──────────────────────┤
│           Line Chart: Daily Revenue Trend          │
│                  (12 columns)                       │
├───────────────────────┬────────────────────────────┤
│  Top 10 Customers     │  Revenue by Segment        │
│  (Bar Chart)          │  (Pie Chart)               │
│  (6 columns)          │  (6 columns)               │
├───────────────────────┴────────────────────────────┤
│           Pivot Table: Revenue by Month/Segment    │
│                  (12 columns)                       │
└────────────────────────────────────────────────────┘
```

### Step 4: Add Dashboard Filters

```
Dashboard → Edit → + Filter
```

**Date Range Filter**:
```yaml
Filter Type: Date Range
Target: revenue_date
Columns:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Default Value: Last 30 days
```

**Categorical Filter**:
```yaml
Filter Type: Select
Target: customer_segment
Columns:
  - fct_orders.customer_segment
  - mart_customer_lifetime_value.customer_segment
Values: [New Customer, Regular Customer, Long-term Customer]
Default: All
Multiple Selection: Yes
Search Enabled: Yes
```

**Numeric Filter**:
```yaml
Filter Type: Number Range
Target: lifetime_value
Columns:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Default: [0, 10000]
```

### Step 5: Cross-Filtering

Enable dashboard cross-filtering:

```
Dashboard → Edit → Settings → Enable Cross-filtering
```

**Configuration**:
```yaml
Enable Cross-filtering: Yes
Cross-filter Scopes:
  Chart 1 (Bar Chart):
    Affects: [Chart 2, Chart 3, Chart 4]
  Chart 2 (Pie Chart):
    Affects: [Chart 1, Chart 3]
```

**User Experience**:
- Click on bar → filters entire dashboard
- Click on pie slice → updates related charts
- Clear filter → resets to default view

---

## Advanced Features

### SQL Lab

Interactive SQL editor for ad-hoc queries.

#### Execute Query

```sql
-- SQL Lab query example
SELECT 
    c.customer_tier,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    SUM(o.total_amount) AS total_revenue,
    AVG(o.total_amount) AS avg_order_value,
    ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM Production.Dimensions.dim_customers c
INNER JOIN Production.Facts.fct_orders o
    ON c.customer_id = o.customer_id
WHERE o.status = 'COMPLETED'
  AND o.order_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY c.customer_tier
ORDER BY total_revenue DESC;
```

**Features**:
- Autocomplete for tables and columns
- Query history
- Multiple tabs
- Result export (CSV, JSON)
- Save query for reuse

#### Create Table from Query (CTAS)

```sql
-- Create temporary table
CREATE TABLE temp_customer_summary AS
SELECT 
    customer_id,
    full_name,
    lifetime_value,
    customer_tier
FROM Production.Dimensions.dim_customers
WHERE lifetime_value > 1000;

-- Query the new table
SELECT * FROM temp_customer_summary;
```

### Jinja Templating

Dynamic SQL with Jinja2 templates:

```sql
-- Filter with Jinja template
SELECT 
    order_date,
    SUM(total_amount) AS revenue
FROM Production.Facts.fct_orders
WHERE order_date >= '{{ from_dttm }}'
  AND order_date < '{{ to_dttm }}'
{% if filter_values('customer_segment')|length > 0 %}
  AND customer_segment IN ({{ "'" + "','".join(filter_values('customer_segment')) + "'" }})
{% endif %}
GROUP BY order_date
ORDER BY order_date;
```

**Template Variables**:
- `{{ from_dttm }}` - Start of date range
- `{{ to_dttm }}` - End of date range
- `{{ filter_values('column') }}` - Selected filter values
- `{{ current_username }}` - Logged-in user

### Alerts and Reports

#### Create Alert

```
UI → Alerts & Reports → + Alert
```

**Configuration**:
```yaml
Name: Daily Revenue Alert
Type: Alert
Database: Dremio
SQL:
  SELECT SUM(total_revenue) AS daily_revenue
  FROM Production.Marts.mart_daily_revenue
  WHERE revenue_date = CURRENT_DATE

Condition:
  - daily_revenue < 50000  # Alert if revenue below threshold

Schedule:
  Type: Cron
  Expression: "0 18 * * *"  # 6 PM daily

Recipients:
  - email: finance@company.com
  - slack: #revenue-alerts

Message:
  Subject: "Low Revenue Alert"
  Body: "Daily revenue is {{ daily_revenue | currency }}, below threshold of $50,000"
```

#### Create Report

```yaml
Name: Weekly Customer Report
Type: Report
Dashboard: Customer Analytics Dashboard

Schedule:
  Type: Cron
  Expression: "0 9 * * 1"  # Monday 9 AM

Format: PDF
Recipients:
  - email: executives@company.com

Content:
  Include: All charts
  Filters:
    date_range: Last 7 days
```

### Custom Visualization Plugins

Create custom chart types:

```javascript
// src/MyCustomChart/MyCustomChart.tsx
import React from 'react';
import { SupersetPluginChartProps } from '@superset-ui/core';

export default function MyCustomChart(props: SupersetPluginChartProps) {
  const { data, height, width } = props;
  
  return (
    <div style={{ height, width }}>
      <h2>Custom Chart</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
```

Build and install:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Security and Permissions

### Role-Based Access Control (RBAC)

```mermaid
graph TB
    subgraph "Users"
        U1[Admin User]
        U2[Analyst User]
        U3[Viewer User]
    end
    
    subgraph "Roles"
        R1[Admin]
        R2[Alpha]
        R3[Gamma]
    end
    
    subgraph "Permissions"
        P1[All Database Access]
        P2[All Dashboard Access]
        P3[Can Edit]
        P4[Can Explore]
        P5[Can View]
    end
    
    U1 --> R1
    U2 --> R2
    U3 --> R3
    
    R1 --> P1 & P2 & P3
    R2 --> P2 & P3 & P4
    R3 --> P2 & P5
    
    style R1 fill:#FF6B6B
    style R2 fill:#4ECDC4
    style R3 fill:#95E1D3
```

### Built-in Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | All permissions | System administrators |
| **Alpha** | Create, edit, delete dashboards/charts | Data analysts |
| **Gamma** | View dashboards, run SQL Lab queries | Business users |
| **sql_lab** | Access SQL Lab only | Data scientists |
| **Public** | View public dashboards only | Anonymous users |

### Create Custom Role

```
UI → Settings → List Roles → + Role
```

**Example: Marketing Analyst Role**
```yaml
Name: Marketing Analyst
Permissions:
  - can read on Dashboard
  - can write on Dashboard
  - can read on Chart
  - can write on Chart
  - database access on [Dremio]
  - schema access on [Production.Marts]
  - datasource access on [mart_customer_lifetime_value, mart_marketing_attribution]
```

### Row-Level Security (RLS)

Restrict data based on user attributes:

```
UI → Data → Datasets → [dataset] → Edit → Row Level Security
```

**Example: Region-Based RLS**
```sql
-- Filter: User sees only their region's data
region = '{{ current_user_region() }}'
```

**Example: Customer-Based RLS**
```sql
-- Filter: Sales rep sees only their customers
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Database Connection Security

```python
# superset_config.py

# Encrypt connection passwords
SQLALCHEMY_DATABASE_URI = 'postgresql://user:encrypted_password@host/db'

# Use environment variables
import os
SQLALCHEMY_DATABASE_URI = os.environ.get('SUPERSET_DATABASE_URI')

# SSL for database connections
DATABASE_EXTRA_PARAMS = {
    'sslmode': 'require',
    'sslrootcert': '/path/to/ca-cert.pem'
}
```

---

## Performance Optimization

### Query Caching

```python
# superset_config.py

# Cache query results for 1 hour
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
}

# Cache dashboard filter state
FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
}
```

**Cache Strategy**:
```mermaid
flowchart LR
    A[User Request] --> B{Cache Check}
    B -->|Hit| C[Return Cached Data<br/><100ms]
    B -->|Miss| D[Execute Query]
    D --> E[Cache Result]
    E --> F[Return Fresh Data<br/>1-10s]
    
    style C fill:#4CAF50,color:#fff
    style F fill:#FFA500
```

### Async Queries

Enable async query execution for long-running queries:

```python
# superset_config.py

# Enable async queries
FEATURE_FLAGS = {
    'GLOBAL_ASYNC_QUERIES': True,
}

# Configure Celery workers
from celery.schedules import crontab

class CeleryConfig:
    broker_url = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        'cache-warmup': {
            'task': 'cache-warmup',
            'schedule': crontab(minute=0, hour='*'),
        },
    }

CELERY_CONFIG = CeleryConfig
```

### Database Query Optimization

```sql
-- Bad: Full table scan
SELECT * FROM fct_orders
WHERE order_date >= '2025-01-01';

-- Good: Use partitioning and column pruning
SELECT 
    order_id,
    customer_id,
    total_amount
FROM fct_orders
WHERE order_date >= '2025-01-01'  -- Partition pruning
  AND status = 'COMPLETED';        -- Index usage
```

### Dashboard Load Optimization

```yaml
# Dashboard optimization settings
Caching:
  Cache Timeout: 3600  # 1 hour
  
Queries:
  Row Limit: 10000  # Limit result size
  Force Async: true  # Run in background
  
Rendering:
  Lazy Load: true  # Load charts on scroll
  Progressive Rendering: true
```

### Monitoring Performance

```sql
-- Query performance monitoring
SELECT 
    user_id,
    database_name,
    sql,
    start_time,
    end_time,
    DATEDIFF('second', start_time, end_time) AS duration_seconds,
    rows_returned
FROM query_history
WHERE start_time >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY duration_seconds DESC
LIMIT 20;
```

---

## Embedding and Sharing

### Public Dashboards

Make dashboards accessible without login:

```
Dashboard → Edit → Settings → Published
```

**Public URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Iframe Embedding

Embed dashboards in external applications:

```html
<!-- Embed Superset dashboard -->
<iframe 
  src="https://superset.company.com/dashboard/1/?standalone=1"
  width="100%" 
  height="800"
  frameborder="0"
  allowfullscreen
></iframe>
```

**Embed Parameters**:
- `standalone=1` - Hide navigation
- `show_filters=0` - Hide filter panel
- `show_title=0` - Hide dashboard title

### Guest Token Authentication

Programmatic access for embedded dashboards:

```python
# Generate guest token
import requests
import json

url = 'https://superset.company.com/api/v1/security/guest_token/'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

payload = {
    "user": {
        "username": "guest_user",
        "first_name": "Guest",
        "last_name": "User"
    },
    "resources": [{
        "type": "dashboard",
        "id": "dashboard-id"
    }],
    "rls": [{
        "clause": "region = 'US-West'"
    }]
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
guest_token = response.json()['token']

# Use guest token in embed URL
embed_url = f"https://superset.company.com/dashboard/1/?guest_token={guest_token}"
```

### Export Dashboards

```bash
# Export dashboard as JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Import dashboard
superset import-dashboards -f dashboard_export.json
```

---

## Best Practices

### Dashboard Design

1. **Layout Hierarchy**
   ```
   Top: Key Metrics (Big Numbers)
   Middle: Trends (Line/Area Charts)
   Bottom: Details (Tables, Breakdowns)
   ```

2. **Color Consistency**
   - Use consistent color scheme across dashboards
   - Green for positive metrics, red for negative
   - Brand colors for categories

3. **Performance**
   - Limit charts per dashboard (< 15)
   - Use appropriate aggregation levels
   - Enable caching for static data
   - Set reasonable row limits

4. **Interactivity**
   - Add meaningful filters
   - Enable cross-filtering for exploration
   - Provide drill-down capabilities

### Chart Selection

| Data Type | Recommended Charts | Avoid |
|-----------|-------------------|-------|
| **Time Series** | Line, Area | Pie, Donut |
| **Comparison** | Bar, Column | Line (for few data points) |
| **Part-to-Whole** | Pie, Donut, Treemap | Bar (too many categories) |
| **Distribution** | Histogram, Box Plot | Pie |
| **Correlation** | Scatter, Bubble | Bar |
| **Geographic** | Map, Choropleth | Table |

### Query Optimization

```sql
-- Use aggregation in database, not in Superset
SELECT 
    DATE_TRUNC('day', order_date) AS day,
    SUM(total_amount) AS revenue
FROM fct_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '90' DAY
GROUP BY DATE_TRUNC('day', order_date);

-- Better than:
-- SELECT order_date, total_amount FROM fct_orders;
-- (then aggregate in Superset)
```

### Security

1. **Access Control**
   - Use RBAC for user management
   - Implement RLS for data isolation
   - Restrict database connections by role

2. **Data Governance**
   - Document dataset ownership
   - Set data refresh schedules
   - Monitor query performance

3. **Compliance**
   - Mask PII in visualizations
   - Audit dashboard access
   - Implement data retention policies

---

## Summary

This comprehensive Superset guide covered:

- **Setup**: Installation, configuration, database connections
- **Charts**: 50+ chart types, configuration, SQL generation
- **Dashboards**: Layout design, filters, cross-filtering
- **Advanced Features**: SQL Lab, Jinja templates, alerts, custom plugins
- **Security**: RBAC, RLS, database connection security
- **Performance**: Caching, async queries, query optimization
- **Embedding**: Public dashboards, iframe embedding, guest tokens
- **Best Practices**: Design principles, chart selection, security

Key takeaways:
- Superset connects to Dremio for high-performance analytics
- Rich visualization library supports diverse use cases
- Built-in caching and async queries ensure fast dashboards
- RBAC and RLS enable secure self-service analytics
- Embedding capabilities allow integration with external apps

**Related Documentation:**
- [Dremio Setup Guide](./dremio-setup.md)
- [Architecture: Data Flow](../architecture/data-flow.md)
- [First Steps Tutorial](../getting-started/first-steps.md)
- [Data Quality Guide](./data-quality.md)

---

**Version**: 3.2.0  
**Last Updated**: October 16, 2025
