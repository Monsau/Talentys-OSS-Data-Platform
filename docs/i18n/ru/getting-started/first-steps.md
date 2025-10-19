# Начало работы с платформой данных

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Язык**: французский

---

## Обзор

В этом руководстве вы познакомитесь с первыми взаимодействиями с платформой данных: от подключения к сервисам до создания первого конвейера данных с помощью Airbyte, Dremio, dbt и Superset.

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

**Расчетное время**: 60–90 минут.

---

## Предварительные условия

Прежде чем начать, убедитесь, что:

- ✅Все сервисы установлены и работают
- ✅ Вы можете получить доступ к веб-интерфейсам
- ✅ Виртуальная среда Python включена
- ✅ Базовое понимание SQL

**Проверьте, что службы работают:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## Шаг 1: доступ ко всем услугам

### URL-адреса служб

| Услуги | URL-адрес | Учетные данные по умолчанию |
|---------|----------|------------------------|
| **Эйрбайт** | http://локальный хост:8000 | airbyte@example.com / пароль |
| **Дремио** | http://локальный хост:9047 | админ/admin123 |
| **Суперсет** | http://локальный хост:8088 | админ / админ |
| **МиНИО** | http://локальный хост:9001 | миниоадмин / minioadmin123 |

### Первое подключение

**Эйрбайт:**
1. Откройте http://localhost:8000.
2. Завершите работу мастера установки.
3. Установите имя рабочей области: «Производство».
4. Переопределить настройки (возможна более поздняя настройка)

**Дремио:**
1. Откройте http://localhost:9047.
2. Создайте пользователя-администратора при первом доступе:
   - Имя пользователя: `admin`
   - Электронная почта: `admin@example.com`.
   - Пароль: `admin123`
3. Нажмите «Начать».

**Суперсет:**
1. Откройте http://localhost:8088.
2. Войдите в систему с учетными данными по умолчанию.
3. Измените пароль: Настройки → Информация о пользователе → Сбросить пароль.

---

## Шаг 2. Настройте свой первый источник данных в Airbyte

### Создайте исходный код PostgreSQL

**Сценарий**: Извлечение данных из базы данных PostgreSQL.

1. **Перейдите к «Источникам»**
   - Нажмите «Источники» в левом меню.
   - Нажмите «+ Новый источник»

2. **Выберите PostgreSQL**
   - Найдите «PostgreSQL».
   - Нажмите на соединитель «PostgreSQL».

3. **Настроить соединение**
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

4. **Протестируйте и сохраните**
   - Нажмите «Настроить источник».
   - Дождитесь проверки соединения
   - Исходник создан ✅

### Создать образец данных (необязательно)

Если у вас еще нет данных, создайте примеры таблиц:

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

## Шаг 3. Настройте назначение MinIO S3

### Создайте пункт назначения

1. **Перейдите к пунктам назначения**
   - Нажмите «Направления» в левом меню.
   - Нажмите «+ Новое направление»

2. **Выберите S3**
   - Найдите «S3»
   - Нажмите на разъем «S3».

3. **Настройте MinIO как S3**
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

4. **Протестируйте и сохраните**
   - Нажмите «Настроить пункт назначения».
   - Тест соединения должен пройти ✅

---

## Шаг 4: Создайте первое соединение

### Ссылка источника на место назначения

1. **Перейдите к разделу «Соединения»**.
   - Нажмите «Подключения» в левом меню.
   - Нажмите на «+ Новое подключение»

2. **Выберите источник**
   - Выберите «Производство PostgreSQL».
   - Нажмите «Использовать существующий источник».

3. **Выберите пункт назначения**
   - Выберите «Озеро данных MinIO».
   - Нажмите «Использовать существующий пункт назначения».

4. **Настроить синхронизацию**
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

5. **Нормализация**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **Резервное копирование и синхронизация**
   - Нажмите «Настроить соединение».
   - Нажмите «Синхронизировать сейчас», чтобы выполнить первую синхронизацию.
   - Отслеживание хода синхронизации

### Синхронизация монитора

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

**Проверьте статус синхронизации:**
- Статус должен показывать «Успешно» (зеленый).
- Синхронизированных записей: ~11 (5 клиентов + 6 заказов)
- Подробности смотрите в журналах.

---

## Шаг 5: Подключите Dremio к MinIO

### Добавьте источник S3 в Dremio

1. **Перейдите к «Источникам»**
   - Откройте http://localhost:9047.
   - Нажмите «Добавить источник» (значок +)

2. **Выберите S3**
   - Выберите «Амазон S3»
   - Настроить как MinIO:

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

3. **Проверьте и сохраните**
   - Нажмите «Сохранить»
   - Dremio проанализирует сегменты MinIO.

### Просмотр данных

1. **Перейдите к исходному коду MinIOLake**
   - Разработка «MinIOLake»
   - Разработать сегмент «datalake».
   - Разверните папку «сырые данные».
   - См. папку «production_public».

2. **Предварительный просмотр данных**
   - Нажмите на папку «клиенты».
   - Нажмите на файл паркета.
   - Нажмите «Предварительный просмотр», чтобы просмотреть данные.
   - Данные должны соответствовать PostgreSQL ✅

### Создайте виртуальный набор данных

