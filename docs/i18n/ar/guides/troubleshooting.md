# دليل استكشاف الأخطاء وإصلاحها

**الإصدار**: 3.2.0  
**آخر تحديث**: 16 أكتوبر 2025  
**اللغة**: الفرنسية

## جدول المحتويات

1. [نظرة عامة](#overview)
2. [النهج العام لاستكشاف الأخطاء وإصلاحها](#general-troubleshooting-approach)
3. [مشاكل Airbyte](#airbyte-problems)
4. [مشاكل دريميو](#مشاكل دريميو)
5. [مشاكل dbt](#مشاكل-dbt)
6. [مشكلات المجموعة الشاملة](#مشاكل المجموعة الشاملة)
7. [مشاكل PostgreSQL](#postgresql-problems)
8. [مشاكل MiniIO](#minio-problems)
9. [مشكلات البحث المرن](#elasticsearch-issues)
10. [الشبكة والاتصال](#الشبكة والاتصال)
11. [مشكلات الأداء](#مشكلات الأداء)
12. [مشكلات جودة البيانات](#مشكلات جودة البيانات)

---

## ملخص

يساعدك دليل استكشاف الأخطاء وإصلاحها الشامل هذا على تشخيص المشكلات الشائعة وحلها عبر جميع مكونات النظام الأساسي. يتم تنظيم المشكلات حسب المكونات مع أعراض وتشخيصات وحلول واضحة.

### منهجية استكشاف الأخطاء وإصلاحها

```mermaid
flowchart TB
    A[Problème signalé] --> B[Identifier les symptômes]
    B --> C[Vérifier les logs]
    C --> D[Isoler le composant]
    D --> E{Problème connu?}
    E -->|Oui| F[Appliquer la solution]
    E -->|Non| G[Déboguer davantage]
    G --> H[Vérifier les dépendances]
    H --> I[Tester la solution]
    F --> I
    I --> J{Résolu?}
    J -->|Oui| K[Documenter la solution]
    J -->|Non| L[Escalader]
    
    style A fill:#e1f5ff
    style F fill:#4CAF50,color:#fff
    style K fill:#4CAF50,color:#fff
    style L fill:#FF6B6B
```

---

## النهج العام لاستكشاف الأخطاء وإصلاحها

### الخطوة 1: التحقق من حالة الخدمات

```bash
# Check all Docker containers
docker-compose ps

# Expected output:
#   airbyte-server     Up       0.0.0.0:8001->8001/tcp
#   airbyte-webapp     Up       0.0.0.0:8000->80/tcp
#   dremio             Up       0.0.0.0:9047->9047/tcp
#   superset           Up       0.0.0.0:8088->8088/tcp
#   postgres           Up       0.0.0.0:5432->5432/tcp
#   minio              Up       0.0.0.0:9000-9001->9000-9001/tcp
#   elasticsearch      Up       0.0.0.0:9200->9200/tcp
```

### الخطوة 2: التحقق من السجلات

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### الخطوة 3: التحقق من اتصال الشبكة

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### الخطوة 4: التحقق من استخدام الموارد

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### الإصلاحات السريعة الشائعة

```bash
# Restart specific service
docker-compose restart [service_name]

# Restart all services
docker-compose restart

# Full cleanup and restart
docker-compose down
docker-compose up -d

# Remove volumes and start fresh (⚠️ data loss!)
docker-compose down -v
docker-compose up -d
```

---

## قضايا إيربايت

### المشكلة الأولى: عدم تحميل واجهة Airbyte

**أعراض** :
- يعرض المتصفح رسالة "لا يمكن الاتصال" أو انتهاء المهلة
- URL: `http://localhost:8000` لا يستجيب

**تشخبص**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**الحلول**:

1. **تأكد من أن المنفذ ليس قيد الاستخدام**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **إعادة تشغيل حاويات Airbyte**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **التحقق من سلامة الخادم**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### المشكلة الثانية: فشل المزامنة مع "مهلة الاتصال"

**أعراض** :
- تفشل مهمة المزامنة أو تتوقف على الفور
- خطأ: "انتهت مهلة الاتصال" أو "غير قادر على الاتصال بالمصدر"

**تشخبص**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**الحلول**:

1. **التحقق من معرفات المصدر**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **زيادة المهلة**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **التحقق من الشبكة**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### المشكلة 3: نفاد الذاكرة أثناء المزامنة

**أعراض** :
- تعطل عامل الحاوية أثناء عمليات المزامنة الكبيرة
- خطأ: "OutOfMemoryError" أو "مساحة كومة Java"

**تشخبص**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**الحلول**:

1. **زيادة ذاكرة العامل**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **تقليل حجم الدفعة**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **استخدم المزامنة المتزايدة**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### المشكلة 4: لا تظهر البيانات في الوجهة

**أعراض** :
- اكتملت المزامنة بنجاح
- لا توجد أخطاء في السجلات
- البيانات ليست في MiniIO/الوجهة

**تشخبص**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**الحلول**:

1. **تحقق من تكوين الوجهة**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **التحقق من التطبيع**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **التحقق اليدوي**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## مشاكل دريميو

### المشكلة 1: غير قادر على الاتصال بواجهة Dremio

**أعراض** :
- يظهر المتصفح خطأ في الاتصال في `http://localhost:9047`

**تشخبص**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**الحلول**:

1. **انتظر حتى اكتمال بدء التشغيل** (قد يستغرق الأمر من 2 إلى 3 دقائق):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **زيادة الذاكرة**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **تنظيف بيانات Dremio** (⚠️ إعادة ضبط التكوين):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### المشكلة الثانية: "المصدر غير المتصل" لـ MinIO

**أعراض** :
- يعرض مصدر MinIO مؤشر "غير متصل" باللون الأحمر
- خطأ: "غير قادر على الاتصال بالمصدر"

**تشخبص**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**الحلول**:

1. **تحقق من نقطة نهاية MinIO**:
   ```json
   {
     "config": {
       "propertyList": [
         {
           "name": "fs.s3a.endpoint",
           "value": "minio:9000"  // Not localhost!
         },
         {
           "name": "fs.s3a.path.style.access",
           "value": "true"
         }
       ]
     }
   }
   ```

2. **التحقق من بيانات الاعتماد**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **تحديث البيانات الوصفية**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### المشكلة 3: أداء الاستعلام بطيء

**أعراض** :
- الاستعلامات تستغرق أكثر من 10 ثواني
- لوحات المعلومات بطيئة في التحميل

**تشخبص**:
```sql
-- Check query profile
SELECT * FROM sys.jobs 
WHERE execution_time_ms > 10000
ORDER BY start_time DESC
LIMIT 10;

-- Check if reflection was used
SELECT 
    query_text,
    acceleration_profile.accelerated
FROM sys.jobs
WHERE job_id = 'your-job-id';
```

**الحلول**:

1. **إنشاء انعكاسات**:
   ```sql
   -- Create raw reflection
   CREATE REFLECTION raw_customers
   ON Production.Dimensions.dim_customers
   USING DISPLAY (customer_id, name, email, lifetime_value);
   
   -- Create aggregation reflection
   CREATE REFLECTION agg_daily_revenue
   ON Production.Facts.fct_orders
   USING DIMENSIONS (order_date)
   MEASURES (SUM(amount), COUNT(*));
   ```

2. **إضافة عوامل تصفية الأقسام**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **زيادة ذاكرة المنفذ**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### المشكلة الرابعة: التأمل لا يبني

**أعراض** :
- يظل الانعكاس عالقًا في حالة "التحديث".
- لا ينتهي أبدا

**تشخبص**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**الحلول**:

1. **التعطيل وإعادة التمكين**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **التحقق من بيانات المصدر**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **زيادة المهلة**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## مشاكل دي بي تي

### المشكلة 1: "خطأ في الاتصال" عند تشغيل dbt

**أعراض** :
- `dbt debug` فشل
- خطأ: "تعذر الاتصال بـ Dremio"

**تشخبص**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**الحلول**:

1. **تحقق من ملف Profiles.yml**:
   ```yaml
   dremio_project:
     target: dev
     outputs:
       dev:
         type: dremio
         host: localhost  # or dremio container name
         port: 9047
         username: admin
         password: your_password
         use_ssl: false
   ```

2. **اختبار اتصال Drimio**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **قم بتثبيت محول Dremio**:
   ```bash
   pip install dbt-dremio
   ```

### المشكلة الثانية: فشل بناء النموذج

**أعراض** :
- `dbt run` فشل في نموذج محدد
- خطأ في تجميع SQL أو التنفيذ

**تشخبص**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**الحلول**:

1. **التحقق من بناء جملة النموذج**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **الاختبار أولاً في SQL IDE**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **التحقق من التبعيات**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### المشكلة 3: فشل الاختبارات

**أعراض** :
- `dbt test` تقارير الفشل
- تم اكتشاف مشاكل في جودة البيانات

**تشخبص**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**الحلول**:

1. **تصحيح بيانات المصدر**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **ضبط حد الاختبار**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **التحقق من السبب الجذري**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### المشكلة 4: النموذج التزايدي لا يعمل

**أعراض** :
- يتم إعادة بناء النموذج التزايدي بالكامل في كل مرة يتم تشغيله
- لا يوجد سلوك تدريجي

**تشخبص**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**الحلول**:

1. **إضافة متطلبات النظام**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. ** إضافة منطق تزايدي **:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **فرض التحديث الكامل مرة واحدة**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## مشاكل المجموعة الفائقة

### المشكلة 1: غير قادر على الاتصال بـ Superset

**أعراض** :
- تعرض صفحة تسجيل الدخول "بيانات اعتماد غير صالحة"
- زوج المسؤول/المسؤول الافتراضي لا يعمل

**تشخبص**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**الحلول**:

1. **إعادة تعيين كلمة مرور المسؤول**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **إنشاء مستخدم إداري**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **إعادة ضبط المجموعة الفائقة**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### المشكلة 2: فشل الاتصال بقاعدة البيانات

**أعراض** :
- فشل زر "اختبار الاتصال".
- خطأ: "لا يمكن الاتصال بقاعدة البيانات"

**تشخبص**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**الحلول**:

1. **استخدم عنوان URI الصحيح لـ SQLAlchemy**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **تثبيت برامج التشغيل المطلوبة**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **التحقق من الشبكة**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### المشكلة 3: عدم تحميل المخططات

**أعراض** :
- تعرض لوحة المعلومات أداة التحميل الدوارة إلى أجل غير مسمى
- تعرض الرسوم البيانية "خطأ في تحميل البيانات"

**تشخبص**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**الحلول**:

1. **التحقق من مهلة الاستعلام**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **تمكين الطلبات غير المتزامنة**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **مسح ذاكرة التخزين المؤقت**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### المشكلة 4: أخطاء الأذونات

**أعراض** :
- لا يمكن للمستخدم رؤية لوحات المعلومات
- خطأ: "ليس لديك حق الوصول إلى لوحة التحكم هذه"

**تشخبص**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**الحلول**:

1. **أضف المستخدم إلى الدور**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **منح حق الوصول إلى لوحة التحكم**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **تحقق من قواعد RLS**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## مشكلات PostgreSQL

### المشكلة 1: تم رفض الاتصال

**أعراض** :
- لا يمكن للتطبيقات الاتصال بـ PostgreSQL
- خطأ: "تم رفض الاتصال" أو "تعذر الاتصال"

**تشخبص**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**الحلول**:

1. **إعادة تشغيل PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

2. **التحقق من تعيين المنفذ**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **التحقق من بيانات الاعتماد**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### المشكلة الثانية: عدم وجود اتصالات

**أعراض** :
- خطأ: "فادح: فتحات الاتصال المتبقية محجوزة"
- فشل التطبيقات في الاتصال بشكل متقطع

**تشخبص**:
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- List active connections
SELECT pid, usename, application_name, client_addr
FROM pg_stat_activity
WHERE state = 'active';
```

**الحلول**:

1. **زيادة الحد الأقصى لعدد الاتصالات**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **استخدام تجمع الاتصالات**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **إيقاف الاتصالات الخاملة**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### المشكلة 3: الاستعلامات البطيئة

**أعراض** :
- تستغرق استعلامات قاعدة البيانات عدة ثوانٍ
- تنتهي صلاحية التطبيقات

**تشخبص**:
```sql
-- Find slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - pg_stat_activity.query_start > interval '5 seconds'
ORDER BY duration DESC;

-- Check if indexes exist
SELECT tablename, indexname FROM pg_indexes
WHERE schemaname = 'public';
```

**الحلول**:

1. **إنشاء فهارس**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **تشغيل التحليل**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **زيادة المخازن المؤقتة المشتركة**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##مشكلات MiniIO

### المشكلة 1: غير قادر على الوصول إلى وحدة تحكم MinIO

**أعراض** :
- يعرض المتصفح خطأ في `http://localhost:9001`

**تشخبص**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**الحلول**:

1. **التحقق من المنافذ**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **الوصول إلى عنوان URL الصحيح**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **إعادة تشغيل MiniIO**:
   ```bash
   docker-compose restart minio
   ```

### المشكلة 2: أخطاء رفض الوصول

**أعراض** :
- لا يمكن للتطبيقات القراءة/الكتابة إلى S3
- خطأ: "تم رفض الوصول" أو "403 محظور"

**تشخبص**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**الحلول**:

1. **التحقق من بيانات الاعتماد**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **التحقق من سياسة المجموعة**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **إنشاء مفتاح وصول للتطبيق**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### المشكلة 3: لم يتم العثور على الجرافة

**أعراض** :
- خطأ: "المجموعة المحددة غير موجودة"

**تشخبص**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**الحلول**:

1. **إنشاء الدلو**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **تحقق من اسم المجموعة في التكوين**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## الشبكة والاتصال

### المشكلة: لا يمكن للخدمات التواصل

**أعراض** :
- "تم رفض الاتصال" بين الحاويات
- أخطاء "لم يتم العثور على المضيف".

**تشخبص**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**الحلول**:

1. **تأكد من وجود جميع الخدمات على نفس الشبكة**:
   ```yaml
   # docker-compose.yml
   services:
     airbyte-server:
       networks:
         - data-platform
     postgres:
       networks:
         - data-platform
   
   networks:
     data-platform:
       driver: bridge
   ```

2. **استخدم أسماء الحاويات، وليس المضيف المحلي**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **إعادة إنشاء الشبكة**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## مشكلات الأداء

### المشكلة: الاستخدام العالي لوحدة المعالجة المركزية

**تشخبص**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**الحلول**:

1. **الحد من الطلبات المتنافسة**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **تحسين الاستعلامات** (راجع [مشكلات Dremio](#dremio-issues))

3. **زيادة تخصيص وحدة المعالجة المركزية**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### المشكلة: استخدام الذاكرة العالية

**تشخبص**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**الحلول**:

1. **زيادة حجم الكومة**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **تمكين سكب القرص**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## قضايا جودة البيانات

راجع الحلول المفصلة في [دليل جودة البيانات](./data-quality.md).

### فحوصات سريعة

```sql
-- Check for duplicates
SELECT customer_id, COUNT(*)
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for nulls
SELECT COUNT(*) - COUNT(email) AS null_emails
FROM customers;

-- Check data freshness
SELECT MAX(updated_at) AS last_update
FROM orders;
```

---

## ملخص

يغطي دليل استكشاف الأخطاء وإصلاحها ما يلي:

- **المنهج العام**: منهجية منهجية لتشخيص المشكلات
- **المشاكل حسب المكونات**: حلول للخدمات السبعة للمنصة
- **مشكلات الشبكة**: مشكلات الاتصال بالحاويات
- **مشكلات الأداء**: تحسين وحدة المعالجة المركزية والذاكرة والاستعلام
- **مشكلات جودة البيانات**: مشكلات البيانات وعمليات التحقق الشائعة

**الوجبات الرئيسية**:
- تحقق دائمًا من السجلات أولاً: `docker-compose logs [service]`
- استخدم أسماء الحاويات، وليس المضيف المحلي، للاتصال بين الخدمات
- اختبار الاتصال: `docker exec [container] ping [target]`
- مراقبة الموارد: `docker stats`
- البدء البسيط: أعد تشغيل الخدمة قبل إجراء التصحيح المعقد

**الوثائق ذات الصلة:**
- [دليل التثبيت](../getting-started/installation.md)
- [دليل التكوين](../getting-started/configuration.md)
- [دليل جودة البيانات](./data-quality.md)
- [الهندسة المعمارية: النشر](../architecture/deployment.md)

**هل تحتاج إلى المزيد من المساعدة؟**
- التحقق من سجلات المكونات: `docker-compose logs -f [service]`
- راجع وثائق الخدمة
- بحث قضايا جيثب
- الاتصال بفريق الدعم

---

**الإصدار**: 3.2.0  
**آخر تحديث**: 16 أكتوبر 2025