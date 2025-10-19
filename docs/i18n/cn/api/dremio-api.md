# Dremio API 参考

**版本**：3.2.0  
**最后更新**：2025 年 10 月 16 日  
**语言**：法语

＃＃ 目录

1. [概述](#overview)
2. [身份验证](#authentication)
3. [REST API](#api-rest)
4. [Arrow Flight SQL](#arrow-flight-sql)
5. [ODBC/JDBC](#odbcjdbc)
6. [Python客户端](#client-python)
7. [Java客户端](#java-client)
8. [API 示例](#dapi-examples)

---

＃＃ 概述

Dremio 提供了多个 API 来与数据 Lakehouse 交互：

| API 类型 |使用案例 |港口|协议|
|------------|--------|------|---------|
|休息 API |管理、元数据 | 9047 | 9047 HTTP/HTTPS |
| ArrowFlightSQL |高性能查询 | 32010| gRPC |
| ODBC | BI 工具连接 | 31010| ODBC |
|数据库管理 | Java 应用程序 | 31010|数据库管理 |

### API架构

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

＃＃ 验证

### 生成身份验证令牌

**端点**：`POST /apiv2/login`

**要求** ：
```bash
curl -X POST http://localhost:9047/apiv2/login \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "admin",
    "password": "your_password"
  }'
```

**回答** ：
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userName": "admin",
  "firstName": "Admin",
  "lastName": "User",
  "expires": 1729209600000
}
```

### 在请求中使用令牌

```bash
# Set token as variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in subsequent requests
curl -X GET http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN"
```

### 令牌过期

默认情况下，令牌会在 24 小时后过期。在`dremio.conf`中配置：

```conf
services.tokens.expiration: 86400000  # 24 hours in milliseconds
```

---

## 休息 API

### 基本网址

```
http://localhost:9047/apiv2
```

### 常用标头

```bash
Authorization: Bearer <token>
Content-Type: application/json
```

### 目录管理

#### 列出目录项

**端点**：`GET /catalog`

```bash
curl -X GET http://localhost:9047/apiv2/catalog \
  -H "Authorization: Bearer $TOKEN"
```

**回答** ：
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

#### 通过路径获取目录项

**端点**：`GET /catalog/by-path/{path}`

```bash
curl -X GET "http://localhost:9047/apiv2/catalog/by-path/MinIO/bronze/customers" \
  -H "Authorization: Bearer $TOKEN"
```

**回答** ：
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

### 虚拟数据集 (VDS)

#### 创建虚拟数据集

**端点**：`POST /catalog`

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

**回答** ：
```json
{
  "id": "vds-id-789",
  "path": ["Production", "Dimensions", "dim_customers"],
  "tag": "vds-tag-789",
  "type": "VIRTUAL_DATASET"
}
```

#### 更新虚拟数据集

**端点**：`PUT /catalog/{id}`

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

#### 删除数据集

**端点**：`DELETE /catalog/{id}?tag={tag}`

```bash
curl -X DELETE "http://localhost:9047/apiv2/catalog/vds-id-789?tag=vds-tag-789" \
  -H "Authorization: Bearer $TOKEN"
```

### SQL执行

#### 执行 SQL 查询

**端点**：`POST /sql`

```bash
curl -X POST http://localhost:9047/apiv2/sql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM Production.Dimensions.dim_customers LIMIT 10"
  }'
```

**回答** ：
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

### 工作管理

#### 获取工作状态

**端点**：`GET /job/{jobId}`

```bash
curl -X GET "http://localhost:9047/apiv2/job/job-id-abc123" \
  -H "Authorization: Bearer $TOKEN"
```

**回答** ：
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

#### 列出最近的工作

**端点**：`GET /jobs`

```bash
curl -X GET "http://localhost:9047/apiv2/jobs?limit=20&sort=startTime&order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

#### 取消工作

**端点**：`POST /job/{jobId}/cancel`

```bash
curl -X POST "http://localhost:9047/apiv2/job/job-id-abc123/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

###反思

#### 列出反射

**端点**：`GET /reflections`

```bash
curl -X GET http://localhost:9047/apiv2/reflections \
  -H "Authorization: Bearer $TOKEN"
```

**回答** ：
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

#### 创建反射

**端点**：`POST /reflections`

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

### 源码管理

#### 添加 S3 源

**端点**：`PUT /source/{name}`

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

#### 刷新源元数据

**端点**：`POST /source/{name}/refresh`

```bash
curl -X POST "http://localhost:9047/apiv2/source/MinIO/refresh" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 箭头飞行 SQL

Arrow Flight SQL 提供高性能查询执行（比 ODBC/JDBC 快 20-50 倍）。

### 使用 PyArrow 的 Python 客户端

＃＃＃＃ 设施

```bash
pip install pyarrow
```

#### 连接与查询

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

#### 示例：带参数查询

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

#### 批处理

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

### 性能比较

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

## ODBC/JDBC

### ODBC 连接

#### Windows 设置

1. **下载 ODBC 驱动程序**：
   ```
   https://download.dremio.com/odbc-driver/dremio-odbc-1.4.0.1041.msi
   ```

2. **配置DSN**：
   ```
   Host: localhost
   Port: 31010
   Authentication Type: Plain
   UID: admin
   PWD: your_password
   ```

3. **连接字符串**：
   ```
   DRIVER={Dremio ODBC Driver 64-bit};
   HOST=localhost;
   PORT=31010;
   UID=admin;
   PWD=your_password;
   AuthenticationType=Plain
   ```

#### Linux 设置

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

### JDBC 连接

#### 下载驱动程序

```bash
wget https://download.dremio.com/jdbc-driver/dremio-jdbc-driver-26.0.0.jar
```

#### 连接字符串

```java
String url = "jdbc:dremio:direct=localhost:31010";
String username = "admin";
String password = "your_password";

Connection conn = DriverManager.getConnection(url, username, password);
```

＃＃＃＃ 特性

```properties
jdbc:dremio:direct=localhost:31010;
schema=Production;
authentication=PLAIN;
useEncryption=false
```

---

## Python 客户端

### 完整示例

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

## Java 客户端

### Maven 依赖

```xml
<dependency>
    <groupId>com.dremio.distribution</groupId>
    <artifactId>dremio-jdbc-driver</artifactId>
    <version>26.0.0</version>
</dependency>
```

### 完整示例

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

## API 示例

### 示例 1：自动报告

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

### 示例2：数据导出

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

### 示例 3：元数据发现

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

＃＃ 概括

此 API 参考涵盖：

- **身份验证**：使用 REST API 进行基于令牌的身份验证
- **REST API**：目录、SQL 执行、作业、反射
- **Arrow Flight SQL**：高性能查询（快 20-50 倍）
- **ODBC/JDBC**：BI 工具连接
- **Python客户端**：完整的客户端实现
- **Java 客户端**：JDBC 示例
- **实际示例**：报告、导出、元数据发现

**要点**：
- 使用 Arrow Flight SQL 进行高性能数据访问
- 使用REST API进行管理和自动化
- 使用ODBC/JDBC进行BI工具集成
- 始终使用身份验证令牌
- 批量处理大型查询以获得更好的性能

**相关文档：**
- [Dremio 设置指南](../guides/dremio-setup.md)
- [架构：数据流](../architecture/data-flow.md)
- [dbt开发指南](../guides/dbt-development.md)

---

**版本**：3.2.0  
**最后更新**：2025 年 10 月 16 日