# Come iniziare con la piattaforma dati

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 2025-10-16  
**Lingua**: francese

---

## Panoramica

Questo tutorial ti guida attraverso le tue prime interazioni con la piattaforma dati, dalla connessione ai servizi alla creazione della tua prima pipeline di dati con Airbyte, Dremio, dbt e Superset.

```mermaid
graph LR
    A[Accéder aux Services] --> B[Configurer Airbyte]
    B --> C[Connecter Dremio]
    C --> D[Créer Modèles dbt]
    D --> E[Construire Tableau de Bord]
    E --> F[Pipeline Complet]
    
    style F fill:#90EE90
    style A fill:#87CEEB
```

**Tempo stimato**: 60-90 minuti

---

## Prerequisiti

Prima di iniziare, assicurati che:

- ✅ Tutti i servizi sono installati e funzionanti
- ✅ Puoi accedere alle interfacce web
- ✅ L'ambiente virtuale Python è abilitato
- ✅ Comprensione di base di SQL

**Verifica che i servizi funzionino:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Passaggio 1: accedi a tutti i servizi

### URL dei servizi

| Servizi | URL | Credenziali predefinite |
|---------|----------|-----------------------|
| **Airbyte** | http://localhost:8000 | airbyte@esempio.com/password |
| **Dremio** | http://localhost:9047 | admin/admin123 |
| **Superinsieme** | http://localhost:8088 | amministratore/amministratore |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### Prima connessione

**Airbyte:**
1. Apri http://localhost:8000
2. Completa la procedura guidata di configurazione
3. Imposta il nome dell'area di lavoro: "Produzione"
4. Ignora le preferenze (è possibile una configurazione successiva)

**Dremio:**
1. Apri http://localhost:9047
2. Crea un utente amministratore al primo accesso:
   - Nome utente: `admin`
   - E-mail: `admin@example.com`
   - Password: `admin123`
3. Fare clic su "Inizia"

**Superinsieme:**
1. Apri http://localhost:8088
2. Accedi con le credenziali predefinite
3. Modifica password: Impostazioni → Informazioni utente → Reimposta password

---

## Passaggio 2: configura la tua prima origine dati in Airbyte

### Crea un sorgente PostgreSQL

**Scenario**: estrae dati da un database PostgreSQL.

1. **Vai alle fonti**
   - Clicca su “Sorgenti” nel menu a sinistra
   - Clicca su “+ Nuova fonte”

2. **Seleziona PostgreSQL**
   - Cerca "PostgreSQL"
   - Fare clic sul connettore "PostgreSQL".

3. **Configura connessione**
   ```yaml
   Source name: Production PostgreSQL
   Host: postgres
   Port: 5432
   Database: dremio_db
   Username: postgres
   Password: postgres123
   SSL Mode: prefer
   Replication Method: Standard
   ```

4. **Prova e salva**
   - Clicca su “Imposta fonte”
   - Attendere il test di connessione
   - Fonte creata ✅

### Crea dati di esempio (facoltativo)

Se non disponi ancora di dati, crea tabelle di esempio:

```sql
-- Se connecter à PostgreSQL
docker exec -it postgres psql -U postgres -d dremio_db

-- Créer des tables exemples
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    amount DECIMAL(10,2),
    status VARCHAR(20),
    order_date DATE DEFAULT CURRENT_DATE
);

-- Insérer des données exemples
INSERT INTO customers (name, email, country) VALUES
    ('John Doe', 'john@example.com', 'USA'),
    ('Jane Smith', 'jane@example.com', 'UK'),
    ('Carlos Garcia', 'carlos@example.com', 'Spain'),
    ('Marie Dubois', 'marie@example.com', 'France'),
    ('Yuki Tanaka', 'yuki@example.com', 'Japan');

INSERT INTO orders (customer_id, amount, status) VALUES
    (1, 150.00, 'completed'),
    (1, 250.00, 'completed'),
    (2, 300.00, 'pending'),
    (3, 120.00, 'completed'),
    (4, 450.00, 'completed'),
    (5, 200.00, 'shipped');

-- Vérifier les données
SELECT * FROM customers;
SELECT * FROM orders;
```

