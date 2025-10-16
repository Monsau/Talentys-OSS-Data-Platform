# Premiers Pas avec la Plateforme de Données

**Version**: 3.2.0  
**Dernière mise à jour**: 2025-10-16  
**Langue**: Français

---

## Vue d'ensemble

Ce tutoriel vous guide à travers vos premières interactions avec la plateforme de données, de la connexion aux services à la création de votre premier pipeline de données avec Airbyte, Dremio, dbt et Superset.

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

**Temps estimé**: 60-90 minutes

---

## Prérequis

Avant de commencer, assurez-vous que:

- ✅ Tous les services sont installés et en cours d'exécution
- ✅ Vous pouvez accéder aux interfaces web
- ✅ L'environnement virtuel Python est activé
- ✅ Compréhension de base de SQL

**Vérifier que les services fonctionnent:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Étape 1: Accéder à Tous les Services

### URLs des Services

| Service | URL | Identifiants par Défaut |
|---------|-----|-------------------------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / password |
| **Dremio** | http://localhost:9047 | admin / admin123 |
| **Superset** | http://localhost:8088 | admin / admin |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### Première Connexion

**Airbyte:**
1. Ouvrir http://localhost:8000
2. Compléter l'assistant de configuration
3. Définir le nom de l'espace de travail: "Production"
4. Ignorer les préférences (configuration ultérieure possible)

**Dremio:**
1. Ouvrir http://localhost:9047
2. Créer un utilisateur administrateur au premier accès:
   - Nom d'utilisateur: `admin`
   - Email: `admin@example.com`
   - Mot de passe: `admin123`
3. Cliquer sur "Get Started"

**Superset:**
1. Ouvrir http://localhost:8088
2. Se connecter avec les identifiants par défaut
3. Changer le mot de passe: Settings → User Info → Reset Password

---

## Étape 2: Configurer Votre Première Source de Données dans Airbyte

### Créer une Source PostgreSQL

**Scénario**: Extraire des données d'une base de données PostgreSQL.

1. **Naviguer vers Sources**
   - Cliquer sur "Sources" dans le menu de gauche
   - Cliquer sur "+ New source"

2. **Sélectionner PostgreSQL**
   - Rechercher "PostgreSQL"
   - Cliquer sur le connecteur "PostgreSQL"

3. **Configurer la Connexion**
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

4. **Tester et Sauvegarder**
   - Cliquer sur "Set up source"
   - Attendre le test de connexion
   - Source créée ✅

### Créer des Données Exemples (Optionnel)

Si vous n'avez pas encore de données, créer des tables exemples:

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

## Étape 3: Configurer la Destination MinIO S3

### Créer une Destination

1. **Naviguer vers Destinations**
   - Cliquer sur "Destinations" dans le menu de gauche
   - Cliquer sur "+ New destination"

2. **Sélectionner S3**
   - Rechercher "S3"
   - Cliquer sur le connecteur "S3"

3. **Configurer MinIO comme S3**
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

4. **Tester et Sauvegarder**
   - Cliquer sur "Set up destination"
   - Le test de connexion devrait réussir ✅

---

## Étape 4: Créer Votre Première Connexion

### Lier la Source à la Destination

1. **Naviguer vers Connexions**
   - Cliquer sur "Connections" dans le menu de gauche
   - Cliquer sur "+ New connection"

2. **Sélectionner la Source**
   - Choisir "Production PostgreSQL"
   - Cliquer sur "Use existing source"

3. **Sélectionner la Destination**
   - Choisir "MinIO Data Lake"
   - Cliquer sur "Use existing destination"

4. **Configurer la Synchronisation**
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

5. **Normalisation**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Sauvegarder et Synchroniser**
   - Cliquer sur "Set up connection"
   - Cliquer sur "Sync now" pour exécuter la première synchronisation
   - Surveiller la progression de la synchronisation

### Surveiller la Synchronisation

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

**Vérifier le statut de synchronisation:**
- Le statut devrait afficher "Succeeded" (vert)
- Enregistrements synchronisés: ~11 (5 clients + 6 commandes)
- Voir les logs pour les détails

---

## Étape 5: Connecter Dremio à MinIO

### Ajouter une Source S3 dans Dremio

1. **Naviguer vers Sources**
   - Ouvrir http://localhost:9047
   - Cliquer sur "Add Source" (icône +)

2. **Sélectionner S3**
   - Choisir "Amazon S3"
   - Configurer comme MinIO:

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

3. **Tester et Sauvegarder**
   - Cliquer sur "Save"
   - Dremio va analyser les buckets MinIO

### Parcourir les Données

1. **Naviguer vers la source MinIOLake**
   - Développer "MinIOLake"
   - Développer le bucket "datalake"
   - Développer le dossier "raw-data"
   - Voir le dossier "production_public"

2. **Prévisualiser les Données**
   - Cliquer sur le dossier "customers"
   - Cliquer sur le fichier Parquet
   - Cliquer sur "Preview" pour voir les données
   - Les données doivent correspondre à PostgreSQL ✅

### Créer un Dataset Virtuel

1. **Requêter les Données**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Sauvegarder comme VDS**
   - Cliquer sur "Save View As"
   - Nom: `vw_customers`
   - Espace: `@admin` (votre espace)
   - Cliquer sur "Save"

