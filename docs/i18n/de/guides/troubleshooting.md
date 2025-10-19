# Leitfaden zur Fehlerbehebung

**Version**: 3.2.0  
**Letzte Aktualisierung**: 16. Oktober 2025  
**Sprache**: Französisch

## Inhaltsverzeichnis

1. [Übersicht](#Übersicht)
2. [Allgemeiner Ansatz zur Fehlerbehebung](#general-troubleshooting-approach)
3. [Airbyte-Probleme](#airbyte-problems)
4. [Dremio-Probleme](#dremio-problems)
5. [dbt-Probleme](#dbt-problems)
6. [Superset-Probleme](#superset-problems)
7. [PostgreSQL-Probleme](#postgresql-problems)
8. [MinIO-Probleme](#minio-problems)
9. [Elasticsearch-Probleme](#elasticsearch-issues)
10. [Netzwerk und Konnektivität](#network-and-connectivity)
11. [Leistungsprobleme](#performance-issues)
12. [Datenqualitätsprobleme](#data-quality-issues)

---

## Übersicht

Dieser umfassende Leitfaden zur Fehlerbehebung hilft Ihnen bei der Diagnose und Lösung häufiger Probleme bei allen Plattformkomponenten. Probleme werden nach Komponenten mit klaren Symptomen, Diagnosen und Lösungen geordnet.

### Methodik zur Fehlerbehebung

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

## Allgemeiner Ansatz zur Fehlerbehebung

### Schritt 1: Überprüfen Sie den Status der Dienste

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

### Schritt 2: Protokolle prüfen

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Schritt 3: Überprüfen Sie die Netzwerkkonnektivität

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Schritt 4: Überprüfen Sie die Ressourcennutzung

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Häufige Schnelllösungen

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

## Airbyte-Probleme

### Problem 1: Airbyte-Schnittstelle wird nicht geladen

**Symptome**:
- Der Browser zeigt „Verbindung nicht möglich“ oder Zeitüberschreitung an
- URL: `http://localhost:8000` antwortet nicht

**Diagnose**:
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Lösungen**:

1. **Überprüfen Sie, ob der Port nicht verwendet wird**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Airbyte-Container neu starten**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Überprüfen Sie, ob der Server fehlerfrei ist**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Problem 2: Synchronisierung schlägt mit „Verbindungszeitüberschreitung“ fehl

**Symptome**:
– Die Synchronisierungsaufgabe schlägt sofort fehl oder bleibt hängen
- Fehler: „Verbindungszeitüberschreitung“ oder „Verbindung zur Quelle konnte nicht hergestellt werden“

**Diagnose**:
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Lösungen**:

1. **Quellenkennungen prüfen**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Erhöhen Sie das Timeout**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Überprüfen Sie das Netzwerk**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problem 3: Nicht genügend Speicher während der Synchronisierung

**Symptome**:
– Der Container-Worker stürzt bei großen Synchronisierungen ab
- Fehler: „OutOfMemoryError“ oder „Java-Heap-Speicherplatz“

**Diagnose**:
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Lösungen**:

1. **Arbeitsspeicher erhöhen**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Stapelgröße reduzieren**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Inkrementelle Synchronisierung verwenden**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Problem 4: Daten erscheinen nicht im Ziel

**Symptome**:
- Die Synchronisierung wurde erfolgreich abgeschlossen
- Keine Fehler in den Protokollen
- Daten befinden sich nicht in MinIO/Ziel

**Diagnose**:
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Lösungen**:

1. **Überprüfen Sie die Zielkonfiguration**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Normalisierung prüfen**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Manuelle Überprüfung**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Dremio-Probleme

### Problem 1: Es kann keine Verbindung zur Dremio-Schnittstelle hergestellt werden

**Symptome**:
- Browser zeigt Verbindungsfehler bei `http://localhost:9047` an

**Diagnose**:
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Lösungen**:

1. **Warten Sie auf den vollständigen Start** (kann 2-3 Minuten dauern):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Speicher erhöhen**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Dremio-Daten bereinigen** (⚠️ setzt die Konfiguration zurück):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Problem 2: „Offline-Quelle“ für MinIO

**Symptome**:
- Die MinIO-Quelle zeigt eine rote „Offline“-Anzeige an
- Fehler: „Verbindung zur Quelle konnte nicht hergestellt werden“

**Diagnose**:
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Lösungen**:

1. **Überprüfen Sie den MinIO-Endpunkt**:
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

2. **Zugangsdaten prüfen**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Metadaten aktualisieren**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Problem 3: Langsame Abfrageleistung

**Symptome**:
- Abfragen dauern mehr als 10 Sekunden
- Dashboards werden langsam geladen

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

**Lösungen**:

1. **Reflexionen erstellen**:
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

2. **Partitionsfilter hinzufügen**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Executor-Speicher erhöhen**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Problem 4: Reflexion baut sich nicht auf

**Symptome**:
- Die Reflexion bleibt im Status „REFRESHING“ hängen
- Niemals enden

**Diagnose**:
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Lösungen**:

1. **Deaktivieren und erneut aktivieren**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Quelldaten prüfen**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Erhöhen Sie das Timeout**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## DBT-Probleme

### Problem 1: „Verbindungsfehler“ beim Ausführen von dbt

**Symptome**:
- `dbt debug` schlägt fehl
- Fehler: „Verbindung zu Dremio konnte nicht hergestellt werden“

**Diagnose**:
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Lösungen**:

1. **Profile.yml prüfen**:
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

2. **Dremio-Konnektivität testen**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Installieren Sie den Dremio-Adapter**:
   ```bash
   pip install dbt-dremio
   ```

### Problem 2: Das Modell kann nicht erstellt werden

**Symptome**:
- `dbt run` schlägt für ein bestimmtes Modell fehl
- SQL-Kompilierungs- oder Ausführungsfehler

**Diagnose**:
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Lösungen**:

1. **Modellsyntax prüfen**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Zuerst in einer SQL-IDE testen**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Abhängigkeiten prüfen**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Problem 3: Tests schlagen fehl

**Symptome**:
- `dbt test` meldet Fehler
- Es wurden Probleme mit der Datenqualität festgestellt

**Diagnose**:
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Lösungen**:

1. **Korrigieren Sie die Quelldaten**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Passen Sie den Testschwellenwert an**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Untersuchen Sie die Grundursache**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Problem 4: Inkrementelles Modell funktioniert nicht

**Symptome**:
- Das inkrementelle Modell wird bei jeder Ausführung vollständig neu erstellt
- Kein inkrementelles Verhalten

**Diagnose**:
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Lösungen**:

1. **Systemanforderungen hinzufügen**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Inkrementelle Logik hinzufügen**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Einmalige vollständige Aktualisierung erzwingen**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Superset-Probleme

### Problem 1: Es kann keine Verbindung zu Superset hergestellt werden

**Symptome**:
- Auf der Anmeldeseite wird „Ungültige Anmeldeinformationen“ angezeigt.
- Das Standardpaar Admin/Administrator funktioniert nicht

**Diagnose**:
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Lösungen**:

1. **Administratorpasswort zurücksetzen**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Erstellen Sie einen Admin-Benutzer**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Obermenge zurücksetzen**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Problem 2: Datenbankverbindung schlägt fehl

**Symptome**:
- Die Schaltfläche „Verbindung testen“ schlägt fehl
- Fehler: „Verbindung zur Datenbank kann nicht hergestellt werden“

**Diagnose**:
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Lösungen**:

1. **Verwenden Sie den richtigen SQLAlchemy-URI**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Installieren Sie die erforderlichen Treiber**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Überprüfen Sie das Netzwerk**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problem 3: Diagramme werden nicht geladen

**Symptome**:
- Das Dashboard zeigt auf unbestimmte Zeit einen Lade-Spinner an
- Diagramme zeigen „Fehler beim Laden der Daten“ an

**Diagnose**:
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Lösungen**:

1. **Abfrage-Timeout prüfen**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Asynchrone Anfragen aktivieren**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Cache leeren**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Problem 4: Berechtigungsfehler

**Symptome**:
- Der Benutzer kann keine Dashboards sehen
- Fehler: „Sie haben keinen Zugriff auf dieses Dashboard“

**Diagnose**:
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Lösungen**:

1. **Fügen Sie den Benutzer einer Rolle hinzu**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Zugriff auf das Dashboard gewähren**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Überprüfen Sie die RLS-Regeln**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL-Probleme

### Problem 1: Verbindung abgelehnt

**Symptome**:
- Anwendungen können keine Verbindung zu PostgreSQL herstellen
- Fehler: „Verbindung abgelehnt“ oder „Verbindung konnte nicht hergestellt werden“

**Diagnose**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Lösungen**:

1. **PostgreSQL neu starten**:
   ```bash
   docker-compose restart postgres
   ```

2. **Portzuordnung prüfen**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Zugangsdaten prüfen**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Problem 2: Fehlende Verbindungen

**Symptome**:
- Fehler: „FATAL: verbleibende Verbindungsslots sind reserviert“
- Apps können zeitweise keine Verbindung herstellen

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

**Lösungen**:

1. **Max_Verbindungen erhöhen**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Verbindungspooling verwenden**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Leere Verbindungen beenden**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Problem 3: Langsame Abfragen

**Symptome**:
- Datenbankabfragen dauern mehrere Sekunden
- Apps laufen ab

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

**Lösungen**:

1. **Indizes erstellen**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **ANALYZE ausführen**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Shared_buffers erhöhen**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO-Probleme

### Problem 1: Zugriff auf die MinIO-Konsole nicht möglich

**Symptome**:
- Der Browser zeigt einen Fehler bei `http://localhost:9001` an

**Diagnose**:
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Lösungen**:

1. **Ports prüfen**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Greifen Sie auf die richtige URL zu**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **MinIO neu starten**:
   ```bash
   docker-compose restart minio
   ```

### Problem 2: Fehler „Zugriff verweigert“.

**Symptome**:
- Anwendungen können nicht auf S3 lesen/schreiben
- Fehler: „Zugriff verweigert“ oder „403 verboten“

**Diagnose**:
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Lösungen**:

1. **Zugangsdaten prüfen**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Überprüfen Sie die Bucket-Richtlinie**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Erstellen Sie einen Zugriffsschlüssel für die Anwendung**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Problem 3: Bucket nicht gefunden

**Symptome**:
- Fehler: „Der angegebene Bucket existiert nicht“

**Diagnose**:
```bash
# List all buckets
docker exec minio mc ls local/
```

**Lösungen**:

1. **Bucket erstellen**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Überprüfen Sie den Bucket-Namen in der Konfiguration**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Netzwerk und Konnektivität

### Problem: Dienste können nicht kommunizieren

**Symptome**:
- „Verbindung abgelehnt“ zwischen Containern
- „Host nicht gefunden“-Fehler

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

**Lösungen**:

1. **Stellen Sie sicher, dass sich alle Dienste im selben Netzwerk befinden**:
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

2. **Containernamen verwenden, nicht localhost**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Erstellen Sie das Netzwerk neu**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Leistungsprobleme

### Problem: Hohe CPU-Auslastung

**Diagnose**:
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Lösungen**:

1. **Konkurrierende Anfragen begrenzen**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Abfragen optimieren** (siehe [Dremio-Probleme](#dremio-issues))

3. **CPU-Zuteilung erhöhen**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Problem: Hohe Speichernutzung

**Diagnose**:
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Lösungen**:

1. **Heap-Größe erhöhen**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Festplattenüberlauf aktivieren**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Probleme mit der Datenqualität

Sehen Sie sich die Lösungen im [Datenqualitätsleitfaden](./data-quality.md) an.

### Schnelle Kontrollen

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

## Zusammenfassung

In diesem Leitfaden zur Fehlerbehebung wurde Folgendes behandelt:

- **Allgemeiner Ansatz**: Systematische Methodik zur Problemdiagnose
- **Probleme nach Komponenten**: Lösungen für die 7 Dienste der Plattform
- **Netzwerkprobleme**: Probleme mit der Containerkonnektivität
- **Leistungsprobleme**: CPU-, Speicher- und Abfrageoptimierung
- **Datenqualitätsprobleme**: Häufige Datenprobleme und -prüfungen

**Wichtige Erkenntnisse**:
- Überprüfen Sie immer zuerst die Protokolle: `docker-compose logs [service]`
– Verwenden Sie für die Kommunikation zwischen Diensten Containernamen und nicht „localhost“.
- Konnektivität testen: `docker exec [container] ping [target]`
- Ressourcen überwachen: `docker stats`
- Einfach starten: Starten Sie den Dienst vor dem komplexen Debuggen neu

**Zugehörige Dokumentation:**
- [Installationsanleitung](../getting-started/installation.md)
- [Konfigurationshandbuch](../getting-started/configuration.md)
- [Datenqualitätsleitfaden](./data-quality.md)
- [Architektur: Bereitstellung](../architecture/deployment.md)

**Benötigen Sie weitere Hilfe?**
- Überprüfen Sie die Komponentenprotokolle: `docker-compose logs -f [service]`
- Konsultieren Sie die Servicedokumentation
- Suchen Sie nach GitHub-Problemen
- Kontaktieren Sie das Support-Team

---

**Version**: 3.2.0  
**Letzte Aktualisierung**: 16. Oktober 2025