# Обзор архитектуры

**Версия**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Язык**: французский

---

## Введение

Платформа данных представляет собой современную облачную архитектуру, построенную на технологиях с открытым исходным кодом. Он предоставляет комплексное решение для приема, хранения, преобразования и визуализации данных, предназначенное для аналитических рабочих нагрузок корпоративного масштаба.

```mermaid
graph TB
    subgraph "Couche d'Ingestion"
        AB[Airbyte<br/>Intégration Données]
    end
    
    subgraph "Couche de Stockage"
        S3[MinIO S3<br/>Data Lake]
        PG[PostgreSQL<br/>OLTP]
        ES[Elasticsearch<br/>Recherche]
    end
    
    subgraph "Couche de Traitement"
        DR[Dremio<br/>Lakehouse]
        DBT[dbt<br/>Transform]
    end
    
    subgraph "Couche de Présentation"
        SUP[Superset<br/>Plateforme BI]
    end
    
    AB --> S3
    AB --> PG
    S3 --> DR
    PG --> DR
    ES --> DR
    DR <--> DBT
    DR --> SUP
    
    style AB fill:#615EFF,color:#fff
    style DR fill:#FDB515
    style DBT fill:#FF694B,color:#fff
    style SUP fill:#20A7C9,color:#fff
```

---

## Принципы проектирования

### 1. Открытый исходный код прежде всего

**Философия**: используйте технологии с открытым исходным кодом, чтобы избежать привязки к поставщику и сохранить гибкость.

**Преимущества**:
- Никаких затрат на лицензирование
- Развитие сообщества
- Полная возможность настройки
- Прозрачный аудит безопасности
- Широкая совместимость с экосистемами

### 2. Многоуровневая архитектура

**Философия**: разделение проблем на отдельные уровни для удобства обслуживания и масштабируемости.

**Слои**:
```
┌─────────────────────────────────────┐
│     Couche de Présentation          │  Superset (BI & Tableaux de Bord)
├─────────────────────────────────────┤
│     Couche Sémantique               │  Dremio (Moteur de Requête)
├─────────────────────────────────────┤
│     Couche de Transformation        │  dbt (Transformation Données)
├─────────────────────────────────────┤
│     Couche de Stockage              │  MinIO, PostgreSQL, Elasticsearch
├─────────────────────────────────────┤
│     Couche d'Ingestion              │  Airbyte (Intégration Données)
└─────────────────────────────────────┘
```

### 3. ELT, а не ETL

**Философия**: сначала загружайте необработанные данные, а затем преобразуйте их в пункт назначения (ELT).

**Почему ELT?**
- **Гибкость**: преобразуйте данные несколькими способами без повторного извлечения.
- **Производительность**: используйте расчет назначения для преобразований.
- **Аудитируемость**: необработанные данные всегда доступны для проверки.
- **Стоимость**: снижение нагрузки на исходные системы при извлечении данных.

**Поток**:
```
Extract → Load → Transform
(Airbyte) (MinIO/PostgreSQL) (dbt + Dremio)
```

### 4. Модель озера данных

**Философия**: объедините гибкость озера данных с производительностью хранилища данных.

**Функции**:
- **ACID-транзакции**: доверенные операции с данными.
- **Приложение схемы**: гарантии качества данных.
- **Путешествие во времени**: запрос исторических версий.
- **Открытые форматы**: Паркет, Айсберг, Дельта озера.
- **Прямой доступ к файлам**: нет собственной блокировки.

### 5. Облачный дизайн

**Философия**: проектирование для контейнерных и распределенных сред.

**Выполнение**:
- Docker-контейнеры для всех сервисов
- Горизонтальная масштабируемость
- Инфраструктура как код
- Лица без гражданства, где это возможно
- Конфигурация через переменные среды

---

## Модели архитектуры

### Лямбда-архитектура (Пакетная + Поточная)

