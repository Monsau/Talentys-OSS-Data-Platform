# 故障排除指南

**版本**：3.2.0  
**最后更新**：2025 年 10 月 16 日  
**语言**：法语

＃＃ 目录

1. [概述](#overview)
2. [一般故障排除方法](#general-troubleshooting-approach)
3. [Airbyte 问题](#airbyte-problems)
4. [Dremio 问题](#dremio-problems)
5. [dbt问题](#dbt-问题)
6. [超集问题](#superset-problems)
7. [PostgreSQL 问题](#postgresql-problems)
8. [MinIO 问题](#minio-problems)
9. [Elasticsearch 问题](#elasticsearch-issues)
10. [网络和连接](#network-and-connectivity)
11. [性能问题](#performance-issues)
12. [数据质量问题](#data-quality-issues)

---

＃＃ 概述

这份全面的故障排除指南可帮助您诊断和解决所有平台组件的常见问题。问题按组件进行组织，具有明确的症状、诊断和解决方案。

### 故障排除方法

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

## 一般故障排除方法

### 第 1 步：检查服务状态

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

### 第 2 步：检查日志

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### 步骤 3：检查网络连接

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### 步骤 4：检查资源使用情况

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### 常见的快速修复

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

## Airbyte 问题

### 问题 1：Airbyte 界面未加载

**症状** ：
- 浏览器显示“无法连接”或超时
- URL：`http://localhost:8000`未响应

**诊断**：
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**解决方案**：

1. **检查端口是否未被使用**：
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **重新启动 Airbyte 容器**：
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **检查服务器是否健康**：
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### 问题 2：同步失败并出现“连接超时”

**症状** ：
- 同步任务立即失败或挂起
- 错误：“连接超时”或“无法连接到源”

**诊断**：
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**解决方案**：

1. **检查源标识符**：
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **增加超时**：
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **检查网络**：
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### 问题 3：同步期间内存不足

**症状** ：
- 容器工作线程在大型同步期间崩溃
- 错误：“OutOfMemoryError”或“Java 堆空间”

**诊断**：
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**解决方案**：

1. **增加工人记忆**：
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **减少批量**：
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **使用增量同步**：
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### 问题 4：数据未出现在目标中

**症状** ：
- 同步成功完成
- 日志中没有错误
- 数据不在 MinIO/目标中

**诊断**：
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**解决方案**：

1. **检查目标配置**：
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **检查标准化**：
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **手动验证**：
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## 德雷米奥问题

### 问题1：无法连接Dremio接口

**症状** ：
- 浏览器在 `http://localhost:9047`处显示连接错误

**诊断**：
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**解决方案**：

1. **等待完全启动**（可能需要2-3分钟）：
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **增加内存**：
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **清理Dremio数据**（⚠️重置配置）：
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### 问题 2：MinIO 的“离线源”

**症状** ：
- MinIO 源显示红色“离线”指示器
- 错误：“无法连接到源”

**诊断**：
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**解决方案**：

1. **检查 MinIO 端点**：
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

2. **检查凭据**：
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **刷新元数据**：
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### 问题 3：查询性能缓慢

**症状** ：
- 查询需要 10 秒以上
- 仪表板加载缓慢

**诊断**：
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

**解决方案**：

1. **创建反射**：
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

2. **添加分区过滤器**：
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **增加执行器内存**：
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### 问题 4：反射无法构建

**症状** ：
- 反射仍停留在“刷新”状态
- 永无止境

**诊断**：
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**解决方案**：

1. **禁用并重新启用**：
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **检查源数据**：
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **增加超时**：
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## 数据库问题

### 问题 1：运行 dbt 时出现“连接错误”

**症状** ：
- `dbt debug`失败
- 错误：“无法连接到 Dremio”

**诊断**：
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**解决方案**：

1. **检查profiles.yml**：
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

2. **测试 Dremio 连接性**：
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **安装 Dremio 适配器**：
   ```bash
   pip install dbt-dremio
   ```

### 问题2：模型构建失败

**症状** ：
- `dbt run` 对于特定型号失败
- SQL编译或执行错误

**诊断**：
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**解决方案**：

1. **检查模型语法**：
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **首先在 SQL IDE 中测试**：
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **检查依赖关系**：
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### 问题 3：测试失败

**症状** ：
- `dbt test`报告失败
- 检测到数据质量问题

**诊断**：
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**解决方案**：

1. **更正源数据**：
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **调整测试阈值**：
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **调查根本原因**：
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### 问题4：增量模型不起作用

**症状** ：
- 增量模型每次运行时都会完全重建
- 无增量行为

**诊断**：
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**解决方案**：

1. **添加系统要求**：
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **添加增量逻辑**：
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **强制完全刷新一次**：
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## 超集问题

### 问题 1：无法连接到 Superset

**症状** ：
- 登录页面显示“无效凭据”
- 默认的管理员/管理员对不起作用

**诊断**：
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**解决方案**：

1. **重置管理员密码**：
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **创建管理员用户**：
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **重置超级集**：
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### 问题2：数据库连接失败

**症状** ：
- “测试连接”按钮失败
- 错误：“无法连接到数据库”

**诊断**：
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**解决方案**：

1. **使用正确的 SQLAlchemy URI**：
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **安装所需的驱动程序**：
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **检查网络**：
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### 问题 3：图表未加载

**症状** ：
- 仪表板无限期地显示加载旋转器
- 图表显示“加载数据时出错”

**诊断**：
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**解决方案**：

1. **检查查询超时**：
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **启用异步请求**：
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **清除缓存**：
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### 问题 4：权限错误

**症状** ：
- 用户看不到仪表板
- 错误：“您无权访问此仪表板”

**诊断**：
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**解决方案**：

1. **将用户添加到角色**：
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **授予对仪表板的访问权限**：
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **检查RLS规则**：
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL 问题

### 问题 1：连接被拒绝

**症状** ：
- 应用程序无法连接到 PostgreSQL
- 错误：“连接被拒绝”或“无法连接”

**诊断**：
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**解决方案**：

1. **重新启动 PostgreSQL**：
   ```bash
   docker-compose restart postgres
   ```

2. **检查端口映射**：
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **检查凭据**：
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### 问题 2：缺乏连接

**症状** ：
- 错误：“致命：保留剩余连接插槽”
- 应用程序间歇性无法连接

**诊断**：
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

**解决方案**：

1. **增加 max_connections**：
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **使用连接池**：
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **终止空闲连接**：
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### 问题 3：查询速度慢

**症状** ：
- 数据库查询需要几秒钟
- 应用程序过期

**诊断**：
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

**解决方案**：

1. **创建索引**：
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **运行分析**：
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **增加shared_buffers**：
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO 问题

### 问题1：无法访问MinIO控制台

**症状** ：
- 浏览器在 `http://localhost:9001`处显示错误

**诊断**：
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**解决方案**：

1. **检查端口**：
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **访问正确的URL**：
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **重启MinIO**：
   ```bash
   docker-compose restart minio
   ```

### 问题 2：访问被拒绝错误

**症状** ：
- 应用程序无法读取/写入 S3
- 错误：“访问被拒绝”或“403 禁止”

**诊断**：
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**解决方案**：

1. **检查凭据**：
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **检查存储桶策略**：
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **为应用程序创建访问密钥**：
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### 问题 3：未找到存储桶

**症状** ：
- 错误：“指定的存储桶不存在”

**诊断**：
```bash
# List all buckets
docker exec minio mc ls local/
```

**解决方案**：

1. **创建存储桶**：
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **查看配置中的bucket名称**：
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## 网络和连接

### 问题：服务无法通信

**症状** ：
- 容器之间的“连接被拒绝”
- “找不到主机”错误

**诊断**：
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**解决方案**：

1. **确保所有服务都在同一网络上**：
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

2. **使用容器名称，而不是 localhost**：
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **重新创建网络**：
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## 性能问题

### 问题：CPU 使用率高

**诊断**：
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**解决方案**：

1. **限制竞争请求**：
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **优化查询**（请参阅 [Dremio 问题](#dremio-issues)）

3. **增加CPU分配**：
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### 问题：内存使用率高

**诊断**：
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**解决方案**：

1. **增加堆大小**：
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **启用磁盘溢出**：
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## 数据质量问题

详细解决方案请参见【数据质量指南】(./data-quality.md)。

### 快速检查

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

＃＃ 概括

本故障排除指南涵盖：

- **一般方法**：诊断问题的系统方法
- **按组件划分的问题**：平台7项服务的解决方案
- **网络问题**：容器连接问题
- **性能问题**：CPU、内存和查询优化
- **数据质量问题**：常见数据问题和检查

**要点**：
- 务必先检查日志：`docker-compose logs [service]`
- 使用容器名称而不是本地主机进行服务间通信
- 测试连接：`docker exec [container] ping [target]`
- 监控资源：`docker stats`
- 简单启动：复杂调试前先重启服务

**相关文档：**
- [安装指南](../getting-started/installation.md)
- [配置指南](../getting-started/configuration.md)
- [数据质量指南](./data-quality.md)
- [架构：部署](../architecture/deployment.md)

**需要更多帮助吗？**
- 检查组件日志：`docker-compose logs -f [service]`
- 查阅服务文档
- 搜索 GitHub 问题
- 联系支持团队

---

**版本**：3.2.0  
**最后更新**：2025 年 10 月 16 日