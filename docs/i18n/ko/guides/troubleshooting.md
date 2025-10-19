# 문제 해결 가이드

**버전**: 3.2.0  
**최종 업데이트**: 2025년 10월 16일  
**언어**: 프랑스어

## 목차

1. [개요](#overview)
2. [일반적인 문제 해결 방법](#general-troubleshooting-approach)
3. [에어바이트 문제](#airbyte-problems)
4. [드레미오 문제](#dremio-problems)
5. [dbt 문제](#dbt-problems)
6. [슈퍼세트 문제](#superset-problems)
7. [PostgreSQL 문제](#postgresql-problems)
8. [MinIO 문제](#minio-problems)
9. [Elasticsearch 문제](#elasticsearch-issues)
10. [네트워크 및 연결](#network-and-connectivity)
11. [성능 문제](#performance-issues)
12. [데이터 품질 문제](#data-quality-issues)

---

## 개요

이 포괄적인 문제 해결 가이드는 모든 플랫폼 구성 요소에서 일반적인 문제를 진단하고 해결하는 데 도움이 됩니다. 문제는 명확한 증상, 진단 및 솔루션을 통해 구성 요소별로 구성됩니다.

### 문제 해결 방법론

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

## 일반적인 문제 해결 접근 방식

### 1단계: 서비스 상태 확인

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

### 2단계: 로그 확인

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### 3단계: 네트워크 연결 확인

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### 4단계: 리소스 사용량 확인

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### 일반적인 빠른 수정

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

## 에어바이트 문제

### 문제 1: Airbyte 인터페이스가 로드되지 않음

**증상** :
- 브라우저에 "연결할 수 없음" 또는 시간 초과가 표시됩니다.
- URL: `http://localhost:8000` 응답하지 않음

**진단**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**해결책**:

1. **포트가 사용 중이 아닌지 확인**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Airbyte 컨테이너 다시 시작**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **서버가 정상인지 확인**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### 문제 2: "연결 시간 초과"로 인해 동기화가 실패합니다.

**증상** :
- 동기화 작업이 즉시 실패하거나 중단됩니다.
- 오류: "연결 시간 초과" 또는 "소스에 연결할 수 없습니다"

**진단**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**해결책**:

1. **소스 식별자 확인**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **시간 제한을 늘립니다**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **네트워크 확인**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### 문제 3: 동기화 중 메모리 부족

**증상** :
- 대규모 동기화 중 컨테이너 작업자 충돌
- 오류: "OutOfMemoryError" 또는 "Java 힙 공간"

**진단**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**해결책**:

1. **작업자 메모리 늘리기**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **배치 크기 줄이기**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **증분 동기화 사용**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### 문제 4: 대상에 데이터가 표시되지 않습니다.

**증상** :
- 동기화가 성공적으로 완료되었습니다.
- 로그에 오류가 없습니다.
- 데이터가 MinIO/대상에 없음

**진단**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**해결책**:

1. **대상 구성 확인**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **정규화 확인**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **수동 확인**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## 드레미오 문제

### 문제 1: Dremio 인터페이스에 연결할 수 없습니다

**증상** :
- 브라우저에서 `http://localhost:9047`에 연결 오류가 표시됩니다.

**진단**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**해결책**:

1. **시작이 완료될 때까지 기다립니다**(2~3분 정도 소요될 수 있음):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **메모리 늘리기**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Dremio 데이터 정리**(⚠️ 구성 재설정):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### 문제 2: MinIO의 "오프라인 소스"

**증상** :
- MinIO 소스에 빨간색 "오프라인" 표시기가 표시됩니다.
- 오류: "소스에 연결할 수 없습니다."

**진단**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**해결책**:

1. **MinIO 엔드포인트 확인**:
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

2. **자격 증명 확인**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **메타데이터 새로고침**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### 문제 3: 느린 쿼리 성능

**증상** :
- 쿼리에 10초 이상 소요
- 대시보드 로드 속도가 느림

**진단**:
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

**해결책**:

1. **반사 만들기**:
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

2. **파티션 필터 추가**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **실행기 메모리 늘리기**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### 문제 4: 리플렉션이 빌드되지 않습니다.

**증상** :
- 반사가 "새로 고침" 상태로 유지됩니다.
- 끝나지 않아

**진단**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**해결책**:

1. **비활성화 및 재활성화**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **소스 데이터 확인**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **시간 제한을 늘립니다**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## DBT 문제

### 문제 1: dbt 실행 시 "연결 오류" 발생

**증상** :
- `dbt debug` 실패
- 오류: "Dremio에 연결할 수 없습니다."

**진단**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**해결책**:

1. **profiles.yml을 확인하세요**:
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

2. **Dremio 연결 테스트**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Dremio 어댑터 설치**:
   ```bash
   pip install dbt-dremio
   ```

### 문제 2: 모델 구축에 실패함

**증상** :
- `dbt run`는 특정 모델에 대해 실패합니다.
- SQL 컴파일 또는 실행 오류

**진단**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**해결책**:

1. **모델 구문 확인**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **SQL IDE에서 먼저 테스트**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **종속성 확인**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### 문제 3: 테스트 실패

**증상** :
- `dbt test` 보고 실패
- 데이터 품질 문제가 감지되었습니다.

**진단**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**해결책**:

1. **소스 데이터 수정**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **테스트 임계값 조정**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **근본 원인 조사**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### 문제 4: 증분 모델이 작동하지 않습니다.

**증상** :
- 증분형 모델은 실행될 때마다 완전히 재구축됩니다.
- 증분 동작 없음

**진단**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**해결책**:

1. **시스템 요구사항 추가**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **증분 논리 추가**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **한 번 전체 새로 고침을 강제 실행**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## 슈퍼세트 문제

### 문제 1: Superset에 연결할 수 없습니다.

**증상** :
- 로그인 페이지에 "잘못된 자격 증명"이 표시됩니다.
- 기본 관리자/관리자 쌍이 작동하지 않습니다.

**진단**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**해결책**:

1. **관리자 비밀번호 재설정**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **관리자 생성**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **슈퍼세트 재설정**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### 문제 2: 데이터베이스 연결 실패

**증상** :
- “연결 테스트” 버튼이 실패합니다.
- 오류: "데이터베이스에 연결할 수 없습니다."

**진단**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**해결책**:

1. **올바른 SQLAlchemy URI를 사용하세요**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **필요한 드라이버를 설치합니다**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **네트워크 확인**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### 문제 3: 차트가 로드되지 않음

**증상** :
- 대시보드에 로딩 스피너가 무한정 표시됩니다.
- 차트에 "데이터 로드 오류"가 표시됩니다.

**진단**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**해결책**:

1. **쿼리 시간 초과 확인**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **비동기 요청 활성화**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **캐시 지우기**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### 문제 4: 권한 오류

**증상** :
- 사용자가 대시보드를 볼 수 없습니다.
- 오류: "이 대시보드에 액세스할 수 없습니다."

**진단**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**해결책**:

1. **사용자를 역할에 추가**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **대시보드에 대한 액세스 권한을 부여합니다**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **RLS 규칙을 확인하세요**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL 문제

### 문제 1: 연결이 거부되었습니다.

**증상** :
- 애플리케이션이 PostgreSQL에 연결할 수 없습니다.
- 오류: "연결이 거부되었습니다" 또는 "연결할 수 없습니다"

**진단**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**해결책**:

1. **PostgreSQL 다시 시작**:
   ```bash
   docker-compose restart postgres
   ```

2. **포트 매핑 확인**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **자격 증명 확인**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### 문제 2: 연결 부족

**증상** :
- 오류: "치명적: 나머지 연결 슬롯이 예약되어 있습니다."
- 앱이 간헐적으로 연결되지 않습니다.

**진단**:
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

**해결책**:

1. **max_connections 증가**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **연결 풀링 사용**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **유휴 연결 종료**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### 문제 3: 느린 쿼리

**증상** :
- 데이터베이스 쿼리에는 몇 초가 걸립니다.
- 앱 만료

**진단**:
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

**해결책**:

1. **인덱스 생성**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **분석 실행**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **shared_buffers 늘리기**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO 문제

### 문제 1: MinIO 콘솔에 액세스할 수 없습니다.

**증상** :
- 브라우저에서 `http://localhost:9001`에 오류가 표시됩니다.

**진단**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**해결책**:

1. **포트 확인**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **올바른 URL에 액세스하세요**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **MinIO 다시 시작**:
   ```bash
   docker-compose restart minio
   ```

### 문제 2: 액세스 거부 오류

**증상** :
- 애플리케이션이 S3를 읽고 쓸 수 없습니다.
- 오류: "액세스 거부됨" 또는 "403 금지됨"

**진단**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**해결책**:

1. **자격 증명 확인**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **버킷 정책을 확인하세요**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **애플리케이션에 대한 액세스 키를 생성합니다**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### 문제 3: 버킷을 찾을 수 없음

**증상** :
- 오류: "지정된 버킷이 존재하지 않습니다."

**진단**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**해결책**:

1. **버킷 생성**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **구성에서 버킷 이름을 확인하세요**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## 네트워크 및 연결

### 문제: 서비스가 통신할 수 없습니다.

**증상** :
- 컨테이너 간 "연결이 거부되었습니다"
- "호스트를 찾을 수 없음" 오류

**진단**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**해결책**:

1. **모든 서비스가 동일한 네트워크에 있는지 확인**:
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

2. **localhost가 아닌 컨테이너 이름을 사용하십시오**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **네트워크를 다시 생성**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## 성능 문제

### 문제: 높은 CPU 사용량

**진단**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**해결책**:

1. **경쟁 요청 제한**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **쿼리 최적화**([Dremio 문제](#dremio-issues) 참조)

3. **CPU 할당 늘리기**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### 문제: 높은 메모리 사용량

**진단**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**해결책**:

1. **힙 크기 늘리기**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **디스크 유출 활성화**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## 데이터 품질 문제

[데이터 품질 가이드](./data-quality.md)에서 자세한 솔루션을 확인하세요.

### 빠른 확인

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

## 요약

이 문제 해결 가이드에서는 다음을 다룹니다.

- **일반적인 접근 방식**: 문제 진단을 위한 체계적인 방법론
- **구성요소별 문제점**: 플랫폼의 7개 서비스에 대한 솔루션
- **네트워크 문제**: 컨테이너 연결 문제
- **성능 문제**: CPU, 메모리 및 쿼리 최적화
- **데이터 품질 문제**: 일반적인 데이터 문제 및 점검

**주요 사항**:
- 항상 로그를 먼저 확인하세요: `docker-compose logs [service]`
- 서비스 간 통신에는 localhost가 아닌 컨테이너 이름을 사용합니다.
- 연결 테스트: `docker exec [container] ping [target]`
- 리소스 모니터링: `docker stats`
- 단순 시작: 복잡한 디버깅 전에 서비스를 다시 시작합니다.

**관련 문서:**
- [설치 가이드](../getting-started/installation.md)
- [구성 가이드](../getting-started/configuration.md)
- [데이터 품질 가이드](./data-quality.md)
- [아키텍처: 배포](../architecture/deployment.md)

**도움이 더 필요하세요?**
- 구성요소 로그 확인: `docker-compose logs -f [service]`
- 서비스 문서를 참조하세요.
- GitHub 문제 검색
- 지원팀에 문의하세요

---

**버전**: 3.2.0  
**최종 업데이트**: 2025년 10월 16일