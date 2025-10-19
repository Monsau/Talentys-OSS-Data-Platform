# डेटा प्लेटफ़ॉर्म के साथ शुरुआत करना

**संस्करण**: 3.2.0  
**अंतिम अद्यतन**: 2025-10-16  
**भाषा**: फ्रेंच

---

## अवलोकन

यह ट्यूटोरियल आपको सेवाओं से जुड़ने से लेकर एयरबाइट, ड्रेमियो, डीबीटी और सुपरसेट के साथ अपनी पहली डेटा पाइपलाइन बनाने तक, डेटा प्लेटफ़ॉर्म के साथ आपकी पहली बातचीत के बारे में बताता है।

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

**अनुमानित समय**: 60-90 मिनट

---

## पूर्वावश्यकताएँ

आरंभ करने से पहले, सुनिश्चित करें कि:

- ✅ सभी सेवाएँ स्थापित और चल रही हैं
- ✅ आप वेब इंटरफेस तक पहुंच सकते हैं
- ✅ पायथन वर्चुअल वातावरण सक्षम है
- ✅ एसक्यूएल की बुनियादी समझ

**जाँचें कि सेवाएँ काम कर रही हैं:**
```bash
docker-compose ps
docker-compose -f docker-compose-airbyte.yml ps
```

---

## चरण 1: सभी सेवाओं तक पहुंचें

### सेवा यूआरएल

| सेवाएँ | यूआरएल | डिफ़ॉल्ट क्रेडेंशियल |
|---------|----------|----------------------|
| **एयरबाइट** | http://localhost:8000 | Airbyte@example.com / पासवर्ड |
| **ड्रेमियो** | http://localhost:9047 | एडमिन/एडमिन123 |
| **सुपरसेट** | http://localhost:8088 | व्यवस्थापक / व्यवस्थापक |
| **मिनियो** | http://localhost:9001 | मिनीएडमिन/मिनीएडमिन123 |

### पहला कनेक्शन

**एयरबाइट:**
1. http://localhost:8000 खोलें
2. सेटअप विज़ार्ड पूरा करें
3. कार्यस्थल का नाम सेट करें: "उत्पादन"
4. ओवरराइड प्राथमिकताएँ (बाद में कॉन्फ़िगरेशन संभव)

**ड्रेमियो:**
1. http://localhost:9047 खोलें
2. पहली पहुंच पर एक व्यवस्थापक उपयोगकर्ता बनाएं:
   - उपयोगकर्ता नाम: `admin`
   - ईमेल: `admin@example.com`
   - पासवर्ड: `admin123`
3. "आरंभ करें" पर क्लिक करें

**सुपरसेट:**
1. http://localhost:8088 खोलें
2. डिफ़ॉल्ट क्रेडेंशियल के साथ लॉग इन करें
3. पासवर्ड बदलें: सेटिंग्स → उपयोगकर्ता जानकारी → पासवर्ड रीसेट करें

---

## चरण 2: एयरबाइट में अपना पहला डेटा स्रोत कॉन्फ़िगर करें

### एक PostgreSQL स्रोत बनाएं

**परिदृश्य**: PostgreSQL डेटाबेस से डेटा निकालें।

1. **स्रोतों पर नेविगेट करें**
   - बाएं मेनू में "स्रोत" पर क्लिक करें
   - "+ नया स्रोत" पर क्लिक करें

2. **पोस्टग्रेएसक्यूएल चुनें**
   - "पोस्टग्रेएसक्यूएल" खोजें
   - "PostgreSQL" कनेक्टर पर क्लिक करें

3. **कनेक्शन कॉन्फ़िगर करें**
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

4. **परीक्षण करें और सहेजें**
   - "सेट अप सोर्स" पर क्लिक करें
   - कनेक्शन परीक्षण की प्रतीक्षा करें
   - स्रोत बनाया गया ✅

### नमूना डेटा बनाएं (वैकल्पिक)

यदि आपके पास अभी तक कोई डेटा नहीं है, तो उदाहरण तालिकाएँ बनाएँ:

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

## चरण 3: मिनियो एस3 गंतव्य कॉन्फ़िगर करें

### एक गंतव्य बनाएं

1. **गंतव्यों पर नेविगेट करें**
   - बाएं मेनू में "गंतव्य" पर क्लिक करें
   - "+ नया गंतव्य" पर क्लिक करें

