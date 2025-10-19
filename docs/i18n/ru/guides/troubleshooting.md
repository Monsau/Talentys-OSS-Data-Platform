# Руководство по устранению неполадок

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Язык**: французский

## Оглавление

1. [Обзор](#обзор)
2. [Общий подход к устранению неполадок](#general-troubleshooting-approach)
3. [Проблемы Airbyte](#airbyte-problems)
4. [Проблемы Дремио](#dremio-problems)
5. [проблемы с dbt](#dbt-problems)
6. [Суперсет проблем](#superset-problems)
7. [Проблемы PostgreSQL](#postgresql-problems)
8. [Проблемы MinIO](#minio-problems)
9. [Проблемы Elasticsearch](#elasticsearch-issues)
10. [Сеть и подключение](#network-and-connectivity)
11. [Проблемы с производительностью](# Performance-issues)
12. [Проблемы с качеством данных](#data-quality-issues)

---

## Обзор

Это подробное руководство по устранению неполадок поможет вам диагностировать и решать распространенные проблемы во всех компонентах платформы. Проблемы сгруппированы по компонентам с четкими симптомами, диагностикой и решениями.

### Методика устранения неполадок

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

## Общий подход к устранению неполадок

### Шаг 1. Проверьте статус услуг

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

### Шаг 2. Проверьте журналы

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Шаг 3. Проверьте подключение к сети

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Шаг 4. Проверьте использование ресурсов

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Распространенные быстрые исправления

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

## Проблемы с Airbyte

### Проблема 1: интерфейс Airbyte не загружается

**Симптомы** :
- В браузере отображается сообщение «Невозможно подключиться» или время ожидания.
- URL: `http://localhost:8000` не отвечает.

**Диагноз**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Решения**:

1. **Убедитесь, что порт не используется**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Перезапустите контейнеры Airbyte**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Убедитесь, что сервер исправен**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Проблема 2: синхронизация завершается с ошибкой «Тайм-аут соединения»

**Симптомы** :
- Задача синхронизации немедленно завершается сбоем или зависает.
- Ошибка: «Тайм-аут соединения» или «Невозможно подключиться к источнику».

**Диагноз**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Решения**:

1. **Проверьте идентификаторы источников**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Увеличьте время ожидания**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Проверьте сеть**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Проблема 3. Недостаточно памяти во время синхронизации.

**Симптомы** :
- Контейнерный работник аварийно завершает работу во время больших синхронизаций.
- Ошибка: «OutOfMemoryError» или «Кучное пространство Java».

**Диагноз**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Решения**:

1. **Увеличение рабочей памяти**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Уменьшить размер партии**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Используйте инкрементальную синхронизацию**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Проблема 4: данные не отображаются в месте назначения.

**Симптомы** :
- Синхронизация завершена успешно
- Отсутствие ошибок в логах
- Данные отсутствуют в MinIO/месте назначения.

**Диагноз**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Решения**:

1. **Проверьте конфигурацию назначения**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Проверьте нормализацию**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Ручная проверка**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Проблемы с Дремио

### Проблема 1: невозможно подключиться к интерфейсу Dremio.

**Симптомы** :
- Браузер показывает ошибку подключения по адресу `http://localhost:9047`.

**Диагноз**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Решения**:

1. **Дождитесь полного запуска** (это может занять 2–3 минуты):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Увеличение памяти**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Очистить данные Dremio** (⚠️ сбрасывает конфигурацию):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Проблема 2: «Автономный источник» для MinIO

**Симптомы** :
- Источник MinIO отображает красный индикатор «Не в сети».
- Ошибка: «Невозможно подключиться к источнику».

**Диагноз**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Решения**:

1. **Проверьте конечную точку MinIO**:
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

2. **Проверьте учетные данные**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Обновить метаданные**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Проблема 3: низкая производительность запросов

**Симптомы** :
- Запросы занимают более 10 секунд.
- Панели инструментов загружаются медленно.

**Диагноз**:
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

**Решения**:

1. **Создавайте отражения**:
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

2. **Добавьте фильтры разделов**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Увеличить память исполнителя**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Проблема 4: Reflection не строится

**Симптомы** :
- Отражение остается в состоянии «ОБНОВЛЕНИЕ».
- Никогда не заканчивается

**Диагноз**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Решения**:

1. **Отключите и снова включите**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Проверьте исходные данные**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Увеличьте время ожидания**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## проблемы с БДТ

### Проблема 1: «Ошибка подключения» при запуске dbt

**Симптомы** :
- `dbt debug` не работает
- Ошибка: «Не удалось подключиться к Дремио»

**Диагноз**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Решения**:

1. **Проверьте файл Profiles.yml**:
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

2. **Проверьте подключение Dremio**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Установите адаптер Dremio**:
   ```bash
   pip install dbt-dremio
   ```

### Проблема 2: модель не удается построить

**Симптомы** :
- `dbt run` не работает для конкретной модели.
- Ошибка компиляции или выполнения SQL.

**Диагноз**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Решения**:

1. **Проверьте синтаксис модели**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Сначала протестируйте в SQL IDE**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Проверьте зависимости**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Проблема 3: тесты не пройдены

**Симптомы** :
- `dbt test` сообщает об ошибках
- Обнаружены проблемы с качеством данных.

**Диагноз**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Решения**:

1. **Исправьте исходные данные**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Отрегулируйте порог тестирования**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Выясните причину**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Проблема 4: инкрементальная модель не работает

**Симптомы** :
- Инкрементальная модель полностью перестраивается при каждом запуске.
- Никакого дополнительного поведения

**Диагноз**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Решения**:

1. **Добавьте системные требования**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Добавьте инкрементальную логику**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Принудительно выполнить полное обновление один раз**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Проблемы с суперсетами

### Проблема 1: невозможно подключиться к Superset.

**Симптомы** :
- На странице входа отображается сообщение «Неверные учетные данные».
- Пара администратор/администратор по умолчанию не работает.

**Диагноз**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Решения**:

1. **Сбросить пароль администратора**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Создайте администратора**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Сбросить суперсет**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Проблема 2. Не удалось подключиться к базе данных.

**Симптомы** :
- Кнопка «Проверить соединение» не работает
- Ошибка: «Невозможно подключиться к базе данных»

**Диагноз**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Решения**:

1. **Используйте правильный URI SQLAlchemy**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Установите необходимые драйверы**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Проверьте сеть**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Проблема 3: диаграммы не загружаются

**Симптомы** :
- На приборной панели отображается индикатор загрузки на неопределенный срок.
- На диаграммах отображается сообщение «Ошибка загрузки данных».

**Диагноз**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Решения**:

1. **Проверьте тайм-аут запроса**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Включить асинхронные запросы**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Очистить кеш**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Проблема 4: ошибки разрешений

**Симптомы** :
- Пользователь не может видеть информационные панели.
- Ошибка: «У вас нет доступа к этой панели управления».

**Диагноз**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Решения**:

1. **Добавьте пользователя в роль**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Предоставьте доступ к панели управления**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Проверьте правила RLS**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## Проблемы с PostgreSQL

### Проблема 1: соединение отклонено

**Симптомы** :
- Приложения не могут подключиться к PostgreSQL.
- Ошибка: «Соединение отклонено» или «Не удалось подключиться».

**Диагноз**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Решения**:

1. **Перезапустите PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

2. **Проверьте сопоставление портов**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Проверьте учетные данные**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Проблема 2: Отсутствие связей

**Симптомы** :
- Ошибка: «FATAL: оставшиеся слоты подключения зарезервированы»
- Приложения периодически не подключаются

**Диагноз**:
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

**Решения**:

1. **Увеличьте максимальное количество соединений**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Использовать пул соединений**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Завершить простаивающие соединения**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Проблема 3: Медленные запросы

**Симптомы** :
- Запросы к базе данных занимают несколько секунд.
- Срок действия приложений истекает

**Диагноз**:
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

**Решения**:

1. **Создание индексов**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Запустите АНАЛИЗ**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Увеличьте общие_буферы**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##Проблемы с MinIO

### Проблема 1. Невозможно получить доступ к консоли MinIO.

**Симптомы** :
- Браузер отображает ошибку по адресу `http://localhost:9001`.

**Диагноз**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Решения**:

1. **Проверьте порты**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Перейдите по правильному URL**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Перезапустите MinIO**:
   ```bash
   docker-compose restart minio
   ```

### Проблема 2: ошибки «Отказано в доступе»

**Симптомы** :
- Приложения не могут читать/записывать в S3.
- Ошибка: «Доступ запрещен» или «403 запрещен».

**Диагноз**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Решения**:

1. **Проверьте учетные данные**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Проверьте политику сегмента**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Создайте ключ доступа к приложению**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Проблема 3: сегмент не найден

**Симптомы** :
- Ошибка: «Указанный сегмент не существует».

**Диагноз**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Решения**:

1. **Создайте сегмент**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Проверьте имя сегмента в конфигурации**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Сеть и подключение

### Проблема: службы не могут обмениваться данными

**Симптомы** :
- «Соединение отклонено» между контейнерами
- Ошибки «Хост не найден»

**Диагноз**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Решения**:

1. **Убедитесь, что все службы находятся в одной сети**:
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

2. **Используйте имена контейнеров, а не localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Воссоздайте сеть**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Проблемы с производительностью

### Проблема: высокая загрузка ЦП.

**Диагноз**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Решения**:

1. **Ограничьте конкурирующие запросы**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Оптимизируйте запросы** (см. [Проблемы с Dremio](#dremio-issues))

3. **Увеличить выделение ЦП**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Проблема: высокое использование памяти.

**Диагноз**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Решения**:

1. **Увеличьте размер кучи**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Включить разгрузку диска**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Проблемы с качеством данных

См. решения, подробно описанные в [Руководстве по качеству данных](./data-quality.md).

### Быстрые проверки

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

## Краткое содержание

В этом руководстве по устранению неполадок рассматриваются:

- **Общий подход**: Систематическая методология диагностики проблем.
- **Проблемы по компонентам**: Решения для 7 сервисов платформы.
- **Проблемы с сетью**: проблемы с подключением контейнера.
- **Проблемы с производительностью**: оптимизация ЦП, памяти и запросов.
- **Проблемы с качеством данных**: распространенные проблемы с данными и проверки.

**Основные выводы**:
- Всегда сначала проверяйте логи: `docker-compose logs [service]`.
— Используйте имена контейнеров, а не localhost, для межсервисного взаимодействия.
- Проверка подключения: `docker exec [container] ping [target]`.
- Ресурсы монитора: `docker stats`.
- Начните с простого: перезапустите службу перед сложной отладкой.

**Сопутствующая документация:**
- [Руководство по установке](../getting-started/installation.md)
- [Руководство по настройке](../getting-started/configuration.md)
- [Руководство по качеству данных](./data-quality.md)
- [Архитектура: Развертывание](../architecture/deployment.md)

**Нужна дополнительная помощь?**
- Проверьте журналы компонентов: `docker-compose logs -f [service]`.
- Ознакомьтесь с сервисной документацией.
- Поиск проблем на GitHub
- Свяжитесь со службой поддержки

---

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.