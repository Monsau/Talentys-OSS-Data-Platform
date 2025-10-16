# 🔐 Credentials Standards - Projet Dremio + dbt

## Vue d'Ensemble

**Date**: 2025-10-15  
**Statut**: ✅ Standardisé partout

---

## 📋 Credentials par Service

### 1. **Dremio** 
**URL**: http://localhost:9047  
**Username**: `admin`  
**Password**: `admin123`  

**Création**:
- Automatique via API `/apiv2/bootstrap/firstuser`
- Script: `build_complete_ecosystem.py` (étape 8)
- Script: `setup_dremio_complete.py`
- Script: `init_full_dremio_env.py`

**Utilisé dans**:
- Tous les scripts Python (`DREMIO_USER`, `DREMIO_PASSWORD`)
- Documentation (README, PHASE2, STATUT_FINAL, etc.)
- Configuration dbt (`dbt/profiles.yml`)

---

### 2. **PostgreSQL**
**Host**: localhost (ou dremio-postgres dans Docker network)  
**Port**: `5432`  
**Database**: `business_db`  
**Username**: `postgres`  
**Password**: `postgres123`

**Défini dans**:
- `docker-compose.yml` (POSTGRES_USER, POSTGRES_PASSWORD)
- `build_complete_ecosystem.py` (CONFIG["postgres"])
- `setup_dremio_complete.py` (source configuration)

---

### 3. **MinIO**
**API**: http://localhost:9000  
**Console**: http://localhost:9001  
**Access Key**: `minioadmin`  
**Secret Key**: `minioadmin123`  

**Défini dans**:
- `docker-compose.yml` (MINIO_ROOT_USER, MINIO_ROOT_PASSWORD)
- `build_complete_ecosystem.py` (CONFIG["minio"])
- `setup_dremio_complete.py` (source configuration)

---

### 4. **Elasticsearch**
**URL**: http://localhost:9200  
**Authentication**: None (xpack.security.enabled=false)

**Défini dans**:
- `docker-compose.yml` (environment)
- `build_complete_ecosystem.py` (CONFIG["elasticsearch"])

---

## 🔄 Workflow d'Initialisation

### Dremio Bootstrap (Première Fois)

```python
# 1. Attendre que Dremio soit prêt
time.sleep(15)

# 2. Tester si admin existe déjà
response = requests.post(
    "http://localhost:9047/apiv2/login",
    json={"userName": "admin", "password": "admin123"}
)

# 3. Si non (status != 200), créer via bootstrap
if response.status_code != 200:
    setup_data = {
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@dremio.local",
        "createdAt": int(time.time() * 1000),
        "userName": "admin",
        "password": "admin123"
    }
    
    requests.put(
        "http://localhost:9047/apiv2/bootstrap/firstuser",
        json=setup_data
    )

# 4. Authentifier pour obtenir token
auth_response = requests.post(
    "http://localhost:9047/apiv2/login",
    json={"userName": "admin", "password": "admin123"}
)

token = auth_response.json().get("token")
headers = {"Authorization": f"_dremio{token}"}
```

---

## ✅ Vérifications Standards

### Check PostgreSQL
```bash
psql -h localhost -p 5432 -U postgres -d business_db
# Password: postgres123
```

### Check MinIO
```bash
curl http://localhost:9000/minio/health/live
# Or open: http://localhost:9001
# Login: minioadmin / minioadmin123
```

### Check Elasticsearch
```bash
curl http://localhost:9200/_cluster/health
```

### Check Dremio
```bash
curl -X POST http://localhost:9047/apiv2/login \
  -H "Content-Type: application/json" \
  -d '{"userName":"admin","password":"admin123"}'
```

---

## 📝 Scripts Utilisant Ces Credentials

### Scripts Automatisés
- ✅ `build_complete_ecosystem.py` - Orchestration complète
- ✅ `setup_dremio_complete.py` - Configuration Dremio sources
- ✅ `init_full_dremio_env.py` - Init environnement complet
- ✅ `deploy_dremio_connector.py` - Déploiement connecteur

### Scripts Utilitaires
- ✅ `create_elasticsearch_source.py`
- ✅ `configure_es_in_dremio_advanced.py`
- ✅ `create_es_vds*.py` (multiples)
- ✅ `refresh_elasticsearch_source.py`
- ✅ `force_es_metadata_refresh.py`
- ✅ `refresh_dremio_selenium.py`
- ✅ `configure_opensearch_in_dremio.py`

### Scripts Shell
- ✅ `verify_phase1.sh`
- ✅ `verify_all.sh`
- ✅ `automate_phase1.sh`

---

## 🎯 Best Practices

### 1. **Jamais hardcoder** les credentials
```python
# ❌ MAL
password = "admin123"

# ✅ BON
CONFIG = {
    "dremio": {
        "username": "admin",
        "password": "admin123"
    }
}
password = CONFIG["dremio"]["password"]
```

### 2. **Utiliser variables d'environnement en production**
```python
import os

DREMIO_USER = os.getenv("DREMIO_USER", "admin")
DREMIO_PASS = os.getenv("DREMIO_PASS", "admin123")
```

### 3. **Documenter dans .env.example**
```bash
# .env.example
DREMIO_URL=http://localhost:9047
DREMIO_USER=admin
DREMIO_PASS=admin123

POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASS=postgres123

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

---

## 🔒 Sécurité

### Développement (Actuel)
- ✅ Credentials simples pour faciliter le développement
- ✅ Pas de secrets exposés publiquement (localhost only)
- ✅ Documentation claire pour reproduction

### Production (À Faire)
- 🔲 Utiliser secrets management (Vault, AWS Secrets Manager)
- 🔲 Rotation automatique des passwords
- 🔲 Authentification LDAP/SSO pour Dremio
- 🔲 TLS/SSL pour toutes les connexions
- 🔲 Network policies strictes

---

## 📚 Références

### Documentation Officielle
- Dremio REST API: https://docs.dremio.com/cloud/reference/api/
- PostgreSQL Auth: https://www.postgresql.org/docs/current/auth-methods.html
- MinIO Admin: https://min.io/docs/minio/linux/administration/identity-access-management.html

### Scripts Projet
- `build_complete_ecosystem.py` (lignes 658-742)
- `setup_dremio_complete.py` (lignes 21-23, 28-53)
- `init_full_dremio_env.py` (lignes 140-180)

---

**Dernière Mise à Jour**: 2025-10-15  
**Responsable**: Architecture & DevOps  
**Status**: ✅ Production-Ready pour environnement de développement
