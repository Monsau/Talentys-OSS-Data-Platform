# Veri Platformuna Başlarken

**Sürüm**: 3.2.0  
**Son güncelleme**: 2025-10-16  
**Dil**: Fransızca

---

## Genel Bakış

Bu eğitim, hizmetlere bağlanmaktan Airbyte, Dremio, dbt ve Superset ile ilk veri hattınızı oluşturmaya kadar veri platformuyla ilk etkileşimlerinizde size yol gösterir.

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

**Tahmini süre**: 60-90 dakika

---

## Önkoşullar

Başlamadan önce aşağıdakilerden emin olun:

- ✅ Tüm hizmetler kurulu ve çalışıyor
- ✅ Web arayüzlerine erişebilirsiniz
- ✅ Python sanal ortamı etkinleştirildi
- ✅ Temel SQL anlayışı

**Hizmetlerin çalışıp çalışmadığını kontrol edin:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Adım 1: Tüm Hizmetlere Erişin

### Hizmet URL'leri

| Hizmetler | URL'si | Varsayılan Kimlik Bilgileri |
|-----------|----------|------------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / şifre |
| **Dremio** | http://localhost:9047 | yönetici/yönetici123 |
| **Süper set** | http://localhost:8088 | yönetici / yönetici |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### İlk Bağlantı

**Airbyte:**
1. http://localhost:8000'i açın
2. Kurulum sihirbazını tamamlayın
3. Çalışma alanı adını ayarlayın: “Üretim”
4. Tercihleri ​​geçersiz kıl (daha sonra yapılandırma mümkündür)

**Dremio:**
1. http://localhost:9047'yi açın
2. İlk erişimde bir yönetici kullanıcı oluşturun:
   - Kullanıcı adı: `admin`
   - E-posta: `admin@example.com`
   - Şifre: `admin123`
3. "Başlayın"a tıklayın

**Süper set:**
1. http://localhost:8088'i açın
2. Varsayılan kimlik bilgileriyle oturum açın
3. Şifreyi değiştirin: Ayarlar → Kullanıcı Bilgileri → Şifreyi Sıfırla

---

## Adım 2: Airbyte'da İlk Veri Kaynağınızı Yapılandırın

### PostgreSQL Kaynağı Oluşturun

**Senaryo**: PostgreSQL veritabanından veri çıkarın.

1. **Kaynaklara Gidin**
   - Soldaki menüden “Kaynaklar”a tıklayın
   - “+ Yeni kaynak”a tıklayın

2. **PostgreSQL'i seçin**
   - “PostgreSQL”i arayın
   - “PostgreSQL” bağlayıcısına tıklayın

3. **Bağlantıyı Yapılandırın**
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

4. **Test Et ve Kaydet**
   - “Kaynağı ayarla”ya tıklayın
   - Bağlantı testini bekleyin
   - Kaynak oluşturuldu ✅

### Örnek Veri Oluşturun (İsteğe bağlı)

Henüz veriniz yoksa örnek tablolar oluşturun:

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

## Adım 3: MinIO S3 Hedefini Yapılandırın

### Bir Hedef Oluşturun

1. **Hedeflere Gidin**
   - Soldaki menüden “Hedefler”e tıklayın
   - “+ Yeni hedef”e tıklayın

2. **S3'ü seçin**
   - “S3”ü arayın
   - “S3” konektörüne tıklayın

3. **MinIO'yu S3 olarak yapılandırın**
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

4. **Test Et ve Kaydet**
   - "Hedefi ayarla"ya tıklayın
   - Bağlantı testi geçmeli ✅

---

## Adım 4: İlk Bağlantınızı Oluşturun

### Kaynağı Hedefe Bağla

1. **Bağlantılar'a gidin**
   - Soldaki menüden “Bağlantılar”a tıklayın
   - “+ Yeni bağlantı”ya tıklayın

2. **Kaynak Seçin**
   - “PostgreSQL Üretimi”ni seçin
   - “Mevcut kaynağı kullan”a tıklayın

3. **Hedef Seçin**
   - “MinIO Data Lake”i seçin
   - “Mevcut hedefi kullan”a tıklayın

