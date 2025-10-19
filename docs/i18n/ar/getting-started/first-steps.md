# البدء باستخدام منصة البيانات

**الإصدار**: 3.2.0  
**آخر تحديث**: 16-10-2025  
**اللغة**: الفرنسية

---

## ملخص

يرشدك هذا البرنامج التعليمي خلال تفاعلاتك الأولى مع منصة البيانات، بدءًا من الاتصال بالخدمات وحتى إنشاء أول خط بيانات لك باستخدام Airbyte وDremio وdbt وSuperset.

```mermaid
graph LR
    A[Accéder aux Services] --> B[Configurer Airbyte]
    B --> C[Connecter Dremio]
    C --> D[Créer Modèles dbt]
    D --> E[Construire Tableau de Bord]
    E --> F[Pipeline Complet]
    
    style F fill:#90EE90
    style A fill:#87CEEB
```

**الوقت المقدر**: 60-90 دقيقة

---

## المتطلبات الأساسية

قبل أن تبدأ، تأكد من:

- ✅ جميع الخدمات تم تركيبها وتشغيلها
- ✅ يمكنك الوصول إلى واجهات الويب
- ✅ تم تمكين بيئة بايثون الافتراضية
- ✅ الفهم الأساسي لـ SQL

**التأكد من عمل الخدمات:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## الخطوة 1: الوصول إلى كافة الخدمات

### عناوين URL للخدمة

| الخدمات | عنوان URL | بيانات الاعتماد الافتراضية |
|---------|---------|-----------------------|
| **ايربايت** | http://localhost:8000 | airbyte@example.com / كلمة المرور |
| **دريميو** | http://localhost:9047 | المشرف/admin123 |
| **المجموعة الشاملة** | http://localhost:8088 | المشرف / المشرف |
| **مينيو** | http://localhost:9001 | minioadmin / minioadmin123 |

### الاتصال الأول

**إيربايت:**
1. افتح http://localhost:8000
2. أكمل معالج الإعداد
3. قم بتعيين اسم مساحة العمل: "الإنتاج"
4. تجاوز التفضيلات (التكوين اللاحق ممكن)

**دريميو:**
1. افتح http://localhost:9047
2. قم بإنشاء مستخدم مسؤول عند الوصول لأول مرة:
   - اسم المستخدم: `admin`
   - البريد الإلكتروني: `admin@example.com`
   - كلمة المرور: `admin123`
3. انقر على "البدء"

** المجموعة الشاملة: **
1. افتح http://localhost:8088
2. قم بتسجيل الدخول باستخدام بيانات الاعتماد الافتراضية
3. تغيير كلمة المرور: الإعدادات → معلومات المستخدم → إعادة تعيين كلمة المرور

---

## الخطوة الثانية: قم بتكوين مصدر بياناتك الأول في Airbyte

### إنشاء مصدر PostgreSQL

**السيناريو**: استخراج البيانات من قاعدة بيانات PostgreSQL.

1. ** انتقل إلى المصادر **
   - اضغط على "المصادر" في القائمة اليسرى
   - اضغط على "+ مصدر جديد"

2. **اختر PostgreSQL**
   - ابحث عن "PostgreSQL"
   - انقر على موصل "PostgreSQL".

3. **تكوين الاتصال**
   ```yaml
   Source name: Production PostgreSQL
   Host: postgres
   Port: 5432
   Database: dremio_db
   Username: postgres
   Password: postgres123
   SSL Mode: prefer
   Replication Method: Standard
   ```

4. **اختبر واحفظ**
   - اضغط على "إعداد المصدر"
   - انتظر اختبار الاتصال
   - تم إنشاء المصدر ✅

### إنشاء بيانات نموذجية (اختياري)

إذا لم يكن لديك أي بيانات حتى الآن، فقم بإنشاء جداول الأمثلة:

