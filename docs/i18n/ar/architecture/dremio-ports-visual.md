# الدليل المرئي لمنافذ Dremio

**الإصدار**: 3.2.5  
**آخر تحديث**: 16 أكتوبر 2025  
**اللغة**: العربية

---

## نظرة عامة على منافذ Dremio الثلاثة

```mermaid
graph TB
    subgraph "المنفذ 9047 - REST API"
        direction TB
        A1[🌐 واجهة الويب UI]
        A2[🔧 الإدارة]
        A3[📊 المراقبة]
        A4[🔐 المصادقة]
    end
    
    subgraph "المنفذ 31010 - وكيل PostgreSQL"
        direction TB
        B1[💼 أدوات BI القديمة]
        B2[🔌 JDBC/ODBC قياسي]
        B3[🐘 توافق PostgreSQL]
        B4[🔄 ترحيل سهل]
    end
    
    subgraph "المنفذ 32010 - Arrow Flight"
        direction TB
        C1[⚡ أداء أقصى]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ منسق Dremio<br/>Dremio 26.0 OSS]
    
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

## بنية وكيل PostgreSQL التفصيلية

### تدفق الاتصال العميل → Dremio

```mermaid
graph LR
    subgraph "تطبيقات العميل"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "بروتوكول PostgreSQL Wire"
        P[المنفذ 31010<br/>وكيل PostgreSQL]
    end
    
    subgraph "محرك Dremio"
        direction TB
        M1[محلل SQL]
        M2[محسّن]
        M3[منفذ]
    end
    
    subgraph "مصادر البيانات"
        direction TB
        S1[📦 ملفات Parquet<br/>MinIO S3]
        S2[💾 جداول PostgreSQL]
        S3[🔍 فهرس Elasticsearch]
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

## مقارنة الأداء

### معيار: مسح 100 جيجابايت من البيانات

```mermaid
gantt
    title وقت التنفيذ حسب البروتوكول (ثواني)
    dateFormat X
    axisFormat %s ثانية
    
    section REST API :9047
    نقل 100 جيجابايت     :0, 180
    
    section PostgreSQL :31010
    نقل 100 جيجابايت     :0, 90
    
    section Arrow Flight :32010
    نقل 100 جيجابايت     :0, 5
```

### إنتاجية البيانات

```mermaid
graph LR
    subgraph "أداء الشبكة حسب البروتوكول"
        A["المنفذ 9047<br/>REST API<br/>📊 ~500 ميجابايت/ث<br/>⏱️ قياسي"]
        B["المنفذ 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 جيجابايت/ث<br/>⏱️ جيد"]
        C["المنفذ 32010<br/>Arrow Flight<br/>📊 ~20 جيجابايت/ث<br/>⏱️ ممتاز"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### تأخير الاستعلام البسيط

| البروتوكول | المنفذ | التأخير المتوسط | عبء الشبكة |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 مللي ثانية | JSON (مطوّل) |
| **وكيل PostgreSQL** | 31010 | 20-50 مللي ثانية | Wire Protocol (مضغوط) |
| **Arrow Flight** | 32010 | 5-10 مللي ثانية | Apache Arrow (ثنائي عمودي) |

---

## حالات الاستخدام حسب المنفذ

### المنفذ 9047 - REST API

```mermaid
graph TB
    A[المنفذ 9047<br/>REST API]
    
    A --> B1[🌐 واجهة متصفح الويب]
    A --> B2[🔧 تكوين الخدمات]
    A --> B3[👤 إدارة المستخدمين]
    A --> B4[📊 لوحات المراقبة]
    A --> B5[🔐 تسجيل دخول OAuth/SAML]
    
    B1 --> C1[إنشاء مساحات/مجلدات]
    B1 --> C2[تعريف VDS]
    B1 --> C3[استكشاف مجموعات البيانات]
    
    B2 --> C4[إضافة مصادر]
    B2 --> C5[تكوين Reflections]
    B2 --> C6[تكوين النظام]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### المنفذ 31010 - وكيل PostgreSQL

```mermaid
graph TB
    A[المنفذ 31010<br/>وكيل PostgreSQL]
    
    A --> B1[💼 أدوات BI القديمة]
    A --> B2[🔄 ترحيل PostgreSQL]
    A --> B3[🔌 برامج تشغيل قياسية]
    
    B1 --> C1[Tableau Desktop<br/>بدون Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[كود JDBC موجود<br/>بدون تعديلات]
    B2 --> D2[سكريبتات psql<br/>توافق 100%]
    B2 --> D3[تطبيقات Python<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[برامج تشغيل أصلية للنظام]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### المنفذ 32010 - Arrow Flight

```mermaid
graph TB
    A[المنفذ 32010<br/>Arrow Flight]
    
    A --> B1[⚡ أداء أقصى]
    A --> B2[🎯 أدوات حديثة]
    A --> B3[🐍 نظام Python البيئي]
    
    B1 --> C1[مسح تيرابايت/بيتابايت]
    B1 --> C2[تجميعات ضخمة]
    B1 --> C3[نقل Zero-Copy]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[مكتبة pyarrow]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[تكامل Polars]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## شجرة القرار: أي منفذ تستخدم؟