4. **Senkronizasyonu Yapılandırın**
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

5. **Normalleşme**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Yedekle ve Senkronize Et**
   - “Bağlantı kur”a tıklayın
   - İlk senkronizasyonu gerçekleştirmek için "Şimdi senkronize et"e tıklayın
   - Senkronizasyon ilerlemesini izleyin

### Monitör Senkronizasyonu

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

**Senkronizasyon durumunu kontrol edin:**
- Durum "Başarılı" (yeşil) olarak görünmelidir
- Senkronize kayıtlar: ~11 (5 müşteri + 6 sipariş)
- Ayrıntılar için günlüklere bakın

---

## Adım 5: Dremio'yu MinIO'ya bağlayın

### Dremio'ya bir S3 Kaynağı ekleyin

1. **Kaynaklara Gidin**
   - http://localhost:9047'yi açın
   - “Kaynak Ekle”ye tıklayın (+ simgesi)

2. **S3'ü seçin**
   - “Amazon S3”ü seçin
   - MinIO olarak yapılandırın:

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

3. **Test Et ve Kaydet**
   - “Kaydet”e tıklayın
   - Dremio, MinIO kovalarını analiz edecek

### Verilere Göz Atın

1. **MiniOLake kaynağına gidin**
   - “MinIOLake”i geliştirin
   - "Datalake" paketini geliştirin
   - "ham veri" klasörünü genişletin
   - "prodüksiyon_public" klasörüne bakın

2. **Verileri Önizleyin**
   - “Müşteriler” klasörüne tıklayın
   - Parke dosyasına tıklayın
   - Verileri görmek için “Önizleme”ye tıklayın
   - Veriler PostgreSQL ile eşleşmelidir ✅

### Sanal Veri Kümesi Oluşturun

1. **Verileri Sorgula**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **VDS olarak kaydet**
   - “Görünümü Farklı Kaydet”e tıklayın
   - İsim: `vw_customers`
   - Boşluk: `@admin` (alanınız)
   - “Kaydet”e tıklayın

3. **Verileri Biçimlendir** (isteğe bağlı)
   - `vw_customers` seçeneğine tıklayın
   - Sütunları yeniden adlandırmak, türleri değiştirmek için arayüzü kullanın
   - Örnek: `customer_id` öğesini `id` olarak yeniden adlandırın

---

## Adım 6: dbt Şablonları oluşturun

### dbt Projesini başlat

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

### Kaynak Tanımı Oluştur

**Dosya**: `dbt/models/sources.yml`

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

### Hazırlama Şablonu Oluşturun

**Dosya**: `dbt/models/staging/stg_customers.sql`

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

**Dosya**: `dbt/models/staging/stg_orders.sql`

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

### Bir Mart Şablonu Oluşturun

**Dosya**: `dbt/models/marts/fct_customer_orders.sql`

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

### dbt Modellerini Çalıştır

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

### Dremio'yu kontrol edin

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Adım 7: Superset'te Kontrol Paneli Oluşturun

### Dremio Veritabanını Ekle

1. **Veritabanlarına Gidin**
   - http://localhost:8088'i açın
   - “Veri” → “Veritabanları”na tıklayın
   - “+ Veritabanı”na tıklayın

2. **Dremio'yu seçin**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **“Bağlan”a tıklayın**

### Veri Kümesi Oluşturun

1. **Veri Kümeleri'ne gidin**
   - “Veri” → “Veri Kümeleri”ne tıklayın
   - “+ Veri Kümesi”ne tıklayın

2. **Veri Kümesini Yapılandırın**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **"Veri Kümesi Oluştur ve Grafik Oluştur"a tıklayın**

### Grafikler Oluşturun

#### Grafik 1: Müşteri Segmentleri (Dairesel Diyagram)

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

#### Grafik 2: Ülkelere Göre Gelirler (Çubuk Grafik)

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

#### Grafik 3: Müşteri Metrikleri (Büyük Sayı)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Kontrol Panelini Oluşturun

