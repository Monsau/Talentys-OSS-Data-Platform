# Visual Guide to Dremio Ports

**Version**: 3.2.5  
**Last Updated**: October 16, 2025  
**Language**: English

---

## Overview of 3 Dremio Ports

```mermaid
graph TB
    subgraph "Port 9047 - REST API"
        direction TB
        A1[🌐 Web UI Interface]
        A2[🔧 Administration]
        A3[📊 Monitoring]
        A4[🔐 Authentication]
    end
    
    subgraph "Port 31010 - PostgreSQL Proxy"
        direction TB
        B1[💼 Legacy BI Tools]
        B2[🔌 Standard JDBC/ODBC]
        B3[🐘 PostgreSQL Compatibility]
        B4[🔄 Easy Migration]
    end
    
    subgraph "Port 32010 - Arrow Flight"
        direction TB
        C1[⚡ Maximum Performance]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Dremio Coordinator<br/>Dremio 26.0 OSS]
    
    A1 & A2 & A3 & A4 --> D
    B1 & B2 & B3 & B4 --> D
    C1 & C2 & C3 & C4 --> D
    
    E1[(MinIO S3)]
    E2[(PostgreSQL)]
    E3[(Elasticsearch)]
    
    D --> E1 & E2 & E3
    
    style D fill:#FDB515,color:#000,stroke:#000,stroke-width:3px
    style A1 fill:#4CAF50,color:#fff
    style A2 fill:#4CAF50,color:#fff
    style A3 fill:#4CAF50,color:#fff
    style A4 fill:#4CAF50,color:#fff
    style B1 fill:#336791,color:#fff
    style B2 fill:#336791,color:#fff
    style B3 fill:#336791,color:#fff
    style B4 fill:#336791,color:#fff
    style C1 fill:#FF5722,color:#fff
    style C2 fill:#FF5722,color:#fff
    style C3 fill:#FF5722,color:#fff
    style C4 fill:#FF5722,color:#fff
```

---

## Detailed PostgreSQL Proxy Architecture

### Client → Dremio Connection Flow

```mermaid
graph LR
    subgraph "Client Applications"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "PostgreSQL Wire Protocol"
        P[Port 31010<br/>PostgreSQL Proxy]
    end
    
    subgraph "Dremio Engine"
        direction TB
        M1[SQL Parser]
        M2[Optimizer]
        M3[Executor]
    end
    
    subgraph "Data Sources"
        direction TB
        S1[📦 Parquet Files<br/>MinIO S3]
        S2[💾 PostgreSQL Tables]
        S3[🔍 Elasticsearch Index]
    end
    
    A1 & A2 & A3 --> P
    A4 & A5 & A6 --> P
    
    P --> M1
    M1 --> M2
    M2 --> M3
    
    M3 --> S1 & S2 & S3
    
    style P fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style M1 fill:#FDB515,color:#000
    style M2 fill:#FDB515,color:#000
    style M3 fill:#FDB515,color:#000
```

---

## Performance Comparison

### Benchmark: 100 GB Data Scan

```mermaid
gantt
    title Execution Time by Protocol (seconds)
    dateFormat X
    axisFormat %s sec
    
    section REST API :9047
    Transfer 100 GB     :0, 180
    
    section PostgreSQL :31010
    Transfer 100 GB     :0, 90
    
    section Arrow Flight :32010
    Transfer 100 GB     :0, 5
```

### Data Throughput

