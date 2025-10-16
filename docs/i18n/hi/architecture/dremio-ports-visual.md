# Dremio पोर्ट्स के लिए विज़ुअल गाइड

**संस्करण**: 3.2.5  
**अंतिम अपडेट**: 16 अक्टूबर 2025  
**भाषा**: हिन्दी

---

## Dremio के 3 पोर्ट्स का अवलोकन

```mermaid
graph TB
    subgraph "पोर्ट 9047 - REST API"
        direction TB
        A1[🌐 वेब UI इंटरफ़ेस]
        A2[🔧 प्रशासन]
        A3[📊 निगरानी]
        A4[🔐 प्रमाणीकरण]
    end
    
    subgraph "पोर्ट 31010 - PostgreSQL प्रॉक्सी"
        direction TB
        B1[💼 लिगेसी BI टूल्स]
        B2[🔌 मानक JDBC/ODBC]
        B3[🐘 PostgreSQL संगतता]
        B4[🔄 आसान माइग्रेशन]
    end
    
    subgraph "पोर्ट 32010 - Arrow Flight"
        direction TB
        C1[⚡ अधिकतम प्रदर्शन]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Dremio समन्वयक<br/>Dremio 26.0 OSS]
    
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

## PostgreSQL प्रॉक्सी विस्तृत आर्किटेक्चर

### क्लाइंट → Dremio कनेक्शन प्रवाह

```mermaid
graph LR
    subgraph "क्लाइंट एप्लिकेशन"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "PostgreSQL Wire प्रोटोकॉल"
        P[पोर्ट 31010<br/>PostgreSQL प्रॉक्सी]
    end
    
    subgraph "Dremio इंजन"
        direction TB
        M1[SQL पार्सर]
        M2[ऑप्टिमाइज़र]
        M3[एक्ज़ीक्यूटर]
    end
    
    subgraph "डेटा स्रोत"
        direction TB
        S1[📦 Parquet फ़ाइलें<br/>MinIO S3]
        S2[💾 PostgreSQL तालिकाएँ]
        S3[🔍 Elasticsearch इंडेक्स]
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

## प्रदर्शन तुलना

### बेंचमार्क: 100 GB डेटा स्कैन

```mermaid
gantt
    title प्रोटोकॉल द्वारा निष्पादन समय (सेकंड)
    dateFormat X
    axisFormat %s सेकंड
    
    section REST API :9047
    100 GB स्थानांतरण     :0, 180
    
    section PostgreSQL :31010
    100 GB स्थानांतरण     :0, 90
    
    section Arrow Flight :32010
    100 GB स्थानांतरण     :0, 5
```

### डेटा थ्रूपुट

```mermaid
graph LR
    subgraph "प्रोटोकॉल द्वारा नेटवर्क प्रदर्शन"
        A["पोर्ट 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ मानक"]
        B["पोर्ट 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ अच्छा"]
        C["पोर्ट 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ उत्कृष्ट"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### सरल क्वेरी लेटेंसी

| प्रोटोकॉल | पोर्ट | औसत लेटेंसी | नेटवर्क ओवरहेड |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON (विस्तृत) |
| **PostgreSQL प्रॉक्सी** | 31010 | 20-50 ms | Wire Protocol (संक्षिप्त) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (बाइनरी कॉलमर) |

---

## पोर्ट द्वारा उपयोग के मामले

### पोर्ट 9047 - REST API

```mermaid
graph TB
    A[पोर्ट 9047<br/>REST API]
    
    A --> B1[🌐 वेब ब्राउज़र इंटरफ़ेस]
    A --> B2[🔧 सेवा कॉन्फ़िगरेशन]
    A --> B3[👤 उपयोगकर्ता प्रबंधन]
    A --> B4[📊 निगरानी डैशबोर्ड]
    A --> B5[🔐 OAuth/SAML लॉगिन]
    
    B1 --> C1[स्पेस/फ़ोल्डर बनाएं]
    B1 --> C2[VDS परिभाषित करें]
    B1 --> C3[डेटासेट एक्सप्लोर करें]
    
    B2 --> C4[स्रोत जोड़ें]
    B2 --> C5[Reflections कॉन्फ़िगर करें]
    B2 --> C6[सिस्टम कॉन्फ़िगरेशन]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### पोर्ट 31010 - PostgreSQL प्रॉक्सी

```mermaid
graph TB
    A[पोर्ट 31010<br/>PostgreSQL प्रॉक्सी]
    
    A --> B1[💼 लिगेसी BI टूल्स]
    A --> B2[🔄 PostgreSQL माइग्रेशन]
    A --> B3[🔌 मानक ड्राइवर]
    
    B1 --> C1[Tableau Desktop<br/>Arrow Flight के बिना]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[मौजूदा JDBC कोड<br/>बिना संशोधन के]
    B2 --> D2[psql स्क्रिप्ट<br/>100% संगत]
    B2 --> D3[Python ऐप्स<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[OS नेटिव ड्राइवर]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### पोर्ट 32010 - Arrow Flight

```mermaid
graph TB
    A[पोर्ट 32010<br/>Arrow Flight]
    
    A --> B1[⚡ अधिकतम प्रदर्शन]
    A --> B2[🎯 आधुनिक टूल्स]
    A --> B3[🐍 Python इकोसिस्टम]
    
    B1 --> C1[TB/PB स्कैन]
    B1 --> C2[बड़े पैमाने पर एग्रीगेशन]
    B1 --> C3[ज़ीरो-कॉपी ट्रांसफ़र]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[pyarrow लाइब्रेरी]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Polars इंटीग्रेशन]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## निर्णय वृक्ष: किस पोर्ट का उपयोग करें?

