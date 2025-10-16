# Visuele Gids voor Dremio-Poorten

**Versie**: 3.2.5  
**Laatste update**: 16 oktober 2025  
**Taal**: Nederlands

---

## Overzicht van de 3 Dremio-Poorten

```mermaid
graph TB
    subgraph "Poort 9047 - REST API"
        direction TB
        A1[🌐 Web UI Interface]
        A2[🔧 Beheer]
        A3[📊 Monitoring]
        A4[🔐 Authenticatie]
    end
    
    subgraph "Poort 31010 - PostgreSQL Proxy"
        direction TB
        B1[💼 Legacy BI Tools]
        B2[🔌 Standaard JDBC/ODBC]
        B3[🐘 PostgreSQL Compatibiliteit]
        B4[🔄 Gemakkelijke Migratie]
    end
    
    subgraph "Poort 32010 - Arrow Flight"
        direction TB
        C1[⚡ Maximale Prestaties]
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

## Gedetailleerde PostgreSQL Proxy Architectuur

### Client → Dremio Verbindingsstroom

```mermaid
graph LR
    subgraph "Clientapplicaties"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "PostgreSQL Wire Protocol"
        P[Poort 31010<br/>PostgreSQL Proxy]
    end
    
    subgraph "Dremio Engine"
        direction TB
        M1[SQL Parser]
        M2[Optimizer]
        M3[Executor]
    end
    
    subgraph "Gegevensbronnen"
        direction TB
        S1[📦 Parquet Bestanden<br/>MinIO S3]
        S2[💾 PostgreSQL Tabellen]
        S3[🔍 Elasticsearch Indices]
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

## Prestatievergelijking

### Benchmark: 100 GB Datascan

```mermaid
gantt
    title Uitvoeringstijd per Protocol (seconden)
    dateFormat X
    axisFormat %s seconden
    
    section REST API :9047
    100 GB overdracht     :0, 180
    
    section PostgreSQL :31010
    100 GB overdracht     :0, 90
    
    section Arrow Flight :32010
    100 GB overdracht     :0, 5
```

### Data Doorvoer

```mermaid
graph LR
    subgraph "Netwerkprestaties per Protocol"
        A["Poort 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ Standaard"]
        B["Poort 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ Goed"]
        C["Poort 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ Uitstekend"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### Eenvoudige Query Latentie

| Protocol | Poort | Gemiddelde Latentie | Netwerkoverhead |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON (uitgebreid) |
| **PostgreSQL Proxy** | 31010 | 20-50 ms | Wire Protocol (compact) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (binair kolomsgewijs) |

---

## Gebruikscases per Poort

### Poort 9047 - REST API

```mermaid
graph TB
    A[Poort 9047<br/>REST API]
    
    A --> B1[🌐 Webbrowser Interface]
    A --> B2[🔧 Serviceconfiguratie]
    A --> B3[👤 Gebruikersbeheer]
    A --> B4[📊 Monitoring Dashboard]
    A --> B5[🔐 OAuth/SAML Login]
    
    B1 --> C1[Maak Space/Mappen]
    B1 --> C2[Definieer VDS]
    B1 --> C3[Verken Datasets]
    
    B2 --> C4[Voeg Bronnen Toe]
    B2 --> C5[Configureer Reflections]
    B2 --> C6[Systeemconfiguratie]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### Poort 31010 - PostgreSQL Proxy

```mermaid
graph TB
    A[Poort 31010<br/>PostgreSQL Proxy]
    
    A --> B1[💼 Legacy BI Tools]
    A --> B2[🔄 PostgreSQL Migratie]
    A --> B3[🔌 Standaard Drivers]
    
    B1 --> C1[Tableau Desktop<br/>Zonder Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[Bestaande JDBC Code<br/>Geen Wijzigingen]
    B2 --> D2[psql Scripts<br/>100% Compatibel]
    B2 --> D3[Python Apps<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[Systeem Native Drivers]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### Poort 32010 - Arrow Flight

```mermaid
graph TB
    A[Poort 32010<br/>Arrow Flight]
    
    A --> B1[⚡ Maximale Prestaties]
    A --> B2[🎯 Moderne Tools]
    A --> B3[🐍 Python Ecosysteem]
    
    B1 --> C1[TB/PB Scans]
    B1 --> C2[Grote Aggregaties]
    B1 --> C3[Zero-Copy Overdracht]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[pyarrow Bibliotheek]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Polars Integratie]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## Beslissingsboom: Welke Poort Gebruiken?