```mermaid
graph LR
    subgraph "Sources de Données"
        SRC[Sources]
    end
    
    subgraph "Couche Batch"
        B1[Airbyte Batch] --> B2[MinIO S3]
        B2 --> B3[Vues Dremio]
    end
    
    subgraph "Couche Vitesse"
        S1[Airbyte CDC] --> S2[PostgreSQL]
        S2 --> S3[Dremio Live]
    end
    
    subgraph "Couche Service"
        B3 --> MERGE[Vue Unifiée]
        S3 --> MERGE
        MERGE --> SUP[Superset]
    end
    
    SRC --> B1
    SRC --> S1
```

**Пакетный уровень** (исторические данные):
- Большие объемы данных
- Периодическое лечение (ежечасно/ежедневно)
- Приемлемая высокая задержка
- Возможна полная переработка

**Уровень скорости** (данные в реальном времени):
- Сбор измененных данных (CDC)
- Требуется низкая задержка
- Только дополнительные обновления
- Управляет последними данными

**Сервисный уровень**:
- Объединяет пакетные и скоростные представления
- Интерфейс единого запроса (Dremio)
- Автоматический выбор вида

### Медальон «Архитектура» (Бронза → Серебро → Золото)

```mermaid
graph LR
    A[Sources] -->|Brut| B[Couche Bronze<br/>MinIO S3]
    B -->|Nettoyé| C[Couche Silver<br/>dbt Staging]
    C -->|Agrégé| D[Couche Gold<br/>dbt Marts]
    D --> E[Utilisateurs Métier<br/>Superset]
    
    style B fill:#CD7F32,color:#fff
    style C fill:#C0C0C0
    style D fill:#FFD700
```

**Бронзовый слой** (Raw):
- Данные как есть из источников
- Никакой трансформации
- Сохранена полная история
- Airbyte загружается сюда

**Серебристый слой** (Очищенный):
- Качество прикладных данных
- Стандартизированные форматы
- шаблоны промежуточной обработки dbt
- Готовая аналитика

**Золотой слой** (Профессия):
- Агрегированные показатели
- Прикладная бизнес-логика.
- Модели Marts dbt
- Оптимизирован для потребления

---

## Взаимодействие между компонентами

### Поток приема данных

```mermaid
sequenceDiagram
    participant Src as Source Données
    participant Ab as Airbyte
    participant S3 as MinIO S3
    participant Dr as Dremio
    participant Pg as PostgreSQL
    
    Src->>Ab: 1. Extraire données
    Ab->>Ab: 2. Transformer en Parquet
    Ab->>S3: 3. Écrire couche bronze
    Ab->>Pg: 4. Écrire métadonnées
    
    Note over S3,Dr: Dremio analyse S3
    Dr->>S3: 5. Lire fichiers Parquet
    Dr->>Dr: 6. Construire métadonnées
    Dr->>Pg: 7. Requêter métadonnées
    
    Note over Dr: Données prêtes pour requêtes
```

### Конвейер трансформации

```mermaid
sequenceDiagram
    participant Dr as Dremio
    participant Dbt as dbt
    participant S3 as MinIO S3
    
    Dbt->>Dr: 1. Lire données bronze (SELECT)
    Dr->>S3: 2. Analyser fichiers Parquet
    S3->>Dr: 3. Retourner données
    Dr->>Dbt: 4. Résultats requête
    
    Dbt->>Dbt: 5. Appliquer transformations
    Dbt->>Dbt: 6. Exécuter tests
    
    Dbt->>Dr: 7. Écrire silver/gold (CREATE TABLE)
    Dr->>S3: 8. Écrire Parquet
    S3->>Dr: 9. Confirmer écriture
    Dr->>Dbt: 10. Succès
    
    Note over Dbt,Dr: Données transformées disponibles
```

### Выполнение запросов

