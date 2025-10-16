# Configuration Elasticsearch dans Dremio

## ✅ Étape 1: Données Elasticsearch créées

Les données suivantes ont été créées dans Elasticsearch:

### Indices créés:
- **application_logs** (500 documents) - Logs d'application
- **user_events** (1000 documents) - Événements utilisateurs  
- **performance_metrics** (300 documents) - Métriques de performance

### Vérification:
```bash
curl http://localhost:9200/_cat/indices?v
```

## 📋 Étape 2: Configuration manuelle dans Dremio

Malheureusement, l'API REST de Dremio ne permet pas de créer facilement une source Elasticsearch de manière programmatique. Voici comment le faire manuellement:

### Dans l'interface Dremio (http://localhost:9047):

1. **Cliquer sur "+" (Add Source)**
2. **Sélectionner "Elasticsearch"**
3. **Configuration:**
   - Name: `elasticsearch`
   - Host: `elasticsearch` (nom du conteneur Docker)
   - Port: `9200`
   - Authentication: Anonymous/None
   - Options avancées:
     - Scroll Size: `4000`
     - Scroll Timeout: `60000`
     - Enable Scripts: ✓

4. **Tester la connexion et Sauvegarder**

## 🎯 Alternative: Utiliser JDBC/ODBC

Si la configuration web ne fonctionne pas, vous pouvez aussi:

1. Accéder aux indices directement via requêtes HTTP
2. Créer des External Tables dans Dremio pointant vers des fichiers JSON
3. Utiliser un connecteur tiers

## 📊 Prochaines étapes (après configuration)

Une fois la source configurée, vous verrez ces indices:
- `elasticsearch`.`application_logs`
- `elasticsearch`.`user_events`
- `elasticsearch`.`performance_metrics`

Vous pourrez alors:
1. Créer des VDS pour transformer ces données
2. Les intégrer dans vos modèles dbt
3. Joindre avec les données PostgreSQL et MinIO

## 🔍 Données disponibles

### application_logs
```sql
SELECT * FROM elasticsearch.application_logs LIMIT 10;
```
Colonnes: timestamp, level, service, message, user_id, request_id, duration_ms, status_code

### user_events
```sql
SELECT * FROM elasticsearch.user_events LIMIT 10;
```
Colonnes: timestamp, event_type, user_id, session_id, page, action, device, browser

### performance_metrics
```sql
SELECT * FROM elasticsearch.performance_metrics LIMIT 10;
```
Colonnes: timestamp, metric_name, service, value, unit, host, environment
