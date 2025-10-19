# Apache Süper Kümesi Kontrol Panelleri Kılavuzu

**Sürüm**: 3.2.0  
**Son Güncelleme**: 16 Ekim 2025  
**Dil**: Fransızca

## İçindekiler

1. [Genel Bakış](#genel bakış)
2. [İlk Yapılandırma](#başlangıç-yapılandırma)
3. [Veri Kaynakları Bağlantısı](#veri-kaynakları-bağlantısı)
4. [Grafik Oluşturma](#grafik-oluşturma)
5. [Gösterge Paneli Yapımı](#gösterge paneli-yapımı)
6. [Gelişmiş Özellikler](#gelişmiş-özellikler)
7. [Güvenlik ve İzinler](#güvenlik-ve-izinler)
8. [Performans Optimizasyonu](#performans optimizasyonu)
9. [Entegrasyon ve Paylaşım](#entegrasyon ve paylaşım)
10. [İyi Uygulamalar](#iyi uygulamalar)

---

## Genel Bakış

Apache Superset, kullanıcıların sezgisel kontrol panelleri ve grafikler aracılığıyla verileri keşfetmesine ve görselleştirmesine olanak tanıyan, modern, kurumsal kullanıma hazır bir iş zekası web uygulamasıdır.

### Temel Özellikler

| Özellik | Açıklama | Kâr |
|----------------|---------|--------|
| **SQL IDE** | Otomatik tamamlama özelliğine sahip etkileşimli SQL düzenleyici | Özel analiz |
| **Zengin Görselleştirmeler** | 50'den fazla grafik türü | Çeşitli veri gösterimi |
| **Kontrol Paneli Oluşturucu** | Sürükle ve bırak arayüzü | Kolay kontrol paneli oluşturma |
| **Önbelleğe alma** | Önbellek sonuçları sorguları | Hızlı yükleme süreleri |
| **Güvenlik** | Satır düzeyinde güvenlik, rol tabanlı erişim | Veri yönetimi |
| **Uyarılar** | Otomatik e-posta/Slack bildirimleri | Proaktif izleme |

### Mimari Entegrasyon

```mermaid
graph LR
    A[Navigateur Utilisateur] --> B[Web Superset]
    B --> C[Base Données Superset<br/>PostgreSQL]
    B --> D{Sources Données}
    
    D --> E[Dremio<br/>Arrow Flight]
    D --> F[PostgreSQL]
    D --> G[Elasticsearch]
    
    E --> H[MinIO S3<br/>Data Lake]
    
    B --> I[Couche Cache<br/>Redis]
    
    style A fill:#e1f5ff
    style B fill:#20A7C9,color:#fff
    style C fill:#336791,color:#fff
    style E fill:#FDB515
    style H fill:#C72E49,color:#fff
    style I fill:#DC382D,color:#fff
```

---

## İlk Yapılandırma

### İlk Bağlantı

Superset'e `http://localhost:8088` adresinden erişin:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Güvenlik Notu**: İlk girişten hemen sonra varsayılan şifreyi değiştirin.

### İlk Kurulum

```bash
# Dans conteneur Superset
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@company.com \
  --password your_secure_password

# Initialiser base de données
superset db upgrade

# Charger données exemple (optionnel)
superset load_examples

# Initialiser rôles et permissions
superset init
```

### Yapılandırma Dosyası

```python
# superset_config.py

# Configuration Application Flask
SECRET_KEY = 'your-secret-key-here'  # Changer ceci!
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Configuration Base de Données
SQLALCHEMY_DATABASE_URI = 'postgresql://superset:superset@postgres:5432/superset'

# Configuration Cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
}

# Backend Résultats (pour requêtes async)
RESULTS_BACKEND = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_results_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 2,
}

# Drapeaux Fonctionnalités
FEATURE_FLAGS = {
    'ALERT_REPORTS': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_RBAC': True,
    'EMBEDDABLE_CHARTS': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
}

# Limite Ligne pour SQL Lab
SQL_MAX_ROW = 100000
SUPERSET_WEBSERVER_TIMEOUT = 60

# Activer requêtes async
SUPERSET_CELERY_WORKERS = 4
```

---

## Bağlantı Veri Kaynakları

### Dremio'ya giriş yapın

#### Adım 1: Dremio Veritabanı Sürücüsünü Kurun

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Adım 2: Dremio Veritabanını Ekleyin

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Yapılandırma**:
```json
{
  "database_name": "Dremio",
  "sqlalchemy_uri": "dremio+flight://admin:password@localhost:32010/datalake",
  "expose_in_sqllab": true,
  "allow_ctas": true,
  "allow_cvas": true,
  "allow_dml": false,
  "extra": {
    "engine_params": {
      "connect_args": {
        "use_encryption": false
      }
    },
    "metadata_params": {},
    "metadata_cache_timeout": 86400,
    "schemas_allowed_for_csv_upload": []
  }
}
```

#### 3. Adım: Bağlantıyı Test Edin

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### PostgreSQL'e bağlanma

```json
{
  "database_name": "PostgreSQL",
  "sqlalchemy_uri": "postgresql://postgres:postgres@postgres:5432/datawarehouse",
  "expose_in_sqllab": true,
  "allow_ctas": true,
  "allow_cvas": true,
  "extra": {
    "metadata_cache_timeout": 3600,
    "engine_params": {
      "pool_size": 10,
      "pool_recycle": 3600
    }
  }
}
```

### Elasticsearch'e bağlanma

```json
{
  "database_name": "Elasticsearch",
  "sqlalchemy_uri": "elasticsearch+http://elasticsearch:9200",
  "expose_in_sqllab": true,
  "allow_ctas": false,
  "allow_cvas": false,
  "extra": {
    "metadata_cache_timeout": 600
  }
}
```

---

## Grafik Oluşturma

### Grafik Oluşturma İş Akışı

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant Superset
    participant Database as Base Données
    participant Cache
    
    User->>Superset: Sélectionner dataset
    User->>Superset: Choisir type graphique
    User->>Superset: Configurer métriques & filtres
    Superset->>Cache: Vérifier cache
    
    alt Cache Hit
        Cache-->>Superset: Retourner données en cache
    else Cache Miss
        Superset->>Database: Exécuter requête
        Database-->>Superset: Retourner résultats
        Superset->>Cache: Stocker résultats
    end
    
    Superset->>User: Rendre visualisation
    User->>Superset: Sauvegarder graphique
```

### Seçim Grafiği Türü

| Grafik Türü | En İyisi | Kullanım Durumu Örneği |
|----------------|---------------|----------|
| **Doğrusal Grafik** | Zamansal eğilimler | Günlük gelir eğilimi |
| **Çubuk Grafiği** | Karşılaştırmalar | Ürün kategorisine göre gelir |
| **Sektör Tablosu** | Toplamın payı | Bölgelere göre pazar payı |
| **Tablo** | Detaylı veriler | Metrikleri içeren müşteri listesi |
| **Büyük Sayı** | Tek Metrik | Toplam YTD Geliri |
| **Isı Kartı** | Desen algılama | Günlük/saatlik satışlar |
| **Nokta Bulutu** | Korelasyonlar | Müşteri değeri ve sıklık |
| **Sankey Diyagramı** | Akış analizi | Kullanıcı yolculuğu |

### Örnek: Doğrusal Grafik (Gelir Trendi)

#### 1. Adım: Veri Kümesi Oluşturun

```
Interface → Données → Datasets → + Dataset
```

**Yapılandırma**:
- **Veritabanı**: Dremio
- **Diyagram**: Üretim.Martlar
- **Tablo**: mart_daily_revenue

#### Adım 2: Grafik Oluşturun

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Parametreler**:
```yaml
Dataset: mart_daily_revenue

Requête:
  Métriques:
    - SUM(total_revenue) AS "Revenu Total"
  Dimensions:
    - revenue_date
  Filtres:
    - revenue_date >= 2025-01-01
  Limite Lignes: 365

Personnaliser:
  Axe X: revenue_date
  Axe Y: Revenu Total
  Moyenne Mobile: 7 jours
  Afficher Points: Oui
  Style Ligne: Lisse
  Schéma Couleurs: Superset Par Défaut
```

**SQL Oluşturuldu**:
```sql
SELECT 
    revenue_date AS "Date",
    SUM(total_revenue) AS "Revenu Total"
FROM Production.Marts.mart_daily_revenue
WHERE revenue_date >= '2025-01-01'
GROUP BY revenue_date
ORDER BY revenue_date
LIMIT 365
```

### Örnek: Çubuk Grafik (En İyi Müşteriler)

```yaml
Type Graphique: Graphique Barres

Dataset: mart_customer_lifetime_value

Requête:
  Métriques:
    - lifetime_value AS "Valeur Vie"
  Dimensions:
    - full_name AS "Client"
  Filtres:
    - customer_status = 'Active'
  Trier Par: lifetime_value DESC
  Limite Lignes: 10

Personnaliser:
  Orientation: Horizontale
  Afficher Valeurs: Oui
  Couleur: Par Métrique
  Largeur Barre: 0.8
```

### Örnek: Özet Tablo

```yaml
Type Graphique: Tableau Croisé Dynamique

Dataset: fct_orders

Requête:
  Métriques:
    - SUM(total_amount) AS "Revenu"
    - COUNT(*) AS "Nombre Commandes"
    - AVG(total_amount) AS "Valeur Commande Moy"
  
  Lignes:
    - DATE_TRUNC('month', order_date) AS "Mois"
  
  Colonnes:
    - customer_segment
  
  Filtres:
    - order_date >= 2025-01-01
    - status = 'COMPLETED'

Personnaliser:
  Afficher Totaux: Ligne & Colonne
  Formatage Conditionnel:
    Revenu > 100000: Vert
    Revenu < 50000: Rouge
```

### Örnek: Trendli Büyük Sayı

```yaml
Type Graphique: Grand Nombre avec Ligne Tendance

Dataset: mart_daily_revenue

Requête:
  Métrique: SUM(total_revenue)
  Colonne Temps: revenue_date
  Plage Temps: 30 derniers jours
  Comparer À: Période Précédente

Personnaliser:
  Format Nombre: $,.2f
  Afficher Tendance: Oui
  Calcul Tendance: Semaine sur Semaine
  Couleur Positive: Vert
  Couleur Négative: Rouge
```

---

## İnşaat Kontrol Panelleri

### Kontrol Paneli Oluşturma Süreci

```mermaid
flowchart TB
    A[Créer Tableau de Bord] --> B[Ajouter Graphiques]
    B --> C[Arranger Disposition]
    C --> D[Ajouter Filtres]
    D --> E[Configurer Interactions]
    E --> F[Définir Planning Rafraîchissement]
    F --> G[Publier Tableau de Bord]
    
    style A fill:#20A7C9,color:#fff
    style G fill:#4CAF50,color:#fff
```

### Adım 1: Kontrol Paneli Oluşturun

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Kontrol Paneli Ayarları**:
```yaml
Titre: Tableau de Bord Analytique Clients
Propriétaires: [analytics_team]
Schéma Couleurs: Superset Par Défaut
Métadonnées JSON:
  refresh_frequency: 300  # 5 minutes
  timed_refresh_immune_slices: []
  expanded_slices: {}
  filter_scopes: {}
  default_filters: "{}"
  color_scheme: ""
```

### Adım 2: Grafik Ekle

Grafikleri sol panelden sürükleyip bırakın veya yenilerini oluşturun:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Adım 3: Tasarım Düzeni

**Izgara Sistemi**:
- 12 sütun genişliğinde
- Grafikler ızgaraya yapışır
- Yeniden boyutlandırmak ve yeniden konumlandırmak için kaydırın

**Örnek Düzen**:
```
┌────────────────────────────────────────────────────┐
│  Grand Nombre: Revenu Total  │  Grand Nombre: Cmd  │
│         (6 colonnes)          │      (6 colonnes)   │
├─────────────────────────────┴──────────────────────┤
│       Graphique Linéaire: Tendance Revenu Quotidien│
│                  (12 colonnes)                      │
├───────────────────────┬────────────────────────────┤
│  Top 10 Clients       │  Revenu par Segment        │
│  (Graphique Barres)   │  (Graphique Secteurs)      │
│  (6 colonnes)         │  (6 colonnes)              │
├───────────────────────┴────────────────────────────┤
│      Tableau Croisé: Revenu par Mois/Segment       │
│                  (12 colonnes)                      │
└────────────────────────────────────────────────────┘
```

### Adım 4: Kontrol Paneli Filtreleri Ekleyin

```
Tableau de Bord → Éditer → + Filtre
```

**Tarih Aralığı Filtresi**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Kategori Filtresi**:
```yaml
Type Filtre: Sélection
Cible: customer_segment
Colonnes:
  - fct_orders.customer_segment
  - mart_customer_lifetime_value.customer_segment
Valeurs: [New Customer, Regular Customer, Long-term Customer]
Par Défaut: Tous
Sélection Multiple: Oui
Recherche Activée: Oui
```

**Dijital Filtre**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Adım 5: Çapraz Filtreleme

Kontrol paneli çapraz filtrelemeyi etkinleştirin:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Yapılandırma**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Kullanıcı Deneyimi**:
- Çubuğa tıklayın → tüm kontrol panelini filtreleyin
- Sektör paylaşımına tıklayın → ilgili grafikleri güncelleyin
- Filtreyi temizle → varsayılan görünüme sıfırlanır

---

## Gelişmiş Özellikler

### SQL Laboratuvarı

Geçici sorgular için etkileşimli SQL düzenleyici.

#### Sorguyu Yürüt

```sql
-- Exemple requête SQL Lab
SELECT 
    c.customer_tier,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    SUM(o.total_amount) AS total_revenue,
    AVG(o.total_amount) AS avg_order_value,
    ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM Production.Dimensions.dim_customers c
INNER JOIN Production.Facts.fct_orders o
    ON c.customer_id = o.customer_id
WHERE o.status = 'COMPLETED'
  AND o.order_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY c.customer_tier
ORDER BY total_revenue DESC;
```

**Özellikler**:
- Tablolar ve sütunlar için otomatik tamamlama
- Talep geçmişi
- Çoklu sekmeler
- Sonuçları dışa aktarın (CSV, JSON)
- Sorguyu yeniden kullanmak üzere kaydet

#### Sorgudan Tablo Oluştur (CTAS)

```sql
-- Créer table temporaire
CREATE TABLE temp_customer_summary AS
SELECT 
    customer_id,
    full_name,
    lifetime_value,
    customer_tier
FROM Production.Dimensions.dim_customers
WHERE lifetime_value > 1000;

-- Interroger nouvelle table
SELECT * FROM temp_customer_summary;
```

### Jinja Şablonları

Jinja2 şablonlarıyla dinamik SQL:

```sql
-- Filtre avec template Jinja
SELECT 
    order_date,
    SUM(total_amount) AS revenue
FROM Production.Facts.fct_orders
WHERE order_date >= '{{ from_dttm }}'
  AND order_date < '{{ to_dttm }}'
{% if filter_values('customer_segment')|length > 0 %}
  AND customer_segment IN ({{ "'" + "','".join(filter_values('customer_segment')) + "'" }})
{% endif %}
GROUP BY order_date
ORDER BY order_date;
```

**Şablon Değişkenleri**:
- `{{ from_dttm }}` - Başlangıç ​​tarihi aralığı
- `{{ to_dttm }}` - Tarih aralığının sonu
- `{{ filter_values('column') }}` - Seçilen filtre değerleri
- `{{ current_username }}` - Kullanıcı oturum açtı

### Uyarılar ve Raporlar

#### Uyarı Oluştur

```
Interface → Alertes & Rapports → + Alerte
```

**Yapılandırma**:
```yaml
Nom: Alerte Revenu Quotidien
Type: Alerte
Base de Données: Dremio
SQL:
  SELECT SUM(total_revenue) AS daily_revenue
  FROM Production.Marts.mart_daily_revenue
  WHERE revenue_date = CURRENT_DATE

Condition:
  - daily_revenue < 50000  # Alerter si revenu sous seuil

Planning:
  Type: Cron
  Expression: "0 18 * * *"  # 18h quotidien

Destinataires:
  - email: finance@company.com
  - slack: #revenue-alerts

Message:
  Sujet: "Alerte Revenu Faible"
  Corps: "Revenu quotidien est {{ daily_revenue | currency }}, sous seuil de 50 000$"
```

#### Rapor Oluştur

```yaml
Nom: Rapport Client Hebdomadaire
Type: Rapport
Tableau de Bord: Tableau de Bord Analytique Clients

Planning:
  Type: Cron
  Expression: "0 9 * * 1"  # Lundi 9h

Format: PDF
Destinataires:
  - email: executives@company.com

Contenu:
  Inclure: Tous graphiques
  Filtres:
    date_range: 7 derniers jours
```

### Özel Görselleştirme Eklentileri

Özel grafik türleri oluşturun:

```javascript
// src/MyCustomChart/MyCustomChart.tsx
import React from 'react';
import { SupersetPluginChartProps } from '@superset-ui/core';

export default function MyCustomChart(props: SupersetPluginChartProps) {
  const { data, height, width } = props;
  
  return (
    <div style={{ height, width }}>
      <h2>Graphique Personnalisé</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
```

Oluşturun ve yükleyin:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Güvenlik ve İzinler

### Rol Tabanlı Erişim Kontrolü (RBAC)

```mermaid
graph TB
    subgraph "Utilisateurs"
        U1[Utilisateur Admin]
        U2[Utilisateur Analyste]
        U3[Utilisateur Viewer]
    end
    
    subgraph "Rôles"
        R1[Admin]
        R2[Alpha]
        R3[Gamma]
    end
    
    subgraph "Permissions"
        P1[Accès Toutes Bases]
        P2[Accès Tous Tableaux de Bord]
        P3[Peut Éditer]
        P4[Peut Explorer]
        P5[Peut Voir]
    end
    
    U1 --> R1
    U2 --> R2
    U3 --> R3
    
    R1 --> P1 & P2 & P3
    R2 --> P2 & P3 & P4
    R3 --> P2 & P5
    
    style R1 fill:#FF6B6B
    style R2 fill:#4ECDC4
    style R3 fill:#95E1D3
```

### Entegre Roller

| Rol | İzinler | Kullanım Durumları |
|------|-------------|------------|
| **Yönetici** | Tüm izinler | Sistem yöneticileri |
| **Alfa** | Kontrol panelleri/grafikler oluşturun, düzenleyin, silin | Veri analistleri |
| **Gama** | Kontrol panellerini görüntüleyin, SQL Lab sorgularını çalıştırın | Ticari kullanıcılar |
| **sql_lab** | Yalnızca SQL Laboratuvarı erişimi | Veri bilimcileri |
| **Herkese açık** | Yalnızca genel kontrol panellerini görüntüleyin | İsimsiz kullanıcılar |

### Özel Rol Oluştur

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Örnek: Pazarlama Analisti Rolü**
```yaml
Nom: Analyste Marketing
Permissions:
  - can read on Dashboard
  - can write on Dashboard
  - can read on Chart
  - can write on Chart
  - database access on [Dremio]
  - schema access on [Production.Marts]
  - datasource access on [mart_customer_lifetime_value, mart_marketing_attribution]
```

### Hat Seviyesinde Güvenlik (RLS)

Verileri kullanıcı özelliklerine göre kısıtlayın:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Örnek: Bölge Bazlı RLS**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Örnek: İstemci Tabanlı RLS**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Veritabanı Bağlantı Güvenliği

```python
# superset_config.py

# Chiffrer mots de passe connexion
SQLALCHEMY_DATABASE_URI = 'postgresql://user:encrypted_password@host/db'

# Utiliser variables environnement
import os
SQLALCHEMY_DATABASE_URI = os.environ.get('SUPERSET_DATABASE_URI')

# SSL pour connexions base de données
DATABASE_EXTRA_PARAMS = {
    'sslmode': 'require',
    'sslrootcert': '/path/to/ca-cert.pem'
}
```

---

## Performans Optimizasyonu

### Sorguları Önbelleğe Alma

```python
# superset_config.py

# Mettre en cache résultats requêtes pour 1 heure
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 heure
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
}

# Mettre en cache état filtre tableau de bord
FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 heures
}
```

**Önbellek Stratejisi**:
```mermaid
flowchart LR
    A[Requête Utilisateur] --> B{Vérif Cache}
    B -->|Hit| C[Retourner Données Cache<br/><100ms]
    B -->|Miss| D[Exécuter Requête]
    D --> E[Mettre en Cache Résultat]
    E --> F[Retourner Données Fraîches<br/>1-10s]
    
    style C fill:#4CAF50,color:#fff
    style F fill:#FFA500
```

### Eşzamansız İstekler

Uzun sorgular için eşzamansız sorgu yürütmeyi etkinleştirin:

```python
# superset_config.py

# Activer requêtes async
FEATURE_FLAGS = {
    'GLOBAL_ASYNC_QUERIES': True,
}

# Configurer workers Celery
from celery.schedules import crontab

class CeleryConfig:
    broker_url = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        'cache-warmup': {
            'task': 'cache-warmup',
            'schedule': crontab(minute=0, hour='*'),
        },
    }

CELERY_CONFIG = CeleryConfig
```

### Veritabanı Sorgu Optimizasyonu

```sql
-- Mauvais: Scan table complète
SELECT * FROM fct_orders
WHERE order_date >= '2025-01-01';

-- Bon: Utiliser partitionnement et élagage colonnes
SELECT 
    order_id,
    customer_id,
    total_amount
FROM fct_orders
WHERE order_date >= '2025-01-01'  -- Élagage partition
  AND status = 'COMPLETED';        -- Utilisation index
```

### Kontrol Paneli Yükleme Optimizasyonu

```yaml
# Paramètres optimisation tableau de bord
Mise en Cache:
  Timeout Cache: 3600  # 1 heure
  
Requêtes:
  Limite Lignes: 10000  # Limiter taille résultat
  Forcer Async: true  # Exécuter en arrière-plan
  
Rendu:
  Chargement Paresseux: true  # Charger graphiques au scroll
  Rendu Progressif: true
```

### Performans İzleme

```sql
-- Surveillance performance requêtes
SELECT 
    user_id,
    database_name,
    sql,
    start_time,
    end_time,
    DATEDIFF('second', start_time, end_time) AS duration_seconds,
    rows_returned
FROM query_history
WHERE start_time >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY duration_seconds DESC
LIMIT 20;
```

---

## Entegrasyon ve Paylaşım

### Genel Kontrol Panelleri

Kontrol panellerini bağlantı olmadan erişilebilir hale getirin:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**Genel URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Iframe entegrasyonu

Kontrol panellerini harici uygulamalara entegre edin:

```html
<!-- Intégrer tableau de bord Superset -->
<iframe 
  src="https://superset.company.com/dashboard/1/?standalone=1"
  width="100%" 
  height="800"
  frameborder="0"
  allowfullscreen
></iframe>
```

**Entegrasyon Ayarları**:
- `standalone=1` - Gezinmeyi gizle
- `show_filters=0` - Filtre panelini gizle
- `show_title=0` - Kontrol paneli başlığını gizle

### Konuk Belirteci Kimlik Doğrulaması

Entegre kontrol panelleri için programlı erişim:

```python
# Générer jeton invité
import requests
import json

url = 'https://superset.company.com/api/v1/security/guest_token/'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

payload = {
    "user": {
        "username": "guest_user",
        "first_name": "Guest",
        "last_name": "User"
    },
    "resources": [{
        "type": "dashboard",
        "id": "dashboard-id"
    }],
    "rls": [{
        "clause": "region = 'US-West'"
    }]
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
guest_token = response.json()['token']

# Utiliser jeton invité dans URL intégration
embed_url = f"https://superset.company.com/dashboard/1/?guest_token={guest_token}"
```

### Kontrol Panellerini Dışa Aktarma

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## En İyi Uygulamalar

### Kontrol Paneli Tasarımı

1. **Yerleşim Hiyerarşisi**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Renk Tutarlılığı**
   - Tüm kontrol panellerinde tutarlı renk şeması kullanın
   - Pozitif ölçümler için yeşil, negatif ölçümler için kırmızı
   - Kategoriler için marka renkleri

3. **Performans**
   - Kontrol paneli başına grafikleri sınırlayın (< 15)
   - Uygun toplama seviyelerini kullanın
   - Statik veriler için önbelleği etkinleştirin
   - Makul hat limitleri belirleyin

4. **Etkileşim**
   - Anlamlı filtreler ekleyin
   - Keşif için çapraz filtrelemeyi etkinleştirin
   - Detaya inme yetenekleri sağlayın

### Grafik Seçimi

| Veri Türü | Önerilen Grafikler | Kaçının |
|----------------|-----------------|-----------|
| **Zaman Serisi** | Doğrusal, Alanlar | Sektörler, Halka |
| **Karşılaştırma** | Barlar, Sütunlar | Doğrusal (birkaç veri noktası) |
| **Toplamın Payı** | Sektörler, Halka, Ağaç Haritası | Barlar (ayrıca kategoriler) |
| **Dağıtım** | Histogram, Kutu Grafiği | Sektörler |
| **Korelasyon** | Bulut Noktaları, Kabarcıklar | Barlar |
| **Coğrafi** | Harita, Choropleth | Tablo |

### Sorgu Optimizasyonu

```sql
-- Utiliser agrégation dans base de données, pas dans Superset
SELECT 
    DATE_TRUNC('day', order_date) AS day,
    SUM(total_amount) AS revenue
FROM fct_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '90' DAY
GROUP BY DATE_TRUNC('day', order_date);

-- Mieux que:
-- SELECT order_date, total_amount FROM fct_orders;
-- (puis agréger dans Superset)
```

### Güvenlik

1. **Erişim Kontrolü**
   - Kullanıcı yönetimi için RBAC kullanın
   - Veri izolasyonu için RLS'yi uygulayın
   - Veritabanı bağlantılarını role göre kısıtla

2. **Veri Yönetişimi**
   - Belge veri kümeleri özelliği
   - Veri yenileme programlarını tanımlayın
   - Sorgu performansını izleyin

3. **Uyumluluk**
   - Görselleştirmelerde PII'yi gizle
   - Kontrol panosu erişimini denetleyin
   - Veri saklama politikalarını uygulayın

---

## Özet

Bu kapsamlı Süperset kılavuzu şunları kapsamaktadır:

- **Yapılandırma**: Kurulum, yapılandırma, veritabanı bağlantıları
- **Grafikler**: 50'den fazla grafik türü, konfigürasyon, SQL oluşturma
- **Kontrol Panelleri**: Düzen tasarımı, filtreler, çapraz filtreleme
- **Gelişmiş Özellikler**: SQL Lab, Jinja şablonları, uyarılar, özel eklentiler
- **Güvenlik**: RBAC, RLS, veritabanı bağlantı güvenliği
- **Performans**: Önbelleğe alma, eşzamansız sorgular, sorgu optimizasyonu
- **Entegrasyon**: Genel kontrol panelleri, iframe entegrasyonu, misafir belirteçleri
- **İyi Uygulamalar**: Tasarım ilkeleri, grafik seçimi, güvenlik

Hatırlanması gereken önemli noktalar:
- Superset, yüksek performanslı analizler için Dremio'ya bağlanır
- Zengin görselleştirme kitaplığı çeşitli kullanım durumlarını destekler
- Yerleşik önbelleğe alma ve eşzamansız sorgular hızlı kontrol panelleri sağlar
- RBAC ve RLS, güvenli self-servis analitiği mümkün kılar
- Entegrasyon yetenekleri harici uygulamalarla entegrasyonu mümkün kılar

**İlgili Belgeler:**
- [Dremio Kurulum Kılavuzu](./dremio-setup.md)
- [Mimarlık: Veri Akışı](../architecture/data-flow.md)
- [İlk Adımlar Eğitimi](../getting-started/first-steps.md)
- [Veri Kalitesi Kılavuzu](./data-quality.md)

---

**Sürüm**: 3.2.0  
**Son Güncelleme**: 16 Ekim 2025