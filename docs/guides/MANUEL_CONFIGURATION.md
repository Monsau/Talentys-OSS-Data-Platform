# 🚀 Guide de Configuration Manuelle - Environnement Dremio Complet

**Date**: 14 Octobre 2025  
**Environnement**: Dremio 26.0 + PostgreSQL + MinIO + OpenMetadata + Airflow + Polaris

---

## 📊 **État de l'Environnement**

### ✅ **Services Opérationnels**

| Service | URL | Status | Credentials |
|---------|-----|---------|-------------|
| **Dremio** | http://localhost:9047 | 🟢 UP | admin/admin123 |
| **MinIO** | http://localhost:9001 | 🟢 UP | minio_admin/minio_password |
| **PostgreSQL** | localhost:5432 | 🟢 UP | dbt_user/dbt_password |
| **Elasticsearch** | http://localhost:9200 | 🟢 UP | - |
| **Airflow** | http://localhost:8080 | 🟢 UP | admin/admin |

### ⚠️ **Services à Configurer**

| Service | URL | Status | Action Requise |
|---------|-----|---------|----------------|
| **OpenMetadata** | http://localhost:8585 | 🟡 CONFIG | Démarrage en cours |
| **Polaris** | http://localhost:8181 | 🟡 CONFIG | Configuration Iceberg |

---

## 🔧 **Configuration Manuelle Dremio**

### **Étape 1: Accès Initial**

1. **Ouvrir Dremio** : http://localhost:9047
2. **Se connecter** : admin / admin123
3. **Vérifier tableau de bord**

### **Étape 2: Ajouter Source PostgreSQL**

1. **Aller dans Sources** → **Add Source**
2. **Sélectionner PostgreSQL** 
3. **Paramètres** :
   ```
   Name: PostgreSQL_Business
   Host: postgres  
   Port: 5432
   Database: business_data
   Username: dbt_user
   Password: dbt_password
   ```
4. **Test Connection** → **Save**

### **Étape 3: Ajouter Source MinIO S3**

1. **Add Source** → **Amazon S3**
2. **Paramètres** :
   ```
   Name: MinIO_Storage
   Access Key: minio_admin
   Secret Key: minio_password
   
   Advanced Options:
   - Endpoint: http://minio:9000
   - Path Style Access: Enabled
   - Encrypt connection: Disabled
   ```
3. **Test Connection** → **Save**

### **Étape 4: Créer Espaces**

1. **Add Space** pour chaque espace :
   - **raw** (données brutes)
   - **staging** (données nettoyées) 
   - **marts** (données métier)
   - **sandbox** (expérimentation)

### **Étape 5: Créer VDS d'Exemple**

**Dans l'espace `raw`** :
```sql
-- VDS: customer_summary
SELECT 
    customer_id,
    first_name || ' ' || last_name as full_name,
    email,
    city,
    country,
    created_at
FROM "PostgreSQL_Business".public.customers
```

**Dans l'espace `staging`** :
```sql
-- VDS: customer_orders  
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name as customer_name,
    c.email,
    o.order_id,
    o.order_date,
    o.total_amount,
    o.status
FROM "PostgreSQL_Business".public.customers c
LEFT JOIN "PostgreSQL_Business".public.orders o 
    ON c.customer_id = o.customer_id
```

---

## 🗂️ **Configuration MinIO**

### **Étape 1: Accès Console**

1. **Ouvrir MinIO Console** : http://localhost:9001
2. **Se connecter** : minio_admin / minio_password

### **Étape 2: Créer Buckets**

Créer les buckets suivants :
- **raw-data** (données sources)
- **staging-data** (données transformées)
- **analytics-data** (données finales)
- **dbt-artifacts** (modèles dbt)
- **dremio-cache** (cache Dremio)

### **Étape 3: Upload Données Test (Optionnel)**

Créer quelques fichiers CSV dans `raw-data` pour tester :
```csv
# sample_customers.csv
id,name,email,city
1,John Doe,john@email.com,New York
2,Jane Smith,jane@email.com,London
```