1. **Данные запроса**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **Сохранить как VDS**
   - Нажмите «Сохранить вид как».
   - Имя: `vw_customers`
   - Пробел: `@admin` (ваш пробел)
   - Нажмите «Сохранить»

3. **Форматировать данные** (необязательно).
   - Нажмите `vw_customers`.
   - Используйте интерфейс для переименования столбцов, изменения типов
   - Пример: переименуйте `customer_id` в `id`.

---

## Шаг 6: Создание шаблонов dbt

### Инициализируем проект dbt

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

### Создать определение источника

**Файл**: `dbt/models/sources.yml`

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

### Создание промежуточного шаблона

**Файл**: `dbt/models/staging/stg_customers.sql`

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

**Файл**: `dbt/models/staging/stg_orders.sql`

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

### Создайте шаблон витрины

**Файл**: `dbt/models/marts/fct_customer_orders.sql`

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

### Запуск моделей dbt

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

### Зарегистрируйтесь в Дремио

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## Шаг 7. Создайте панель мониторинга в Superset

### Добавить базу данных Dremio

1. **Перейдите к базам данных**
   - Откройте http://localhost:8088.
   - Нажмите «Данные» → «Базы данных»
   - Нажмите «+ База данных»

2. **Выберите Дремио**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **Нажмите «Подключиться»**.

### Создайте набор данных

1. **Перейдите к наборам данных**
   - Нажмите «Данные» → «Наборы данных».
   - Нажмите «+ Набор данных».

2. **Настройте набор данных**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **Нажмите «Создать набор данных и создать диаграмму»**.

### Создание диаграмм

#### Диаграмма 1: Сегменты клиентов (круговая диаграмма)

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

#### Диаграмма 2: Доходы по странам (столбчатая диаграмма)

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

#### Диаграмма 3. Показатели клиентов (большое число)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### Создайте панель мониторинга

1. **Перейдите к панелям мониторинга**
   - Нажмите «Панели мониторинга».
   - Нажмите «+ Панель управления»

2. **Настройте панель управления**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **Добавить графику**
   - Перетащите созданную графику
   - Организуйте в сетке:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **Добавить фильтры** (необязательно).
   - Нажмите «Добавить фильтр».
   - Фильтровать по: код_страны
   - Применить ко всем диаграммам

5. **Сохраните панель**

---

## Шаг 8. Проверьте весь конвейер

### Сквозное тестирование

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

### Добавить новые данные

1. **Вставьте новые записи в PostgreSQL**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **Запустить синхронизацию Airbyte**
   - Откройте интерфейс Airbyte
   - Заходим в соединение «PostgreSQL → MinIO»
   - Нажмите «Синхронизировать сейчас».
   - Дождитесь конца ✅

3. **Запустите dbt**
   ```bash
   cd dbt
   dbt run
   ```

4. **Обновите панель мониторинга Superset**.
   - Откройте панель управления
   - Нажмите кнопку «Обновить».
   - Должны появиться новые данные ✅

### Проверка потока данных

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

## Шаг 9. Автоматизируйте конвейер

### Расписание синхронизации Airbyte

Уже настроено на запуск каждые 24 часа в 02:00.

Чтобы изменить:
1. Открыть соединение в Airbyte
2. Перейдите на вкладку «Настройки».
3. Обновление «Частота репликации»
4. Сохранить

### Расписание выполнения dbt

**Вариант 1: задание Cron (Linux)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**Вариант 2: скрипт Python**

**Файл**: `scripts/run_pipeline.py`
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

### Расписание с помощью Docker Compose

**Файл**: `docker-compose.scheduler.yml`
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

## Следующие шаги

Поздравляем! Вы создали полноценный сквозной конвейер данных. 🎉

### Узнать больше

1. **Airbyte Advanced** — [Руководство по интеграции Airbyte](../guides/airbyte-integration.md)
2. **Оптимизация Dremio** — [Руководство по установке Dremio](../guides/dremio-setup.md)
3. **Сложные модели dbt** - [Руководство по разработке dbt](../guides/dbt-development.md)
4. **Расширенные информационные панели** – [Руководство по расширенным панелям мониторинга](../guides/superset-dashboards.md)
5. **Качество данных** – [Руководство по качеству данных](../guides/data-quality.md)

### Поиск неисправностей

Если у вас возникли проблемы, см.:
- [Руководство по устранению неполадок](../guides/troubleshooting.md)
- [Руководство по установке](installation.md#troubleshooting)
- [Руководство по настройке](configuration.md)

---

## Краткое содержание

Вы успешно:

- ✅ Доступ к 7 сервисам платформы
- ✅ Настройте источник Airbyte (PostgreSQL)
- ✅ Настройте пункт назначения Airbyte (MinIO S3)
- ✅ Создайте свое первое соединение Airbyte
- ✅ Подключите Дремио к MinIO
- ✅ Создание шаблонов БДТ (постановка + витрины)
- ✅ Создайте панель мониторинга Superset
- ✅ Проверьте сквозной поток данных
- ✅ Автоматизировать выполнение конвейера

**Ваша платформа данных теперь работает!** 🚀

---

**Версия Руководства по первым шагам**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Поддерживает**: команда платформы данных.