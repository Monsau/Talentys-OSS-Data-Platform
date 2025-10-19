# Sorun Giderme Kılavuzu

**Sürüm**: 3.2.0  
**Son güncelleme**: 16 Ekim 2025  
**Dil**: Fransızca

## İçindekiler

1. [Genel Bakış](#genel bakış)
2. [Genel sorun giderme yaklaşımı](#genel-sorun giderme-yaklaşımı)
3. [Airbyte sorunları](#airbyte sorunları)
4. [Dremio Sorunları](#dremio-problemleri)
5. [dbt sorunları](#dbt-problemleri)
6. [Süper Küme Problemleri](#süperküme-problemleri)
7. [PostgreSQL sorunları](#postgresql-problemleri)
8. [MinIO Sorunları](#minio-problemler)
9. [Elasticsearch sorunları](#elasticsearch-issues)
10. [Ağ ve Bağlantı](#ağ ve bağlantı)
11. [Performans sorunları](#performans sorunları)
12. [Veri kalitesi sorunları](#veri kalitesi sorunları)

---

## Genel Bakış

Bu kapsamlı sorun giderme kılavuzu, tüm platform bileşenlerinde sık karşılaşılan sorunları tanılamanıza ve çözmenize yardımcı olur. Sorunlar, açık belirtiler, teşhisler ve çözümler içeren bileşenlere göre düzenlenir.

### Sorun Giderme Metodolojisi

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

## Genel sorun giderme yaklaşımı

### 1. Adım: Hizmetlerin durumunu kontrol edin

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

### 2. Adım: Günlükleri kontrol edin

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### 3. Adım: Ağ bağlantısını kontrol edin

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### 4. Adım: Kaynak kullanımını kontrol edin

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Yaygın hızlı düzeltmeler

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

## Airbyte sorunları

### Sorun 1: Airbyte arayüzü yüklenmiyor

**Belirtiler**:
- Tarayıcıda "Bağlanamıyor" veya zaman aşımı görüntüleniyor
- URL: `http://localhost:8000` yanıt vermiyor

**Tanı**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Çözümler**:

1. **Bağlantı noktasının kullanımda olmadığını kontrol edin**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Airbyte Containers'ı yeniden başlatın**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Sunucunun sağlıklı olup olmadığını kontrol edin**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Sorun 2: Senkronizasyon "Bağlantı Zaman Aşımı" nedeniyle başarısız oluyor

**Belirtiler**:
- Senkronizasyon görevi hemen başarısız oluyor veya kilitleniyor
- Hata: "Bağlantı zaman aşımı" veya "Kaynağa bağlanılamıyor"

**Tanı**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Çözümler**:

1. **Kaynak tanımlayıcılarını kontrol edin**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Zaman aşımını artırın**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Ağı kontrol edin**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Sorun 3: Senkronizasyon sırasında bellek yetersiz

**Belirtiler**:
- Konteyner çalışanı büyük senkronizasyonlar sırasında çöküyor
- Hata: "OutOfMemoryError" veya "Java yığın alanı"

**Tanı**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Çözümler**:

1. **Çalışan hafızasını artırın**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Toplu iş boyutunu azaltın**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Artımlı senkronizasyonu kullanın**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Sorun 4: Veriler hedefte görünmüyor

**Belirtiler**:
- Senkronizasyon başarıyla tamamlandı
- Günlüklerde hata yok
- Veri MinIO/hedefte değil

**Tanı**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Çözümler**:

1. **Hedef yapılandırmasını kontrol edin**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Normalleştirmeyi kontrol edin**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Manuel doğrulama**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Dremio Sorunları

### Sorun 1: Dremio arayüzüne bağlanılamıyor

**Belirtiler**:
- Tarayıcı `http://localhost:9047` adresinde bağlantı hatası gösteriyor

**Tanı**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Çözümler**:

1. **Başlatmanın tamamlanmasını bekleyin** (2-3 dakika sürebilir):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Belleği artırın**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Dremio verilerini temizleyin** (⚠️ yapılandırmayı sıfırlar):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Sorun 2: MinIO için "Çevrimdışı Kaynak"

**Belirtiler**:
- MinIO kaynağı kırmızı bir "Çevrimdışı" göstergesi görüntüler
- Hata: "Kaynağa bağlanılamıyor"

**Tanı**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Çözümler**:

1. **MinIO uç noktasını kontrol edin**:
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

2. **Kimlik bilgilerini kontrol edin**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Meta verileri yenileyin**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Sorun 3: Yavaş sorgu performansı

**Belirtiler**:
- Sorgular 10+ saniye sürer
- Kontrol panellerinin yüklenmesi yavaş

**Tanı**:
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

**Çözümler**:

1. **Yansımalar oluşturun**:
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

2. **Bölüm filtreleri ekleyin**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Yürütücü hafızasını artırın**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Sorun 4: Yansıma oluşmuyor

**Belirtiler**:
- Yansıma "REFRESHING" durumunda takılı kalıyor
- Asla bitmez

**Tanı**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Çözümler**:

1. **Devre dışı bırakın ve yeniden etkinleştirin**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Kaynak verilerini kontrol edin**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Zaman aşımını artırın**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## dbt sorunları

### Sorun 1: dbt'yi çalıştırırken "Bağlantı Hatası"

**Belirtiler**:
- `dbt debug` başarısız
- Hata: "Dremio'ya bağlanılamadı"

**Tanı**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Çözümler**:

1. **profiles.yml'yi kontrol edin**:
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

2. **Dremio bağlantısını test edin**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Dremio adaptörünü takın**:
   ```bash
   pip install dbt-dremio
   ```

### Sorun 2: Model oluşturulamıyor

**Belirtiler**:
- `dbt run` belirli bir model için başarısız oluyor
- SQL derleme veya yürütme hatası

**Tanı**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Çözümler**:

1. **Model sözdizimini kontrol edin**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Önce SQL IDE'de test edin**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Bağımlılıkları kontrol edin**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Sorun 3: Testler başarısız

**Belirtiler**:
- `dbt test` hataları bildirir
- Veri kalitesi sorunları algılandı

**Tanı**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Çözümler**:

1. **Kaynak verileri düzeltin**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Test eşiğini ayarlayın**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Temel nedeni araştırın**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Sorun 4: Artımlı model çalışmıyor

**Belirtiler**:
- Artımlı model her çalıştırıldığında tamamen yeniden oluşturulur
- Artımlı davranış yok

**Tanı**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Çözümler**:

1. **Sistem gereksinimlerini ekleyin**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Artımlı mantık ekleyin**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Tam yenilemeyi bir kez zorlayın**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Süperset Problemleri

### Sorun 1: Superset'e bağlanılamıyor

**Belirtiler**:
- Giriş sayfasında "Geçersiz kimlik bilgileri" görüntüleniyor
- Varsayılan yönetici/yönetici çifti çalışmıyor

**Tanı**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Çözümler**:

1. **Yönetici şifresini sıfırlayın**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Yönetici kullanıcı oluşturun**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Süper Seti Sıfırla**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Sorun 2: Veritabanı bağlantısı başarısız oluyor

**Belirtiler**:
- “Bağlantıyı Test Et” düğmesi başarısız oluyor
- Hata: "Veritabanına bağlanılamıyor"

**Tanı**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Çözümler**:

1. **Doğru SQLAlchemy URI'sini kullanın**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Gerekli sürücüleri yükleyin**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Ağı kontrol edin**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Sayı 3: Grafikler yüklenmiyor

**Belirtiler**:
- Kontrol panelinde süresiz olarak bir yükleme döndürücüsü görüntülenir
- Grafikler "Veri yüklenirken hata" gösteriyor

**Tanı**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Çözümler**:

1. **Sorgu zaman aşımını kontrol edin**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Eşzamansız istekleri etkinleştirin**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Önbelleği temizle**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Sorun 4: İzin hataları

**Belirtiler**:
- Kullanıcı kontrol panellerini göremez
- Hata: "Bu kontrol paneline erişiminiz yok"

**Tanı**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Çözümler**:

1. **Kullanıcıyı bir role ekleyin**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Kontrol paneline erişim izni verin**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **RLS kurallarını kontrol edin**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL sorunları

### Sorun 1: Bağlantı reddedildi

**Belirtiler**:
- Uygulamalar PostgreSQL'e bağlanamıyor
- Hata: "Bağlantı reddedildi" veya "Bağlanılamadı"

**Tanı**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Çözümler**:

1. **PostgreSQL'i yeniden başlatın**:
   ```bash
   docker-compose restart postgres
   ```

2. **Bağlantı noktası eşlemesini kontrol edin**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Kimlik bilgilerini kontrol edin**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Sorun 2: Bağlantı eksikliği

**Belirtiler**:
- Hata: "ÖLÜMCÜL: kalan bağlantı yuvaları ayrıldı"
- Uygulamalar zaman zaman bağlanamıyor

**Tanı**:
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

**Çözümler**:

1. **max_connections'ı artırın**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Bağlantı havuzunu kullanın**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Boş bağlantıları sonlandırın**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Sorun 3: Yavaş sorgular

**Belirtiler**:
- Veritabanı sorguları birkaç saniye sürer
- Uygulamaların süresi doluyor

**Tanı**:
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

**Çözümler**:

1. **Dizinler oluşturun**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **ANALİZİ çalıştırın**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Paylaşılan_bufferları artırın**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO sorunları

### Sorun 1: MinIO konsoluna erişilemiyor

**Belirtiler**:
- Tarayıcı `http://localhost:9001` adresinde bir hata görüntülüyor

**Tanı**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Çözümler**:

1. **Bağlantı noktalarını kontrol edin**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Doğru URL'ye erişin**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **MinIO'yu yeniden başlatın**:
   ```bash
   docker-compose restart minio
   ```

### Sorun 2: Erişim Reddedildi Hataları

**Belirtiler**:
- Uygulamalar S3'e okuyamıyor/yazamıyor
- Hata: "Erişim Reddedildi" veya "403 Yasak"

**Tanı**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Çözümler**:

1. **Kimlik bilgilerini kontrol edin**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Paket politikasını kontrol edin**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Uygulama için bir erişim anahtarı oluşturun**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Sorun 3: Kova bulunamadı

**Belirtiler**:
- Hata: "Belirtilen paket mevcut değil"

**Tanı**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Çözümler**:

1. **Paketi oluşturun**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Yapılandırmadaki paket adını kontrol edin**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Ağ ve bağlantı

### Sorun: Hizmetler iletişim kuramıyor

**Belirtiler**:
- Kaplar arasında "Bağlantı reddedildi"
- “Ana Bilgisayar bulunamadı” hataları

**Tanı**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Çözümler**:

1. **Tüm hizmetlerin aynı ağda olduğundan emin olun**:
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

2. **Localhost yerine kapsayıcı adlarını kullanın**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Ağı yeniden oluşturun**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Performans sorunları

### Sorun: Yüksek CPU kullanımı

**Tanı**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Çözümler**:

1. **Rakip istekleri sınırlayın**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Sorguları optimize edin** (bkz. [Dremio sorunları](#dremio-issues))

3. **CPU tahsisini artırın**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Sorun: Yüksek bellek kullanımı

**Tanı**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Çözümler**:

1. **Yığın boyutunu artırın**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Disk aktarımını etkinleştirin**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Veri kalitesi sorunları

[Veri Kalitesi Kılavuzu](./data-quality.md) belgesinde ayrıntılı olarak açıklanan çözümlere bakın.

### Hızlı kontroller

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

## Özet

Bu sorun giderme kılavuzu şunları kapsıyordu:

- **Genel yaklaşım**: Sorunların teşhisi için sistematik metodoloji
- **Bileşenlere göre sorunlar**: Platformun 7 hizmeti için çözümler
- **Ağ Sorunları**: Container bağlantı sorunları
- **Performans sorunları**: CPU, bellek ve sorgu optimizasyonu
- **Veri kalitesi sorunları**: Yaygın veri sorunları ve kontrolleri

**Önemli çıkarımlar**:
- Her zaman önce günlükleri kontrol edin: `docker-compose logs [service]`
- Hizmetler arası iletişim için localhost yerine kapsayıcı adlarını kullanın
- Bağlantıyı test edin: `docker exec [container] ping [target]`
- Kaynakları izleyin: `docker stats`
- Basit başlayın: karmaşık hata ayıklamadan önce hizmeti yeniden başlatın

**İlgili belgeler:**
- [Kurulum Kılavuzu](../getting-started/installation.md)
- [Yapılandırma Kılavuzu](../getting-started/configuration.md)
- [Veri Kalitesi Kılavuzu](./data-quality.md)
- [Mimarlık: Dağıtım](../architecture/deployment.md)

**Daha fazla yardıma mı ihtiyacınız var?**
- Bileşen günlüklerini kontrol edin: `docker-compose logs -f [service]`
- Servis belgelerine bakın
- GitHub sorunlarını arayın
- Destek ekibiyle iletişime geçin

---

**Sürüm**: 3.2.0  
**Son güncelleme**: 16 Ekim 2025