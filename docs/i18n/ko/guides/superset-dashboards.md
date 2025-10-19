# Apache Superset 대시보드 가이드

**버전**: 3.2.0  
**최종 업데이트**: 2025년 10월 16일  
**언어**: 프랑스어

## 목차

1. [개요](#overview)
2. [초기 설정](#initial-configuration)
3. [데이터 소스 연결](#data-sources-connection)
4. [그래픽 생성](#graphics-creation)
5. [대시보드 구축](#dashboard-construction)
6. [고급 기능](#advanced-features)
7. [보안 및 권한](#security-and-permissions)
8. [성능 최적화](#performance-optimization)
9. [통합과 공유](#integration-and-sharing)
10. [모범 사례](#good-practices)

---

## 개요

Apache Superset은 사용자가 직관적인 대시보드와 차트를 통해 데이터를 탐색하고 시각화할 수 있는 현대적인 기업용 비즈니스 인텔리전스 웹 애플리케이션입니다.

### 주요 기능

| 기능 | 설명 | 이익 |
|---|---------|---------|
| **SQL IDE** | 자동 완성 기능이 있는 대화형 SQL 편집기 | 임시 분석 |
| **풍부한 시각화** | 50개 이상의 차트 유형 | 다양한 데이터 표현 |
| **대시보드 빌더** | 드래그 앤 드롭 인터페이스 | 간편한 대시보드 생성 |
| **캐싱** | 캐시 결과 쿼리 | 빠른 로딩 시간 |
| **보안** | 행 수준 보안, 역할 기반 액세스 | 데이터 거버넌스 |
| **경고** | 자동 이메일/Slack 알림 | 사전 모니터링 |

### 아키텍처 통합

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

## 초기 구성

### 첫 번째 연결

`http://localhost:8088`의 상위 집합에 액세스:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**보안 참고사항**: 처음 로그인한 후 즉시 기본 비밀번호를 변경하세요.

### 초기 설정

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

### 구성 파일

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

## 연결 데이터 소스

### 드레미오에 로그인하세요

#### 1단계: Dremio 데이터베이스 드라이버 설치

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### 2단계: Dremio 데이터베이스 추가

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**구성**:
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

#### 3단계: 연결 테스트

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### PostgreSQL에 연결

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

### Elasticsearch에 연결 중

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

## 그래픽 생성

### 그래픽 생성 작업흐름

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

### 선택 그래픽 유형

| 그래픽 유형 | 최고의 대상 | 사용 사례 예 |
|---|---------------|-------|
| **선형 차트** | 시간적 추세 | 일일소득 추이 |
| **막대형 차트** | 비교 | 제품 카테고리별 매출 |
| **섹터 차트** | 전체 비중 | 지역별 시장점유율 |
| **테이블** | 상세 데이터 | 측정항목이 포함된 고객 목록 |
| **큰 숫자** | 단일 측정항목 | 총 YTD 소득 |
| **히트 카드** | 패턴 감지 | 일별/시간별 매출 |
| **포인트 클라우드** | 상관관계 | 고객 가치와 빈도 |
| **생키 다이어그램** | 흐름 분석 | 사용자 여정 |

### 예: 선형 차트(소득 추세)

#### 1단계: 데이터 세트 생성

```
Interface → Données → Datasets → + Dataset
```

**구성**:
- **데이터베이스**: Dremio
- **다이어그램**: Production.Marts
- **테이블**: mart_daily_revenue

#### 2단계: 차트 만들기

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**매개변수**:
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

**SQL 생성**:
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

### 예: 막대 차트(상위 고객)

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

### 예: 피벗 테이블

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

### 예: 추세가 있는 큰 숫자

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

## 건설 대시보드

### 대시보드 생성 프로세스

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

### 1단계: 대시보드 만들기

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**대시보드 설정**:
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

### 2단계: 그래픽 추가

왼쪽 패널에서 그래픽을 드래그 앤 드롭하거나 새 그래픽을 만듭니다.

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### 3단계: 디자인 레이아웃

**그리드 시스템**:
- 너비 12열
- 그래픽이 그리드에 맞춰집니다.
- 스와이프하여 크기와 위치를 조정하세요.

**예시 레이아웃**:
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

### 4단계: 대시보드 필터 추가

```
Tableau de Bord → Éditer → + Filtre
```

**기간 필터**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**카테고리 필터**:
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

**디지털 필터**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### 5단계: 교차 필터링

대시보드 교차 필터링을 활성화합니다.

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**구성**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**사용자 경험**:
- 막대 클릭 → 전체 대시보드 필터링
- 섹터 공유 클릭 → 관련 그래픽 업데이트
- 필터 지우기 → 기본 보기로 재설정

---

## 고급 기능

### SQL 연구실

임시 쿼리를 위한 대화형 SQL 편집기입니다.

#### 쿼리 실행

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

**특징**:
- 테이블 및 열 자동 완성
- 요청 내역
- 여러 탭
- 결과 내보내기(CSV, JSON)
- 재사용을 위해 쿼리 저장

#### 쿼리에서 테이블 생성(CTAS)

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

### Jinja 템플릿

Jinja2 템플릿을 사용한 동적 SQL:

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

**템플릿 변수**:
- `{{ from_dttm }}` - 시작 기간
- `{{ to_dttm }}` - 기간 종료
- `{{ filter_values('column') }}` - 선택된 필터 값
- `{{ current_username }}` - 로그인한 사용자

### 경고 및 보고서

#### 알림 생성

```
Interface → Alertes & Rapports → + Alerte
```

**구성**:
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

#### 보고서 작성

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

### 사용자 정의 시각화 플러그인

사용자 정의 그래픽 유형 만들기:

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

빌드 및 설치:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## 보안 및 권한

### 역할 기반 액세스 제어(RBAC)

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

### 통합 역할

| 역할 | 권한 | 사용 사례 |
|------|-------------|-------------|
| **관리자** | 모든 권한 | 시스템 관리자 |
| **알파** | 대시보드/차트 생성, 편집, 삭제 | 데이터 분석가 |
| **감마** | 대시보드 보기, SQL Lab 쿼리 실행 | 비즈니스 사용자 |
| **sql_lab** | SQL Lab 액세스 전용 | 데이터 과학자 |
| **공개** | 공개 대시보드만 보기 | 익명 사용자 |

### 맞춤 역할 만들기

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**예: 마케팅 분석가 역할**
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

### 라인 레벨 안전(RLS)

사용자 속성에 따라 데이터를 제한합니다.

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**예: 지역 기반 RLS**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**예: 클라이언트 기반 RLS**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### 데이터베이스 연결 보안

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

## 성능 최적화

### 캐싱 쿼리

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

**캐시 전략**:
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

### 비동기 요청

긴 쿼리에 대해 비동기 쿼리 실행을 활성화합니다.

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

### 데이터베이스 쿼리 최적화

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

### 대시보드 로딩 최적화

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

### 성능 모니터링

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

## 통합 및 공유

### 공개 대시보드

연결 없이 대시보드에 액세스할 수 있도록 설정:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**공개 URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### 아이프레임 통합

대시보드를 외부 애플리케이션에 통합합니다.

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

**통합 설정**:
- `standalone=1` - 탐색 숨기기
- `show_filters=0` - 필터 패널 숨기기
- `show_title=0` - 대시보드 제목 숨기기

### 게스트 토큰 인증

통합 대시보드에 대한 프로그래밍 방식 액세스:

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

### 대시보드 내보내기

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## 모범 사례

### 대시보드 디자인

1. **레이아웃 계층구조**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **색상 일관성**
   - 모든 대시보드에서 일관된 색상 구성표 사용
   - 긍정적인 지표는 녹색, 부정적인 지표는 빨간색
   - 카테고리별 브랜드 색상

3. **성능**
   - 대시보드당 그래픽 제한(< 15)
   - 적절한 집계 수준을 사용하십시오.
   - 정적 데이터에 대한 캐시 활성화
   - 합리적인 회선 제한 설정

4. **상호작용**
   - 의미 있는 필터 추가
   - 탐색을 위한 교차 필터링 활성화
   - 드릴다운 기능 제공

### 그래픽 선택

| 데이터 유형 | 추천 차트 | 피하십시오 |
|---------------|---------------|-------|
| **시계열** | 선형, 영역 | 섹터, 링 |
| **비교** | 바, 기둥 | 선형(데이터 포인트가 적음) |
| **전체 비중** | 섹터, 링, 트리맵 | 바(카테고리도 포함) |
| **배포** | 히스토그램, 상자 그림 | 분야 |
| **상관관계** | 클라우드 포인트, 버블 | 바 |
| **지리적** | 지도, 등치 | 테이블 |

### 쿼리 최적화

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

### 보안

1. **액세스 제어**
   - 사용자 관리를 위해 RBAC를 사용합니다.
   - 데이터 격리를 위한 RLS 구현
   - 역할별로 데이터베이스 연결을 제한합니다.

2. **데이터 거버넌스**
   - 문서 데이터 세트 속성
   - 데이터 새로 고침 일정 정의
   - 쿼리 성능 모니터링

3. **규정 준수**
   - 시각화에서 PII 숨기기
   - 대시보드 액세스 감사
   - 데이터 보존 정책 구현

---

## 요약

이 포괄적인 슈퍼세트 가이드에서는 다음 내용을 다뤘습니다.

- **구성**: 설치, 구성, 데이터베이스 연결
- **그래픽**: 50개 이상의 그래픽 유형, 구성, SQL 생성
- **대시보드**: 레이아웃 디자인, 필터, 교차 필터링
- **고급 기능**: SQL Lab, Jinja 템플릿, 경고, 사용자 정의 플러그인
- **보안**: RBAC, RLS, 데이터베이스 연결 보안
- **성능**: 캐싱, 비동기 쿼리, 쿼리 최적화
- **통합**: 공개 대시보드, iframe 통합, 게스트 토큰
- **모범 사례**: 디자인 원칙, 그래픽 선택, 보안

기억해야 할 핵심 사항:
- Superset은 고성능 분석을 위해 Dremio에 연결됩니다.
- 풍부한 시각화 라이브러리는 다양한 사용 사례를 지원합니다.
- 내장된 캐싱 및 비동기 쿼리로 빠른 대시보드 보장
- RBAC 및 RLS를 통해 안전한 셀프 서비스 분석 가능
- 통합 기능으로 외부 애플리케이션과의 통합 가능

**관련 문서:**
- [Dremio 설정 가이드](./dremio-setup.md)
- [아키텍처: 데이터 흐름](../architecture/data-flow.md)
- [첫 번째 단계 튜토리얼](../getting-started/first-steps.md)
- [데이터 품질 가이드](./data-quality.md)

---

**버전**: 3.2.0  
**최종 업데이트**: 2025년 10월 16일