```sql
-- Se connecter à PostgreSQL
docker exec -it postgres psql -U postgres -d dremio_db

-- Créer des tables exemples
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    amount DECIMAL(10,2),
    status VARCHAR(20),
    order_date DATE DEFAULT CURRENT_DATE
);

-- Insérer des données exemples
INSERT INTO customers (name, email, country) VALUES
    ('John Doe', 'john@example.com', 'USA'),
    ('Jane Smith', 'jane@example.com', 'UK'),
    ('Carlos Garcia', 'carlos@example.com', 'Spain'),
    ('Marie Dubois', 'marie@example.com', 'France'),
    ('Yuki Tanaka', 'yuki@example.com', 'Japan');

INSERT INTO orders (customer_id, amount, status) VALUES
    (1, 150.00, 'completed'),
    (1, 250.00, 'completed'),
    (2, 300.00, 'pending'),
    (3, 120.00, 'completed'),
    (4, 450.00, 'completed'),
    (5, 200.00, 'shipped');

-- Vérifier les données
SELECT * FROM customers;
SELECT * FROM orders;
```

---

## الخطوة 3: تكوين وجهة MinIO S3

### إنشاء وجهة

1. ** انتقل إلى الوجهات **
   - اضغط على "الوجهات" في القائمة اليسرى
   - اضغط على "+ وجهة جديدة"

2. **اختر S3**
   - ابحث عن "S3"
   - انقر على الرابط "S3".

3. ** تكوين MinIO كـ S3 **
   ```yaml
   Destination name: MinIO Data Lake
   S3 Bucket Name: datalake
   S3 Bucket Path: raw-data
   S3 Bucket Region: us-east-1
   S3 Endpoint: http://minio:9000
   Access Key ID: minioadmin
   Secret Access Key: minioadmin123
   
   Output Format:
     Format Type: Parquet
     Compression: GZIP
     Block Size (Row Group Size): 128 MB
   ```

4. **اختبر واحفظ**
   - انقر على "إعداد الوجهة"
   - يجب أن يجتاز اختبار الاتصال ✅

---

## الخطوة 4: أنشئ اتصالك الأول

### ربط المصدر بالوجهة

1. ** انتقل إلى الاتصالات **
   - انقر على "اتصالات" في القائمة اليسرى
   - اضغط على "+ اتصال جديد"

2. **اختر المصدر**
   - اختر "إنتاج PostgreSQL"
   - انقر على "استخدام المصدر الموجود"

3. **اختر الوجهة**
   - اختر "MinIO Data Lake"
   - انقر على "استخدام الوجهة الحالية"

4. **تكوين المزامنة**
   ```yaml
   Connection name: PostgreSQL → MinIO
   Replication frequency: Every 24 hours at 02:00
   Destination Namespace: Custom format
     Format: production_${SOURCE_NAMESPACE}
   
   Streams to sync:
     ☑ customers
       Sync mode: Full Refresh | Overwrite
       Primary key: customer_id
       Cursor field: created_at
       
     ☑ orders
       Sync mode: Incremental | Append
       Primary key: order_id
       Cursor field: order_date
   ```

5. **التطبيع**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. ** النسخ الاحتياطي والمزامنة **
   - انقر على "إعداد الاتصال"
   - انقر على "المزامنة الآن" لتنفيذ المزامنة الأولى
   - مراقبة تقدم المزامنة

### مراقبة التزامن

```mermaid
sequenceDiagram
    participant PG as PostgreSQL
    participant AB as Airbyte Worker
    participant S3 as MinIO S3
    
    AB->>PG: 1. Extraction: SELECT * FROM customers
    PG->>AB: 2. Retour données (5 lignes)
    AB->>AB: 3. Transformation en Parquet
    AB->>S3: 4. Téléversement vers datalake/raw-data/
    
    AB->>PG: 5. Extraction: SELECT * FROM orders WHERE order_date > last_sync
    PG->>AB: 6. Retour nouvelles données
    AB->>AB: 7. Transformation en Parquet
    AB->>S3: 8. Téléversement vers datalake/raw-data/
    
    Note over AB: Synchronisation Terminée ✅
```

**التحقق من حالة المزامنة:**
- يجب أن تظهر الحالة "تم النجاح" (باللون الأخضر)
- السجلات المتزامنة: ~11 (5 عملاء + 6 طلبات)
- انظر السجلات للحصول على التفاصيل

---

## الخطوة 5: قم بتوصيل Dremio بـ MinIO

### أضف مصدر S3 في Drimio

1. ** انتقل إلى المصادر **
   - افتح http://localhost:9047
   - انقر على "إضافة مصدر" (+ أيقونة)

2. **اختر S3**
   - اختر "أمازون S3"
   - التكوين كـ MinIO:

