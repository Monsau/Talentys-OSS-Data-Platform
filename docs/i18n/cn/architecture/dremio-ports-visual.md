# Dremio 端口可视化指南

**版本**: 3.2.5  
**最后更新**: 2025年10月16日  
**语言**: 中文

---

## Dremio 三个端口概览

```mermaid
graph TB
    subgraph "端口 9047 - REST API"
        direction TB
        A1[🌐 Web UI 界面]
        A2[🔧 管理配置]
        A3[📊 监控]
        A4[🔐 身份验证]
    end
    
    subgraph "端口 31010 - PostgreSQL 代理"
        direction TB
        B1[💼 传统 BI 工具]
        B2[🔌 标准 JDBC/ODBC]
        B3[🐘 PostgreSQL 兼容]
        B4[🔄 轻松迁移]
    end
    
    subgraph "端口 32010 - Arrow Flight"
        direction TB
        C1[⚡ 最大性能]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Dremio 协调器<br/>Dremio 26.0 OSS]
    
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

## PostgreSQL 代理详细架构

### 客户端 → Dremio 连接流程

```mermaid
graph LR
    subgraph "客户端应用"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "PostgreSQL Wire 协议"
        P[端口 31010<br/>PostgreSQL 代理]
    end
    
    subgraph "Dremio 引擎"
        direction TB
        M1[SQL 解析器]
        M2[优化器]
        M3[执行器]
    end
    
    subgraph "数据源"
        direction TB
        S1[📦 Parquet 文件<br/>MinIO S3]
        S2[💾 PostgreSQL 表]
        S3[🔍 Elasticsearch 索引]
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

## 性能对比

### 基准测试：扫描 100 GB 数据

```mermaid
gantt
    title 各协议执行时间（秒）
    dateFormat X
    axisFormat %s 秒
    
    section REST API :9047
    传输 100 GB     :0, 180
    
    section PostgreSQL :31010
    传输 100 GB     :0, 90
    
    section Arrow Flight :32010
    传输 100 GB     :0, 5
```

### 数据吞吐量

```mermaid
graph LR
    subgraph "各协议网络性能"
        A["端口 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ 标准"]
        B["端口 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ 良好"]
        C["端口 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ 优秀"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### 简单查询延迟

| 协议 | 端口 | 平均延迟 | 网络开销 |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 毫秒 | JSON（冗长） |
| **PostgreSQL 代理** | 31010 | 20-50 毫秒 | Wire Protocol（紧凑） |
| **Arrow Flight** | 32010 | 5-10 毫秒 | Apache Arrow（二进制列式） |

---

## 各端口使用场景

### 端口 9047 - REST API

```mermaid
graph TB
    A[端口 9047<br/>REST API]
    
    A --> B1[🌐 Web 浏览器界面]
    A --> B2[🔧 服务配置]
    A --> B3[👤 用户管理]
    A --> B4[📊 监控面板]
    A --> B5[🔐 OAuth/SAML 登录]
    
    B1 --> C1[创建空间/文件夹]
    B1 --> C2[定义 VDS]
    B1 --> C3[探索数据集]
    
    B2 --> C4[添加数据源]
    B2 --> C5[配置 Reflections]
    B2 --> C6[系统配置]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### 端口 31010 - PostgreSQL 代理

```mermaid
graph TB
    A[端口 31010<br/>PostgreSQL 代理]
    
    A --> B1[💼 传统 BI 工具]
    A --> B2[🔄 PostgreSQL 迁移]
    A --> B3[🔌 标准驱动程序]
    
    B1 --> C1[Tableau Desktop<br/>无 Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[现有 JDBC 代码<br/>无需修改]
    B2 --> D2[psql 脚本<br/>100% 兼容]
    B2 --> D3[Python 应用<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[操作系统原生驱动]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### 端口 32010 - Arrow Flight

```mermaid
graph TB
    A[端口 32010<br/>Arrow Flight]
    
    A --> B1[⚡ 最大性能]
    A --> B2[🎯 现代工具]
    A --> B3[🐍 Python 生态]
    
    B1 --> C1[TB/PB 扫描]
    B1 --> C2[大规模聚合]
    B1 --> C3[零拷贝传输]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[pyarrow 库]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Polars 集成]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## 决策树：使用哪个端口？

