# دليل التثبيت

**الإصدار**: 3.2.0  
**آخر تحديث**: 16-10-2025  
**اللغة**: الفرنسية

---

## ملخص

يوفر هذا الدليل إرشادات خطوة بخطوة لتثبيت وتكوين النظام الأساسي للبيانات بالكامل، بما في ذلك Airbyte وDremio وdbt وApache Superset والبنية التحتية الداعمة.

```mermaid
graph TD
    A[Début de l'Installation] --> B{Prérequis Satisfaits?}
    B -->|Non| C[Installer les Prérequis]
    C --> B
    B -->|Oui| D[Cloner le Dépôt]
    D --> E[Configurer l'Environnement]
    E --> F[Installer les Dépendances]
    F --> G[Démarrer les Services Docker]
    G --> H[Vérifier l'Installation]
    H --> I{Tous les Services Fonctionnent?}
    I -->|Non| J[Vérifier les Logs et Dépanner]
    J --> G
    I -->|Oui| K[Installation Terminée]
    
    style K fill:#90EE90
    style A fill:#87CEEB
```

---

## المتطلبات الأساسية

### متطلبات النظام

**الحد الأدنى من المتطلبات:**
- **وحدة المعالجة المركزية**: 4 مراكز (يوصى بـ 8+)
- **ذاكرة الوصول العشوائي**: 8 جيجابايت (يوصى بـ 16+ جيجابايت)
- **مساحة القرص**: 20 جيجابايت متاحة (يوصى بـ 50+ جيجابايت)
- **الشبكة**: اتصال إنترنت مستقر لصور Docker

**أنظمة التشغيل:**
- لينكس (أوبونتو 20.04+، CentOS 8+، ديبيان 11+)
- ماك (11.0+)
- ويندوز 10/11 مع WSL2

### البرامج المطلوبة

#### 1. عامل الميناء

**الإصدار**: 20.10 أو أعلى

**منشأة:**

**لينكس:**
```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Démarrer le service Docker
sudo systemctl start docker
sudo systemctl enable docker

# Vérifier l'installation
docker --version
```

**ماك:**
```bash
# Télécharger et installer Docker Desktop depuis:
# https://www.docker.com/products/docker-desktop

# Vérifier l'installation
docker --version
```

**الويندوز:**
```powershell
# Installer WSL2 d'abord
wsl --install

# Télécharger et installer Docker Desktop depuis:
# https://www.docker.com/products/docker-desktop

# Vérifier l'installation
docker --version
```

#### 2. إنشاء عامل الميناء

**الإصدار**: 2.0 أو أعلى

**منشأة:**

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

**ملاحظة**: يتضمن Docker Desktop لنظامي التشغيل macOS وWindows Docker Compose.

#### 3. بايثون

**الإصدار**: 3.11 أو أعلى

**منشأة:**

**لينكس (أوبونتو/ديبيان):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**ماك:**
```bash
brew install python@3.11
```

**الويندوز:**
```powershell
# Télécharger l'installateur depuis python.org
# Ou utiliser winget:
winget install Python.Python.3.11
```

**تَحَقّق:**
```bash
python --version  # ou python3 --version
pip --version     # ou pip3 --version
```

#### 4. جيت

**منشأة:**

```bash
# Linux
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL

# macOS
brew install git

# Windows
winget install Git.Git
```

**تَحَقّق:**
```bash
git --version
```

---

## خطوات التثبيت

### الخطوة 1: استنساخ المستودع

```bash
# Cloner le dépôt
git clone https://github.com/your-org/dremiodbt.git

# Naviguer vers le répertoire du projet
cd dremiodbt

# Vérifier le contenu
ls -la
```

**الهيكل المتوقع:**
```
dremiodbt/
├── docker-compose.yml
├── docker-compose-airbyte.yml
├── README.md
├── requirements.txt
├── dbt/
├── dremio_connector/
├── docs/
└── scripts/
```

### الخطوة الثانية: تكوين البيئة

#### إنشاء ملف البيئة

