# Guía de paneles de control de Apache Superset

**Versión**: 3.2.0  
**Última actualización**: 16 de octubre de 2025  
**Idioma**: Francés

## Tabla de contenido

1. [Resumen](#resumen)
2. [Configuración inicial](#configuración-inicial)
3. [Conexión de fuentes de datos](#conexión-fuentes-de-datos)
4. [Creación de gráficos](#graphics-creation)
5. [Construcción del tablero](#dashboard-construction)
6. [Funciones avanzadas](#funciones-avanzadas)
7. [Seguridad y permisos](#seguridad-y-permisos)
8. [Optimización del rendimiento](#optimización del rendimiento)
9. [Integración y uso compartido](#integración-y-compartición)
10. [Buenas Prácticas](#buenas-practicas)

---

## Descripción general

Apache Superset es una aplicación web de inteligencia empresarial moderna y preparada para empresas que permite a los usuarios explorar y visualizar datos a través de paneles y gráficos intuitivos.

### Características clave

| Característica | Descripción | Beneficio |
|----------------|---------|---------|
| **IDE SQL** | Editor SQL interactivo con autocompletado | Análisis ad hoc |
| **Visualizaciones enriquecidas** | Más de 50 tipos de gráficos | Diversas representaciones de datos |
| **Creador de paneles** | Interfaz de arrastrar y soltar | Fácil creación de paneles |
| **Almacenamiento en caché** | Consultas de resultados de caché | Tiempos de carga rápidos |
| **Seguridad** | Seguridad a nivel de fila, acceso basado en roles | Gobernanza de datos |
| **Alertas** | Correo electrónico automatizado/notificaciones de Slack | Monitoreo proactivo |

### Integración de arquitectura

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

## Configuración inicial

### Primera conexión

Acceda a Superset en `http://localhost:8088`:

```
Identifiants Par Défaut:
Nom d'utilisateur: admin
Mot de passe: admin
```

**Nota de seguridad**: Cambie la contraseña predeterminada inmediatamente después del primer inicio de sesión.

### Configuración inicial

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

### Archivo de configuración

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

## Fuentes de datos de conexión

### Iniciar sesión en Dremio

#### Paso 1: Instale el controlador de base de datos Dremio

```bash
# Installer connecteur Arrow Flight SQL
pip install pyarrow adbc-driver-flightsql
```

#### Paso 2: Agregar la base de datos Dremio

```
Interface → Paramètres → Connexions Base de Données → + Base de Données
```

**Configuración**:
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

#### Paso 3: Probar la conexión

```sql
-- Requête test dans SQL Lab
SELECT 
    customer_id,
    full_name,
    lifetime_value
FROM Production.Marts.mart_customer_lifetime_value
LIMIT 10;
```

### Conexión a PostgreSQL

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

### Conexión a Elasticsearch

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

## Creación de gráficos

### Flujo de trabajo de creación gráfica

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

### Tipo de gráfico de selección

| Tipo gráfico | Mejor para | Ejemplo de caso de uso |
|----------|---------------|---------------------|
| **Gráfico lineal** | Tendencias temporales | Tendencia de ingresos diarios |
| **Gráfico de barras** | Comparaciones | Ingresos por categoría de producto |
| **Gráfico de sectores** | Participación del total | Cuota de mercado por región |
| **Tabla** | Datos detallados | Lista de clientes con métricas |
| **Número grande** | Métrica única | Ingresos totales hasta la fecha |
| **Tarjeta térmica** | Detección de patrones | Ventas por día/hora |
| **Nube de puntos** | Correlaciones | Valor para el cliente vs frecuencia |
| **Diagrama de Sankey** | Análisis de flujo | Viaje del usuario |

### Ejemplo: gráfico lineal (tendencia de ingresos)

#### Paso 1: Crear conjunto de datos

```
Interface → Données → Datasets → + Dataset
```

**Configuración**:
- **Base de datos**: Dremio
- **Diagrama**: Production.Marts
- **Tabla**: mart_daily_revenue

#### Paso 2: Crear gráfico

```
Interface → Graphiques → + Graphique → Graphique Linéaire
```

**Parámetros**:
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

**SQL generado**:
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

### Ejemplo: gráfico de barras (clientes principales)

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

### Ejemplo: tabla dinámica

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

### Ejemplo: Número grande con tendencia

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

## Paneles de construcción

### Proceso de creación del panel

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

### Paso 1: Crear panel

```
Interface → Tableaux de Bord → + Tableau de Bord
```

**Configuración del panel**:
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

### Paso 2: Agregar gráficos

Arrastre y suelte gráficos desde el panel izquierdo o cree otros nuevos:

```
+ → Graphique Existant → Sélectionner graphique
+ → Créer Nouveau Graphique → Choisir type
```

### Paso 3: Diseño

**Sistema de red**:
- 12 columnas de ancho
- Los gráficos se ajustan a la cuadrícula.
- Desliza para cambiar el tamaño y reposicionar

**Diseño de ejemplo**:
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

### Paso 4: Agregar filtros al panel

```
Tableau de Bord → Éditer → + Filtre
```

**Filtro de rango de fechas**:
```yaml
Type Filtre: Plage Date
Cible: revenue_date
Colonnes:
  - mart_daily_revenue.revenue_date
  - fct_orders.order_date
Valeur Par Défaut: 30 derniers jours
```

**Filtro de categoría**:
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

**Filtro digital**:
```yaml
Type Filtre: Plage Numérique
Cible: lifetime_value
Colonnes:
  - mart_customer_lifetime_value.lifetime_value
Min: 0
Max: 10000
Par Défaut: [0, 10000]
```

### Paso 5: filtrado cruzado

Habilite el filtrado cruzado del panel:

```
Tableau de Bord → Éditer → Paramètres → Activer Filtrage Croisé
```

**Configuración**:
```yaml
Activer Filtrage Croisé: Oui
Portées Filtre Croisé:
  Graphique 1 (Graphique Barres):
    Affecte: [Graphique 2, Graphique 3, Graphique 4]
  Graphique 2 (Graphique Secteurs):
    Affecte: [Graphique 1, Graphique 3]
```

**Experiencia de usuario**:
- Haga clic en la barra → filtrar todo el panel
- Haga clic en compartir sector → actualiza gráficos relacionados
- Borrar filtro → se restablece a la vista predeterminada

---

## Funciones avanzadas

### Laboratorio SQL

Editor SQL interactivo para consultas ad-hoc.

#### Ejecutar consulta

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

**Características**:
- Autocompletar para tablas y columnas.
- Historial de solicitudes
- Múltiples pestañas
- Exportar resultados (CSV, JSON)
- Guardar consulta para reutilizar

#### Crear tabla a partir de consulta (CTAS)

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

### Plantillas Jinja

SQL dinámico con plantillas Jinja2:

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

**Variables de plantilla**:
- `{{ from_dttm }}` - Rango de fechas de inicio
- `{{ to_dttm }}` - Fin del rango de fechas
- `{{ filter_values('column') }}` - Valores de filtro seleccionados
- `{{ current_username }}` - Usuario registrado

### Alertas e informes

#### Crear alerta

```
Interface → Alertes & Rapports → + Alerte
```

**Configuración**:
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

#### Crear informe

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

### Complementos de visualización personalizados

Cree tipos de gráficos personalizados:

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

Construya e instale:
```bash
npm run build
superset install-plugin ./dist/MyCustomChart.zip
```

---

## Seguridad y permisos

### Control de acceso basado en roles (RBAC)

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

### Roles integrados

| Rol | Permisos | Casos de uso |
|------|-------------|-------------|
| **Administrador** | Todos los permisos | Administradores de sistemas |
| **Alfa** | Crear, editar, eliminar paneles/gráficos | Analistas de datos |
| **Gama** | Ver paneles, ejecutar consultas de SQL Lab | Usuarios empresariales |
| **sql_lab** | Acceso exclusivo al laboratorio SQL | Científicos de datos |
| **Público** | Ver paneles públicos únicamente | Usuarios anónimos |

### Crear rol personalizado

```
Interface → Paramètres → Lister Rôles → + Rôle
```

**Ejemplo: función de analista de marketing**
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

### Seguridad a nivel de línea (RLS)

Restringir datos según atributos del usuario:

```
Interface → Données → Datasets → [dataset] → Éditer → Sécurité Niveau Ligne
```

**Ejemplo: RLS basado en región**
```sql
-- Filtre: Utilisateur voit uniquement données de sa région
region = '{{ current_user_region() }}'
```

**Ejemplo: RLS basado en cliente**
```sql
-- Filtre: Commercial voit uniquement ses clients
customer_id IN (
  SELECT customer_id 
  FROM user_customer_mapping 
  WHERE user_email = '{{ current_username() }}'
)
```

### Seguridad de la conexión de la base de datos

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

## Optimización del rendimiento

### Consultas de almacenamiento en caché

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

**Estrategia de caché**:
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

### Solicitudes asincrónicas

Habilite la ejecución de consultas asíncronas para consultas largas:

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

### Optimización de consultas de bases de datos

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

### Optimización de carga del panel

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

### Monitoreo del desempeño

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

## Integración y uso compartido

### Paneles públicos

Haga que los paneles sean accesibles sin conexión:

```
Tableau de Bord → Éditer → Paramètres → Publié
```

**URL pública**:
```
https://superset.company.com/dashboard/public/{uuid}
```

### Integración de marco flotante

Integre paneles en aplicaciones externas:

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

**Configuración de integración**:
- `standalone=1` - Ocultar navegación
- `show_filters=0` - Ocultar panel de filtro
- `show_title=0` - Ocultar título del panel

### Autenticación de token de invitado

Acceso programático para paneles integrados:

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

### Exportar paneles

```bash
# Exporter tableau de bord comme JSON
superset export-dashboards -f dashboard_export.json -d 1,2,3

# Importer tableau de bord
superset import-dashboards -f dashboard_export.json
```

---

## Mejores prácticas

### Diseño de tablero

1. **Jerarquía de diseño**
   ```
   Haut: Métriques Clés (Grands Nombres)
   Milieu: Tendances (Graphiques Linéaires/Aires)
   Bas: Détails (Tableaux, Répartitions)
   ```

2. **Consistencia del color**
   - Utilice una combinación de colores consistente en todos los paneles
   - Verde para métricas positivas, rojo para negativas.
   - Colores de marca para categorías.

3. **Rendimiento**
   - Limitar gráficos por panel (<15)
   - Utilice niveles de agregación apropiados
   - Habilitar caché para datos estáticos
   - Establecer límites de línea razonables

4. **Interactividad**
   - Agregar filtros significativos
   - Habilitar el filtrado cruzado para la exploración.
   - Proporcionar capacidades de desglose

### Selección gráfica

| Tipo de datos | Gráficos recomendados | Evitar |
|----------------------|----------------------|--------|
| **Serie temporal** | Lineal, Áreas | Sectores, Anillo |
| **Comparación** | Barras, columnas | Lineal (pocos puntos de datos) |
| **Participación del total** | Sectores, Anillo, Mapa de árbol | Bares (también categorías) |
| **Distribución** | Histograma, diagrama de caja | Sectores |
| **Correlación** | Puntos de nube, burbujas | Bares |
| **Geográfico** | Mapa, Coropletas | Mesa |

### Optimización de consultas

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

### Seguridad

1. **Control de acceso**
   - Utilice RBAC para la gestión de usuarios.
   - Implementar RLS para aislamiento de datos.
   - Restringir las conexiones de bases de datos por rol

2. **Gobernanza de datos**
   - Propiedad de conjuntos de datos de documentos
   - Definir horarios de actualización de datos.
   - Supervisar el rendimiento de las consultas.

3. **Cumplimiento**
   - Ocultar PII en visualizaciones
   - Acceso al panel de auditoría
   - Implementar políticas de retención de datos.

---

## Resumen

Esta guía completa de Superconjuntos ha cubierto:

- **Configuración**: Instalación, configuración, conexiones a bases de datos.
- **Gráficos**: Más de 50 tipos de gráficos, configuración, generación de SQL
- **Paneles**: diseño de diseño, filtros, filtrado cruzado
- **Funciones avanzadas**: SQL Lab, plantillas Jinja, alertas, complementos personalizados
- **Seguridad**: RBAC, RLS, seguridad de conexión de base de datos
- **Rendimiento**: almacenamiento en caché, consultas asíncronas, optimización de consultas
- **Integración**: paneles públicos, integración de iframe, tokens de invitado
- **Buenas Prácticas**: Principios de diseño, selección gráfica, seguridad.

Puntos clave para recordar:
- Superset se conecta a Dremio para realizar análisis de alto rendimiento
- Una rica biblioteca de visualización admite varios casos de uso
- El almacenamiento en caché integrado y las consultas asíncronas garantizan paneles rápidos
- RBAC y RLS permiten análisis de autoservicio seguros
- Las capacidades de integración permiten la integración con aplicaciones externas

**Documentación relacionada:**
- [Guía de configuración de Dremio] (./dremio-setup.md)
- [Arquitectura: Flujo de datos](../architecture/data-flow.md)
- [Tutorial de Primeros Pasos](../getting-started/first-steps.md)
- [Guía de calidad de datos] (./data-quality.md)

---

**Versión**: 3.2.0  
**Última actualización**: 16 de octubre de 2025