```mermaid
graph TB
    Start[मुझे Dremio से कनेक्ट करना है]
    
    Start --> Q1{एप्लिकेशन प्रकार?}
    
    Q1 -->|वेब इंटरफ़ेस<br/>प्रशासन| Port9047[✅ पोर्ट 9047<br/>REST API]
    
    Q1 -->|BI टूल/SQL क्लाइंट| Q2{Arrow Flight समर्थन?}
    
    Q2 -->|नहीं<br/>लिगेसी टूल| Port31010[✅ पोर्ट 31010<br/>PostgreSQL प्रॉक्सी]
    Q2 -->|हाँ<br/>आधुनिक टूल| Q3{प्रदर्शन महत्वपूर्ण?}
    
    Q3 -->|हाँ<br/>प्रोडक्शन| Port32010[✅ पोर्ट 32010<br/>Arrow Flight]
    Q3 -->|नहीं<br/>Dev/Test| Port31010b[⚠️ पोर्ट 31010<br/>आसान]
    
    Q1 -->|कस्टम एप्लिकेशन| Q4{प्रोग्रामिंग भाषा?}
    
    Q4 -->|Python/Java| Q5{प्रदर्शन महत्वपूर्ण?}
    Q5 -->|हाँ| Port32010b[✅ पोर्ट 32010<br/>Arrow Flight]
    Q5 -->|नहीं| Port31010c[✅ पोर्ट 31010<br/>JDBC/psycopg2]
    
    Q4 -->|अन्य<br/>Go/Rust/.NET| Port31010d[✅ पोर्ट 31010<br/>PostgreSQL Wire]
    
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

## PostgreSQL प्रॉक्सी कनेक्शन उदाहरण

### 1. psql CLI

```bash
# सरल कनेक्शन
psql -h localhost -p 31010 -U admin -d datalake

# सीधी क्वेरी
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# इंटरैक्टिव मोड
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

### 2. DBeaver कॉन्फ़िगरेशन

```yaml
कनेक्शन प्रकार: PostgreSQL
कनेक्शन नाम: Dremio via PostgreSQL Proxy

मुख्य:
  होस्ट: localhost
  पोर्ट: 31010
  डेटाबेस: datalake
  उपयोगकर्ता: admin
  पासवर्ड: [your-password]
  
ड्राइवर गुण:
  ssl: false
  
उन्नत:
  कनेक्शन टाइमआउट: 30000
  क्वेरी टाइमआउट: 0
```

### 3. Python psycopg2 के साथ

```python
import psycopg2
from psycopg2 import sql

# कनेक्शन
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# कर्सर
cursor = conn.cursor()

# सरल क्वेरी
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# पैरामीटराइज़्ड क्वेरी
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# बंद करें
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

### 5. ODBC कनेक्शन स्ट्रिंग (DSN)

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

## Docker Compose कॉन्फ़िगरेशन

### Dremio पोर्ट मैपिंग

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # पोर्ट 9047 - REST API / Web UI
      - "9047:9047"
      
      # पोर्ट 31010 - PostgreSQL प्रॉक्सी (ODBC/JDBC)
      - "31010:31010"
      
      # पोर्ट 32010 - Arrow Flight (प्रदर्शन)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### पोर्ट सत्यापन

```bash
# तीनों पोर्ट खुले हैं या नहीं जाँचें
netstat -an | grep -E '9047|31010|32010'

# REST API परीक्षण
curl -v http://localhost:9047

# PostgreSQL प्रॉक्सी परीक्षण
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Arrow Flight परीक्षण (Python के साथ)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## त्वरित दृश्य सारांश

### एक नज़र में 3 पोर्ट

| पोर्ट | प्रोटोकॉल | मुख्य उपयोग | प्रदर्शन | संगतता |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, Admin | ⭐⭐ मानक | ⭐⭐⭐ सार्वभौमिक |
| **31010** | PostgreSQL Wire | 💼 BI टूल्स, माइग्रेशन | ⭐⭐⭐ अच्छा | ⭐⭐⭐ उत्कृष्ट |
| **32010** | Arrow Flight | ⚡ प्रोडक्शन, dbt, Superset | ⭐⭐⭐⭐⭐ अधिकतम | ⭐⭐ सीमित |

### चयन मैट्रिक्स

```mermaid
graph TB
    subgraph "चयन गाइड"
        A["🎯 उपयोग का मामला"]
        
        A --> B1["वेब इंटरफ़ेस<br/>कॉन्फ़िगरेशन"]
        A --> B2["लिगेसी BI टूल<br/>Arrow Flight नहीं"]
        A --> B3["PostgreSQL माइग्रेशन<br/>मौजूदा JDBC कोड"]
        A --> B4["dbt, Superset<br/>प्रोडक्शन"]
        A --> B5["Python pyarrow<br/>विश्लेषण"]
        
        B1 --> C1["पोर्ट 9047<br/>REST API"]
        B2 --> C2["पोर्ट 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["पोर्ट 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## अतिरिक्त संसाधन

### संबंधित दस्तावेज़ीकरण

- [आर्किटेक्चर - घटक](./components.md) - "Dremio के लिए PostgreSQL प्रॉक्सी" अनुभाग
- [गाइड - Dremio सेटअप](../guides/dremio-setup.md) - "PostgreSQL प्रॉक्सी के माध्यम से कनेक्शन" अनुभाग
- [कॉन्फ़िगरेशन - Dremio](../getting-started/configuration.md) - `dremio.conf` कॉन्फ़िगरेशन

### आधिकारिक लिंक

- **Dremio दस्तावेज़ीकरण**: https://docs.dremio.com/
- **PostgreSQL Wire प्रोटोकॉल**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**संस्करण**: 3.2.5  
**अंतिम अपडेट**: 16 अक्टूबर 2025  
**स्थिति**: ✅ पूर्ण
