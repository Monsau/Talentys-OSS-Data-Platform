# Apache Superset Dashboards-Handbuch

**Version**: 3.2.0  
**Letzte Aktualisierung**: 16. Oktober 2025  
**Sprache**: Französisch

## Inhaltsverzeichnis

1. [Übersicht](#Übersicht)
2. [Anfangskonfiguration](#initial-configuration)
3. [Datenquellenverbindung](#data-sources-connection)
4. [Grafikerstellung](#graphics-creation)
5. [Dashboard-Konstruktion](#dashboard-construction)
6. [Erweiterte Funktionen](#advanced-features)
7. [Sicherheit und Berechtigungen](#security-and-permissions)
8. [Leistungsoptimierung](#leistungsoptimierung)
9. [Integration und Teilen](#integration-and-sharing)
10. [Gute Praktiken](#good-practices)

---

## Übersicht

Apache Superset ist eine moderne, unternehmenstaugliche Business-Intelligence-Webanwendung, die es Benutzern ermöglicht, Daten über intuitive Dashboards und Diagramme zu erkunden und zu visualisieren.

### Hauptmerkmale

| Funktion | Beschreibung | Gewinn |
|----------------|---------|---------|
| **SQL-IDE** | Interaktiver SQL-Editor mit Autovervollständigung | Ad-hoc-Analyse |
| **Reichhaltige Visualisierungen** | Über 50 Diagrammtypen | Verschiedene Datendarstellung |
| **Dashboard Builder** | Drag-and-Drop-Schnittstelle | Einfache Dashboard-Erstellung |
| **Caching** | Cache-Ergebnisabfragen | Schnelle Ladezeiten |
| **Sicherheit** | Sicherheit auf Zeilenebene, rollenbasierter Zugriff | Datenverwaltung |
| **Benachrichtigungen** | Automatisierte E-Mail-/Slack-Benachrichtigungen | Proaktive Überwachung |

### Architekturintegration

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

## Erstkonfiguration

### Erste Verbindung

Greifen Sie auf die Obermenge von `http://localhost:8088` zu:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Sicherheitshinweis**: Ändern Sie das Standardkennwort sofort nach der ersten Anmeldung.

### Ersteinrichtung

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

### Konfigurationsdatei

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

## Verbindungsdatenquellen

### Melden Sie sich bei Dremio an

#### Schritt 1: Dremio-Datenbanktreiber installieren

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Schritt 2: Dremio-Datenbank hinzufügen

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Konfiguration**:
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

#### Schritt 3: Verbindung testen

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Verbindung zu PostgreSQL herstellen

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

### Verbindung zu Elasticsearch herstellen

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

## Grafikerstellung

### Grafikerstellungs-Workflow

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

### Auswahl Grafiktyp

| Grafiktyp | Am besten für | Anwendungsfallbeispiel |
|----------------|--------------|-------|
| **Lineares Diagramm** | Zeitliche Trends | Tägliche Einkommensentwicklung |
| **Balkendiagramm** | Vergleiche | Umsatz nach Produktkategorie |
| **Sektordiagramm** | Anteil an der Gesamtmenge | Marktanteil nach Regionen |
| **Tabelle** | Detaillierte Daten | Kundenliste mit Kennzahlen |
| **Große Zahl** | Einzelne Metrik | Gesamtertrag YTD |
| **Wärmekarte** | Mustererkennung | Umsatz pro Tag/Stunde |
| **Punktwolke** | Korrelationen | Kundenwert vs. Häufigkeit |
| **Sankey-Diagramm** | Strömungsanalyse | Benutzerreise |

### Beispiel: Lineares Diagramm (Einkommenstrend)

#### Schritt 1: Datensatz erstellen

```
Interface → Données → Datasets → + Dataset
```

**Konfiguration**:
- **Datenbank**: Dremio
- **Diagramm**: Production.Marts
- **Tabelle**: mart_daily_revenue

#### Schritt 2: Diagramm erstellen

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Parameter**:
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

**SQL generiert**:
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

### Beispiel: Balkendiagramm (Top-Kunden)

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

### Beispiel: PivotTable

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

### Beispiel: Große Zahl mit Trend

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

## Bau-Dashboards

### Dashboard-Erstellungsprozess

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

### Schritt 1: Dashboard erstellen

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Dashboard-Einstellungen**:
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

### Schritt 2: Grafiken hinzufügen

Ziehen Sie Grafiken per Drag-and-Drop aus dem linken Bereich oder erstellen Sie neue:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Schritt 3: Layout entwerfen

**Gittersystem**:
- 12 Spalten breit
- Grafiken werden am Raster ausgerichtet
- Wischen Sie, um die Größe zu ändern und neu zu positionieren

**Beispiellayout**:
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

### Schritt 4: Dashboard-Filter hinzufügen

```
Tableau de Bord → Éditer → + Filtre
```

**Datumsbereichsfilter**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Kategoriefilter**:
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

**Digitalfilter**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Schritt 5: Kreuzfilterung

Dashboard-Kreuzfilterung aktivieren:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Konfiguration**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Benutzererfahrung**:
- Klicken Sie auf Leiste → Filtern Sie das gesamte Dashboard
- Klicken Sie auf Sektoranteil → Aktualisiert verwandte Grafiken
- Filter löschen → Zurücksetzen auf Standardansicht

---

## Erweiterte Funktionen

### SQL-Labor

Interaktiver SQL-Editor für Ad-hoc-Abfragen.

#### Abfrage ausführen

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

**Merkmale**:
- Automatische Vervollständigung für Tabellen und Spalten
- Anforderungsverlauf
- Mehrere Registerkarten
- Ergebnisse exportieren (CSV, JSON)
- Abfrage zur Wiederverwendung speichern

#### Tabelle aus Abfrage erstellen (CTAS)

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

### Jinja-Vorlagen

Dynamisches SQL mit Jinja2-Vorlagen:

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

**Vorlagenvariablen**:
- `{{ from_dttm }}` – Startdatumsbereich
- `{{ to_dttm }}` – Ende des Datumsbereichs
- `{{ filter_values('column') }}` - Ausgewählte Filterwerte
- `{{ current_username }}` – Angemeldeter Benutzer

### Warnungen und Berichte

#### Benachrichtigung erstellen

```
Interface → Alertes & Rapports → + Alerte
```

**Konfiguration**:
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

#### Bericht erstellen

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

### Benutzerdefinierte Visualisierungs-Plugins

Erstellen Sie benutzerdefinierte Grafiktypen:

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

Erstellen und installieren:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Sicherheit und Berechtigungen

### Rollenbasierte Zugriffskontrolle (RBAC)

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

### Integrierte Rollen

| Rolle | Berechtigungen | Anwendungsfälle |
|------|-------------|-------------|
| **Administrator** | Alle Berechtigungen | Systemadministratoren |
| **Alpha** | Dashboards/Diagramme erstellen, bearbeiten, löschen | Datenanalysten |
| **Gamma** | Dashboards anzeigen, SQL Lab-Abfragen ausführen | Geschäftsanwender |
| **sql_lab** | Nur SQL Lab-Zugriff | Datenwissenschaftler |
| **Öffentlich** | Nur öffentliche Dashboards anzeigen | Anonyme Benutzer |

### Erstellen Sie eine benutzerdefinierte Rolle

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Beispiel: Rolle eines Marketinganalysten**
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

### Line Level Safety (RLS)

Daten nach Benutzerattributen einschränken:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Beispiel: Regionsbasiertes RLS**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Beispiel: Clientbasiertes RLS**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Datenbankverbindungssicherheit

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

## Leistungsoptimierung

### Caching-Abfragen

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

**Cache-Strategie**:
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

### Asynchrone Anfragen

Aktivieren Sie die asynchrone Abfrageausführung für lange Abfragen:

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

### Datenbankabfrageoptimierung

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

### Dashboard-Ladeoptimierung

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

### Leistungsüberwachung

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

## Integration und Teilen

### Öffentliche Dashboards

Machen Sie Dashboards ohne Verbindung zugänglich:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**Öffentliche URL**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Iframe-Integration

Integrieren Sie Dashboards in externe Anwendungen:

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

**Integrationseinstellungen**:
- `standalone=1` - Navigation ausblenden
- `show_filters=0` - Filterfeld ausblenden
- `show_title=0` – Dashboard-Titel ausblenden

### Gast-Token-Authentifizierung

Programmgesteuerter Zugriff für integrierte Dashboards:

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

### Dashboards exportieren

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Best Practices

### Dashboard-Design

1. **Layouthierarchie**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Farbkonsistenz**
   - Verwenden Sie auf allen Dashboards ein einheitliches Farbschema
   - Grün für positive Kennzahlen, rot für negative
   - Markenfarben für Kategorien

3. **Leistung**
   - Grafiken pro Dashboard begrenzen (< 15)
   - Verwenden Sie geeignete Aggregationsebenen
   - Cache für statische Daten aktivieren
   - Legen Sie angemessene Zeilenlimits fest

4. **Interaktivität**
   - Fügen Sie aussagekräftige Filter hinzu
   - Aktivieren Sie die Kreuzfilterung zur Erkundung
   - Bereitstellung von Drilldown-Funktionen

### Grafikauswahl

| Datentyp | Empfohlene Diagramme | Vermeiden |
|--------------|-------------|--------|
| **Zeitreihe** | Linear, Flächen | Sektoren, Ring |
| **Vergleich** | Balken, Säulen | Linear (wenige Datenpunkte) |
| **Anteil am Gesamtergebnis** | Sektoren, Ring, Baumkarte | Bars (zu Kategorien) |
| **Verteilung** | Histogramm, Boxplot | Sektoren |
| **Korrelation** | Wolkenpunkte, Blasen | Balken |
| **Geografisch** | Karte, Choropleth | Tabelle |

### Abfrageoptimierung

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

### Sicherheit

1. **Zugriffskontrolle**
   - Verwenden Sie RBAC für die Benutzerverwaltung
   - Implementieren Sie RLS zur Datenisolierung
   - Beschränken Sie Datenbankverbindungen nach Rolle

2. **Daten-Governance**
   – Eigenschaft für Dokumentdatensätze
   - Definieren Sie Zeitpläne für die Datenaktualisierung
   - Überwachen Sie die Abfrageleistung

3. **Compliance**
   - PII in Visualisierungen ausblenden
   - Zugriff auf das Audit-Dashboard
   - Implementieren Sie Richtlinien zur Datenaufbewahrung

---

## Zusammenfassung

Dieser umfassende Superset-Leitfaden behandelt Folgendes:

- **Konfiguration**: Installation, Konfiguration, Datenbankverbindungen
- **Grafik**: Mehr als 50 Grafiktypen, Konfiguration, SQL-Generierung
- **Dashboards**: Layoutdesign, Filter, Kreuzfilterung
- **Erweiterte Funktionen**: SQL Lab, Jinja-Vorlagen, Warnungen, benutzerdefinierte Plugins
- **Sicherheit**: RBAC, RLS, Datenbankverbindungssicherheit
- **Leistung**: Caching, asynchrone Abfragen, Abfrageoptimierung
- **Integration**: Öffentliche Dashboards, Iframe-Integration, Gast-Tokens
- **Gute Praktiken**: Designprinzipien, Grafikauswahl, Sicherheit

Wichtige Punkte, die Sie beachten sollten:
- Superset verbindet sich mit Dremio für leistungsstarke Analysen
- Umfangreiche Visualisierungsbibliothek unterstützt verschiedene Anwendungsfälle
- Integriertes Caching und asynchrone Abfragen sorgen für schnelle Dashboards
– RBAC und RLS ermöglichen sichere Self-Service-Analysen
- Integrationsfunktionen ermöglichen die Integration mit externen Anwendungen

**Zugehörige Dokumentation:**
- [Dremio-Setup-Anleitung](./dremio-setup.md)
- [Architektur: Datenfluss](../architecture/data-flow.md)
- [Tutorial „Erste Schritte“](../getting-started/first-steps.md)
- [Datenqualitätsleitfaden](./data-quality.md)

---

**Version**: 3.2.0  
**Letzte Aktualisierung**: 16. Oktober 2025