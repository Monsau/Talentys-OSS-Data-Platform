# 🧹 OPEN SOURCE CLEANUP CHECKLIST

**Date**: October 16, 2025  
**Project**: Dremio + dbt + OpenMetadata  
**Goal**: Préparer le projet pour l'open source

---

## ✅ CHECKLIST DE NETTOYAGE

### 🔒 1. Sécurité et Credentials (CRITIQUE)

- [x] **.env** → Vérifier qu'il est dans `.gitignore` ✅
- [ ] Supprimer fichiers de credentials réels
- [ ] Vérifier tokens hardcodés dans le code
- [ ] Nettoyer les mots de passe de test dans les scripts
- [ ] Remplacer les vraies credentials par des exemples

### 📁 2. Fichiers Temporaires et Backups

- [ ] Supprimer `backup_20251015_224849/`
- [ ] Supprimer `archive/`
- [ ] Supprimer `logs/`
- [ ] Nettoyer fichiers `*.backup`
- [ ] Supprimer rapports temporaires JSON

### 📝 3. Documentation Obsolète

- [ ] Supprimer `README_v3.0_backup.md`
- [ ] Vérifier doublons dans docs/
- [ ] Nettoyer fichiers `*_COMPLETE.md` temporaires
- [ ] Organiser CHANGELOG

### 🐍 4. Python Artifacts

- [x] `__pycache__/` → Vérifié dans `.gitignore` ✅
- [x] `*.pyc` → Vérifié dans `.gitignore` ✅
- [x] `venv/` → Vérifié dans `.gitignore` ✅
- [ ] Vérifier pas de venv non-listés

### 🐳 5. Docker et Volumes

- [ ] Nettoyer données Docker locales
- [ ] Vérifier docker-compose examples
- [ ] S'assurer que volumes ne sont pas versionnés

### 📊 6. Données de Test

- [ ] Vérifier `data/` ne contient pas de données sensibles
- [ ] Nettoyer `opendata/` si nécessaire
- [ ] Vérifier `minio/` et `postgres/`

### 🔧 7. Scripts de Déploiement

- [ ] Vérifier `deploy*.py` ne contiennent pas de credentials
- [ ] Nettoyer hardcoded URLs/IPs
- [ ] Vérifier scripts PowerShell

### 📦 8. Configuration

- [ ] Créer `.env.example` complet
- [ ] Documenter toutes les variables d'environnement
- [ ] Vérifier `config/` ne contient pas de secrets

### 📚 9. Documentation Open Source

- [ ] README.md clair et professionnel
- [ ] CONTRIBUTING.md complet
- [ ] LICENSE vérifié (MIT)
- [ ] CHANGELOG.md à jour
- [ ] CODE_OF_CONDUCT.md
- [ ] SECURITY.md

### 🏷️ 10. Metadata GitHub

- [ ] `.github/` workflows (CI/CD)
- [ ] Issue templates
- [ ] Pull request template
- [ ] Funding (optionnel)

---

## 🚨 FICHIERS À SUPPRIMER AVANT PUSH

### Critiques
```
.env                              # Credentials réelles
backup_20251015_224849/          # Backup ancien
archive/                          # Archives
logs/                             # Logs de développement
```

### Temporaires
```
*_COMPLETE.md                     # Rapports temporaires
*_REPORT.json                     # Rapports de dev
README_v3.0_backup.md            # Backup ancien
dremio.conf.backup               # Config backup
```

### Scripts de Développement
```
cleanup_and_reorganize_i18n.py   # Script de dev
create_professional_i18n_docs.py # Script de dev
fix_business_overview.py         # Script de dev
reorganize_project.py            # Script de dev
verify_professional_docs.py      # Script de dev
```

---

## 🎯 ACTIONS PRIORITAIRES

### 1. Supprimer Credentials Hardcodées

**Fichiers à vérifier:**
- `deploy_dremio_connector.py` → Ligne 96-100 (token OpenMetadata)
- `docker-compose-*.yml` → Passwords
- Scripts PowerShell → Credentials

### 2. Créer Documentation Open Source

**Fichiers à créer:**
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`

### 3. Améliorer .gitignore

**Ajouter:**
```gitignore
# Backups
backup*/
archive/
*.backup

