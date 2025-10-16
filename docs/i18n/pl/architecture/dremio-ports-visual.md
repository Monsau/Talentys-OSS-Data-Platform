# Wizualny Przewodnik po Portach Dremio

**Wersja**: 3.2.5  
**Ostatnia aktualizacja**: 16 października 2025  
**Język**: Polski

---

## Przegląd 3 Portów Dremio

```mermaid
graph TB
    subgraph "Port 9047 - REST API"
        direction TB
        A1[🌐 Interfejs Web UI]
        A2[🔧 Administracja]
        A3[📊 Monitorowanie]
        A4[🔐 Uwierzytelnianie]
    end
    
    subgraph "Port 31010 - PostgreSQL Proxy"
        direction TB
        B1[💼 Starsze Narzędzia BI]
        B2[🔌 Standardowe JDBC/ODBC]
        B3[🐘 Kompatybilność PostgreSQL]
        B4[🔄 Łatwa Migracja]
    end
    
    subgraph "Port 32010 - Arrow Flight"
        direction TB
        C1[⚡ Maksymalna Wydajność]
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

## Szczegółowa Architektura PostgreSQL Proxy

### Przepływ Połączenia Klient → Dremio

```mermaid
graph LR
    subgraph "Aplikacje Klienckie"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "Protokół PostgreSQL Wire"
        P[Port 31010<br/>PostgreSQL Proxy]
    end
    
    subgraph "Silnik Dremio"
        direction TB
        M1[SQL Parser]
        M2[Optimizer]
        M3[Executor]
    end
    
    subgraph "Źródła Danych"
        direction TB
        S1[📦 Pliki Parquet<br/>MinIO S3]
        S2[💾 Tabele PostgreSQL]
        S3[🔍 Indeksy Elasticsearch]
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

## Porównanie Wydajności

### Benchmark: Skanowanie 100 GB Danych

```mermaid
gantt
    title Czas Wykonania według Protokołu (sekundy)
    dateFormat X
    axisFormat %s sekund
    
    section REST API :9047
    Transfer 100 GB     :0, 180
    
    section PostgreSQL :31010
    Transfer 100 GB     :0, 90
    
    section Arrow Flight :32010
    Transfer 100 GB     :0, 5
```

### Przepustowość Danych