```mermaid
sequenceDiagram
    participant User as Utilisateur Final
    participant Sup as Superset
    participant Dr as Dremio
    participant S3 as MinIO S3
    participant Pg as PostgreSQL
    
    User->>Sup: 1. Demander tableau de bord
    Sup->>Dr: 2. Exécuter SQL (Arrow Flight)
    
    Dr->>Dr: 3. Parser requête
    Dr->>Dr: 4. Vérifier réflexions (cache)
    
    alt Réflexion disponible
        Dr->>S3: 5a. Lire données en cache
    else Pas de réflexion
        Dr->>S3: 5b. Analyser fichiers source
        Dr->>Pg: 5c. Requêter métadonnées
    end
    
    Dr->>Dr: 6. Exécuter requête
    Dr->>Sup: 7. Retourner résultats (Arrow)
    Sup->>Sup: 8. Rendre graphiques
    Sup->>User: 9. Afficher tableau de bord
```

---

## Модели масштабируемости

### Горизонтальное масштабирование

**Сервисы без гражданства** (могут свободно развиваться):
- Airbyte Workers: развивайтесь для параллельной синхронизации.
- Dremio Executors: масштабирование производительности запросов.
- Веб-суперсет: развивайтесь для конкурирующих пользователей.

**Службы с отслеживанием состояния** (требуется согласование):
- PostgreSQL: репликация первичной реплики.
- MinIO: распределенный режим (несколько узлов)
- Elasticsearch: кластер с шардингом

### Вертикальное масштабирование

**Интенсив по памяти**:
- Dremio: увеличение кучи JVM для больших запросов.
- PostgreSQL: больше оперативной памяти для буфера кэша.
- Elasticsearch: больше кучи для индексации

**Нагрузка на процессор**:
- dbt: больше ядер для моделей параллельного построения.
- Airbyte: более быстрое преобразование данных.

### Разделение данных

```sql
-- Exemple: Partitionner par date
CREATE TABLE orders_partitioned (
    order_id INT,
    customer_id INT,
    amount DECIMAL,
    order_date DATE
)
PARTITION BY (DATE_TRUNC('month', order_date))
STORED AS PARQUET;

-- La requête analyse uniquement les partitions pertinentes
SELECT SUM(amount)
FROM orders_partitioned
WHERE order_date >= '2025-01-01'
  AND order_date < '2025-02-01';
-- Analyse uniquement la partition de janvier
```

---

## Высокая доступность

### Резервирование услуг

```mermaid
graph TB
    subgraph "Équilibreur de Charge"
        LB[HAProxy/Nginx]
    end
    
    subgraph "Niveau Application"
        SUP1[Superset 1]
        SUP2[Superset 2]
        SUP3[Superset 3]
    end
    
    subgraph "Niveau Données"
        DR1[Dremio Primaire]
        DR2[Dremio Exécuteur 1]
        DR3[Dremio Exécuteur 2]
    end
    
    subgraph "Niveau Stockage"
        PG1[(PostgreSQL Primaire)]
        PG2[(PostgreSQL Réplique)]
        S3C[Cluster MinIO]
    end
    
    LB --> SUP1
    LB --> SUP2
    LB --> SUP3
    
    SUP1 --> DR1
    SUP2 --> DR1
    SUP3 --> DR1
    
    DR1 --> DR2
    DR1 --> DR3
    
    DR1 --> S3C
    DR2 --> S3C
    DR3 --> S3C
    
    DR1 --> PG1
    PG1 -.->|Réplication| PG2
```

### Сценарии сбоев

| Компонент | Разбивка | Восстановление |
|---------------|-------|---------|
| **Рабочий Airbyte** | Крушение контейнера | Автоматический перезапуск, возобновление синхронизации |
| **Палач Дремио** | Сбой узла | Запрос перенаправлен другим исполнителям |
| **PostgreSQL** | Первичный выход из строя | Продвигать реплику в первичном |
| **Узел MinIO** | Сбой диска | Стирающее кодирование восстанавливает данные |
| **Суперсет** | Служба не работает | Балансировщик перенаправляет трафик |

### Стратегия резервного копирования

```bash
# Sauvegardes automatisées quotidiennes
0 2 * * * /scripts/backup_all.sh

# backup_all.sh
#!/bin/bash

# Sauvegarder PostgreSQL
pg_dumpall -U postgres > /backups/postgres_$(date +%Y%m%d).sql

# Sauvegarder métadonnées Dremio
tar czf /backups/dremio_$(date +%Y%m%d).tar.gz /opt/dremio/data

# Synchroniser MinIO vers S3 distant
mc mirror MinIOLake/datalake s3-offsite/datalake-backup

# Conserver 30 jours
find /backups -mtime +30 -delete
```