2. **S3 चुनें**
   - "S3" खोजें
   - "S3" कनेक्टर पर क्लिक करें

3. **मिनियो को S3 के रूप में कॉन्फ़िगर करें**
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

4. **परीक्षण करें और सहेजें**
   - "सेट अप डेस्टिनेशन" पर क्लिक करें
   - कनेक्शन परीक्षण पास होना चाहिए ✅

---

## चरण 4: अपना पहला कनेक्शन बनाएं

### स्रोत को गंतव्य से लिंक करें

1. **कनेक्शन पर नेविगेट करें**
   - बाएं मेनू में "कनेक्शन" पर क्लिक करें
   - "+ नया कनेक्शन" पर क्लिक करें

2. **स्रोत चुनें**
   - "पोस्टग्रेएसक्यूएल प्रोडक्शन" चुनें
   - "मौजूदा स्रोत का उपयोग करें" पर क्लिक करें

3. **गंतव्य चुनें**
   - "मिनियो डेटा लेक" चुनें
   - "मौजूदा गंतव्य का उपयोग करें" पर क्लिक करें

4. **सिंक्रनाइज़ेशन कॉन्फ़िगर करें**
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

5. **सामान्यीकरण**
   ```yaml
   Normalization: Disabled
   # Nous utiliserons dbt pour les transformations
   ```

6. **बैकअप और सिंक्रोनाइज़**
   - "सेट अप कनेक्शन" पर क्लिक करें
   - पहला सिंक्रनाइज़ेशन निष्पादित करने के लिए "अभी सिंक करें" पर क्लिक करें
   - सिंक प्रगति की निगरानी करें

### मॉनिटर सिंक्रोनाइज़ेशन

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

**सिंक स्थिति जांचें:**
- स्थिति में "सफल" (हरा) दिखना चाहिए
- सिंक्रनाइज़ रिकॉर्ड: ~11 (5 ग्राहक + 6 ऑर्डर)
- विवरण के लिए लॉग देखें

---

## चरण 5: ड्रेमियो को मिनिओ से कनेक्ट करें

### ड्रेमियो में एक S3 स्रोत जोड़ें

1. **स्रोतों पर नेविगेट करें**
   - http://localhost:9047 खोलें
   - "स्रोत जोड़ें" (+ आइकन) पर क्लिक करें

2. **S3 चुनें**
   - "अमेज़ॅन S3" चुनें
   - मिनिओ के रूप में कॉन्फ़िगर करें:

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

3. **परीक्षण करें और सहेजें**
   - "सहेजें" पर क्लिक करें
   - ड्रेमियो मिनिओ बकेट का विश्लेषण करेगा

### डेटा ब्राउज़ करें

1. **मिनिओलेक स्रोत पर नेविगेट करें**
   - "मिनिओलेक" विकसित करें
   - "डेटालेक" बकेट विकसित करें
   - "रॉ-डेटा" फ़ोल्डर का विस्तार करें
   - "production_public" फ़ोल्डर देखें

2. **पूर्वावलोकन डेटा**
   - "ग्राहक" फ़ोल्डर पर क्लिक करें
   - Parquet फ़ाइल पर क्लिक करें
   - डेटा देखने के लिए "पूर्वावलोकन" पर क्लिक करें
   - डेटा PostgreSQL ✅ से मेल खाना चाहिए

### एक वर्चुअल डेटासेट बनाएं

1. **डेटा क्वेरी करें**
   ```sql
   -- Dans Dremio SQL Runner
   SELECT *
   FROM MinIOLake.datalake."raw-data".production_public.customers
   LIMIT 100;
   ```

2. **वीडीएस के रूप में सहेजें**
   - "इस रूप में देखें सहेजें" पर क्लिक करें
   - नाम: `vw_customers`
   - स्थान: `@admin` (आपका स्थान)
   - "सहेजें" पर क्लिक करें

3. **प्रारूप डेटा** (वैकल्पिक)
   - `vw_customers` पर क्लिक करें
   - कॉलम का नाम बदलने, प्रकार बदलने के लिए इंटरफ़ेस का उपयोग करें
   - उदाहरण: `customer_id` का नाम बदलकर `id` कर दें

---

