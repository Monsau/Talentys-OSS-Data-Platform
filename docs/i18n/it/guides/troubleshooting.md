# Guida alla risoluzione dei problemi

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 16 ottobre 2025  
**Lingua**: francese

## Sommario

1. [Panoramica](#panoramica)
2. [Approccio generale alla risoluzione dei problemi](#approccio-generale alla risoluzione dei problemi)
3. [Problemi Airbyte](#problemi-airbyte)
4. [Problemi con Dremio](#dremio-problemi)
5. [problemi dbt](#problemi-dbt)
6. [Problemi nel superset](#problemi-superset)
7. [Problemi PostgreSQL](#problemi postgresql)
8. [Problemi con MinIO](#minio-problemi)
9. [Problemi di Elasticsearch](#elasticsearch-problemi)
10. [Rete e connettività](#rete-e-connettività)
11. [Problemi di prestazioni](#problemi di prestazioni)
12. [Problemi di qualità dei dati](#problemi di qualità dei dati)

---

## Panoramica

Questa guida completa alla risoluzione dei problemi ti aiuta a diagnosticare e risolvere i problemi comuni su tutti i componenti della piattaforma. I problemi sono organizzati per componente con sintomi, diagnostica e soluzioni chiari.

### Metodologia di risoluzione dei problemi

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

## Approccio generale alla risoluzione dei problemi

### Passaggio 1: controlla lo stato dei servizi

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

### Passaggio 2: controlla i log

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Passaggio 3: verifica la connettività di rete

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Passaggio 4: controlla l'utilizzo delle risorse

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Soluzioni rapide comuni

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

## Problemi con Airbyte

### Problema 1: l'interfaccia Airbyte non si carica

**Sintomi**:
- Il browser visualizza "Impossibile connettersi" o timeout
- URL: `http://localhost:8000` non risponde

**Diagnosi**:
§§§CODICE_7§§§

**Soluzioni**:

1. **Verifica che la porta non sia in uso**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Riavvia i contenitori Airbyte**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Verifica che il server sia integro**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Problema 2: la sincronizzazione non riesce con "Timeout connessione"

**Sintomi**:
- L'attività di sincronizzazione fallisce o si blocca immediatamente
- Errore: "Timeout connessione" o "Impossibile connettersi alla sorgente"

**Diagnosi**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Soluzioni**:

1. **Controlla gli identificatori della fonte**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Aumenta il timeout**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Controlla la rete**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problema 3: memoria insufficiente durante la sincronizzazione

**Sintomi**:
- Il lavoratore del contenitore si arresta in modo anomalo durante sincronizzazioni di grandi dimensioni
- Errore: "OutOfMemoryError" o "spazio heap Java"

**Diagnosi**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Soluzioni**:

1. **Aumenta la memoria del lavoratore**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Riduci le dimensioni del batch**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Utilizza sincronizzazione incrementale**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Problema 4: i dati non vengono visualizzati nella destinazione

**Sintomi**:
- La sincronizzazione viene completata correttamente
- Nessun errore nei log
- I dati non sono nel MinIO/destinazione

**Diagnosi**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Soluzioni**:

1. **Controlla la configurazione della destinazione**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Controlla la normalizzazione**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Verifica manuale**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Problemi con Dremio

### Problema 1: impossibile connettersi all'interfaccia Dremio

**Sintomi**:
- Il browser mostra un errore di connessione su `http://localhost:9047`

**Diagnosi**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Soluzioni**:

1. **Attendere l'avvio completo** (potrebbero essere necessari 2-3 minuti):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Aumenta memoria**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Pulisci i dati di Dremio** (⚠️ ripristina la configurazione):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Problema 2: "Sorgente offline" per MinIO

**Sintomi**:
- La sorgente MinIO visualizza un indicatore rosso "Offline".
- Errore: "Impossibile connettersi alla sorgente"

**Diagnosi**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Soluzioni**:

1. **Controlla l'endpoint MinIO**:
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

2. **Verifica le credenziali**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Aggiorna metadati**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Problema 3: prestazioni lente delle query

**Sintomi**:
- Le query richiedono più di 10 secondi
- I dashboard sono lenti da caricare

**Diagnosi**:
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

**Soluzioni**:

1. **Crea riflessioni**:
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

2. **Aggiungi filtri partizione**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Aumenta la memoria dell'esecutore**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Problema 4: la riflessione non si costruisce

**Sintomi**:
- La riflessione rimane bloccata nello stato "REFRESHING".
- Non finisce mai

**Diagnosi**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Soluzioni**:

1. **Disabilita e riabilita**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Controlla i dati di origine**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Aumenta il timeout**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## problemi con il debito

### Problema 1: "Errore di connessione" durante l'esecuzione di dbt

**Sintomi**:
- `dbt debug` fallisce
- Errore: "Impossibile connettersi a Dremio"

**Diagnosi**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Soluzioni**:

1. **Controlla profiles.yml**:
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

2. **Prova la connettività Dremio**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Installa l'adattatore Dremio**:
   ```bash
   pip install dbt-dremio
   ```

### Problema 2: la creazione del modello non riesce

**Sintomi**:
- `dbt run` fallisce per un modello specifico
- Errore di compilazione o esecuzione SQL

**Diagnosi**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Soluzioni**:

1. **Controlla la sintassi del modello**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Testare prima in un IDE SQL**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Verifica le dipendenze**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Problema 3: i test falliscono

**Sintomi**:
- `dbt test` segnala i guasti
- Rilevati problemi di qualità dei dati

**Diagnosi**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Soluzioni**:

1. **Correggi i dati di origine**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Regola la soglia del test**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Indagare sulla causa principale**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Problema 4: il modello incrementale non funziona

**Sintomi**:
- Il modello incrementale viene completamente ricostruito ogni volta che viene eseguito
- Nessun comportamento incrementale

**Diagnosi**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Soluzioni**:

1. **Aggiungi requisiti di sistema**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Aggiungi logica incrementale**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Forza un aggiornamento completo una volta**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Problemi di superinsieme

### Problema 1: impossibile connettersi a Superset

**Sintomi**:
- La pagina di accesso visualizza "Credenziali non valide"
- La coppia amministratore/amministratore predefinita non funziona

**Diagnosi**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Soluzioni**:

1. **Reimposta password amministratore**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Crea un utente amministratore**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Ripristina superset**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Problema 2: la connessione al database non riesce

**Sintomi**:
- Il pulsante "Verifica connessione" non funziona
- Errore: "Impossibile connettersi al database"

**Diagnosi**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Soluzioni**:

1. **Utilizza l'URI SQLAlchemy corretto**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Installa i driver richiesti**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Controlla la rete**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problema 3: i grafici non vengono caricati

**Sintomi**:
- La dashboard visualizza uno spinner di caricamento a tempo indeterminato
- I grafici visualizzano "Errore durante il caricamento dei dati"

**Diagnosi**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Soluzioni**:

1. **Controlla il timeout della query**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Abilita richieste asincrone**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Svuota cache**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Problema 4: errori di autorizzazione

**Sintomi**:
- L'utente non può vedere i dashboard
- Errore: "Non hai accesso a questa dashboard"

**Diagnosi**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Soluzioni**:

1. **Aggiungi l'utente a un ruolo**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Concedi l'accesso alla dashboard**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Controlla le regole RLS**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## Problemi con PostgreSQL

### Problema 1: connessione rifiutata

**Sintomi**:
- Le applicazioni non possono connettersi a PostgreSQL
- Errore: "Connessione rifiutata" o "Impossibile connettersi"

**Diagnosi**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Soluzioni**:

1. **Riavvia PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

2. **Controlla la mappatura delle porte**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Controlla le credenziali**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Problema 2: mancanza di connessioni

**Sintomi**:
- Errore: "FATAL: gli slot di connessione rimanenti sono riservati"
- Le app a intermittenza non riescono a connettersi

**Diagnosi**:
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

**Soluzioni**:

1. **Aumenta max_connections**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Utilizzare il pool di connessioni**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Elimina le connessioni inattive**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Problema 3: query lente

**Sintomi**:
- Le query del database richiedono diversi secondi
- Le app scadono

**Diagnosi**:
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

**Soluzioni**:

1. **Crea indici**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Esegui ANALISI**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Aumenta shared_buffers**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##Problemi con MinIO

### Problema 1: impossibile accedere alla console MinIO

**Sintomi**:
- Il browser visualizza un errore in `http://localhost:9001`

**Diagnosi**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Soluzioni**:

1. **Controlla le porte**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Accedi all'URL corretto**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Riavvia MinIO**:
   ```bash
   docker-compose restart minio
   ```

### Problema 2: errori di accesso negato

**Sintomi**:
- Le applicazioni non possono leggere/scrivere su S3
- Errore: "Accesso negato" o "403 Vietato"

**Diagnosi**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Soluzioni**:

1. **Verifica le credenziali**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Controlla la politica del bucket**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Crea una chiave di accesso per l'applicazione**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Problema 3: bucket non trovato

**Sintomi**:
- Errore: "Il bucket specificato non esiste"

**Diagnosi**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Soluzioni**:

1. **Crea il bucket**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Controlla il nome del bucket nella configurazione**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Rete e connettività

### Problema: i servizi non possono comunicare

**Sintomi**:
- "Connessione rifiutata" tra contenitori
- Errori "Host non trovato".

**Diagnosi**:
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Soluzioni**:

1. **Assicurarsi che tutti i servizi siano sulla stessa rete**:
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

2. **Utilizza nomi di contenitori, non localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Ricrea la rete**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Problemi di prestazioni

### Problema: utilizzo elevato della CPU

**Diagnosi**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Soluzioni**:

1. **Limita richieste concorrenti**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Ottimizza le query** (vedi [Problemi di Dremio](#dremio-issues))

3. **Aumenta l'allocazione della CPU**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Problema: utilizzo elevato della memoria

**Diagnosi**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Soluzioni**:

1. **Aumenta la dimensione dell'heap**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Abilita la distribuzione del disco**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Problemi di qualità dei dati

Consulta le soluzioni dettagliate nella [Guida alla qualità dei dati](./data-quality.md).

### Controlli rapidi

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

## Riepilogo

Questa guida alla risoluzione dei problemi riguardava:

- **Approccio generale**: metodologia sistematica per la diagnosi dei problemi
- **Problemi per componente**: Soluzioni per i 7 servizi della piattaforma
- **Problemi di rete**: problemi di connettività del contenitore
- **Problemi di prestazioni**: CPU, memoria e ottimizzazione delle query
- **Problemi relativi alla qualità dei dati**: problemi e controlli comuni sui dati

**Aspetti principali**:
- Controlla sempre prima i log: `docker-compose logs [service]`
- Utilizzare nomi di contenitori, non localhost, per la comunicazione tra servizi
- Prova connettività: `docker exec [container] ping [target]`
- Monitorare le risorse: `docker stats`
- Avvia semplice: riavvia il servizio prima del debug complesso

**Documentazione correlata:**
- [Guida all'installazione](../getting-started/installation.md)
- [Guida alla configurazione](../getting-started/configuration.md)
- [Guida alla qualità dei dati](./data-quality.md)
- [Architettura: Distribuzione](../architecture/deployment.md)

**Hai bisogno di ulteriore aiuto?**
- Controlla i log dei componenti: `docker-compose logs -f [service]`
- Consultare la documentazione del servizio
- Cerca problemi su GitHub
- Contatta il team di supporto

---

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 16 ottobre 2025