---

## Passaggio 3: configurare la destinazione MinIO S3

### Crea una destinazione

1. **Navigazione verso le destinazioni**
   - Clicca su “Destinazioni” nel menu a sinistra
   - Clicca su “+ Nuova destinazione”

2. **Seleziona S3**
   - Cerca "S3"
   - Cliccare sul connettore “S3”.

3. **Configura MinIO come S3**
   §§§CODICE_7§§§

4. **Prova e salva**
   - Clicca su “Imposta destinazione”
   - Il test di connessione dovrebbe passare ✅

---

## Passaggio 4: crea la tua prima connessione

### Collega la sorgente alla destinazione

1. **Vai a Connessioni**
   - Clicca su “Connessioni” nel menu di sinistra
   - Clicca su “+ Nuova connessione”

2. **Seleziona sorgente**
   - Scegli "Produzione PostgreSQL"
   - Clicca su "Utilizza fonte esistente"

3. **Seleziona destinazione**
   - Scegli "MinIO Data Lake"
   - Clicca su "Utilizza destinazione esistente"

4. **Configura la sincronizzazione**
   ```yaml
   Connection name: PostgreSQL → MinIO
   Replication frequency: Every 24 hours at 02:00
   Destination Namespace: Custom format
     Format: production_${SOURCE_NAMESPACE}
   
   Streams to sync:
     ☑ customers
       Sync mode: Full Refresh | Overwrite
       Primary key: customer_id
       Cursor field: created_at
       
     ☑ orders
       Sync mode: Incremental | Append
       Primary key: order_id
       Cursor field: order_date
   ```

5. **Normalizzazione**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Backup e sincronizzazione**
   - Clicca su “Configura connessione”
   - Fare clic su "Sincronizza ora" per eseguire la prima sincronizzazione
   - Monitorare l'avanzamento della sincronizzazione

### Monitora la sincronizzazione

```mermaid
sequenceDiagram
    participant PG as PostgreSQL
    participant AB as Airbyte Worker
    participant S3 as MinIO S3
    
    AB->>PG: 1. Extraction: SELECT * FROM customers
    PG->>AB: 2. Retour données (5 lignes)
    AB->>AB: 3. Transformation en Parquet
    AB->>S3: 4. Téléversement vers datalake/raw-data/
    
    AB->>PG: 5. Extraction: SELECT * FROM orders WHERE order_date > last_sync
    PG->>AB: 6. Retour nouvelles données
    AB->>AB: 7. Transformation en Parquet
    AB->>S3: 8. Téléversement vers datalake/raw-data/
    
    Note over AB: Synchronisation Terminée ✅
```

**Controlla lo stato della sincronizzazione:**
- Lo stato dovrebbe mostrare "Riuscito" (verde)
- Record sincronizzati: ~11 (5 clienti + 6 ordini)
- Vedi i registri per i dettagli

---

## Passaggio 5: collega Dremio a MinIO

### Aggiungi una sorgente S3 in Dremio

1. **Vai alle fonti**
   - Apri http://localhost:9047
   - Clicca su "Aggiungi fonte" (+ icona)

2. **Seleziona S3**
   - Scegli "Amazon S3"
   - Configura come MinIO:

```yaml
General:
  Name: MinIOLake

Connection:
  Authentication: AWS Access Key
  AWS Access Key: minioadmin
  AWS Secret Key: minioadmin123
  
  Encrypt connection: No
  
Advanced Options:
  Connection Properties:
    fs.s3a.path.style.access: true
    fs.s3a.endpoint: minio:9000
    dremio.s3.compat: true
  
  Root Path: /
  
  Enable compatibility mode: Yes
```

