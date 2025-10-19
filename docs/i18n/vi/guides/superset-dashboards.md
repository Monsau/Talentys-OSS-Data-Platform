# Hướng dẫn về bảng điều khiển Superset của Apache

**Phiên bản**: 3.2.0  
**Cập nhật lần cuối**: Ngày 16 tháng 10 năm 2025  
**Ngôn ngữ**: Tiếng Pháp

## Mục lục

1. [Tổng quan](#tổng quan)
2. [Cấu hình ban đầu](#cấu hình ban đầu)
3. [Kết nối nguồn dữ liệu](#data-sources-connection)
4. [Sáng tạo đồ họa](#graphics-creation)
5. [Xây dựng bảng điều khiển](#xây dựng bảng điều khiển)
6. [Tính năng nâng cao](#advanced-features)
7. [Bảo mật và quyền](#security-and-permissions)
8. [Tối ưu hóa hiệu suất](#performance-optimization)
9. [Tích hợp và chia sẻ](#tích hợp và chia sẻ)
10. [Các phương pháp hay](#good-practice)

---

## Tổng quan

Apache Superset là một ứng dụng web thông minh kinh doanh hiện đại, sẵn sàng cho doanh nghiệp, cho phép người dùng khám phá và trực quan hóa dữ liệu thông qua các bảng điều khiển và biểu đồ trực quan.

### Các tính năng chính

| Tính năng | Mô tả | Lợi nhuận |
|-------|----------|---------|
| **IDE SQL** | Trình soạn thảo SQL tương tác có tính năng tự động hoàn thành | Phân tích đặc biệt |
| **Hình ảnh phong phú** | Hơn 50 loại biểu đồ | Trình bày dữ liệu khác nhau |
| **Trình tạo bảng điều khiển** | Giao diện kéo và thả | Tạo bảng điều khiển dễ dàng |
| **Bộ nhớ đệm** | Truy vấn kết quả bộ nhớ đệm | Thời gian tải nhanh |
| **An ninh** | Bảo mật cấp hàng, truy cập dựa trên vai trò | Quản trị dữ liệu |
| **Cảnh báo** | Email tự động/Thông báo chậm | Giám sát chủ động |

### Tích hợp kiến ​​trúc

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

## Cấu hình ban đầu

### Kết nối đầu tiên

Truy cập Superset trên `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Lưu ý bảo mật**: Thay đổi mật khẩu mặc định ngay sau lần đăng nhập đầu tiên.

### Thiết lập ban đầu

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

### Tệp cấu hình

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

## Nguồn dữ liệu kết nối

### Đăng nhập vào Dremio

#### Bước 1: Cài đặt trình điều khiển cơ sở dữ liệu Dremio

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Bước 2: Thêm cơ sở dữ liệu Dremio

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Cấu hình**:
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

#### Bước 3: Kiểm tra kết nối

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Đang kết nối với PostgreSQL

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

### Kết nối với Elaticsearch

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

## Sáng tạo đồ họa

### Quy trình tạo đồ họa

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

### Loại đồ họa lựa chọn

| Loại đồ họa | Tốt nhất cho | Ví dụ về trường hợp sử dụng |
|-------|--------------||----------------------|
| **Biểu đồ tuyến tính** | Xu hướng thời gian | Xu hướng thu nhập hàng ngày |
| **Biểu đồ thanh** | So sánh | Doanh thu theo danh mục sản phẩm |
| **Biểu đồ ngành** | Chia sẻ tổng cộng | Thị phần theo khu vực |
| **Bảng** | Dữ liệu chi tiết | Danh sách khách hàng có số liệu |
| **Số Lớn** | Số liệu đơn | Tổng thu nhập từ đầu năm |
| **Thẻ nhiệt** | Phát hiện mẫu | Doanh thu mỗi ngày/giờ |
| **Đám mây điểm** | Tương quan | Giá trị khách hàng so với tần suất |
| **Sơ đồ Sankey** | Phân tích dòng chảy | Hành trình của người dùng |

### Ví dụ: Biểu đồ tuyến tính (Xu hướng thu nhập)

#### Bước 1: Tạo Dataset

```
Interface → Données → Datasets → + Dataset
```

**Cấu hình**:
- **Cơ sở dữ liệu**: Dremio
- **Sơ đồ**: Production.Marts
- **Bảng**: mart_daily_revenue

#### Bước 2: Tạo biểu đồ

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Thông số**:
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

**Đã tạo SQL**:
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

### Ví dụ: Biểu đồ thanh (Khách hàng hàng đầu)

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

### Ví dụ: PivotTable

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

### Ví dụ: Số lớn có Xu hướng

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

## Bảng điều khiển xây dựng

### Quy trình tạo bảng điều khiển

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

### Bước 1: Tạo Dashboard

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Cài đặt bảng điều khiển**:
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

### Bước 2: Thêm đồ họa

Kéo và thả đồ họa từ bảng điều khiển bên trái hoặc tạo đồ họa mới:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Bước 3: Thiết kế bố cục

**Hệ thống lưới**:
- rộng 12 cột
- Đồ họa gắn vào lưới
- Vuốt để thay đổi kích thước và định vị lại

**Bố cục mẫu**:
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

### Bước 4: Thêm bộ lọc bảng điều khiển

```
Tableau de Bord → Éditer → + Filtre
```

**Bộ lọc phạm vi ngày**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Bộ lọc danh mục**:
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

**Bộ lọc kỹ thuật số**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Bước 5: Lọc chéo

Bật tính năng lọc chéo trang tổng quan:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Cấu hình**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Trải nghiệm người dùng**:
- Click vào thanh → lọc toàn bộ bảng điều khiển
- Bấm vào chia sẻ ngành → cập nhật đồ họa liên quan
- Xóa bộ lọc → đặt lại về chế độ xem mặc định

---

## Tính năng nâng cao

### Phòng thí nghiệm SQL

Trình soạn thảo SQL tương tác cho các truy vấn đặc biệt.

#### Thực thi truy vấn

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

**Đặc trưng**:
- Tự động hoàn thiện bảng và cột
- Lịch sử yêu cầu
- Nhiều tab
- Xuất kết quả (CSV, JSON)
- Lưu truy vấn để sử dụng lại

#### Tạo bảng từ truy vấn (CTAS)

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

### Mẫu Jinja

SQL động với các mẫu Jinja2:

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

**Biến mẫu**:
- `{{ from_dttm }}` - Phạm vi ngày bắt đầu
- `{{ to_dttm }}` - Kết thúc phạm vi ngày
- `{{ filter_values('column') }}` - Giá trị bộ lọc đã chọn
- `{{ current_username }}` - Người dùng đã đăng nhập

### Cảnh báo và Báo cáo

####Tạo cảnh báo

```
Interface → Alertes & Rapports → + Alerte
```

**Cấu hình**:
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

####Tạo báo cáo

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

### Plugin trực quan hóa tùy chỉnh

Tạo các loại đồ họa tùy chỉnh:

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

Xây dựng và cài đặt:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Bảo mật và quyền

### Kiểm soát truy cập dựa trên vai trò (RBAC)

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

### Vai trò tích hợp

| Vai trò | Quyền | Trường hợp sử dụng |
|------|-------------|-------------|
| **Quản trị viên** | Tất cả các quyền | Quản trị viên hệ thống |
| **Alpha** | Tạo, chỉnh sửa, xóa bảng thông tin/biểu đồ | Nhà phân tích dữ liệu |
| **Gamma** | Xem bảng thông tin, chạy truy vấn SQL Lab | Người dùng doanh nghiệp |
| **sql_lab** | Chỉ truy cập SQL Lab | Nhà khoa học dữ liệu |
| **Công cộng** | Chỉ xem bảng điều khiển công khai | Người dùng ẩn danh |

### Tạo vai trò tùy chỉnh

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Ví dụ: Vai trò Nhà phân tích Tiếp thị**
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

### An toàn cấp độ đường dây (RLS)

Hạn chế dữ liệu theo thuộc tính người dùng:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Ví dụ: RLS dựa trên khu vực**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Ví dụ: RLS dựa trên máy khách**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Bảo mật kết nối cơ sở dữ liệu

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

## Tối ưu hóa hiệu suất

### Truy vấn bộ nhớ đệm

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

**Chiến lược bộ đệm**:
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

### Yêu cầu không đồng bộ

Bật thực thi truy vấn không đồng bộ cho các truy vấn dài:

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

### Tối ưu hóa truy vấn cơ sở dữ liệu

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

### Tối ưu hóa tải trang tổng quan

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

### Giám sát hiệu suất

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

## Tích hợp và chia sẻ

### Trang tổng quan công khai

Làm cho trang tổng quan có thể truy cập được mà không cần kết nối:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**URL công khai**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Tích hợp khung nội tuyến

Tích hợp bảng điều khiển vào các ứng dụng bên ngoài:

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

**Cài đặt tích hợp**:
- `standalone=1` - Ẩn điều hướng
- `show_filters=0` - Ẩn bảng lọc
- `show_title=0` - Ẩn tiêu đề trang tổng quan

### Xác thực mã thông báo khách

Quyền truy cập có lập trình cho bảng thông tin tích hợp:

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

### Xuất trang tổng quan

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Các phương pháp hay nhất

### Thiết kế bảng điều khiển

1. **Phân cấp bố cục**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Tính nhất quán về màu sắc**
   - Sử dụng bảng màu nhất quán trên tất cả các bảng điều khiển
   - Màu xanh lá cây cho số liệu dương, màu đỏ cho số liệu âm
   - Màu sắc thương hiệu cho các danh mục

3. **Hiệu suất**
   - Giới hạn đồ họa trên mỗi bảng điều khiển (<15)
   - Sử dụng mức độ tổng hợp thích hợp
   - Kích hoạt bộ đệm cho dữ liệu tĩnh
   - Đặt giới hạn dòng hợp lý

4. **Tương tác**
   - Thêm bộ lọc ý nghĩa
   - Kích hoạt tính năng lọc chéo để khám phá
   - Cung cấp khả năng truy sâu

### Lựa chọn đồ họa

| Kiểu dữ liệu | Biểu đồ được đề xuất | Tránh |
|--------------|------------------------------------------|--------|
| **Chuỗi thời gian** | Tuyến tính, Diện tích | Ngành, Vòng |
| **So sánh** | Thanh, Cột | Tuyến tính (vài điểm dữ liệu) |
| **Tỷ lệ trong tổng số** | Lĩnh vực, Vòng, Sơ đồ cây | Thanh (quá loại) |
| **Phân phối** | Biểu đồ, Sơ đồ hộp | Lĩnh vực |
| **Tương quan** | Điểm đám mây, bong bóng | Quán bar |
| **Địa lý** | Bản đồ, Choropleth | Bảng |

### Tối ưu hóa truy vấn

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

### Bảo vệ

1. **Kiểm soát truy cập**
   - Sử dụng RBAC để quản lý người dùng
   - Triển khai RLS để cách ly dữ liệu
   - Hạn chế kết nối cơ sở dữ liệu theo vai trò

2. **Quản trị dữ liệu**
   - Thuộc tính tập dữ liệu tài liệu
   - Xác định lịch làm mới dữ liệu
   - Giám sát hiệu suất truy vấn

3. **Tuân thủ**
   - Ẩn PII trong trực quan hóa
   - Kiểm tra quyền truy cập bảng điều khiển
   - Thực hiện chính sách lưu giữ dữ liệu

---

## Bản tóm tắt

Hướng dẫn Superset toàn diện này đã đề cập đến:

- **Cấu hình**: Cài đặt, cấu hình, kết nối cơ sở dữ liệu
- **Đồ họa**: Hơn 50 loại đồ họa, cấu hình, tạo SQL
- **Bảng điều khiển**: Thiết kế bố cục, bộ lọc, lọc chéo
- **Tính năng nâng cao**: SQL Lab, mẫu Jinja, cảnh báo, plugin tùy chỉnh
- **Bảo mật**: RBAC, RLS, bảo mật kết nối cơ sở dữ liệu
- **Hiệu suất**: Bộ nhớ đệm, truy vấn không đồng bộ, tối ưu hóa truy vấn
- **Tích hợp**: Bảng điều khiển công khai, tích hợp iframe, mã thông báo của khách
- **Các phương pháp thực hành tốt**: Nguyên tắc thiết kế, lựa chọn đồ họa, bảo mật

Những điểm chính cần nhớ:
- Superset kết nối với Dremio để phân tích hiệu suất cao
- Thư viện trực quan phong phú hỗ trợ nhiều trường hợp sử dụng khác nhau
- Bộ nhớ đệm tích hợp và truy vấn không đồng bộ đảm bảo bảng điều khiển nhanh
- RBAC và RLS cho phép phân tích tự phục vụ an toàn
- Khả năng tích hợp cho phép tích hợp với các ứng dụng bên ngoài

**Tài liệu liên quan:**
- [Hướng dẫn thiết lập Dremio](./dremio-setup.md)
- [Kiến trúc: Luồng dữ liệu](../architecture/data-flow.md)
- [Hướng dẫn các bước đầu tiên](../getting-started/first-steps.md)
- [Hướng dẫn chất lượng dữ liệu](./data-quality.md)

---

**Phiên bản**: 3.2.0  
**Cập nhật lần cuối**: Ngày 16 tháng 10 năm 2025