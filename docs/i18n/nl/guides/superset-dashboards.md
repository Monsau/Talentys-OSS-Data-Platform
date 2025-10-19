# Apache Superset Dashboards-gids

**Versie**: 3.2.0  
**Laatste update**: 16 oktober 2025  
**Taal**: Frans

## Inhoudsopgave

1. [Overzicht](#overzicht)
2. [Initiële configuratie](#initial-configuration)
3. [Verbinding met gegevensbronnen](#data-sources-connection)
4. [Grafische creatie](#graphics-creation)
5. [Dashboardconstructie](#dashboard-constructie)
6. [Geavanceerde functies](#advanced-features)
7. [Beveiliging en machtigingen](#security-and-permissions)
8. [Prestatieoptimalisatie](#performance-optimalisatie)
9. [Integratie en delen](#integration-and-sharing)
10. [Goede praktijken](#goede praktijken)

---

## Overzicht

Apache Superset is een moderne, bedrijfsklare business intelligence-webapplicatie waarmee gebruikers gegevens kunnen verkennen en visualiseren via intuïtieve dashboards en grafieken.

### Belangrijkste kenmerken

| Kenmerk | Beschrijving | Winst |
|---------------|---------|---------|
| **SQL-IDE** | Interactieve SQL-editor met automatische aanvulling | Ad-hocanalyse |
| **Rijke visualisaties** | 50+ diagramtypen | Diverse gegevensweergave |
| **Dashboardbouwer** | Slepen-en-neerzetten-interface | Eenvoudig dashboard maken |
| **Caching** | Zoekresultaten in cache opslaan | Snelle laadtijden |
| **Beveiliging** | Beveiliging op rijniveau, op rollen gebaseerde toegang | Gegevensbeheer |
| **Waarschuwingen** | Geautomatiseerde e-mail/Slack-meldingen | Proactief toezicht |

### Architectuurintegratie

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

## Initiële configuratie

### Eerste verbinding

Toegang tot Superset op `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Veiligheidsopmerking**: Wijzig het standaardwachtwoord onmiddellijk na de eerste keer inloggen.

### Initiële installatie

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

### Configuratiebestand

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

## Verbindingsgegevensbronnen

### Log in op Dremio

#### Stap 1: Installeer het Dremio-databasestuurprogramma

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Stap 2: Dremio-database toevoegen

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Configuratie**:
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

#### Stap 3: Test de verbinding

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Verbinding maken met PostgreSQL

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

### Verbinding maken met Elasticsearch

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

## Grafische creatie

### Grafische creatieworkflow

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

### Selectie grafisch type

| Grafisch type | Beste voor | Gebruiksvoorbeeld |
|---------------|---------------|--------------------|
| **Lineaire grafiek** | Tijdelijke trends | Dagelijkse inkomenstrend |
| ** Staafdiagram ** | Vergelijkingen | Omzet per productcategorie |
| **Sectorendiagram** | Aandeel van totaal | Marktaandeel per regio |
| **Tabel** | Gedetailleerde gegevens | Klantenlijst met statistieken |
| **Groot aantal** | Enkele statistiek | Totaal YTD-inkomen |
| ** Warmtekaart ** | Patroondetectie | Verkoop per dag/uur |
| **Puntenwolk** | Correlaties | Klantwaarde versus frequentie |
| **Sankey-diagram** | Stromingsanalyse | Gebruikerstraject |

### Voorbeeld: lineaire grafiek (inkomenstrend)

#### Stap 1: Gegevensset maken

```
Interface → Données → Datasets → + Dataset
```

**Configuratie**:
- **Database**: Dremio
- **Diagram**: Productie.Marts
- **Tabel**: mart_daily_revenue

#### Stap 2: Maak een diagram

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Parameters**:
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

**SQL gegenereerd**:
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

### Voorbeeld: staafdiagram (topklanten)

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

### Voorbeeld: draaitabel

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

### Voorbeeld: groot getal met trend

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

## Bouwdashboards

### Dashboardcreatieproces

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

### Stap 1: Dashboard maken

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Dashboardinstellingen**:
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

### Stap 2: Afbeeldingen toevoegen

Sleep afbeeldingen vanuit het linkerpaneel en zet ze neer of maak nieuwe:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Stap 3: Ontwerplay-out

**Rastersysteem**:
- 12 kolommen breed
- Grafische afbeeldingen passen op het raster
- Veeg om het formaat te wijzigen en te verplaatsen

**Voorbeeldindeling**:
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

### Stap 4: Dashboardfilters toevoegen

```
Tableau de Bord → Éditer → + Filtre
```

**Datumbereikfilter**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Categoriefilter**:
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

**Digitaal filter**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Stap 5: Kruisfiltering

Kruisfiltering op dashboard inschakelen:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Configuratie**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Gebruikerservaring**:
- Klik op de balk → filter het hele dashboard
- Klik op sectoraandeel → updates van gerelateerde afbeeldingen
- Wis filter → reset naar standaardweergave

---

## Geavanceerde functies

### SQL-lab

Interactieve SQL-editor voor ad-hocquery's.

#### Query uitvoeren

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

**Functies**:
- Automatische aanvulling voor tabellen en kolommen
- Geschiedenis opvragen
- Meerdere tabbladen
- Resultaten exporteren (CSV, JSON)
- Bewaar zoekopdracht voor hergebruik

#### Tabel maken op basis van query (CTAS)

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

### Jinja-sjablonen

Dynamische SQL met Jinja2-sjablonen:

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

**Sjabloonvariabelen**:
- `{{ from_dttm }}` - Begindatumbereik
- `{{ to_dttm }}` - Einde van datumbereik
- `{{ filter_values('column') }}` - Geselecteerde filterwaarden
- `{{ current_username }}` - Ingelogde gebruiker

### Waarschuwingen en rapporten

#### Melding maken

```
Interface → Alertes & Rapports → + Alerte
```

**Configuratie**:
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

#### Rapport maken

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

### Aangepaste visualisatieplug-ins

Aangepaste grafische typen maken:

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

Bouw en installeer:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Beveiliging en machtigingen

### Op rollen gebaseerde toegangscontrole (RBAC)

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

### Geïntegreerde rollen

| Rol | Machtigingen | Gebruiksscenario's |
|-----|-------------|------------|
| **Beheer** | Alle rechten | Systeembeheerders |
| **Alfa** | Dashboards/grafieken maken, bewerken en verwijderen | Data-analisten |
| **Gamma** | Dashboards bekijken, SQL Lab-query's uitvoeren | Zakelijke gebruikers |
| **sql_lab** | Alleen toegang tot SQL Lab | Datawetenschappers |
| **Openbaar** | Alleen openbare dashboards bekijken | Anonieme gebruikers |

### Aangepaste rol maken

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Voorbeeld: rol van marketinganalist**
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

### Lijnniveauveiligheid (RLS)

Beperk gegevens op basis van gebruikerskenmerken:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Voorbeeld: regiogebaseerde RLS**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Voorbeeld: klantgebaseerde RLS**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Beveiliging van databaseverbindingen

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

## Prestatieoptimalisatie

### Caching-query's

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

**Cachestrategie**:
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

### Asynchrone verzoeken

Schakel asynchrone query-uitvoering in voor lange query's:

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

### Optimalisatie van databasequery's

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

### Dashboard-laadoptimalisatie

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

### Prestatiebewaking

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

## Integratie en delen

### Openbare dashboards

Dashboards toegankelijk maken zonder verbinding:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**Openbare URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Iframe-integratie

Integreer dashboards in externe applicaties:

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

**Integratie-instellingen**:
- `standalone=1` - Navigatie verbergen
- `show_filters=0` - Filterpaneel verbergen
- `show_title=0` - Dashboardtitel verbergen

### Gasttokenverificatie

Programmatische toegang voor geïntegreerde dashboards:

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

### Dashboards exporteren

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Beste praktijken

### Dashboardontwerp

1. **Indelingshiërarchie**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Kleurconsistentie**
   - Gebruik een consistent kleurenschema op alle dashboards
   - Groen voor positieve statistieken, rood voor negatief
   - Merkkleuren voor categorieën

3. **Prestaties**
   - Beperk afbeeldingen per dashboard (< 15)
   - Gebruik geschikte aggregatieniveaus
   - Schakel cache voor statische gegevens in
   - Stel redelijke lijnlimieten in

4. **Interactiviteit**
   - Voeg betekenisvolle filters toe
   - Schakel kruisfiltering in voor verkenning
   - Bied drill-downmogelijkheden aan

### Grafische selectie

| Gegevenstype | Aanbevolen grafieken | Vermijd |
|-------------|-------------------------|--------|
| **Tijdreeks** | Lineair, gebieden | Sectoren, Ring |
| **Vergelijking** | Staven, kolommen | Lineair (weinig datapunten) |
| **Aandeel van totaal** | Sectoren, Ring, Boomkaart | Bars (te categorieën) |
| **Distributie** | Histogram, boxplot | Sectoren |
| **Correlatie** | Wolkenpunten, bubbels | Staven |
| **Geografisch** | Kaart, Choropleth | Tabel |

### Zoekopdrachtoptimalisatie

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

### Beveiliging

1. **Toegangscontrole**
   - Gebruik RBAC voor gebruikersbeheer
   - Implementeer RLS voor gegevensisolatie
   - Beperk databaseverbindingen per rol

2. **Gegevensbeheer**
   - Documentgegevenssets eigendom
   - Definieer schema's voor het vernieuwen van gegevens
   - Controleer de queryprestaties

3. **Naleving**
   - Verberg PII in visualisaties
   - Toegang tot auditdashboard
   - Implementeer beleid voor het bewaren van gegevens

---

## Samenvatting

Deze uitgebreide Superset-gids behandelt:

- **Configuratie**: installatie, configuratie, databaseverbindingen
- **Grafiek**: meer dan 50 grafische typen, configuratie, SQL-generatie
- **Dashboards**: lay-outontwerp, filters, kruisfiltering
- **Geavanceerde functies**: SQL Lab, Jinja-sjablonen, waarschuwingen, aangepaste plug-ins
- **Beveiliging**: RBAC, RLS, beveiliging van databaseverbindingen
- **Prestaties**: caching, asynchrone zoekopdrachten, zoekopdrachtoptimalisatie
- **Integratie**: openbare dashboards, iframe-integratie, gasttokens
- **Goede praktijken**: ontwerpprincipes, grafische selectie, beveiliging

Belangrijke punten om te onthouden:
- Superset maakt verbinding met Dremio voor krachtige analyses
- Rijke visualisatiebibliotheek ondersteunt verschillende gebruiksscenario's
- Ingebouwde caching en asynchrone queries zorgen voor snelle dashboards
- RBAC en RLS maken veilige selfservice-analyses mogelijk
- Integratiemogelijkheden maken integratie met externe applicaties mogelijk

**Gerelateerde documentatie:**
- [Dremio Installatiehandleiding](./dremio-setup.md)
- [Architectuur: gegevensstroom](../architecture/data-flow.md)
- [Eerste stappen-tutorial](../getting-started/first-steps.md)
- [Handleiding gegevenskwaliteit](./data-quality.md)

---

**Versie**: 3.2.0  
**Laatste update**: 16 oktober 2025