# Reports
*_REPORT.json
*_REPORT.md
*_COMPLETE.md

# Temporary
TODO*.md
PHASE*.md

# Data
data/
opendata/*.csv
minio/data/
postgres/data/
```

---

## 📋 COMMANDES DE NETTOYAGE

### Windows PowerShell
```powershell
# Supprimer backups
Remove-Item -Recurse -Force .\backup_20251015_224849
Remove-Item -Recurse -Force .\archive

# Supprimer logs
Remove-Item -Recurse -Force .\logs

# Supprimer fichiers temporaires
Remove-Item *.backup
Remove-Item *_COMPLETE.md
Remove-Item *_REPORT.json

# Supprimer scripts de dev
Remove-Item cleanup_and_reorganize_i18n.py
Remove-Item create_professional_i18n_docs.py
Remove-Item fix_business_overview.py
Remove-Item reorganize_project.py
Remove-Item verify_professional_docs.py
```

### Linux/Mac
```bash
# Supprimer backups
rm -rf backup_20251015_224849 archive logs

# Supprimer fichiers temporaires
rm -f *.backup *_COMPLETE.md *_REPORT.json

# Supprimer scripts de dev
rm -f cleanup_and_reorganize_i18n.py create_professional_i18n_docs.py
rm -f fix_business_overview.py reorganize_project.py verify_professional_docs.py
```

---

## 🔍 VÉRIFICATIONS FINALES

### Avant le Commit
```bash
# Vérifier pas de credentials
git grep -i "password.*=" | grep -v "example"
git grep -i "token.*=" | grep -v "example"
git grep -i "secret.*=" | grep -v "example"

# Vérifier .env n'est pas versionné
git status | grep ".env"

# Vérifier taille repo
du -sh .git

# Vérifier fichiers trackés
git ls-files | wc -l
```

### Scan de Sécurité
```bash
# Installer truffleHog (optionnel)
pip install trufflehog

# Scanner les secrets
trufflehog filesystem . --json
```

---

## 📝 TEMPLATE .env.example

```bash
# ========================================
# DREMIO + DBT + OPENMETADATA CONFIGURATION
# ========================================

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme_postgres_password
POSTGRES_DB=business_db
POSTGRES_PORT=5432

# Dremio
DREMIO_VERSION=24.3.2
DREMIO_ADMIN_USER=admin
DREMIO_ADMIN_PASSWORD=changeme_dremio_password
DREMIO_REST_PORT=9047
DREMIO_ODBC_PORT=31010
DREMIO_FLIGHT_PORT=32010

# OpenMetadata
OPENMETADATA_VERSION=1.2.0
OPENMETADATA_ADMIN_USER=admin
OPENMETADATA_ADMIN_PASSWORD=changeme_openmetadata_password
OPENMETADATA_PORT=8585
OPENMETADATA_API_TOKEN=your_jwt_token_here

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=changeme_minio_password
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001

# dbt
DBT_PROFILES_DIR=./dbt
DBT_TARGET=dev

# Superset (optionnel)
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=changeme_superset_password
SUPERSET_SECRET_KEY=generate_with_openssl_rand_base64_42
SUPERSET_PORT=8088

# Elasticsearch (optionnel)
ELASTIC_PASSWORD=changeme_elastic_password
ELASTIC_PORT=9200

# Configuration
LOG_LEVEL=INFO
DEBUG=false
```

---

## ✅ CRITÈRES DE SUCCÈS

### Avant Publication
- [ ] Aucune credential réelle dans le code
- [ ] `.env` non versionné et `.env.example` complet
- [ ] Tous les backups et archives supprimés
- [ ] Documentation open source complète
- [ ] README.md professionnel
- [ ] LICENSE présente et valide
- [ ] .gitignore exhaustif
- [ ] Pas de données sensibles

### Tests
- [ ] `git clone` sur nouveau répertoire fonctionne
- [ ] Instructions README permettent de démarrer
- [ ] Tous les exemples fonctionnent
- [ ] Documentation 18 langues accessible

---

**Status**: 🔄 EN COURS  
**Prochaine étape**: Exécuter les commandes de nettoyage
