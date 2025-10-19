# 🚀 OpenMetadata 1.10.1 - Guide de Démarrage Rapide

## 📋 Prérequis

- Docker & Docker Compose installés
- Ports disponibles : 3307 (MySQL), 8585-8586 (OpenMetadata), 9200 (Elasticsearch)
- Au moins 8 GB RAM disponible

---

## 🎯 Démarrage Rapide

### 1. Démarrer tous les services

```bash
# Démarrer l'ensemble de la plateforme
docker-compose up -d

# Ou démarrer uniquement OpenMetadata et ses dépendances
docker-compose up -d mysql elasticsearch openmetadata-server
```

### 2. Vérifier les services

```bash
# Vérifier les conteneurs actifs
docker-compose ps

# Voir les logs OpenMetadata
docker-compose logs -f openmetadata-server

# Vérifier la santé
docker-compose ps | grep healthy
```

### 3. Accéder à OpenMetadata

**Interface Web**: http://localhost:8585

**Identifiants par défaut**:
- Username: `admin`
- Password: `admin`

---

## 🔧 Configuration

### Variables d'Environnement

Les principales variables sont configurées dans `docker-compose.yml` :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DB_HOST` | mysql | Hôte MySQL |
| `DB_PORT` | 3306 | Port MySQL interne |
| `DB_USER` | openmetadata_user | Utilisateur DB |
| `OM_DATABASE` | openmetadata_db | Nom de la base |
| `ELASTICSEARCH_HOST` | elasticsearch | Hôte ES |
| `SERVER_PORT` | 8585 | Port API/UI |
| `SERVER_ADMIN_PORT` | 8586 | Port admin |

### Ports Exposés

| Port | Service | Description |
|------|---------|-------------|
| **3307** | MySQL | Base de données (externe: 3307 → interne: 3306) |
| **8585** | OpenMetadata | API REST + Interface Web |
| **8586** | OpenMetadata | Port d'administration |
| **9200** | Elasticsearch | API de recherche |

---

## 📊 Fonctionnalités Principales

### 1. Découverte de Données (Data Discovery)

- **Catalogue de métadonnées**: Tables, colonnes, schémas
- **Recherche full-text**: Recherche rapide dans tous les assets
- **Lineage**: Traçabilité des transformations de données
- **Tags & Glossaire**: Organisation et documentation

### 2. Qualité des Données (Data Quality)

- **Tests de qualité**: Règles personnalisées
- **Profiling**: Statistiques automatiques sur les données
- **Alertes**: Notifications sur violations de qualité
- **Tableaux de bord**: Vue d'ensemble de la qualité

### 3. Gouvernance (Data Governance)

- **Ownership**: Attribution de propriétaires
- **Tiers**: Classification par criticité
- **Domains**: Organisation par domaine métier
- **Policies**: Règles d'accès et de conformité

### 4. Collaboration

- **Activity Feeds**: Flux d'activités
- **Conversations**: Discussions sur les assets
- **Announcements**: Communications importantes
- **Tasks**: Attribution de tâches

---

## 🔌 Intégration avec Dremio

### Configuration du Connecteur Dremio

1. **Accéder aux Services** (Settings → Services → Add Service)

2. **Sélectionner "Dremio"**

3. **Configuration**:
   ```json
   {
     "type": "Dremio",
     "serviceName": "dremio-prod",
     "serviceConnection": {
       "config": {
         "type": "Dremio",
         "hostPort": "http://dremio:9047",
         "username": "admin",
         "password": "admin123",
         "databaseSchema": "samples"
       }
     }
   }
   ```

4. **Test Connection** → **Save**

5. **Configurer l'Ingestion**:
   - Metadata: Toutes les 6 heures
   - Profiler: Quotidien
   - Data Quality: Hebdomadaire

### Exemples de Requêtes Lineage

Une fois connecté à Dremio, OpenMetadata tracera automatiquement :

```sql
-- Cette transformation sera visible dans le lineage
CREATE TABLE analytics.customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.amount) as total_spent
FROM sources.postgres.customers c
LEFT JOIN sources.postgres.orders o 
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;
```

Le lineage montrera :
```
[sources.postgres.customers] ──┐
                               ├──> [analytics.customer_summary]
[sources.postgres.orders] ─────┘
```

---

## 📡 Intégration avec Airflow

### Configurer le Connecteur Airflow

```python
# airflow/dags/openmetadata_sync.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from metadata.ingestion.api.workflow import Workflow
from datetime import datetime

