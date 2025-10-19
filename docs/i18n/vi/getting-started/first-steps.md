# Bắt đầu với Nền tảng dữ liệu

**Phiên bản**: 3.2.0  
**Cập nhật lần cuối**: 2025-10-16  
**Ngôn ngữ**: Tiếng Pháp

---

## Tổng quan

Hướng dẫn này hướng dẫn bạn các tương tác đầu tiên với nền tảng dữ liệu, từ kết nối với các dịch vụ đến xây dựng đường dẫn dữ liệu đầu tiên của bạn với Airbyte, Dremio, dbt và Superset.

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

**Thời gian dự kiến**: 60-90 phút

---

## Điều kiện tiên quyết

Trước khi bạn bắt đầu, hãy đảm bảo rằng:

- ✅ Tất cả các dịch vụ đã được cài đặt và chạy
- ✅ Bạn có thể truy cập vào giao diện web
- ✅ Môi trường ảo Python được kích hoạt
- ✅ Hiểu biết cơ bản về SQL

**Kiểm tra xem các dịch vụ có hoạt động không:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Bước 1: Truy cập tất cả dịch vụ

### URL dịch vụ

| Dịch vụ | URL | Thông tin xác thực mặc định |
|----------|----------|---------------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / mật khẩu |
| **Dremio** | http://localhost:9047 | quản trị viên/admin123 |
| **Siêu bộ** | http://localhost:8088 | quản trị viên / quản trị viên |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### Kết nối đầu tiên

**Airbyte:**
1. Mở http://localhost:8000
2. Hoàn tất trình hướng dẫn thiết lập
3. Đặt tên không gian làm việc: “Sản xuất”
4. Ghi đè tùy chọn (có thể cấu hình sau)

**Dremio:**
1. Mở http://localhost:9047
2. Tạo người dùng quản trị viên trong lần truy cập đầu tiên:
   - Tên người dùng: `admin`
   - Email: `admin@example.com`
   - Mật khẩu: `admin123`
3. Nhấp vào “Bắt đầu”

**Siêu bộ:**
1. Mở http://localhost:8088
2. Đăng nhập bằng thông tin đăng nhập mặc định
3. Thay đổi mật khẩu: Cài đặt → Thông tin người dùng → Đặt lại mật khẩu

---

## Bước 2: Định cấu hình nguồn dữ liệu đầu tiên của bạn trong Airbyte

### Tạo nguồn PostgreSQL

**Kịch bản**: Trích xuất dữ liệu từ cơ sở dữ liệu PostgreSQL.

1. **Điều hướng đến Nguồn**
   - Nhấp vào “Nguồn” ở menu bên trái
   - Bấm vào “+ Nguồn mới”

2. **Chọn PostgreSQL**
   - Tìm kiếm “PostgreSQL”
   - Nhấp vào trình kết nối “PostgreSQL”

3. **Định cấu hình kết nối**
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

4. **Kiểm tra và lưu**
   - Click vào “Thiết lập nguồn”
   - Chờ kiểm tra kết nối
   - Nguồn được tạo ✅

### Tạo dữ liệu mẫu (Tùy chọn)

Nếu bạn chưa có dữ liệu nào, hãy tạo các bảng ví dụ:

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

## Bước 3: Cấu hình đích MiniIO S3

### Tạo điểm đến

1. **Điều hướng đến các điểm đến**
   - Bấm vào “Điểm đến” ở menu bên trái
   - Click vào “+ Điểm đến mới”

2. **Chọn S3**
   - Tìm kiếm “S3”
   - Nhấp vào đầu nối “S3”

3. **Định cấu hình MinIO là S3**
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

4. **Kiểm tra và lưu**
   - Bấm vào “Thiết lập điểm đến”
   - Kiểm tra kết nối phải đạt ✅

---

## Bước 4: Tạo kết nối đầu tiên của bạn

### Liên kết nguồn tới đích

1. **Điều hướng đến Kết nối**
   - Nhấp vào “Kết nối” ở menu bên trái
   - Bấm vào “+Kết nối mới”

2. **Chọn nguồn**
   - Chọn “Sản xuất PostgreSQL”
   - Bấm vào “Sử dụng nguồn hiện có”