```yaml
General:
  Name: MinIOLake

Connection:
  Authentication: AWS Access Key
  AWS Access Key: minioadmin
  AWS Secret Key: minioadmin123
  
  Encrypt connection: No
  
Advanced Options:
  Connection Properties:
    fs.s3a.path.style.access: true
    fs.s3a.endpoint: minio:9000
    dremio.s3.compat: true
  
  Root Path: /
  
  Enable compatibility mode: Yes
```

3. **اختبر واحفظ**
   - اضغط على "حفظ"
   - سيقوم Dremio بتحليل مجموعات MinIO

### تصفح البيانات

1. ** انتقل إلى مصدر MinIOLake **
   - تطوير "MinIOLake"
   - تطوير دلو "datalake".
   - قم بتوسيع مجلد "البيانات الأولية".
   - راجع المجلد "production_public".

2. **معاينة البيانات**
   - اضغط على مجلد "العملاء".
   - اضغط على ملف الباركيه
   - اضغط على "معاينة" لرؤية البيانات
   - يجب أن تتطابق البيانات مع PostgreSQL ✅

### إنشاء مجموعة بيانات افتراضية

1. **بيانات الاستعلام**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **حفظ باسم VDS**
   - اضغط على "حفظ العرض باسم"
   - الاسم: `vw_customers`
   - المساحة: `@admin` (مساحتك الخاصة)
   - اضغط على "حفظ"

3. **تنسيق البيانات** (اختياري)
   - اضغط على `vw_customers`
   - استخدم الواجهة لإعادة تسمية الأعمدة وتغيير الأنواع
   - مثال: أعد تسمية `customer_id` إلى `id`

---

## الخطوة 6: إنشاء قوالب dbt

### تهيئة مشروع dbt

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate  # Windows

# Naviguer vers le répertoire dbt
cd dbt

# Tester la connexion
dbt debug

# Devrait afficher: "All checks passed!"
```

### إنشاء تعريف المصدر

**الملف**: `dbt/models/sources.yml`

```yaml
version: 2

sources:
  - name: airbyte_raw
    description: Données brutes des synchronisations Airbyte
    database: MinIOLake.datalake."raw-data".production_public
    tables:
      - name: customers
        description: Données maîtres clients
        columns:
          - name: customer_id
            description: Identifiant unique du client
            tests:
              - unique
              - not_null
          - name: email
            tests:
              - unique
              - not_null
      
      - name: orders
        description: Transactions de commandes
        columns:
          - name: order_id
            description: Identifiant unique de la commande
            tests:
              - unique
              - not_null
          - name: customer_id
            description: Clé étrangère vers customers
            tests:
              - not_null
              - relationships:
                  to: source('airbyte_raw', 'customers')
                  field: customer_id
```

### إنشاء قالب التدريج

**الملف**: `dbt/models/staging/stg_customers.sql`

```sql
-- Modèle de staging: Nettoyer et standardiser les données clients

{{ config(
    materialized='view',
    schema='staging'
) }}

with source as (
    select * from {{ source('airbyte_raw', 'customers') }}
),

cleaned as (
    select
        customer_id,
        trim(name) as customer_name,
        lower(trim(email)) as email,
        upper(trim(country)) as country_code,
        created_at,
        current_timestamp() as dbt_loaded_at
    from source
)

select * from cleaned
```

**الملف**: `dbt/models/staging/stg_orders.sql`

```sql
-- Modèle de staging: Nettoyer et standardiser les données de commandes

{{ config(
    materialized='view',
    schema='staging'
) }}

with source as (
    select * from {{ source('airbyte_raw', 'orders') }}
),

cleaned as (
    select
        order_id,
        customer_id,
        amount,
        lower(trim(status)) as order_status,
        order_date,
        current_timestamp() as dbt_loaded_at
    from source
    where amount > 0  -- Filtre de qualité des données
)

select * from cleaned
```

### إنشاء قالب مارت

**الملف**: `dbt/models/marts/fct_customer_orders.sql`

```sql
-- Table de faits: Résumé des commandes clients

