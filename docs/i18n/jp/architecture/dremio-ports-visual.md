# Dremio ポート ビジュアルガイド

**バージョン**: 3.2.5  
**最終更新**: 2025年10月16日  
**言語**: 日本語

---

## Dremio の 3 つのポート概要

```mermaid
graph TB
    subgraph "ポート 9047 - REST API"
        direction TB
        A1[🌐 Web UI インターフェース]
        A2[🔧 管理]
        A3[📊 モニタリング]
        A4[🔐 認証]
    end
    
    subgraph "ポート 31010 - PostgreSQL プロキシ"
        direction TB
        B1[💼 レガシー BI ツール]
        B2[🔌 標準 JDBC/ODBC]
        B3[🐘 PostgreSQL 互換性]
        B4[🔄 簡単な移行]
    end
    
    subgraph "ポート 32010 - Arrow Flight"
        direction TB
        C1[⚡ 最大パフォーマンス]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Dremio コーディネーター<br/>Dremio 26.0 OSS]
    
    A1 & A2 & A3 & A4 --> D
    B1 & B2 & B3 & B4 --> D
    C1 & C2 & C3 & C4 --> D
    
    E1[(MinIO S3)]
    E2[(PostgreSQL)]
    E3[(Elasticsearch)]
    
    D --> E1 & E2 & E3
    
    style D fill:#FDB515,color:#000,stroke:#000,stroke-width:3px
    style A1 fill:#4CAF50,color:#fff
    style A2 fill:#4CAF50,color:#fff
    style A3 fill:#4CAF50,color:#fff
    style A4 fill:#4CAF50,color:#fff
    style B1 fill:#336791,color:#fff
    style B2 fill:#336791,color:#fff
    style B3 fill:#336791,color:#fff
    style B4 fill:#336791,color:#fff
    style C1 fill:#FF5722,color:#fff
    style C2 fill:#FF5722,color:#fff
    style C3 fill:#FF5722,color:#fff
    style C4 fill:#FF5722,color:#fff
```

---

## PostgreSQL プロキシ詳細アーキテクチャ

### クライアント → Dremio 接続フロー

```mermaid
graph LR
    subgraph "クライアントアプリケーション"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "PostgreSQL Wire プロトコル"
        P[ポート 31010<br/>PostgreSQL プロキシ]
    end
    
    subgraph "Dremio エンジン"
        direction TB
        M1[SQL パーサー]
        M2[オプティマイザー]
        M3[エグゼキューター]
    end
    
    subgraph "データソース"
        direction TB
        S1[📦 Parquet ファイル<br/>MinIO S3]
        S2[💾 PostgreSQL テーブル]
        S3[🔍 Elasticsearch インデックス]
    end
    
    A1 & A2 & A3 --> P
    A4 & A5 & A6 --> P
    
    P --> M1
    M1 --> M2
    M2 --> M3
    
    M3 --> S1 & S2 & S3
    
    style P fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style M1 fill:#FDB515,color:#000
    style M2 fill:#FDB515,color:#000
    style M3 fill:#FDB515,color:#000
```

---

## パフォーマンス比較

### ベンチマーク: 100 GB データスキャン

```mermaid
gantt
    title プロトコル別実行時間（秒）
    dateFormat X
    axisFormat %s 秒
    
    section REST API :9047
    100 GB 転送     :0, 180
    
    section PostgreSQL :31010
    100 GB 転送     :0, 90
    
    section Arrow Flight :32010
    100 GB 転送     :0, 5
```

### データスループット

