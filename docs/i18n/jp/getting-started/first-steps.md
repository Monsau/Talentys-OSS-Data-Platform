# データ プラットフォームの使用を開始する

**バージョン**: 3.2.0  
**最終更新**: 2025-10-16  
**言語**: フランス語

---

＃＃ 概要

このチュートリアルでは、サービスへの接続から、Airbyte、Dremio、dbt、Superset を使用した最初のデータ パイプラインの構築まで、データ プラットフォームとの最初のやり取りについて説明します。

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

**推定所要時間**: 60 ～ 90 分

---

## 前提条件

始める前に、次のことを確認してください。

- ✅ すべてのサービスがインストールされ、実行されています。
- ✅ Webインターフェースにアクセスできます
- ✅ Python仮想環境が有効になっています
- ✅ SQL の基本的な理解

**サービスが動作していることを確認してください:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## ステップ 1: すべてのサービスにアクセスする

### サービス URL

|サービス | URL |デフォルトの認証情報 |
|----------|----------|---------------|
| **エアバイト** | http://ローカルホスト:8000 | airbyte@example.com / パスワード |
| **ドレミオ** | http://ローカルホスト:9047 |管理者/管理者123 |
| **スーパーセット** | http://ローカルホスト:8088 |管理者 / 管理者 |
| **MinIO** | http://ローカルホスト:9001 |ミニオアドミン / ミニオアドミン123 |

### 最初の接続

**エアバイト:**
1. http://localhost:8000 を開きます。
2. セットアップウィザードを完了します
3. ワークスペース名を「Production」に設定します。
4. 設定を上書きする (後で構成可能)

**ドレミオ:**
1. http://localhost:9047 を開きます。
2. 最初のアクセス時に管理者ユーザーを作成します。
   - ユーザー名: `admin`
   - 電子メール: `admin@example.com`
   - パスワード: `admin123`
3.「始める」をクリックします。

**スーパーセット:**
1. http://localhost:8088 を開きます。
2. デフォルトの資格情報でログインします。
3. パスワードを変更します: [設定] → [ユーザー情報] → [パスワードをリセット]

---

## ステップ 2: Airbyte で最初のデータ ソースを構成する

### PostgreSQL ソースを作成する

**シナリオ**: PostgreSQL データベースからデータを抽出します。

1. **ソースに移動**
   - 左側のメニューで「ソース」をクリックします。
   - 「+ 新しいソース」をクリックします。

2. **PostgreSQL を選択**
   - 「PostgreSQL」を検索します
   - 「PostgreSQL」コネクタをクリックします。

3. **接続の設定**
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

4. **テストして保存**
   - 「ソースの設定」をクリックします。
   - 接続テストを待ちます
   - ソースが作成されました ✅

### サンプルデータの作成 (オプション)

まだデータがない場合は、サンプル テーブルを作成します。

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

## ステップ 3: MinIO S3 宛先を構成する

### 目的地を作成する

1. **目的地に移動**
   - 左側のメニューで「目的地」をクリックします
   - 「+ 新しい目的地」をクリックします。

2. **S3 を選択**
   - 「S3」を検索
   - 「S3」コネクタをクリックします

3. **MinIO を S3 として構成**
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

4. **テストして保存**
   - 「目的地を設定」をクリックします。
   - 接続テストに合格する必要があります ✅

---

## ステップ 4: 最初の接続を作成する

### ソースから宛先へのリンク

1. **接続に移動**
   - 左側のメニューで「接続」をクリックします
   - 「+ 新しい接続」をクリックします。

2. **ソースを選択**
   - 「PostgreSQL 本番環境」を選択します。
   - 「既存のソースを使用」をクリックします。

3. **目的地を選択**
   - 「MinIO データレイク」を選択します
   - 「既存の宛先を使用」をクリックします。

4. **同期の構成**
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

5. **正規化**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **バックアップと同期**
   - 「接続のセットアップ」をクリックします。
   - 「今すぐ同期」をクリックして最初の同期を実行します
   - 同期の進行状況を監視する

### モニターの同期

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

**同期ステータスを確認します:**
- ステータスは「成功」(緑色) と表示されます。
- 同期されたレコード: ~11 (顧客 5 件 + 注文 6 件)
- 詳細についてはログを参照してください

---

## ステップ 5: Dremio を MinIO に接続する

### Dremio に S3 ソースを追加する

1. **ソースに移動**
   - http://localhost:9047 を開きます
   - 「ソースを追加」(+アイコン)をクリックします。

2. **S3 を選択**
   - 「Amazon S3」を選択します
   - MinIO として設定します。

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

3. **テストして保存**
   - 「保存」をクリックします
   - Dremio は MinIO バケットを分析します

### データの参照

1. **MinIOLake ソースに移動します**
   - 「MinIOLake」を開発
   - 「データレイク」バケットを開発する
   - 「raw-data」フォルダーを展開します。
   - 「production_public」フォルダーを参照してください。

2. **データのプレビュー**
   - 「顧客」フォルダをクリックします
   - Parquet ファイルをクリックします
   - 「プレビュー」をクリックしてデータを確認します
   - データは PostgreSQL と一致する必要があります ✅

### 仮想データセットを作成する