```bash
# Copier le fichier d'environnement exemple
cp .env.example .env

# Éditer la configuration (optionnel)
nano .env  # ou utiliser votre éditeur préféré
```

#### متغيرات البيئة

** التكوين الأساسي: **
```bash
# Projet
PROJECT_NAME=dremiodbt
ENVIRONMENT=development

# Réseau Docker
NETWORK_NAME=dremio_network

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=dremio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Dremio
DREMIO_VERSION=26.0
DREMIO_HTTP_PORT=9047
DREMIO_FLIGHT_PORT=32010
DREMIO_ADMIN_USER=admin
DREMIO_ADMIN_PASSWORD=admin123

# Airbyte
AIRBYTE_VERSION=0.50.33
AIRBYTE_HTTP_PORT=8000
AIRBYTE_API_PORT=8001

# Superset
SUPERSET_VERSION=3.0
SUPERSET_HTTP_PORT=8088
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=admin

# MinIO
MINIO_VERSION=latest
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# Elasticsearch
ELASTIC_VERSION=8.15.0
ELASTIC_HTTP_PORT=9200
```

### الخطوة 3: تثبيت تبعيات بايثون

#### إنشاء البيئة الافتراضية

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Linux/macOS:
source venv/bin/activate

# Windows:
.\venv\Scripts\activate
```

#### متطلبات التثبيت

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

** الحزم المثبتة الرئيسية: **
- `pyarrow>=21.0.0` - عميل رحلة السهم
- `pandas>=2.3.0` - معالجة البيانات
- `dbt-core>=1.10.0` - تحويل البيانات
- `sqlalchemy>=2.0.0` - الاتصال بقاعدة البيانات
- `pyyaml>=6.0.0` - إدارة التكوين

### الخطوة 4: بدء تشغيل خدمات Docker

#### ابدأ الخدمات الرئيسية

```bash
# Démarrer tous les services
docker-compose up -d

# Ou utiliser Makefile (si disponible)
make up
```

**بدأت الخدمات:**
- بوستجري إس كيو إل (المنفذ 5432)
- دريميو (المنافذ 9047، 32010)
- أباتشي سوبرسيت (المنفذ 8088)
- MiniIO (المنافذ 9000، 9001)
- Elasticsearch (المنفذ 9200)

#### بدء Airbyte (إنشاء منفصل)

```bash
# Démarrer les services Airbyte
docker-compose -f docker-compose-airbyte.yml up -d
```

**بدأت خدمات Airbyte:**
- خادم Airbyte (المنفذ 8001)
- واجهة مستخدم الويب Airbyte (المنفذ 8000)
- عامل إيربايت
- Airbyte المؤقتة
- قاعدة بيانات إيربايت

#### التحقق من حالة الخدمات

```bash
# Voir les conteneurs en cours d'exécution
docker-compose ps

# Voir tous les conteneurs (incluant Airbyte)
docker ps

# Voir les logs
docker-compose logs -f

# Voir les logs Airbyte
docker-compose -f docker-compose-airbyte.yml logs -f
```

---

## تَحَقّق

### الخطوة 5: التحقق من الخدمات

#### 1. بوستجري إس كيو إل

```bash
# Tester la connexion
docker exec -it postgres psql -U postgres -d dremio_db -c "SELECT version();"
```

**الناتج المتوقع:**
```
PostgreSQL 16.x on x86_64-pc-linux-gnu
```

#### 2. دريميو

**واجهة الويب:**
```
http://localhost:9047
```

**الاتصال الأول:**
- اسم المستخدم: `admin`
- كلمة المرور: `admin123`
- سيُطلب منك إنشاء حساب مسؤول عند الوصول لأول مرة

**اختبار الاتصال:**
```bash
# Tester le point de terminaison HTTP
curl http://localhost:9047/apiv2/login
```

#### 3. إيربايت

**واجهة الويب:**
```
http://localhost:8000
```

**المعرفات الافتراضية:**
- البريد الإلكتروني: `airbyte@example.com`
- كلمة المرور: `password`

**اختبار واجهة برمجة التطبيقات:**
```bash
# Vérification de santé
curl http://localhost:8001/health
```

**الرد المتوقع:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-16T12:00:00Z"
}
```

