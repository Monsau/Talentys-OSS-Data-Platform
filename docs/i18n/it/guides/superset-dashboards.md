# Guida ai dashboard Apache Superset

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 16 ottobre 2025  
**Lingua**: francese

## Sommario

1. [Panoramica](#panoramica)
2. [Configurazione iniziale](#configurazione-iniziale)
3. [Connessione origini dati](#connessione-origine-dati)
4. [Creazione grafica](#creazione-grafica)
5. [Costruzione del cruscotto](#costruzione-cruscotto)
6. [Funzionalità avanzate](#funzionalità-avanzate)
7. [Sicurezza e autorizzazioni](#sicurezza-e-autorizzazioni)
8. [Ottimizzazione delle prestazioni](#ottimizzazione-delle prestazioni)
9. [Integrazione e condivisione](#integrazione-e-condivisione)
10. [Buone pratiche](#buone-pratiche)

---

## Panoramica

Apache Superset è un'applicazione Web di business intelligence moderna e pronta per l'azienda che consente agli utenti di esplorare e visualizzare i dati tramite dashboard e grafici intuitivi.

### Caratteristiche principali

| Caratteristica | Descrizione | Profitto |
|----------------|---------|---------|
| **IDESQL** | Editor SQL interattivo con completamento automatico | Analisi ad hoc |
| **Visualizzazioni ricche** | Oltre 50 tipi di grafici | Varie rappresentazioni dei dati |
| **Creatore di dashboard** | Interfaccia trascina e rilascia | Creazione semplice di dashboard |
| **Memorizzazione nella cache** | Query dei risultati della cache | Tempi di caricamento rapidi |
| **Sicurezza** | Sicurezza a livello di riga, accesso basato sui ruoli | Governance dei dati |
| **Avvisi** | Notifiche email/Slack automatizzate | Monitoraggio proattivo |

### Integrazione dell'architettura

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

## Configurazione iniziale

### Prima connessione

Accedi al Superset su `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Nota sulla sicurezza**: modifica la password predefinita immediatamente dopo il primo accesso.

### Configurazione iniziale

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

### File di configurazione

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

## Origini dati di connessione

### Accedi a Dremio

#### Passaggio 1: installare il driver del database Dremio

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Passaggio 2: aggiungi il database Dremio

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Configurazione**:
§§§CODICE_7§§§

#### Passaggio 3: verificare la connessione

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Connessione a PostgreSQL

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

### Connessione a Elasticsearch

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

## Creazione grafica

### Flusso di lavoro per la creazione grafica

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

### Selezione Tipo Grafico

| Tipo grafico | Ideale per | Esempio di caso d'uso |
|----------------|--------------|---------------------|
| **Grafico lineare** | Tendenze temporali | Andamento del reddito giornaliero |
| **Grafico a barre** | Confronti | Entrate per categoria di prodotto |
| **Grafico dei settori** | Quota del totale | Quota di mercato per regione |
| **Tabella** | Dati dettagliati | Elenco clienti con metriche |
| **Numero grande** | Metrica singola | Reddito totale da inizio anno |
| **Carta termica** | Rilevamento del modello | Vendite al giorno/ora |
| **Nuvola di punti** | Correlazioni | Valore del cliente rispetto alla frequenza |
| **Diagramma Sankey** | Analisi del flusso | Viaggio dell'utente |

### Esempio: grafico lineare (tendenza del reddito)

#### Passaggio 1: crea il set di dati

```
Interface → Données → Datasets → + Dataset
```

**Configurazione**:
- **Banca dati**: Dremio
- **Diagramma**: Produzione.Mart
- **Tabella**: mart_daily_revenue

#### Passaggio 2: crea il grafico

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Parametri**:
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

**SQL generato**:
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

### Esempio: grafico a barre (clienti principali)

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

### Esempio: tabella pivot

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

### Esempio: numero grande con tendenza

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

## Cruscotti di costruzione

### Processo di creazione del dashboard

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

### Passaggio 1: crea la dashboard

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Impostazioni dashboard**:
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

### Passaggio 2: aggiungi la grafica

Trascina e rilascia la grafica dal pannello di sinistra o creane di nuovi:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Passaggio 3: layout di progettazione

**Sistema di griglia**:
- 12 colonne di larghezza
- La grafica si aggancia alla griglia
- Scorri per ridimensionare e riposizionare

**Disposizione di esempio**:
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

### Passaggio 4: aggiungi filtri alla dashboard

```
Tableau de Bord → Éditer → + Filtre
```

**Filtro intervallo di date**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Filtro categoria**:
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

**Filtro digitale**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Passaggio 5: filtro incrociato

Abilita il filtro incrociato della dashboard:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Configurazione**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Esperienza utente**:
- Fare clic sulla barra → filtra l'intera dashboard
- Fare clic sulla condivisione del settore → aggiorna la grafica relativa
- Cancella filtro → ripristina la visualizzazione predefinita

---

## Funzionalità avanzate

### Laboratorio SQL

Editor SQL interattivo per query ad hoc.

#### Esegui la query

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

**Caratteristiche**:
- Completamento automatico per tabelle e colonne
- Richiedi la cronologia
- Schede multiple
- Esporta risultati (CSV, JSON)
- Salva query per il riutilizzo

#### Crea tabella da query (CTAS)

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

### Modelli Jinja

SQL dinamico con modelli Jinja2:

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

**Variabili del modello**:
- `{{ from_dttm }}` - Intervallo di date di inizio
- `{{ to_dttm }}` - Fine dell'intervallo di date
- `{{ filter_values('column') }}` - Valori del filtro selezionati
- `{{ current_username }}` - Utente registrato

### Avvisi e rapporti

#### Crea avviso

```
Interface → Alertes & Rapports → + Alerte
```

**Configurazione**:
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

#### Crea rapporto

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

### Plugin di visualizzazione personalizzati

Crea tipi grafici personalizzati:

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

Costruisci e installa:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Sicurezza e autorizzazioni

### Controllo degli accessi basato sui ruoli (RBAC)

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

### Ruoli integrati

| Ruolo | Autorizzazioni | Casi d'uso |
|------|-------------|-----|
| **Amministratore** | Tutti i permessi | Amministratori di sistema |
| **Alfa** | Crea, modifica, elimina dashboard/grafici | Analisti di dati |
| **Gamma** | Visualizza dashboard, esegui query SQL Lab | Utenti aziendali |
| **sql_lab** | Solo accesso a SQL Lab | Scienziati dei dati |
| **Pubblico** | Visualizza solo dashboard pubbliche | Utenti anonimi |

### Crea ruolo personalizzato

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Esempio: ruolo di analista di marketing**
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

### Sicurezza a livello di linea (RLS)

Limita i dati in base agli attributi dell'utente:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Esempio: RLS basato sulla regione**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Esempio: RLS basata su client**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Sicurezza della connessione al database

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

## Ottimizzazione delle prestazioni

### Query di memorizzazione nella cache

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

**Strategia cache**:
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

### Richieste asincrone

Abilita l'esecuzione di query asincrone per query lunghe:

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

### Ottimizzazione delle query del database

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

### Ottimizzazione del caricamento della dashboard

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

### Monitoraggio delle prestazioni

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

## Integrazione e condivisione

### Dashboard pubbliche

Rendi i dashboard accessibili senza connessione:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**URL pubblico**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Integrazione iframe

Integra dashboard in applicazioni esterne:

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

**Impostazioni di integrazione**:
- `standalone=1` - Nascondi la navigazione
- `show_filters=0` - Nascondi il pannello dei filtri
- `show_title=0` - Nascondi il titolo della dashboard

### Autenticazione token ospite

Accesso programmatico per dashboard integrati:

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

### Esporta dashboard

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Migliori pratiche

### Progettazione del cruscotto

1. **Gerarchia di layout**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Coerenza del colore**
   - Utilizza una combinazione di colori coerente su tutti i dashboard
   - Verde per metriche positive, rosso per negative
   - Colori del marchio per le categorie

3. **Prestazioni**
   - Limita grafica per dashboard (< 15)
   - Utilizzare livelli di aggregazione appropriati
   - Abilita la cache per i dati statici
   - Impostare limiti di linea ragionevoli

4. **Interattività**
   - Aggiungi filtri significativi
   - Abilita il filtro incrociato per l'esplorazione
   - Fornire funzionalità di drill-down

### Selezione grafica

| Tipo di dati | Grafici consigliati | Evitare |
|--------------|---------------------|--------|
| **Serie storica** | Lineare, Aree | Settori, Anello |
| **Confronto** | Barre, colonne | Lineare (pochi punti dati) |
| **Quota sul totale** | Settori, Anello, Mappa ad albero | Bar (anche categorie) |
| **Distribuzione** | Istogramma, diagramma a scatola | Settori |
| **Correlazione** | Punti nuvola, bolle | Barre |
| **Geografico** | Mappa, coropleta | Tabella |

### Ottimizzazione delle query

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

### Sicurezza

1. **Controllo degli accessi**
   - Utilizzare RBAC per la gestione degli utenti
   - Implementare la RLS per l'isolamento dei dati
   - Limitare le connessioni al database per ruolo

2. **Governance dei dati**
   - Proprietà dei set di dati del documento
   - Definire le pianificazioni di aggiornamento dei dati
   - Monitorare le prestazioni delle query

3. **Conformità**
   - Nascondi le PII nelle visualizzazioni
   - Accesso al dashboard di controllo
   - Implementare politiche di conservazione dei dati

---

## Riepilogo

Questa guida completa ai Superset ha trattato:

- **Configurazione**: Installazione, configurazione, connessioni al database
- **Grafica**: più di 50 tipi grafici, configurazione, generazione SQL
- **Dashboard**: progettazione del layout, filtri, filtri incrociati
- **Funzionalità avanzate**: SQL Lab, modelli Jinja, avvisi, plug-in personalizzati
- **Sicurezza**: RBAC, RLS, sicurezza della connessione al database
- **Prestazioni**: memorizzazione nella cache, query asincrone, ottimizzazione delle query
- **Integrazione**: dashboard pubblici, integrazione iframe, token ospite
- **Buone Pratiche**: Principi di progettazione, selezione grafica, sicurezza

Punti chiave da ricordare:
- Superset si connette a Dremio per analisi ad alte prestazioni
- La ricca libreria di visualizzazioni supporta vari casi d'uso
- La memorizzazione nella cache integrata e le query asincrone garantiscono dashboard veloci
- RBAC e RLS consentono analisi self-service sicure
- Le funzionalità di integrazione consentono l'integrazione con applicazioni esterne

**Documentazione correlata:**
- [Guida all'installazione di Dremio](./dremio-setup.md)
- [Architettura: flusso di dati](../architecture/data-flow.md)
- [Tutorial sui primi passi](../getting-started/first-steps.md)
- [Guida alla qualità dei dati](./data-quality.md)

---

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 16 ottobre 2025