1. **Kontrol Panellerine gidin**
   - “Kontrol Panelleri”ne tıklayın
   - “+ Kontrol Paneli”ne tıklayın

2. **Kontrol Panelini Yapılandırın**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Grafik Ekle**
   - Oluşturulan grafikleri sürükleyip bırakın
   - Bir ızgarada düzenleyin:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Filtre Ekle** (isteğe bağlı)
   - "Filtre Ekle"ye tıklayın
   - Şuna göre filtrele: ülke_kodu
   - Tüm grafiklere uygula

5. **Kontrol Panelini Kaydet**

---

## Adım 8: Tüm Boru Hattını Kontrol Edin

### Uçtan Uca Test

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

### Yeni Veri Ekle

1. **PostgreSQL'e yeni kayıtlar ekleyin**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Airbyte senkronizasyonunu tetikleyin**
   - Airbyte arayüzünü açın
   - "PostgreSQL → MinIO" bağlantısına gidin
   - “Şimdi senkronize et”e tıklayın
   - Sonunu bekle ✅

3. **dbt'yi çalıştırın**
   ```bash
   cd dbt
   dbt run
   ```

4. **Süperset Kontrol Panelini yenileyin**
   - Kontrol panelini açın
   - “Yenile” butonuna tıklayın
   - Yeni veriler görünmeli ✅

### Veri Akışını Kontrol Edin

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

## Adım 9: İşlem Hattını Otomatikleştirin

### Airbyte Senkronizasyonunu Programla

Zaten 24 saatte bir saat 02:00'de çalışacak şekilde yapılandırılmıştır.

Düzenlemek için:
1. Bağlantıyı Airbyte'da açın
2. "Ayarlar" sekmesine gidin
3. “Çoğaltma sıklığı”nı güncelleyin
4. Kaydet

### Dbt Yürütmelerini planlayın

**Seçenek 1: Cron İşi (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Seçenek 2: Python Komut Dosyası**

**Dosya**: `scripts/run_pipeline.py`
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

### Docker Compose ile planlama

**Dosya**: `docker-compose.scheduler.yml`
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

## Sonraki Adımlar

Tebrikler! Eksiksiz bir uçtan uca veri hattı oluşturdunuz. 🎉

### Daha fazla bilgi edin

1. **Airbyte Advanced** - [Airbyte Entegrasyon Kılavuzu](../guides/airbyte-integration.md)
2. **Dremio Optimizasyonu** - [Dremio Kurulum Kılavuzu](../guides/dremio-setup.md)
3. **Karmaşık dbt Modelleri** - [dbt Geliştirme Kılavuzu](../guides/dbt-development.md)
4. **Gelişmiş Kontrol Panelleri** - [Süper Set Kontrol Panelleri Kılavuzu](../guides/superset-dashboards.md)
5. **Veri Kalitesi** - [Veri Kalitesi Kılavuzu](../guides/data-quality.md)

### Sorun giderme

Sorun yaşıyorsanız şuraya bakın:
- [Sorun Giderme Kılavuzu](../guides/troubleshooting.md)
- [Kurulum Kılavuzu](installation.md#troubleshooting)
- [Yapılandırma Kılavuzu](configuration.md)

---

## Özet

Başarıyla:

- ✅ Platformun 7 hizmetine erişin
- ✅ Bir Airbyte kaynağı yapılandırın (PostgreSQL)
- ✅ Bir Airbyte hedefi yapılandırın (MinIO S3)
- ✅ İlk Airbyte bağlantınızı oluşturun
- ✅ Dremio'yu MinIO'ya bağlayın
- ✅ Dbt şablonları oluşturun (hazırlama + martlar)
- ✅ Bir Süperset Kontrol Paneli oluşturun
- ✅ Uçtan uca veri akışını kontrol edin
- ✅ Boru hattının yürütülmesini otomatikleştirin

**Veri platformunuz artık çalışır durumda!** 🚀

---

**İlk Adım Kılavuzu Versiyonu**: 3.2.0  
**Son Güncelleme**: 2025-10-16  
**Bakımını Yapan**: Veri Platformu Ekibi