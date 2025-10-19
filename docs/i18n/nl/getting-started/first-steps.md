# Aan de slag met het dataplatform

**Versie**: 3.2.0  
**Laatst bijgewerkt**: 16-10-2025  
**Taal**: Frans

---

## Overzicht

Deze tutorial leidt u door uw eerste interacties met het dataplatform, van het verbinden met services tot het bouwen van uw eerste datapijplijn met Airbyte, Dremio, dbt en Superset.

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

**Geschatte tijd**: 60-90 minuten

---

## Vereisten

Voordat u begint, zorg ervoor dat:

- ✅ Alle services zijn geïnstalleerd en actief
- ✅ U hebt toegang tot webinterfaces
- ✅ Virtuele Python-omgeving is ingeschakeld
- ✅ Basiskennis van SQL

**Controleer of de services werken:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Stap 1: toegang tot alle services

### Service-URL's

| Diensten | URL | Standaardgegevens |
|---------|----------|----------------------|
| **Airbyte** | http://localhost:8000 | airbyte@voorbeeld.com / wachtwoord |
| **Dremio** | http://localhost:9047 | beheerder/beheerder123 |
| **Superset** | http://localhost:8088 | beheerder / beheerder |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### Eerste verbinding

**Airbyte:**
1. Open http://localhost:8000
2. Voltooi de installatiewizard
3. Stel de naam van de werkruimte in: “Productie”
4. Voorkeuren overschrijven (latere configuratie mogelijk)

**Dremio:**
1. Open http://localhost:9047
2. Maak een beheerdergebruiker bij de eerste toegang:
   - Gebruikersnaam: `admin`
   - E-mail: `admin@example.com`
   - Wachtwoord: `admin123`
3. Klik op “Aan de slag”

**Superset:**
1. Open http://localhost:8088
2. Log in met standaardgegevens
3. Wachtwoord wijzigen: Instellingen → Gebruikersinfo → Wachtwoord opnieuw instellen

---

## Stap 2: Configureer uw eerste gegevensbron in Airbyte

### Maak een PostgreSQL-bron

**Scenario**: Gegevens extraheren uit een PostgreSQL-database.

1. **Navigeer naar bronnen**
   - Klik in het linkermenu op “Bronnen”.
   - Klik op “+ Nieuwe bron”

2. **Selecteer PostgreSQL**
   - Zoek naar “PostgreSQL”
   - Klik op de “PostgreSQL”-connector

3. **Verbinding configureren**
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

4. **Test en bewaar**
   - Klik op “Bron instellen”
   - Wacht op de verbindingstest
   - Bron aangemaakt ✅

### Voorbeeldgegevens maken (optioneel)

Als u nog geen gegevens heeft, maakt u voorbeeldtabellen:

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

## Stap 3: Configureer de MinIO S3-bestemming

### Maak een bestemming

1. **Navigeer naar bestemmingen**
   - Klik in het linkermenu op “Bestemmingen”.
   - Klik op “+ Nieuwe bestemming”

2. **Selecteer S3**
   - Zoek naar "S3"
   - Klik op de “S3”-connector

3. **Configureer MinIO als S3**
   ```yaml
   Destination name: MinIO Data Lake
   S3 Bucket Name: datalake
   S3 Bucket Path: raw-data
   S3 Bucket Region: us-east-1
   S3 Endpoint: http://minio:9000
   Access Key ID: minioadmin
   Secret Access Key: minioadmin123
   
   Output Format:
     Format Type: Parquet
     Compression: GZIP
     Block Size (Row Group Size): 128 MB
   ```

4. **Test en bewaar**
   - Klik op “Bestemming instellen”
   - Verbindingstest moet slagen ✅

---

## Stap 4: Maak uw eerste verbinding

### Koppel bron aan bestemming

1. **Navigeer naar Verbindingen**
   - Klik op “Verbindingen” in het linkermenu
   - Klik op “+ Nieuwe verbinding”

2. **Selecteer bron**
   - Kies “PostgreSQL-productie”
   - Klik op “Gebruik bestaande bron”

3. **Selecteer bestemming**
   - Kies “MinIO Data Lake”
   - Klik op “Gebruik bestaande bestemming”

4. **Synchronisatie configureren**
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

5. **Normalisatie**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Back-up maken en synchroniseren**
   - Klik op “Verbinding instellen”
   - Klik op “Nu synchroniseren” om de eerste synchronisatie uit te voeren
   - Controleer de voortgang van de synchronisatie

### Monitorsynchronisatie

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

**Controleer de synchronisatiestatus:**
- Status zou "Geslaagd" moeten zijn (groen)
- Gesynchroniseerde records: ~11 (5 klanten + 6 bestellingen)
- Zie logboeken voor details

---

## Stap 5: Verbind Dremio met MinIO

### Voeg een S3-bron toe in Dremio

1. **Navigeer naar bronnen**
   - Open http://localhost:9047
   - Klik op “Bron toevoegen” (+ icoontje)

2. **Selecteer S3**
   - Kies “Amazon S3”
   - Configureer als MinIO:

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

3. **Test en bewaar**
   - Klik op “Opslaan”
   - Dremio zal MinIO-buckets analyseren

### Blader door gegevens

1. **Navigeer naar MinIOLake-bron**
   - Ontwikkel “MinIOLake”
   - Ontwikkel de "datalake"-bucket
   - Vouw de map "raw-data" uit
   - Zie de map "production_public".

2. **Voorbeeldgegevens**
   - Klik op de map “klanten”.
   - Klik op het Parquet-bestand
   - Klik op “Preview” om de gegevens te bekijken
   - Gegevens moeten overeenkomen met PostgreSQL ✅

