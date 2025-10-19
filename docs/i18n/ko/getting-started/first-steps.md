# 데이터 플랫폼 시작하기

**버전**: 3.2.0  
**최종 업데이트**: 2025-10-16  
**언어**: 프랑스어

---

## 개요

이 튜토리얼에서는 서비스 연결부터 Airbyte, Dremio, dbt 및 Superset을 사용한 첫 번째 데이터 파이프라인 구축에 이르기까지 데이터 플랫폼과의 첫 번째 상호 작용을 안내합니다.

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

**예상 시간**: 60~90분

---

## 전제 조건

시작하기 전에 다음 사항을 확인하세요.

- ✅ 모든 서비스가 설치되어 실행 중입니다.
- ✅ 웹 인터페이스에 액세스할 수 있습니다
- ✅ Python 가상 환경이 활성화되었습니다.
- ✅ SQL에 대한 기본 이해

**서비스가 작동하는지 확인하세요.**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## 1단계: 모든 서비스에 액세스

### 서비스 URL

| 서비스 | URL | 기본 자격 증명 |
|---------|----------|------------|
| **에어바이트** | http://localhost:8000 | airbyte@example.com / 비밀번호 |
| **드레미오** | http://localhost:9047 | 관리자/admin123 |
| **슈퍼세트** | http://localhost:8088 | 관리자 / 관리자 |
| **미니IO** | http://localhost:9001 | minioadmin / minioadmin123 |

### 첫 번째 연결

**에어바이트:**
1. http://localhost:8000을 엽니다.
2. 설정 마법사 완료
3. 워크스페이스 이름을 '프로덕션'으로 설정합니다.
4. 기본 설정 재정의(나중에 구성 가능)

**드레미오:**
1. http://localhost:9047을 엽니다.
2. 처음 액세스할 때 관리자를 생성합니다.
   - 사용자 이름: `admin`
   - 이메일: `admin@example.com`
   - 비밀번호 : `admin123`
3. “시작하기”를 클릭하세요

**상위 집합:**
1. http://localhost:8088을 엽니다.
2. 기본 자격 증명으로 로그인
3. 비밀번호 변경 : 설정 → 사용자 정보 → 비밀번호 재설정

---

## 2단계: Airbyte에서 첫 번째 데이터 소스 구성

### PostgreSQL 소스 생성

**시나리오**: PostgreSQL 데이터베이스에서 데이터를 추출합니다.

1. **소스로 이동**
   - 왼쪽 메뉴에서 '소스'를 클릭하세요.
   - '+ 새 소스'를 클릭하세요.

2. **PostgreSQL 선택**
   - “PostgreSQL”을 검색하세요.
   - “PostgreSQL” 커넥터를 클릭하세요.

3. **연결 구성**
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

4. **테스트 및 저장**
   - '소스 설정'을 클릭하세요.
   - 연결 테스트를 기다립니다.
   - 소스가 생성되었습니다 ✅

### 샘플 데이터 생성(선택 사항)

아직 데이터가 없으면 예제 테이블을 만듭니다.

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

## 3단계: MinIO S3 대상 구성

### 목적지 만들기

1. **목적지 탐색**
   - 왼쪽 메뉴에서 '목적지'를 클릭하세요.
   - '+ 새 목적지'를 클릭하세요.

2. **S3 선택**
   - “S3”를 검색하세요.
   - “S3” 커넥터를 클릭하세요.

3. **MinIO를 S3으로 구성**
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

4. **테스트 및 저장**
   - '목적지 설정'을 클릭하세요.
   - 연결 테스트를 통과해야 합니다 ✅

---

## 4단계: 첫 번째 연결 만들기

### 소스를 대상으로 링크

1. **연결로 이동**
   - 왼쪽 메뉴에서 '연결'을 클릭하세요.
   - '+ 새 연결'을 클릭하세요.

2. **소스 선택**
   - "PostgreSQL 프로덕션"을 선택합니다.
   - '기존 소스 사용'을 클릭하세요.

3. **목적지 선택**
   - "MinIO 데이터 레이크"를 선택하세요.
   - '기존 대상 사용'을 클릭하세요.

4. **동기화 구성**
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

5. **정규화**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **백업 및 동기화**
   - '연결 설정'을 클릭하세요.
   - 첫 번째 동기화를 실행하려면 "지금 동기화"를 클릭하세요.
   - 동기화 진행 상황 모니터링

### 모니터 동기화

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

**동기화 상태 확인:**
- 상태가 "성공"(녹색)으로 표시되어야 합니다.
- 동기화 기록 : ~11개 (고객 5명 + 주문 6명)
- 자세한 내용은 로그를 참조하세요.

---

## 5단계: Dremio를 MinIO에 연결

### Dremio에 S3 소스 추가

1. **소스로 이동**
   - http://localhost:9047을 엽니다.
   - “소스 추가”(+ 아이콘)를 클릭하세요.

2. **S3 선택**
   - "아마존 S3"를 선택하세요
   - MinIO로 구성:

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

3. **테스트 및 저장**
   - '저장'을 클릭하세요.
   - Dremio는 MinIO 버킷을 분석합니다.

### 데이터 찾아보기

1. **MinIOLake 소스로 이동**
   - “MinIOLake” 개발
   - "데이터레이크" 버킷 개발
   - "원시 데이터" 폴더를 확장합니다.
   - "production_public" 폴더를 확인하세요.

2. **미리보기 데이터**
   - '고객' 폴더를 클릭하세요.
   - Parquet 파일을 클릭하세요.
   - '미리보기'를 클릭하면 데이터를 볼 수 있습니다.
   - 데이터는 PostgreSQL과 일치해야 합니다 ✅