#### 4. أباتشي سوبرسيت

**واجهة الويب:**
```
http://localhost:8088
```

**المعرفات الافتراضية:**
- اسم المستخدم: `admin`
- كلمة المرور: `admin`

**اختبار الاتصال:**
```bash
curl http://localhost:8088/health
```

#### 5.MinIO

**واجهة مستخدم وحدة التحكم:**
```
http://localhost:9001
```

**أوراق اعتماد:**
- اسم المستخدم: `minioadmin`
- كلمة المرور: `minioadmin123`

**اختبار واجهة برمجة تطبيقات S3:**
```bash
# Installer le client MinIO
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configurer
./mc alias set local http://localhost:9000 minioadmin minioadmin123

# Tester
./mc ls local
```

#### 6. البحث المرن

**اختبار الاتصال:**
```bash
# Vérification de santé
curl http://localhost:9200/_cluster/health

# Obtenir les informations
curl http://localhost:9200
```

**الرد المتوقع:**
```json
{
  "name": "elasticsearch",
  "cluster_name": "docker-cluster",
  "version": {
    "number": "8.15.0"
  }
}
```

### الخطوة 6: إجراء عمليات التحقق من الصحة

```bash
# Exécuter le script de vérification de santé complet
python scripts/health_check.py

# Ou utiliser Makefile
make health-check
```

**الناتج المتوقع:**
```
✓ PostgreSQL: En cours d'exécution (port 5432)
✓ Dremio: En cours d'exécution (ports 9047, 32010)
✓ Airbyte: En cours d'exécution (ports 8000, 8001)
✓ Superset: En cours d'exécution (port 8088)
✓ MinIO: En cours d'exécution (ports 9000, 9001)
✓ Elasticsearch: En cours d'exécution (port 9200)

Tous les services sont opérationnels!
```

---

## تكوين ما بعد التثبيت

### 1. تهيئة دريميو

```bash
# Exécuter le script d'initialisation
python scripts/init_dremio.py
```

**إنشاء:**
- مستخدم المشرف
- المصادر الافتراضية (PostgreSQL، MinIO)
- مجموعات البيانات سبيل المثال

### 2. تهيئة المجموعة الفائقة

```bash
# Initialiser la base de données
docker exec -it superset superset db upgrade

# Créer un utilisateur administrateur (si inexistant)
docker exec -it superset superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password admin

# Initialiser Superset
docker exec -it superset superset init
```

### 3. تكوين dbt

```bash
# Naviguer vers le répertoire dbt
cd dbt

# Tester la connexion
dbt debug

# Exécuter les modèles initiaux
dbt run

# Exécuter les tests
dbt test
```

### 4. تكوين Airbyte