3. **Prova e salva**
   - Clicca su "Salva"
   - Dremio analizzerà i bucket MinIO

### Sfoglia i dati

1. **Vai alla sorgente MinIOLake**
   - Sviluppare "MinIOLake"
   - Sviluppare il bucket "datalake".
   - Espandi la cartella "raw-data".
   - Vedi la cartella "production_public".

2. **Anteprima dati**
   - Fare clic sulla cartella "clienti".
   - Clicca sulla scheda Parquet
   - Fare clic su "Anteprima" per visualizzare i dati
   - I dati devono corrispondere a PostgreSQL ✅

### Crea un set di dati virtuale

1. **Dati della query**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Salva come VDS**
   - Clicca su "Salva vista con nome"
   - Nome: `vw_customers`
   - Spazio: `@admin` (il tuo spazio)
   - Clicca su "Salva"

3. **Formatta dati** (facoltativo)
   - Clicca su `vw_customers`
   - Utilizza l'interfaccia per rinominare colonne, modificare tipi
   - Esempio: rinominare `customer_id` in `id`

---

## Passaggio 6: crea modelli dbt

### Inizializza il progetto dbt

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate  # Windows

# Naviguer vers le répertoire dbt
cd dbt

# Tester la connexion
dbt debug

# Devrait afficher: "All checks passed!"
```

### Crea la definizione della sorgente

**File**: `dbt/models/sources.yml`

```yaml
version: 2

sources:
  - name: airbyte_raw
    description: Données brutes des synchronisations Airbyte
    database: MinIOLake.datalake."raw-data".production_public
    tables:
      - name: customers
        description: Données maîtres clients
        columns:
          - name: customer_id
            description: Identifiant unique du client
            tests:
              - unique
              - not_null
          - name: email
            tests:
              - unique
              - not_null
      
      - name: orders
        description: Transactions de commandes
        columns:
          - name: order_id
            description: Identifiant unique de la commande
            tests:
              - unique
              - not_null
          - name: customer_id
            description: Clé étrangère vers customers
            tests:
              - not_null
              - relationships:
                  to: source('airbyte_raw', 'customers')
                  field: customer_id
```

### Crea un modello di gestione temporanea

**File**: `dbt/models/staging/stg_customers.sql`

```sql
-- Modèle de staging: Nettoyer et standardiser les données clients

{{ config(
    materialized='view',
    schema='staging'
) }}

with source as (
    select * from {{ source('airbyte_raw', 'customers') }}
),

cleaned as (
    select
        customer_id,
        trim(name) as customer_name,
        lower(trim(email)) as email,
        upper(trim(country)) as country_code,
        created_at,
        current_timestamp() as dbt_loaded_at
    from source
)

select * from cleaned
```

**File**: `dbt/models/staging/stg_orders.sql`

```sql
-- Modèle de staging: Nettoyer et standardiser les données de commandes

{{ config(
    materialized='view',
    schema='staging'
) }}

with source as (
    select * from {{ source('airbyte_raw', 'orders') }}
),

cleaned as (
    select
        order_id,
        customer_id,
        amount,
        lower(trim(status)) as order_status,
        order_date,
        current_timestamp() as dbt_loaded_at
    from source
    where amount > 0  -- Filtre de qualité des données
)

select * from cleaned
```

### Crea un modello Mart

**File**: `dbt/models/marts/fct_customer_orders.sql`

```sql
-- Table de faits: Résumé des commandes clients

