# Troubleshooting Guide

**Version**: 3.2.0  
**Last updated**: October 16, 2025  
**Language**: French

## Table of contents

1. [Overview](#overview)
2. [General troubleshooting approach](#general-troubleshooting-approach)
3. [Airbyte problems](#airbyte-problems)
4. [Dremio Problems](#dremio-problems)
5. [dbt problems](#dbt-problems)
6. [Superset Problems](#superset-problems)
7. [PostgreSQL problems](#postgresql-problems)
8. [MinIO Problems](#minio-problems)
9. [Elasticsearch issues](#elasticsearch-issues)
10. [Network and Connectivity](#network-and-connectivity)
11. [Performance issues](#performance-issues)
12. [Data quality issues](#data-quality-issues)

---

## Overview

This comprehensive troubleshooting guide helps you diagnose and resolve common issues across all platform components. Problems are organized by component with clear symptoms, diagnostics, and solutions.

### Troubleshooting Methodology

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

## General troubleshooting approach

### Step 1: Check the status of services

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

### Step 2: Check logs

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Step 3: Check network connectivity

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Step 4: Check resource usage

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Common quick fixes

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

## Airbyte issues

### Problem 1: Airbyte interface not loading

**Symptoms** :
- The browser displays "Cannot connect" or timeout
- URL: `http://localhost:8000` not responding

**Diagnosis**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Solutions**:

1. **Check that the port is not in use**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Restart Airbyte Containers**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Check that the server is healthy**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Problem 2: Synchronization fails with "Connection Timeout"

**Symptoms** :
- Sync task immediately fails or hangs
- Error: "Connection timeout" or "Unable to connect to source"

**Diagnosis**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Solutions**:

1. **Check source identifiers**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Increase the timeout**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Check the network**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Issue 3: Out of memory during sync

**Symptoms** :
- Container worker crashes during large synchronizations
- Error: "OutOfMemoryError" or "Java heap space"

**Diagnosis**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Solutions**:

1. **Increase worker memory**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Reduce batch size**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Use incremental synchronization**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Problem 4: Data does not appear in destination

**Symptoms** :
- Synchronization completes successfully
- No errors in the logs
- Data is not in MinIO/destination

**Diagnosis**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Solutions**:

1. **Check the destination configuration**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Check normalization**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Manual verification**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Dremio Problems

### Problem 1: Unable to connect to Dremio interface

**Symptoms** :
- Browser shows connection error at `http://localhost:9047`

**Diagnosis**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Solutions**:

1. **Wait for complete startup** (may take 2-3 minutes):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Increase memory**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Clean Dremio data** (⚠️ resets configuration):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Problem 2: "Offline Source" for MinIO

**Symptoms** :
- The MinIO source displays a red “Offline” indicator
- Error: "Unable to connect to source"

**Diagnosis**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Solutions**:

1. **Check the MinIO endpoint**:
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

2. **Check credentials**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Refresh metadata**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Issue 3: Slow query performance

**Symptoms** :
- Queries take 10+ seconds
- Dashboards are slow to load

**Diagnosis**:
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

**Solutions**:

1. **Create reflections**:
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

2. **Add partition filters**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Increase executor memory**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Problem 4: Reflection does not build

**Symptoms** :
- Reflection remains stuck in "REFRESHING" state
- Never ends

**Diagnosis**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Solutions**:

1. **Disable and re-enable**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Check source data**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Increase the timeout**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## dbt problems

### Problem 1: "Connection Error" when running dbt

**Symptoms** :
- `dbt debug` fails
- Error: "Could not connect to Dremio"

**Diagnosis**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Solutions**:

1. **Check profiles.yml**:
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

2. **Test Dremio connectivity**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Install the Dremio adapter**:
   ```bash
   pip install dbt-dremio
   ```

### Problem 2: The model fails to build

**Symptoms** :
- `dbt run` fails for a specific model
- SQL compilation or execution error

**Diagnosis**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Solutions**:

1. **Check model syntax**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Test first in a SQL IDE**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Check dependencies**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Problem 3: Tests fail

**Symptoms** :
- `dbt test` reports failures
- Data quality issues detected

**Diagnosis**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Solutions**:

1. **Correct the source data**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Adjust the test threshold**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Investigate the root cause**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Problem 4: Incremental model does not work

**Symptoms** :
- The incremental model is completely rebuilt each time it is run
- No incremental behavior

**Diagnosis**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Solutions**:

1. **Add system requirements**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Add incremental logic**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Force a full refresh once**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Superset Problems

### Problem 1: Unable to connect to Superset

**Symptoms** :
- Login page displays "Invalid credentials"
- The default admin/admin pair does not work

**Diagnosis**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Solutions**:

1. **Reset admin password**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Create an admin user**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Reset Superset**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Issue 2: Database connection fails

**Symptoms** :
- “Test Connection” button fails
- Error: "Cannot connect to database"

**Diagnosis**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Solutions**:

1. **Use the correct SQLAlchemy URI**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Install the required drivers**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Check the network**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Issue 3: Charts not loading

**Symptoms** :
- Dashboard displays a loading spinner indefinitely
- Charts display "Error loading data"

**Diagnosis**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Solutions**:

1. **Check query timeout**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Enable asynchronous requests**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Clear cache**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Problem 4: Permissions errors

**Symptoms** :
- User cannot see dashboards
- Error: "You don't have access to this dashboard"

**Diagnosis**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Solutions**:

1. **Add the user to a role**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Grant access to the dashboard**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Check RLS rules**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL issues

### Problem 1: Connection refused

**Symptoms** :
- Applications cannot connect to PostgreSQL
- Error: "Connection refused" or "Could not connect"

**Diagnosis**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Solutions**:

1. **Restart PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

2. **Check port mapping**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Check credentials**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Problem 2: Lack of connections

**Symptoms** :
- Error: "FATAL: remaining connection slots are reserved"
- Apps intermittently fail to connect

**Diagnosis**:
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

**Solutions**:

1. **Increase max_connections**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Use connection pooling**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Kill idle connections**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Problem 3: Slow queries

**Symptoms** :
- Database queries take several seconds
- Apps expire

**Diagnosis**:
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

**Solutions**:

1. **Create indexes**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Run ANALYZE**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Increase shared_buffers**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO issues

### Issue 1: Unable to access MinIO console

**Symptoms** :
- The browser displays an error at `http://localhost:9001`

**Diagnosis**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Solutions**:

1. **Check ports**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Access the correct URL**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Restart MinIO**:
   ```bash
   docker-compose restart minio
   ```

### Issue 2: Access Denied Errors

**Symptoms** :
- Applications cannot read/write to S3
- Error: "Access Denied" or "403 Forbidden"

**Diagnosis**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Solutions**:

1. **Check credentials**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Check the bucket policy**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Create an access key for the application**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Problem 3: Bucket not found

**Symptoms** :
- Error: "The specified bucket does not exist"

**Diagnosis**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Solutions**:

1. **Create the bucket**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Check the bucket name in the configuration**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Network and connectivity

### Problem: Services cannot communicate

**Symptoms** :
- "Connection refused" between containers
- “Host not found” errors

**Diagnosis**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Solutions**:

1. **Ensure all services are on the same network**:
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

2. **Use container names, not localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Recreate the network**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Performance issues

### Problem: High CPU usage

**Diagnosis**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Solutions**:

1. **Limit competing requests**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Optimize queries** (see [Dremio issues](#dremio-issues))

3. **Increase CPU allocation**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Problem: High memory usage

**Diagnosis**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Solutions**:

1. **Increase the heap size**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Enable disk spilling**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Data quality issues

See the solutions detailed in the [Data Quality Guide](./data-quality.md).

### Quick checks

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

## Summary

This troubleshooting guide covered:

- **General approach**: Systematic methodology for diagnosing problems
- **Problems by component**: Solutions for the 7 services of the platform
- **Network Issues**: Container connectivity issues
- **Performance issues**: CPU, memory and query optimization
- **Data quality issues**: Common data issues and checks

**Key takeaways**:
- Always check the logs first: `docker-compose logs [service]`
- Use container names, not localhost, for inter-service communication
- Test connectivity: `docker exec [container] ping [target]`
- Monitor resources: `docker stats`
- Start simple: restart the service before complex debugging

**Related documentation:**
- [Installation Guide](../getting-started/installation.md)
- [Configuration Guide](../getting-started/configuration.md)
- [Data Quality Guide](./data-quality.md)
- [Architecture: Deployment](../architecture/deployment.md)

**Need more help?**
- Check the component logs: `docker-compose logs -f [service]`
- Consult the service documentation
- Search GitHub issues
- Contact the support team

---

**Version**: 3.2.0  
**Last updated**: October 16, 2025