## चरण 6: डीबीटी टेम्पलेट बनाएं

### डीबीटी प्रोजेक्ट आरंभ करें

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

### स्रोत परिभाषा बनाएँ

**फ़ाइल**: `dbt/models/sources.yml`

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

### एक स्टेजिंग टेम्पलेट बनाएं

**फ़ाइल**: `dbt/models/staging/stg_customers.sql`

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

**फ़ाइल**: `dbt/models/staging/stg_orders.sql`

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

### एक मार्ट टेम्पलेट बनाएं

**फ़ाइल**: `dbt/models/marts/fct_customer_orders.sql`

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

### डीबीटी मॉडल चलाएँ

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

### ड्रेमियो में चेक करें

```sql
-- Vérifier les vues de staging
SELECT * FROM "@admin".staging.stg_customers;
SELECT * FROM "@admin".staging.stg_orders;

-- Vérifier la table mart
SELECT * FROM "@admin".marts.fct_customer_orders
ORDER BY lifetime_value DESC;
```

---

## चरण 7: सुपरसेट में एक डैशबोर्ड बनाएं

### ड्रेमियो डेटाबेस जोड़ें

1. **डेटाबेस पर नेविगेट करें**
   - http://localhost:8088 खोलें
   - "डेटा" → "डेटाबेस" पर क्लिक करें
   - "+डेटाबेस" पर क्लिक करें

2. **ड्रेमियो का चयन करें**
   ```yaml
   Database name: Dremio Lakehouse
   SQLAlchemy URI: dremio+flight://admin:admin123@dremio:32010
   
   Test connection: ✅ Succès
   ```

3. **"कनेक्ट" पर क्लिक करें**

### एक डेटासेट बनाएं

1. **डेटासेट पर नेविगेट करें**
   - "डेटा" → "डेटासेट" पर क्लिक करें
   - "+ डेटासेट" पर क्लिक करें

2. **डेटासेट कॉन्फ़िगर करें**
   ```yaml
   Database: Dremio Lakehouse
   Schema: @admin.marts
   Table: fct_customer_orders
   ```

3. **“डेटासेट बनाएं और चार्ट बनाएं” पर क्लिक करें**

### चार्ट बनाएं

#### चार्ट 1: ग्राहक खंड (वृत्ताकार आरेख)

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

#### चार्ट 2: देश के अनुसार आय (बार चार्ट)

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

#### चार्ट 3: ग्राहक मेट्रिक्स (बड़ी संख्या)

```yaml
Chart Type: Big Number
Datasource: fct_customer_orders

Metric: COUNT(DISTINCT customer_id)
Subheader: Total Clients

Chart Options:
  Number Format: ,d
```

### डैशबोर्ड बनाएं

1. **डैशबोर्ड पर नेविगेट करें**
   - "डैशबोर्ड" पर क्लिक करें
   - "+ डैशबोर्ड" पर क्लिक करें

2. **डैशबोर्ड कॉन्फ़िगर करें**
   ```yaml
   Title: Analytique Clients
   Slug: customer-analytics
   Owners: admin
   Published: Yes
   ```

3. **ग्राफिक्स जोड़ें**
   - बनाए गए ग्राफ़िक्स को खींचें और छोड़ें
   - एक ग्रिड में व्यवस्थित करें:
     ```
     [ Total Clients      ]
     [ Segments ] [ Revenu par Pays ]
     ```

4. **फ़िल्टर जोड़ें** (वैकल्पिक)
   - "फ़िल्टर जोड़ें" पर क्लिक करें
   - इसके अनुसार फ़िल्टर करें: देश_कोड
   - सभी चार्ट पर लागू करें

5. **डैशबोर्ड सहेजें**

---

## चरण 8: पूरी पाइपलाइन की जाँच करें

### शुरू से अंत तक परीक्षण

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

### नया डेटा जोड़ें

1. **PostgreSQL में नए रिकॉर्ड डालें**
   ```sql
   docker exec -it postgres psql -U postgres -d dremio_db
   
   INSERT INTO customers (name, email, country) VALUES
       ('Emma Wilson', 'emma@example.com', 'USA'),
       ('Li Wei', 'li@example.com', 'China');
   
   INSERT INTO orders (customer_id, amount, status) VALUES
       (6, 500.00, 'completed'),
       (7, 350.00, 'pending');
   ```