### 가상 데이터세트 생성

1. **데이터 쿼리**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **VDS로 저장**
   - '다른 이름으로 보기 저장'을 클릭하세요.
   - 이름 : `vw_customers`
   - 공간: `@admin` (당신의 공간)
   - '저장'을 클릭하세요.

3. **데이터 형식**(선택 사항)
   - `vw_customers`을 클릭하세요.
   - 인터페이스를 사용하여 열 이름 바꾸기, 유형 변경
   - 예: `customer_id`의 이름을 `id`로 변경합니다.

---

## 6단계: DBT 템플릿 생성

### dbt 프로젝트 초기화

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

### 소스 정의 생성

**파일**: `dbt/models/sources.yml`

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

### 스테이징 템플릿 만들기

**파일**: `dbt/models/staging/stg_customers.sql`

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

**파일**: `dbt/models/staging/stg_orders.sql`

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

### 마트 템플릿 만들기

**파일**: `dbt/models/marts/fct_customer_orders.sql`

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

### dbt 모델 실행

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

### 드레미오 체크인

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## 7단계: Superset에서 대시보드 만들기

### Dremio 데이터베이스 추가

1. **데이터베이스로 이동**
   - http://localhost:8088을 엽니다.
   - “데이터” → “데이터베이스”를 클릭하세요.
   - "+ 데이터베이스"를 클릭하세요.

2. **드레미오 선택**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **“연결”을 클릭하세요**

### 데이터 세트 만들기

1. **데이터세트로 이동**
   - “데이터” → “데이터세트”를 클릭하세요.
   - '+ 데이터세트'를 클릭하세요.

2. **데이터 세트 구성**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **“데이터 세트 생성 및 차트 생성”을 클릭하세요**

### 차트 만들기

#### 차트 1: 고객 세그먼트(원형 다이어그램)

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

#### 차트 2: 국가별 소득(막대 차트)

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

#### 차트 3: 고객 지표(큰 숫자)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### 대시보드 만들기

1. **대시보드로 이동**
   - '대시보드'를 클릭하세요.
   - '+ 대시보드'를 클릭하세요.

2. **대시보드 구성**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **그래픽 추가**
   - 생성된 그래픽을 드래그 앤 드롭하세요.
   - 그리드로 구성:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **필터 추가**(선택 사항)
   - '필터 추가'를 클릭하세요.
   - 필터링 기준: 국가 코드
   - 모든 차트에 적용

5. **대시보드 저장**

---

## 8단계: 전체 파이프라인 확인

### 엔드투엔드 테스트

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

### 새 데이터 추가

1. **PostgreSQL에 새 레코드 삽입**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Airbyte 동기화 실행**
   - Airbyte 인터페이스를 엽니다.
   - "PostgreSQL → MinIO" 연결로 이동합니다.
   - '지금 동기화'를 클릭하세요.
   - 끝까지 기다려주세요✅

3. **dbt 실행**
   ```bash
   cd dbt
   dbt run
   ```

4. **상위 집합 대시보드 새로 고침**
   - 대시보드를 엽니다.
   - '새로고침' 버튼을 클릭하세요.
   - 새로운 데이터가 나타나야 합니다 ✅

### 데이터 흐름 확인

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

## 9단계: 파이프라인 자동화

### Airbyte 동기화 예약

이미 24시간마다 02:00에 실행되도록 구성되어 있습니다.

편집하려면:
1. Airbyte에서 연결 열기
2. '설정' 탭으로 이동하세요.
3. “복제 빈도” 업데이트
4. 저장

### dbt 실행 예약

**옵션 1: 크론 작업(Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**옵션 2: Python 스크립트**

**파일**: `scripts/run_pipeline.py`
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

### Docker Compose로 일정 예약

**파일**: `docker-compose.scheduler.yml`
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

## 다음 단계

축하해요! 완전한 엔드투엔드 데이터 파이프라인을 구축했습니다. 🎉

### 자세히 알아보기

1. **Airbyte Advanced** - [Airbyte 통합 가이드](../guides/airbyte-integration.md)
2. **Dremio 최적화** - [Dremio 설정 가이드](../guides/dremio-setup.md)
3. **복잡한 DBT 모델** - [dbt 개발 가이드](../guides/dbt-development.md)
4. **고급 대시보드** - [상위 대시보드 가이드](../guides/superset-dashboards.md)
5. **데이터 품질** - [데이터 품질 가이드](../guides/data-quality.md)

### 문제 해결

문제가 있는 경우 다음을 참조하세요.
- [문제해결 가이드](../guides/troubleshooting.md)
- [설치 가이드](installation.md#troubleshooting)
- [구성 가이드](configuration.md)

---

## 요약

당신은 성공적으로:

- ✅ 플랫폼의 7가지 서비스에 액세스하세요
- ✅ Airbyte 소스 구성(PostgreSQL)
- ✅ Airbyte 대상 구성(MinIO S3)
- ✅ 첫 번째 Airbyte 연결 생성
- ✅ Dremio를 MinIO에 연결
- ✅ DBT 템플릿 생성(스테이징 + 마트)
- ✅ 상위 집합 대시보드 구축
- ✅ 엔드투엔드 데이터 흐름 확인
- ✅ 파이프라인 실행 자동화

**귀하의 데이터 플랫폼이 이제 작동 중입니다!** 🚀

---

**첫 번째 단계 가이드 버전**: 3.2.0  
**최종 업데이트**: 2025-10-16  
**관리자**: 데이터 플랫폼 팀