{{ config(
    materialized='table',
    schema='marts'
) }}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_metrics as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount) as total_spent,
        avg(amount) as avg_order_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        sum(case when order_status = 'completed' then 1 else 0 end) as completed_orders
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.country_code,
        c.created_at as customer_since,
        
        coalesce(m.total_orders, 0) as total_orders,
        coalesce(m.total_spent, 0) as lifetime_value,
        coalesce(m.avg_order_value, 0) as avg_order_value,
        m.first_order_date,
        m.last_order_date,
        coalesce(m.completed_orders, 0) as completed_orders,
        
        datediff('day', m.last_order_date, current_date()) as days_since_last_order,
        
        case
            when m.total_orders >= 5 then 'VIP'
            when m.total_orders >= 2 then 'Regular'
            else 'New'
        end as customer_segment
        
    from customers c
    left join customer_metrics m on c.customer_id = m.customer_id
)

select * from final
```

### Esegui modelli dbt

```bash
# Exécuter tous les modèles
dbt run

# Devrait afficher:
# Completed successfully
# Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3

# Exécuter les tests
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve  # Ouvre le navigateur sur localhost:8080
```

### Controlla a Dremio

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Passaggio 7: crea una dashboard in Superset

### Aggiungi il database Dremio

1. **Vai ai database**
   - Apri http://localhost:8088
   - Fare clic su "Dati" → "Database"
   - Fare clic su "+ Banca dati"

2. **Seleziona Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **Fai clic su "Connetti"**

### Crea un set di dati

1. **Vai ai set di dati**
   - Fare clic su "Dati" → "Set di dati"
   - Fare clic su "+ Set di dati"

2. **Configura il set di dati**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Fai clic su "Crea set di dati e crea grafico"**

### Crea grafici

#### Grafico 1: Segmenti di clienti (diagramma circolare)

```yaml
Chart Type: Pie Chart
Datasource: fct_customer_orders

Dimensions:
  - customer_segment

Metrics:
  - COUNT(customer_id)

Filters: Aucun

Chart Options:
  Show Labels: Yes
  Show Legend: Yes
```

#### Grafico 2: reddito per paese (grafico a barre)

```yaml
Chart Type: Bar Chart
Datasource: fct_customer_orders

Dimensions:
  - country_code

Metrics:
  - SUM(lifetime_value)

Sort by: SUM(lifetime_value) DESC
Limit: 10

Chart Options:
  Show Labels: Yes
  Color Scheme: Superset Colors
```

#### Grafico 3: Metriche dei clienti (numero grande)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Crea la dashboard

1. **Vai a Dashboard**
   - Clicca su "Dashboard"
   - Clicca su "+ Dashboard"

2. **Configura la dashboard**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Aggiungi grafica**
   - Trascina e rilascia la grafica creata
   - Organizza in una griglia:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Aggiungi filtri** (facoltativo)
   - Clicca su "Aggiungi filtro"
   - Filtra per: codice_paese
   - Applicare a tutti i grafici

5. **Salva la dashboard**

---

## Passaggio 8: controlla la pipeline completa

### Test end-to-end

```mermaid
graph LR
    A[PostgreSQL<br/>Données Source] -->|Sync Airbyte| B[MinIO S3<br/>Données Brutes]
    B -->|Requête Dremio| C[dbt<br/>Transformations]
    C -->|Écriture| D[Dremio<br/>Marts]
    D -->|Requête SQL| E[Superset<br/>Tableau de Bord]
    
    style A fill:#336791,color:#fff
    style B fill:#C72E49,color:#fff
    style C fill:#FF694B,color:#fff
    style D fill:#FDB515
    style E fill:#20A7C9,color:#fff
```

### Aggiungi nuovi dati

1. **Inserisci nuovi record in PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Attiva la sincronizzazione di Airbyte**
   - Apri l'interfaccia Airbyte
   - Vai alla connessione "PostgreSQL → MinIO"
   - Fai clic su "Sincronizza ora"
   - Aspetta la fine ✅

3. **Esegui dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **Aggiorna la dashboard del superset**
   - Apri il cruscotto
   - Fare clic sul pulsante "Aggiorna".
   - Dovrebbero apparire nuovi dati ✅

### Controlla il flusso di dati

```sql
-- Dans Dremio SQL Runner