** عبر واجهة الويب (http://localhost:8000):**

1. أكمل معالج الإعداد
2. قم بتكوين المصدر الأول (على سبيل المثال: PostgreSQL)
3. قم بتكوين الوجهة (على سبيل المثال: MinIO S3)
4. قم بإنشاء الاتصال
5. قم بتشغيل المزامنة الأولى

** عبر واجهة برمجة التطبيقات: **
```bash
# Voir docs/i18n/fr/guides/airbyte-integration.md pour les détails
python scripts/configure_airbyte.py
```

---

## هيكل الدليل بعد التثبيت

```
dremiodbt/
├── venv/                          # Environnement virtuel Python
├── data/                          # Stockage de données local
│   ├── dremio/                    # Métadonnées Dremio
│   ├── postgres/                  # Données PostgreSQL
│   └── minio/                     # Données MinIO
├── logs/                          # Logs applicatifs
│   ├── dremio.log
│   ├── airbyte.log
│   ├── superset.log
│   └── dbt.log
├── dbt/
│   ├── models/                    # Modèles dbt
│   ├── tests/                     # Tests dbt
│   ├── target/                    # SQL compilé
│   └── logs/                      # Logs dbt
└── docker-volume/                 # Volumes persistants Docker
    ├── db-data/                   # Données de base de données
    ├── minio-data/                # Stockage objet
    └── elastic-data/              # Index de recherche
```

---

## استكشاف الأخطاء وإصلاحها

### المشاكل الشائعة

#### 1. المنفذ مستخدم بالفعل

**خطأ:**
```
Error: bind: address already in use
```

**حل:**
```bash
# Trouver le processus utilisant le port (exemple: 9047)
sudo lsof -i :9047

# Terminer le processus
sudo kill -9 <PID>

# Ou changer le port dans docker-compose.yml
```

#### 2. الذاكرة غير كافية

**خطأ:**
```
ERROR: Insufficient memory available
```

**حل:**
```bash
# Augmenter l'allocation mémoire Docker
# Docker Desktop: Paramètres > Ressources > Mémoire (16Go recommandés)

# Linux: Éditer /etc/docker/daemon.json
{
  "default-ulimits": {
    "memlock": {
      "Hard": -1,
      "Name": "memlock",
      "Soft": -1
    }
  }
}

# Redémarrer Docker
sudo systemctl restart docker
```

#### 3. عدم بدء الخدمات

** التحقق من السجلات: **
```bash
# Voir tous les logs des services
docker-compose logs

# Voir un service spécifique
docker-compose logs dremio
docker-compose logs airbyte-server

# Suivre les logs en temps réel
docker-compose logs -f
```

#### 4. مشاكل الشبكة

** إعادة تعيين شبكة دوكر: **
```bash
# Arrêter tous les services
docker-compose down
docker-compose -f docker-compose-airbyte.yml down

# Supprimer le réseau
docker network rm dremio_network

# Redémarrer les services
docker-compose up -d
docker-compose -f docker-compose-airbyte.yml up -d
```

#### 5. مشكلات الأذونات (Linux)

**حل:**
```bash
# Corriger les permissions des répertoires de données
sudo chown -R $USER:$USER data/ docker-volume/

# Corriger les permissions du socket Docker
sudo chmod 666 /var/run/docker.sock
```

---

## إلغاء التثبيت

### إيقاف الخدمات

```bash
# Arrêter les services principaux
docker-compose down

# Arrêter Airbyte
docker-compose -f docker-compose-airbyte.yml down
```

### حذف البيانات (اختياري)

```bash
# Supprimer les volumes (ATTENTION: Supprime toutes les données)
docker-compose down -v
docker-compose -f docker-compose-airbyte.yml down -v

# Supprimer les répertoires de données locaux
rm -rf data/ docker-volume/ logs/
```

### حذف صور عامل الميناء

```bash
# Lister les images
docker images | grep dremio

# Supprimer des images spécifiques
docker rmi dremio/dremio-oss:24.0
docker rmi airbyte/server:0.50.33
docker rmi apache/superset:3.0

# Supprimer toutes les images non utilisées
docker image prune -a
```

---

## الخطوات التالية

بعد التثبيت الناجح:

1. **تكوين مصادر البيانات** - راجع [دليل التكوين](configuration.md)
2. **البرنامج التعليمي للخطوات الأولى** - راجع [الخطوات الأولى](first-steps.md)
3. **تكوين Airbyte** - راجع [دليل تكامل Airbyte](../guides/airbyte-integration.md)
4. **إعداد Dremio** - راجع [دليل إعداد Dremio](../guides/dremio-setup.md)
5. **إنشاء نماذج dbt** - راجع [دليل تطوير dbt](../guides/dbt-development.md)
6. **إنشاء لوحات المعلومات** - راجع [دليل Superset Dashboards](../guides/superset-dashboards.md)

---

## يدعم

بالنسبة لمشاكل التثبيت:

- **الوثائق**: [دليل استكشاف الأخطاء وإصلاحها](../guides/troubleshooting.md)
- **مشكلات GitHub**: https://github.com/your-org/dremiodbt/issues
- **المجتمع**: https://github.com/your-org/dremiodbt/discussions

---

**إصدار دليل التثبيت**: 3.2.0  
**آخر تحديث**: 16-10-2025  
** تتم صيانته بواسطة **: فريق منصة البيانات