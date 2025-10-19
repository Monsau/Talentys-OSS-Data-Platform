# Apache スーパーセット ダッシュボード ガイド

**バージョン**: 3.2.0  
**最終更新**: 2025 年 10 月 16 日  
**言語**: フランス語

＃＃ 目次

1. [概要](#overview)
2. [初期設定](#initial-configuration)
3. [データソース接続](#data-sources-connection)
4. [グラフィック作成](#graphics-creation)
5. [ダッシュボード構築](#dashboard-construction)
6. [高度な機能](#advanced-features)
7. [セキュリティと権限](#security-and-permissions)
8. [パフォーマンスの最適化](#performance-optimization)
9. [統合と共有](#integration-and-sharing)
10. [グッドプラクティス](#good-practices)

---

＃＃ 概要

Apache Superset は、ユーザーが直感的なダッシュボードとグラフを通じてデータを探索および視覚化できるようにする、最新のエンタープライズ対応ビジネス インテリジェンス Web アプリケーションです。

### 主な機能

|特集 |説明 |利益 |
|-----|----------|----------|
| **SQL IDE** |オートコンプリート機能を備えた対話型 SQL エディタ |アドホック分析 |
| **豊富なビジュアライゼーション** | 50 以上のチャート タイプ |さまざまなデータ表現 |
| **ダッシュボード ビルダー** |ドラッグ アンド ドロップ インターフェイス |簡単なダッシュボード作成 |
| **キャッシング** |結果のクエリをキャッシュする |読み込み時間が速い |
| **セキュリティ** |行レベルのセキュリティ、ロールベースのアクセス |データガバナンス |
| **アラート** |自動メール/Slack 通知 |プロアクティブなモニタリング |

### アーキテクチャの統合

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

## 初期設定

### 最初の接続

`http://localhost:8088` のスーパーセットにアクセスします。

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**セキュリティ上の注意**: 最初のログイン後、すぐにデフォルトのパスワードを変更してください。

### 初期セットアップ

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

### 設定ファイル

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

## 接続データソース

### Dremio にログイン

#### ステップ 1: Dremio データベースドライバーをインストールする

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### ステップ 2: Dremio データベースを追加する

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**構成**：
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

#### ステップ 3: 接続のテスト

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### PostgreSQL への接続

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

### Elasticsearch への接続

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

## グラフィックの作成

### グラフィック作成ワークフロー

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

### 選択グラフィックタイプ

|グラフィックタイプ |最適な用途 |使用例 |
|-||--|-------|
| **線形グラフ** |一時的な傾向 |日当収入推移 |
| **棒グラフ** |比較 |製品カテゴリー別の収益 |
| **セクター チャート** |全体のシェア |地域別の市場シェア |
| **表** |詳細データ |指標を含む顧客リスト |
| **多数** |単一のメトリック | YTD 合計収入 |
| **ヒートカード** |パターン検出 | 1 日/時間あたりの売上高 |
| **点群** |相関関係 |顧客価値と頻度 |
| **サンキーダイアグラム** |流れ分析 |ユーザージャーニー |

### 例: 折れ線グラフ (収入の傾向)

#### ステップ 1: データセットの作成

```
Interface → Données → Datasets → + Dataset
```

**構成**：
- **データベース**: Dremio
- **図**: Production.Marts
- **テーブル**: mart_daily_revenue

#### ステップ 2: グラフの作成

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**パラメータ**:
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

**生成された SQL**:
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

### 例: 棒グラフ (上位顧客)

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

### 例: ピボットテーブル

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

### 例: トレンドのある大きな数値

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

## 建設ダッシュボード

### ダッシュボード作成プロセス

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

### ステップ 1: ダッシュボードの作成

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**ダッシュボード設定**:
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

### ステップ 2: グラフィックの追加

左側のパネルからグラフィックをドラッグ アンド ドロップするか、新しいグラフィックを作成します。

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### ステップ 3: レイアウトを設計する

**グリッド システム**:
- 12列幅
- グラフィックスがグリッドにスナップします
- スワイプしてサイズ変更と位置変更

**レイアウト例**:
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

### ステップ 4: ダッシュボード フィルターを追加する

```
Tableau de Bord → Éditer → + Filtre
```

**日付範囲フィルター**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**カテゴリフィルター**:
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

**デジタルフィルター**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### ステップ 5: クロス フィルタリング

ダッシュボードのクロスフィルタリングを有効にします。

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**構成**：
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**ユーザーエクスペリエンス**:
- バーをクリック→ダッシュボード全体をフィルタリングします
- セクターシェアをクリック→関連グラフィックを更新
- フィルタをクリア → デフォルトのビューにリセット

---

## 高度な機能

### SQL ラボ

アドホック クエリ用の対話型 SQL エディター。

#### クエリの実行

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

**特徴**：
- テーブルと列のオートコンプリート
- リクエスト履歴
- 複数のタブ
- 結果のエクスポート（CSV、JSON）
- 再利用のためにクエリを保存

#### クエリからテーブルを作成 (CTAS)

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

### 神社テンプレート

Jinja2 テンプレートを使用した動的 SQL:

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

**テンプレート変数**:
- `{{ from_dttm }}` - 開始日の範囲
- `{{ to_dttm }}` - 日付範囲の終了
- `{{ filter_values('column') }}` - 選択されたフィルター値
- `{{ current_username }}` - ログインユーザー

### アラートとレポート

#### アラートの作成

```
Interface → Alertes & Rapports → + Alerte
```

**構成**：
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

#### レポートの作成

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

### カスタム視覚化プラグイン

カスタム グラフィック タイプを作成します。

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

ビルドしてインストールします。
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## セキュリティと権限

### ロールベースのアクセス制御 (RBAC)

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

### 統合された役割

|役割 |権限 |使用例 |
|------|---------------|---------------|
| **管理者** |すべての権限 |システム管理者 |
| **アルファ** |ダッシュボード/チャートの作成、編集、削除 |データアナリスト |
| **ガンマ** |ダッシュボードの表示、SQL Lab クエリの実行 |ビジネスユーザー |
| **sql_lab** | SQL Lab へのアクセスのみ |データサイエンティスト |
| **パブリック** |公開ダッシュボードのみを表示 |匿名ユーザー |

### カスタムロールの作成

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**例: マーケティング アナリストの役割**
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

### ラインレベル安全性 (RLS)

ユーザー属性に従ってデータを制限します。

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**例: 地域ベースの RLS**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**例: クライアントベースの RLS**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### データベース接続のセキュリティ

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

## パフォーマンスの最適化

### クエリのキャッシュ

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

**キャッシュ戦略**:
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

### 非同期リクエスト

長いクエリの非同期クエリ実行を有効にします。

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

### データベースクエリの最適化

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

### ダッシュボードの読み込みの最適化

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

### パフォーマンスの監視

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

## 統合と共有

### パブリック ダッシュボード

接続なしでダッシュボードにアクセスできるようにします。

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**公開 URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### iframe の統合

ダッシュボードを外部アプリケーションに統合します。

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

**統合設定**:
- `standalone=1` - ナビゲーションを非表示にする
- `show_filters=0` - フィルターパネルを非表示にする
- `show_title=0` - ダッシュボードのタイトルを非表示にする

### ゲストトークン認証

統合ダッシュボードへのプログラムによるアクセス:

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

### ダッシュボードのエクスポート

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## ベストプラクティス

### ダッシュボードのデザイン

1. **レイアウト階層**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **色の一貫性**
   - すべてのダッシュボードで一貫した配色を使用する
   - 緑は正の指標、赤は負の指標
   - カテゴリのブランドカラー

3. **パフォーマンス**
   - ダッシュボードごとのグラフィックの制限 (< 15)
   - 適切な集計レベルを使用する
   - 静的データのキャッシュを有効にする
   - 適切な行数制限を設定する

4. **インタラクティブ性**
   - 意味のあるフィルターを追加する
   - 探索のためのクロスフィルタリングを有効にする
   - ドリルダウン機能を提供します

### グラフィックの選択

|データ型 |推奨チャート |避ける |
|--------------|----------------------------|----------|
| **時系列** |線形、面 |セクター、リング |
| **比較** |バー、コラム |線形 (データポイントが少ない) |
| **全体のシェア** |セクター、リング、ツリーマップ |バー (カテゴリもあり) |
| **配布** |ヒストグラム、箱ひげ図 |セクター |
| **相関関係** |雲点、泡 |バー |
| **地理** |地図、コロプレス |表 |

### クエリの最適化

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

＃＃＃ 安全

1. **アクセス制御**
   - ユーザー管理にRBACを使用する
   - データ分離のための RLS の実装
   - ロールごとにデータベース接続を制限する

2. **データ ガバナンス**
   - ドキュメント データセット プロパティ
   - データ更新スケジュールを定義する
   - クエリのパフォーマンスを監視する

3. **コンプライアンス**
   - ビジュアライゼーションで PII を非表示にする
   - ダッシュボードへのアクセスを監査する
   - データ保持ポリシーを実装する

---

＃＃ まとめ

この包括的なスーパーセット ガイドでは以下について説明しています。

- **構成**: インストール、構成、データベース接続
- **グラフィック**: 50 を超えるグラフィック タイプ、構成、SQL 生成
- **ダッシュボード**: レイアウト設計、フィルタ、クロスフィルタリング
- **高度な機能**: SQL Lab、Jinja テンプレート、アラート、カスタム プラグイン
- **セキュリティ**: RBAC、RLS、データベース接続セキュリティ
- **パフォーマンス**: キャッシュ、非同期クエリ、クエリの最適化
- **統合**: パブリック ダッシュボード、iframe 統合、ゲスト トークン
- **グッドプラクティス**: デザイン原則、グラフィックの選択、セキュリティ

覚えておくべき重要なポイント:
- スーパーセットは、高パフォーマンス分析のために Dremio に接続します
- 豊富な視覚化ライブラリでさまざまなユースケースをサポート
- 組み込みのキャッシュと非同期クエリにより、高速なダッシュボードが保証されます
- RBAC と RLS により安全なセルフサービス分析が可能になります
- 統合機能により、外部アプリケーションとの統合が可能

**関連ドキュメント:**
- [Dremio セットアップガイド](./dremio-setup.md)
- [アーキテクチャ: データ フロー](../architecture/data-flow.md)
- [最初のステップのチュートリアル](../getting-started/first-steps.md)
- [データ品質ガイド](./data-quality.md)

---

**バージョン**: 3.2.0  
**最終更新**: 2025 年 10 月 16 日