{{ config(
    materialized='table',
    schema='marts'
) }}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_metrics as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount) as total_spent,
        avg(amount) as avg_order_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        sum(case when order_status = 'completed' then 1 else 0 end) as completed_orders
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.country_code,
        c.created_at as customer_since,
        
        coalesce(m.total_orders, 0) as total_orders,
        coalesce(m.total_spent, 0) as lifetime_value,
        coalesce(m.avg_order_value, 0) as avg_order_value,
        m.first_order_date,
        m.last_order_date,
        coalesce(m.completed_orders, 0) as completed_orders,
        
        datediff('day', m.last_order_date, current_date()) as days_since_last_order,
        
        case
            when m.total_orders >= 5 then 'VIP'
            when m.total_orders >= 2 then 'Regular'
            else 'New'
        end as customer_segment
        
    from customers c
    left join customer_metrics m on c.customer_id = m.customer_id
)

select * from final
```

### تشغيل نماذج dbt

```bash
# Exécuter tous les modèles
dbt run

# Devrait afficher:
# Completed successfully
# Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3

# Exécuter les tests
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve  # Ouvre le navigateur sur localhost:8080
```

### تحقق في دريميو

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## الخطوة 7: إنشاء لوحة معلومات في Superset

### إضافة قاعدة بيانات دريميو

1. ** انتقل إلى قواعد البيانات **
   - افتح http://localhost:8088
   - انقر على "البيانات" ← "قواعد البيانات"
   - اضغط على "+ قاعدة البيانات"

2. **اختر دريميو**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **انقر على "اتصال"**

### إنشاء مجموعة بيانات

1. ** انتقل إلى مجموعات البيانات **
   - انقر على "البيانات" ← "مجموعات البيانات"
   - اضغط على "+ مجموعة البيانات"

2. **تكوين مجموعة البيانات**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **انقر على "إنشاء مجموعة بيانات وإنشاء مخطط"**

### إنشاء الرسوم البيانية

#### الرسم البياني 1: شرائح العملاء (مخطط دائري)

```yaml
Chart Type: Pie Chart
Datasource: fct_customer_orders

Dimensions:
  - customer_segment

Metrics:
  - COUNT(customer_id)

Filters: Aucun

Chart Options:
  Show Labels: Yes
  Show Legend: Yes
```

#### الرسم البياني 2: الدخل حسب الدولة (مخطط شريطي)

```yaml
Chart Type: Bar Chart
Datasource: fct_customer_orders

Dimensions:
  - country_code

Metrics:
  - SUM(lifetime_value)

Sort by: SUM(lifetime_value) DESC
Limit: 10

Chart Options:
  Show Labels: Yes
  Color Scheme: Superset Colors
```

#### الرسم البياني 3: مقاييس العملاء (عدد كبير)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### إنشاء لوحة التحكم

1. **انتقل إلى لوحات المعلومات**
   - انقر على "لوحات المعلومات"
   - اضغط على "+ لوحة التحكم"

2. **تكوين لوحة المعلومات**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **إضافة الرسومات**
   - قم بسحب وإسقاط الرسومات التي تم إنشاؤها
   - التنظيم في الشبكة:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **إضافة عوامل التصفية** (اختياري)
   - اضغط على "إضافة فلتر"
   - التصفية حسب: رمز البلد
   - تنطبق على جميع الرسوم البيانية

5. **حفظ لوحة المعلومات**

---

## الخطوة 8: التحقق من خط الأنابيب الكامل

### الاختبار الشامل

```mermaid
graph LR
    A[PostgreSQL<br/>Données Source] -->|Sync Airbyte| B[MinIO S3<br/>Données Brutes]
    B -->|Requête Dremio| C[dbt<br/>Transformations]
    C -->|Écriture| D[Dremio<br/>Marts]
    D -->|Requête SQL| E[Superset<br/>Tableau de Bord]
    
    style A fill:#336791,color:#fff
    style B fill:#C72E49,color:#fff
    style C fill:#FF694B,color:#fff
    style D fill:#FDB515
    style E fill:#20A7C9,color:#fff
```

### إضافة بيانات جديدة

1. **أدخل سجلات جديدة في PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. ** تشغيل مزامنة Airbyte **
   - افتح واجهة Airbyte
   - انتقل إلى الاتصال "PostgreSQL → MinIO"
   - انقر على "المزامنة الآن"
   - انتظر النهاية ✅

3. ** تشغيل دي بي تي **
   ```bash
   cd dbt
   dbt run
   ```

4. **تحديث لوحة معلومات Superset**
   - افتح لوحة القيادة
   - انقر على زر "تحديث".
   - يجب أن تظهر البيانات الجديدة ✅

### التحقق من تدفق البيانات

```sql
-- Dans Dremio SQL Runner