-- 1. Vérifier les données brutes d'Airbyte
SELECT COUNT(*) as raw_customers
FROM MinIOLake.datalake."raw-data".production_public.customers;
-- Devrait retourner: 7

-- 2. Vérifier la vue de staging
SELECT COUNT(*) as staged_customers
FROM "@admin".staging.stg_customers;
-- Devrait retourner: 7

-- 3. Vérifier la table mart
SELECT
    customer_segment,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_revenue
FROM "@admin".marts.fct_customer_orders
GROUP BY customer_segment
ORDER BY total_revenue DESC;
```

---

## Passaggio 9: automatizza la pipeline

### Pianifica la sincronizzazione di Airbyte

Già configurato per essere eseguito ogni 24 ore alle 02:00.

Per modificare:
1. Apri la connessione in Airbyte
2. Vai alla scheda "Impostazioni".
3. Aggiorna "Frequenza di replica"
4. Salva

### Pianifica esecuzioni dbt

**Opzione 1: Cron Job (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Opzione 2: script Python**

**File**: `scripts/run_pipeline.py`
```python
#!/usr/bin/env python3
"""
Exécution automatisée du pipeline
Exécute les modèles dbt après la synchronisation Airbyte
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_dbt():
    """Exécuter les modèles dbt"""
    dbt_dir = Path(__file__).parent.parent / 'dbt'
    
    logger.info("Exécution des modèles dbt...")
    result = subprocess.run(
        ['dbt', 'run'],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("Exécution dbt terminée avec succès")
        return True
    else:
        logger.error(f"Échec exécution dbt: {result.stderr}")
        return False

if __name__ == '__main__':
    success = run_dbt()
    exit(0 if success else 1)
```

### Pianifica con Docker Compose

**File**: `docker-compose.scheduler.yml`
```yaml
version: '3.8'

services:
  dbt-scheduler:
    image: ghcr.io/dbt-labs/dbt-core:1.10.0
    volumes:
      - ./dbt:/usr/app/dbt
    command: >
      sh -c "while true; do
        dbt run --profiles-dir /usr/app/dbt;
        sleep 3600;
      done"
    networks:
      - dremio_network
```

---

## Passaggi successivi

Congratulazioni! Hai creato una pipeline di dati end-to-end completa. 🎉

### Saperne di più

1. **Airbyte Advanced** - [Guida all'integrazione di Airbyte](../guides/airbyte-integration.md)
2. **Ottimizzazione Dremio** - [Guida all'installazione di Dremio](../guides/dremio-setup.md)
3. **Modelli dbt complessi** - [Guida allo sviluppo di dbt](../guides/dbt-development.md)
4. **Dashboard avanzati** - [Guida ai dashboard Superset](../guides/superset-dashboards.md)
5. **Qualità dei dati** - [Guida alla qualità dei dati](../guides/data-quality.md)

### Risoluzione dei problemi

In caso di problemi, vedere:
- [Guida alla risoluzione dei problemi](../guides/troubleshooting.md)
- [Guida all'installazione](installation.md#risoluzione dei problemi)
- [Guida alla configurazione](configuration.md)

---

## Riepilogo

Hai con successo:

- ✅ Accedi ai 7 servizi della piattaforma
- ✅ Configura una sorgente Airbyte (PostgreSQL)
- ✅ Configura una destinazione Airbyte (MinIO S3)
- ✅ Crea la tua prima connessione Airbyte
- ✅ Collega Dremio a MinIO
- ✅Crea modelli dbt (staging + mart)
- ✅ Costruisci una dashboard Superset
- ✅ Controllare il flusso di dati end-to-end
- ✅ Automatizza l'esecuzione della pipeline

**La tua piattaforma dati è ora operativa!** 🚀

---

**Versione della Guida ai primi passi**: 3.2.0  
**Ultimo aggiornamento**: 2025-10-16  
**Mantenuto da**: Team della piattaforma dati