```mermaid
graph LR
    subgraph "Network Throughput by Protocol"
        A["Port 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ Standard"]
        B["Port 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ Good"]
        C["Port 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ Excellent"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### Simple Query Latency

| Protocol | Port | Average Latency | Network Overhead |
|----------|------|-----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON (verbose) |
| **PostgreSQL Proxy** | 31010 | 20-50 ms | Wire Protocol (compact) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (columnar binary) |

---

## Use Cases by Port

### Port 9047 - REST API

```mermaid
graph TB
    A[Port 9047<br/>REST API]
    
    A --> B1[🌐 Web Browser Interface]
    A --> B2[🔧 Service Configuration]
    A --> B3[👤 User Management]
    A --> B4[📊 Monitoring Dashboards]
    A --> B5[🔐 OAuth/SAML Login]
    
    B1 --> C1[Create Spaces/Folders]
    B1 --> C2[Define VDS]
    B1 --> C3[Explore Datasets]
    
    B2 --> C4[Add Sources]
    B2 --> C5[Configure Reflections]
    B2 --> C6[System Settings]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### Port 31010 - PostgreSQL Proxy

```mermaid
graph TB
    A[Port 31010<br/>PostgreSQL Proxy]
    
    A --> B1[💼 Legacy BI Tools]
    A --> B2[🔄 PostgreSQL Migration]
    A --> B3[🔌 Standard Drivers]
    
    B1 --> C1[Tableau Desktop<br/>without Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>PostgreSQL JDBC]
    
    B2 --> D1[Existing JDBC Code<br/>no modifications]
    B2 --> D2[psql Scripts<br/>100% compatible]
    B2 --> D3[Python Apps<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[Native OS Drivers]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### Port 32010 - Arrow Flight

```mermaid
graph TB
    A[Port 32010<br/>Arrow Flight]
    
    A --> B1[⚡ Maximum Performance]
    A --> B2[🎯 Modern Tools]
    A --> B3[🐍 Python Ecosystem]
    
    B1 --> C1[TB/PB Scans]
    B1 --> C2[Massive Aggregations]
    B1 --> C3[Zero-Copy Transfers]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[pyarrow Library]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Polars Integration]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## Decision Tree: Which Port to Use?

```mermaid
graph TB
    Start[Need to Connect to Dremio]
    
    Start --> Q1{Application Type?}
    
    Q1 -->|Web Interface<br/>Administration| Port9047[✅ Port 9047<br/>REST API]
    
    Q1 -->|BI Tool/SQL Client| Q2{Supports Arrow Flight?}
    
    Q2 -->|No<br/>Legacy Tool| Port31010[✅ Port 31010<br/>PostgreSQL Proxy]
    Q2 -->|Yes<br/>Modern Tool| Q3{Performance Critical?}
    
    Q3 -->|Yes<br/>Production| Port32010[✅ Port 32010<br/>Arrow Flight]
    Q3 -->|No<br/>Dev/Test| Port31010b[⚠️ Port 31010<br/>Easier]
    
    Q1 -->|Custom Application| Q4{Language?}
    
    Q4 -->|Python/Java| Q5{Performance Important?}
    Q5 -->|Yes| Port32010b[✅ Port 32010<br/>Arrow Flight]
    Q5 -->|No| Port31010c[✅ Port 31010<br/>JDBC/psycopg2]
    
    Q4 -->|Other<br/>Go/Rust/.NET| Port31010d[✅ Port 31010<br/>PostgreSQL Wire]
    
    style Start fill:#2196F3,color:#fff
    style Port9047 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style Port31010 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010b fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010c fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010d fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port32010 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
    style Port32010b fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## PostgreSQL Proxy Connection Examples

### 1. psql CLI

```bash
# Simple connection
psql -h localhost -p 31010 -U admin -d datalake

# Direct query
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# Interactive mode
$ psql -h localhost -p 31010 -U admin -d datalake
Password for user admin: ****
psql (16.0, server 26.0)
Type "help" for help.

datalake=> \dt
           List of relations
 Schema |   Name    | Type  | Owner 
--------+-----------+-------+-------
 public | customers | table | admin
 public | orders    | table | admin
(2 rows)

datalake=> SELECT customer_id, name, state FROM customers LIMIT 5;
```

### 2. DBeaver Configuration

```yaml
Connection Type: PostgreSQL
Connection Name: Dremio via PostgreSQL Proxy