```mermaid
graph LR
    subgraph "プロトコル別ネットワークパフォーマンス"
        A["ポート 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ 標準"]
        B["ポート 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ 良好"]
        C["ポート 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ 優秀"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### シンプルクエリのレイテンシ

| プロトコル | ポート | 平均レイテンシ | ネットワークオーバーヘッド |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON（冗長） |
| **PostgreSQL プロキシ** | 31010 | 20-50 ms | Wire Protocol（コンパクト） |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow（バイナリカラムナ） |

---

## ポート別ユースケース

### ポート 9047 - REST API

```mermaid
graph TB
    A[ポート 9047<br/>REST API]
    
    A --> B1[🌐 Web ブラウザインターフェース]
    A --> B2[🔧 サービス設定]
    A --> B3[👤 ユーザー管理]
    A --> B4[📊 モニタリングダッシュボード]
    A --> B5[🔐 OAuth/SAML ログイン]
    
    B1 --> C1[スペース/フォルダ作成]
    B1 --> C2[VDS 定義]
    B1 --> C3[データセット探索]
    
    B2 --> C4[ソース追加]
    B2 --> C5[Reflections 設定]
    B2 --> C6[システム設定]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### ポート 31010 - PostgreSQL プロキシ

```mermaid
graph TB
    A[ポート 31010<br/>PostgreSQL プロキシ]
    
    A --> B1[💼 レガシー BI ツール]
    A --> B2[🔄 PostgreSQL 移行]
    A --> B3[🔌 標準ドライバー]
    
    B1 --> C1[Tableau Desktop<br/>Arrow Flight なし]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[既存 JDBC コード<br/>変更不要]
    B2 --> D2[psql スクリプト<br/>100% 互換]
    B2 --> D3[Python アプリ<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[OS ネイティブドライバー]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### ポート 32010 - Arrow Flight

```mermaid
graph TB
    A[ポート 32010<br/>Arrow Flight]
    
    A --> B1[⚡ 最大パフォーマンス]
    A --> B2[🎯 モダンツール]
    A --> B3[🐍 Python エコシステム]
    
    B1 --> C1[TB/PB スキャン]
    B1 --> C2[大規模集約]
    B1 --> C3[ゼロコピー転送]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[pyarrow ライブラリ]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Polars 統合]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## デシジョンツリー: どのポートを使う？

```mermaid
graph TB
    Start[Dremio に接続する必要がある]
    
    Start --> Q1{アプリケーションタイプ？}
    
    Q1 -->|Web インターフェース<br/>管理| Port9047[✅ ポート 9047<br/>REST API]
    
    Q1 -->|BI ツール/SQL クライアント| Q2{Arrow Flight サポート？}
    
    Q2 -->|なし<br/>レガシーツール| Port31010[✅ ポート 31010<br/>PostgreSQL プロキシ]
    Q2 -->|あり<br/>モダンツール| Q3{パフォーマンス重視？}
    
    Q3 -->|はい<br/>本番環境| Port32010[✅ ポート 32010<br/>Arrow Flight]
    Q3 -->|いいえ<br/>開発/テスト| Port31010b[⚠️ ポート 31010<br/>より簡単]
    
    Q1 -->|カスタムアプリケーション| Q4{プログラミング言語？}
    
    Q4 -->|Python/Java| Q5{パフォーマンス重要？}
    Q5 -->|はい| Port32010b[✅ ポート 32010<br/>Arrow Flight]
    Q5 -->|いいえ| Port31010c[✅ ポート 31010<br/>JDBC/psycopg2]
    
    Q4 -->|その他<br/>Go/Rust/.NET| Port31010d[✅ ポート 31010<br/>PostgreSQL Wire]
    
    style Start fill:#2196F3,color:#fff
    style Port9047 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style Port31010 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010b fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010c fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010d fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port32010 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
    style Port32010b fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## PostgreSQL プロキシ接続例

### 1. psql CLI

```bash
# シンプル接続
psql -h localhost -p 31010 -U admin -d datalake

# ダイレクトクエリ
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# インタラクティブモード
$ psql -h localhost -p 31010 -U admin -d datalake
Password for user admin: ****
psql (16.0, server 26.0)
Type "help" for help.

datalake=> \dt
           List of relations
 Schema |   Name    | Type  | Owner 
--------+-----------+-------+-------
 public | customers | table | admin
 public | orders    | table | admin
(2 rows)

datalake=> SELECT customer_id, name, state FROM customers LIMIT 5;
```

### 2. DBeaver 設定

```yaml
接続タイプ: PostgreSQL
接続名: Dremio via PostgreSQL Proxy

