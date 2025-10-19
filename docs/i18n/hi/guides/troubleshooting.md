# समस्या निवारण मार्गदर्शिका

**संस्करण**: 3.2.0  
**अंतिम अद्यतन**: 16 अक्टूबर, 2025  
**भाषा**: फ्रेंच

## विषयसूची

1. [अवलोकन](#अवलोकन)
2. [सामान्य समस्या निवारण दृष्टिकोण](#सामान्य-समस्या निवारण-दृष्टिकोण)
3. [एयरबाइट समस्याएं](#एयरबाइट-समस्याएं)
4. [ड्रेमियो समस्याएं](#ड्रेमियो-समस्याएं)
5. [डीबीटी समस्याएं](#डीबीटी-समस्याएं)
6. [सुपरसेट समस्याएँ](#सुपरसेट-समस्याएँ)
7. [पोस्टग्रेएसक्यूएल समस्याएं](#पोस्टग्रेएसक्यूएल-समस्याएं)
8. [मिनियो समस्याएं](#मिनियो-समस्याएं)
9. [इलास्टिक्स खोज मुद्दे](#इलास्टिक्स खोज मुद्दे)
10. [नेटवर्क और कनेक्टिविटी](#नेटवर्क-और-कनेक्टिविटी)
11. [प्रदर्शन संबंधी मुद्दे](#प्रदर्शन-मुद्दे)
12. [डेटा गुणवत्ता संबंधी समस्याएं](#डेटा-गुणवत्ता-समस्याएं)

---

## अवलोकन

यह व्यापक समस्या निवारण मार्गदर्शिका आपको सभी प्लेटफ़ॉर्म घटकों में सामान्य समस्याओं का निदान और समाधान करने में मदद करती है। समस्याओं को स्पष्ट लक्षण, निदान और समाधान के साथ घटक द्वारा व्यवस्थित किया जाता है।

### समस्या निवारण पद्धति

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

## सामान्य समस्या निवारण दृष्टिकोण

### चरण 1: सेवाओं की स्थिति जांचें

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

### चरण 2: लॉग जाँचें

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### चरण 3: नेटवर्क कनेक्टिविटी की जाँच करें

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### चरण 4: संसाधन उपयोग की जाँच करें

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### सामान्य त्वरित सुधार

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

## एयरबाइट मुद्दे

### समस्या 1: एयरबाइट इंटरफ़ेस लोड नहीं हो रहा है

**लक्षण** :
- ब्राउज़र "कनेक्ट नहीं हो सकता" या टाइमआउट प्रदर्शित करता है
- यूआरएल: `http://localhost:8000` प्रतिसाद नहीं दे रहा

**निदान**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**समाधान**:

1. **जाँचें कि पोर्ट उपयोग में नहीं है**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **एयरबाइट कंटेनर पुनः आरंभ करें**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **जाँचें कि सर्वर ठीक है**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### समस्या 2: "कनेक्शन टाइमआउट" के साथ सिंक्रनाइज़ेशन विफल हो जाता है

**लक्षण** :
- सिंक कार्य तुरंत विफल हो जाता है या लटक जाता है
- त्रुटि: "कनेक्शन टाइमआउट" या "स्रोत से कनेक्ट करने में असमर्थ"

**निदान**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**समाधान**:

1. **स्रोत पहचानकर्ताओं की जाँच करें**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **समयबाह्य बढ़ाएँ**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **नेटवर्क जांचें**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### अंक 3: सिंक के दौरान स्मृति से बाहर

**लक्षण** :
- बड़े सिंक्रोनाइजेशन के दौरान कंटेनर वर्कर क्रैश हो जाता है
- त्रुटि: "OutOfMemoryError" या "Java heap space"

**निदान**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**समाधान**:

1. **कर्मचारी की याददाश्त बढ़ाएँ**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **बैच का आकार कम करें**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **वृद्धिशील सिंक्रनाइज़ेशन का उपयोग करें**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### समस्या 4: डेटा गंतव्य में दिखाई नहीं देता है

**लक्षण** :
-सिंक्रनाइज़ेशन सफलतापूर्वक पूरा हो गया
- लॉग में कोई त्रुटि नहीं
- डेटा मिनियो/गंतव्य में नहीं है

**निदान**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**समाधान**:

1. **गंतव्य कॉन्फ़िगरेशन की जाँच करें**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **सामान्यीकरण की जाँच करें**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **मैन्युअल सत्यापन**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## ड्रेमियो समस्याएँ

### समस्या 1: ड्रेमियो इंटरफ़ेस से कनेक्ट करने में असमर्थ

**लक्षण** :
- ब्राउज़र `http://localhost:9047` पर कनेक्शन त्रुटि दिखाता है

**निदान**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**समाधान**:

1. **पूर्ण स्टार्टअप की प्रतीक्षा करें** (2-3 मिनट लग सकते हैं):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **याददाश्त बढ़ाएँ**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **ड्रेमियो डेटा साफ़ करें** (⚠️ कॉन्फ़िगरेशन रीसेट करता है):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### समस्या 2: मिनिओ के लिए "ऑफ़लाइन स्रोत"।

**लक्षण** :
- मिनिओ स्रोत एक लाल "ऑफ़लाइन" संकेतक प्रदर्शित करता है
- त्रुटि: "स्रोत से कनेक्ट करने में असमर्थ"

**निदान**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**समाधान**:

1. **मिनियो एंडपॉइंट की जाँच करें**:
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

2. **प्रमाणपत्र जांचें**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **मेटाडेटा ताज़ा करें**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### अंक 3: धीमा क्वेरी प्रदर्शन

**लक्षण** :
- क्वेरीज़ में 10+ सेकंड लगते हैं
- डैशबोर्ड लोड होने में धीमे हैं

**निदान**:
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

**समाधान**:

1. **प्रतिबिंब बनाएँ**:
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

2. **विभाजन फ़िल्टर जोड़ें**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **निष्पादक मेमोरी बढ़ाएँ**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### समस्या 4: प्रतिबिंब नहीं बनता

**लक्षण** :
-प्रतिबिंब "ताज़ा" अवस्था में अटका रहता है
- कभी समाप्त नहीं होती

**निदान**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**समाधान**:

1. **अक्षम करें और पुनः सक्षम करें**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **स्रोत डेटा की जाँच करें**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **समयबाह्य बढ़ाएँ**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## डीबीटी समस्याएं

### समस्या 1: डीबीटी चलाते समय "कनेक्शन त्रुटि"।

**लक्षण** :
- `dbt debug` विफल
- त्रुटि: "ड्रेमियो से कनेक्ट नहीं हो सका"

**निदान**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**समाधान**:

1. **प्रोफ़ाइल जांचें.yml**:
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

2. **ड्रेमियो कनेक्टिविटी का परीक्षण करें**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **ड्रेमियो एडाप्टर स्थापित करें**:
   ```bash
   pip install dbt-dremio
   ```

### समस्या 2: मॉडल बनने में विफल

**लक्षण** :
- `dbt run` एक विशिष्ट मॉडल के लिए विफल रहता है
- SQL संकलन या निष्पादन त्रुटि

**निदान**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**समाधान**:

1. **मॉडल सिंटैक्स जांचें**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **पहले SQL IDE में परीक्षण करें**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **निर्भरताओं की जांच करें**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### समस्या 3: परीक्षण विफल

**लक्षण** :
- `dbt test` विफलताओं की रिपोर्ट करता है
- डेटा गुणवत्ता संबंधी समस्याओं का पता चला

**निदान**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**समाधान**:

1. **स्रोत डेटा को सही करें**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **परीक्षण सीमा समायोजित करें**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **मूल कारण की जांच करें**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### समस्या 4: वृद्धिशील मॉडल काम नहीं करता

**लक्षण** :
- वृद्धिशील मॉडल को हर बार चलाने पर पूरी तरह से पुनर्निर्मित किया जाता है
- कोई वृद्धिशील व्यवहार नहीं

**निदान**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**समाधान**:

1. **सिस्टम आवश्यकताएँ जोड़ें**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **वृद्धिशील तर्क जोड़ें**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **एक बार पूर्ण रीफ्रेश को बाध्य करें**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## सुपरसेट समस्याएँ

### समस्या 1: सुपरसेट से कनेक्ट करने में असमर्थ

**लक्षण** :
- लॉगिन पृष्ठ "अमान्य क्रेडेंशियल" प्रदर्शित करता है
- डिफ़ॉल्ट एडमिन/एडमिन जोड़ी काम नहीं करती

**निदान**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**समाधान**:

1. **एडमिन पासवर्ड रीसेट करें**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **एक व्यवस्थापक उपयोगकर्ता बनाएँ**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **सुपरसेट रीसेट करें**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### अंक 2: डेटाबेस कनेक्शन विफल

**लक्षण** :
- "टेस्ट कनेक्शन" बटन विफल रहता है
- त्रुटि: "डेटाबेस से कनेक्ट नहीं हो सकता"

**निदान**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**समाधान**:

1. **सही SQLAlchemy URI का उपयोग करें**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **आवश्यक ड्राइवर स्थापित करें**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **नेटवर्क जांचें**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### अंक 3: चार्ट लोड नहीं हो रहे हैं

**लक्षण** :
- डैशबोर्ड एक लोडिंग स्पिनर को अनिश्चित काल तक प्रदर्शित करता है
- चार्ट "डेटा लोड करने में त्रुटि" प्रदर्शित करते हैं

**निदान**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**समाधान**:

1. **क्वेरी टाइमआउट जांचें**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **अतुल्यकालिक अनुरोध सक्षम करें**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **कैश साफ़ करें**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### समस्या 4: अनुमतियाँ त्रुटियाँ

**लक्षण** :
- उपयोगकर्ता डैशबोर्ड नहीं देख सकता
- त्रुटि: "आपके पास इस डैशबोर्ड तक पहुंच नहीं है"

**निदान**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**समाधान**:

1. **उपयोगकर्ता को किसी भूमिका में जोड़ें**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **डैशबोर्ड तक पहुंच प्रदान करें**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **आरएलएस नियम जांचें**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## पोस्टग्रेएसक्यूएल मुद्दे

### समस्या 1: कनेक्शन अस्वीकृत

**लक्षण** :
- एप्लिकेशन PostgreSQL से कनेक्ट नहीं हो सकते
- त्रुटि: "कनेक्शन अस्वीकृत" या "कनेक्ट नहीं हो सका"

**निदान**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**समाधान**:

1. **पोस्टग्रेएसक्यूएल को पुनरारंभ करें**:
   ```bash
   docker-compose restart postgres
   ```

2. **पोर्ट मैपिंग जांचें**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **प्रमाणपत्र जांचें**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### समस्या 2: कनेक्शन का अभाव

**लक्षण** :
- त्रुटि: "घातक: शेष कनेक्शन स्लॉट आरक्षित हैं"
- ऐप्स रुक-रुक कर कनेक्ट होने में विफल रहते हैं

**निदान**:
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

**समाधान**:

1. **अधिकतम_कनेक्शन बढ़ाएँ**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **कनेक्शन पूलिंग का उपयोग करें**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **निष्क्रिय कनेक्शन समाप्त करें**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### समस्या 3: धीमी क्वेरीज़

**लक्षण** :
- डेटाबेस क्वेरीज़ में कई सेकंड लगते हैं
- ऐप्स समाप्त हो जाते हैं

**निदान**:
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

**समाधान**:

1. **अनुक्रमणिका बनाएं**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **विश्लेषण चलाएँ**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **शेयर्ड_बफ़र्स बढ़ाएँ**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##मिनियो मुद्दे

### समस्या 1: मिनियो कंसोल तक पहुँचने में असमर्थ

**लक्षण** :
- ब्राउज़र `http://localhost:9001` पर एक त्रुटि प्रदर्शित करता है

**निदान**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**समाधान**:

1. **पोर्ट की जाँच करें**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **सही यूआरएल तक पहुंचें**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **मिनियो को पुनरारंभ करें**:
   ```bash
   docker-compose restart minio
   ```

### अंक 2: प्रवेश अस्वीकृत त्रुटियाँ

**लक्षण** :
- एप्लिकेशन S3 को पढ़/लिख नहीं सकते
- त्रुटि: "प्रवेश निषेध" या "403 निषिद्ध"

**निदान**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**समाधान**:

1. **प्रमाणपत्र जांचें**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **बकेट नीति की जाँच करें**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **एप्लिकेशन के लिए एक एक्सेस कुंजी बनाएं**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### समस्या 3: बाल्टी नहीं मिली

**लक्षण** :
- त्रुटि: "निर्दिष्ट बाल्टी मौजूद नहीं है"

**निदान**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**समाधान**:

1. **बाल्टी बनाएँ**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **कॉन्फ़िगरेशन में बकेट का नाम जांचें**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## नेटवर्क और कनेक्टिविटी

### समस्या: सेवाएँ संचार नहीं कर सकतीं

**लक्षण** :
- कंटेनरों के बीच "कनेक्शन अस्वीकृत"।
- "होस्ट नहीं मिला" त्रुटियाँ

**निदान**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**समाधान**:

1. **सुनिश्चित करें कि सभी सेवाएँ एक ही नेटवर्क पर हैं**:
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

2. **कंटेनर नामों का उपयोग करें, लोकलहोस्ट का नहीं**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **नेटवर्क पुनः बनाएँ**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## निष्पादन मुद्दे

### समस्या: उच्च CPU उपयोग

**निदान**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**समाधान**:

1. **प्रतिस्पर्धी अनुरोधों को सीमित करें**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **प्रश्नों को अनुकूलित करें** (देखें [ड्रेमियो मुद्दे](#ड्रेमियो-मुद्दे))

3. **सीपीयू आवंटन बढ़ाएँ**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### समस्या: उच्च मेमोरी उपयोग

**निदान**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**समाधान**:

1. **ढेर का आकार बढ़ाएँ**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **डिस्क स्पिलिंग सक्षम करें**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## डेटा गुणवत्ता संबंधी समस्याएं

[डेटा गुणवत्ता गाइड](./data-quality.md) में विस्तृत समाधान देखें।

### त्वरित जाँच

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

## सारांश

इस समस्या निवारण मार्गदर्शिका में शामिल हैं:

- **सामान्य दृष्टिकोण**: समस्याओं के निदान के लिए व्यवस्थित पद्धति
- **घटक द्वारा समस्याएं**: प्लेटफ़ॉर्म की 7 सेवाओं के लिए समाधान
- **नेटवर्क समस्याएँ**: कंटेनर कनेक्टिविटी समस्याएँ
- **प्रदर्शन संबंधी समस्याएं**: सीपीयू, मेमोरी और क्वेरी अनुकूलन
- **डेटा गुणवत्ता संबंधी समस्याएं**: सामान्य डेटा समस्याएं और जांचें

**चाबी छीनना**:
- हमेशा पहले लॉग जांचें: `docker-compose logs [service]`
- अंतर-सेवा संचार के लिए कंटेनर नामों का उपयोग करें, लोकलहोस्ट का नहीं
- टेस्ट कनेक्टिविटी: `docker exec [container] ping [target]`
- मॉनिटर संसाधन: `docker stats`
- सरल शुरुआत करें: जटिल डिबगिंग से पहले सेवा को पुनरारंभ करें

**संबंधित दस्तावेज़:**
- [इंस्टालेशन गाइड](../getting-started/installation.md)
- [कॉन्फ़िगरेशन गाइड](../getting-started/configuration.md)
- [डेटा गुणवत्ता गाइड](./data-quality.md)
- [वास्तुकला: परिनियोजन](../आर्किटेक्चर/तैनाती.md)

**और अधिक मदद की आवश्यकता है?**
- घटक लॉग की जाँच करें: `docker-compose logs -f [service]`
- सेवा दस्तावेज़ से परामर्श लें
- GitHub मुद्दे खोजें
- सहायता टीम से संपर्क करें

---

**संस्करण**: 3.2.0  
**अंतिम अद्यतन**: 16 अक्टूबर, 2025