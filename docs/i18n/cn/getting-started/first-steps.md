# 数据平台入门

**版本**：3.2.0  
**最后更新**：2025-10-16  
**语言**：法语

---

＃＃ 概述

本教程将引导您完成与数据平台的首次交互，从连接到服务到使用 Airbyte、Dremio、dbt 和 Superset 构建您的第一个数据管道。

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

**预计时间**：60-90 分钟

---

## 先决条件

在开始之前，请确保：

- ✅ 所有服务均已安装并运行
- ✅ 您可以访问网络界面
- ✅ 启用Python虚拟环境
- ✅ 对 SQL 的基本了解

**检查服务是否正常工作：**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## 第 1 步：访问所有服务

### 服务 URL

|服务 |网址 |默认凭证 |
|---------|----------|------------------------|
| **Airbyte** | http://localhost:8000 | http://localhost:8000 | airbyte@example.com / 密码 |
| **德雷米奥** | http://本地主机:9047 |管理员/管理员123 |
| **超级组** | http://本地主机:8088 |管理员/管理员|
| **MinIO** | http://localhost:9001 | http://localhost:9001 | minioadmin / minioadmin123 |

### 第一次连接

**航空字节：**
1.打开http://localhost:8000
2. 完成设置向导
3. 设置工作区名称：“Production”
4. 覆盖首选项（可以稍后配置）

**德雷米奥：**
1.打开http://localhost:9047
2. 首次访问时创建管理员用户：
   - 用户名：`admin`
   - 电子邮件：`admin@example.com`
   - 密码：`admin123`
3. 点击“开始”

**超级组：**
1.打开http://localhost:8088
2. 使用默认凭据登录
3. 修改密码：设置→用户信息→重置密码

---

## 步骤 2：在 Airbyte 中配置您的第一个数据源

### 创建 PostgreSQL 源

**场景**：从 PostgreSQL 数据库中提取数据。

1. **导航至来源**
   - 单击左侧菜单中的“来源”
   - 点击“+新来源”

2. **选择 PostgreSQL**
   - 搜索“PostgreSQL”
   - 单击“PostgreSQL”连接器

3. **配置连接**
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

4. **测试并保存**
   - 单击“设置源”
   - 等待连接测试
   - 来源已创建 ✅

### 创建示例数据（可选）

如果您还没有任何数据，请创建示例表：

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

## 步骤 3：配置 MinIO S3 目标

### 创建一个目的地

1. **导航至目的地**
   - 点击左侧菜单中的“目的地”
   - 点击“+新目的地”

2. **选择S3**
   - 搜索“S3”
   - 单击“S3”连接器

3. **将 MinIO 配置为 S3**
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

4. **测试并保存**
   - 点击“设置目的地”
   - 连接测试应该通过 ✅

---

## 步骤 4：创建您的第一个连接

### 将源链接到目标

1. **导航到连接**
   - 单击左侧菜单中的“连接”
   - 点击“+新连接”

2. **选择来源**
   - 选择“PostgreSQL 生产”
   - 单击“使用现有源”

3. **选择目的地**
   - 选择“MinIO数据湖”
   - 点击“使用现有目的地”

4. **配置同步**
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

5. **标准化**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **备份与同步**
   - 点击“设置连接”
   - 点击“立即同步”执行第一次同步
   - 监控同步进度

### 监控同步

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

**检查同步状态：**
- 状态应显示“成功”（绿色）
- 同步记录：~11（5个客户+6个订单）
- 详细信息请参阅日志

---

## 步骤 5：将 Dremio 连接到 MinIO

### 在 Dremio 中添加 S3 源

1. **导航至来源**
   - 打开 http://localhost:9047
   - 单击“添加源”（+ 图标）

2. **选择S3**
   - 选择“亚马逊S3”
   - 配置为 MinIO：

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

3. **测试并保存**
   - 点击“保存”
   - Dremio 将分析 MinIO 存储桶

### 浏览数据

1. **导航到 MinIOLake 源**
   - 开发“MinIOLake”
   - 开发“datalake”桶
   - 展开“原始数据”文件夹
   - 请参阅“product_public”文件夹

2. **预览数据**
   - 单击“客户”文件夹
   - 单击 Parquet 文件
   - 点击“预览”查看数据
   - 数据必须匹配 PostgreSQL ✅

### 创建虚拟数据集

