# Riferimento API Dremio

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 16 ottobre 2025  
**Lingua**: francese

## Sommario

1. [Panoramica](#panoramica)
2. [Autenticazione](#autenticazione)
3. [API REST](#api-rest)
4. [SQL di volo della freccia](#arrow-flight-sql)
5. [ODBC/JDBC](#odbcjdbc)
6. [Client Python](#client-python)
7. [Client Java](#client-java)
8. [Esempi API](#dapi-esempi)

---

## Panoramica

Dremio fornisce diverse API per interagire con la data Lakehouse:

| Tipo API | Casi d'uso | Porto | Protocollo |
|------------|--------|------|----------|
| API REST | Gestione, metadati | 9047| HTTP/HTTPS |
| ArrowFlightSQL | Query ad alte prestazioni | 32010| gRPC |
| ODBC | Connettività dello strumento BI | 31010| ODBC |
| JDBC | Applicazioni Java | 31010| JDBC |

### Architettura dell'API

```mermaid
graph TB
    subgraph "APIs Dremio"
        REST[REST API<br/>:9047]
        FLIGHT[Arrow Flight SQL<br/>:32010]
        ODBC[Driver ODBC<br/>:31010]
        JDBC[Driver JDBC<br/>:31010]
    end
    
    subgraph "Clients"
        BI[Outils BI]
        PY[Apps Python]
        JAVA[Apps Java]
        WEB[Apps Web]
    end
    
    BI --> ODBC
    BI --> JDBC
    PY --> FLIGHT
    PY --> REST
    JAVA --> JDBC
    JAVA --> FLIGHT
    WEB --> REST
    
    REST --> DREMIO[Moteur Dremio]
    FLIGHT --> DREMIO
    ODBC --> DREMIO
    JDBC --> DREMIO
    
    style REST fill:#4CAF50
    style FLIGHT fill:#2196F3
    style ODBC fill:#FF9800
    style JDBC fill:#9C27B0
```

---

## Autenticazione

### Genera un token di autenticazione

**Endpoint**: `POST /apiv2/login`

**Richiesta** :
```bash
curl -X POST http://localhost:9047/apiv2/login \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "admin",
    "password": "your_password"
  }'
```

**Risposta** :
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userName": "admin",
  "firstName": "Admin",
  "lastName": "User",
  "expires": 1729209600000
}
```

### Usa il token nelle richieste

```bash
# Set token as variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in subsequent requests
curl -X GET http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN"
```

### Scadenza del token

Per impostazione predefinita, i token scadono dopo 24 ore. Configura in `dremio.conf`:

```conf
services.tokens.expiration: 86400000  # 24 hours in milliseconds
```

---

##API REST

### URL di base

§§§CODICE_7§§§

### Intestazioni comuni

```bash
Authorization: Bearer <token>
Content-Type: application/json
```

### Gestione del catalogo

#### Elenca gli elementi del catalogo

**Endpoint**: `GET /catalog`

```bash
curl -X GET http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN"
```

**Risposta** :
```json
{
  "data": [
    {
      "id": "dremio:/",
      "path": [],
      "tag": "root",
      "type": "CONTAINER",
      "children": [
        {
          "id": "source-id-123",
          "path": ["MinIO"],
          "tag": "source-tag-123",
          "type": "SOURCE"
        }
      ]
    }
  ]
}
```

#### Ottieni un elemento del catalogo in base al percorso

**Endpoint**: `GET /catalog/by-path/{path}`

```bash
curl -X GET "http://localhost:9047/apiv2/catalog/by-path/MinIO/bronze/customers" \
  -H "Authorization: Bearer $TOKEN"
```

**Risposta** :
```json
{
  "id": "table-id-456",
  "path": ["MinIO", "bronze", "customers"],
  "tag": "table-tag-456",
  "type": "DATASET",
  "format": {
    "type": "Parquet"
  },
  "fields": [
    {
      "name": "customer_id",
      "type": "INTEGER"
    },
    {
      "name": "name",
      "type": "VARCHAR"
    }
  ]
}
```

### Set di dati virtuali (VDS)

#### Crea un set di dati virtuale

**Endpoint**: `POST /catalog`

```bash
curl -X POST http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entityType": "dataset",
    "path": ["Production", "Dimensions", "dim_customers"],
    "type": "VIRTUAL_DATASET",
    "sql": "SELECT customer_id, name, email FROM MinIO.bronze.customers WHERE active = true",
    "sqlContext": ["MinIO"]
  }'
```

**Risposta** :
```json
{
  "id": "vds-id-789",
  "path": ["Production", "Dimensions", "dim_customers"],
  "tag": "vds-tag-789",
  "type": "VIRTUAL_DATASET"
}
```

#### Aggiorna un set di dati virtuale

**Endpoint**: `PUT /catalog/{id}`

```bash
curl -X PUT "http://localhost:9047/apiv2/catalog/vds-id-789" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": ["Production", "Dimensions", "dim_customers"],
    "type": "VIRTUAL_DATASET",
    "sql": "SELECT customer_id, UPPER(name) as name, email FROM MinIO.bronze.customers WHERE active = true",
    "tag": "vds-tag-789"
  }'
```

#### Elimina un set di dati

**Punto finale**: `DELETE /catalog/{id}?tag={tag}`

```bash
curl -X DELETE "http://localhost:9047/apiv2/catalog/vds-id-789?tag=vds-tag-789" \
  -H "Authorization: Bearer $TOKEN"
```

### Esecuzione SQL

#### Esegue una query SQL

**Punto finale**: `POST /sql`

```bash
curl -X POST http://localhost:9047/apiv2/sql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM Production.Dimensions.dim_customers LIMIT 10"
  }'
```

**Risposta** :
```json
{
  "id": "job-id-abc123",
  "state": "COMPLETED",
  "rowCount": 10,
  "rows": [
    {
      "customer_id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

### Gestione del lavoro

#### Ottieni lo stato di un lavoro

**Endpoint**: `GET /job/{jobId}`

```bash
curl -X GET "http://localhost:9047/apiv2/job/job-id-abc123" \
  -H "Authorization: Bearer $TOKEN"
```

**Risposta** :
```json
{
  "id": "job-id-abc123",
  "state": "COMPLETED",
  "user": "admin",
  "startTime": 1729108800000,
  "endTime": 1729108805000,
  "queryType": "UI_RUN",
  "sql": "SELECT * FROM ...",
  "datasetVersion": "1",
  "outputRecords": 10,
  "outputBytes": 1024,
  "accelerationDetails": {
    "accelerated": true,
    "reflectionIds": ["reflection-id-123"]
  }
}
```

#### Elenca i lavori recenti

**Endpoint**: `GET /jobs`

```bash
curl -X GET "http://localhost:9047/apiv2/jobs?limit=20&sort=startTime&order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

#### Annulla un lavoro

**Punto finale**: `POST /job/{jobId}/cancel`

```bash
curl -X POST "http://localhost:9047/apiv2/job/job-id-abc123/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

###Riflessioni

#### Elenca le riflessioni

**Punto finale**: `GET /reflections`

```bash
curl -X GET http://localhost:9047/apiv2/reflections \
  -H "Authorization: Bearer $TOKEN"
```

**Risposta** :
```json
{
  "data": [
    {
      "id": "reflection-id-123",
      "name": "raw_customers",
      "type": "RAW",
      "datasetId": "vds-id-789",
      "status": {
        "status": "ACTIVE",
        "lastRefreshTime": 1729108800000
      }
    }
  ]
}
```

#### Crea una riflessione

**Punto finale**: `POST /reflections`

```bash
curl -X POST http://localhost:9047/apiv2/reflections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "agg_daily_revenue",
    "type": "AGGREGATION",
    "datasetId": "vds-id-789",
    "dimensions": [
      {"name": "order_date"}
    ],
    "measures": [
      {"name": "amount", "measureType": ["SUM", "COUNT"]}
    ]
  }'
```

### Gestione delle fonti

#### Aggiungi una sorgente S3

**Punto finale**: `PUT /source/{name}`

```bash
curl -X PUT "http://localhost:9047/apiv2/source/MinIO" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MinIO",
    "type": "S3",
    "config": {
      "credentialType": "ACCESS_KEY",
      "accessKey": "minioadmin",
      "accessSecret": "minioadmin",
      "secure": false,
      "externalBucketList": ["datalake"],
      "enableAsync": true,
      "propertyList": [
        {
          "name": "fs.s3a.endpoint",
          "value": "minio:9000"
        },
        {
          "name": "fs.s3a.path.style.access",
          "value": "true"
        }
      ]
    }
  }'
```

#### Aggiorna i metadati di origine

**Endpoint**: `POST /source/{name}/refresh`

```bash
curl -X POST "http://localhost:9047/apiv2/source/MinIO/refresh" \
  -H "Authorization: Bearer $TOKEN"
```

---

## SQL di volo della freccia

Arrow Flight SQL fornisce un'esecuzione di query ad alte prestazioni (20-50 volte più veloce di ODBC/JDBC).

### Client Python con PyArrow

#### Facilità

```bash
pip install pyarrow
```

#### Connessione e interrogazione

```python
from pyarrow import flight
import pyarrow

# Create Flight client
location = flight.Location.for_grpc_tcp("localhost", 32010)
client = flight.FlightClient(location)

# Authenticate
token_pair = client.authenticate_basic_token(b"admin", b"password")
options = flight.FlightCallOptions(headers=[token_pair])

# Execute query
query = "SELECT * FROM Production.Dimensions.dim_customers LIMIT 10"
flight_info = client.get_flight_info(
    flight.FlightDescriptor.for_command(query.encode('utf-8')),
    options
)

# Read results
reader = client.do_get(flight_info.endpoints[0].ticket, options)
table = reader.read_all()

# Convert to pandas
df = table.to_pandas()
print(df)
```

#### Esempio: interrogazione con parametri

```python
def query_customers_by_status(status):
    """Query customers filtered by status"""
    query = f"""
        SELECT customer_id, name, email, lifetime_value
        FROM Production.Dimensions.dim_customers
        WHERE status = '{status}'
        ORDER BY lifetime_value DESC
    """
    
    flight_info = client.get_flight_info(
        flight.FlightDescriptor.for_command(query.encode('utf-8')),
        options
    )
    
    reader = client.do_get(flight_info.endpoints[0].ticket, options)
    return reader.read_all().to_pandas()

# Use function
active_customers = query_customers_by_status('active')
print(f"Found {len(active_customers)} active customers")
```

#### Elaborazione batch

```python
def process_large_query(query, batch_size=10000):
    """Process large queries in batches"""
    flight_info = client.get_flight_info(
        flight.FlightDescriptor.for_command(query.encode('utf-8')),
        options
    )
    
    reader = client.do_get(flight_info.endpoints[0].ticket, options)
    
    for batch in reader:
        # Process each batch
        df = batch.data.to_pandas()
        print(f"Processing batch of {len(df)} rows")
        
        # Your processing logic here
        process_batch(df)

# Example usage
query = "SELECT * FROM Production.Facts.fct_orders WHERE order_date >= '2025-01-01'"
process_large_query(query)
```

### Confronto delle prestazioni

```python
import time

def benchmark_query(query):
    """Compare REST API vs Arrow Flight performance"""
    
    # Test Arrow Flight
    start = time.time()
    flight_info = client.get_flight_info(
        flight.FlightDescriptor.for_command(query.encode('utf-8')),
        options
    )
    reader = client.do_get(flight_info.endpoints[0].ticket, options)
    table = reader.read_all()
    flight_time = time.time() - start
    
    print(f"Arrow Flight: {flight_time:.2f}s for {len(table)} rows")
    print(f"Throughput: {len(table) / flight_time:.0f} rows/sec")

# Test with large query
query = """
    SELECT *
    FROM Production.Facts.fct_orders
    WHERE order_date >= '2024-01-01'
"""
benchmark_query(query)

# Typical results:
# Arrow Flight: 2.5s for 1,000,000 rows (400,000 rows/sec)
# REST API: 45s for 1,000,000 rows (22,000 rows/sec)
# Speedup: 18x faster
```

---

##ODBC/JDBC

### Connessione ODBC

#### Installazione di Windows

1. **Scarica il driver ODBC**:
   ```
   https://download.dremio.com/odbc-driver/dremio-odbc-1.4.0.1041.msi
   ```

2. **Configura il DSN**:
   ```
   Host: localhost
   Port: 31010
   Authentication Type: Plain
   UID: admin
   PWD: your_password
   ```

3. **Stringa di connessione**:
   ```
   DRIVER={Dremio ODBC Driver 64-bit};
   HOST=localhost;
   PORT=31010;
   UID=admin;
   PWD=your_password;
   AuthenticationType=Plain
   ```

#### Configurazione di Linux

```bash
# Install driver
tar -xzvf dremio-odbc-1.4.0.1041-1.x86_64.tar.gz
cd dremio-odbc-1.4.0.1041

# Configure odbcinst.ini
cat >> /etc/odbcinst.ini << EOF
[Dremio ODBC Driver 64-bit]
Description=Dremio ODBC Driver 64-bit
Driver=/opt/dremio-odbc/lib64/libdrillodbc_sb64.so
EOF

# Configure odbc.ini
cat >> ~/.odbc.ini << EOF
[Dremio]
Driver=Dremio ODBC Driver 64-bit
HOST=localhost
PORT=31010
UID=admin
PWD=your_password
AuthenticationType=Plain
EOF
```

### Connessione JDBC

#### Scarica il driver

```bash
wget https://download.dremio.com/jdbc-driver/dremio-jdbc-driver-26.0.0.jar
```

#### Stringa di connessione

```java
String url = "jdbc:dremio:direct=localhost:31010";
String username = "admin";
String password = "your_password";

Connection conn = DriverManager.getConnection(url, username, password);
```

#### Proprietà

```properties
jdbc:dremio:direct=localhost:31010;
schema=Production;
authentication=PLAIN;
useEncryption=false
```

---

## Cliente Python

### Esempio completo

```python
import pyarrow.flight as flight
import pandas as pd
from typing import Optional

class DremioClient:
    """Dremio client using Arrow Flight SQL"""
    
    def __init__(self, host: str = "localhost", port: int = 32010,
                 username: str = "admin", password: str = "password"):
        """Initialize Dremio client"""
        self.location = flight.Location.for_grpc_tcp(host, port)
        self.client = flight.FlightClient(self.location)
        
        # Authenticate
        token_pair = self.client.authenticate_basic_token(
            username.encode('utf-8'),
            password.encode('utf-8')
        )
        self.options = flight.FlightCallOptions(headers=[token_pair])
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return pandas DataFrame"""
        flight_info = self.client.get_flight_info(
            flight.FlightDescriptor.for_command(sql.encode('utf-8')),
            self.options
        )
        
        reader = self.client.do_get(flight_info.endpoints[0].ticket, self.options)
        table = reader.read_all()
        
        return table.to_pandas()
    
    def query_stream(self, sql: str):
        """Execute query and yield batches"""
        flight_info = self.client.get_flight_info(
            flight.FlightDescriptor.for_command(sql.encode('utf-8')),
            self.options
        )
        
        reader = self.client.do_get(flight_info.endpoints[0].ticket, self.options)
        
        for batch in reader:
            yield batch.data.to_pandas()
    
    def execute(self, sql: str) -> bool:
        """Execute SQL command (CREATE, DROP, etc.)"""
        try:
            self.query(sql)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

# Usage example
if __name__ == "__main__":
    # Connect to Dremio
    dremio = DremioClient()
    
    # Simple query
    df = dremio.query("SELECT * FROM Production.Dimensions.dim_customers LIMIT 10")
    print(df)
    
    # Aggregation query
    revenue = dremio.query("""
        SELECT 
            DATE_TRUNC('month', order_date) as month,
            SUM(amount) as total_revenue,
            COUNT(*) as order_count
        FROM Production.Facts.fct_orders
        WHERE order_date >= '2025-01-01'
        GROUP BY 1
        ORDER BY 1
    """)
    print(revenue)
    
    # Stream large results
    for batch in dremio.query_stream("SELECT * FROM large_table"):
        print(f"Processing batch of {len(batch)} rows")
        # Process batch
```

---

##Client Java

### Dipendenza da Maven

```xml
<dependency>
    <groupId>com.dremio.distribution</groupId>
    <artifactId>dremio-jdbc-driver</artifactId>
    <version>26.0.0</version>
</dependency>
```

### Esempio completo

```java
import java.sql.*;

public class DremioJDBCExample {
    
    private static final String URL = "jdbc:dremio:direct=localhost:31010";
    private static final String USERNAME = "admin";
    private static final String PASSWORD = "your_password";
    
    public static void main(String[] args) {
        try (Connection conn = DriverManager.getConnection(URL, USERNAME, PASSWORD)) {
            
            // Simple query
            simpleQuery(conn);
            
            // Parameterized query
            parameterizedQuery(conn, "2025-01-01");
            
            // Batch insert (if writing enabled)
            // batchInsert(conn);
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    
    private static void simpleQuery(Connection conn) throws SQLException {
        String sql = "SELECT * FROM Production.Dimensions.dim_customers LIMIT 10";
        
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                int id = rs.getInt("customer_id");
                String name = rs.getString("name");
                String email = rs.getString("email");
                
                System.out.printf("Customer: %d, %s, %s%n", id, name, email);
            }
        }
    }
    
    private static void parameterizedQuery(Connection conn, String startDate) 
            throws SQLException {
        String sql = """
            SELECT 
                DATE_TRUNC('month', order_date) as month,
                SUM(amount) as total_revenue,
                COUNT(*) as order_count
            FROM Production.Facts.fct_orders
            WHERE order_date >= ?
            GROUP BY 1
            ORDER BY 1
        """;
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, startDate);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Date month = rs.getDate("month");
                    double revenue = rs.getDouble("total_revenue");
                    int orders = rs.getInt("order_count");
                    
                    System.out.printf("%s: $%.2f (%d orders)%n", 
                                    month, revenue, orders);
                }
            }
        }
    }
}
```

---

## Esempi di API

### Esempio 1: reporting automatizzato

```python
#!/usr/bin/env python3
"""
Daily sales report generation
"""
from datetime import datetime, timedelta
import pandas as pd

def generate_daily_sales_report():
    """Generate and email daily sales report"""
    dremio = DremioClient()
    
    # Query yesterday's sales
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    query = f"""
        SELECT 
            p.category,
            COUNT(DISTINCT o.customer_id) as unique_customers,
            COUNT(*) as order_count,
            SUM(o.amount) as total_revenue,
            AVG(o.amount) as avg_order_value
        FROM Production.Facts.fct_orders o
        JOIN Production.Dimensions.dim_products p ON o.product_id = p.product_id
        WHERE o.order_date = '{yesterday}'
        GROUP BY 1
        ORDER BY total_revenue DESC
    """
    
    df = dremio.query(query)
    
    # Generate report
    report = f"""
    Daily Sales Report - {yesterday}
    ================================
    
    {df.to_string(index=False)}
    
    Total Revenue: ${df['total_revenue'].sum():,.2f}
    Total Orders: {df['order_count'].sum():,}
    Unique Customers: {df['unique_customers'].sum():,}
    """
    
    print(report)
    # Send email (not shown)

if __name__ == "__main__":
    generate_daily_sales_report()
```

### Esempio 2: esportazione dei dati

```python
def export_to_csv(query: str, output_file: str):
    """Export query results to CSV"""
    dremio = DremioClient()
    
    # Stream results for large datasets
    with open(output_file, 'w') as f:
        first_batch = True
        
        for batch in dremio.query_stream(query):
            batch.to_csv(f, index=False, header=first_batch)
            first_batch = False
            
            print(f"Exported {len(batch)} rows")

# Usage
export_to_csv(
    "SELECT * FROM Production.Facts.fct_orders WHERE order_date >= '2025-01-01'",
    "orders_2025.csv"
)
```

### Esempio 3: rilevamento dei metadati

```python
import requests

def list_all_datasets(token: str):
    """List all datasets in Dremio catalog"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        "http://localhost:9047/apiv2/catalog",
        headers=headers
    )
    
    catalog = response.json()
    
    def traverse(item, path=[]):
        """Recursively traverse catalog"""
        current_path = path + [item.get('path', [''])[0]]
        
        if item.get('type') == 'DATASET':
            print(f"Dataset: {'/'.join(current_path)}")
        
        for child in item.get('children', []):
            traverse(child, current_path)
    
    traverse(catalog['data'][0])

# Usage
token = get_auth_token("admin", "password")
list_all_datasets(token)
```

---

## Riepilogo

Questo riferimento API riguardava:

- **Autenticazione**: autenticazione basata su token con API REST
- **API REST**: catalogo, esecuzione SQL, lavori, riflessioni
- **Arrow Flight SQL**: query ad alte prestazioni (20-50 volte più veloci)
- **ODBC/JDBC**: connettività dello strumento BI
- **Client Python**: implementazione completa del client
- **Client Java**: esempi JDBC
- **Esempi pratici**: Reporting, esportazione, rilevamento dei metadati

**Aspetti principali**:
- Utilizza Arrow Flight SQL per l'accesso ai dati ad alte prestazioni
- Utilizza l'API REST per la gestione e l'automazione
- Utilizzare ODBC/JDBC per l'integrazione degli strumenti BI
- Utilizza sempre i token di autenticazione
- Elabora query di grandi dimensioni in batch per prestazioni migliori

**Documentazione correlata:**
- [Guida all'installazione di Dremio](../guides/dremio-setup.md)
- [Architettura: flusso di dati](../architecture/data-flow.md)
- [guida allo sviluppo dbt](../guides/dbt-development.md)

---

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 16 ottobre 2025