3. **Formater les Données** (optionnel)
   - Cliquer sur `vw_customers`
   - Utiliser l'interface pour renommer les colonnes, changer les types
   - Exemple: Renommer `customer_id` en `id`

---

## Étape 6: Créer des Modèles dbt

### Initialiser le Projet dbt

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

### Créer la Définition des Sources

**Fichier**: `dbt/models/sources.yml`

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

### Créer un Modèle de Staging

**Fichier**: `dbt/models/staging/stg_customers.sql`

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

**Fichier**: `dbt/models/staging/stg_orders.sql`

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

### Créer un Modèle Mart

**Fichier**: `dbt/models/marts/fct_customer_orders.sql`

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

### Exécuter les Modèles dbt

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

### Vérifier dans Dremio

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Étape 7: Créer un Tableau de Bord dans Superset

### Ajouter la Base de Données Dremio

1. **Naviguer vers Bases de Données**
   - Ouvrir http://localhost:8088
   - Cliquer sur "Data" → "Databases"
   - Cliquer sur "+ Database"

2. **Sélectionner Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **Cliquer sur "Connect"**

### Créer un Dataset

1. **Naviguer vers Datasets**
   - Cliquer sur "Data" → "Datasets"
   - Cliquer sur "+ Dataset"

2. **Configurer le Dataset**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Cliquer sur "Create Dataset and Create Chart"**

### Créer des Graphiques

#### Graphique 1: Segments Clients (Diagramme Circulaire)

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

#### Graphique 2: Revenu par Pays (Diagramme en Barres)

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

#### Graphique 3: Métriques Clients (Grand Nombre)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Créer le Tableau de Bord

1. **Naviguer vers Tableaux de Bord**
   - Cliquer sur "Dashboards"
   - Cliquer sur "+ Dashboard"

2. **Configurer le Tableau de Bord**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Ajouter les Graphiques**
   - Glisser-déposer les graphiques créés
   - Organiser dans une grille:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Ajouter des Filtres** (optionnel)
   - Cliquer sur "Add Filter"
   - Filtrer par: country_code
   - Appliquer à tous les graphiques

5. **Sauvegarder le Tableau de Bord**

---

## Étape 8: Vérifier le Pipeline Complet

### Test de Bout en Bout

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

### Ajouter de Nouvelles Données

1. **Insérer de nouveaux enregistrements dans PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Déclencher la synchronisation Airbyte**
   - Ouvrir l'interface Airbyte
   - Aller à la connexion "PostgreSQL → MinIO"
   - Cliquer sur "Sync now"
   - Attendre la fin ✅

3. **Exécuter dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **Actualiser le Tableau de Bord Superset**
   - Ouvrir le tableau de bord
   - Cliquer sur le bouton "Refresh"
   - Les nouvelles données devraient apparaître ✅

### Vérifier le Flux de Données

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

## Étape 9: Automatiser le Pipeline

### Planifier la Synchronisation Airbyte

Déjà configuré pour s'exécuter toutes les 24 heures à 02:00.

Pour modifier:
1. Ouvrir la connexion dans Airbyte
2. Aller dans l'onglet "Settings"
3. Mettre à jour "Replication frequency"
4. Sauvegarder

### Planifier les Exécutions dbt

**Option 1: Tâche Cron (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Option 2: Script Python**

**Fichier**: `scripts/run_pipeline.py`
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

### Planifier avec Docker Compose

**Fichier**: `docker-compose.scheduler.yml`
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

## Prochaines Étapes

Félicitations! Vous avez construit un pipeline de données complet de bout en bout. 🎉

### En Savoir Plus

1. **Airbyte Avancé** - [Guide d'Intégration Airbyte](../guides/airbyte-integration.md)
2. **Optimisation Dremio** - [Guide de Configuration Dremio](../guides/dremio-setup.md)
3. **Modèles dbt Complexes** - [Guide de Développement dbt](../guides/dbt-development.md)
4. **Tableaux de Bord Avancés** - [Guide Tableaux de Bord Superset](../guides/superset-dashboards.md)
5. **Qualité des Données** - [Guide Qualité des Données](../guides/data-quality.md)

### Dépannage

Si vous rencontrez des problèmes, voir:
- [Guide de Dépannage](../guides/troubleshooting.md)
- [Guide d'Installation](installation.md#dépannage)
- [Guide de Configuration](configuration.md)

---

## Résumé

Vous avez réussi à:

- ✅ Accéder aux 7 services de la plateforme
- ✅ Configurer une source Airbyte (PostgreSQL)
- ✅ Configurer une destination Airbyte (MinIO S3)
- ✅ Créer votre première connexion Airbyte
- ✅ Connecter Dremio à MinIO
- ✅ Créer des modèles dbt (staging + marts)
- ✅ Construire un tableau de bord Superset
- ✅ Vérifier le flux de données de bout en bout
- ✅ Automatiser l'exécution du pipeline

**Votre plateforme de données est maintenant opérationnelle!** 🚀

---

**Version du Guide Premiers Pas**: 3.2.0  
**Dernière Mise à Jour**: 2025-10-16  
**Maintenu Par**: Équipe Plateforme de Données