---

## Архитектура безопасности

### Сетевая безопасность

```mermaid
graph TB
    subgraph "Externe"
        U[Utilisateurs]
    end
    
    subgraph "DMZ"
        FW[Pare-feu]
        RP[Proxy Inverse]
    end
    
    subgraph "Réseau Application"
        SUP[Superset :8088]
        DR[Dremio :9047/:31010/:32010]
        AB[Airbyte :8000]
    end
    
    subgraph "Réseau Données"
        PG[PostgreSQL :5432]
        S3[MinIO :9000]
        ES[Elasticsearch :9200]
    end
    
    U -->|HTTPS| FW
    FW --> RP
    RP --> SUP
    RP --> DR
    RP --> AB
    
    SUP --> PG
    SUP --> DR
    DR --> PG
    DR --> S3
    DR --> ES
    AB --> PG
    AB --> S3
```

### Аутентификация и авторизация

**Аутентификация службы**:
- **Dremio**: интеграция LDAP/AD, OAuth2, SAML.
- **Расширенный набор**: проверка подлинности базы данных, LDAP, OAuth2.
- **Airbyte**: базовая аутентификация, OAuth2 (корпоративный)
- **MinIO**: политики IAM, токены STS.

**Уровни авторизации**:
```yaml
Rôles:
  - Admin:
      - Accès complet à tous les services
      - Gestion utilisateurs
      - Modifications configuration
  
  - Data Engineer:
      - Créer/modifier sources données
      - Exécuter syncs Airbyte
      - Exécuter modèles dbt
      - Créer datasets Dremio
  
  - Analyst:
      - Accès lecture seule données
      - Créer tableaux de bord Superset
      - Requêter datasets Dremio
  
  - Viewer:
      - Voir tableaux de bord uniquement
      - Pas d'accès données
```

### Шифрование данных

**В состоянии покоя**:
- MinIO: шифрование на стороне сервера (AES-256).
- PostgreSQL: прозрачное шифрование данных (TDE).
- Elasticsearch: зашифрованные индексы.

**В пути**:
- TLS 1.3 для всей межсервисной связи.
- Полет по стреле с TLS для Дремио ↔ Суперсет
- HTTPS для веб-интерфейсов

---

## Мониторинг и наблюдаемость

### Сбор метрик

```mermaid
graph LR
    A[Airbyte] -->|Métriques| P[Prometheus]
    D[Dremio] -->|Métriques| P
    S[Superset] -->|Métriques| P
    PG[PostgreSQL] -->|Métriques| P
    M[MinIO] -->|Métriques| P
    
    P --> G[Grafana]
    P --> AL[Alertmanager]
    
    AL -->|Email| E[Email]
    AL -->|Slack| SL[Slack]
```

**Ключевые показатели**:
- **Airbyte**: процент успешной синхронизации, синхронизированные записи, переданные байты.
- **Dremio**: задержка запроса, частота попадания в кеш, использование ресурсов.
- **dbt**: время построения модели, неудачные тесты.
- **Суперсет**: время загрузки панели управления, активные пользователи.
- **Инфраструктура**: процессор, память, диск, сеть.

### Ведение журнала

**Централизованное ведение журнала**:
```yaml
Stack ELK:
  - Elasticsearch: Stocker logs
  - Logstash: Traiter logs
  - Kibana: Visualiser logs

Sources de Logs:
  - Logs application (format JSON)
  - Logs d'accès
  - Logs d'audit
  - Logs d'erreur
```

### Трассировка

**Распределенная трассировка**:
- Интеграция Jaeger или Zipkin
- Трассировка запросов между сервисами
- Выявить узкие места
- Отладка проблем с производительностью.

---

## Топологии развертывания

### Среда разработки

