# अपाचे सुपरसेट डैशबोर्ड गाइड

**संस्करण**: 3.2.0  
**आखिरी अपडेट**: 16 अक्टूबर, 2025  
**भाषा**: फ्रेंच

## विषयसूची

1. [अवलोकन](#अवलोकन)
2. [प्रारंभिक विन्यास](#प्रारंभिक-विन्यास)
3. [डेटा स्रोत कनेक्शन](#डेटा-स्रोत-कनेक्शन)
4. [ग्राफिक्स निर्माण](#ग्राफिक्स-निर्माण)
5. [डैशबोर्ड निर्माण](#डैशबोर्ड-निर्माण)
6. [उन्नत सुविधाएँ](#उन्नत-सुविधाएँ)
7. [सुरक्षा और अनुमतियाँ](#सुरक्षा-और-अनुमतियाँ)
8. [प्रदर्शन अनुकूलन](#प्रदर्शन-अनुकूलन)
9. [एकीकरण और साझाकरण](#एकीकरण-और-साझाकरण)
10. [अच्छी प्रथाएं](#अच्छी प्रथाएं)

---

## अवलोकन

अपाचे सुपरसेट एक आधुनिक, उद्यम-तैयार बिजनेस इंटेलिजेंस वेब एप्लिकेशन है जो उपयोगकर्ताओं को सहज ज्ञान युक्त डैशबोर्ड और चार्ट के माध्यम से डेटा का पता लगाने और कल्पना करने की अनुमति देता है।

### प्रमुख विशेषताऐं

| फ़ीचर | विवरण | मुनाफ़ा |
|----------------|------|---------|
| **एसक्यूएल आईडीई** | स्वत: पूर्णता के साथ इंटरएक्टिव एसक्यूएल संपादक | तदर्थ विश्लेषण |
| **समृद्ध विज़ुअलाइज़ेशन** | 50+ चार्ट प्रकार | विभिन्न डेटा प्रतिनिधित्व |
| **डैशबोर्ड बिल्डर** | इंटरफ़ेस खींचें और छोड़ें | आसान डैशबोर्ड निर्माण |
| **कैशिंग** | कैश परिणाम प्रश्न | तेज़ लोडिंग समय |
| **सुरक्षा** | पंक्ति-स्तरीय सुरक्षा, भूमिका-आधारित पहुंच | डेटा गवर्नेंस |
| **अलर्ट** | स्वचालित ईमेल/स्लैक सूचनाएं | सक्रिय निगरानी |

### वास्तुकला एकीकरण

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

## प्रारंभिक कॉन्फ़िगरेशन

### पहला कनेक्शन

`http://localhost:8088` पर सुपरसेट तक पहुंचें:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**सुरक्षा नोट**: पहले लॉगिन के तुरंत बाद डिफ़ॉल्ट पासवर्ड बदलें।

### प्रारंभिक सेटअप

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

### कॉन्फ़िगरेशन फ़ाइल

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

## कनेक्शन डेटा स्रोत

### ड्रेमियो में लॉगिन करें

#### चरण 1: ड्रेमियो डेटाबेस ड्राइवर स्थापित करें

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### चरण 2: ड्रेमियो डेटाबेस जोड़ें

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**विन्यास**:
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

#### चरण 3: कनेक्शन का परीक्षण करें

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### PostgreSQL से कनेक्ट हो रहा है

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

### इलास्टिक्स खोज से जुड़ना

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

## ग्राफ़िक्स निर्माण

### ग्राफिक निर्माण वर्कफ़्लो

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

### चयन ग्राफिक प्रकार

| ग्राफ़िक प्रकार | के लिए सर्वश्रेष्ठ | केस उदाहरण का प्रयोग करें |
|----------------|----------------------|----------------------|
| **रैखिक चार्ट** | अस्थायी रुझान | दैनिक आय प्रवृत्ति |
| **बार चार्ट** | तुलना | उत्पाद श्रेणी के अनुसार राजस्व |
| **सेक्टर चार्ट** | कुल का हिस्सा | क्षेत्र के अनुसार बाज़ार हिस्सेदारी |
| **तालिका** | विस्तृत डेटा | मेट्रिक्स के साथ ग्राहक सूची |
| **बड़ी संख्या** | एकल मीट्रिक | कुल YTD आय |
| **हीट कार्ड** | पैटर्न का पता लगाना | प्रति दिन/घंटा बिक्री |
| **प्वाइंट क्लाउड** | सहसंबंध | ग्राहक मूल्य बनाम आवृत्ति |
| **सैंकी आरेख** | प्रवाह विश्लेषण | उपयोगकर्ता यात्रा |

### उदाहरण: रेखीय चार्ट (आय प्रवृत्ति)

#### चरण 1: डेटासेट बनाएं

```
Interface → Données → Datasets → + Dataset
```

**विन्यास**:
- **डेटाबेस**: ड्रेमियो
- **आरेख**: उत्पादन.मार्ट
- **तालिका**: मार्ट_दैनिक_राजस्व

#### चरण 2: चार्ट बनाएं

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**पैरामीटर**:
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

**एसक्यूएल उत्पन्न**:
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

### उदाहरण: बार चार्ट (शीर्ष ग्राहक)

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

### उदाहरण: पिवोटटेबल

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

### उदाहरण: रुझान के साथ बड़ी संख्या

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

## निर्माण डैशबोर्ड

### डैशबोर्ड निर्माण प्रक्रिया

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

### चरण 1: डैशबोर्ड बनाएं

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**डैशबोर्ड सेटिंग्स**:
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

### चरण 2: ग्राफ़िक्स जोड़ें

बाएं पैनल से ग्राफ़िक्स खींचें और छोड़ें या नए बनाएं:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### चरण 3: डिज़ाइन लेआउट

**ग्रिड प्रणाली**:
- 12 कॉलम चौड़ा
- ग्राफ़िक्स ग्रिड पर स्नैप करें
- आकार बदलने और स्थिति बदलने के लिए स्वाइप करें

**उदाहरण लेआउट**:
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

### चरण 4: डैशबोर्ड फ़िल्टर जोड़ें

```
Tableau de Bord → Éditer → + Filtre
```

**दिनांक सीमा फ़िल्टर**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**श्रेणी फ़िल्टर**:
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

**डिजिटल फ़िल्टर**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### चरण 5: क्रॉस फ़िल्टरिंग

डैशबोर्ड क्रॉस फ़िल्टरिंग सक्षम करें:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**विन्यास**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**प्रयोगकर्ता का अनुभव**:
- बार पर क्लिक करें → संपूर्ण डैशबोर्ड को फ़िल्टर करें
- सेक्टर शेयर → अपडेट संबंधित ग्राफिक्स पर क्लिक करें
- फ़िल्टर साफ़ करें → डिफ़ॉल्ट दृश्य पर रीसेट हो जाता है

---

## उन्नत विशेषताएँ

### एसक्यूएल लैब

तदर्थ प्रश्नों के लिए इंटरएक्टिव एसक्यूएल संपादक।

#### क्वेरी को निष्पादित करें

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

**विशेषताएँ**:
- तालिकाओं और स्तंभों के लिए स्वतः पूर्णता
- इतिहास का अनुरोध करें
- एकाधिक टैब
- निर्यात परिणाम (CSV, JSON)
- पुन: उपयोग के लिए क्वेरी सहेजें

#### क्वेरी से तालिका बनाएं (CTAS)

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

### जिंजा टेम्पलेट्स

Jinja2 टेम्पलेट्स के साथ गतिशील SQL:

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

**टेम्पलेट वेरिएबल्स**:
- `{{ from_dttm }}` - प्रारंभ तिथि सीमा
- `{{ to_dttm }}` - तिथि सीमा की समाप्ति
- `{{ filter_values('column') }}` - चयनित फ़िल्टर मान
- `{{ current_username }}` - लॉग इन उपयोगकर्ता

### अलर्ट और रिपोर्ट

#### अलर्ट बनाएं

```
Interface → Alertes & Rapports → + Alerte
```

**विन्यास**:
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

#### रिपोर्ट बनाएं

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

### कस्टम विज़ुअलाइज़ेशन प्लगइन्स

कस्टम ग्राफिक प्रकार बनाएं:

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

बनाएं और इंस्टॉल करें:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## सुरक्षा और अनुमतियाँ

### भूमिका आधारित अभिगम नियंत्रण (आरबीएसी)

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

### एकीकृत भूमिकाएँ

| भूमिका | अनुमतियाँ | उपयोग के मामले |
|------|----|---|
| **एडमिन** | सभी अनुमतियाँ | सिस्टम प्रशासक |
| **अल्फ़ा** | डैशबोर्ड/चार्ट बनाएं, संपादित करें, हटाएं | डेटा विश्लेषक |
| **गामा** | डैशबोर्ड देखें, SQL लैब क्वेरीज़ चलाएँ | व्यावसायिक उपयोगकर्ता |
| **sql_lab** | केवल SQL लैब तक पहुंच | डेटा वैज्ञानिक |
| **सार्वजनिक** | केवल सार्वजनिक डैशबोर्ड देखें | अनाम उपयोगकर्ता |

### कस्टम भूमिका बनाएँ

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**उदाहरण: विपणन विश्लेषक भूमिका**
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

### लाइन लेवल सुरक्षा (आरएलएस)

उपयोगकर्ता विशेषताओं के अनुसार डेटा प्रतिबंधित करें:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**उदाहरण: क्षेत्र आधारित आरएलएस**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**उदाहरण: ग्राहक-आधारित आरएलएस**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### डेटाबेस कनेक्शन सुरक्षा

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

## प्रदर्शन अनुकूलन

### कैशिंग क्वेरीज़

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

**कैश रणनीति**:
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

### अतुल्यकालिक अनुरोध

लंबी क्वेरी के लिए एसिंक क्वेरी निष्पादन सक्षम करें:

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

### डेटाबेस क्वेरी अनुकूलन

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

### डैशबोर्ड लोडिंग अनुकूलन

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

### निष्पादन की निगरानी

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

## एकीकरण और साझाकरण

### सार्वजनिक डैशबोर्ड

डैशबोर्ड को बिना कनेक्शन के पहुंच योग्य बनाएं:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**सार्वजनिक यूआरएल**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### आईफ्रेम एकीकरण

डैशबोर्ड को बाहरी अनुप्रयोगों में एकीकृत करें:

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

**एकीकरण सेटिंग्स**:
- `standalone=1` - नेविगेशन छुपाएं
- `show_filters=0` - फ़िल्टर पैनल छिपाएँ
- `show_title=0` - डैशबोर्ड शीर्षक छुपाएं

### अतिथि टोकन प्रमाणीकरण

एकीकृत डैशबोर्ड के लिए प्रोग्रामेटिक एक्सेस:

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

### डैशबोर्ड निर्यात करें

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## सर्वोत्तम प्रथाएं

### डैशबोर्ड डिज़ाइन

1. **लेआउट पदानुक्रम**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **रंग संगति**
   - सभी डैशबोर्ड पर एक समान रंग योजना का उपयोग करें
   - सकारात्मक मेट्रिक्स के लिए हरा, नकारात्मक के लिए लाल
   - श्रेणियों के लिए ब्रांड रंग

3. **प्रदर्शन**
   - प्रति डैशबोर्ड ग्राफिक्स सीमित करें (<15)
   - उचित एकत्रीकरण स्तरों का उपयोग करें
   - स्थिर डेटा के लिए कैश सक्षम करें
   - उचित लाइन सीमा निर्धारित करें

4. **अन्तरक्रियाशीलता**
   - सार्थक फ़िल्टर जोड़ें
   - अन्वेषण के लिए क्रॉस फ़िल्टरिंग सक्षम करें
   - ड्रिल-डाउन क्षमताएं प्रदान करें

### ग्राफिक चयन

| डेटा प्रकार | अनुशंसित चार्ट | बचें |
|----|--------------------------------|--------|
| **समय श्रृंखला** | रैखिक, क्षेत्रफल | सेक्टर, रिंग |
| **तुलना** | बार्स, कॉलम | रैखिक (कुछ डेटा बिंदु) |
| **कुल का हिस्सा** | सेक्टर, रिंग, ट्रीमैप | बार्स (भी श्रेणियां) |
| **वितरण** | हिस्टोग्राम, बॉक्स प्लॉट | सेक्टर |
| **सहसंबंध** | बादल बिंदु, बुलबुले | बार्स |
| **भौगोलिक** | मानचित्र, कोरोप्लेथ | तालिका |

### क्वेरी अनुकूलन

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

### सुरक्षा

1. **पहुंच नियंत्रण**
   - उपयोगकर्ता प्रबंधन के लिए आरबीएसी का प्रयोग करें
   - डेटा अलगाव के लिए आरएलएस लागू करें
   - भूमिका के आधार पर डेटाबेस कनेक्शन प्रतिबंधित करें

2. **डेटा गवर्नेंस**
   - दस्तावेज़ डेटासेट संपत्ति
   - डेटा रिफ्रेश शेड्यूल को परिभाषित करें
   - क्वेरी प्रदर्शन की निगरानी करें

3. **अनुपालन**
   - विज़ुअलाइज़ेशन में PII छिपाएँ
   - ऑडिट डैशबोर्ड एक्सेस
   - डेटा प्रतिधारण नीतियों को लागू करें

---

## सारांश

इस व्यापक सुपरसेट गाइड में निम्नलिखित को शामिल किया गया है:

- **कॉन्फ़िगरेशन**: इंस्टालेशन, कॉन्फ़िगरेशन, डेटाबेस कनेक्शन
- **ग्राफिक्स**: 50 से अधिक ग्राफिक प्रकार, कॉन्फ़िगरेशन, एसक्यूएल पीढ़ी
- **डैशबोर्ड**: लेआउट डिज़ाइन, फ़िल्टर, क्रॉस-फ़िल्टरिंग
- **उन्नत सुविधाएं**: एसक्यूएल लैब, जिंजा टेम्पलेट्स, अलर्ट, कस्टम प्लगइन्स
- **सुरक्षा**: आरबीएसी, आरएलएस, डेटाबेस कनेक्शन सुरक्षा
- **प्रदर्शन**: कैशिंग, एसिंक क्वेरीज़, क्वेरी अनुकूलन
- **एकीकरण**: सार्वजनिक डैशबोर्ड, आईफ़्रेम एकीकरण, अतिथि टोकन
- **अच्छी प्रथाएँ**: डिज़ाइन सिद्धांत, ग्राफिक चयन, सुरक्षा

याद रखने योग्य मुख्य बिंदु:
- सुपरसेट उच्च-प्रदर्शन विश्लेषण के लिए ड्रेमियो से जुड़ता है
- रिच विज़ुअलाइज़ेशन लाइब्रेरी विभिन्न उपयोग मामलों का समर्थन करती है
- अंतर्निहित कैशिंग और एसिंक क्वेरीज़ तेज़ डैशबोर्ड सुनिश्चित करती हैं
- आरबीएसी और आरएलएस सुरक्षित स्व-सेवा विश्लेषण सक्षम करते हैं
- एकीकरण क्षमताएं बाहरी अनुप्रयोगों के साथ एकीकरण को सक्षम बनाती हैं

**संबंधित दस्तावेज:**
- [ड्रेमियो सेटअप गाइड](./dremio-setup.md)
- [आर्किटेक्चर: डेटा प्रवाह](../आर्किटेक्चर/डेटा-फ्लो.एमडी)
- [प्रथम चरण ट्यूटोरियल](../getting-started/first-steps.md)
- [डेटा गुणवत्ता गाइड](./data-quality.md)

---

**संस्करण**: 3.2.0  
**आखिरी अपडेट**: 16 अक्टूबर, 2025