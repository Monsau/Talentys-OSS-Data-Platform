# Руководство по панелям мониторинга Apache Superset

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Язык**: французский

## Оглавление

1. [Обзор](#обзор)
2. [Первоначальная конфигурация](#initial-configuration)
3. [Подключение к источникам данных](#data-sources-connection)
4. [Создание графики](#graphics-creation)
5. [Создание информационной панели](#dashboard-construction)
6. [Расширенные функции](#advanced-features)
7. [Безопасность и разрешения](#security-and-permissions)
8. [Оптимизация производительности](# Performance-Optimization)
9. [Интеграция и обмен](#integration-and-sharing)
10. [Передовая практика](#передовая практика)

---

## Обзор

Apache Superset — это современное веб-приложение для бизнес-аналитики, готовое к использованию на предприятиях, которое позволяет пользователям исследовать и визуализировать данные с помощью интуитивно понятных информационных панелей и диаграмм.

### Ключевые особенности

| Особенность | Описание | Прибыль |
|----------------|---------|---------|
| **SQL IDE** | Интерактивный редактор SQL с автозаполнением | Специальный анализ |
| **Богатые визуализации** | Более 50 типов диаграмм | Различное представление данных |
| **Конструктор информационных панелей** | Перетащите интерфейс | Простое создание информационной панели |
| **Кэширование** | Кэшировать результаты запросов | Быстрое время загрузки |
| **Безопасность** | Безопасность на уровне строк, доступ на основе ролей | Управление данными |
| **Оповещения** | Автоматические уведомления по электронной почте/Slack | Проактивный мониторинг |

### Интеграция архитектуры

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

## Начальная конфигурация

### Первое подключение

Доступ к расширенному набору по `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Примечание по безопасности**: измените пароль по умолчанию сразу после первого входа в систему.

### Начальная настройка

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

### Файл конфигурации

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

## Источники данных подключения

### Войти в Дремио

#### Шаг 1. Установите драйвер базы данных Dremio

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Шаг 2. Добавьте базу данных Dremio

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Конфигурация**:
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

#### Шаг 3. Проверка соединения

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Подключение к PostgreSQL

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

### Подключение к Elasticsearch

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

## Создание графики

### Рабочий процесс создания графики

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

### Выбор графического типа

| Графический тип | Лучшее для | Пример использования |
|----------------|---------------|---------------------|
| **Линейная диаграмма** | Временные тенденции | Тенденция ежедневного дохода |
| **Гистограмма** | Сравнения | Доход по категориям продуктов |
| **Диаграмма секторов** | Доля от общего числа | Доля рынка по регионам |
| **Таблица** | Подробные данные | Список клиентов с показателями |
| **Большое количество** | Единая метрика | Общий доход с начала года |
| **Тепловая карта** | Обнаружение закономерностей | Продажи в день/час |
| **Облако точек** | Корреляции | Ценность клиента против частоты |
| **Диаграмма Сэнки** | Анализ потока | Путешествие пользователя |

### Пример: линейный график (тренд дохода)

#### Шаг 1. Создайте набор данных

```
Interface → Données → Datasets → + Dataset
```

**Конфигурация**:
- **База данных**: Дремио
- **Диаграмма**: Производство.Марки
- **Таблица**: mart_daily_revenue

#### Шаг 2. Создайте диаграмму

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Параметры**:
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

**Сгенерировано SQL**:
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

### Пример: гистограмма (основные клиенты)

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

### Пример: сводная таблица

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

### Пример: большое число с трендом

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

## Информационные панели строительства

### Процесс создания панели мониторинга

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

### Шаг 1. Создайте панель мониторинга

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Настройки панели управления**:
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

### Шаг 2. Добавьте графику

Перетащите графику с левой панели или создайте новую:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Шаг 3: Макет дизайна

**Система сетки**:
- 12 столбцов в ширину
- Графика привязана к сетке
- Проведите пальцем по экрану, чтобы изменить размер и положение.

**Пример макета**:
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

### Шаг 4. Добавьте фильтры панели мониторинга

```
Tableau de Bord → Éditer → + Filtre
```

**Фильтр диапазона дат**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Фильтр по категориям**:
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

**Цифровой фильтр**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Шаг 5. Перекрестная фильтрация

Включите перекрестную фильтрацию панели мониторинга:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Конфигурация**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Пользовательский опыт**:
- Нажмите на панель → отфильтровать всю панель инструментов.
- Нажмите на долю сектора → обновите соответствующую графику.
- Очистить фильтр → возвращается к виду по умолчанию.

---

## Расширенные функции

### Лаборатория SQL

Интерактивный редактор SQL для специальных запросов.

#### Выполнение запроса

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

**Функции**:
- Автозаполнение таблиц и столбцов
- История запросов
- Несколько вкладок
- Экспорт результатов (CSV, JSON)
- Сохранить запрос для повторного использования.

#### Создать таблицу из запроса (CTAS)

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

### Шаблоны Джинджа

Динамический SQL с шаблонами Jinja2:

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

**Переменные шаблона**:
- `{{ from_dttm }}` – Диапазон дат начала.
- `{{ to_dttm }}` – Конец диапазона дат.
- `{{ filter_values('column') }}` - Выбранные значения фильтра
- `{{ current_username }}` - Вошедший пользователь

### Оповещения и отчеты

#### Создать оповещение

```
Interface → Alertes & Rapports → + Alerte
```

**Конфигурация**:
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

#### Создать отчет

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

### Пользовательские плагины визуализации

Создайте пользовательские типы графики:

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

Сборка и установка:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Безопасность и разрешения

### Управление доступом на основе ролей (RBAC)

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

### Интегрированные роли

| Роль | Разрешения | Варианты использования |
|------|-------------|-------------|
| **Администратор** | Все разрешения | Системные администраторы |
| **Альфа** | Создание, редактирование, удаление информационных панелей/диаграмм | Аналитики данных |
| **Гамма** | Просмотр информационных панелей, выполнение запросов SQL Lab | Бизнес-пользователи |
| **sql_lab** | Только доступ к лаборатории SQL | Специалисты по данным |
| **Общедоступный** | Просмотр только общедоступных информационных панелей | Анонимные пользователи |

### Создать пользовательскую роль

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Пример: роль маркетингового аналитика**
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

### Безопасность линейного уровня (RLS)

Ограничить данные в соответствии с атрибутами пользователя:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Пример: RLS на основе региона**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Пример: клиентский RLS**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Безопасность подключения к базе данных

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

## Оптимизация производительности

### Кэширование запросов

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

**Стратегия кэширования**:
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

### Асинхронные запросы

Включите асинхронное выполнение запросов для длинных запросов:

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

### Оптимизация запросов к базе данных

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

### Оптимизация загрузки информационной панели

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

### Мониторинг производительности

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

## Интеграция и обмен

### Публичные информационные панели

Сделайте дашборды доступными без подключения:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**Общедоступный URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Интеграция Iframe

Интегрируйте информационные панели во внешние приложения:

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

**Настройки интеграции**:
- `standalone=1` - Скрыть навигацию
- `show_filters=0` - Скрыть панель фильтров.
- `show_title=0` - Скрыть заголовок информационной панели

### Аутентификация гостевого токена

Программный доступ к интегрированным информационным панелям:

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

### Экспорт информационных панелей

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Лучшие практики

### Дизайн информационной панели

1. **Иерархия макетов**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Постоянство цвета**
   - Используйте единую цветовую схему на всех информационных панелях.
   - Зеленый для положительных показателей, красный для отрицательных.
   - Фирменные цвета для категорий

3. **Производительность**
   - Ограничить графику на приборной панели (< 15)
   - Используйте соответствующие уровни агрегирования.
   - Включить кеш для статических данных.
   - Установите разумные пределы линий

4. **Интерактивность**
   - Добавьте содержательные фильтры
   - Включить перекрестную фильтрацию для исследования.
   - Обеспечить возможность детализации

### Выбор графики

| Тип данных | Рекомендуемые графики | Избегайте |
|--------------|----------------------------|--------|
| **Временной ряд** | Линейный, Площади | Секторы, Кольцо |
| **Сравнение** | Бары, Колонны | Линейный (несколько точек данных) |
| **Доля от общего числа** | Секторы, Кольцо, Древовидная карта | Бары (тоже категории) |
| **Распространение** | Гистограмма, коробчатая диаграмма | Секторы |
| **Корреляция** | Точки облаков, пузыри | Бары |
| **Географический** | Карта, картограмма | Стол |

### Оптимизация запросов

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

### Безопасность

1. **Контроль доступа**
   - Используйте RBAC для управления пользователями.
   - Внедрение RLS для изоляции данных.
   - Ограничить подключения к базе данных по роли.

2. **Управление данными**
   - Свойство наборов данных документа.
   - Определить графики обновления данных
   - Мониторинг производительности запросов

3. **Соответствие**
   - Скрыть личные данные в визуализациях
   - Аудит доступа к панели управления
   - Внедрить политику хранения данных.

---

## Краткое содержание

В этом подробном руководстве по суперсетам рассматриваются:

- **Конфигурация**: установка, настройка, подключение к базе данных.
- **Графика**: более 50 типов графики, конфигурация, генерация SQL.
– **Панели мониторинга**: дизайн макета, фильтры, перекрестная фильтрация.
- **Расширенные функции**: лаборатория SQL, шаблоны Jinja, оповещения, пользовательские плагины.
- **Безопасность**: RBAC, RLS, безопасность подключения к базе данных.
- **Производительность**: кеширование, асинхронные запросы, оптимизация запросов.
- **Интеграция**: общедоступные информационные панели, интеграция iframe, гостевые токены.
- **Передовая практика**: принципы дизайна, выбор графики, безопасность.

Ключевые моменты, которые следует запомнить:
- Superset подключается к Dremio для высокопроизводительной аналитики.
- Богатая библиотека визуализации поддерживает различные варианты использования.
- Встроенное кэширование и асинхронные запросы обеспечивают быструю работу информационных панелей.
- RBAC и RLS обеспечивают безопасную аналитику самообслуживания.
- Возможности интеграции обеспечивают интеграцию с внешними приложениями.

**Сопутствующая документация:**
- [Руководство по установке Dremio](./dremio-setup.md)
- [Архитектура: поток данных](../architecture/data-flow.md)
- [Учебное пособие по первым шагам](../getting-started/first-steps.md)
- [Руководство по качеству данных](./data-quality.md)

---

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.