```mermaid
graph TB
    Start[أحتاج إلى الاتصال بـ Dremio]
    
    Start --> Q1{نوع التطبيق؟}
    
    Q1 -->|واجهة ويب<br/>إدارة| Port9047[✅ المنفذ 9047<br/>REST API]
    
    Q1 -->|أداة BI/عميل SQL| Q2{دعم Arrow Flight؟}
    
    Q2 -->|لا<br/>أداة قديمة| Port31010[✅ المنفذ 31010<br/>وكيل PostgreSQL]
    Q2 -->|نعم<br/>أداة حديثة| Q3{أداء حرج؟}
    
    Q3 -->|نعم<br/>إنتاج| Port32010[✅ المنفذ 32010<br/>Arrow Flight]
    Q3 -->|لا<br/>تطوير/اختبار| Port31010b[⚠️ المنفذ 31010<br/>أسهل]
    
    Q1 -->|تطبيق مخصص| Q4{لغة البرمجة؟}
    
    Q4 -->|Python/Java| Q5{الأداء مهم؟}
    Q5 -->|نعم| Port32010b[✅ المنفذ 32010<br/>Arrow Flight]
    Q5 -->|لا| Port31010c[✅ المنفذ 31010<br/>JDBC/psycopg2]
    
    Q4 -->|أخرى<br/>Go/Rust/.NET| Port31010d[✅ المنفذ 31010<br/>PostgreSQL Wire]
    
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

## أمثلة اتصال وكيل PostgreSQL

### 1. psql CLI

```bash
# اتصال بسيط
psql -h localhost -p 31010 -U admin -d datalake

# استعلام مباشر
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# الوضع التفاعلي
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

### 2. تكوين DBeaver

```yaml
نوع الاتصال: PostgreSQL
اسم الاتصال: Dremio via PostgreSQL Proxy

الرئيسي:
  المضيف: localhost
  المنفذ: 31010
  قاعدة البيانات: datalake
  المستخدم: admin
  كلمة المرور: [كلمة-المرور-الخاصة-بك]
  
خصائص برنامج التشغيل:
  ssl: false
  
متقدم:
  مهلة الاتصال: 30000
  مهلة الاستعلام: 0
```

### 3. Python مع psycopg2

```python
import psycopg2
from psycopg2 import sql

# الاتصال
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="كلمة-المرور-الخاصة-بك"
)

# المؤشر
cursor = conn.cursor()

# استعلام بسيط
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# استعلام معلمي
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# الإغلاق
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
        String password = "كلمة-المرور-الخاصة-بك";
        
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

### 5. سلسلة اتصال ODBC (DSN)

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
Password=كلمة-المرور-الخاصة-بك
SSLMode=disable
Protocol=7.4
```

---

## تكوين Docker Compose

### تعيين منافذ Dremio

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # المنفذ 9047 - REST API / Web UI
      - "9047:9047"
      
      # المنفذ 31010 - وكيل PostgreSQL (ODBC/JDBC)
      - "31010:31010"
      
      # المنفذ 32010 - Arrow Flight (الأداء)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### التحقق من المنافذ

```bash
# التحقق من فتح المنافذ الثلاثة
netstat -an | grep -E '9047|31010|32010'

# اختبار REST API
curl -v http://localhost:9047

# اختبار وكيل PostgreSQL
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# اختبار Arrow Flight (مع Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## ملخص مرئي سريع

### المنافذ الثلاثة في لمحة

| المنفذ | البروتوكول | الاستخدام الرئيسي | الأداء | التوافق |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, إدارة | ⭐⭐ قياسي | ⭐⭐⭐ عالمي |
| **31010** | PostgreSQL Wire | 💼 أدوات BI, ترحيل | ⭐⭐⭐ جيد | ⭐⭐⭐ ممتاز |
| **32010** | Arrow Flight | ⚡ إنتاج, dbt, Superset | ⭐⭐⭐⭐⭐ أقصى | ⭐⭐ محدود |

### مصفوفة الاختيار

```mermaid
graph TB
    subgraph "دليل الاختيار"
        A["🎯 حالة الاستخدام"]
        
        A --> B1["واجهة ويب<br/>تكوين"]
        A --> B2["أداة BI قديمة<br/>بدون Arrow Flight"]
        A --> B3["ترحيل PostgreSQL<br/>كود JDBC موجود"]
        A --> B4["dbt, Superset<br/>إنتاج"]
        A --> B5["Python pyarrow<br/>تحليلات"]
        
        B1 --> C1["المنفذ 9047<br/>REST API"]
        B2 --> C2["المنفذ 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["المنفذ 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## موارد إضافية

### الوثائق ذات الصلة

- [البنية - المكونات](./components.md) - قسم "وكيل PostgreSQL لـ Dremio"
- [الدليل - إعداد Dremio](../guides/dremio-setup.md) - قسم "الاتصال عبر وكيل PostgreSQL"
- [التكوين - Dremio](../getting-started/configuration.md) - تكوين `dremio.conf`

### الروابط الرسمية

- **وثائق Dremio**: https://docs.dremio.com/
- **بروتوكول PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**الإصدار**: 3.2.5  
**آخر تحديث**: 16 أكتوبر 2025  
**الحالة**: ✅ مكتمل
