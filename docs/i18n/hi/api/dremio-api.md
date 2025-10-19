# ड्रेमियो एपीआई संदर्भ

**संस्करण**: 3.2.0  
**अंतिम अद्यतन**: 16 अक्टूबर, 2025  
**भाषा**: फ्रेंच

## विषयसूची

1. [अवलोकन](#अवलोकन)
2. [प्रमाणीकरण](#प्रमाणीकरण)
3. [रेस्ट एपीआई](#एपीआई-रेस्ट)
4. [एरो फ्लाइट एसक्यूएल](#एरो-फ्लाइट-एसक्यूएल)
5. [ओडीबीसी/जेडीबीसी](#odbcjdbc)
6. [पायथन क्लाइंट](#क्लाइंट-पायथन)
7. [जावा क्लाइंट](#जावा-क्लाइंट)
8. [एपीआई उदाहरण](#डापी-उदाहरण)

---

## अवलोकन

ड्रेमियो डेटा लेकहाउस के साथ इंटरैक्ट करने के लिए कई एपीआई प्रदान करता है:

| एपीआई प्रकार | मामलों का प्रयोग करें | बंदरगाह | प्रोटोकॉल |
|--|--------|------|-------|
| बाकी एपीआई | प्रबंधन, मेटाडेटा | 9047 | HTTP/HTTPS |
| एरोफ्लाइटएसक्यूएल | उच्च निष्पादन प्रश्न | 32010 | जीआरपीसी |
| ओडीबीसी | बीआई टूल कनेक्टिविटी | 31010 | ओडीबीसी |
| जेडीबीसी | जावा एप्लीकेशन | 31010 | जेडीबीसी |

### एपीआई आर्किटेक्चर

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

## प्रमाणीकरण

### एक प्रमाणीकरण टोकन उत्पन्न करें

**समाप्ति बिंदु**: `POST /apiv2/login`

**अनुरोध** :
```bash
curl -X POST http://localhost:9047/apiv2/login \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "admin",
    "password": "your_password"
  }'
```

**उत्तर** :
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userName": "admin",
  "firstName": "Admin",
  "lastName": "User",
  "expires": 1729209600000
}
```

### अनुरोधों में टोकन का उपयोग करें

```bash
# Set token as variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in subsequent requests
curl -X GET http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN"
```

### टोकन समाप्ति

टोकन डिफ़ॉल्ट रूप से 24 घंटे के बाद समाप्त हो जाते हैं। `dremio.conf` में कॉन्फ़िगर करें:

```conf
services.tokens.expiration: 86400000  # 24 hours in milliseconds
```

---

## रेस्ट एपीआई

### बेस यूआरएल

```
http://localhost:9047/apiv2
```

### सामान्य शीर्षलेख

```bash
Authorization: Bearer <token>
Content-Type: application/json
```

### कैटलॉग प्रबंधन

#### कैटलॉग आइटमों की सूची बनाएं

**समाप्ति बिंदु**: `GET /catalog`

```bash
curl -X GET http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN"
```

**उत्तर** :
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

#### पथ के अनुसार कैटलॉग आइटम प्राप्त करें

**समाप्ति बिंदु**: `GET /catalog/by-path/{path}`

```bash
curl -X GET "http://localhost:9047/apiv2/catalog/by-path/MinIO/bronze/customers" \
  -H "Authorization: Bearer $TOKEN"
```

**उत्तर** :
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

### वर्चुअल डेटासेट (वीडीएस)

#### एक वर्चुअल डेटासेट बनाएं

**समाप्ति बिंदु**: `POST /catalog`

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

**उत्तर** :
```json
{
  "id": "vds-id-789",
  "path": ["Production", "Dimensions", "dim_customers"],
  "tag": "vds-tag-789",
  "type": "VIRTUAL_DATASET"
}
```

#### वर्चुअल डेटासेट अपडेट करें

**समाप्ति बिंदु**: `PUT /catalog/{id}`

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

#### एक डेटासेट हटाएं

**समाप्ति बिंदु**: `DELETE /catalog/{id}?tag={tag}`

```bash
curl -X DELETE "http://localhost:9047/apiv2/catalog/vds-id-789?tag=vds-tag-789" \
  -H "Authorization: Bearer $TOKEN"
```

### एसक्यूएल निष्पादन

#### SQL क्वेरी निष्पादित करें

**समाप्ति बिंदु**: `POST /sql`

```bash
curl -X POST http://localhost:9047/apiv2/sql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM Production.Dimensions.dim_customers LIMIT 10"
  }'
```

**उत्तर** :
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

### कार्य प्रबंधन

#### नौकरी का दर्जा प्राप्त करें

**समाप्ति बिंदु**: `GET /job/{jobId}`

```bash
curl -X GET "http://localhost:9047/apiv2/job/job-id-abc123" \
  -H "Authorization: Bearer $TOKEN"
```

**उत्तर** :
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

#### हाल की नौकरियों की सूची बनाएं

**समाप्ति बिंदु**: `GET /jobs`

```bash
curl -X GET "http://localhost:9047/apiv2/jobs?limit=20&sort=startTime&order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

#### कोई कार्य रद्द करें

**समाप्ति बिंदु**: `POST /job/{jobId}/cancel`

```bash
curl -X POST "http://localhost:9047/apiv2/job/job-id-abc123/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

###प्रतिबिंब

#### सूची प्रतिबिंब

**समाप्ति बिंदु**: `GET /reflections`

```bash
curl -X GET http://localhost:9047/apiv2/reflections \
  -H "Authorization: Bearer $TOKEN"
```

**उत्तर** :
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

#### एक प्रतिबिंब बनाएं

**समाप्ति बिंदु**: `POST /reflections`

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

### स्रोत प्रबंधन

#### एक S3 स्रोत जोड़ें

**समाप्ति बिंदु**: `PUT /source/{name}`

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

#### स्रोत मेटाडेटा ताज़ा करें

**समाप्ति बिंदु**: `POST /source/{name}/refresh`

```bash
curl -X POST "http://localhost:9047/apiv2/source/MinIO/refresh" \
  -H "Authorization: Bearer $TOKEN"
```

---

## एरो फ्लाइट एसक्यूएल

एरो फ़्लाइट SQL उच्च प्रदर्शन क्वेरी निष्पादन (ODBC/JDBC से 20-50x तेज़) प्रदान करता है।

### पायएरो के साथ पायथन क्लाइंट

#### सुविधा

```bash
pip install pyarrow
```

#### कनेक्शन और क्वेरी

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

#### उदाहरण: पैरामीटर के साथ क्वेरी

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

#### प्रचय संसाधन

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

### प्रदर्शन तुलना

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

## ओडीबीसी/जेडीबीसी

### ओडीबीसी कनेक्शन

#### विंडोज सेटअप

1. **ओडीबीसी ड्राइवर डाउनलोड करें**:
   ```
   https://download.dremio.com/odbc-driver/dremio-odbc-1.4.0.1041.msi
   ```

2. **डीएसएन कॉन्फ़िगर करें**:
   ```
   Host: localhost
   Port: 31010
   Authentication Type: Plain
   UID: admin
   PWD: your_password
   ```

3. **कनेक्शन स्ट्रिंग**:
   ```
   DRIVER={Dremio ODBC Driver 64-bit};
   HOST=localhost;
   PORT=31010;
   UID=admin;
   PWD=your_password;
   AuthenticationType=Plain
   ```

#### लिनक्स सेटअप

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

### जेडीबीसी कनेक्शन

#### ड्राइवर डाउनलोड करें

```bash
wget https://download.dremio.com/jdbc-driver/dremio-jdbc-driver-26.0.0.jar
```

#### कनेक्शन स्ट्रिंग

```java
String url = "jdbc:dremio:direct=localhost:31010";
String username = "admin";
String password = "your_password";

Connection conn = DriverManager.getConnection(url, username, password);
```

#### गुण

```properties
jdbc:dremio:direct=localhost:31010;
schema=Production;
authentication=PLAIN;
useEncryption=false
```

---

## पायथन क्लाइंट

### पूरा उदाहरण

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

## जावा क्लाइंट

### मावेन निर्भरता

```xml
<dependency>
    <groupId>com.dremio.distribution</groupId>
    <artifactId>dremio-jdbc-driver</artifactId>
    <version>26.0.0</version>
</dependency>
```

### पूरा उदाहरण

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

## एपीआई उदाहरण

### उदाहरण 1: स्वचालित रिपोर्टिंग

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

### उदाहरण 2: डेटा निर्यात

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

### उदाहरण 3: मेटाडेटा खोज

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

## सारांश

इस एपीआई संदर्भ में शामिल है:

- **प्रमाणीकरण**: REST API के साथ टोकन-आधारित प्रमाणीकरण
- **रेस्ट एपीआई**: कैटलॉग, एसक्यूएल निष्पादन, नौकरियां, प्रतिबिंब
- **एरो फ़्लाइट एसक्यूएल**: उच्च प्रदर्शन क्वेरीज़ (20-50x तेज़)
- **ओडीबीसी/जेडीबीसी**: बीआई टूल कनेक्टिविटी
- **पायथन क्लाइंट**: पूर्ण क्लाइंट कार्यान्वयन
- **जावा क्लाइंट**: जेडीबीसी उदाहरण
- **व्यावहारिक उदाहरण**: रिपोर्टिंग, निर्यात, मेटाडेटा खोज

**चाबी छीनना**:
- उच्च प्रदर्शन डेटा एक्सेस के लिए एरो फ़्लाइट SQL का उपयोग करें
- प्रबंधन और स्वचालन के लिए REST API का उपयोग करें
- बीआई टूल्स के एकीकरण के लिए ओडीबीसी/जेडीबीसी का उपयोग करें
- हमेशा प्रमाणीकरण टोकन का उपयोग करें
- बेहतर प्रदर्शन के लिए बड़े प्रश्नों को बैचों में संसाधित करें

**संबंधित दस्तावेज़:**
- [ड्रेमियो सेटअप गाइड](../guides/dremio-setup.md)
- [आर्किटेक्चर: डेटा प्रवाह](../आर्किटेक्चर/डेटा-फ्लो.एमडी)
- [डीबीटी विकास गाइड](../guides/dbt-development.md)

---

**संस्करण**: 3.2.0  
**अंतिम अद्यतन**: 16 अक्टूबर, 2025