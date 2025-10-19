# Gids voor probleemoplossing

**Versie**: 3.2.0  
**Laatst bijgewerkt**: 16 oktober 2025  
**Taal**: Frans

## Inhoudsopgave

1. [Overzicht](#overzicht)
2. [Algemene aanpak voor probleemoplossing](#general-troubleshooting-approach)
3. [Airbyte-problemen](#airbyte-problemen)
4. [Dremio-problemen](#dremio-problemen)
5. [dbt-problemen](#dbt-problemen)
6. [Superset-problemen](#superset-problemen)
7. [PostgreSQL-problemen](#postgresql-problemen)
8. [MinIO-problemen](#minio-problemen)
9. [Elasticsearch-problemen](#elasticsearch-issues)
10. [Netwerk en connectiviteit](#network-and-connectivity)
11. [Prestatieproblemen](#performance-issues)
12. [Problemen met de gegevenskwaliteit](#data-quality-issues)

---

## Overzicht

Met deze uitgebreide gids voor probleemoplossing kunt u veelvoorkomende problemen in alle platformcomponenten diagnosticeren en oplossen. Problemen zijn geordend per onderdeel met duidelijke symptomen, diagnostiek en oplossingen.

### Methodologie voor probleemoplossing

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

## Algemene aanpak voor probleemoplossing

### Stap 1: Controleer de status van services

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

### Stap 2: Controleer logboeken

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Stap 3: Controleer de netwerkconnectiviteit

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Stap 4: Controleer het bronnengebruik

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Veelvoorkomende snelle oplossingen

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

## Airbyte-problemen

### Probleem 1: Airbyte-interface wordt niet geladen

**Symptomen**:
- De browser geeft "Kan geen verbinding maken" of time-out weer
- URL: `http://localhost:8000` reageert niet

**Diagnose**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Oplossingen**:

1. **Controleer of de poort niet in gebruik is**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Airbyte Containers opnieuw opstarten**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Controleer of de server in orde is**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Probleem 2: Synchronisatie mislukt met "Connection Timeout"

**Symptomen**:
- Synchronisatietaak mislukt onmiddellijk of loopt vast
- Fout: "Verbindingstime-out" of "Kan geen verbinding maken met de bron"

**Diagnose**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Oplossingen**:

1. **Controleer bron-ID's**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Verhoog de time-out**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Controleer het netwerk**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Probleem 3: Onvoldoende geheugen tijdens synchronisatie

**Symptomen**:
- Containerwerker loopt vast tijdens grote synchronisaties
- Fout: "OutOfMemoryError" of "Java-heapruimte"

**Diagnose**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Oplossingen**:

1. **Vergroot het geheugen van werknemers**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Verminder de batchgrootte**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Gebruik incrementele synchronisatie**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Probleem 4: Gegevens verschijnen niet op de bestemming

**Symptomen**:
- Synchronisatie is succesvol voltooid
- Geen fouten in de logs
- Gegevens bevinden zich niet in MinIO/bestemming

**Diagnose**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Oplossingen**:

1. **Controleer de bestemmingsconfiguratie**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Controleer normalisatie**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Handmatige verificatie**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Dremio-problemen

### Probleem 1: Kan geen verbinding maken met de Dremio-interface

**Symptomen**:
- Browser toont verbindingsfout bij `http://localhost:9047`

**Diagnose**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Oplossingen**:

1. **Wacht tot het volledig is opgestart** (kan 2-3 minuten duren):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Vergroot het geheugen**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Dremio-gegevens opschonen** (⚠️ reset configuratie):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Probleem 2: "Offline bron" voor MinIO

**Symptomen**:
- De MinIO-bron geeft een rode “Offline”-indicator weer
- Fout: "Kan geen verbinding maken met de bron"

**Diagnose**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Oplossingen**:

1. **Controleer het MinIO-eindpunt**:
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

2. **Controleer inloggegevens**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Metagegevens vernieuwen**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Probleem 3: Trage queryprestaties

**Symptomen**:
- Zoekopdrachten duren meer dan 10 seconden
- Dashboards laden traag

**Diagnose**:
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

**Oplossingen**:

1. **Maak reflecties**:
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

2. **Partitiefilters toevoegen**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Vergroot het geheugen van de uitvoerder**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Probleem 4: Reflectie bouwt niet op

**Symptomen**:
- Reflectie blijft hangen in de status "REFRESHING".
- Eindigt nooit

**Diagnose**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Oplossingen**:

1. **Uitschakelen en opnieuw inschakelen**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Controleer brongegevens**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Verhoog de time-out**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## dbt-problemen

### Probleem 1: "Verbindingsfout" bij het uitvoeren van dbt

**Symptomen**:
- `dbt debug` mislukt
- Fout: "Kan geen verbinding maken met Dremio"

**Diagnose**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Oplossingen**:

1. **Controleer profielen.yml**:
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

2. **Dremio-connectiviteit testen**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Installeer de Dremio-adapter**:
   ```bash
   pip install dbt-dremio
   ```

### Probleem 2: Het model kan niet worden gebouwd

**Symptomen**:
- `dbt run` mislukt voor een specifiek model
- SQL-compilatie- of uitvoeringsfout

**Diagnose**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Oplossingen**:

1. **Controleer de syntaxis van het model**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Eerst testen in een SQL IDE**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Controleer afhankelijkheden**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Probleem 3: Tests mislukken

**Symptomen**:
- `dbt test` meldt fouten
- Er zijn problemen met de gegevenskwaliteit gedetecteerd

**Diagnose**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Oplossingen**:

1. **Corrigeer de brongegevens**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Pas de testdrempel aan**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Onderzoek de oorzaak**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Probleem 4: Incrementeel model werkt niet

**Symptomen**:
- Het incrementele model wordt elke keer dat het wordt uitgevoerd volledig opnieuw opgebouwd
- Geen incrementeel gedrag

**Diagnose**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Oplossingen**:

1. **Systeemvereisten toevoegen**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Voeg incrementele logica toe**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Forceer één keer een volledige vernieuwing**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Superset-problemen

### Probleem 1: Kan geen verbinding maken met Superset

**Symptomen**:
- Inlogpagina toont "Ongeldige inloggegevens"
- Het standaard admin/admin-paar werkt niet

**Diagnose**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Oplossingen**:

1. **Beheerderswachtwoord opnieuw instellen**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Maak een admin-gebruiker**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Superset opnieuw instellen**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Probleem 2: Databaseverbinding mislukt

**Symptomen**:
- De knop “Testverbinding” mislukt
- Fout: "Kan geen verbinding maken met database"

**Diagnose**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Oplossingen**:

1. **Gebruik de juiste SQLAlchemy-URI**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Installeer de vereiste stuurprogramma's**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Controleer het netwerk**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Probleem 3: Grafieken worden niet geladen

**Symptomen**:
- Dashboard geeft voor onbepaalde tijd een laadspinner weer
- Grafieken tonen "Fout bij laden van gegevens"

**Diagnose**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Oplossingen**:

1. **Controleer de time-out van de query**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Asynchrone verzoeken inschakelen**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Cache wissen**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Probleem 4: Machtigingsfouten

**Symptomen**:
- Gebruiker kan dashboards niet zien
- Fout: "U heeft geen toegang tot dit dashboard"

**Diagnose**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Oplossingen**:

1. **Voeg de gebruiker toe aan een rol**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Verleen toegang tot het dashboard**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Controleer de RLS-regels**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL-problemen

### Probleem 1: Verbinding geweigerd

**Symptomen**:
- Applicaties kunnen geen verbinding maken met PostgreSQL
- Fout: "Verbinding geweigerd" of "Kan geen verbinding maken"

**Diagnose**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Oplossingen**:

1. **PostgreSQL opnieuw starten**:
   ```bash
   docker-compose restart postgres
   ```

2. **Controleer poorttoewijzing**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Controleer inloggegevens**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Probleem 2: Gebrek aan verbindingen

**Symptomen**:
- Fout: "FATAL: resterende verbindingsslots zijn gereserveerd"
- Apps kunnen af ​​en toe geen verbinding maken

**Diagnose**:
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

**Oplossingen**:

1. **Max. verbindingen verhogen**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Gebruik verbindingspooling**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Inactieve verbindingen uitschakelen**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Probleem 3: Trage zoekopdrachten

**Symptomen**:
- Databasequery's duren enkele seconden
- Apps verlopen

**Diagnose**:
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

**Oplossingen**:

1. **Indices maken**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Voer ANALYSEREN uit**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Gedeelde_buffers vergroten**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO-problemen

### Probleem 1: Geen toegang tot de MinIO-console

**Symptomen**:
- De browser geeft een foutmelding weer bij `http://localhost:9001`

**Diagnose**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Oplossingen**:

1. **Controleer poorten**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Ga naar de juiste URL**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Herstart MinIO**:
   ```bash
   docker-compose restart minio
   ```

### Probleem 2: Fouten met toegang geweigerd

**Symptomen**:
- Applicaties kunnen niet lezen/schrijven naar S3
- Fout: "Toegang geweigerd" of "403 verboden"

**Diagnose**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Oplossingen**:

1. **Controleer inloggegevens**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Controleer het bucketbeleid**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Maak een toegangssleutel voor de applicatie**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Probleem 3: Emmer niet gevonden

**Symptomen**:
- Fout: "De opgegeven bucket bestaat niet"

**Diagnose**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Oplossingen**:

1. **Maak de bucket**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Controleer de bucketnaam in de configuratie**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Netwerk en connectiviteit

### Probleem: Services kunnen niet communiceren

**Symptomen**:
- "Verbinding geweigerd" tussen containers
- Foutmelding 'Host niet gevonden'

**Diagnose**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Oplossingen**:

1. **Zorg ervoor dat alle services zich op hetzelfde netwerk bevinden**:
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

2. **Gebruik containernamen, niet localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Maak het netwerk opnieuw**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Prestatieproblemen

### Probleem: Hoog CPU-gebruik

**Diagnose**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Oplossingen**:

1. **Beperk concurrerende verzoeken**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Optimaliseer zoekopdrachten** (zie [Dremio-problemen](#dremio-issues))

3. **CPU-toewijzing verhogen**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Probleem: Hoog geheugengebruik

**Diagnose**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Oplossingen**:

1. **Vergroot de heapgrootte**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Schakel het morsen van schijven in**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Problemen met de gegevenskwaliteit

Zie de oplossingen die worden beschreven in de [Handleiding gegevenskwaliteit](./data-quality.md).

### Snelle controles

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

## Samenvatting

Deze gids voor probleemoplossing omvat:

- **Algemene aanpak**: Systematische methodologie voor het diagnosticeren van problemen
- **Problemen per component**: oplossingen voor de 7 diensten van het platform
- **Netwerkproblemen**: problemen met de containerconnectiviteit
- **Prestatieproblemen**: CPU-, geheugen- en query-optimalisatie
- **Gegevenskwaliteitsproblemen**: veelvoorkomende gegevensproblemen en -controles

**Belangrijkste inzichten**:
- Controleer altijd eerst de logs: `docker-compose logs [service]`
- Gebruik containernamen, niet localhost, voor communicatie tussen services
- Connectiviteit testen: `docker exec [container] ping [target]`
- Bronnen monitoren: `docker stats`
- Begin eenvoudig: start de service opnieuw voordat u complexe foutopsporing uitvoert

**Gerelateerde documentatie:**
- [Installatiehandleiding](../getting-started/installation.md)
- [Configuratiegids](../getting-started/configuration.md)
- [Handleiding gegevenskwaliteit](./data-quality.md)
- [Architectuur: implementatie](../architecture/deployment.md)

**Meer hulp nodig?**
- Controleer de componentlogboeken: `docker-compose logs -f [service]`
- Raadpleeg de servicedocumentatie
- Zoek naar GitHub-problemen
- Neem contact op met het ondersteuningsteam

---

**Versie**: 3.2.0  
**Laatst bijgewerkt**: 16 oktober 2025