```mermaid
graph TB
    Start[Ik moet verbinden met Dremio]
    
    Start --> Q1{Type applicatie?}
    
    Q1 -->|Webinterface<br/>Beheer| Port9047[✅ Poort 9047<br/>REST API]
    
    Q1 -->|BI tool/SQL Client| Q2{Arrow Flight ondersteuning?}
    
    Q2 -->|Nee<br/>Legacy tool| Port31010[✅ Poort 31010<br/>PostgreSQL Proxy]
    Q2 -->|Ja<br/>Moderne tool| Q3{Prestaties belangrijk?}
    
    Q3 -->|Ja<br/>Productie| Port32010[✅ Poort 32010<br/>Arrow Flight]
    Q3 -->|Nee<br/>Dev/Test| Port31010b[⚠️ Poort 31010<br/>Gemakkelijker]
    
    Q1 -->|Aangepaste Applicatie| Q4{Programmeertaal?}
    
    Q4 -->|Python/Java| Q5{Prestaties belangrijk?}
    Q5 -->|Ja| Port32010b[✅ Poort 32010<br/>Arrow Flight]
    Q5 -->|Nee| Port31010c[✅ Poort 31010<br/>JDBC/psycopg2]
    
    Q4 -->|Overig<br/>Go/Rust/.NET| Port31010d[✅ Poort 31010<br/>PostgreSQL Wire]
    
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

## PostgreSQL Proxy Verbindingsvoorbeelden

### 1. psql CLI

```bash
# Eenvoudige verbinding
psql -h localhost -p 31010 -U admin -d datalake

# Directe query
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# Interactieve modus
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

### 2. DBeaver Configuratie

```yaml
Verbindingstype: PostgreSQL
Verbindingsnaam: Dremio via PostgreSQL Proxy

Hoofd:
  Host: localhost
  Poort: 31010
  Database: datalake
  Gebruiker: admin
  Wachtwoord: [your-password]
  
Driver Eigenschappen:
  ssl: false
  
Geavanceerd:
  Verbinding timeout: 30000
  Query timeout: 0
```

### 3. Python met psycopg2

```python
import psycopg2
from psycopg2 import sql

# Verbinding
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# Cursor
cursor = conn.cursor()

# Eenvoudige query
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Geparameteriseerde query
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# Sluiten
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

### 5. ODBC Verbindingsstring (DSN)

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

## Docker Compose Configuratie

### Dremio Poortmapping

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # Poort 9047 - REST API / Web UI
      - "9047:9047"
      
      # Poort 31010 - PostgreSQL Proxy (ODBC/JDBC)
      - "31010:31010"
      
      # Poort 32010 - Arrow Flight (Prestaties)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### Poortvalidatie

```bash
# Controleer of alle drie poorten open zijn
netstat -an | grep -E '9047|31010|32010'

# Test REST API
curl -v http://localhost:9047

# Test PostgreSQL Proxy
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Test Arrow Flight (met Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## Snelle Visuele Samenvatting

### 3 Poorten in één Oogopslag

| Poort | Protocol | Hoofdgebruik | Prestaties | Compatibiliteit |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, Admin | ⭐⭐ Standaard | ⭐⭐⭐ Universeel |
| **31010** | PostgreSQL Wire | 💼 BI Tools, Migratie | ⭐⭐⭐ Goed | ⭐⭐⭐ Uitstekend |
| **32010** | Arrow Flight | ⚡ Productie, dbt, Superset | ⭐⭐⭐⭐⭐ Maximaal | ⭐⭐ Beperkt |

### Selectiematrix

```mermaid
graph TB
    subgraph "Selectiegids"
        A["🎯 Gebruikscase"]
        
        A --> B1["Webinterface<br/>Configuratie"]
        A --> B2["Legacy BI Tool<br/>Geen Arrow Flight"]
        A --> B3["PostgreSQL Migratie<br/>Bestaande JDBC Code"]
        A --> B4["dbt, Superset<br/>Productie"]
        A --> B5["Python pyarrow<br/>Analytics"]
        
        B1 --> C1["Poort 9047<br/>REST API"]
        B2 --> C2["Poort 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["Poort 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## Aanvullende Bronnen

### Gerelateerde Documentatie

- [Architectuur - Componenten](./components.md) - Sectie "PostgreSQL Proxy voor Dremio"
- [Gids - Dremio Setup](../guides/dremio-setup.md) - Sectie "Verbinding via PostgreSQL Proxy"
- [Configuratie - Dremio](../getting-started/configuration.md) - `dremio.conf` configuratie

### Officiële Links

- **Dremio Documentatie**: https://docs.dremio.com/
- **PostgreSQL Wire Protocol**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Versie**: 3.2.5  
**Laatste update**: 16 oktober 2025  
**Status**: ✅ Voltooid