Main:
  Host: localhost
  Port: 31010
  Database: datalake
  Username: admin
  Password: [your-password]
  
Driver Properties:
  ssl: false
  
Advanced:
  Connection timeout: 30000
  Query timeout: 0
```

### 3. Python with psycopg2

```python
import psycopg2
from psycopg2 import sql

# Connection
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# Cursor
cursor = conn.cursor()

# Simple query
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Parameterized query
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# Close
cursor.close()
conn.close()
```

### 4. Java JDBC

```java
import java.sql.*;

public class DremioPostgreSQLProxy {
    public static void main(String[] args) {
        String url = "jdbc:postgresql://localhost:31010/datalake";
        String user = "admin";
        String password = "your-password";
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(
                "SELECT customer_id, name, state FROM MinIO.datalake.customers LIMIT 10"
            );
            
            while (rs.next()) {
                int id = rs.getInt("customer_id");
                String name = rs.getString("name");
                String state = rs.getString("state");
                System.out.printf("ID: %d, Name: %s, State: %s%n", id, name, state);
            }
            
            rs.close();
            stmt.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### 5. ODBC Connection String (DSN)

```ini
[ODBC Data Sources]
Dremio_PostgreSQL=PostgreSQL Unicode Driver

[Dremio_PostgreSQL]
Driver=PostgreSQL Unicode
Description=Dremio via PostgreSQL Proxy
Server=localhost
Port=31010
Database=datalake
Username=admin
Password=your-password
SSLMode=disable
Protocol=7.4
```

---

## Docker Compose Configuration

### Dremio Port Mapping

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # Port 9047 - REST API / Web UI
      - "9047:9047"
      
      # Port 31010 - PostgreSQL Proxy (ODBC/JDBC)
      - "31010:31010"
      
      # Port 32010 - Arrow Flight (Performance)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### Port Verification

```bash
# Check all 3 ports are open
netstat -an | grep -E '9047|31010|32010'

# Test REST API
curl -v http://localhost:9047

# Test PostgreSQL Proxy
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Test Arrow Flight (with Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## Quick Visual Summary

### 3 Ports at a Glance

| Port | Protocol | Primary Use | Performance | Compatibility |
|------|----------|-------------|-------------|---------------|
| **9047** | REST API | 🌐 Web UI, Admin | ⭐⭐ Standard | ⭐⭐⭐ Universal |
| **31010** | PostgreSQL Wire | 💼 BI Tools, Migration | ⭐⭐⭐ Good | ⭐⭐⭐ Excellent |
| **32010** | Arrow Flight | ⚡ Production, dbt, Superset | ⭐⭐⭐⭐⭐ Maximum | ⭐⭐ Limited |

### Selection Matrix

```mermaid
graph TB
    subgraph "Selection Guide"
        A["🎯 Use Case"]
        
        A --> B1["Web Interface<br/>Configuration"]
        A --> B2["Legacy BI Tool<br/>No Arrow Flight"]
        A --> B3["PostgreSQL Migration<br/>Existing JDBC Code"]
        A --> B4["dbt, Superset<br/>Production"]
        A --> B5["Python pyarrow<br/>Analytics"]
        
        B1 --> C1["Port 9047<br/>REST API"]
        B2 --> C2["Port 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["Port 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## Additional Resources

### Related Documentation

- [Architecture - Components](./components.md) - "PostgreSQL Proxy for Dremio" section
- [Guide - Dremio Setup](../guides/dremio-setup.md) - "Connection via PostgreSQL Proxy" section
- [Configuration - Dremio](../getting-started/configuration.md) - `dremio.conf` settings

### Official Links

- **Dremio Documentation**: https://docs.dremio.com/
- **PostgreSQL Wire Protocol**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Version**: 3.2.5  
**Last Updated**: October 16, 2025  
**Status**: ✅ Complete
