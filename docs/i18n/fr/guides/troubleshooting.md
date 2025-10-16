# Guide de dépannage

**Version** : 3.2.0  
**Dernière mise à jour** : 16 octobre 2025  
**Langue** : Français

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Approche générale de dépannage](#approche-générale-de-dépannage)
3. [Problèmes Airbyte](#problèmes-airbyte)
4. [Problèmes Dremio](#problèmes-dremio)
5. [Problèmes dbt](#problèmes-dbt)
6. [Problèmes Superset](#problèmes-superset)
7. [Problèmes PostgreSQL](#problèmes-postgresql)
8. [Problèmes MinIO](#problèmes-minio)
9. [Problèmes Elasticsearch](#problèmes-elasticsearch)
10. [Réseau et connectivité](#réseau-et-connectivité)
11. [Problèmes de performance](#problèmes-de-performance)
12. [Problèmes de qualité des données](#problèmes-de-qualité-des-données)

---

## Vue d'ensemble

Ce guide de dépannage complet vous aide à diagnostiquer et résoudre les problèmes courants sur tous les composants de la plateforme. Les problèmes sont organisés par composant avec des symptômes, diagnostics et solutions clairs.

### Méthodologie de dépannage

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

## Approche générale de dépannage

### Étape 1 : Vérifier l'état des services

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

### Étape 2 : Vérifier les logs

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### Étape 3 : Vérifier la connectivité réseau

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### Étape 4 : Vérifier l'utilisation des ressources

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### Corrections rapides courantes

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

## Problèmes Airbyte

### Problème 1 : L'interface Airbyte ne se charge pas

**Symptômes** :
- Le navigateur affiche "Cannot connect" ou timeout
- URL : `http://localhost:8000` ne répond pas

**Diagnostic** :
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**Solutions** :

1. **Vérifier que le port n'est pas utilisé** :
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Redémarrer les conteneurs Airbyte** :
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **Vérifier que le serveur est sain** :
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### Problème 2 : La synchronisation échoue avec "Connection Timeout"

**Symptômes** :
- La tâche de synchronisation échoue immédiatement ou se bloque
- Erreur : "Connection timeout" ou "Unable to connect to source"

**Diagnostic** :
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**Solutions** :

1. **Vérifier les identifiants de la source** :
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **Augmenter le timeout** :
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **Vérifier le réseau** :
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problème 3 : Manque de mémoire pendant la synchronisation

**Symptômes** :
- Le conteneur worker crash pendant les grandes synchronisations
- Erreur : "OutOfMemoryError" ou "Java heap space"

**Diagnostic** :
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**Solutions** :

1. **Augmenter la mémoire du worker** :
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **Réduire la taille des lots** :
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **Utiliser la synchronisation incrémentale** :
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### Problème 4 : Les données n'apparaissent pas dans la destination

**Symptômes** :
- La synchronisation se termine avec succès
- Aucune erreur dans les logs
- Les données ne sont pas dans MinIO/destination

**Diagnostic** :
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**Solutions** :

1. **Vérifier la configuration de la destination** :
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **Vérifier la normalisation** :
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **Vérification manuelle** :
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## Problèmes Dremio

### Problème 1 : Impossible de se connecter à l'interface Dremio

**Symptômes** :
- Le navigateur affiche une erreur de connexion à `http://localhost:9047`

**Diagnostic** :
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**Solutions** :

1. **Attendre le démarrage complet** (peut prendre 2-3 minutes) :
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **Augmenter la mémoire** :
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Nettoyer les données Dremio** (⚠️ réinitialise la configuration) :
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### Problème 2 : "Source Offline" pour MinIO

**Symptômes** :
- La source MinIO affiche un indicateur rouge "Offline"
- Erreur : "Unable to connect to source"

**Diagnostic** :
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**Solutions** :

1. **Vérifier le endpoint MinIO** :
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

2. **Vérifier les identifiants** :
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **Rafraîchir les métadonnées** :
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### Problème 3 : Performance de requête lente

**Symptômes** :
- Les requêtes prennent 10+ secondes
- Les tableaux de bord sont lents à charger

**Diagnostic** :
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

**Solutions** :

1. **Créer des reflections** :
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

2. **Ajouter des filtres de partition** :
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **Augmenter la mémoire de l'exécuteur** :
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### Problème 4 : La reflection ne se construit pas

**Symptômes** :
- La reflection reste bloquée en état "REFRESHING"
- Ne se termine jamais

**Diagnostic** :
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**Solutions** :

1. **Désactiver et réactiver** :
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **Vérifier les données source** :
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **Augmenter le timeout** :
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## Problèmes dbt

### Problème 1 : "Connection Error" lors de l'exécution de dbt

**Symptômes** :
- `dbt debug` échoue
- Erreur : "Could not connect to Dremio"

**Diagnostic** :
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**Solutions** :

1. **Vérifier profiles.yml** :
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

2. **Tester la connectivité Dremio** :
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Installer l'adaptateur Dremio** :
   ```bash
   pip install dbt-dremio
   ```

### Problème 2 : Le modèle ne parvient pas à se construire

**Symptômes** :
- `dbt run` échoue pour un modèle spécifique
- Erreur de compilation ou d'exécution SQL

**Diagnostic** :
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**Solutions** :

1. **Vérifier la syntaxe du modèle** :
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **Tester d'abord dans un IDE SQL** :
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **Vérifier les dépendances** :
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### Problème 3 : Les tests échouent

**Symptômes** :
- `dbt test` signale des échecs
- Problèmes de qualité des données détectés

**Diagnostic** :
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**Solutions** :

1. **Corriger les données source** :
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **Ajuster le seuil du test** :
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **Enquêter sur la cause racine** :
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### Problème 4 : Le modèle incrémental ne fonctionne pas

**Symptômes** :
- Le modèle incrémental se reconstruit entièrement à chaque exécution
- Aucun comportement incrémental

**Diagnostic** :
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**Solutions** :

1. **Ajouter la configuration requise** :
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **Ajouter la logique incrémentale** :
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **Forcer un rafraîchissement complet une fois** :
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## Problèmes Superset

### Problème 1 : Impossible de se connecter à Superset

**Symptômes** :
- La page de connexion affiche "Invalid credentials"
- Le couple admin/admin par défaut ne fonctionne pas

**Diagnostic** :
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**Solutions** :

1. **Réinitialiser le mot de passe admin** :
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **Créer un utilisateur admin** :
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **Réinitialiser Superset** :
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### Problème 2 : La connexion à la base de données échoue

**Symptômes** :
- Le bouton "Test Connection" échoue
- Erreur : "Cannot connect to database"

**Diagnostic** :
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**Solutions** :

1. **Utiliser l'URI SQLAlchemy correct** :
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **Installer les drivers requis** :
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **Vérifier le réseau** :
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### Problème 3 : Les graphiques ne se chargent pas

**Symptômes** :
- Le tableau de bord affiche indéfiniment un spinner de chargement
- Les graphiques affichent "Error loading data"

**Diagnostic** :
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**Solutions** :

1. **Vérifier le timeout de requête** :
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **Activer les requêtes asynchrones** :
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **Vider le cache** :
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### Problème 4 : Erreurs de permissions

**Symptômes** :
- L'utilisateur ne peut pas voir les tableaux de bord
- Erreur : "You don't have access to this dashboard"

**Diagnostic** :
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**Solutions** :

1. **Ajouter l'utilisateur à un rôle** :
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **Accorder l'accès au tableau de bord** :
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **Vérifier les règles RLS** :
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## Problèmes PostgreSQL

### Problème 1 : Connexion refusée

**Symptômes** :
- Les applications ne peuvent pas se connecter à PostgreSQL
- Erreur : "Connection refused" ou "Could not connect"

**Diagnostic** :
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**Solutions** :

1. **Redémarrer PostgreSQL** :
   ```bash
   docker-compose restart postgres
   ```

2. **Vérifier le mapping de port** :
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **Vérifier les identifiants** :
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### Problème 2 : Manque de connexions

**Symptômes** :
- Erreur : "FATAL: remaining connection slots are reserved"
- Les applications échouent par intermittence à se connecter

**Diagnostic** :
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

**Solutions** :

1. **Augmenter max_connections** :
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **Utiliser le pooling de connexions** :
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **Tuer les connexions inactives** :
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### Problème 3 : Requêtes lentes

**Symptômes** :
- Les requêtes de base de données prennent plusieurs secondes
- Les applications expirent

**Diagnostic** :
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

**Solutions** :

1. **Créer des index** :
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **Exécuter ANALYZE** :
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **Augmenter shared_buffers** :
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

## Problèmes MinIO

### Problème 1 : Impossible d'accéder à la console MinIO

**Symptômes** :
- Le navigateur affiche une erreur à `http://localhost:9001`

**Diagnostic** :
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**Solutions** :

1. **Vérifier les ports** :
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **Accéder à la bonne URL** :
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **Redémarrer MinIO** :
   ```bash
   docker-compose restart minio
   ```

### Problème 2 : Erreurs d'accès refusé

**Symptômes** :
- Les applications ne peuvent pas lire/écrire sur S3
- Erreur : "Access Denied" ou "403 Forbidden"

**Diagnostic** :
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**Solutions** :

1. **Vérifier les identifiants** :
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **Vérifier la politique du bucket** :
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **Créer une clé d'accès pour l'application** :
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### Problème 3 : Bucket introuvable

**Symptômes** :
- Erreur : "The specified bucket does not exist"

**Diagnostic** :
```bash
# List all buckets
docker exec minio mc ls local/
```

**Solutions** :

1. **Créer le bucket** :
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **Vérifier le nom du bucket dans la configuration** :
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## Réseau et connectivité

### Problème : Les services ne peuvent pas communiquer

**Symptômes** :
- "Connection refused" entre les conteneurs
- Erreurs "Host not found"

**Diagnostic** :
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**Solutions** :

1. **S'assurer que tous les services sont sur le même réseau** :
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

2. **Utiliser les noms de conteneurs, pas localhost** :
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **Recréer le réseau** :
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## Problèmes de performance

### Problème : Utilisation élevée du CPU

**Diagnostic** :
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**Solutions** :

1. **Limiter les requêtes concurrentes** :
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **Optimiser les requêtes** (voir [Problèmes Dremio](#problèmes-dremio))

3. **Augmenter l'allocation CPU** :
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### Problème : Utilisation élevée de la mémoire

**Diagnostic** :
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**Solutions** :

1. **Augmenter la taille du heap** :
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **Activer le spill sur disque** :
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## Problèmes de qualité des données

Voir les solutions détaillées dans le [Guide Qualité des Données](./data-quality.md).

### Vérifications rapides

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

## Résumé

Ce guide de dépannage a couvert :

- **Approche générale** : Méthodologie systématique pour diagnostiquer les problèmes
- **Problèmes par composant** : Solutions pour les 7 services de la plateforme
- **Problèmes réseau** : Problèmes de connectivité des conteneurs
- **Problèmes de performance** : Optimisation du CPU, de la mémoire et des requêtes
- **Problèmes de qualité des données** : Problèmes de données courants et vérifications

**Points clés à retenir** :
- Toujours vérifier les logs en premier : `docker-compose logs [service]`
- Utiliser les noms de conteneurs, pas localhost, pour la communication inter-services
- Tester la connectivité : `docker exec [container] ping [target]`
- Surveiller les ressources : `docker stats`
- Commencer simple : redémarrer le service avant un débogage complexe

**Documentation associée :**
- [Guide d'installation](../getting-started/installation.md)
- [Guide de configuration](../getting-started/configuration.md)
- [Guide Qualité des Données](./data-quality.md)
- [Architecture : Déploiement](../architecture/deployment.md)

**Besoin de plus d'aide ?**
- Vérifier les logs des composants : `docker-compose logs -f [service]`
- Consulter la documentation des services
- Rechercher les issues GitHub
- Contacter l'équipe de support

---

**Version** : 3.2.0  
**Dernière mise à jour** : 16 octobre 2025