-- 1. Vérifier les données brutes d'Airbyte
SELECT COUNT(*) as raw_customers
FROM MinIOLake.datalake."raw-data".production_public.customers;
-- Devrait retourner: 7

-- 2. Vérifier la vue de staging
SELECT COUNT(*) as staged_customers
FROM "@admin".staging.stg_customers;
-- Devrait retourner: 7

-- 3. Vérifier la table mart
SELECT
    customer_segment,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_revenue
FROM "@admin".marts.fct_customer_orders
GROUP BY customer_segment
ORDER BY total_revenue DESC;
```

---

## الخطوة 9: أتمتة خط الأنابيب

### جدولة مزامنة Airbyte

تمت تهيئته بالفعل للتشغيل كل 24 ساعة في الساعة 02:00.

للتحرير:
1. افتح الاتصال في Airbyte
2. انتقل إلى علامة التبويب "الإعدادات".
3. تحديث "تكرار النسخ المتماثل"
4. احفظ

### جدولة عمليات تنفيذ dbt

**الخيار 1: وظيفة كرون (لينكس)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**الخيار 2: نص بايثون**

**الملف**: `scripts/run_pipeline.py`
```python
#!/usr/bin/env python3
"""
Exécution automatisée du pipeline
Exécute les modèles dbt après la synchronisation Airbyte
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_dbt():
    """Exécuter les modèles dbt"""
    dbt_dir = Path(__file__).parent.parent / 'dbt'
    
    logger.info("Exécution des modèles dbt...")
    result = subprocess.run(
        ['dbt', 'run'],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("Exécution dbt terminée avec succès")
        return True
    else:
        logger.error(f"Échec exécution dbt: {result.stderr}")
        return False

if __name__ == '__main__':
    success = run_dbt()
    exit(0 if success else 1)
```

### الجدول الزمني باستخدام Docker Compose

**الملف**: `docker-compose.scheduler.yml`
```yaml
version: '3.8'

services:
  dbt-scheduler:
    image: ghcr.io/dbt-labs/dbt-core:1.10.0
    volumes:
      - ./dbt:/usr/app/dbt
    command: >
      sh -c "while true; do
        dbt run --profiles-dir /usr/app/dbt;
        sleep 3600;
      done"
    networks:
      - dremio_network
```

---

## الخطوات التالية

تهانينا! لقد قمت ببناء خط أنابيب بيانات كامل من البداية إلى النهاية. 🎉

### يتعلم أكثر

1. **Airbyte Advanced** - [دليل تكامل Airbyte](../guides/airbyte-integration.md)
2. **تحسين Dremio** - [دليل إعداد Dremio](../guides/dremio-setup.md)
3. **نماذج dbt المعقدة** - [دليل تطوير dbt](../guides/dbt-development.md)
4. **لوحات المعلومات المتقدمة** - [دليل لوحات المعلومات Superset](../guides/superset-dashboards.md)
5. **جودة البيانات** - [دليل جودة البيانات](../guides/data-quality.md)

### استكشاف الأخطاء وإصلاحها

إذا كان لديك مشاكل، راجع:
- [دليل استكشاف الأخطاء وإصلاحها](../guides/troubleshooting.md)
- [دليل التثبيت](installation.md#troubleshooting)
- [دليل التكوين](configuration.md)

---

## ملخص

لقد نجحت في:

- ✅ الوصول إلى 7 خدمات للمنصة
- ✅ تكوين مصدر Airbyte (PostgreSQL)
- ✅ تكوين وجهة Airbyte (MinIO S3)
- ✅ قم بإنشاء أول اتصال Airbyte الخاص بك
- ✅ قم بتوصيل Drimio إلى MinIO
- ✅ إنشاء قوالب dbt (التدريج + الأسواق)
- ✅ إنشاء لوحة تحكم Superset
- ✅ التحقق من تدفق البيانات من طرف إلى طرف
- ✅ أتمتة تنفيذ خطوط الأنابيب

**منصة البيانات الخاصة بك جاهزة للعمل الآن!** 🚀

---

**إصدار دليل الخطوات الأولى**: 3.2.0  
**آخر تحديث**: 16-10-2025  
** تتم صيانته بواسطة **: فريق منصة البيانات