1. **データのクエリ**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **VDS として保存**
   - 「名前を付けてビューを保存」をクリックします。
   - 名前: `vw_customers`
   - スペース: `@admin` (あなたのスペース)
   - 「保存」をクリックします

3. **データのフォーマット** (オプション)
   - `vw_customers` をクリックします。
   - インターフェースを使用して列の名前を変更し、タイプを変更します
   - 例: `customer_id` の名前を `id` に変更します。

---

## ステップ 6: dbt テンプレートを作成する

### dbt プロジェクトを初期化する

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

### ソース定義の作成

**ファイル**: `dbt/models/sources.yml`

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

### ステージング テンプレートを作成する

**ファイル**: `dbt/models/staging/stg_customers.sql`

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

**ファイル**: `dbt/models/staging/stg_orders.sql`

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

### マートテンプレートを作成する

**ファイル**: `dbt/models/marts/fct_customer_orders.sql`

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

### dbt モデルを実行する

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

### Dremio をチェックインする

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## ステップ 7: スーパーセットでダッシュボードを作成する

### Dremio データベースを追加する

1. **データベースに移動**
   - http://localhost:8088 を開きます
   - 「データ」→「データベース」をクリックします。
   - 「+データベース」をクリックします。

2. **Dremio を選択**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **「接続」をクリックします**

### データセットを作成する

1. **データセットに移動**
   - 「データ」→「データセット」をクリックします。
   - 「+ データセット」をクリックします。

2. **データセットの構成**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **「データセットの作成とグラフの作成」をクリックします**

### グラフを作成する

#### グラフ 1: 顧客セグメント (円形図)

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

#### グラフ 2: 国別の収入 (棒グラフ)

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

#### グラフ 3: 顧客指標 (多数)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### ダッシュボードを作成する

1. **ダッシュボードに移動**
   - 「ダッシュボード」をクリックします
   - 「+ダッシュボード」をクリックします。

2. **ダッシュボードの構成**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **グラフィックの追加**
   - 作成したグラフィックをドラッグアンドドロップします
   - グリッドに整理します:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **フィルターを追加** (オプション)
   - 「フィルターを追加」をクリックします。
   - フィルター条件: 国コード
   - すべてのチャートに適用

5. **ダッシュボードを保存**

---

## ステップ 8: 完全なパイプラインを確認する

### エンドツーエンドのテスト

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

### 新しいデータを追加する

1. **PostgreSQL に新しいレコードを挿入**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Airbyte同期をトリガー**
   - Airbyteインターフェースを開きます
   - 「PostgreSQL → MinIO」接続に移動します。
   - 「今すぐ同期」をクリックします
   - 最後まで待ってください ✅

3. **dbt を実行**
   ```bash
   cd dbt
   dbt run
   ```

4. **スーパーセット ダッシュボードを更新します**
   - ダッシュボードを開きます
   - 「更新」ボタンをクリックします
   - 新しいデータが表示されるはずです ✅

### データフローを確認する

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

## ステップ 9: パイプラインを自動化する

### Airbyte 同期のスケジュールを設定する

24 時間ごとの 02:00 に実行されるようにすでに構成されています。

編集するには:
1.Airbyteで接続を開く
2.「設定」タブに移動します
3.「レプリケーション頻度」を更新します。
4.保存

### dbt 実行のスケジュールを設定する

**オプション 1: Cron ジョブ (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**オプション 2: Python スクリプト**

**ファイル**: `scripts/run_pipeline.py`
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

### Docker Compose を使用してスケジュールを設定する

**ファイル**: `docker-compose.scheduler.yml`
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

## 次のステップ

おめでとう！完全なエンドツーエンドのデータ パイプラインが構築されました。 🎉

＃＃＃ もっと詳しく知る

1. **Airbyte Advanced** - [Airbyte統合ガイド](../guides/airbyte-integration.md)
2. **Dremio の最適化** - [Dremio セットアップガイド](../guides/dremio-setup.md)
3. **複雑な dbt モデル** - [dbt 開発ガイド](../guides/dbt-development.md)
4. **高度なダッシュボード** - [スーパーセット ダッシュボード ガイド](../guides/superset-dashboards.md)
5. **データ品質** - [データ品質ガイド](../guides/data-quality.md)

### トラブルシューティング

問題がある場合は、次を参照してください。
- [トラブルシューティング ガイド](../guides/troubleshooting.md)
- [インストールガイド](installation.md#troubleshooting)
- [設定ガイド](configuration.md)

---

＃＃ まとめ

成功しました:

- ✅ プラットフォームの 7 つのサービスにアクセス
- ✅ Airbyte ソースを構成する (PostgreSQL)
- ✅ Airbyte の宛先を設定する (MinIO S3)
- ✅ 初めての Airbyte 接続を作成する
- ✅ Dremio を MinIO に接続する
- ✅ dbt テンプレートの作成 (ステージング + マート)
- ✅ スーパーセット ダッシュボードを構築する
- ✅ エンドツーエンドのデータフローを確認する
- ✅ パイプラインの実行を自動化する

**データ プラットフォームが運用できるようになりました!** 🚀

---

**ファースト ステップ ガイド バージョン**: 3.2.0  
**最終更新**: 2025-10-16  
**管理者**: データ プラットフォーム チーム