```mermaid
graph TB
    Start[我需要连接到 Dremio]
    
    Start --> Q1{应用类型？}
    
    Q1 -->|Web 界面<br/>管理| Port9047[✅ 端口 9047<br/>REST API]
    
    Q1 -->|BI 工具/SQL 客户端| Q2{支持 Arrow Flight？}
    
    Q2 -->|否<br/>传统工具| Port31010[✅ 端口 31010<br/>PostgreSQL 代理]
    Q2 -->|是<br/>现代工具| Q3{性能关键？}
    
    Q3 -->|是<br/>生产环境| Port32010[✅ 端口 32010<br/>Arrow Flight]
    Q3 -->|否<br/>开发/测试| Port31010b[⚠️ 端口 31010<br/>更简单]
    
    Q1 -->|自定义应用| Q4{编程语言？}
    
    Q4 -->|Python/Java| Q5{性能重要？}
    Q5 -->|是| Port32010b[✅ 端口 32010<br/>Arrow Flight]
    Q5 -->|否| Port31010c[✅ 端口 31010<br/>JDBC/psycopg2]
    
    Q4 -->|其他<br/>Go/Rust/.NET| Port31010d[✅ 端口 31010<br/>PostgreSQL Wire]
    
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

## PostgreSQL 代理连接示例

### 1. psql CLI

```bash
# 简单连接
psql -h localhost -p 31010 -U admin -d datalake

# 直接查询
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# 交互模式
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

### 2. DBeaver 配置

```yaml
连接类型: PostgreSQL
连接名称: Dremio via PostgreSQL Proxy

主要:
  主机: localhost
  端口: 31010
  数据库: datalake
  用户名: admin
  密码: [你的密码]
  
驱动属性:
  ssl: false
  
高级:
  连接超时: 30000
  查询超时: 0
```

### 3. Python psycopg2

```python
import psycopg2
from psycopg2 import sql

# 连接
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="你的密码"
)

# 游标
cursor = conn.cursor()

# 简单查询
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# 参数化查询
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# 关闭
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
        String password = "你的密码";
        
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

### 5. ODBC 连接字符串 (DSN)

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
Password=你的密码
SSLMode=disable
Protocol=7.4
```

---

## Docker Compose 配置

### Dremio 端口映射

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # 端口 9047 - REST API / Web UI
      - "9047:9047"
      
      # 端口 31010 - PostgreSQL 代理 (ODBC/JDBC)
      - "31010:31010"
      
      # 端口 32010 - Arrow Flight (高性能)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### 端口验证

```bash
# 检查三个端口是否开放
netstat -an | grep -E '9047|31010|32010'

# 测试 REST API
curl -v http://localhost:9047

# 测试 PostgreSQL 代理
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# 测试 Arrow Flight (使用 Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## 快速视觉摘要

### 三个端口一览

| 端口 | 协议 | 主要用途 | 性能 | 兼容性 |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, 管理 | ⭐⭐ 标准 | ⭐⭐⭐ 通用 |
| **31010** | PostgreSQL Wire | 💼 BI 工具, 迁移 | ⭐⭐⭐ 良好 | ⭐⭐⭐ 优秀 |
| **32010** | Arrow Flight | ⚡ 生产, dbt, Superset | ⭐⭐⭐⭐⭐ 最高 | ⭐⭐ 受限 |

### 选择矩阵

```mermaid
graph TB
    subgraph "选择指南"
        A["🎯 使用场景"]
        
        A --> B1["Web 界面<br/>配置"]
        A --> B2["传统 BI 工具<br/>无 Arrow Flight"]
        A --> B3["PostgreSQL 迁移<br/>现有 JDBC 代码"]
        A --> B4["dbt, Superset<br/>生产环境"]
        A --> B5["Python pyarrow<br/>分析"]
        
        B1 --> C1["端口 9047<br/>REST API"]
        B2 --> C2["端口 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["端口 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## 附加资源

### 相关文档

- [架构 - 组件](./components.md) - "Dremio PostgreSQL 代理"部分
- [指南 - Dremio 设置](../guides/dremio-setup.md) - "通过 PostgreSQL 代理连接"部分
- [配置 - Dremio](../getting-started/configuration.md) - `dremio.conf` 配置

### 官方链接

- **Dremio 文档**: https://docs.dremio.com/
- **PostgreSQL Wire 协议**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**版本**: 3.2.5  
**最后更新**: 2025年10月16日  
**状态**: ✅ 完成
