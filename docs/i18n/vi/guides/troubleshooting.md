#Hướng dẫn khắc phục sự cố

**Phiên bản**: 3.2.0  
**Cập nhật lần cuối**: Ngày 16 tháng 10 năm 2025  
**Ngôn ngữ**: Tiếng Pháp

## Mục lục

1. [Tổng quan](#tổng quan)
2. [Phương pháp khắc phục sự cố chung](#phương pháp khắc phục sự cố chung)
3. [Sự cố Airbyte](#sự cố Airbyte)
4. [Sự cố Dremio](#vấn đề dremio)
5. [vấn đề dbt](#dbt-problem)
6. [Vấn đề về superset](#superset-problems)
7. [Vấn đề về PostgreSQL](#postgresql-problems)
8. [Sự cố MinIO](#minio-problems)
9. [Vấn đề về Elaticsearch](#elasticsearch-issues)
10. [Mạng và kết nối](#mạng và kết nối)
11. [Vấn đề về hiệu suất](#performance-issues)
12. [Vấn đề về chất lượng dữ liệu](#data-quality-issues)

---

## Tổng quan

Hướng dẫn khắc phục sự cố toàn diện này giúp bạn chẩn đoán và giải quyết các sự cố phổ biến trên tất cả các thành phần nền tảng. Các vấn đề được sắp xếp theo thành phần với các triệu chứng, chẩn đoán và giải pháp rõ ràng.

### Phương pháp khắc phục sự cố

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

## Phương pháp khắc phục sự cố chung

### Bước 1: Kiểm tra trạng thái dịch vụ

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

### Bước 2: Kiểm tra nhật ký

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Bước 3: Kiểm tra kết nối mạng

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Bước 4: Kiểm tra mức sử dụng tài nguyên

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Các cách sửa nhanh phổ biến

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

## Vấn đề về Airbyte

### Vấn đề 1: Giao diện Airbyte không tải

**Triệu chứng** :
- Trình duyệt hiển thị "Không thể kết nối" hoặc hết thời gian chờ
- URL: `http://localhost:8000` không phản hồi

**Chẩn đoán**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Giải pháp**:

1. **Kiểm tra xem cổng này có được sử dụng không**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Khởi động lại bộ chứa Airbyte**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Kiểm tra xem máy chủ có hoạt động tốt không**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Vấn đề 2: Đồng bộ hóa không thành công với "Hết thời gian kết nối"

**Triệu chứng** :
- Tác vụ đồng bộ ngay lập tức bị lỗi hoặc bị treo
- Lỗi: "Hết thời gian kết nối" hoặc "Không thể kết nối với nguồn"

**Chẩn đoán**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Giải pháp**:

1. **Kiểm tra số nhận dạng nguồn**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Tăng thời gian chờ**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Kiểm tra mạng**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Vấn đề 3: Hết bộ nhớ trong quá trình đồng bộ

**Triệu chứng** :
- Nhân viên container gặp sự cố trong quá trình đồng bộ hóa lớn
- Lỗi: "OutOfMemoryError" hoặc "Không gian heap Java"

**Chẩn đoán**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Giải pháp**:

1. **Tăng bộ nhớ của nhân viên**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Giảm kích thước lô**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Sử dụng đồng bộ hóa tăng dần**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Vấn đề 4: Dữ liệu không xuất hiện ở đích

**Triệu chứng** :
- Quá trình đồng bộ hóa hoàn tất thành công
- Không có lỗi trong nhật ký
- Dữ liệu không có trong MinIO/đích

**Chẩn đoán**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Giải pháp**:

1. **Kiểm tra cấu hình đích**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Kiểm tra chuẩn hóa**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Xác minh thủ công**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Sự cố của Dremio

### Vấn đề 1: Không thể kết nối với giao diện Dremio

**Triệu chứng** :
- Trình duyệt hiển thị lỗi kết nối tại `http://localhost:9047`

**Chẩn đoán**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Giải pháp**:

1. **Chờ quá trình khởi động hoàn tất** (có thể mất 2-3 phút):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Tăng bộ nhớ**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Làm sạch dữ liệu Dremio** (⚠️ đặt lại cấu hình):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Vấn đề 2: "Nguồn offline" cho MinIO

**Triệu chứng** :
- Nguồn MinIO hiển thị đèn báo “Ngoại tuyến” màu đỏ
- Lỗi: "Không thể kết nối với nguồn"

**Chẩn đoán**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Giải pháp**:

1. **Kiểm tra điểm cuối MinIO**:
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

2. **Kiểm tra thông tin đăng nhập**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Làm mới siêu dữ liệu**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Vấn đề 3: Hiệu suất truy vấn chậm

**Triệu chứng** :
- Truy vấn mất hơn 10 giây
- Bảng điều khiển tải chậm

**Chẩn đoán**:
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

**Giải pháp**:

1. **Tạo phản xạ**:
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

2. **Thêm bộ lọc phân vùng**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Tăng bộ nhớ thực thi**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Vấn đề 4: Reflection không build được

**Triệu chứng** :
- Phản chiếu vẫn bị kẹt ở trạng thái "REFRESHING"
- Không bao giờ kết thúc

**Chẩn đoán**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Giải pháp**:

1. **Tắt và bật lại**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Kiểm tra dữ liệu nguồn**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Tăng thời gian chờ**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## vấn đề về dbt

### Vấn đề 1: "Lỗi kết nối" khi chạy dbt

**Triệu chứng** :
- `dbt debug` không thành công
- Lỗi: "Không thể kết nối với Dremio"

**Chẩn đoán**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Giải pháp**:

1. **Kiểm tra hồ sơ.yml**:
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

2. **Kiểm tra kết nối Dremio**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Cài đặt bộ chuyển đổi Dremio**:
   ```bash
   pip install dbt-dremio
   ```

### Vấn đề 2: Model không xây dựng được

**Triệu chứng** :
- `dbt run` không thành công đối với một mô hình cụ thể
- Lỗi biên dịch hoặc thực thi SQL

**Chẩn đoán**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Giải pháp**:

1. **Kiểm tra cú pháp mô hình**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Kiểm tra đầu tiên trong SQL IDE**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Kiểm tra các phần phụ thuộc**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Vấn đề 3: Test thất bại

**Triệu chứng** :
- `dbt test` báo cáo lỗi
- Đã phát hiện vấn đề về chất lượng dữ liệu

**Chẩn đoán**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Giải pháp**:

1. **Sửa dữ liệu nguồn**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Điều chỉnh ngưỡng kiểm tra**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Điều tra nguyên nhân gốc rễ**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Vấn đề 4: Mô hình lũy tiến không hoạt động

**Triệu chứng** :
- Mô hình gia tăng được xây dựng lại hoàn toàn mỗi lần chạy
- Không có hành vi gia tăng

**Chẩn đoán**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Giải pháp**:

1. **Thêm yêu cầu hệ thống**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Thêm logic tăng dần**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Bắt buộc làm mới hoàn toàn một lần**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Sự cố về siêu tập hợp

### Vấn đề 1: Không kết nối được với Superset

**Triệu chứng** :
- Trang đăng nhập hiển thị "Thông tin đăng nhập không hợp lệ"
- Cặp quản trị viên/quản trị viên mặc định không hoạt động

**Chẩn đoán**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Giải pháp**:

1. **Đặt lại mật khẩu quản trị viên**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Tạo người dùng quản trị**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Đặt lại Superset**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Vấn đề 2: Kết nối cơ sở dữ liệu không thành công

**Triệu chứng** :
- Nút “Kiểm tra kết nối” không thành công
- Lỗi: "Không thể kết nối với cơ sở dữ liệu"

**Chẩn đoán**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Giải pháp**:

1. **Sử dụng URI SQLAlchemy chính xác**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Cài đặt trình điều khiển cần thiết**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Kiểm tra mạng**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Vấn đề 3: Biểu đồ không tải

**Triệu chứng** :
- Bảng điều khiển hiển thị vòng quay tải vô thời hạn
- Biểu đồ hiển thị “Lỗi tải dữ liệu”

**Chẩn đoán**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Giải pháp**:

1. **Kiểm tra thời gian chờ truy vấn**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Bật yêu cầu không đồng bộ**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Xóa bộ nhớ đệm**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Vấn đề 4: Lỗi quyền

**Triệu chứng** :
- Người dùng không thể nhìn thấy bảng điều khiển
- Lỗi: "Bạn không có quyền truy cập vào bảng điều khiển này"

**Chẩn đoán**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Giải pháp**:

1. **Thêm người dùng vào một vai trò**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Cấp quyền truy cập vào bảng điều khiển**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Kiểm tra các quy tắc RLS**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## Các vấn đề về PostgreSQL

### Vấn đề 1: Kết nối bị từ chối

**Triệu chứng** :
- Ứng dụng không thể kết nối với PostgreSQL
- Lỗi: "Kết nối bị từ chối" hoặc "Không thể kết nối"

**Chẩn đoán**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Giải pháp**:

1. **Khởi động lại PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

2. **Kiểm tra ánh xạ cổng**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Kiểm tra thông tin đăng nhập**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Vấn đề 2: Thiếu kết nối

**Triệu chứng** :
- Lỗi: "FATAL: các khe kết nối còn lại được dành riêng"
- Ứng dụng thỉnh thoảng không kết nối được

**Chẩn đoán**:
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

**Giải pháp**:

1. **Tăng số kết nối tối đa**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Sử dụng kết nối tổng hợp**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Loại bỏ các kết nối không hoạt động**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Vấn đề 3: Truy vấn chậm

**Triệu chứng** :
- Truy vấn cơ sở dữ liệu mất vài giây
- Ứng dụng hết hạn

**Chẩn đoán**:
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

**Giải pháp**:

1. **Tạo chỉ mục**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Chạy PHÂN TÍCH**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Tăng số lượng bộ đệm chia sẻ**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##Vấn đề về MinIO

### Vấn đề 1: Không thể truy cập bảng điều khiển MinIO

**Triệu chứng** :
- Trình duyệt hiển thị lỗi tại `http://localhost:9001`

**Chẩn đoán**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Giải pháp**:

1. **Kiểm tra cổng**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Truy cập đúng URL**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Khởi động lại MinIO**:
   ```bash
   docker-compose restart minio
   ```

### Vấn đề 2: Lỗi truy cập bị từ chối

**Triệu chứng** :
- Ứng dụng không thể đọc/ghi vào S3
- Lỗi: "Truy cập bị từ chối" hoặc "403 Bị cấm"

**Chẩn đoán**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Giải pháp**:

1. **Kiểm tra thông tin đăng nhập**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Kiểm tra chính sách nhóm**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Tạo khóa truy cập cho ứng dụng**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Vấn đề 3: Không tìm thấy thùng

**Triệu chứng** :
- Lỗi: "Nhóm được chỉ định không tồn tại"

**Chẩn đoán**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Giải pháp**:

1. **Tạo nhóm**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Kiểm tra tên nhóm trong cấu hình**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Mạng và kết nối

### Vấn đề: Dịch vụ không thể giao tiếp

**Triệu chứng** :
- "Kết nối bị từ chối" giữa các container
- Lỗi “Không tìm thấy máy chủ”

**Chẩn đoán**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Giải pháp**:

1. **Đảm bảo tất cả các dịch vụ đều nằm trên cùng một mạng**:
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

2. **Sử dụng tên vùng chứa, không phải localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Tạo lại mạng**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Vấn đề về hiệu suất

### Vấn đề: Sử dụng CPU cao

**Chẩn đoán**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Giải pháp**:

1. **Giới hạn các yêu cầu cạnh tranh**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Tối ưu hóa truy vấn** (xem [Sự cố Dremio](#dremio-issues))

3. **Tăng phân bổ CPU**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Vấn đề: Sử dụng bộ nhớ cao

**Chẩn đoán**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Giải pháp**:

1. **Tăng kích thước vùng heap**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Cho phép tràn đĩa**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Vấn đề về chất lượng dữ liệu

Xem các giải pháp chi tiết trong [Hướng dẫn chất lượng dữ liệu](./data-quality.md).

### Kiểm tra nhanh

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

## Bản tóm tắt

Hướng dẫn khắc phục sự cố này bao gồm:

- **Phương pháp chung**: Phương pháp có hệ thống để chẩn đoán vấn đề
- **Vấn đề theo thành phần**: Giải pháp cho 7 dịch vụ của nền tảng
- **Sự cố mạng**: Sự cố kết nối vùng chứa
- **Vấn đề về hiệu suất**: Tối ưu hóa CPU, bộ nhớ và truy vấn
- **Vấn đề về chất lượng dữ liệu**: Các vấn đề và kiểm tra dữ liệu thường gặp

**Bài học chính**:
- Luôn kiểm tra nhật ký trước: `docker-compose logs [service]`
- Sử dụng tên vùng chứa, không phải localhost, để liên lạc giữa các dịch vụ
- Kiểm tra kết nối: `docker exec [container] ping [target]`
- Giám sát tài nguyên: `docker stats`
- Bắt đầu đơn giản: khởi động lại dịch vụ trước khi gỡ lỗi phức tạp

**Tài liệu liên quan:**
- [Hướng dẫn cài đặt](../getting-started/installation.md)
- [Hướng dẫn cấu hình](../getting-started/configuration.md)
- [Hướng dẫn chất lượng dữ liệu](./data-quality.md)
- [Kiến trúc: Triển khai](../architecture/deployment.md)

**Cần thêm trợ giúp?**
- Kiểm tra nhật ký thành phần: `docker-compose logs -f [service]`
- Tham khảo tài liệu dịch vụ
- Tìm kiếm các vấn đề về GitHub
- Liên hệ với nhóm hỗ trợ

---

**Phiên bản**: 3.2.0  
**Cập nhật lần cuối**: Ngày 16 tháng 10 năm 2025