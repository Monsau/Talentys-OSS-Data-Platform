# ⚡ Quick Start - Dremio Sandbox en 5 Minutes

**Objectif**: Démarrer la sandbox complète et exécuter une première requête multi-sources

**Temps estimé**: 5 minutes

---

## ✅ Prérequis (2 minutes)

### 1. Vérifier Docker Desktop

```powershell
# Version
docker --version
# Requis: Docker 24.0+

# Mémoire allouée
docker info | Select-String "Total Memory"
# Requis: 8 GB minimum (16 GB recommandé)
```

### 2. Vérifier Python

```powershell
python --version
# Requis: Python 3.11+
```

### 3. Espace disque

```powershell
# Vérifier espace libre
Get-PSDrive C | Select-Object Used,Free
# Requis: 20 GB libre
```

---

## 🚀 Étape 1: Démarrer l'Infrastructure (2 minutes)

```powershell
# Naviguer vers le dossier Docker
cd c:\projets\dremiodbt\docker

# Démarrer tous les services
docker-compose up -d

# Attendre que tous les services soient "Up" (2-3 min)
docker-compose ps
```

**Services qui doivent être UP**:
```
NAME                     STATUS
dremio                   Up 2 minutes
postgres                 Up 2 minutes
minio                    Up 2 minutes
elasticsearch            Up 2 minutes
polaris                  Up 2 minutes
openmetadata-server      Up 2 minutes
```

---

## 👤 Étape 2: Créer le Compte Admin Dremio (30 secondes)

1. Ouvrir http://localhost:9047
2. Remplir le formulaire:
   - **Username**: `admin`
   - **First Name**: `Admin`
   - **Last Name**: `User`
   - **Email**: `admin@company.com`
   - **Password**: `admin123`
   - **Confirm Password**: `admin123`
3. Cliquer sur **Create Account**

**⚠️ Important**: Retenir ces credentials (utilisés par les scripts Python)

---

## 📊 Étape 3: Populer les Données (1 minute)

```powershell
# Retour au dossier principal
cd c:\projets\dremiodbt

# Activer Python venv
.\venv_dremio_311\Scripts\Activate.ps1

# Populer PostgreSQL (75 records)
python scripts/setup_postgresql_data.py
# ✅ Output attendu: "PostgreSQL data setup complete. 75 total records."

# Populer MinIO (550 Parquet files)
python scripts/setup_minio_data.py
# ✅ Output attendu: "MinIO data setup complete. 550 files uploaded."

# Populer Elasticsearch (1,800 events)
python scripts/setup_elasticsearch_data.py
# ✅ Output attendu: "Elasticsearch data setup complete. 1,800 documents indexed."
```

---

## 🔗 Étape 4: Configurer les Sources Dremio (1 minute)

```powershell
# Configurer PostgreSQL dans Dremio
python scripts/configure_pg_in_dremio.py
# ✅ Output: "PostgreSQL source configured successfully"

# Configurer MinIO dans Dremio
python scripts/configure_minio_in_dremio.py
# ✅ Output: "MinIO source configured successfully"

# Créer les Virtual Datasets Elasticsearch
python scripts/create_es_vds_dremio26.py
# ✅ Output: "Created VDS: raw.es_application_logs (500 rows)"
# ✅ Output: "Created VDS: raw.es_user_events (1,000 rows)"
# ✅ Output: "Created VDS: raw.es_performance_metrics (300 rows)"
```

---

## ⚙️ Étape 5: Exécuter dbt (30 secondes)

```powershell
# Naviguer vers dbt
cd dbt

# Exécuter tous les modèles
dbt run
# ✅ Output: "Completed successfully" avec 12 modèles créés

# Tester la qualité
dbt test
# ✅ Output: "13 of 14 tests passed (92.9%)"
```

---

## 🎉 Étape 6: Première Requête Multi-Sources!

### Option A: Via Dremio UI

1. Ouvrir http://localhost:9047
2. Cliquer sur **SQL Runner** (en haut à droite)
3. Copier-coller cette requête:

```sql
-- Vue 360° combinant PostgreSQL + Elasticsearch
SELECT 
    -- PostgreSQL: Commandes clients
    COUNT(DISTINCT o.customer_id) as total_customers,
    COUNT(o.order_id) as total_orders,
    SUM(o.order_amount) as total_revenue,
    
    -- Elasticsearch: Événements utilisateur
    (SELECT COUNT(*) FROM elasticsearch.user_events."_doc") as total_events,
    (SELECT COUNT(*) FROM elasticsearch.application_logs."_doc" WHERE log_level = 'ERROR') as total_errors
    
FROM "PostgreSQL_BusinessDB".public.orders o;
```

4. Cliquer sur **Run** (ou F5)

**✅ Résultat attendu**:
```
total_customers | total_orders | total_revenue | total_events | total_errors
----------------|--------------|---------------|--------------|-------------
     25         |      50      |   125,432.50  |    1,000     |     47
```

### Option B: Via dbt Docs