メイン:
  ホスト: localhost
  ポート: 31010
  データベース: datalake
  ユーザー名: admin
  パスワード: [your-password]
  
ドライバープロパティ:
  ssl: false
  
詳細設定:
  接続タイムアウト: 30000
  クエリタイムアウト: 0
```

### 3. Python psycopg2

```python
import psycopg2
from psycopg2 import sql

# 接続
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# カーソル
cursor = conn.cursor()

# シンプルクエリ
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# パラメータ化クエリ
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# クローズ
cursor.close()
conn.close()
```

### 4. Java JDBC

```java
import java.sql.*;

public class DremioPostgreSQLProxy {
    public static void main(String[] args) {
        String url = "jdbc:postgresql://localhost:31010/datalake";
        String user = "admin";
        String password = "your-password";
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(
                "SELECT customer_id, name, state FROM MinIO.datalake.customers LIMIT 10"
            );
            
            while (rs.next()) {
                int id = rs.getInt("customer_id");
                String name = rs.getString("name");
                String state = rs.getString("state");
                System.out.printf("ID: %d, Name: %s, State: %s%n", id, name, state);
            }
            
            rs.close();
            stmt.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### 5. ODBC 接続文字列 (DSN)

```ini
[ODBC Data Sources]
Dremio_PostgreSQL=PostgreSQL Unicode Driver

[Dremio_PostgreSQL]
Driver=PostgreSQL Unicode
Description=Dremio via PostgreSQL Proxy
Server=localhost
Port=31010
Database=datalake
Username=admin
Password=your-password
SSLMode=disable
Protocol=7.4
```

---

## Docker Compose 設定

### Dremio ポートマッピング

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # ポート 9047 - REST API / Web UI
      - "9047:9047"
      
      # ポート 31010 - PostgreSQL プロキシ (ODBC/JDBC)
      - "31010:31010"
      
      # ポート 32010 - Arrow Flight (パフォーマンス)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### ポート検証

```bash
# 3つのポートが開いているか確認
netstat -an | grep -E '9047|31010|32010'

# REST API テスト
curl -v http://localhost:9047

# PostgreSQL プロキシテスト
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Arrow Flight テスト (Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## クイックビジュアルサマリー

### 3つのポート一覧

| ポート | プロトコル | 主な用途 | パフォーマンス | 互換性 |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, 管理 | ⭐⭐ 標準 | ⭐⭐⭐ ユニバーサル |
| **31010** | PostgreSQL Wire | 💼 BI ツール, 移行 | ⭐⭐⭐ 良好 | ⭐⭐⭐ 優秀 |
| **32010** | Arrow Flight | ⚡ 本番, dbt, Superset | ⭐⭐⭐⭐⭐ 最大 | ⭐⭐ 限定的 |

### 選択マトリックス

```mermaid
graph TB
    subgraph "選択ガイド"
        A["🎯 ユースケース"]
        
        A --> B1["Web インターフェース<br/>設定"]
        A --> B2["レガシー BI ツール<br/>Arrow Flight なし"]
        A --> B3["PostgreSQL 移行<br/>既存 JDBC コード"]
        A --> B4["dbt, Superset<br/>本番環境"]
        A --> B5["Python pyarrow<br/>分析"]
        
        B1 --> C1["ポート 9047<br/>REST API"]
        B2 --> C2["ポート 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["ポート 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## 追加リソース

### 関連ドキュメント

- [アーキテクチャ - コンポーネント](./components.md) - "Dremio 用 PostgreSQL プロキシ"セクション
- [ガイド - Dremio セットアップ](../guides/dremio-setup.md) - "PostgreSQL プロキシ経由の接続"セクション
- [設定 - Dremio](../getting-started/configuration.md) - `dremio.conf` 設定

### 公式リンク

- **Dremio ドキュメント**: https://docs.dremio.com/
- **PostgreSQL Wire プロトコル**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**バージョン**: 3.2.5  
**最終更新**: 2025年10月16日  
**ステータス**: ✅ 完了