```mermaid
graph LR
    subgraph "Wydajność Sieciowa według Protokołu"
        A["Port 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ Standardowa"]
        B["Port 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ Dobra"]
        C["Port 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ Doskonała"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### Opóźnienie Prostych Zapytań

| Protokół | Port | Średnie Opóźnienie | Narzut Sieciowy |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON (rozbudowany) |
| **PostgreSQL Proxy** | 31010 | 20-50 ms | Wire Protocol (kompaktowy) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (binarny kolumnowy) |

---

## Przypadki Użycia według Portu

### Port 9047 - REST API

```mermaid
graph TB
    A[Port 9047<br/>REST API]
    
    A --> B1[🌐 Interfejs Przeglądarki]
    A --> B2[🔧 Konfiguracja Usług]
    A --> B3[👤 Zarządzanie Użytkownikami]
    A --> B4[📊 Panel Monitorowania]
    A --> B5[🔐 Login OAuth/SAML]
    
    B1 --> C1[Tworzenie Space/Folderów]
    B1 --> C2[Definicja VDS]
    B1 --> C3[Eksploracja Zbiorów Danych]
    
    B2 --> C4[Dodawanie Źródeł]
    B2 --> C5[Konfiguracja Reflections]
    B2 --> C6[Konfiguracja Systemu]
    
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
    
    A --> B1[💼 Starsze Narzędzia BI]
    A --> B2[🔄 Migracja PostgreSQL]
    A --> B3[🔌 Standardowe Sterowniki]
    
    B1 --> C1[Tableau Desktop<br/>Bez Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[Istniejący Kod JDBC<br/>Bez Modyfikacji]
    B2 --> D2[Skrypty psql<br/>100% Kompatybilne]
    B2 --> D3[Aplikacje Python<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[Natywne Sterowniki SO]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### Port 32010 - Arrow Flight

```mermaid
graph TB
    A[Port 32010<br/>Arrow Flight]
    
    A --> B1[⚡ Maksymalna Wydajność]
    A --> B2[🎯 Nowoczesne Narzędzia]
    A --> B3[🐍 Ekosystem Python]
    
    B1 --> C1[Skanowanie TB/PB]
    B1 --> C2[Duże Agregacje]
    B1 --> C3[Transfer Zero-Copy]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Konfiguracja Bazy]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[Biblioteka pyarrow]
    B3 --> E2[pandas przez Arrow]
    B3 --> E3[Integracja Polars]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## Drzewo Decyzyjne: Którego Portu Użyć?

```mermaid
graph TB
    Start[Muszę połączyć się z Dremio]
    
    Start --> Q1{Typ aplikacji?}
    
    Q1 -->|Interfejs webowy<br/>Administracja| Port9047[✅ Port 9047<br/>REST API]
    
    Q1 -->|Narzędzie BI/Klient SQL| Q2{Wsparcie Arrow Flight?}
    
    Q2 -->|Nie<br/>Starsze narzędzie| Port31010[✅ Port 31010<br/>PostgreSQL Proxy]
    Q2 -->|Tak<br/>Nowoczesne narzędzie| Q3{Wydajność ważna?}
    
    Q3 -->|Tak<br/>Produkcja| Port32010[✅ Port 32010<br/>Arrow Flight]
    Q3 -->|Nie<br/>Dev/Test| Port31010b[⚠️ Port 31010<br/>Łatwiejszy]
    
    Q1 -->|Aplikacja Niestandardowa| Q4{Język programowania?}
    
    Q4 -->|Python/Java| Q5{Wydajność ważna?}
    Q5 -->|Tak| Port32010b[✅ Port 32010<br/>Arrow Flight]
    Q5 -->|Nie| Port31010c[✅ Port 31010<br/>JDBC/psycopg2]
    
    Q4 -->|Inne<br/>Go/Rust/.NET| Port31010d[✅ Port 31010<br/>PostgreSQL Wire]
    
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

## Przykłady Połączenia PostgreSQL Proxy

### 1. psql CLI

```bash
# Proste połączenie
psql -h localhost -p 31010 -U admin -d datalake

# Bezpośrednie zapytanie
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# Tryb interaktywny
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

### 2. Konfiguracja DBeaver

```yaml
Typ Połączenia: PostgreSQL
Nazwa Połączenia: Dremio via PostgreSQL Proxy

Główne:
  Host: localhost
  Port: 31010
  Baza danych: datalake
  Użytkownik: admin
  Hasło: [your-password]
  
Właściwości Sterownika:
  ssl: false
  
Zaawansowane:
  Limit czasu połączenia: 30000
  Limit czasu zapytania: 0
```

### 3. Python z psycopg2

```python
import psycopg2
from psycopg2 import sql

# Połączenie
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# Kursor
cursor = conn.cursor()

# Proste zapytanie
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Zapytanie parametryzowane
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# Zamknij
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

### 5. Ciąg Połączenia ODBC (DSN)

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

## Konfiguracja Docker Compose

### Mapowanie Portów Dremio

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
      
      # Port 32010 - Arrow Flight (Wydajność)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### Walidacja Portów

```bash
# Sprawdź czy wszystkie trzy porty są otwarte
netstat -an | grep -E '9047|31010|32010'

# Test REST API
curl -v http://localhost:9047

# Test PostgreSQL Proxy
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Test Arrow Flight (z Pythonem)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## Szybkie Podsumowanie Wizualne

### 3 Porty na Jeden Rzut Oka

| Port | Protokół | Główne Użycie | Wydajność | Kompatybilność |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, Admin | ⭐⭐ Standardowa | ⭐⭐⭐ Uniwersalna |
| **31010** | PostgreSQL Wire | 💼 Narzędzia BI, Migracja | ⭐⭐⭐ Dobra | ⭐⭐⭐ Doskonała |
| **32010** | Arrow Flight | ⚡ Produkcja, dbt, Superset | ⭐⭐⭐⭐⭐ Maksymalna | ⭐⭐ Ograniczona |

### Macierz Wyboru

```mermaid
graph TB
    subgraph "Przewodnik Wyboru"
        A["🎯 Przypadek Użycia"]
        
        A --> B1["Interfejs Webowy<br/>Konfiguracja"]
        A --> B2["Starsze Narzędzie BI<br/>Bez Arrow Flight"]
        A --> B3["Migracja PostgreSQL<br/>Istniejący Kod JDBC"]
        A --> B4["dbt, Superset<br/>Produkcja"]
        A --> B5["Python pyarrow<br/>Analityka"]
        
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

## Dodatkowe Zasoby

### Powiązana Dokumentacja

- [Architektura - Komponenty](./components.md) - Sekcja "PostgreSQL Proxy dla Dremio"
- [Przewodnik - Konfiguracja Dremio](../guides/dremio-setup.md) - Sekcja "Połączenie przez PostgreSQL Proxy"
- [Konfiguracja - Dremio](../getting-started/configuration.md) - Konfiguracja `dremio.conf`

### Oficjalne Linki

- **Dokumentacja Dremio**: https://docs.dremio.com/
- **Protokół PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Wersja**: 3.2.5  
**Ostatnia aktualizacja**: 16 października 2025  
**Status**: ✅ Ukończone
