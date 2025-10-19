# トラブルシューティングガイド

**バージョン**: 3.2.0  
**最終更新日**: 2025 年 10 月 16 日  
**言語**: フランス語

＃＃ 目次

1. [概要](#overview)
2. [一般的なトラブルシューティングのアプローチ](#general-troubleshooting-approach)
3. [エアバイトの問題](#airbyte-problems)
4. [Dremio の問題](#dremio-problems)
5. [dbt の問題](#dbt-problems)
6. [スーパーセットの問題](#superset-problems)
7. [PostgreSQLの問題](#postgresql-problems)
8. [MinIO の問題](#minio-problems)
9. [Elasticsearch の問題](#elasticsearch-issues)
10. [ネットワークと接続](#network-and-connectivity)
11. [パフォーマンスの問題](#パフォーマンスの問題)
12. [データ品質の問題](#data-quality-issues)

---

＃＃ 概要

この包括的なトラブルシューティング ガイドは、すべてのプラットフォーム コンポーネントにわたる一般的な問題の診断と解決に役立ちます。問題はコンポーネントごとに整理され、明確な症状、診断、解決策が示されています。

### トラブルシューティングの方法論

```mermaid
flowchart TB
    A[Problème signalé] --> B[Identifier les symptômes]
    B --> C[Vérifier les logs]
    C --> D[Isoler le composant]
    D --> E{Problème connu?}
    E -->|Oui| F[Appliquer la solution]
    E -->|Non| G[Déboguer davantage]
    G --> H[Vérifier les dépendances]
    H --> I[Tester la solution]
    F --> I
    I --> J{Résolu?}
    J -->|Oui| K[Documenter la solution]
    J -->|Non| L[Escalader]
    
    style A fill:#e1f5ff
    style F fill:#4CAF50,color:#fff
    style K fill:#4CAF50,color:#fff
    style L fill:#FF6B6B
```

---

## 一般的なトラブルシューティングのアプローチ

### ステップ 1: サービスのステータスを確認する

```bash
# Check all Docker containers
docker-compose ps

# Expected output:
#   airbyte-server     Up       0.0.0.0:8001->8001/tcp
#   airbyte-webapp     Up       0.0.0.0:8000->80/tcp
#   dremio             Up       0.0.0.0:9047->9047/tcp
#   superset           Up       0.0.0.0:8088->8088/tcp
#   postgres           Up       0.0.0.0:5432->5432/tcp
#   minio              Up       0.0.0.0:9000-9001->9000-9001/tcp
#   elasticsearch      Up       0.0.0.0:9200->9200/tcp
```

### ステップ 2: ログを確認する

```bash
# View logs for specific service
docker-compose logs -f [service_name]

# View last 100 lines
docker-compose logs --tail=100 [service_name]

# Search logs for errors
docker-compose logs [service_name] | grep -i error
```

### ステップ 3: ネットワーク接続を確認する

```bash
# Test network connectivity between containers
docker exec airbyte-server ping postgres
docker exec dremio curl http://minio:9000/minio/health/live
```

### ステップ 4: リソースの使用状況を確認する

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### 一般的なクイックフィックス

```bash
# Restart specific service
docker-compose restart [service_name]

# Restart all services
docker-compose restart

# Full cleanup and restart
docker-compose down
docker-compose up -d

# Remove volumes and start fresh (⚠️ data loss!)
docker-compose down -v
docker-compose up -d
```

---

## エアバイトの問題

### 問題 1: Airbyte インターフェースが読み込まれない

**症状** ：
- ブラウザに「接続できません」と表示される、またはタイムアウトになる
- URL: `http://localhost:8000` が応答しません

**診断**：
```bash
# Check if webapp container is running
docker-compose ps airbyte-webapp

# Check webapp logs
docker-compose logs airbyte-webapp
```

**解決策**:

1. **ポートが使用されていないことを確認します**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID [process_id] /F
   ```

2. **Airbyteコンテナを再起動**:
   ```bash
   docker-compose restart airbyte-webapp airbyte-server
   ```

3. **サーバーが正常であることを確認します**:
   ```bash
   curl http://localhost:8001/health
   # Expected: {"available":true}
   ```

### 問題 2: 「接続タイムアウト」により同期が失敗する

**症状** ：
- 同期タスクがすぐに失敗するかハングする
- エラー: 「接続タイムアウト」または「ソースに接続できません」

**診断**：
```bash
# Check worker logs
docker-compose logs airbyte-worker | grep -i error

# Verify source connectivity
docker exec airbyte-worker ping [source_host]
```

**解決策**:

1. **ソース識別子を確認します**:
   ```yaml
   # Check connection configuration
   Host: postgres  # Use container name, not localhost
   Port: 5432
   Username: postgres
   Password: [correct_password]
   ```

2. **タイムアウトを増やします**:
   ```bash
   # Edit docker-compose.yml
   environment:
     - CONNECTION_TIMEOUT_MS=60000  # 60 seconds
   ```

3. **ネットワークを確認します**:
   ```bash
   # Verify services are on same network
   docker network inspect dremiodbt_data-platform
   ```

### 問題 3: 同期中のメモリ不足

**症状** ：
- 大規模な同期中にコンテナー ワーカーがクラッシュする
- エラー: 「OutOfMemoryError」または「Java ヒープ スペース」

**診断**：
```bash
# Check worker memory usage
docker stats airbyte-worker

# Check logs for OOM
docker-compose logs airbyte-worker | grep -i "OutOfMemory"
```

**解決策**:

1. **ワーカーのメモリを増やす**:
   ```yaml
   # docker-compose.yml
   airbyte-worker:
     environment:
       - JOB_MAIN_CONTAINER_MEMORY_LIMIT=2Gi
       - JOB_MAIN_CONTAINER_MEMORY_REQUEST=1Gi
   ```

2. **バッチサイズを減らす**:
   ```json
   {
     "batch_size": 5000  // Reduce from default 10000
   }
   ```

3. **増分同期を使用します**:
   ```yaml
   sync_mode: incremental
   cursor_field: updated_at
   ```

### 問題 4: データが宛先に表示されない

**症状** ：
- 同期が正常に完了しました
- ログにエラーはありません
- データが MinIO/宛先にありません

**診断**：
```bash
# Check sync logs for record count
docker-compose logs airbyte-worker | grep "records"

# Verify destination path
aws s3 ls s3://datalake/bronze/ --endpoint-url http://localhost:9000
```

**解決策**:

1. **宛先構成を確認します**:
   ```json
   {
     "destination_path": "datalake/bronze/",
     "format": "parquet",
     "compression": "snappy"
   }
   ```

2. **正規化をチェック**:
   ```bash
   # Ensure normalization is enabled
   "normalization": {
     "option": "basic"
   }
   ```

3. **手動検証**:
   ```bash
   # Check MinIO directly
   docker exec minio mc ls local/datalake/bronze/
   ```

---

## ドレミオの問題

### 問題 1: Dremio インターフェイスに接続できない

**症状** ：
- ブラウザに `http://localhost:9047` で接続エラーが表示される

**診断**：
```bash
# Check Dremio status
docker-compose ps dremio

# Check logs for startup errors
docker-compose logs dremio | grep -i error
```

**解決策**:

1. **完全に起動するまで待ちます** (2 ～ 3 分かかる場合があります):
   ```bash
   docker-compose logs -f dremio
   # Wait for: "Dremio Daemon Started"
   ```

2. **メモリを増やす**:
   ```yaml
   # docker-compose.yml
   dremio:
     environment:
       - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
   ```

3. **Dremio データをクリーンアップします** (⚠️ 設定をリセットします):
   ```bash
   docker-compose down
   docker volume rm dremiodbt_dremio-data
   docker-compose up -d dremio
   ```

### 問題 2: MinIO の「オフライン ソース」

**症状** ：
- MinIO ソースに赤色の「オフライン」インジケーターが表示される
- エラー: 「ソースに接続できません」

**診断**：
```bash
# Test MinIO from Dremio container
docker exec dremio curl http://minio:9000/minio/health/live

# Check MinIO logs
docker-compose logs minio
```

**解決策**:

1. **MinIO エンドポイントを確認します**:
   ```json
   {
     "config": {
       "propertyList": [
         {
           "name": "fs.s3a.endpoint",
           "value": "minio:9000"  // Not localhost!
         },
         {
           "name": "fs.s3a.path.style.access",
           "value": "true"
         }
       ]
     }
   }
   ```

2. **資格情報を確認します**:
   ```bash
   # Verify MinIO credentials
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

3. **メタデータを更新**:
   ```sql
   -- In Dremio SQL
   ALTER SOURCE MinIO REFRESH METADATA;
   ```

### 問題 3: クエリのパフォーマンスが遅い

**症状** ：
- クエリには 10 秒以上かかります
- ダッシュボードの読み込みが遅い

**診断**：
```sql
-- Check query profile
SELECT * FROM sys.jobs 
WHERE execution_time_ms > 10000
ORDER BY start_time DESC
LIMIT 10;

-- Check if reflection was used
SELECT 
    query_text,
    acceleration_profile.accelerated
FROM sys.jobs
WHERE job_id = 'your-job-id';
```

**解決策**:

1. **反射を作成**:
   ```sql
   -- Create raw reflection
   CREATE REFLECTION raw_customers
   ON Production.Dimensions.dim_customers
   USING DISPLAY (customer_id, name, email, lifetime_value);
   
   -- Create aggregation reflection
   CREATE REFLECTION agg_daily_revenue
   ON Production.Facts.fct_orders
   USING DIMENSIONS (order_date)
   MEASURES (SUM(amount), COUNT(*));
   ```

2. **パーティション フィルターを追加**:
   ```sql
   -- Bad: Full scan
   SELECT * FROM orders;
   
   -- Good: Partition pruning
   SELECT * FROM orders 
   WHERE order_date >= '2025-10-01';
   ```

3. **エグゼキュータのメモリを増やす**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms16g -Xmx32g
   ```

### 問題 4: リフレクションが構築されない

**症状** ：
- リフレクションが「REFRESHING」状態のままになる
- 終わりがない

**診断**：
```sql
-- Check reflection status
SELECT * FROM sys.reflections 
WHERE status != 'ACTIVE';

-- Check reflection errors
SELECT * FROM sys.reflection_dependencies;
```

**解決策**:

1. **無効化してから再度有効化**:
   ```sql
   ALTER REFLECTION reflection_id SET ENABLED = FALSE;
   ALTER REFLECTION reflection_id SET ENABLED = TRUE;
   ```

2. **ソース データを確認します**:
   ```sql
   -- Verify source table is accessible
   SELECT COUNT(*) FROM source_table;
   ```

3. **タイムアウトを増やします**:
   ```conf
   # dremio.conf
   reflection.build.timeout.ms: 7200000  # 2 hours
   ```

---

## dbt の問題

### 問題 1: dbt の実行時に「接続エラー」が発生する

**症状** ：
- `dbt debug` は失敗します
- エラー: 「Dremio に接続できませんでした」

**診断**：
```bash
# Test dbt connection
dbt debug

# Check profiles.yml
cat ~/.dbt/profiles.yml
```

**解決策**:

1. **profiles.yml を確認します**:
   ```yaml
   dremio_project:
     target: dev
     outputs:
       dev:
         type: dremio
         host: localhost  # or dremio container name
         port: 9047
         username: admin
         password: your_password
         use_ssl: false
   ```

2. **Dremio の接続をテストします**:
   ```bash
   curl http://localhost:9047/apiv2/login \
     -H "Content-Type: application/json" \
     -d '{"userName":"admin","password":"your_password"}'
   ```

3. **Dremio アダプターをインストールします**:
   ```bash
   pip install dbt-dremio
   ```

### 問題 2: モデルの構築に失敗する

**症状** ：
- `dbt run` は特定のモデルで失敗します
- SQLのコンパイルまたは実行エラー

**診断**：
```bash
# Run with debug mode
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/project/models/failing_model.sql
```

**解決策**:

1. **モデル構文を確認します**:
   ```sql
   -- Verify SQL is valid
   -- Check for missing commas, parentheses
   -- Ensure all refs are correct: {{ ref('model_name') }}
   ```

2. **最初に SQL IDE でテストします**:
   ```bash
   # Copy compiled SQL and test in Dremio UI
   # Fix syntax errors
   # Update model
   ```

3. **依存関係を確認します**:
   ```bash
   # Ensure upstream models exist
   dbt run --select +failing_model
   ```

### 問題 3: テストが失敗する

**症状** ：
- `dbt test` は失敗を報告します
- データ品質の問題が検出されました

**診断**：
```bash
# Run specific test
dbt test --select stg_customers

# Store failures for analysis
dbt test --store-failures

# Query failed records
SELECT * FROM dbt_test_failures.not_null_stg_customers_email;
```

**解決策**:

1. **ソース データを修正します**:
   ```sql
   -- Add filters to model
   WHERE email IS NOT NULL
     AND email LIKE '%@%'
   ```

2. **テストしきい値を調整**:
   ```yaml
   tests:
     - not_null:
         config:
           error_if: ">= 10"  # Allow up to 10 failures
           warn_if: ">= 1"
   ```

3. **根本原因を調査します**:
   ```sql
   -- Find why test is failing
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE email IS NULL;
   ```

### 問題 4: インクリメンタル モデルが機能しない

**症状** ：
- 増分モデルは実行されるたびに完全に再構築されます
- 増分動作なし

**診断**：
```bash
# Check if unique_key is set
grep -A 5 "config(" models/facts/fct_orders.sql

# Verify is_incremental() block exists
grep -A 3 "is_incremental()" models/facts/fct_orders.sql
```

**解決策**:

1. **システム要件を追加**:
   ```sql
   {{
       config(
           materialized='incremental',
           unique_key='order_id'  -- Must be set!
       )
   }}
   ```

2. **インクリメンタル ロジックを追加**:
   ```sql
   {% if is_incremental() %}
       WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
   {% endif %}
   ```

3. **一度完全リフレッシュを強制します**:
   ```bash
   dbt run --full-refresh --select fct_orders
   ```

---

## スーパーセットの問題

### 問題 1: スーパーセットに接続できない

**症状** ：
- ログイン ページに「無効な資格情報」と表示される
- デフォルトの管理者/管理者のペアが機能しない

**診断**：
```bash
# Check Superset logs
docker-compose logs superset | grep -i login

# Check if admin user exists
docker exec superset superset fab list-users
```

**解決策**:

1. **管理者パスワードをリセット**:
   ```bash
   docker exec -it superset superset fab reset-password \
     --username admin \
     --password new_password
   ```

2. **管理者ユーザーを作成**:
   ```bash
   docker exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@company.com \
     --password admin
   ```

3. **スーパーセットをリセット**:
   ```bash
   docker exec superset superset db upgrade
   docker exec superset superset init
   ```

### 問題 2: データベース接続が失敗する

**症状** ：
- 「接続テスト」ボタンが失敗する
- エラー: 「データベースに接続できません」

**診断**：
```bash
# Test connectivity from Superset container
docker exec superset ping dremio

# Check Dremio is running
docker-compose ps dremio
```

**解決策**:

1. **正しい SQLAlchemy URI を使用します**:
   ```
   # For Dremio via Arrow Flight
   dremio+flight://admin:password@dremio:32010/datalake
   
   # For PostgreSQL
   postgresql://postgres:postgres@postgres:5432/database
   ```

2. **必要なドライバーをインストール**:
   ```bash
   docker exec superset pip install pyarrow
   docker-compose restart superset
   ```

3. **ネットワークを確認します**:
   ```bash
   # Ensure Superset and Dremio are on same network
   docker network inspect dremiodbt_data-platform
   ```

### 問題 3: グラフが読み込まれない

**症状** ：
- ダッシュボードには読み込みスピナーが無期限に表示されます
- グラフに「データのロード中にエラーが発生しました」と表示される

**診断**：
```bash
# Check Superset logs
docker-compose logs superset | tail -100

# Check query execution in SQL Lab
# Run the chart's query directly
```

**解決策**:

1. **クエリのタイムアウトを確認します**:
   ```python
   # superset_config.py
   SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes
   SQL_MAX_ROW = 100000
   ```

2. **非同期リクエストを有効にする**:
   ```python
   FEATURE_FLAGS = {
       'GLOBAL_ASYNC_QUERIES': True
   }
   ```

3. **キャッシュをクリア**:
   ```bash
   # Clear Redis cache
   docker exec redis redis-cli FLUSHALL
   ```

### 問題 4: 権限エラー

**症状** ：
- ユーザーはダッシュボードを表示できません
- エラー: 「このダッシュボードにアクセスできません」

**診断**：
```bash
# Check user roles
docker exec superset superset fab list-users

# Check dashboard ownership
# UI → Dashboards → [dashboard] → Edit → Owners
```

**解決策**:

1. **ユーザーをロールに追加**:
   ```bash
   docker exec superset superset fab add-user-role \
     --username user@company.com \
     --role Alpha
   ```

2. **ダッシュボードへのアクセスを許可**:
   ```
   UI → Dashboards → [dashboard] → Edit
   → Settings → Published (make public)
   or
   → Owners → Add user/role
   ```

3. **RLS ルールを確認します**:
   ```
   UI → Data → Datasets → [dataset]
   → Row Level Security → Review filters
   ```

---

## PostgreSQL の問題

### 問題 1: 接続が拒否されました

**症状** ：
- アプリケーションが PostgreSQL に接続できない
- エラー: 「接続が拒否されました」または「接続できませんでした」

**診断**：
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres | tail -50

# Test connection
docker exec postgres psql -U postgres -c "SELECT 1"
```

**解決策**:

1. **PostgreSQL を再起動**:
   ```bash
   docker-compose restart postgres
   ```

2. **ポートマッピングを確認します**:
   ```bash
   # Verify port 5432 is mapped
   docker-compose ps postgres
   # Should show: 0.0.0.0:5432->5432/tcp
   ```

3. **資格情報を確認します**:
   ```bash
   # Default credentials
   User: postgres
   Password: postgres
   Database: postgres
   ```

### 問題 2: 接続の不足

**症状** ：
- エラー: 「致命的: 残りの接続スロットは予約されています」
- アプリが断続的に接続に失敗する

**診断**：
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- List active connections
SELECT pid, usename, application_name, client_addr
FROM pg_stat_activity
WHERE state = 'active';
```

**解決策**:

1. **max_connections を増やす**:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default is 100
   ```

2. **接続プーリングを使用します**:
   ```yaml
   # docker-compose.yml - add PgBouncer
   pgbouncer:
     image: edoburu/pgbouncer
     environment:
       - DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
       - MAX_CLIENT_CONN=1000
       - DEFAULT_POOL_SIZE=25
   ```

3. **アイドル状態の接続を強制終了**:
   ```sql
   -- Terminate idle connections older than 10 minutes
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

### 問題 3: クエリが遅い

**症状** ：
- データベースクエリには数秒かかります
- アプリの有効期限が切れる

**診断**：
```sql
-- Find slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - pg_stat_activity.query_start > interval '5 seconds'
ORDER BY duration DESC;

-- Check if indexes exist
SELECT tablename, indexname FROM pg_indexes
WHERE schemaname = 'public';
```

**解決策**:

1. **インデックスを作成**:
   ```sql
   -- Index foreign keys
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   
   -- Index frequently filtered columns
   CREATE INDEX idx_orders_order_date ON orders(order_date);
   ```

2. **分析を実行**:
   ```sql
   ANALYZE orders;
   ANALYZE customers;
   ```

3. **shared_buffers を増やす**:
   ```conf
   # postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

---

##MinIO の問題

### 問題 1: MinIO コンソールにアクセスできない

**症状** ：
- ブラウザに `http://localhost:9001` でエラーが表示される

**診断**：
```bash
# Check MinIO status
docker-compose ps minio

# Check logs
docker-compose logs minio
```

**解決策**:

1. **ポートを確認します**:
   ```yaml
   # docker-compose.yml
   ports:
     - "9000:9000"  # API
     - "9001:9001"  # Console
   ```

2. **正しい URL にアクセスします**:
   ```
   API: http://localhost:9000
   Console: http://localhost:9001
   ```

3. **MinIO を再起動**:
   ```bash
   docker-compose restart minio
   ```

### 問題 2: アクセス拒否エラー

**症状** ：
- アプリケーションは S3 の読み取り/書き込みができません
- エラー: 「アクセスが拒否されました」または「403 禁止されました」

**診断**：
```bash
# Test with MinIO client
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc ls local/datalake/
```

**解決策**:

1. **資格情報を確認します**:
   ```bash
   Access Key: minioadmin
   Secret Key: minioadmin
   ```

2. **バケット ポリシーを確認します**:
   ```bash
   # Set public read policy (for testing only!)
   docker exec minio mc anonymous set download local/datalake
   ```

3. **アプリケーションのアクセス キーを作成します**:
   ```bash
   docker exec minio mc admin user add local app_user app_password
   docker exec minio mc admin policy attach local readwrite --user app_user
   ```

### 問題 3: バケットが見つかりません

**症状** ：
- エラー: 「指定されたバケットは存在しません」

**診断**：
```bash
# List all buckets
docker exec minio mc ls local/
```

**解決策**:

1. **バケットを作成します**:
   ```bash
   docker exec minio mc mb local/datalake
   ```

2. **構成内のバケット名を確認します**:
   ```yaml
   # Check for typos
   bucket: datalake  # Not data-lake or DataLake
   ```

---

## ネットワークと接続

### 問題: サービスが通信できない

**症状** ：
- コンテナ間で「接続が拒否されました」
- 「ホストが見つかりません」エラー

**診断**：
```bash
# Check network exists
docker network ls | grep data-platform

# Inspect network
docker network inspect dremiodbt_data-platform

# Test connectivity
docker exec airbyte-server ping postgres
docker exec dremio ping minio
```

**解決策**:

1. **すべてのサービスが同じネットワーク上にあることを確認します**:
   ```yaml
   # docker-compose.yml
   services:
     airbyte-server:
       networks:
         - data-platform
     postgres:
       networks:
         - data-platform
   
   networks:
     data-platform:
       driver: bridge
   ```

2. **ローカルホストではなく、コンテナ名を使用します**:
   ```
   ✗ localhost:5432
   ✓ postgres:5432
   
   ✗ 127.0.0.1:9000
   ✓ minio:9000
   ```

3. **ネットワークを再作成**:
   ```bash
   docker-compose down
   docker network rm dremiodbt_data-platform
   docker-compose up -d
   ```

---

## パフォーマンスの問題

### 問題: CPU 使用率が高い

**診断**：
```bash
# Check resource usage
docker stats

# Find CPU-intensive queries
SELECT query FROM sys.jobs 
WHERE cpu_time_ms > 60000
ORDER BY cpu_time_ms DESC;
```

**解決策**:

1. **競合するリクエストを制限します**:
   ```conf
   # dremio.conf
   planner.max_width_per_node: 2
   ```

2. **クエリの最適化** ([Dremio の問題](#dremio-issues) を参照)

3. **CPU 割り当てを増やす**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '8'
   ```

### 問題: メモリ使用量が多い

**診断**：
```bash
# Monitor memory
docker stats

# Check for memory leaks
docker exec dremio jmap -heap 1
```

**解決策**:

1. **ヒープ サイズを増やします**:
   ```yaml
   environment:
     - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
   ```

2. **ディスク スピルを有効にする**:
   ```conf
   # dremio.conf
   spill.enable: true
   spill.directory: "/opt/dremio/spill"
   ```

---

## データ品質の問題

[データ品質ガイド](./data-quality.md) で詳しく説明されているソリューションを参照してください。

### 簡単なチェック

```sql
-- Check for duplicates
SELECT customer_id, COUNT(*)
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for nulls
SELECT COUNT(*) - COUNT(email) AS null_emails
FROM customers;

-- Check data freshness
SELECT MAX(updated_at) AS last_update
FROM orders;
```

---

＃＃ まとめ

このトラブルシューティング ガイドの内容は次のとおりです。

- **一般的なアプローチ**: 問題を診断するための体系的な方法論
- **コンポーネント別の問題**: プラットフォームの 7 つのサービスの解決策
- **ネットワークの問題**: コンテナの接続の問題
- **パフォーマンスの問題**: CPU、メモリ、クエリの最適化
- **データ品質の問題**: 一般的なデータの問題とチェック

**重要なポイント**:
- 常に最初にログを確認してください: `docker-compose logs [service]`
- サービス間通信にはローカルホストではなくコンテナ名を使用します
- 接続性のテスト: `docker exec [container] ping [target]`
- 監視リソース: `docker stats`
- シンプルに開始: 複雑なデバッグの前にサービスを再起動します。

**関連ドキュメント:**
- [インストールガイド](../getting-started/installation.md)
- [設定ガイド](../getting-started/configuration.md)
- [データ品質ガイド](./data-quality.md)
- [アーキテクチャ: デプロイメント](../architecture/deployment.md)

**さらにサポートが必要ですか?**
- コンポーネントのログを確認します: `docker-compose logs -f [service]`
- サービスドキュメントを参照してください
- GitHub の問題を検索
- サポートチームに連絡する

---

**バージョン**: 3.2.0  
**最終更新日**: 2025 年 10 月 16 日