```powershell
# Générer la documentation
dbt docs generate

# Lancer le serveur
dbt docs serve --port 8080
```

1. Ouvrir http://localhost:8080
2. Explorer le graphe de dépendances
3. Cliquer sur un modèle (ex: `fct_business_overview`)
4. Voir le code SQL, les colonnes, les tests

---

## 🎓 Étape 7: Explorer les Sources

### PostgreSQL

```sql
-- Clients
SELECT * FROM "PostgreSQL_BusinessDB".public.customers LIMIT 5;

-- Commandes
SELECT * FROM "PostgreSQL_BusinessDB".public.orders LIMIT 5;
```

### MinIO (Data Lake)

```sql
-- Ventes Parquet
SELECT * FROM minio_sales."sales-data".sales LIMIT 5;
```

### Elasticsearch

```sql
-- Logs applicatifs (syntaxe spéciale Dremio 26)
SELECT * FROM elasticsearch.application_logs."_doc" LIMIT 5;

-- Événements utilisateur
SELECT * FROM elasticsearch.user_events."_doc" WHERE event_type = 'purchase' LIMIT 5;

-- Métriques système
SELECT * FROM elasticsearch.performance_metrics."_doc" WHERE metric_name = 'cpu_usage' LIMIT 5;
```

---

## 🧪 Étape 8: Tester les Modèles dbt

### Vue Business 360° (le modèle phare!)

```sql
SELECT 
    business_date,
    combined_revenue,
    pg_transactions as "Commandes Web",
    minio_transactions as "Ventes Historiques",
    platform_errors as "Erreurs Plateforme",
    conversion_rate as "Taux Conversion %"
FROM marts.fct_business_overview
WHERE business_date >= CURRENT_DATE - 30
ORDER BY business_date DESC;
```

### Monitoring Plateforme

```sql
SELECT 
    day,
    service,
    error_count,
    avg_cpu_percent,
    avg_memory_mb
FROM marts.fct_platform_health
WHERE day = CURRENT_DATE
ORDER BY error_count DESC;
```

### Analyse Clients

```sql
SELECT 
    customer_segment,
    COUNT(*) as count,
    AVG(total_spent) as avg_spent,
    SUM(total_orders) as total_orders
FROM marts.dim_customers
GROUP BY customer_segment
ORDER BY avg_spent DESC;
```

---

## ✅ Checklist de Validation

Cocher chaque élément:

- [ ] **Docker**: 6 services "Up" (`docker-compose ps`)
- [ ] **Dremio**: Accessible sur http://localhost:9047
- [ ] **PostgreSQL**: 75 records insérés
- [ ] **MinIO**: 550 fichiers Parquet uploadés
- [ ] **Elasticsearch**: 1,800 documents indexés
- [ ] **Sources Dremio**: 3 sources configurées (PostgreSQL, MinIO, Elasticsearch)
- [ ] **VDS**: 3 VDS Elasticsearch créés
- [ ] **dbt**: 12 modèles exécutés avec succès
- [ ] **Tests**: 13/14 tests passent (92.9%)
- [ ] **Requête Multi-Sources**: Exécutée avec succès

---

## 🎯 Prochaines Étapes

Maintenant que la sandbox fonctionne:

1. **Explorer les dashboards**:
   - Voir [DEMO_GUIDE.md](DEMO_GUIDE.md) pour les scénarios de présentation

2. **Comprendre l'architecture**:
   - Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour les détails techniques

3. **Ajouter des données**:
   - Modifier les scripts `setup_*.py` pour générer plus de données
   - Re-exécuter `dbt run` pour mettre à jour les modèles

4. **Créer des dashboards**:
   - Installer Superset: `docker-compose -f docker-compose.superset.yml up -d`
   - Connecter à Dremio et créer des visualisations

5. **Personnaliser**:
   - Ajouter vos propres sources de données
   - Créer de nouveaux modèles dbt dans `dbt/models/`
   - Ajouter des tests de qualité dans `dbt/models/schema.yml`

---

## 🆘 Problèmes Fréquents

### "Port 9047 already in use"

```powershell
# Arrêter Dremio existant
docker stop dremio

# Redémarrer
docker-compose up -d dremio
```

### "Cannot connect to Docker daemon"

```powershell
# Démarrer Docker Desktop manuellement
# Puis réessayer
docker-compose up -d
```

### "Python module not found"

```powershell
# Réinstaller les dépendances
pip install -r requirements.txt
```

### "dbt: Connection refused to Dremio"

```bash
# Vérifier que Dremio est up
docker logs dremio | Select-String "Started on"

# Vérifier le profil dbt
cat dbt/profiles.yml
# Port doit être 9047, pas 31010
```

---

## 📞 Besoin d'Aide?

- **Documentation complète**: [README.md](../README.md)
- **Troubleshooting détaillé**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**🎉 Félicitations! Votre sandbox Dremio est opérationnelle!**

**⏱️ Temps total**: ~5 minutes | **Difficulté**: ⭐⭐☆☆☆

---

**Version**: 1.0 | **Updated**: 14 Oct 2025
