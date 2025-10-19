# دليل لوحات معلومات Apache Superset

**الإصدار**: 3.2.0  
**آخر تحديث**: 16 أكتوبر 2025  
**اللغة**: الفرنسية

## جدول المحتويات

1. [نظرة عامة](#overview)
2. [التكوين الأولي](#التكوين الأولي)
3. [اتصال مصادر البيانات](#data-sources-connection)
4. [إنشاء الرسومات](#إنشاء الرسومات)
5. [إنشاء لوحة القيادة](#dashboard-construction)
6. [الميزات المتقدمة](#advanced-features)
7. [الأمان والأذونات](#الأمن والأذونات)
8. [تحسين الأداء](#تحسين الأداء)
9. [التكامل والمشاركة](#integration-and-sharing)
10. [الممارسات الجيدة](#الممارسات الجيدة)

---

## ملخص

Apache Superset هو تطبيق ويب حديث وجاهز للمؤسسات يسمح للمستخدمين باستكشاف البيانات وتصورها من خلال لوحات المعلومات والرسوم البيانية البديهية.

### الميزات الرئيسية

| ميزة | الوصف | الربح |
|----------------|---------|---------|
| **SQL IDE** | محرر SQL تفاعلي مع الإكمال التلقائي | التحليل المخصص |
| **تصورات غنية** | أكثر من 50 نوعًا من الرسوم البيانية | تمثيل البيانات المختلفة |
| ** منشئ لوحة المعلومات ** | واجهة السحب والإسقاط | من السهل إنشاء لوحة القيادة |
| ** التخزين المؤقت ** | استعلامات نتائج ذاكرة التخزين المؤقت | أوقات تحميل سريعة |
| **الأمن** | أمان على مستوى الصف، وصول قائم على الأدوار | حوكمة البيانات |
| **تنبيهات** | إشعارات البريد الإلكتروني/Slack الآلية | مراقبة استباقية |

### التكامل المعماري

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

## التكوين الأولي

### الاتصال الأول

الوصول إلى Superset على `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**ملاحظة أمنية**: قم بتغيير كلمة المرور الافتراضية مباشرة بعد تسجيل الدخول لأول مرة.

### الإعداد الأولي

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

### ملف التكوين

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

## مصادر بيانات الاتصال

### تسجيل الدخول إلى Dremio

#### الخطوة 1: تثبيت برنامج تشغيل قاعدة بيانات Dremio

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### الخطوة 2: إضافة قاعدة بيانات Drimio

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**إعدادات**:
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

#### الخطوة 3: اختبار الاتصال

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### الاتصال بـ PostgreSQL

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

### الاتصال بـ Elasticsearch

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

## إنشاء الرسومات

### سير عمل إنشاء الرسومات

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

### تحديد نوع الرسم

| نوع الرسم | الأفضل لـ | مثال لحالة الاستخدام |
|----------------|---------------|--------------------|
| ** الرسم البياني الخطي ** | الاتجاهات الزمنية | اتجاه الدخل اليومي |
| ** الرسم البياني الشريطي ** | مقارنات | الإيرادات حسب فئة المنتج |
| **مخطط القطاعات** | حصة من الإجمالي | حصة السوق حسب المنطقة |
| **الجدول** | بيانات تفصيلية | قائمة العملاء مع المقاييس |
| **عدد كبير** | متري واحد | إجمالي الدخل منذ بداية العام |
| **بطاقة الحرارة** | كشف النمط | المبيعات يوميا / ساعة |
| **نقطة السحابة** | الارتباطات | قيمة العميل مقابل التردد |
| ** مخطط سانكي ** | تحليل التدفق | رحلة المستخدم |

### مثال: الرسم البياني الخطي (اتجاه الدخل)

#### الخطوة 1: إنشاء مجموعة البيانات

```
Interface → Données → Datasets → + Dataset
```

**إعدادات**:
- **قاعدة البيانات**: دريميو
- **رسم بياني**: أسواق الإنتاج
- **الجدول**: mart_daily_revenue

#### الخطوة الثانية: إنشاء مخطط

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**حدود**:
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

** تم إنشاء SQL **:
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

### مثال: مخطط شريطي (أهم العملاء)

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

### مثال: PivotTable

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

### مثال: رقم كبير مع اتجاه

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

## لوحات معلومات البناء

### عملية إنشاء لوحة المعلومات

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

### الخطوة 1: إنشاء لوحة التحكم

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**إعدادات لوحة التحكم**:
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

### الخطوة 2: إضافة الرسومات

قم بسحب وإسقاط الرسومات من اللوحة اليمنى أو إنشاء رسومات جديدة:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### الخطوة 3: تخطيط التصميم

** نظام الشبكة **:
- عرض 12 عمود
- الرسومات المفاجئة على الشبكة
- انتقد لتغيير الحجم وتغيير الموضع

**مثال للتخطيط**:
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

### الخطوة 4: إضافة عوامل تصفية لوحة المعلومات

```
Tableau de Bord → Éditer → + Filtre
```

**تصفية النطاق الزمني**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**تصفية الفئة**:
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

**الفلتر الرقمي**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### الخطوة 5: التصفية المتقاطعة

تمكين التصفية المتقاطعة للوحة المعلومات:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**إعدادات**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**تجربة المستخدم**:
- انقر على الشريط → قم بتصفية لوحة المعلومات بأكملها
- انقر على مشاركة القطاع → تحديثات الرسومات ذات الصلة
- مسح الفلتر → إعادة التعيين إلى العرض الافتراضي

---

## الميزات المتقدمة

### مختبر SQL

محرر SQL التفاعلي للاستعلامات المخصصة.

#### تنفيذ الاستعلام

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

**سمات**:
- الإكمال التلقائي للجداول والأعمدة
- طلب التاريخ
- علامات تبويب متعددة
- تصدير النتائج (CSV، JSON)
- حفظ الاستعلام لإعادة استخدامه

#### إنشاء جدول من الاستعلام (CTAS)

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

### قوالب جينجا

SQL الديناميكي مع قوالب Jinja2:

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

** متغيرات القالب **:
- `{{ from_dttm }}` - نطاق تاريخ البدء
- `{{ to_dttm }}` - نهاية النطاق الزمني
- `{{ filter_values('column') }}` - قيم التصفية المحددة
- `{{ current_username }}` - مستخدم مسجل الدخول

### التنبيهات والتقارير

#### إنشاء تنبيه

```
Interface → Alertes & Rapports → + Alerte
```

**إعدادات**:
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

#### إنشاء تقرير

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

### ملحقات التصور المخصصة

إنشاء أنواع رسومية مخصصة:

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

بناء وتثبيت:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## الأمن والأذونات

### التحكم في الوصول المستند إلى الدور (RBAC)

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

### الأدوار المتكاملة

| الدور | أذونات | حالات الاستخدام |
|------|------------|-------------|
| **المسؤول** | جميع الأذونات | مسؤولي النظام |
| **ألفا** | إنشاء وتحرير وحذف لوحات المعلومات/المخططات | محللو البيانات |
| **جاما** | عرض لوحات المعلومات، وتشغيل استعلامات SQL Lab | مستخدمي الأعمال |
| **sql_lab** | الوصول إلى SQL Lab فقط | علماء البيانات |
| **عامة** | عرض لوحات المعلومات العامة فقط | مستخدمون مجهولون |

### إنشاء دور مخصص

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**مثال: دور محلل التسويق**
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

### الأمان على مستوى الخط (RLS)

تقييد البيانات وفقًا لسمات المستخدم:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**مثال: RLS بناءً على المنطقة**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**مثال: خدمة RLS المستندة إلى العميل**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### أمان اتصال قاعدة البيانات

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

## تحسين الأداء

### استعلامات التخزين المؤقت

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

**استراتيجية التخزين المؤقت**:
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

### الطلبات غير المتزامنة

تمكين تنفيذ الاستعلام غير المتزامن للاستعلامات الطويلة:

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

### تحسين استعلام قاعدة البيانات

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

### تحسين تحميل لوحة المعلومات

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

### مراقبة الأداء

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

## التكامل والمشاركة

### لوحات المعلومات العامة

إمكانية الوصول إلى لوحات المعلومات دون اتصال:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**عنوان URL العام**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### تكامل Iframe

دمج لوحات المعلومات في التطبيقات الخارجية:

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

**إعدادات التكامل**:
- `standalone=1` - إخفاء التنقل
- `show_filters=0` - إخفاء لوحة التصفية
- `show_title=0` - إخفاء عنوان لوحة القيادة

### مصادقة رمز الضيف

الوصول البرمجي للوحات المعلومات المتكاملة:

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

### تصدير لوحات المعلومات

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## أفضل الممارسات

### تصميم لوحة القيادة

1. **التسلسل الهرمي للتخطيط**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **تناسق الألوان**
   - استخدم نظام ألوان متناسق في جميع لوحات المعلومات
   - الأخضر للمقاييس الإيجابية، والأحمر للسالبة
   - ألوان العلامة التجارية للفئات

3. **الأداء**
   - الحد من الرسومات لكل لوحة معلومات (< 15)
   - استخدام مستويات التجميع المناسبة
   - تمكين ذاكرة التخزين المؤقت للبيانات الثابتة
   - تعيين حدود خط معقولة

4. **التفاعل**
   - إضافة مرشحات ذات معنى
   - تمكين التصفية المتقاطعة للاستكشاف
   - توفير قدرات الحفر

### اختيار الرسم

| نوع البيانات | الرسوم البيانية الموصى بها | تجنب |
|--------------|--------------------------|--------|
| **السلسلة الزمنية** | المناطق الخطية | القطاعات الدائري |
| **المقارنة** | الحانات والأعمدة | خطي (نقاط بيانات قليلة) |
| **الحصة من الإجمالي** | القطاعات، الحلقة، الخريطة الهيكلية | الحانات (فئات أيضًا) |
| **التوزيع** | رسم بياني، مخطط مربع | القطاعات |
| **الارتباط** | نقاط السحابة، الفقاعات | الحانات |
| **جغرافي** | الخريطة، تشوروبليث | الجدول |

### تحسين الاستعلام

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

### حماية

1. **التحكم في الوصول**
   - استخدم RBAC لإدارة المستخدم
   - تنفيذ RLS لعزل البيانات
   - تقييد اتصالات قاعدة البيانات حسب الدور

2. **إدارة البيانات**
   - خاصية مجموعات بيانات الوثيقة
   - تحديد جداول تحديث البيانات
   - مراقبة أداء الاستعلام

3. **الامتثال**
   - إخفاء معلومات تحديد الهوية الشخصية في المرئيات
   - الوصول إلى لوحة التحكم التدقيق
   - تنفيذ سياسات الاحتفاظ بالبيانات

---

## ملخص

لقد غطى دليل Superset الشامل هذا ما يلي:

- **التكوين**: التثبيت والتكوين واتصالات قاعدة البيانات
- **الرسومات**: أكثر من 50 نوعًا من الرسومات والتكوين وإنشاء SQL
- **لوحات المعلومات**: تصميم التخطيط، والمرشحات، والتصفية المتقاطعة
- **الميزات المتقدمة**: SQL Lab، وقوالب Jinja، والتنبيهات، والمكونات الإضافية المخصصة
- **الأمان**: RBAC، RLS، أمان اتصال قاعدة البيانات
- **الأداء**: التخزين المؤقت، والاستعلامات غير المتزامنة، وتحسين الاستعلام
- **التكامل**: لوحات المعلومات العامة، وتكامل iframe، والرموز المميزة للضيوف
- **الممارسات الجيدة**: مبادئ التصميم واختيار الرسوم والأمان

النقاط الرئيسية التي يجب تذكرها:
- يتصل Superset بـ Dremio للحصول على تحليلات عالية الأداء
- مكتبة تصورية غنية تدعم حالات الاستخدام المختلفة
- يضمن التخزين المؤقت والاستعلامات غير المتزامنة لوحات معلومات سريعة
- يتيح RBAC وRLS تحليلات الخدمة الذاتية الآمنة
- قدرات التكامل تمكن التكامل مع التطبيقات الخارجية

**الوثائق ذات الصلة:**
- [دليل إعداد Dremio](./dremio-setup.md)
- [الهندسة المعمارية: تدفق البيانات](../architecture/data-flow.md)
- [البرنامج التعليمي للخطوات الأولى](../getting-started/first-steps.md)
- [دليل جودة البيانات](./data-quality.md)

---

**الإصدار**: 3.2.0  
**آخر تحديث**: 16 أكتوبر 2025