```yaml
Hôte Unique:
  Ressources: 8 Go RAM, 4 CPUs
  Services: Tous sur une machine
  Stockage: Volumes locaux
  Réseau: Réseau bridge
  Cas d'usage: Développement, tests
```

### Промежуточная среда

```yaml
Multi-Hôtes:
  Ressources: 16 Go RAM, 8 CPUs par hôte
  Services: Répartis sur 2-3 hôtes
  Stockage: NFS partagé ou MinIO distribué
  Réseau: Réseau overlay
  Cas d'usage: Tests pré-production, UAT
```

### Производственная среда

```yaml
Cluster Kubernetes:
  Ressources: Auto-scaling selon charge
  Services: Conteneurisés, répliqués
  Stockage: Volumes persistants (SSD)
  Réseau: Service mesh (Istio)
  Haute Disponibilité: Déploiement multi-zones
  Cas d'usage: Charges production
```

---

## Обоснование технологического выбора

### Почему Airbyte?

- **более 300 соединителей**: встроенные интеграции.
- **Открытый исходный код**: нет привязки к поставщику.
- **Активное сообщество**: более 12 тысяч звезд GitHub.
- **Поддержка CDC**: сбор данных в реальном времени.
- **Стандартизация**: встроенная интеграция с dbt.

### Почему Дремио?

- **Ускорение запросов**: запросы выполняются в 10–100 раз быстрее.
- **Полет по стрелке**: Высокопроизводительная передача данных.
- **Совместимость с озером данных**: перемещение данных не допускается.
- **Самообслуживание**: бизнес-пользователи изучают данные.
- **Прибыльно**: сократите складские расходы.

### Почему ДБТ?

- **На основе SQL**: знаком аналитикам.
- **Контроль версий**: интеграция с Git.
- **Тесты**: встроенные тесты качества данных.
- **Документация**: документы, создаваемые автоматически.
- **Сообщество**: доступно более 5 тысяч пакетов.

### Почему Суперсет?

- **Современный интерфейс**: интуитивно понятный интерфейс.
- **SQL IDE**: расширенные возможности запросов.
- **Богатая визуализация**: более 50 графических типов.
- **Расширяемый**: пользовательские плагины.
- **Открытый исходный код**: поддерживается Apache Foundation.

### Почему PostgreSQL?

- **Надежность**: соответствие требованиям ACID.
- **Производительность**: проверено в масштабе
- **Функции**: JSON, полнотекстовый поиск, расширения.
- **Сообщество**: зрелая экосистема.
- **Стоимость**: бесплатно и с открытым исходным кодом.

### Почему MinIO?

- **Совместимость с S3**: API стандарта отрасли.
- **Производительность**: Высокая скорость потока.
- **Стирающее кодирование**: долговечность данных.
- **Мультиоблако**: развертывание повсюду.
- **Экономично**: альтернатива самостоятельному размещению.

---

## Будущая эволюция архитектуры

### Планируемые улучшения

1. **Каталог данных** (интеграция OpenMetadata)
   - Управление метаданными
   - Отслеживание происхождения
   - Обнаружение данных

2. **Качество данных** (большие ожидания)
   - Автоматическая проверка
   - Обнаружение аномалий
   - Качественные панели мониторинга.

3. **Операции машинного обучения** (MLflow)
   - Моделирование конвейеров обучения
   - Регистрация моделей
   - Автоматизация развертывания

4. **Потоковая обработка** (Apache Flink)
   - Преобразования в реальном времени
   - Сложная обработка событий
   - Потоковая аналитика

5. **Управление данными** (Apache Atlas)
   - Применение политики
   - Аудит доступа
   - Отчеты о соответствии

---

## Ссылки

- [Подробности о компоненте](comComponents.md)
- [Поток данных](data-flow.md)
- [Руководство по развертыванию](deployment.md)
- [Интеграция Airbyte](../guides/airbyte-integration.md)

---

**Версия обзора архитектуры**: 3.2.0  
**Последнее обновление**: 16 октября 2025 г.  
**Поддерживает**: команда платформы данных.