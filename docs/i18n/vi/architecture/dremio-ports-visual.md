# Hướng dẫn Trực quan về Cổng Dremio

**Phiên bản**: 3.2.5  
**Cập nhật lần cuối**: 16 Tháng 10, 2025  
**Ngôn ngữ**: Tiếng Việt

---

## Tổng quan 3 Cổng Dremio

```mermaid
graph TB
    subgraph "Cổng 9047 - REST API"
        direction TB
        A1[🌐 Giao diện Web UI]
        A2[🔧 Quản trị]
        A3[📊 Giám sát]
        A4[🔐 Xác thực]
    end
    
    subgraph "Cổng 31010 - PostgreSQL Proxy"
        direction TB
        B1[💼 Công cụ BI cũ]
        B2[🔌 JDBC/ODBC chuẩn]
        B3[🐘 Tương thích PostgreSQL]
        B4[🔄 Di chuyển dễ dàng]
    end
    
    subgraph "Cổng 32010 - Arrow Flight"
        direction TB
        C1[⚡ Hiệu suất tối đa]
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

## Kiến trúc Chi tiết PostgreSQL Proxy

### Luồng Kết nối Máy khách → Dremio

```mermaid
graph LR
    subgraph "Ứng dụng Máy khách"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "Giao thức PostgreSQL Wire"
        P[Cổng 31010<br/>PostgreSQL Proxy]
    end
    
    subgraph "Công cụ Dremio"
        direction TB
        M1[SQL Parser]
        M2[Optimizer]
        M3[Executor]
    end
    
    subgraph "Nguồn Dữ liệu"
        direction TB
        S1[📦 Tệp Parquet<br/>MinIO S3]
        S2[💾 Bảng PostgreSQL]
        S3[🔍 Index Elasticsearch]
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

## So sánh Hiệu suất

### Đánh giá: Quét Dữ liệu 100 GB

```mermaid
gantt
    title Thời gian Thực thi theo Giao thức (giây)
    dateFormat X
    axisFormat %s giây
    
    section REST API :9047
    Truyền 100 GB     :0, 180
    
    section PostgreSQL :31010
    Truyền 100 GB     :0, 90
    
    section Arrow Flight :32010
    Truyền 100 GB     :0, 5
```

### Thông lượng Dữ liệu

```mermaid
graph LR
    subgraph "Hiệu suất Mạng theo Giao thức"
        A["Cổng 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ Tiêu chuẩn"]
        B["Cổng 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ Tốt"]
        C["Cổng 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ Xuất sắc"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### Độ trễ Truy vấn Đơn giản

| Giao thức | Cổng | Độ trễ Trung bình | Chi phí Mạng |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON (chi tiết) |
| **PostgreSQL Proxy** | 31010 | 20-50 ms | Wire Protocol (gọn) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (nhị phân cột) |

---

## Trường hợp Sử dụng theo Cổng

### Cổng 9047 - REST API

```mermaid
graph TB
    A[Cổng 9047<br/>REST API]
    
    A --> B1[🌐 Giao diện Trình duyệt Web]
    A --> B2[🔧 Cấu hình Dịch vụ]
    A --> B3[👤 Quản lý Người dùng]
    A --> B4[📊 Bảng điều khiển Giám sát]
    A --> B5[🔐 Đăng nhập OAuth/SAML]
    
    B1 --> C1[Tạo Space/Thư mục]
    B1 --> C2[Định nghĩa VDS]
    B1 --> C3[Khám phá Dataset]
    
    B2 --> C4[Thêm Nguồn]
    B2 --> C5[Cấu hình Reflections]
    B2 --> C6[Cấu hình Hệ thống]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### Cổng 31010 - PostgreSQL Proxy

```mermaid
graph TB
    A[Cổng 31010<br/>PostgreSQL Proxy]
    
    A --> B1[💼 Công cụ BI cũ]
    A --> B2[🔄 Di chuyển PostgreSQL]
    A --> B3[🔌 Driver chuẩn]
    
    B1 --> C1[Tableau Desktop<br/>Không có Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[Mã JDBC hiện có<br/>Không cần sửa đổi]
    B2 --> D2[Script psql<br/>Tương thích 100%]
    B2 --> D3[Ứng dụng Python<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[Driver gốc HĐH]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### Cổng 32010 - Arrow Flight

```mermaid
graph TB
    A[Cổng 32010<br/>Arrow Flight]
    
    A --> B1[⚡ Hiệu suất Tối đa]
    A --> B2[🎯 Công cụ Hiện đại]
    A --> B3[🐍 Hệ sinh thái Python]
    
    B1 --> C1[Quét TB/PB]
    B1 --> C2[Tổng hợp Lớn]
    B1 --> C3[Truyền Zero-Copy]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Cấu hình Database]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[Thư viện pyarrow]
    B3 --> E2[pandas qua Arrow]
    B3 --> E3[Tích hợp Polars]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## Sơ đồ Quyết định: Cổng Nào Sử dụng?