3. **Chọn Điểm đến**
   - Chọn “Hồ dữ liệu MinIO”
   - Nhấp vào “Sử dụng điểm đến hiện tại”

4. **Cấu hình đồng bộ hóa**
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

5. **Bình thường hóa**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Sao lưu và đồng bộ hóa**
   - Click vào “Thiết lập kết nối”
   - Bấm vào “Đồng bộ ngay” để thực hiện đồng bộ lần đầu
   - Theo dõi tiến trình đồng bộ hóa

### Đồng bộ hóa màn hình

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

**Kiểm tra trạng thái đồng bộ hóa:**
- Trạng thái sẽ hiển thị “Thành công” (màu xanh lá cây)
- Hồ sơ đồng bộ: ~11 (5 khách hàng + 6 đơn hàng)
- Xem nhật ký để biết chi tiết

---

## Bước 5: Kết nối Dremio với MinIO

### Thêm nguồn S3 vào Dremio

1. **Điều hướng đến Nguồn**
   - Mở http://localhost:9047
   - Nhấp vào “Thêm nguồn” (+ biểu tượng)

2. **Chọn S3**
   - Chọn “Amazon S3”
   - Cấu hình làm MinIO:

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

3. **Kiểm tra và lưu**
   - Click vào “Lưu”
   - Dremio sẽ phân tích các nhóm MiniIO

### Duyệt dữ liệu

1. **Điều hướng đến nguồn MinIOlake**
   - Phát triển “MinIOlake”
   - Phát triển nhóm "datalake"
   - Mở rộng thư mục "raw-data"
   - Xem thư mục “production_public”

2. **Dữ liệu xem trước**
   - Click vào thư mục “khách hàng”
   - Click vào file Parquet
   - Click vào “Preview” để xem dữ liệu
   - Dữ liệu phải khớp với PostgreSQL ✅

### Tạo bộ dữ liệu ảo

1. **Dữ liệu truy vấn**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Lưu dưới dạng VDS**
   - Bấm vào “Lưu dạng xem dưới dạng”
   - Tên: `vw_customers`
   - Không gian: `@admin` (không gian của bạn)
   - Click vào “Lưu”

3. **Định dạng dữ liệu** (tùy chọn)
   - Bấm vào `vw_customers`
   - Sử dụng giao diện đổi tên cột, đổi loại
   - Ví dụ: Đổi tên `customer_id` thành `id`

---

## Bước 6: Tạo mẫu dbt

### Khởi tạo dự án dbt

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

### Tạo định nghĩa nguồn

**Tệp**: `dbt/models/sources.yml`

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

### Tạo mẫu dàn dựng

**Tệp**: `dbt/models/staging/stg_customers.sql`

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

**Tệp**: `dbt/models/staging/stg_orders.sql`

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

### Tạo mẫu Mart

**Tệp**: `dbt/models/marts/fct_customer_orders.sql`

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

### Chạy mô hình dbt

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

### Đăng ký tại Dremio

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Bước 7: Tạo Dashboard trong Superset

### Thêm cơ sở dữ liệu Dremio

1. **Điều hướng đến Cơ sở dữ liệu**
   - Mở http://localhost:8088
   - Bấm vào “Dữ liệu” → “Cơ sở dữ liệu”
   - Bấm vào “+ Cơ sở dữ liệu”

2. **Chọn Dremio**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **Nhấp vào “Kết nối”**

### Tạo tập dữ liệu

1. **Điều hướng đến Bộ dữ liệu**
   - Bấm vào “Dữ liệu” → “Bộ dữ liệu”
   - Bấm vào “+Bộ dữ liệu”

2. **Định cấu hình Bộ dữ liệu**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Nhấp vào “Tạo tập dữ liệu và tạo biểu đồ”**

### Tạo biểu đồ

#### Biểu đồ 1: Phân khúc khách hàng (Sơ đồ tròn)

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

#### Biểu đồ 2: Thu nhập theo quốc gia (Biểu đồ thanh)

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

#### Biểu đồ 3: Chỉ số khách hàng (Số lượng lớn)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Tạo Bảng điều khiển