def sync_to_openmetadata():
    config = {
        "source": {
            "type": "dremio",
            "serviceName": "dremio-prod",
            "serviceConnection": {
                "config": {
                    "type": "Dremio",
                    "hostPort": "http://dremio:9047",
                    "username": "admin",
                    "password": "admin123"
                }
            },
            "sourceConfig": {
                "config": {
                    "type": "DatabaseMetadata"
                }
            }
        },
        "sink": {
            "type": "metadata-rest",
            "config": {
                "hostPort": "http://openmetadata-server:8585/api",
                "authProvider": "openmetadata",
                "securityConfig": {
                    "jwtToken": "your-jwt-token"
                }
            }
        }
    }
    
    workflow = Workflow.create(config)
    workflow.execute()
    workflow.stop()

with DAG(
    'openmetadata_sync',
    start_date=datetime(2025, 1, 1),
    schedule_interval='0 */6 * * *',  # Toutes les 6 heures
    catchup=False
) as dag:
    
    sync_task = PythonOperator(
        task_id='sync_metadata',
        python_callable=sync_to_openmetadata
    )
```

---

## 🔍 API REST

### Authentification

```bash
# Obtenir un JWT token
curl -X POST http://localhost:8585/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@openmetadata.org",
    "password": "admin"
  }'
```

### Exemples d'API

```bash
# Lister toutes les tables
curl -X GET http://localhost:8585/api/v1/tables \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Obtenir les détails d'une table
curl -X GET http://localhost:8585/api/v1/tables/name/dremio-prod.samples.nyc_taxi \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Créer un test de qualité
curl -X POST http://localhost:8585/api/v1/dataQuality/testCases \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "check_null_values",
    "entityLink": "<#E::table::dremio-prod.samples.nyc_taxi>",
    "testDefinition": "columnValuesToBeNotNull",
    "parameterValues": [
      {"name": "columnName", "value": "passenger_count"}
    ]
  }'

# Rechercher des assets
curl -X GET "http://localhost:8585/api/v1/search/query?q=customer&index=table_search_index" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 Dashboard de Monitoring

### Métriques Elasticsearch

```bash
# Santé du cluster
curl http://localhost:9200/_cluster/health?pretty

# Statistiques d'indexation
curl http://localhost:9200/_stats?pretty

# Nombre de documents par index
curl http://localhost:9200/_cat/indices?v
```

### Métriques OpenMetadata

Accéder aux métriques Prometheus : http://localhost:8586/actuator/prometheus

---

## 🐛 Dépannage

### Service ne démarre pas

```bash
# Vérifier les logs
docker-compose logs openmetadata-server

# Vérifier les dépendances
docker-compose ps mysql elasticsearch

# Restart clean
docker-compose down -v
docker-compose up -d mysql elasticsearch
sleep 30  # Attendre que ES soit prêt
docker-compose up -d openmetadata-server
```

### Problèmes de connexion Dremio

```bash
# Vérifier la connectivité réseau
docker exec openmetadata-server curl http://dremio:9047

# Vérifier les credentials Dremio
docker exec -it dremio /bin/bash
cd /opt/dremio/bin
./dremio-admin
```

### Problèmes Elasticsearch

```bash
# Augmenter la mémoire (dans docker-compose.yml)
environment:
  - "ES_JAVA_OPTS=-Xms2g -Xmx2g"

# Réinitialiser les index
curl -X DELETE http://localhost:9200/*_search_index
docker-compose restart openmetadata-server
```

### Reset complet

```bash
# Supprimer tous les volumes
docker-compose down -v

# Supprimer les données locales
rm -rf openmetadata/data
rm -rf docker-volume/

# Redémarrer proprement
docker-compose up -d
```

---

## 📚 Ressources

### Documentation Officielle
- [OpenMetadata Docs](https://docs.open-metadata.org/v1.10.x/)
- [API Reference](https://docs.open-metadata.org/v1.10.x/sdk/python)
- [Connectors](https://docs.open-metadata.org/v1.10.x/connectors)

### Exemples
- [GitHub Examples](https://github.com/open-metadata/OpenMetadata/tree/main/examples)
- [Python SDK](https://github.com/open-metadata/OpenMetadata/tree/main/ingestion)

### Communauté
- [Slack](https://slack.open-metadata.org/)
- [GitHub Issues](https://github.com/open-metadata/OpenMetadata/issues)
- [Discussions](https://github.com/open-metadata/OpenMetadata/discussions)

---

## ✅ Checklist de Production

Avant de déployer en production :

- [ ] Changer les mots de passe par défaut
- [ ] Générer de nouvelles clés JWT
- [ ] Configurer SSL/TLS
- [ ] Activer l'authentification avancée (OAuth, SAML)
- [ ] Configurer les backups automatiques
- [ ] Mettre en place le monitoring (Prometheus/Grafana)
- [ ] Configurer les alertes
- [ ] Documenter la procédure de restauration
- [ ] Tester le disaster recovery
- [ ] Former les utilisateurs

---

**Version**: OpenMetadata 1.10.1  
**Date**: Octobre 2025  
**Statut**: ✅ Production Ready