```mermaid
graph TB
    Start[Tôi cần kết nối đến Dremio]
    
    Start --> Q1{Loại ứng dụng?}
    
    Q1 -->|Giao diện web<br/>Quản trị| Port9047[✅ Cổng 9047<br/>REST API]
    
    Q1 -->|Công cụ BI/SQL Client| Q2{Hỗ trợ Arrow Flight?}
    
    Q2 -->|Không<br/>Công cụ cũ| Port31010[✅ Cổng 31010<br/>PostgreSQL Proxy]
    Q2 -->|Có<br/>Công cụ hiện đại| Q3{Hiệu suất quan trọng?}
    
    Q3 -->|Có<br/>Production| Port32010[✅ Cổng 32010<br/>Arrow Flight]
    Q3 -->|Không<br/>Dev/Test| Port31010b[⚠️ Cổng 31010<br/>Dễ hơn]
    
    Q1 -->|Ứng dụng Tùy chỉnh| Q4{Ngôn ngữ lập trình?}
    
    Q4 -->|Python/Java| Q5{Hiệu suất quan trọng?}
    Q5 -->|Có| Port32010b[✅ Cổng 32010<br/>Arrow Flight]
    Q5 -->|Không| Port31010c[✅ Cổng 31010<br/>JDBC/psycopg2]
    
    Q4 -->|Khác<br/>Go/Rust/.NET| Port31010d[✅ Cổng 31010<br/>PostgreSQL Wire]
    
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

## Ví dụ Kết nối PostgreSQL Proxy

### 1. psql CLI

```bash
# Kết nối đơn giản
psql -h localhost -p 31010 -U admin -d datalake

# Truy vấn trực tiếp
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# Chế độ tương tác
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

### 2. Cấu hình DBeaver

```yaml
Loại Kết nối: PostgreSQL
Tên Kết nối: Dremio via PostgreSQL Proxy

Chính:
  Host: localhost
  Cổng: 31010
  Cơ sở dữ liệu: datalake
  Tên người dùng: admin
  Mật khẩu: [your-password]
  
Thuộc tính Driver:
  ssl: false
  
Nâng cao:
  Thời gian chờ kết nối: 30000
  Thời gian chờ truy vấn: 0
```

### 3. Python với psycopg2

```python
import psycopg2
from psycopg2 import sql

# Kết nối
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# Con trỏ
cursor = conn.cursor()

# Truy vấn đơn giản
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Truy vấn có tham số
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# Đóng
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

### 5. Chuỗi Kết nối ODBC (DSN)

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

## Cấu hình Docker Compose

### Ánh xạ Cổng Dremio

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # Cổng 9047 - REST API / Web UI
      - "9047:9047"
      
      # Cổng 31010 - PostgreSQL Proxy (ODBC/JDBC)
      - "31010:31010"
      
      # Cổng 32010 - Arrow Flight (Hiệu suất)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### Xác thực Cổng

```bash
# Kiểm tra cả ba cổng đều mở
netstat -an | grep -E '9047|31010|32010'

# Kiểm tra REST API
curl -v http://localhost:9047

# Kiểm tra PostgreSQL Proxy
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Kiểm tra Arrow Flight (với Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## Tóm tắt Trực quan Nhanh

### 3 Cổng trong Một Cái nhìn

| Cổng | Giao thức | Sử dụng Chính | Hiệu suất | Tương thích |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, Admin | ⭐⭐ Tiêu chuẩn | ⭐⭐⭐ Phổ quát |
| **31010** | PostgreSQL Wire | 💼 Công cụ BI, Di chuyển | ⭐⭐⭐ Tốt | ⭐⭐⭐ Xuất sắc |
| **32010** | Arrow Flight | ⚡ Production, dbt, Superset | ⭐⭐⭐⭐⭐ Tối đa | ⭐⭐ Hạn chế |

### Ma trận Lựa chọn

```mermaid
graph TB
    subgraph "Hướng dẫn Lựa chọn"
        A["🎯 Trường hợp Sử dụng"]
        
        A --> B1["Giao diện Web<br/>Cấu hình"]
        A --> B2["Công cụ BI cũ<br/>Không Arrow Flight"]
        A --> B3["Di chuyển PostgreSQL<br/>Mã JDBC hiện có"]
        A --> B4["dbt, Superset<br/>Production"]
        A --> B5["Python pyarrow<br/>Phân tích"]
        
        B1 --> C1["Cổng 9047<br/>REST API"]
        B2 --> C2["Cổng 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["Cổng 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## Tài nguyên Bổ sung

### Tài liệu Liên quan

- [Kiến trúc - Thành phần](./components.md) - Phần "PostgreSQL Proxy cho Dremio"
- [Hướng dẫn - Cài đặt Dremio](../guides/dremio-setup.md) - Phần "Kết nối qua PostgreSQL Proxy"
- [Cấu hình - Dremio](../getting-started/configuration.md) - Cấu hình `dremio.conf`

### Liên kết Chính thức

- **Tài liệu Dremio**: https://docs.dremio.com/
- **Giao thức PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Phiên bản**: 3.2.5  
**Cập nhật lần cuối**: 16 Tháng 10, 2025  
**Trạng thái**: ✅ Hoàn thành