2. **ट्रिगर एयरबाइट सिंक**
   - एयरबाइट इंटरफ़ेस खोलें
   - कनेक्शन "PostgreSQL → MiniIO" पर जाएं
   - "अभी सिंक करें" पर क्लिक करें
   - अंत की प्रतीक्षा करें ✅

3. **डीबीटी चलाएँ**
   ```bash
   cd dbt
   dbt run
   ```

4. **सुपरसेट डैशबोर्ड को रीफ्रेश करें**
   - डैशबोर्ड खोलें
   - "रीफ्रेश" बटन पर क्लिक करें
   - नया डेटा दिखना चाहिए ✅

### डेटा प्रवाह की जाँच करें

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

## चरण 9: पाइपलाइन को स्वचालित करें

### एयरबाइट सिंक शेड्यूल करें

प्रत्येक 24 घंटे में 02:00 बजे चलने के लिए पहले से ही कॉन्फ़िगर किया गया है।

सम्पादन के लिए:
1. एयरबाइट में कनेक्शन खोलें
2. "सेटिंग्स" टैब पर जाएं
3. अद्यतन "प्रतिकृति आवृत्ति"
4. सहेजें

### डीबीटी निष्पादन अनुसूची

**विकल्प 1: क्रॉन जॉब (लिनक्स)**
```bash
# Éditer crontab
crontab -e

# Ajouter exécution dbt à 2h30 quotidiennement (après sync Airbyte)
30 2 * * * cd /path/to/dremiodbt/dbt && /path/to/venv/bin/dbt run >> /var/log/dbt.log 2>&1
```

**विकल्प 2: पायथन स्क्रिप्ट**

**फ़ाइल**: `scripts/run_pipeline.py`
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

### डॉकर कंपोज़ के साथ शेड्यूल

**फ़ाइल**: `docker-compose.scheduler.yml`
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

## अगले कदम

बधाई हो! आपने संपूर्ण एंड-टू-एंड डेटा पाइपलाइन बना ली है। 🎉

### और अधिक जानें

1. **एयरबाइट एडवांस्ड** - [एयरबाइट इंटीग्रेशन गाइड](../guides/airbyte-integration.md)
2. **ड्रेमियो ऑप्टिमाइज़ेशन** - [ड्रेमियो सेटअप गाइड](../guides/dremio-setup.md)
3. **जटिल डीबीटी मॉडल** - [डीबीटी विकास गाइड](../guides/dbt-development.md)
4. **उन्नत डैशबोर्ड** - [सुपरसेट डैशबोर्ड गाइड](../guides/superset-dashboards.md)
5. **डेटा गुणवत्ता** - [डेटा गुणवत्ता गाइड](../guides/data-quality.md)

### समस्या निवारण

यदि आपको कोई समस्या है, तो देखें:
- [समस्या निवारण मार्गदर्शिका](../guides/troubleshooting.md)
- [इंस्टॉलेशन गाइड](इंस्टॉलेशन.md#समस्या निवारण)
- [कॉन्फ़िगरेशन गाइड](configuration.md)

---

## सारांश

आपने सफलतापूर्वक किया है:

- ✅ प्लेटफ़ॉर्म की 7 सेवाओं तक पहुंचें
- ✅ एक एयरबाइट स्रोत कॉन्फ़िगर करें (PostgreSQL)
- ✅ एक एयरबाइट गंतव्य कॉन्फ़िगर करें (MinIO S3)
- ✅ अपना पहला एयरबाइट कनेक्शन बनाएं
- ✅ ड्रेमियो को मिनिओ से कनेक्ट करें
- ✅ डीबीटी टेम्प्लेट बनाएं (स्टेजिंग + मार्ट)
- ✅ एक सुपरसेट डैशबोर्ड बनाएं
- ✅ एंड-टू-एंड डेटा प्रवाह की जाँच करें
- ✅ स्वचालित पाइपलाइन निष्पादन

**आपका डेटा प्लेटफ़ॉर्म अब चालू है!** 🚀

---

**प्रथम चरण मार्गदर्शिका संस्करण**: 3.2.0  
**अंतिम अद्यतन**: 2025-10-16  
**द्वारा रखरखाव**: डेटा प्लेटफ़ॉर्म टीम