1. **Điều hướng đến Trang tổng quan**
   - Bấm vào “Bảng điều khiển”
   - Bấm vào “+ Bảng điều khiển”

2. **Định cấu hình Trang tổng quan**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Thêm đồ họa**
   - Kéo và thả đồ họa đã tạo
   - Tổ chức theo dạng lưới:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Thêm bộ lọc** (tùy chọn)
   - Bấm vào “Thêm bộ lọc”
   - Lọc theo: country_code
   - Áp dụng cho tất cả các biểu đồ

5. **Lưu bảng điều khiển**

---

## Bước 8: Kiểm tra đường ống hoàn chỉnh

### Thử nghiệm từ đầu đến cuối

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

### Thêm dữ liệu mới

1. **Chèn bản ghi mới vào PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Kích hoạt đồng bộ hóa Airbyte**
   - Mở giao diện Airbyte
   - Vào kết nối “PostgreSQL → MinIO”
   - Bấm vào “Đồng bộ ngay”
   - Đợi đến cuối ✅

3. **Chạy dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **Làm mới Bảng điều khiển Superset**
   - Mở bảng điều khiển
   - Bấm vào nút “Làm mới”
   - Dữ liệu mới sẽ xuất hiện ✅

### Kiểm tra luồng dữ liệu

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

## Bước 9: Tự động hóa Pipeline

### Lên lịch đồng bộ hóa Airbyte

Đã được cấu hình để chạy 24 giờ một lần vào lúc 02:00.

Để chỉnh sửa:
1. Mở kết nối trong Airbyte
2. Chuyển đến tab “Cài đặt”
3. Cập nhật “Tần suất sao chép”
4. Lưu

### Lên lịch thực thi dbt

**Tùy chọn 1: Công việc định kỳ (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Tùy chọn 2: Tập lệnh Python**

**Tệp**: `scripts/run_pipeline.py`
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

### Lên lịch với Docker Compose

**Tệp**: `docker-compose.scheduler.yml`
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

## Các bước tiếp theo

Chúc mừng! Bạn đã xây dựng một đường dẫn dữ liệu hoàn chỉnh từ đầu đến cuối. 🎉

### Tìm hiểu thêm

1. **Airbyte Advanced** - [Hướng dẫn tích hợp Airbyte](../guides/airbyte-integration.md)
2. **Tối ưu hóa Dremio** - [Hướng dẫn thiết lập Dremio](../guides/dremio-setup.md)
3. **Mô hình dbt phức tạp** - [Hướng dẫn phát triển dbt](../guides/dbt-development.md)
4. **Trang tổng quan nâng cao** - [Hướng dẫn bảng điều khiển Superset](../guides/superset-dashboards.md)
5. **Chất lượng dữ liệu** - [Hướng dẫn về chất lượng dữ liệu](../guides/data-quality.md)

### Khắc phục sự cố

Nếu bạn gặp vấn đề, hãy xem:
- [Hướng dẫn khắc phục sự cố](../guides/troubleshooting.md)
- [Hướng dẫn cài đặt](installation.md#troubleshooting)
- [Hướng dẫn cấu hình](configuration.md)

---

## Bản tóm tắt

Bạn đã thành công:

- ✅ Truy cập 7 dịch vụ của nền tảng
- ✅ Cấu hình nguồn Airbyte (PostgreSQL)
- ✅ Định cấu hình đích Airbyte (MinIO S3)
- ✅ Tạo kết nối Airbyte đầu tiên của bạn
- ✅ Kết nối Dremio với MiniIO
- ✅ Tạo mẫu dbt (staging + mart)
- ✅ Xây dựng Bảng điều khiển Superset
- ✅ Kiểm tra luồng dữ liệu từ đầu đến cuối
- ✅ Tự động thực hiện đường ống

**Nền tảng dữ liệu của bạn hiện đang hoạt động!** 🚀

---

**Phiên bản hướng dẫn các bước đầu tiên**: 3.2.0  
**Cập nhật lần cuối**: 2025-10-16  
**Được duy trì bởi**: Nhóm nền tảng dữ liệu