### Maak een virtuele dataset

1. **Opvraaggegevens**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Opslaan als VDS**
   - Klik op “Weergave opslaan als”
   - Naam: `vw_customers`
   - Spatie: `@admin` (uw ruimte)
   - Klik op “Opslaan”

3. **Gegevens formatteren** (optioneel)
   - Klik op `vw_customers`
   - Gebruik de interface om kolommen te hernoemen en typen te wijzigen
   - Voorbeeld: hernoem `customer_id` naar `id`

---

## Stap 6: Maak dbt-sjablonen

### Initialiseer het dbt-project

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

### Brondefinitie maken

**Bestand**: `dbt/models/sources.yml`

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

### Maak een staging-sjabloon

**Bestand**: `dbt/models/staging/stg_customers.sql`

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

**Bestand**: `dbt/models/staging/stg_orders.sql`

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

### Maak een Mart-sjabloon

**Bestand**: `dbt/models/marts/fct_customer_orders.sql`

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

### Voer dbt-modellen uit

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

### Inchecken Dremio

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Stap 7: Maak een dashboard in Superset

### Dremio-database toevoegen

1. **Navigeer naar databases**
   - Open http://localhost:8088
   - Klik op “Gegevens” → “Databases”
   - Klik op “+Database”

2. **Selecteer Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **Klik op “Verbinden”**

### Maak een gegevensset

1. **Navigeer naar gegevenssets**
   - Klik op “Gegevens” → “Datasets”
   - Klik op “+ Gegevensset”

2. **Configureer de gegevensset**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Klik op “Gegevensset maken en grafiek maken”**

### Grafieken maken

#### Grafiek 1: Klantsegmenten (circulair diagram)

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

#### Grafiek 2: Inkomen per land (staafdiagram)

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

#### Grafiek 3: Klantstatistieken (groot getal)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Maak het dashboard

1. **Navigeer naar Dashboards**
   - Klik op “Dashboards”
   - Klik op “+ Dashboard”

2. **Configureer het dashboard**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Afbeeldingen toevoegen**
   - Sleep de gemaakte afbeeldingen en zet ze neer
   - Organiseer in een raster:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Filters toevoegen** (optioneel)
   - Klik op “Filter toevoegen”
   - Filter op: landcode
   - Toepassen op alle grafieken

5. **Sla het dashboard op**

---

## Stap 8: Controleer de volledige pijplijn

### End-to-end testen

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

### Nieuwe gegevens toevoegen

1. **Nieuwe records invoegen in PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Airbyte-synchronisatie activeren**
   - Open de Airbyte-interface
   - Ga naar de verbinding "PostgreSQL → MinIO"
   - Klik op “Nu synchroniseren”
   - Wacht op het einde ✅

3. **Voer dbt uit**
   ```bash
   cd dbt
   dbt run
   ```

4. **Vernieuw het Superset-dashboard**
   - Open het dashboard
   - Klik op de knop “Vernieuwen”.
   - Nieuwe gegevens zouden moeten verschijnen ✅

### Controleer de gegevensstroom

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

## Stap 9: Automatiseer de pijplijn

### Plan Airbyte-synchronisatie

Al geconfigureerd om elke 24 uur om 02:00 uur te draaien.

Bewerken:
1. Open de verbinding in Airbyte
2. Ga naar het tabblad “Instellingen”.
3. Update “Replicatiefrequentie”
4. Opslaan

### Plan dbt-uitvoeringen

**Optie 1: Cronjob (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Optie 2: Python-script**

**Bestand**: `scripts/run_pipeline.py`
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

### Plan met Docker Compose

**Bestand**: `docker-compose.scheduler.yml`
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

## Volgende stappen

Gefeliciteerd! U hebt een complete end-to-end datapijplijn gebouwd. 🎉

### Meer informatie

1. **Airbyte Advanced** - [Airbyte-integratiegids](../guides/airbyte-integration.md)
2. **Dremio-optimalisatie** - [Dremio-installatiehandleiding](../guides/dremio-setup.md)
3. **Complexe dbt-modellen** - [dbt-ontwikkelingshandleiding](../guides/dbt-development.md)
4. **Geavanceerde dashboards** - [Superset Dashboards-handleiding](../guides/superset-dashboards.md)
5. **Gegevenskwaliteit** - [Handleiding gegevenskwaliteit](../guides/data-quality.md)

### Problemen oplossen

Als u problemen ondervindt, raadpleeg dan:
- [Handleiding voor probleemoplossing](../guides/troubleshooting.md)
- [Installatiehandleiding](installation.md#troubleshooting)
- [Configuratiehandleiding] (configuration.md)

---

## Samenvatting

Je hebt met succes:

- ✅ Toegang tot de 7 diensten van het platform
- ✅ Configureer een Airbyte-bron (PostgreSQL)
- ✅ Configureer een Airbyte-bestemming (MinIO S3)
- ✅ Creëer uw eerste Airbyte-verbinding
- ✅ Verbind Dremio met MinIO
- ✅ Maak dbt-sjablonen (staging + marts)
- ✅ Bouw een Superset-dashboard
- ✅ Controleer de end-to-end gegevensstroom
- ✅ Automatiseer de uitvoering van pijpleidingen

**Uw dataplatform is nu operationeel!** 🚀

---

**Eerste Stappenhandleiding Versie**: 3.2.0  
**Laatst bijgewerkt**: 16-10-2025  
**Onderhoud door**: Data Platform-team