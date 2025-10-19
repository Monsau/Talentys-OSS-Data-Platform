# Veri Akışı Mimarisi

**Sürüm**: 3.2.0  
**Son Güncelleme**: 16 Ekim 2025  
**Dil**: Fransızca

## İçindekiler

1. [Genel Bakış](#genel bakış)
2. [Uçtan Uca Veri Akışı](#uçtan uca veri akışı)
3. [Besleme Katmanı](#besleme katmanı)
4. [Depolama Katmanı](#depolama katmanı)
5. [İşleme Katmanı](#işleme katmanı)
6. [Sunum Katmanı](#sunum katmanı)
7. [Veri Akışı Modelleri](#dataflow-models)
8. [Performansla İlgili Hususlar](#performansla ilgili hususlar)
9. [Veri Akışı İzleme](#veri akışı izleme)
10. [İyi Uygulamalar](#iyi uygulamalar)

---

## Genel Bakış

Bu belge, ilk veri alımından son tüketime kadar platformun tüm veri akışı mimarisinin ayrıntılarını verir. Bu akışları anlamak, performansı optimize etmek, sorunları gidermek ve etkili veri hatları tasarlamak açısından kritik öneme sahiptir.

### Veri Akışı Prensipleri

Mimarimiz şu temel ilkeleri takip eder:

1. **Tek Yönlü Akış**: Veriler net ve öngörülebilir bir yönde hareket eder
2. **Katmanlı İşleme**: Her katmanın belirli bir sorumluluğu vardır
3. **Ayrılmış Bileşenler**: Hizmetler, iyi tanımlanmış arayüzler aracılığıyla iletişim kurar
4. **Idempotence**: İşlemler güvenli bir şekilde tekrarlanabilir
5. **Gözlemlenebilirlik**: Her adım günlüğe kaydedilir ve izlenir

### Mimari Katmanlar

```mermaid
graph TB
    subgraph "Couche d'Ingestion"
        A1[Sources Externes]
        A2[Connecteurs Airbyte]
    end
    
    subgraph "Couche de Stockage"
        B1[MinIO S3]
        B2[PostgreSQL]
        B3[Elasticsearch]
    end
    
    subgraph "Couche de Traitement"
        C1[Dremio Lakehouse]
        C2[Transformations dbt]
    end
    
    subgraph "Couche de Présentation"
        D1[Tableaux de Bord Superset]
        D2[API Arrow Flight]
        D3[API REST]
    end
    
    A1 --> A2
    A2 --> B1
    A2 --> B2
    A2 --> B3
    
    B1 --> C1
    B2 --> C1
    B3 --> C1
    
    C1 --> C2
    C2 --> C1
    
    C1 --> D1
    C1 --> D2
    C1 --> D3
    
    style A1 fill:#e1f5ff
    style A2 fill:#615EFF,color:#fff
    style B1 fill:#C72E49,color:#fff
    style B2 fill:#336791,color:#fff
    style B3 fill:#005571,color:#fff
    style C1 fill:#FDB515
    style C2 fill:#FF694B,color:#fff
    style D1 fill:#20A7C9,color:#fff
```

---

## Uçtan Uca Veri Akışı

### İşlem Hattı Sırasını Tamamlayın

```mermaid
sequenceDiagram
    participant Source as Source Externe
    participant Airbyte as Plateforme Airbyte
    participant Storage as Couche de Stockage
    participant Dremio as Dremio Lakehouse
    participant dbt as dbt Core
    participant Superset as Superset BI
    participant User as Utilisateur Final
    
    Source->>Airbyte: 1. Connexion à la source
    Note over Airbyte: Extraction des données via<br/>connecteur source
    
    Airbyte->>Storage: 2. Chargement des données brutes
    Note over Storage: Stockage dans MinIO (S3),<br/>PostgreSQL ou Elasticsearch
    
    Storage->>Dremio: 3. Connexion source de données
    Note over Dremio: Création datasets virtuels,<br/>application des réflexions
    
    Dremio->>dbt: 4. Requête données brutes
    Note over dbt: Transformation via<br/>modèles SQL
    
    dbt->>Dremio: 5. Écriture données transformées
    Note over Dremio: Stockage dans couches<br/>curées (Silver/Gold)
    
    Dremio->>Superset: 6. Exposition via Arrow Flight
    Note over Superset: Requête datasets<br/>optimisés
    
    Superset->>User: 7. Affichage tableaux de bord
    Note over User: Analytique interactive<br/>et reporting
```

### Veri Akışı Adımları

| Adım | Bileşen | Giriş | Çıkış | Gecikme |
|----------|----------|-----------|-----------|---------|
| **Çıkartma** | Airbyte | Harici API'ler/BD'ler | Ham JSON/CSV | 1-60 dakika |
| **Yükleniyor** | Depolama Katmanı | Ham Dosyalar | Seçilmiş Kovalar | <1 dakika |
| **Kataloglama** | Dremio | Depolama yolları | Sanal veri kümeleri | <1 dakika |
| **Dönüşüm** | dbt | Bronz Masalar | Gümüş/Altın masalar | 5-30 dakika |
| **Optimizasyon** | Dremio Düşünceler | Ham Sorgular | Gizli sonuçlar | Gerçek zamanlı |
| **Görselleştirme** | Süperset | SQL Sorguları | Grafikler/Gösterge Tabloları | <5 saniye |

---

## Besleme Katmanı

### Airbyte Veri Çıkarma

Airbyte, harici kaynaklardan alınan tüm veri alımını yönetir.

#### Kaynak Bağlantı Akışı

```mermaid
flowchart LR
    A[Source Externe] --> B{Type de Connexion}
    
    B -->|Base de données| C[JDBC/Native]
    B -->|API| D[REST/GraphQL]
    B -->|Fichier| E[FTP/S3]
    
    C --> F[Worker Airbyte]
    D --> F
    E --> F
    
    F --> G{Mode de Sync}
    
    G -->|Full Refresh| H[Lecture toutes données]
    G -->|Incrémental| I[Lecture changements seulement]
    
    H --> J[Normalisation]
    I --> J
    
    J --> K[Écriture vers Destination]
    
    style A fill:#e1f5ff
    style F fill:#615EFF,color:#fff
    style K fill:#4CAF50,color:#fff
```

#### Veri Çıkarma Yöntemleri

**1. Tam Yenileme**
```yaml
# Full refresh extrait toutes les données à chaque sync
sync_mode: full_refresh
destination_sync_mode: overwrite

# Cas d'usage:
# - Petits datasets (<1M lignes)
# - Pas de suivi fiable des changements
# - Snapshots complets nécessaires
```

**2. Artımlı Senkronizasyon**
```yaml
# Sync incrémental extrait uniquement les données nouvelles/modifiées
sync_mode: incremental
destination_sync_mode: append_dedup
cursor_field: updated_at

# Cas d'usage:
# - Grands datasets (>1M lignes)
# - Possède champ timestamp ou curseur
# - Optimisation performance sync
```

**3. Veri Yakalamayı Değiştir (CDC)**
```yaml
# CDC utilise les logs de transaction de la base de données
method: CDC
replication_method: LOG_BASED

# Bases de données supportées:
# - PostgreSQL (WAL)
# - MySQL (binlog)
# - MongoDB (change streams)
# - SQL Server (change tracking)
```

### Airbyte API Entegrasyonu

```bash
# Déclencher sync via API
curl -X POST http://localhost:8001/api/v1/connections/sync \
  -H "Content-Type: application/json" \
  -d '{
    "connectionId": "your-connection-id"
  }'

# Vérifier statut sync
curl -X POST http://localhost:8001/api/v1/jobs/get \
  -H "Content-Type: application/json" \
  -d '{
    "id": "job-id"
  }'
```

### Ekstraksiyon Performansı

| Kaynak Türü | Akış | Önerilen Frekans |
|----------------|----------|------------|
| PostgreSQL | 50-100k satır/sn | Her 15-60 dakikada bir |
| REST API'si | 1-10k istek/sn | Her 5-30 dakikada bir |
| CSV dosyaları | 100-500 MB/sn | Günlük |
| MongoDB | 10-50 bin belge/sn | Her 15-60 dakikada bir |
| MySQL CDC'si | Gerçek zamanlı | Sürekli |

---

## Depolama Katmanı

### MinIO S3 Depolama

MinIO ham ve işlenmiş verileri hiyerarşik bir yapıda saklar.

#### Kova Organizasyonu

```mermaid
graph TD
    A[Racine MinIO] --> B[bronze/]
    A --> C[silver/]
    A --> D[gold/]
    A --> E[logs/]
    
    B --> B1[raw/date=2025-10-16/]
    B --> B2[landing/source=postgres/]
    
    C --> C1[cleaned/customers/]
    C --> C2[joined/orders/]
    
    D --> D1[aggregated/daily_revenue/]
    D --> D2[reports/customer_metrics/]
    
    E --> E1[airbyte/]
    E --> E2[dbt/]
    
    style A fill:#C72E49,color:#fff
    style B fill:#CD7F32,color:#fff
    style C fill:#C0C0C0
    style D fill:#FFD700
```

#### Veri Yolu Yapısı

```
s3://datalake/
├── bronze/                      # Données brutes d'Airbyte
│   ├── postgres/
│   │   ├── customers/
│   │   │   └── date=2025-10-16/
│   │   │       └── data.parquet
│   │   └── orders/
│   │       └── date=2025-10-16/
│   │           └── data.parquet
│   ├── api/
│   │   └── rest_endpoint/
│   │       └── timestamp=20251016_120000/
│   │           └── response.json
│   └── files/
│       └── csv_import/
│           └── batch_001.csv
│
├── silver/                      # Données nettoyées et validées
│   ├── customers/
│   │   └── version=v2/
│   │       └── customers_cleaned.parquet
│   └── orders/
│       └── version=v2/
│           └── orders_enriched.parquet
│
└── gold/                        # Agrégats prêts pour le métier
    ├── daily_revenue/
    │   └── year=2025/month=10/
    │       └── day=16/
    │           └── revenue.parquet
    └── customer_metrics/
        └── snapshot=2025-10-16/
            └── metrics.parquet
```

### Depolama Formatı Stratejisi

| Katman | Biçim | Sıkıştırma | Bölümleme | Nedeni |
|----------|-----------|------------|------|----------|
| **Bronz** | Parke | Hızlı | Tarihe göre | Hızlı yazma, iyi sıkıştırma |
| **Gümüş** | Parke | Hızlı | İş anahtarına göre | Etkili sorgular |
| **Altın** | Parke | ZSTD | Zaman dilimine göre | Maksimum Sıkıştırma |
| **Günlükler** | JSON | Gzip | Hizmete/tarihe göre | İnsanlar tarafından okunabilir |

### PostgreSQL Meta Veri Depolama

PostgreSQL depoları:
- Airbyte yapılandırması ve durumu
- Meta veriler ve dbt yürütme geçmişi
- Kontrol panelleri ve kullanıcılar süperset
- Uygulama günlükleri ve ölçümleri

```sql
-- Structure table état Airbyte
CREATE TABLE airbyte_state (
    connection_id UUID PRIMARY KEY,
    state JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Historique exécution dbt
CREATE TABLE dbt_run_history (
    run_id UUID PRIMARY KEY,
    project_name VARCHAR(255),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50),
    models_run INTEGER,
    tests_run INTEGER,
    metadata JSONB
);
```

### Elasticsearch Belge Depolama

Elasticsearch, günlükleri indeksler ve tam metin aramasına izin verir.

```json
{
  "index": "airbyte-logs-2025.10.16",
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "service": {"type": "keyword"},
      "message": {"type": "text"},
      "job_id": {"type": "keyword"},
      "connection_id": {"type": "keyword"},
      "records_synced": {"type": "integer"},
      "bytes_synced": {"type": "long"}
    }
  }
}
```

---

## İşleme Katmanı

### Dremio Veri Sanallaştırma

Dremio, tüm depolama kaynaklarında birleşik bir görünüm oluşturur.

#### Sanal Veri Kümesinin Oluşturulması

```mermaid
sequenceDiagram
    participant User as Ingénieur Données
    participant Dremio as Coordinateur Dremio
    participant MinIO as MinIO S3
    participant PG as PostgreSQL
    
    User->>Dremio: Ajout source S3
    Dremio->>MinIO: Liste buckets/objets
    MinIO-->>Dremio: Métadonnées retournées
    
    User->>Dremio: Promotion dossier en dataset
    Dremio->>Dremio: Inférence schéma
    
    User->>Dremio: Ajout source PostgreSQL
    Dremio->>PG: Découverte tables
    PG-->>Dremio: Schémas tables
    
    User->>Dremio: Création vue jointure
    Dremio->>Dremio: Création dataset virtuel
    
    User->>Dremio: Création réflexion
    Dremio->>Dremio: Construction cache agrégation
    
    Note over Dremio: Les requêtes sont maintenant accélérées !
```

#### Yansımalarla Hızlanma

Dremio yansımaları, anında performans için sorgu sonuçlarını önceden hesaplar.

```sql
-- Créer réflexion brute (sous-ensemble colonnes)
CREATE REFLECTION raw_customers
ON bronze.customers
USING DISPLAY (customer_id, name, email, created_at);

-- Créer réflexion agrégation
CREATE REFLECTION agg_daily_revenue
ON gold.orders
USING DIMENSIONS (order_date)
MEASURES (SUM(amount), COUNT(*), AVG(amount));

-- Les réflexions se rafraîchissent automatiquement selon la politique
ALTER REFLECTION agg_daily_revenue
SET REFRESH EVERY 1 HOUR;
```

**Yansımaların Performans Etkisi:**

| Sorgu Türü | Yansımasız | Yansımalı | Hızlanma |
|----------------||----------------|----------------|-----------|
| Basit SEÇ | 500ms | 50ms | 10x |
| Toplamalar | 5'ler | 100ms | 50x |
| Karmaşık JOIN'ler | 30'lar | 500ms | 60x |
| Büyük Taramalar | 120'ler | 2s | 60x |

### dbt dönüşümleri

dbt, ham verileri iş için hazır modellere dönüştürür.

#### Dönüşüm Akışı

```mermaid
flowchart TB
    A[Tables Bronze] --> B[Modèles Staging]
    B --> C[Modèles Intermédiaires]
    C --> D[Modèles Fait]
    C --> E[Modèles Dimension]
    D --> F[Modèles Mart]
    E --> F
    
    B -.->|dbt test| G[Tests Qualité Données]
    C -.->|dbt test| G
    D -.->|dbt test| G
    E -.->|dbt test| G
    
    F --> H[Couche Gold]
    
    style A fill:#CD7F32,color:#fff
    style B fill:#87CEEB
    style C fill:#90EE90
    style D fill:#FFB6C1
    style E fill:#DDA0DD
    style F fill:#F0E68C
    style H fill:#FFD700
```

#### Dönüşüm Hattı Örneği

```sql
-- models/staging/stg_customers.sql
-- Étape 1: Nettoyage et standardisation
WITH source AS (
    SELECT * FROM bronze.raw_customers
),

cleaned AS (
    SELECT
        customer_id,
        TRIM(UPPER(name)) AS customer_name,
        LOWER(email) AS email,
        phone,
        address,
        city,
        state,
        zip_code,
        created_at,
        updated_at
    FROM source
    WHERE customer_id IS NOT NULL
)

SELECT * FROM cleaned;
```

```sql
-- models/intermediate/int_customer_orders.sql
-- Étape 2: Jointure et enrichissement
WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

joined AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.email,
        o.order_id,
        o.order_date,
        o.amount,
        o.status
    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id
)

SELECT * FROM joined;
```

```sql
-- models/marts/fct_customer_lifetime_value.sql
-- Étape 3: Agrégation pour métriques métier
WITH customer_orders AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
),

metrics AS (
    SELECT
        customer_id,
        customer_name,
        email,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(amount) AS lifetime_value,
        AVG(amount) AS average_order_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        DATEDIFF('day', MIN(order_date), MAX(order_date)) AS customer_lifespan_days
    FROM customer_orders
    WHERE status = 'completed'
    GROUP BY customer_id, customer_name, email
)

SELECT * FROM metrics;
```

#### dbt Yürütme Akışı

```bash
# Exécution pipeline complète
dbt run --select staging        # Exécuter modèles staging
dbt test --select staging       # Tester modèles staging
dbt run --select intermediate   # Exécuter modèles intermédiaires
dbt test --select intermediate  # Tester modèles intermédiaires
dbt run --select marts          # Exécuter modèles mart
dbt test --select marts         # Tester modèles mart

# Générer documentation
dbt docs generate
dbt docs serve
```

### Veri Kökeni İzlenebilirliği

```mermaid
graph LR
    A[bronze.raw_customers] --> B[staging.stg_customers]
    C[bronze.raw_orders] --> D[staging.stg_orders]
    
    B --> E[intermediate.int_customer_orders]
    D --> E
    
    E --> F[marts.fct_customer_lifetime_value]
    
    F --> G[Tableau de Bord Superset:<br/>Analytique Client]
    
    style A fill:#CD7F32,color:#fff
    style C fill:#CD7F32,color:#fff
    style B fill:#C0C0C0
    style D fill:#C0C0C0
    style E fill:#C0C0C0
    style F fill:#FFD700
    style G fill:#20A7C9,color:#fff
```

---

## Sunum Katmanı

### Sorgu Yürütme Akışı

```mermaid
sequenceDiagram
    participant User as Utilisateur Tableau de Bord
    participant Superset as Serveur Superset
    participant Dremio as Coordinateur Dremio
    participant Reflection as Stockage Réflexion
    participant Storage as Couche Stockage
    
    User->>Superset: Ouvrir tableau de bord
    Superset->>Dremio: Exécuter requête SQL
    
    Dremio->>Dremio: Parser & optimiser requête
    
    alt Réflexion Disponible
        Dremio->>Reflection: Requête réflexion
        Reflection-->>Dremio: Résultats cachés (rapide)
    else Pas de Réflexion
        Dremio->>Storage: Scanner données brutes
        Storage-->>Dremio: Résultats scan complet (lent)
    end
    
    Dremio-->>Superset: Retourner résultats
    Superset->>Superset: Rendu graphiques
    Superset-->>User: Afficher tableau de bord
    
    Note over User,Superset: < 5 secondes au total
```

### API Erişim Modelleri

#### 1. Süper Ayar Kontrol Panelleri (BI Interactive)

```python
# Superset exécute SQL via SQLAlchemy
from superset import db

query = """
SELECT 
    order_date,
    SUM(amount) as daily_revenue
FROM gold.fct_daily_revenue
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY order_date
ORDER BY order_date
"""

results = db.session.execute(query)
```

#### 2. Arrow Flight API (Yüksek Performans)

```python
# Connexion Arrow Flight directe pour outils analytiques
from pyarrow import flight

client = flight.FlightClient("grpc://localhost:32010")

# Authentification
token = client.authenticate_basic_token("admin", "password123")

# Exécuter requête
descriptor = flight.FlightDescriptor.for_command(
    b"SELECT * FROM gold.customer_metrics LIMIT 1000"
)

flight_info = client.get_flight_info(descriptor)
reader = client.do_get(flight_info.endpoints[0].ticket)

# Lire comme Table Arrow (zero-copy)
table = reader.read_all()
df = table.to_pandas()
```

#### 3. REST API (Harici Entegrasyonlar)

```bash
# API REST Dremio pour automatisation
curl -X POST http://localhost:9047/api/v3/sql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT COUNT(*) FROM gold.customers"
  }'
```

---

## Veri Akışı Modelleri

### Model 1: ETL Toplu İşlem Hattı

```mermaid
gantt
    title Planification ETL Batch Quotidien
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Ingestion
    Extraction Airbyte (PostgreSQL)     :01:00, 30m
    Extraction Airbyte (APIs)           :01:30, 45m
    
    section Chargement
    Chargement vers Bronze MinIO        :02:15, 15m
    
    section Transformation
    Modèles Staging dbt                 :02:30, 20m
    Modèles Intermédiaires dbt          :02:50, 30m
    Modèles Mart dbt                    :03:20, 40m
    
    section Tests
    Tests Qualité Données dbt           :04:00, 15m
    
    section Optimisation
    Rafraîchissement Réflexions Dremio  :04:15, 20m
    
    section Présentation
    Préchauffage Cache Tableau de Bord  :04:35, 10m
```

### Model 2: Gerçek Zamanlı Akış

```mermaid
flowchart LR
    A[Événements CDC] -->|Continu| B[Worker Airbyte]
    B -->|Stream| C[Bronze MinIO]
    C -->|Micro-batch| D[Streaming Dremio]
    D -->|<1 min| E[Tableau de Bord Live]
    
    style A fill:#FF6B6B
    style B fill:#615EFF,color:#fff
    style C fill:#C72E49,color:#fff
    style D fill:#FDB515
    style E fill:#20A7C9,color:#fff
```

### Desen 3: Artımlı Güncellemeler

```sql
-- Modèle incrémental dbt
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns'
) }}

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    updated_at
FROM {{ source('bronze', 'orders') }}

{% if is_incremental() %}
    -- Traiter uniquement les enregistrements nouveaux ou mis à jour
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

### Model 4: Lambda Mimarisi (Toplu + Akış)

```mermaid
graph TB
    subgraph "Couche Vitesse (Temps Réel)"
        A1[Stream CDC] --> B1[Chargement Incrémental]
        B1 --> C1[Données Chaudes<br/>7 derniers jours]
    end
    
    subgraph "Couche Batch (Historique)"
        A2[Extraction Complète] --> B2[Chargement Batch]
        B2 --> C2[Données Froides<br/>>7 jours]
    end
    
    subgraph "Couche Présentation"
        C1 --> D[Vue Unifiée]
        C2 --> D
        D --> E[Tableau de Bord]
    end
    
    style A1 fill:#FF6B6B
    style A2 fill:#4A90E2
    style D fill:#FDB515
    style E fill:#20A7C9,color:#fff
```

---

## Performansla İlgili Hususlar

### Besleme Optimizasyonu

```yaml
# Configuration connexion Airbyte
sync_mode: incremental
destination_sync_mode: append_dedup
cursor_field: updated_at

# Ajustement performance
batch_size: 10000              # Enregistrements par batch
threads: 4                     # Workers parallèles
timeout_minutes: 60           # Timeout sync
retry_on_failure: true
max_retries: 3

# Optimisation réseau
compression: gzip
buffer_size_mb: 256
```

### Depolama Optimizasyonu

```python
# Options écriture Parquet pour compression optimale
import pyarrow.parquet as pq

pq.write_table(
    table,
    'output.parquet',
    compression='snappy',      # Compression rapide
    use_dictionary=True,       # Activer encodage dictionnaire
    row_group_size=1000000,    # 1M lignes par row group
    data_page_size=1048576,    # 1MB taille page
    write_statistics=True      # Activer statistiques pour pruning
)
```

### Sorgu Optimizasyonu

```sql
-- Bonnes pratiques requêtes Dremio

-- 1. Utiliser partition pruning
SELECT * FROM gold.orders
WHERE order_date >= '2025-10-01'  -- Élague partitions
  AND order_date < '2025-11-01';

-- 2. Exploiter les réflexions
-- Créer réflexion une fois, requêtes auto-accélérées
ALTER REFLECTION agg_orders SET ENABLED = TRUE;

-- 3. Utiliser column pruning
SELECT order_id, amount       -- Seulement colonnes nécessaires
FROM gold.orders
LIMIT 1000;

-- 4. Pousser les filtres
SELECT *
FROM gold.customers
WHERE state = 'CA'            -- Filtre poussé vers stockage
  AND lifetime_value > 1000;
```

### Dönüşümlerin Optimizasyonu

```sql
-- Techniques optimisation dbt

-- 1. Modèles incrémentaux pour grandes tables
{{ config(materialized='incremental') }}

-- 2. Tables partitionnées
{{ config(
    materialized='table',
    partition_by={
        'field': 'order_date',
        'data_type': 'date',
        'granularity': 'day'
    }
) }}

-- 3. Tables clusterisées pour meilleures jointures
{{ config(
    materialized='table',
    cluster_by=['customer_id']
) }}
```

### Performans Karşılaştırmaları

| Operasyon | Küçük Veri Kümesi<br/>(1 milyon satır) | Orta Veri Kümesi<br/>(100 milyon satır) | Büyük Veri Kümesi<br/>(1B satır) |
|-------------------------------|---------------------------|-------------------------------|---------------------------|
| **Airbyte'ı senkronize et** | 2 dakika | 30 dakika | 5 saat |
| **dbt yürütme** | 30 saniye | 10 dakika | 2 saat |
| **İnşaat Yansıması** | 10 saniye | 5 dakika | 30 dakika |
| **Kontrol Paneli Sorgusu** | <100ms | <500ms | <2s |

---

## Veri Akışı İzleme

### İzlenecek Temel Metrikler

```yaml
# Configuration métriques Prometheus
metrics:
  ingestion:
    - airbyte_records_synced_total
    - airbyte_sync_duration_seconds
    - airbyte_sync_failures_total
    
  storage:
    - minio_disk_usage_bytes
    - minio_objects_total
    - postgres_connections_active
    
  processing:
    - dremio_query_duration_seconds
    - dremio_reflection_refresh_seconds
    - dbt_model_execution_time
    
  serving:
    - superset_dashboard_load_time
    - superset_query_cache_hit_rate
    - api_requests_per_second
```

### İzleme Kontrol Paneli

```mermaid
graph TB
    subgraph "Santé Pipeline Données"
        A[Statut Sync Airbyte]
        B[Capacité Stockage]
        C[Performance Requêtes]
        D[Temps Chargement Tableaux de Bord]
    end
    
    subgraph "Alertes"
        E[Échecs Sync]
        F[Disque Plein]
        G[Requêtes Lentes]
        H[Erreurs API]
    end
    
    A -.->|Déclenche| E
    B -.->|Déclenche| F
    C -.->|Déclenche| G
    D -.->|Déclenche| H
    
    style E fill:#FF6B6B
    style F fill:#FF6B6B
    style G fill:#FFA500
    style H fill:#FF6B6B
```

### Günlük Toplama

```bash
# Requête Elasticsearch pour surveillance pipeline
curl -X GET "localhost:9200/airbyte-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "filter": [
          {"range": {"timestamp": {"gte": "now-1h"}}},
          {"term": {"level": "ERROR"}}
        ]
      }
    },
    "aggs": {
      "by_service": {
        "terms": {"field": "service"}
      }
    }
  }'
```

---

## En İyi Uygulamalar

### Veri Akışı Tasarımı

1. **Idempotence için Tasarım**
   - İşlemlerin güvenli bir şekilde tekrarlanabileceğinin garantisi
   - Tekilleştirme için benzersiz anahtarlar kullanın
   - Uygun hata yönetimini uygulayın

2. **Veri Kalitesi Kontrollerini Uygulayın**
   ```sql
   -- Exemple test dbt
   -- tests/assert_positive_amounts.sql
   SELECT *
   FROM {{ ref('fct_orders') }}
   WHERE amount <= 0
   ```

3. **Büyük Veri Kümelerini Bölümleyin**
   ```python
   # Partitionner par date pour requêtes efficaces
   df.write.partitionBy('order_date').parquet('s3://bucket/orders/')
   ```

4. **Uygun Senkronizasyon Modlarını Kullanın**
   - Tam Yenileme: Küçük boyutlu tablolar
   - Artımlı: Büyük olgu tabloları
   - CDC: Gerçek zamanlı gereksinimler

### Performans Ayarlaması

1. **Airbyte Sync Planlamasını Optimize Edin**
   ```yaml
   # Équilibrer fraîcheur vs utilisation ressources
   small_tables:
     frequency: every_15_minutes
   
   large_tables:
     frequency: every_6_hours
   
   dimension_tables:
     frequency: daily
   ```

2. **Stratejik Düşünceler Oluşturun**
   ```sql
   -- Focus sur agrégations fréquemment requêtées
   CREATE REFLECTION common_metrics
   ON gold.orders
   USING DIMENSIONS (product_id, date_trunc('day', order_date))
   MEASURES (SUM(amount), COUNT(*));
   ```

3. **dbt Modellerini Optimize Edin**
   ```yaml
   # models/schema.yml
   models:
     - name: fct_large_table
       config:
         materialized: incremental
         incremental_strategy: merge
         unique_key: id
         partition_by: {field: date, data_type: date}
   ```

### Yaygın Sorun Çözme

| Sorun | Belirti | Çözüm |
|-----------|-----------|----------|
| **Airbyte Senkronizasyonu Yavaş** | Senkronize edilecek zamanlar | Toplu iş boyutunu artırın, artımlı modu kullanın |
| **Hafıza Eksikliği** | Başarısız dbt modelleri | Aşamalı olarak hayata geçirin, bölümleme ekleyin |
| **Yavaş Sorgular** | Zaman aşımı kontrol paneli | Yansımalar oluşturun, dizin ekleyin |
| **Depolama Alanı Dolu** | Yazma hataları | Veri saklamayı uygulayın, eski verileri sıkıştırın |
| **Veriler Eski** | Eski metrikler | Senkronizasyon sıklığını artırın, programları kontrol edin |

### İyi Güvenlik Uygulamaları

1. **Aktarım Halindeki Verileri Şifreleyin**
   ```yaml
   # docker-compose.yml
   minio:
     environment:
       MINIO_SERVER_URL: https://minio:9000
       MINIO_BROWSER_REDIRECT_URL: https://console.minio.local
   ```

2. **Erişim Kontrollerini Uygulayın**
   ```sql
   -- ACLs Dremio
   GRANT SELECT ON gold.customer_metrics TO ROLE analyst;
   GRANT ALL ON bronze.* TO ROLE data_engineer;
   ```

3. **Veri Erişimini Denetleyin**
   ```json
   {
     "audit_log": {
       "enabled": true,
       "log_queries": true,
       "log_user_actions": true,
       "retention_days": 90
     }
   }
   ```

---

## Özet

Bu belgede tüm veri akışı mimarisinin ayrıntıları verilmektedir:

- **Besleme Katmanı**: Airbyte, tam yenileme, artımlı veya CDC yoluyla çeşitli kaynaklardan veri çıkarır
- **Depolama Katmanı**: MinIO, PostgreSQL ve Elasticsearch, ham ve işlenmiş verileri düzenli katmanlarda depolar
- **İşleme Katmanı**: Dremio verileri sanallaştırır ve dbt, hazırlama, ara ve mart modelleri aracılığıyla verileri dönüştürür
- **Sunum Katmanı**: Süper set kontrol panelleri ve API'ler, iş için hazır verilere erişim sağlar

Hatırlanması gereken önemli noktalar:
- Veriler açıkça tanımlanmış katmanlar aracılığıyla tek yönlü olarak akar
- Her bileşenin belirli sorumlulukları ve arayüzleri vardır
- Performans, yansımalar, bölümleme ve önbelleğe alma yoluyla optimize edilmiştir
- İzleme ve gözlemlenebilirlik her katmana entegre edilmiştir
- İyi uygulamalar güvenilirliği, performansı ve güvenliği garanti eder

**İlgili Belgeler:**
- [Mimariye Genel Bakış](./overview.md)
- [Bileşenler](./components.md)
- [Dağıtım](./deployment.md)
- [Airbyte Entegrasyon Kılavuzu](../guides/airbyte-integration.md)
- [dbt Geliştirme Kılavuzu](../guides/dbt-development.md)

---

**Sürüm**: 3.2.0  
**Son Güncelleme**: 16 Ekim 2025