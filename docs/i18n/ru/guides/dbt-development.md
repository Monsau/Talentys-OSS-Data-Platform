# Руководство по разработке dbt

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Язык**: французский

## Оглавление

1. [Обзор](#обзор)
2. [Конфигурация проекта](#project-configuration)
3. [Моделирование данных](#data-modeling)
4. [Тестовая среда](#test-framework)
5. [Документация](#документация)
6. [Макросы и пакеты](#макросы-и-пакеты)
7. [Инкрементальные модели](#инкрементальные-модели)
8. [Рабочий процесс оркестрации] (#orchestration-workflow)
9. [Передовая практика](#передовая практика)
10. [Устранение неполадок](#устранение неполадок)

---

## Обзор

dbt (инструмент построения данных) позволяет инженерам-аналитикам преобразовывать данные в хранилище, используя передовые методы SQL и разработки программного обеспечения. Это руководство охватывает все: от инициализации проекта до передовых методов разработки.

### Что такое ДБТ?

dbt преобразует необработанные данные в готовые для аналитики наборы данных, используя:

- **Преобразования SQL**: записывайте операторы SELECT, остальное обрабатывает dbt.
- **Контроль версий**: интеграция с Git для совместной работы.
- **Тестирование**: интегрированная система тестирования качества данных.
- **Документация**: документация, созданная самостоятельно с использованием происхождения.
- **Модульность**: многократно используемые шаблоны и макросы.

### Ключевые понятия

```mermaid
graph LR
    A[Données Source] --> B[Modèles Staging]
    B --> C[Modèles Intermédiaires]
    C --> D[Tables Fait]
    C --> E[Tables Dimension]
    D --> F[Modèles Mart]
    E --> F
    F --> G[Outils BI]
    
    H[Tests dbt] -.->|Valider| B
    H -.->|Valider| C
    H -.->|Valider| D
    H -.->|Valider| E
    
    style A fill:#CD7F32,color:#fff
    style B fill:#87CEEB
    style C fill:#90EE90
    style D fill:#FFB6C1
    style E fill:#DDA0DD
    style F fill:#FFD700
    style G fill:#20A7C9,color:#fff
```

### рабочий процесс dbt

```mermaid
sequenceDiagram
    participant Dev as Développeur
    participant Git as Dépôt Git
    participant dbt as dbt Core
    participant DW as Data Warehouse
    participant Docs as Documentation
    
    Dev->>Git: 1. Écrire modèles SQL
    Dev->>dbt: 2. dbt run
    dbt->>DW: 3. Exécuter transformations
    DW-->>dbt: 4. Retourner résultats
    Dev->>dbt: 5. dbt test
    dbt->>DW: 6. Exécuter tests
    DW-->>dbt: 7. Résultats tests
    Dev->>dbt: 8. dbt docs generate
    dbt->>Docs: 9. Créer documentation
    Dev->>Git: 10. Commit changements
```

---

## Конфигурация проекта

### Инициализация проекта dbt

```bash
# Créer nouveau projet dbt
dbt init dremio_analytics

# Structure projet créée:
dremio_analytics/
├── dbt_project.yml
├── profiles.yml
├── README.md
├── models/
│   └── example/
├── tests/
├── macros/
├── snapshots/
└── analyses/
```

### Настройка Profiles.yml

```yaml
# ~/.dbt/profiles.yml
dremio_analytics:
  target: dev
  outputs:
    dev:
      type: dremio
      threads: 4
      host: localhost
      port: 9047
      username: "{{ env_var('DREMIO_USER') }}"
      password: "{{ env_var('DREMIO_PASSWORD') }}"
      use_ssl: false
      object_storage_source: MinIO
      object_storage_path: datalake
      datalake_name: "@{{ env_var('DREMIO_USER') }}"
      
    prod:
      type: dremio
      threads: 8
      host: dremio.production.com
      port: 443
      username: "{{ env_var('DREMIO_PROD_USER') }}"
      password: "{{ env_var('DREMIO_PROD_PASSWORD') }}"
      use_ssl: true
      object_storage_source: MinIO
      object_storage_path: datalake
      datalake_name: "Production"
```

### Настройте dbt_project.yml

```yaml
# dbt_project.yml
name: 'dremio_analytics'
version: '1.0.0'
config-version: 2

profile: 'dremio_analytics'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

# Configuration globale modèles
models:
  dremio_analytics:
    # Modèles staging - vues pour développement rapide
    staging:
      +materialized: view
      +schema: staging
      
    # Modèles intermédiaires - éphémères ou vues
    intermediate:
      +materialized: view
      +schema: intermediate
      
    # Tables fait - tables pour performance
    facts:
      +materialized: table
      +schema: facts
      
    # Tables dimension - tables pour performance
    dimensions:
      +materialized: table
      +schema: dimensions
      
    # Modèles mart - tables pour reporting
    marts:
      +materialized: table
      +schema: marts

# Documentation
docs:
  dremio_analytics:
    +enabled: true

# Configuration seed
seeds:
  dremio_analytics:
    +schema: seeds
    +quote_columns: false

# Configuration snapshot
snapshots:
  dremio_analytics:
    +target_schema: snapshots
    +strategy: timestamp
    +updated_at: updated_at

vars:
  # Variables globales
  current_year: 2025
  reporting_currency: 'USD'
```

### Переменные среды

```bash
# Fichier .env (ne jamais commit sur Git!)
export DREMIO_USER=admin
export DREMIO_PASSWORD=your_secure_password
export DREMIO_PROD_USER=dbt_service_account
export DREMIO_PROD_PASSWORD=prod_password
```

### Тестовое соединение

```bash
# Vérifier que dbt peut se connecter
dbt debug

# Sortie attendue:
# Configuration:
#   profiles.yml file [OK found and valid]
#   dbt_project.yml file [OK found and valid]
# 
# Connection:
#   host: localhost
#   port: 9047
#   user: admin
#   database: datalake
#   Connection test: [OK connection ok]
```

---

## Моделирование данных

### Промежуточные модели

Промежуточные модели очищают и стандартизируют необработанные данные из источников.

#### Установить источники

```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: bronze
    description: Données brutes depuis ingestion Airbyte
    database: MinIO
    schema: datalake.bronze
    tables:
      - name: raw_customers
        description: Données clients brutes depuis PostgreSQL
        columns:
          - name: customer_id
            description: Clé primaire
            tests:
              - unique
              - not_null
          - name: email
            description: Adresse email client
            tests:
              - not_null
          - name: created_at
            description: Horodatage création compte
            
      - name: raw_orders
        description: Données commandes brutes
        columns:
          - name: order_id
            tests:
              - unique
              - not_null
          - name: customer_id
            tests:
              - not_null
              - relationships:
                  to: source('bronze', 'raw_customers')
                  field: customer_id
```

#### Пример промежуточной модели

```sql
-- models/staging/stg_customers.sql
{{
    config(
        materialized='view',
        tags=['staging', 'customers']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('bronze', 'raw_customers') }}
),

cleaned AS (
    SELECT
        -- Clé primaire
        customer_id,
        
        -- Standardisation nom
        TRIM(UPPER(COALESCE(first_name, ''))) AS first_name,
        TRIM(UPPER(COALESCE(last_name, ''))) AS last_name,
        TRIM(UPPER(COALESCE(first_name, ''))) || ' ' || 
        TRIM(UPPER(COALESCE(last_name, ''))) AS full_name,
        
        -- Informations contact
        LOWER(TRIM(email)) AS email,
        REGEXP_REPLACE(phone, '[^0-9]', '') AS phone_clean,
        
        -- Adresse
        TRIM(address) AS address,
        UPPER(TRIM(city)) AS city,
        UPPER(TRIM(state)) AS state,
        LPAD(CAST(zip_code AS VARCHAR), 5, '0') AS zip_code,
        UPPER(TRIM(country)) AS country,
        
        -- Horodatages
        created_at,
        updated_at,
        
        -- Métadonnées
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM source
    
    -- Filtres qualité données
    WHERE customer_id IS NOT NULL
      AND email IS NOT NULL
      AND email LIKE '%@%'
      AND created_at IS NOT NULL
)

SELECT * FROM cleaned
```

```sql
-- models/staging/stg_orders.sql
{{
    config(
        materialized='view',
        tags=['staging', 'orders']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('bronze', 'raw_orders') }}
),

cleaned AS (
    SELECT
        -- Clé primaire
        order_id,
        
        -- Clés étrangères
        customer_id,
        
        -- Détails commande
        order_date,
        CAST(amount AS DECIMAL(10,2)) AS amount,
        CAST(tax AS DECIMAL(10,2)) AS tax,
        CAST(shipping AS DECIMAL(10,2)) AS shipping,
        CAST(amount + tax + shipping AS DECIMAL(10,2)) AS total_amount,
        
        -- Normalisation statut
        CASE 
            WHEN UPPER(status) IN ('COMPLETE', 'COMPLETED', 'SUCCESS') 
                THEN 'COMPLETED'
            WHEN UPPER(status) IN ('PENDING', 'PROCESSING') 
                THEN 'PENDING'
            WHEN UPPER(status) IN ('CANCEL', 'CANCELLED', 'CANCELED') 
                THEN 'CANCELLED'
            WHEN UPPER(status) IN ('FAIL', 'FAILED', 'ERROR') 
                THEN 'FAILED'
            ELSE 'UNKNOWN'
        END AS status,
        
        -- Méthode paiement
        UPPER(TRIM(payment_method)) AS payment_method,
        
        -- Horodatages
        created_at,
        updated_at,
        
        -- Métadonnées
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM source
    
    WHERE order_id IS NOT NULL
      AND customer_id IS NOT NULL
      AND order_date IS NOT NULL
      AND amount >= 0
)

SELECT * FROM cleaned
```

### Промежуточные модели

Промежуточные модели объединяют и обогащают данные.

```sql
-- models/intermediate/int_customer_orders.sql
{{
    config(
        materialized='view',
        tags=['intermediate', 'customer_orders']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customer_orders AS (
    SELECT
        -- Attributs client
        c.customer_id,
        c.full_name,
        c.email,
        c.city,
        c.state,
        c.country,
        c.created_at AS customer_created_at,
        
        -- Attributs commande
        o.order_id,
        o.order_date,
        o.amount,
        o.tax,
        o.shipping,
        o.total_amount,
        o.status,
        o.payment_method,
        
        -- Champs calculés
        DATEDIFF('day', c.created_at, o.order_date) AS days_since_signup,
        CASE 
            WHEN DATEDIFF('day', c.created_at, o.order_date) <= 30 
                THEN 'New Customer'
            WHEN DATEDIFF('day', c.created_at, o.order_date) <= 180 
                THEN 'Regular Customer'
            ELSE 'Long-term Customer'
        END AS customer_segment,
        
        -- Classification commande
        CASE
            WHEN o.total_amount < 50 THEN 'Small'
            WHEN o.total_amount < 200 THEN 'Medium'
            ELSE 'Large'
        END AS order_size,
        
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id
)

SELECT * FROM customer_orders
```

### Таблицы сделаны

```sql
-- models/facts/fct_orders.sql
{{
    config(
        materialized='table',
        tags=['facts', 'orders']
    )
}}

WITH customer_orders AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
),

order_metrics AS (
    SELECT
        -- Clés
        order_id,
        customer_id,
        
        -- Dates
        order_date,
        DATE_TRUNC('month', order_date) AS order_month,
        DATE_TRUNC('year', order_date) AS order_year,
        EXTRACT(YEAR FROM order_date) AS year,
        EXTRACT(MONTH FROM order_date) AS month,
        EXTRACT(DAY FROM order_date) AS day,
        EXTRACT(DOW FROM order_date) AS day_of_week,
        
        -- Montants
        amount,
        tax,
        shipping,
        total_amount,
        
        -- Attributs
        status,
        payment_method,
        customer_segment,
        order_size,
        
        -- Drapeaux
        CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END AS is_completed,
        CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END AS is_cancelled,
        
        -- Ancienneté client
        days_since_signup,
        
        -- Métadonnées
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM customer_orders
)

SELECT * FROM order_metrics
```

### Таблицы размеров

```sql
-- models/dimensions/dim_customers.sql
{{
    config(
        materialized='table',
        tags=['dimensions', 'customers']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    WHERE status = 'COMPLETED'
),

customer_metrics AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS lifetime_orders,
        SUM(total_amount) AS lifetime_value,
        AVG(total_amount) AS average_order_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        MAX(order_date) AS most_recent_order_date
    FROM orders
    GROUP BY customer_id
),

final AS (
    SELECT
        -- Attributs client
        c.customer_id,
        c.first_name,
        c.last_name,
        c.full_name,
        c.email,
        c.phone_clean AS phone,
        c.address,
        c.city,
        c.state,
        c.zip_code,
        c.country,
        c.created_at AS registration_date,
        
        -- Métriques commande
        COALESCE(m.lifetime_orders, 0) AS lifetime_orders,
        COALESCE(m.lifetime_value, 0) AS lifetime_value,
        COALESCE(m.average_order_value, 0) AS average_order_value,
        m.first_order_date,
        m.last_order_date,
        
        -- Statut client
        CASE 
            WHEN m.customer_id IS NULL THEN 'No Orders'
            WHEN DATEDIFF('day', m.most_recent_order_date, CURRENT_DATE) <= 30 THEN 'Active'
            WHEN DATEDIFF('day', m.most_recent_order_date, CURRENT_DATE) <= 90 THEN 'At Risk'
            ELSE 'Churned'
        END AS customer_status,
        
        -- Niveau client
        CASE
            WHEN COALESCE(m.lifetime_value, 0) >= 1000 THEN 'Platinum'
            WHEN COALESCE(m.lifetime_value, 0) >= 500 THEN 'Gold'
            WHEN COALESCE(m.lifetime_value, 0) >= 100 THEN 'Silver'
            ELSE 'Bronze'
        END AS customer_tier,
        
        -- Métadonnées
        c.updated_at,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM customers c
    LEFT JOIN customer_metrics m
        ON c.customer_id = m.customer_id
)

SELECT * FROM final
```

### Модели рынка

```sql
-- models/marts/mart_customer_lifetime_value.sql
{{
    config(
        materialized='table',
        tags=['marts', 'customer_analytics']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('fct_orders') }}
    WHERE is_completed = 1
),

customer_cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', registration_date) AS cohort_month
    FROM customers
),

customer_summary AS (
    SELECT
        c.customer_id,
        c.full_name,
        c.email,
        c.city,
        c.state,
        c.registration_date,
        cc.cohort_month,
        c.customer_status,
        c.customer_tier,
        
        -- Métriques commande
        c.lifetime_orders,
        c.lifetime_value,
        c.average_order_value,
        c.first_order_date,
        c.last_order_date,
        
        -- Métriques calculées
        DATEDIFF('day', c.first_order_date, c.last_order_date) AS customer_lifespan_days,
        CASE 
            WHEN c.lifetime_orders > 1 
            THEN DATEDIFF('day', c.first_order_date, c.last_order_date) / (c.lifetime_orders - 1)
            ELSE NULL
        END AS avg_days_between_orders,
        
        -- Recency, Frequency, Monetary (RFM)
        DATEDIFF('day', c.last_order_date, CURRENT_DATE) AS recency_days,
        c.lifetime_orders AS frequency,
        c.lifetime_value AS monetary,
        
        -- Scores RFM (1-5)
        NTILE(5) OVER (ORDER BY DATEDIFF('day', c.last_order_date, CURRENT_DATE) DESC) AS recency_score,
        NTILE(5) OVER (ORDER BY c.lifetime_orders) AS frequency_score,
        NTILE(5) OVER (ORDER BY c.lifetime_value) AS monetary_score,
        
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM customers c
    LEFT JOIN customer_cohorts cc
        ON c.customer_id = cc.customer_id
)

SELECT * FROM customer_summary
```

---

## Тестовая среда

### Интегрированные тесты

```yaml
# models/staging/schema.yml
version: 2

models:
  - name: stg_customers
    description: Données clients nettoyées et standardisées
    columns:
      - name: customer_id
        description: Clé primaire
        tests:
          - unique
          - not_null
          
      - name: email
        description: Email client
        tests:
          - not_null
          - unique
          
      - name: state
        description: Code état US
        tests:
          - accepted_values:
              values: ['CA', 'NY', 'TX', 'FL', 'IL']
              quote: true
              
      - name: created_at
        description: Date inscription
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= '2020-01-01'"
```

### Персонализированные тесты

```sql
-- tests/assert_positive_order_amounts.sql
-- Test que tous les montants commande sont positifs

SELECT
    order_id,
    customer_id,
    amount
FROM {{ ref('stg_orders') }}
WHERE amount < 0
```

```sql
-- tests/assert_valid_email_format.sql
-- Test que tous les emails ont un format valide

SELECT
    customer_id,
    email
FROM {{ ref('stg_customers') }}
WHERE email NOT LIKE '%@%.%'
   OR email LIKE '%..%'
   OR email LIKE '.%'
   OR email LIKE '%.'
```

### Общие тесты

```sql
-- macros/generic_tests/test_not_empty_string.sql
{% test not_empty_string(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NULL
   OR TRIM({{ column_name }}) = ''

{% endtest %}
```

Использовать:
```yaml
# models/staging/schema.yml
columns:
  - name: full_name
    tests:
      - not_empty_string
```

### Запуск тестов

```bash
# Exécuter tous les tests
dbt test

# Exécuter tests pour modèle spécifique
dbt test --select stg_customers

# Exécuter tests pour tag spécifique
dbt test --select tag:staging

# Exécuter type test spécifique
dbt test --select test_type:unique
dbt test --select test_type:not_null
```

---

## Документация

### Документация модели

```yaml
# models/marts/schema.yml
version: 2

models:
  - name: mart_customer_lifetime_value
    description: |
      Analyse valeur vie client avec segmentation RFM.
      
      Ce mart combine les attributs client avec le comportement d'achat
      pour calculer la valeur vie, les scores RFM et les segments client.
      
      **Fréquence Mise à Jour**: Quotidien à 2h UTC
      
      **Sources de Données**:
      - dim_customers: Données maître client
      - fct_orders: Commandes complètes uniquement
      
      **Métriques Clés**:
      - Valeur Vie: Revenu total du client
      - Scores RFM: Recency, Frequency, Monetary (échelle 1-5)
      - Niveau Client: Bronze/Silver/Gold/Platinum
      
    columns:
      - name: customer_id
        description: Identifiant client unique (PK)
        tests:
          - unique
          - not_null
          
      - name: lifetime_value
        description: |
          Revenu total généré par le client sur toutes les commandes complètes.
          Exclut les commandes annulées et échouées.
        tests:
          - not_null
          
      - name: recency_score
        description: |
          Score RFM recency (1-5).
          5 = Achat le plus récent (meilleur)
          1 = Achat le plus ancien (pire)
          
      - name: frequency_score
        description: |
          Score RFM frequency (1-5).
          5 = Plus de commandes (meilleur)
          1 = Moins de commandes (pire)
          
      - name: monetary_score
        description: |
          Score RFM monetary (1-5).
          5 = Dépenses les plus élevées (meilleur)
          1 = Dépenses les plus faibles (pire)
```

### Добавить описания

```sql
-- models/staging/stg_customers.sql
{{
    config(
        materialized='view',
        tags=['staging', 'customers']
    )
}}

-- Description: Modèle staging pour données client
-- Source: bronze.raw_customers (depuis PostgreSQL via Airbyte)
-- Transformations:
--   - Standardisation nom (UPPER TRIM)
--   - Normalisation email (minuscules)
--   - Nettoyage téléphone (chiffres uniquement)
--   - Padding code postal (5 chiffres)
-- Qualité Données: Filtre enregistrements avec IDs null ou emails invalides

WITH source AS (
    SELECT * FROM {{ source('bronze', 'raw_customers') }}
),
...
```

### Создание документации

```bash
# Générer site documentation
dbt docs generate

# Servir documentation localement
dbt docs serve

# Ouvre navigateur sur http://localhost:8080
```

**Документация по функциям**:
- **Графики происхождения**: визуальное представление зависимостей модели.
- **Сведения о столбце**: описания, типы, тесты.
- **Новизна источника**: когда данные загружены.
- **Просмотр проекта**: содержимое README.
- **Поиск**: поиск моделей, столбцов, описаний.

---

## Макросы и пакеты

### Пользовательские макросы

```sql
-- macros/calculate_age.sql
{% macro calculate_age(birth_date) %}
    DATEDIFF('year', {{ birth_date }}, CURRENT_DATE)
{% endmacro %}
```

Использовать:
```sql
SELECT
    customer_id,
    {{ calculate_age('birth_date') }} AS age
FROM {{ ref('stg_customers') }}
```

### Многоразовые фрагменты SQL

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

### Установочные пакеты

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
    
  - package: calogica/dbt_expectations
    version: 0.10.1
    
  - package: dbt-labs/codegen
    version: 0.12.1
```

Установить пакеты:
```bash
dbt deps

# Packages installés dans dbt_packages/
```

### Использовать пакет макросов

```sql
-- Utiliser dbt_utils
SELECT
    {{ dbt_utils.surrogate_key(['customer_id', 'order_id']) }} AS unique_key,
    customer_id,
    order_id
FROM {{ ref('int_customer_orders') }}
```

```yaml
# Utiliser dbt_expectations
tests:
  - dbt_expectations.expect_column_values_to_be_between:
      min_value: 0
      max_value: 10000
      
  - dbt_expectations.expect_column_values_to_match_regex:
      regex: "^[A-Z]{2}$"
```

---

## Инкрементные модели

### Базовая инкрементальная модель

```sql
-- models/facts/fct_orders_incremental.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='sync_all_columns'
    )
}}

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    updated_at
FROM {{ ref('stg_orders') }}

{% if is_incremental() %}
    -- Traiter uniquement enregistrements nouveaux ou mis à jour
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

### Дополнительные стратегии

#### 1. Добавление стратегии

```sql
{{
    config(
        materialized='incremental',
        incremental_strategy='append'
    )
}}

SELECT * FROM {{ ref('stg_events') }}

{% if is_incremental() %}
    WHERE event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
{% endif %}
```

#### 2. Стратегия слияния

```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        merge_update_columns=['status', 'updated_at']
    )
}}

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    updated_at
FROM {{ ref('stg_orders') }}

{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

#### 3. Удалить+Вставить стратегию

```sql
{{
    config(
        materialized='incremental',
        unique_key='order_date',
        incremental_strategy='delete+insert'
    )
}}

SELECT
    order_date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_revenue
FROM {{ ref('fct_orders') }}

{% if is_incremental() %}
    WHERE order_date >= CURRENT_DATE - INTERVAL '7' DAY
{% endif %}

GROUP BY order_date
```

### Полное обновление

```bash
# Forcer rafraîchissement complet modèle incrémental
dbt run --full-refresh --select fct_orders_incremental

# Ou pour tous les modèles incrémentaux
dbt run --full-refresh --select config.materialized:incremental
```

---

## Рабочий процесс оркестрации

### dbt Команды запуска

```bash
# Exécuter tous les modèles
dbt run

# Exécuter modèle spécifique
dbt run --select stg_customers

# Exécuter modèle et dépendances aval
dbt run --select stg_customers+

# Exécuter modèle et dépendances amont
dbt run --select +stg_customers

# Exécuter modèles par tag
dbt run --select tag:staging
dbt run --select tag:facts

# Exécuter modèles par chemin
dbt run --select models/staging/
dbt run --select models/marts/

# Exclure modèles
dbt run --exclude tag:deprecated
```

### Полный конвейер

```bash
#!/bin/bash
# scripts/run_dbt_pipeline.sh

set -e  # Sortir sur erreur

echo "Démarrage pipeline dbt..."

# 1. Compiler projet
echo "Compilation projet..."
dbt compile

# 2. Exécuter modèles staging
echo "Exécution modèles staging..."
dbt run --select tag:staging

# 3. Tester modèles staging
echo "Test modèles staging..."
dbt test --select tag:staging

# 4. Exécuter modèles intermédiaires
echo "Exécution modèles intermédiaires..."
dbt run --select tag:intermediate

# 5. Exécuter faits et dimensions
echo "Exécution faits et dimensions..."
dbt run --select tag:facts tag:dimensions

# 6. Tester faits et dimensions
echo "Test faits et dimensions..."
dbt test --select tag:facts tag:dimensions

# 7. Exécuter marts
echo "Exécution marts..."
dbt run --select tag:marts

# 8. Tester marts
echo "Test marts..."
dbt test --select tag:marts

# 9. Générer documentation
echo "Génération documentation..."
dbt docs generate

echo "Pipeline terminé!"
```

### Интеграция воздушного потока

```python
# dags/dbt_pipeline_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dbt_daily_pipeline',
    default_args=default_args,
    description='Pipeline transformation dbt quotidien',
    schedule_interval='0 2 * * *',  # 2h quotidien
    catchup=False,
    tags=['dbt', 'transformation'],
)

# Tâche: Exécuter modèles staging
run_staging = BashOperator(
    task_id='run_staging',
    bash_command='cd /opt/dbt && dbt run --select tag:staging',
    dag=dag,
)

# Tâche: Tester modèles staging
test_staging = BashOperator(
    task_id='test_staging',
    bash_command='cd /opt/dbt && dbt test --select tag:staging',
    dag=dag,
)

# Tâche: Exécuter faits et dimensions
run_facts_dims = BashOperator(
    task_id='run_facts_dimensions',
    bash_command='cd /opt/dbt && dbt run --select tag:facts tag:dimensions',
    dag=dag,
)

# Tâche: Exécuter marts
run_marts = BashOperator(
    task_id='run_marts',
    bash_command='cd /opt/dbt && dbt run --select tag:marts',
    dag=dag,
)

# Tâche: Générer docs
generate_docs = BashOperator(
    task_id='generate_docs',
    bash_command='cd /opt/dbt && dbt docs generate',
    dag=dag,
)

# Définir dépendances tâches
run_staging >> test_staging >> run_facts_dims >> run_marts >> generate_docs
```

---

## Лучшие практики

### 1. Соглашения об именах

```
Staging:     stg_{source}_{table}        ex: stg_postgres_customers
Intermédiaire: int_{entity}_{verb}         ex: int_customer_orders
Faits:       fct_{entity}                ex: fct_orders
Dimensions:  dim_{entity}                ex: dim_customers
Marts:       mart_{business_area}_{entity} ex: mart_finance_revenue
```

### 2. Структура папок

```
models/
├── staging/
│   ├── postgres/
│   │   ├── stg_postgres_customers.sql
│   │   └── stg_postgres_orders.sql
│   ├── stripe/
│   │   └── stg_stripe_payments.sql
│   └── sources.yml
├── intermediate/
│   ├── int_customer_orders.sql
│   └── int_customer_payments.sql
├── facts/
│   ├── fct_orders.sql
│   └── fct_payments.sql
├── dimensions/
│   ├── dim_customers.sql
│   └── dim_products.sql
└── marts/
    ├── finance/
    │   └── mart_finance_revenue.sql
    └── marketing/
        └── mart_marketing_attribution.sql
```

### 3. Используйте CTE

```sql
-- Bon: CTEs claires et lisibles
WITH source_data AS (
    SELECT * FROM {{ source('bronze', 'raw_orders') }}
),

filtered_data AS (
    SELECT *
    FROM source_data
    WHERE order_date >= '2025-01-01'
),

final AS (
    SELECT
        order_id,
        SUM(amount) AS total_amount
    FROM filtered_data
    GROUP BY order_id
)

SELECT * FROM final
```

### 4. Добавляйте тесты заранее

```yaml
# Toujours tester clés primaires
tests:
  - unique
  - not_null

# Tester clés étrangères
tests:
  - relationships:
      to: ref('dim_customers')
      field: customer_id

# Tester logique métier
tests:
  - dbt_utils.expression_is_true:
      expression: "total_amount >= 0"
```

### 5. Документируйте все

```sql
-- Bonne documentation
-- models/marts/mart_customer_ltv.sql

-- Objectif: Calculer valeur vie client avec segmentation RFM
-- Propriétaire: Équipe Analytics (analytics@company.com)
-- Fréquence Mise à Jour: Quotidien à 2h
-- Dépendances: dim_customers, fct_orders
-- Consommateurs: Tableau de bord exécutif, campagnes marketing
-- SLA: Doit terminer avant 6h pour rapports quotidiens
```

---

## Поиск неисправностей

### Распространенные проблемы

#### Проблема 1: ошибка компиляции

**Ошибка**: `Compilation Error: Model not found`.

**Решение**:
```bash
# Vérifier si modèle existe
ls models/staging/stg_customers.sql

# Vérifier syntaxe ref()
SELECT * FROM {{ ref('stg_customers') }}  # Correct
SELECT * FROM {{ ref('staging.stg_customers') }}  # Incorrect
```

#### Проблема 2: циклические зависимости

**Ошибка**: `Compilation Error: Circular dependency detected`.

**Решение**:
```bash
# Visualiser lignage
dbt docs generate
dbt docs serve

# Vérifier graphe dépendances dans interface
# Corriger en supprimant références circulaires
```

#### Проблема 3: Неудачные тесты

**Ошибка**: `ERROR test not_null_stg_customers_email (FAIL 15)`.

**Решение**:
```sql
-- Déboguer test échoué
SELECT *
FROM {{ ref('stg_customers') }}
WHERE email IS NULL;

-- Corriger données source ou ajouter filtre
WHERE email IS NOT NULL
```

#### Проблема 4: инкрементная модель не работает

**Ошибка**: инкрементная модель каждый раз перестраивается с нуля.

**Решение**:
```sql
-- Vérifier unique_key défini
{{
    config(
        unique_key='order_id'  -- Doit être défini
    )
}}

-- Vérifier condition if
{% if is_incremental() %}
    -- Ce bloc doit exister
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

---

## Краткое содержание

Это полное руководство по разработке dbt охватывает:

- **Конфигурация проекта**: инициализация, настройка, настройка среды.
- **Моделирование данных**: промежуточные, промежуточные, фактические, размерные и рыночные модели.
- **Рамочные тесты**: интегрированные тесты, специальные тесты, общие тесты.
– **Документация**: документация по модели, автоматически создаваемая документация сайта.
- **Макросы и пакеты**: многоразовый код, dbt_utils, ожидания.
- **Инкрементные модели**: стратегии добавления, объединения, удаления+вставки.
- **Оркестрация рабочего процесса**: команды dbt, сценарии конвейера, интеграция Airflow.
– **Рекомендации**: соглашения об именах, структура папок, документация.
- **Устранение неполадок**: распространенные проблемы и решения.

Ключевые моменты, которые следует запомнить:
- Используйте операторы SQL SELECT, dbt управляет DDL/DML.
- Тестируйте заранее и часто с помощью интегрированной среды тестирования.
- Модели документов для аналитики самообслуживания.
- Используйте инкрементные модели для больших таблиц.
- Следуйте единообразным соглашениям об именах.
- Использование пакетов для общих функций.

**Сопутствующая документация:**
- [Руководство по установке Dremio](./dremio-setup.md)
- [Руководство по качеству данных](./data-quality.md)
- [Архитектура: поток данных](../architecture/data-flow.md)
- [Учебное пособие по первым шагам](../getting-started/first-steps.md)

---

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.