# Guide Tableaux de Bord Apache Superset

**Version**: 3.2.0  
**Dernière Mise à Jour**: 16 octobre 2025  
**Langue**: Français

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Configuration Initiale](#configuration-initiale)
3. [Connexion Sources de Données](#connexion-sources-de-données)
4. [Création Graphiques](#création-graphiques)
5. [Construction Tableaux de Bord](#construction-tableaux-de-bord)
6. [Fonctionnalités Avancées](#fonctionnalités-avancées)
7. [Sécurité et Permissions](#sécurité-et-permissions)
8. [Optimisation Performance](#optimisation-performance)
9. [Intégration et Partage](#intégration-et-partage)
10. [Bonnes Pratiques](#bonnes-pratiques)

---

## Vue d'ensemble

Apache Superset est une application web moderne de business intelligence prête pour l'entreprise qui permet aux utilisateurs d'explorer et de visualiser les données via des tableaux de bord et graphiques intuitifs.

### Fonctionnalités Clés

| Fonctionnalité | Description | Bénéfice |
|----------------|-------------|----------|
| **IDE SQL** | Éditeur SQL interactif avec auto-complétion | Analyse ad-hoc |
| **Visualisations Riches** | Plus de 50 types de graphiques | Représentation données diverse |
| **Constructeur Tableaux de Bord** | Interface glisser-déposer | Création tableaux de bord facile |
| **Mise en Cache** | Cache résultats requêtes | Temps chargement rapides |
| **Sécurité** | Sécurité niveau ligne, accès basé rôles | Gouvernance données |
| **Alertes** | Notifications email/Slack automatisées | Surveillance proactive |

### Intégration Architecture

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

## Configuration Initiale

### Première Connexion

Accéder à Superset sur `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Note de Sécurité**: Changer le mot de passe par défaut immédiatement après la première connexion.

### Configuration Initiale

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

### Fichier Configuration

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

## Connexion Sources de Données

### Connexion à Dremio

#### Étape 1: Installer Pilote Base de Données Dremio

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Étape 2: Ajouter Base de Données Dremio

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Configuration**:
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

#### Étape 3: Tester Connexion

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Connexion à PostgreSQL

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

### Connexion à Elasticsearch

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

## Création Graphiques

### Workflow Création Graphique

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

### Sélection Type Graphique

| Type Graphique | Meilleur Pour | Cas d'Usage Exemple |
|----------------|---------------|---------------------|
| **Graphique Linéaire** | Tendances temporelles | Tendance revenu quotidien |
| **Graphique Barres** | Comparaisons | Revenu par catégorie produit |
| **Graphique Secteurs** | Part du total | Part marché par région |
| **Tableau** | Données détaillées | Liste clients avec métriques |
| **Grand Nombre** | Métrique unique | Revenu YTD total |
| **Carte Chaleur** | Détection motifs | Ventes par jour/heure |
| **Nuage Points** | Corrélations | Valeur client vs fréquence |
| **Diagramme Sankey** | Analyse flux | Parcours utilisateur |

### Exemple: Graphique Linéaire (Tendance Revenu)

#### Étape 1: Créer Dataset

```
Interface → Données → Datasets → + Dataset
```

**Configuration**:
- **Base de Données**: Dremio
- **Schéma**: Production.Marts
- **Table**: mart_daily_revenue

#### Étape 2: Créer Graphique

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Paramètres**:
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

**SQL Généré**:
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

### Exemple: Graphique Barres (Top Clients)

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

### Exemple: Tableau Croisé Dynamique

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

### Exemple: Grand Nombre avec Tendance

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

## Construction Tableaux de Bord

### Processus Création Tableau de Bord

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

### Étape 1: Créer Tableau de Bord

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Paramètres Tableau de Bord**:
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

### Étape 2: Ajouter Graphiques

Glisser-déposer graphiques depuis panneau gauche ou créer nouveaux:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Étape 3: Conception Disposition

**Système Grille**:
- 12 colonnes de large
- Les graphiques s'accrochent à la grille
- Glisser pour redimensionner et repositionner

**Exemple Disposition**:
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

### Étape 4: Ajouter Filtres Tableau de Bord

```
Tableau de Bord → Éditer → + Filtre
```

**Filtre Plage Date**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Filtre Catégoriel**:
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

**Filtre Numérique**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Étape 5: Filtrage Croisé

Activer filtrage croisé tableau de bord:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Configuration**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Expérience Utilisateur**:
- Clic sur barre → filtre tout le tableau de bord
- Clic sur part secteur → met à jour graphiques liés
- Effacer filtre → réinitialise à vue par défaut

---

## Fonctionnalités Avancées

### SQL Lab

Éditeur SQL interactif pour requêtes ad-hoc.

#### Exécuter Requête

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

**Fonctionnalités**:
- Auto-complétion pour tables et colonnes
- Historique requêtes
- Onglets multiples
- Export résultats (CSV, JSON)
- Sauvegarder requête pour réutilisation

#### Créer Table depuis Requête (CTAS)

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

### Templates Jinja

SQL dynamique avec templates Jinja2:

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

**Variables Template**:
- `{{ from_dttm }}` - Début plage date
- `{{ to_dttm }}` - Fin plage date
- `{{ filter_values('column') }}` - Valeurs filtre sélectionnées
- `{{ current_username }}` - Utilisateur connecté

### Alertes et Rapports

#### Créer Alerte

```
Interface → Alertes & Rapports → + Alerte
```

**Configuration**:
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

#### Créer Rapport

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

### Plugins Visualisation Personnalisés

Créer types graphiques personnalisés:

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

Construire et installer:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Sécurité et Permissions

### Contrôle d'Accès Basé Rôles (RBAC)

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

### Rôles Intégrés

| Rôle | Permissions | Cas d'Usage |
|------|-------------|-------------|
| **Admin** | Toutes permissions | Administrateurs système |
| **Alpha** | Créer, éditer, supprimer tableaux de bord/graphiques | Analystes données |
| **Gamma** | Voir tableaux de bord, exécuter requêtes SQL Lab | Utilisateurs métier |
| **sql_lab** | Accès SQL Lab uniquement | Data scientists |
| **Public** | Voir tableaux de bord publics uniquement | Utilisateurs anonymes |

### Créer Rôle Personnalisé

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Exemple: Rôle Analyste Marketing**
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

### Sécurité Niveau Ligne (RLS)

Restreindre données selon attributs utilisateur:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Exemple: RLS Basée Région**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Exemple: RLS Basée Client**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Sécurité Connexion Base de Données

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

## Optimisation Performance

### Mise en Cache Requêtes

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

**Stratégie Cache**:
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

### Requêtes Asynchrones

Activer exécution requêtes async pour requêtes longues:

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

### Optimisation Requête Base de Données

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

### Optimisation Chargement Tableau de Bord

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

### Surveillance Performance

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

## Intégration et Partage

### Tableaux de Bord Publics

Rendre tableaux de bord accessibles sans connexion:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**URL Publique**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Intégration Iframe

Intégrer tableaux de bord dans applications externes:

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

**Paramètres Intégration**:
- `standalone=1` - Masquer navigation
- `show_filters=0` - Masquer panneau filtres
- `show_title=0` - Masquer titre tableau de bord

### Authentification Jeton Invité

Accès programmatique pour tableaux de bord intégrés:

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

### Exporter Tableaux de Bord

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Bonnes Pratiques

### Conception Tableau de Bord

1. **Hiérarchie Disposition**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Cohérence Couleurs**
   - Utiliser schéma couleurs cohérent sur tous tableaux de bord
   - Vert pour métriques positives, rouge pour négatives
   - Couleurs marque pour catégories

3. **Performance**
   - Limiter graphiques par tableau de bord (< 15)
   - Utiliser niveaux agrégation appropriés
   - Activer cache pour données statiques
   - Définir limites lignes raisonnables

4. **Interactivité**
   - Ajouter filtres significatifs
   - Activer filtrage croisé pour exploration
   - Fournir capacités drill-down

### Sélection Graphique

| Type Données | Graphiques Recommandés | Éviter |
|--------------|------------------------|--------|
| **Séries Temporelles** | Linéaire, Aires | Secteurs, Anneau |
| **Comparaison** | Barres, Colonnes | Linéaire (peu points données) |
| **Part du Total** | Secteurs, Anneau, Treemap | Barres (trop catégories) |
| **Distribution** | Histogramme, Box Plot | Secteurs |
| **Corrélation** | Nuage Points, Bulles | Barres |
| **Géographique** | Carte, Choroplèthe | Tableau |

### Optimisation Requête

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

### Sécurité

1. **Contrôle d'Accès**
   - Utiliser RBAC pour gestion utilisateurs
   - Implémenter RLS pour isolation données
   - Restreindre connexions base de données par rôle

2. **Gouvernance Données**
   - Documenter propriété datasets
   - Définir plannings rafraîchissement données
   - Surveiller performance requêtes

3. **Conformité**
   - Masquer PII dans visualisations
   - Auditer accès tableaux de bord
   - Implémenter politiques rétention données

---

## Résumé

Ce guide complet Superset a couvert :

- **Configuration**: Installation, configuration, connexions base de données
- **Graphiques**: Plus de 50 types graphiques, configuration, génération SQL
- **Tableaux de Bord**: Conception disposition, filtres, filtrage croisé
- **Fonctionnalités Avancées**: SQL Lab, templates Jinja, alertes, plugins personnalisés
- **Sécurité**: RBAC, RLS, sécurité connexion base de données
- **Performance**: Mise en cache, requêtes async, optimisation requêtes
- **Intégration**: Tableaux de bord publics, intégration iframe, jetons invités
- **Bonnes Pratiques**: Principes conception, sélection graphiques, sécurité

Points clés à retenir :
- Superset se connecte à Dremio pour analytique haute performance
- Bibliothèque visualisations riche supporte cas d'usage divers
- Mise en cache et requêtes async intégrées assurent tableaux de bord rapides
- RBAC et RLS permettent analytique self-service sécurisée
- Capacités intégration permettent intégration avec applications externes

**Documentation Associée:**
- [Guide Configuration Dremio](./dremio-setup.md)
- [Architecture: Flux Données](../architecture/data-flow.md)
- [Tutoriel Premiers Pas](../getting-started/first-steps.md)
- [Guide Qualité Données](./data-quality.md)

---

**Version**: 3.2.0  
**Dernière Mise à Jour**: 16 octobre 2025
