# Guía de solución de problemas

**Versión**: 3.2.0  
**Última actualización**: 16 de octubre de 2025  
**Idioma**: Francés

## Tabla de contenido

1. [Resumen](#resumen)
2. [Enfoque general de solución de problemas](#enfoque-de-solución-de-problemas-generales)
3. [Problemas de Airbyte](#problemas-airbyte)
4. [Problemas de Dremio](#dremio-problemas)
5. [problemas dbt](#problemas-dbt)
6. [Problemas de superconjunto] (#problemas de superconjunto)
7. [Problemas de PostgreSQL](#postgresql-problemas)
8. [Problemas de MinIO](#minio-problemas)
9. [Problemas de Elasticsearch](#elasticsearch-issues)
10. [Red y Conectividad](#red-y-conectividad)
11. [Problemas de rendimiento](#problemas-de rendimiento)
12. [Problemas de calidad de datos](#problemas-de-calidad-de-datos)

---

## Descripción general

Esta guía integral de solución de problemas lo ayuda a diagnosticar y resolver problemas comunes en todos los componentes de la plataforma. Los problemas están organizados por componentes con síntomas, diagnósticos y soluciones claros.

### Metodología de resolución de problemas

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

## Enfoque general de solución de problemas

### Paso 1: Verificar el estado de los servicios

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

### Paso 2: comprobar los registros

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Paso 3: Verifique la conectividad de la red

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Paso 4: Verificar el uso de recursos

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Soluciones rápidas comunes

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

## Problemas con Airbytes

### Problema 1: la interfaz de Airbyte no se carga

**Síntomas** :
- El navegador muestra "No se puede conectar" o se agotó el tiempo de espera.
- URL: `http://localhost:8000` no responde

**Diagnóstico**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Soluciones**:

1. **Compruebe que el puerto no esté en uso**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Reiniciar contenedores Airbyte**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Compruebe que el servidor esté en buen estado**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Problema 2: la sincronización falla con "Tiempo de espera de conexión"

**Síntomas** :
- La tarea de sincronización falla o se bloquea inmediatamente
- Error: "Tiempo de espera de conexión" o "No se puede conectar a la fuente"

**Diagnóstico**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Soluciones**:

1. **Verifique los identificadores de origen**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Aumentar el tiempo de espera**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Comprueba la red**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problema 3: Sin memoria durante la sincronización

**Síntomas** :
- El trabajador del contenedor falla durante sincronizaciones grandes
- Error: "OutOfMemoryError" o "espacio de almacenamiento dinámico de Java"

**Diagnóstico**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Soluciones**:

1. **Aumentar la memoria del trabajador**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Reducir el tamaño del lote**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Usar sincronización incremental**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Problema 4: Los datos no aparecen en destino

**Síntomas** :
- La sincronización se completa con éxito
- No hay errores en los registros.
- Los datos no están en MinIO/destino

**Diagnóstico**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Soluciones**:

1. **Comprueba la configuración de destino**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Verificar normalización**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Verificación manual**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Problemas de Dremio

### Problema 1: No se puede conectar a la interfaz Dremio

**Síntomas** :
- El navegador muestra un error de conexión en `http://localhost:9047`

**Diagnóstico**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Soluciones**:

1. **Espere hasta que se inicie por completo** (puede tardar entre 2 y 3 minutos):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Aumentar memoria**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Limpiar datos de Dremio** (⚠️ restablece la configuración):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Problema 2: "Fuente sin conexión" para MinIO

**Síntomas** :
- La fuente MinIO muestra un indicador rojo "Sin conexión"
- Error: "No se puede conectar a la fuente"

**Diagnóstico**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Soluciones**:

1. **Verifique el punto final MinIO**:
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

2. **Verificar credenciales**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Actualizar metadatos**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Problema 3: rendimiento lento de las consultas

**Síntomas** :
- Las consultas tardan más de 10 segundos
- Los paneles tardan en cargarse

**Diagnóstico**:
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

**Soluciones**:

1. **Crea reflejos**:
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

2. **Agregar filtros de partición**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Aumentar la memoria del ejecutor**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Problema 4: La reflexión no construye

**Síntomas** :
- El reflejo permanece atascado en el estado "REFRESCANTE"
- Nunca termina

**Diagnóstico**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Soluciones**:

1. **Desactivar y volver a activar**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Verificar datos de origen**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Aumentar el tiempo de espera**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## problemas de dbt

### Problema 1: "Error de conexión" al ejecutar dbt

**Síntomas** :
- `dbt debug` falla
- Error: "No se pudo conectar a Dremio"

**Diagnóstico**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Soluciones**:

1. **Compruebe perfiles.yml**:
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

2. **Pruebe la conectividad de Dremio**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Instale el adaptador Dremio**:
   ```bash
   pip install dbt-dremio
   ```

### Problema 2: el modelo no se construye

**Síntomas** :
- `dbt run` falla para un modelo específico
- Error de compilación o ejecución de SQL

**Diagnóstico**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Soluciones**:

1. **Verifique la sintaxis del modelo**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Pruebe primero en un IDE de SQL**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Verificar dependencias**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Problema 3: las pruebas fallan

**Síntomas** :
- `dbt test` informa fallas
- Problemas de calidad de datos detectados

**Diagnóstico**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Soluciones**:

1. **Corrige los datos de origen**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Ajuste el umbral de prueba**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Investigue la causa raíz**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Problema 4: el modelo incremental no funciona

**Síntomas** :
- El modelo incremental se reconstruye completamente cada vez que se ejecuta.
- Sin comportamiento incremental

**Diagnóstico**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Soluciones**:

1. **Agregar requisitos del sistema**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Agregar lógica incremental**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Forzar una actualización completa una vez**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Problemas de superconjunto

### Problema 1: No se puede conectar a Superset

**Síntomas** :
- La página de inicio de sesión muestra "Credenciales no válidas"
- El par predeterminado administrador/administrador no funciona

**Diagnóstico**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Soluciones**:

1. **Restablecer contraseña de administrador**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Crea un usuario administrador**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Restablecer superconjunto**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Problema 2: falla la conexión a la base de datos

**Síntomas** :
- El botón "Probar conexión" falla
- Error: "No se puede conectar a la base de datos"

**Diagnóstico**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Soluciones**:

1. **Utilice el URI de SQLAlchemy correcto**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Instale los controladores necesarios**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Comprueba la red**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problema 3: los gráficos no se cargan

**Síntomas** :
- El panel muestra un control giratorio de carga indefinidamente
- Los gráficos muestran "Error al cargar datos".

**Diagnóstico**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Soluciones**:

1. **Verifique el tiempo de espera de la consulta**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Habilitar solicitudes asincrónicas**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Borrar caché**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Problema 4: errores de permisos

**Síntomas** :
- El usuario no puede ver los paneles
- Error: "No tienes acceso a este panel"

**Diagnóstico**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Soluciones**:

1. **Agregue el usuario a un rol**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Otorgar acceso al panel**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Consulte las reglas de RLS**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## Problemas de PostgreSQL

### Problema 1: Conexión rechazada

**Síntomas** :
- Las aplicaciones no pueden conectarse a PostgreSQL
- Error: "Conexión rechazada" o "No se pudo conectar"

**Diagnóstico**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Soluciones**:

1. **Reinicie PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

2. **Compruebe la asignación de puertos**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Verificar credenciales**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Problema 2: Falta de conexiones

**Síntomas** :
- Error: "FATAL: las ranuras de conexión restantes están reservadas"
- Las aplicaciones fallan intermitentemente al conectarse

**Diagnóstico**:
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

**Soluciones**:

1. **Aumentar max_connections**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Usar agrupación de conexiones**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Eliminar conexiones inactivas**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Problema 3: consultas lentas

**Síntomas** :
- Las consultas a la base de datos tardan varios segundos.
- Las aplicaciones caducan

**Diagnóstico**:
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

**Soluciones**:

1. **Crear índices**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Ejecute ANALIZAR**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Aumentar los buffers_compartidos**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##Problemas con MinIO

### Problema 1: No se puede acceder a la consola MinIO

**Síntomas** :
- El navegador muestra un error en `http://localhost:9001`

**Diagnóstico**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Soluciones**:

1. **Compruebe los puertos**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Acceda a la URL correcta**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Reinicie MinIO**:
   ```bash
   docker-compose restart minio
   ```

### Problema 2: Errores de acceso denegado

**Síntomas** :
- Las aplicaciones no pueden leer/escribir en S3
- Error: "Acceso denegado" o "403 prohibido"

**Diagnóstico**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Soluciones**:

1. **Verificar credenciales**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Consulta la política del depósito**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Crea una clave de acceso para la aplicación**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Problema 3: depósito no encontrado

**Síntomas** :
- Error: "El depósito especificado no existe"

**Diagnóstico**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Soluciones**:

1. **Crea el depósito**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Verifique el nombre del depósito en la configuración**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Red y conectividad

### Problema: los servicios no pueden comunicarse

**Síntomas** :
- "Conexión rechazada" entre contenedores
- Errores de "Host no encontrado"

**Diagnóstico**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Soluciones**:

1. **Asegúrese de que todos los servicios estén en la misma red**:
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

2. **Utilice nombres de contenedores, no localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Recrea la red**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Problemas de rendimiento

### Problema: uso elevado de CPU

**Diagnóstico**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Soluciones**:

1. **Limitar solicitudes competidoras**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Optimizar consultas** (consulte [Problemas de Dremio](#dremio-issues))

3. **Aumentar la asignación de CPU**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Problema: uso elevado de memoria

**Diagnóstico**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Soluciones**:

1. **Aumentar el tamaño del montón**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Habilitar el desbordamiento del disco**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Problemas de calidad de los datos

Consulte las soluciones detalladas en la [Guía de calidad de datos] (./data-quality.md).

### Comprobaciones rápidas

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

## Resumen

Esta guía de solución de problemas cubrió:

- **Enfoque general**: Metodología sistemática para el diagnóstico de problemas.
- **Problemas por componente**: Soluciones para los 7 servicios de la plataforma
- **Problemas de red**: problemas de conectividad de contenedores
- **Problemas de rendimiento**: CPU, memoria y optimización de consultas
- **Problemas de calidad de datos**: problemas y comprobaciones de datos comunes

**Conclusiones clave**:
- Siempre verifique primero los registros: `docker-compose logs [service]`
- Utilice nombres de contenedores, no localhost, para la comunicación entre servicios.
- Prueba de conectividad: `docker exec [container] ping [target]`
- Monitorear recursos: `docker stats`
- Comience simple: reinicie el servicio antes de una depuración compleja

**Documentación relacionada:**
- [Guía de instalación](../getting-started/installation.md)
- [Guía de configuración](../getting-started/configuration.md)
- [Guía de calidad de datos] (./data-quality.md)
- [Arquitectura: Implementación](../architecture/deployment.md)

**¿Necesitas más ayuda?**
- Verifique los registros del componente: `docker-compose logs -f [service]`
- Consultar la documentación del servicio.
- Buscar problemas de GitHub
- Póngase en contacto con el equipo de soporte

---

**Versión**: 3.2.0  
**Última actualización**: 16 de octubre de 2025