---

## 📊 **Configuration OpenMetadata**

### **Étape 1: Attendre Démarrage**

```bash
# Vérifier logs OpenMetadata
cd docker
docker-compose logs openmetadata-server
```

### **Étape 2: Premier Accès**

1. **Ouvrir** : http://localhost:8585
2. **Créer compte admin** si demandé
3. **Configurer JWT token** pour API

### **Étape 3: Ajouter Service Dremio**

1. **Settings** → **Services** → **Databases**
2. **Add Service** → **Custom Database**
3. **Configuration** :
   ```json
   {
     "type": "CustomDatabase",
     "serviceName": "Dremio_DataLake", 
     "serviceConnection": {
       "config": {
         "sourcePythonClass": "your.connector.class",
         "connectionOptions": {
           "hostPort": "dremio:9047",
           "username": "admin",
           "password": "admin123"
         }
       }
     }
   }
   ```

---

## ⚡ **Tests de Fonctionnement**

### **Test 1: Dremio → PostgreSQL**

1. Dans Dremio, aller vers **PostgreSQL_Business**
2. Explorer **public schema**
3. Prévisualiser **customers table**
4. Vérifier **5 lignes** de données

### **Test 2: Création VDS**

1. Créer nouvelle requête dans **raw** space
2. Utiliser SQL d'exemple ci-dessus
3. **Save As** → `customer_summary`
4. Vérifier résultats

### **Test 3: MinIO Integration**

1. Upload fichier dans MinIO bucket
2. Refresh **MinIO_Storage** dans Dremio
3. Explorer fichier uploadé
4. Créer VDS depuis fichier S3

---

## 🔄 **Intégration avec notre Connecteur**

### **Script de Test**

```python
# test_dremio_integration.py
import requests

# Test connexion Dremio
response = requests.get("http://localhost:9047")
print(f"Dremio Status: {response.status_code}")

# Test API (si disponible)
# auth_data = {"userName": "admin", "password": "admin123"}
# auth = requests.post("http://localhost:9047/api/v3/login", json=auth_data)
```

### **Configuration Connector**

Éditer le fichier de configuration dans le projet `dremio_connector` :

```yaml
# config/ingestion.yaml
dremio:
  url: "http://localhost:9047"
  username: "admin" 
  password: "admin123"

openmetadata:
  api_url: "http://localhost:8585/api"
  service_name: "Dremio_DataLake"
```

---

## 🚀 **Prochaines Étapes**

### **1. Configuration Automatisée**
- Finaliser script Python de configuration
- Créer des VDS automatiquement
- Synchroniser avec OpenMetadata

### **2. Tests d'Intégration**
- Test connecteur Python vers Dremio
- Test ingestion OpenMetadata
- Test pipeline dbt

### **3. Données d'Exemple**
- Créer jeu de données complet
- Transformer avec dbt
- Visualiser lineage dans OpenMetadata

---

## 📋 **Commandes Utiles**

```bash
# Redémarrer environnement
cd docker && docker-compose restart

# Voir logs service spécifique  
docker-compose logs -f dremio

# Arrêter/Démarrer
docker-compose down
docker-compose up -d

# Test santé
python test_health.py

# Configuration Dremio
python setup_dremio_complete.py
```

---

## 🎯 **Objectifs Atteints**

- ✅ **Dremio 26.0** opérationnel
- ✅ **PostgreSQL** avec données business
- ✅ **MinIO S3** prêt pour object storage
- ✅ **Infrastructure complète** déployée

## 🎯 **Objectifs Suivants**

- 🔄 **Configuration sources** Dremio
- 🔄 **OpenMetadata** intégration
- 🔄 **Pipeline dbt** avec lineage
- 🔄 **Tests connecteur** complets

---

**🎉 Environnement Dremio Complet Prêt !**

*Configuration manuelle requise - suivre ce guide étape par étape*