1. **查询数据**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **另存为VDS**
   - 单击“视图另存为”
   - 姓名：`vw_customers`
   - 空间：`@admin`（您的空间）
   - 点击“保存”

3. **格式化数据**（可选）
   - 点击`vw_customers`
   - 使用界面重命名列、更改类型
   - 示例：将 `customer_id` 重命名为 `id`

---

## 步骤 6：创建 dbt 模板

### 初始化 dbt 项目

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

### 创建源定义

**文件**：`dbt/models/sources.yml`

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

### 创建暂存模板

**文件**：`dbt/models/staging/stg_customers.sql`

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

**文件**：`dbt/models/staging/stg_orders.sql`

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

### 创建一个集市模板

**文件**：`dbt/models/marts/fct_customer_orders.sql`

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

### 运行 dbt 模型

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

### 签到德雷米奥

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## 步骤 7：在 Superset 中创建仪表板

### 添加 Dremio 数据库

1. **导航到数据库**
   - 打开http://localhost:8088
   - 单击“数据”→“数据库”
   - 点击“+数据库”

2. **选择Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **点击“连接”**

### 创建数据集

1. **导航到数据集**
   - 单击“数据”→“数据集”
   - 单击“+数据集”

2. **配置数据集**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **点击“创建数据集并创建图表”**

### 创建图表

####图表1：客户群（圆形图）

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

#### 图 2：按国家/地区划分的收入（条形图）

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

####图表3：客户指标（大数字）

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### 创建仪表板

1. **导航至仪表板**
   - 点击“仪表板”
   - 点击“+仪表板”

2. **配置仪表板**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **添加图形**
   - 拖放创建的图形
   - 以网格形式组织：
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **添加过滤器**（可选）
   - 点击“添加过滤器”
   - 过滤条件：国家/地区代码
   - 适用于所有图表

5. **保存仪表板**

---

## 步骤 8：检查完整的管道

### 端到端测试

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

### 添加新数据

1. **在PostgreSQL中插入新记录**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **触发Airbyte同步**
   - 打开Airbyte界面
   - 转到连接“PostgreSQL → MinIO”
   - 单击“立即同步”
   - 等待结局✅

3. **运行dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **刷新 Superset 仪表板**
   - 打开仪表板
   - 单击“刷新”按钮
   - 新数据应该出现 ✅

### 检查数据流

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

## 步骤 9：自动化管道

### 安排 Airbyte 同步

已配置为每 24 小时 02:00 运行一次。

编辑：
1. 在Airbyte中打开连接
2. 进入“设置”选项卡
3.更新“复制频率”
4. 保存

### 安排 dbt 执行

**选项 1：Cron 作业 (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**选项 2：Python 脚本**

**文件**：`scripts/run_pipeline.py`
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

### 使用 Docker Compose 进行调度

**文件**：`docker-compose.scheduler.yml`
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

## 后续步骤

恭喜！您已经构建了完整的端到端数据管道。 🎉

＃＃＃ 了解更多

1. **Airbyte Advanced** - [Airbyte 集成指南](../guides/airbyte-integration.md)
2. **Dremio 优化** - [Dremio 设置指南](../guides/dremio-setup.md)
3. **复杂的dbt模型** - [dbt开发指南](../guides/dbt-development.md)
4. **高级仪表板** - [Superset 仪表板指南](../guides/superset-dashboards.md)
5. **数据质量** - [数据质量指南](../guides/data-quality.md)

### 故障排除

如果您遇到问题，请参阅：
- [疑难解答指南](../guides/troubleshooting.md)
- [安装指南](installation.md#troubleshooting)
- [配置指南](configuration.md)

---

＃＃ 概括

您已成功：

- ✅ 访问平台的7项服务
- ✅ 配置 Airbyte 源 (PostgreSQL)
- ✅ 配置 Airbyte 目的地 (MinIO S3)
- ✅ 创建您的第一个 Airbyte 连接
- ✅ 将 Dremio 连接到 MinIO
- ✅ 创建 dbt 模板（登台 + 集市）
- ✅ 构建 Superset 仪表板
- ✅ 检查端到端数据流
- ✅ 自动化管道执行

**您的数据平台现已投入运行！** 🚀

---

**第一步指南版本**：3.2.0  
**最后更新**：2025-10-16  
**维护者**：数据平台团队