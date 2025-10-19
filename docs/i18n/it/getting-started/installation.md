# Guida all'installazione

**Versione**: 3.2.0  
**Ultimo aggiornamento**: 2025-10-16  
**Lingua**: francese

---

## Panoramica

Questa guida fornisce istruzioni dettagliate per l'installazione e la configurazione della piattaforma dati completa, inclusi Airbyte, Dremio, dbt, Apache Superset e l'infrastruttura di supporto.

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

## Prerequisiti

### Requisiti di sistema

**Requisiti minimi:**
- **CPU**: 4 core (8+ consigliati)
- **RAM**: 8 GB (16+ GB consigliati)
- **Spazio su disco**: 20 GB disponibili (50+ GB consigliati)
- **Rete**: connessione Internet stabile per immagini Docker

**Sistemi operativi:**
-Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- macOS (11.0+)
-Windows 10/11 con WSL2

### Software richiesto

#### 1. Finestra mobile

**Versione**: 20.10 o successiva

**Facilità:**

**Linux:**
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

**macOS:**
```bash
# Télécharger et installer Docker Desktop depuis:
# https://www.docker.com/products/docker-desktop

# Vérifier l'installation
docker --version
```

**Finestre:**
```powershell
# Installer WSL2 d'abord
wsl --install

# Télécharger et installer Docker Desktop depuis:
# https://www.docker.com/products/docker-desktop

# Vérifier l'installation
docker --version
```

#### 2. Finestra mobile Componi

**Versione**: 2.0 o successiva

**Facilità:**

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

**Nota**: Docker Desktop per macOS e Windows include Docker Compose.

#### 3. Pitone

**Versione**: 3.11 o successiva

**Facilità:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**macOS:**
```bash
brew install python@3.11
```

**Finestre:**
§§§CODICE_7§§§

**Verifica:**
```bash
python --version  # ou python3 --version
pip --version     # ou pip3 --version
```

#### 4. Git

**Facilità:**

```bash
# Linux
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL

# macOS
brew install git

# Windows
winget install Git.Git
```

**Verifica:**
```bash
git --version
```

---

## Passaggi di installazione

### Passaggio 1: clonare il repository

```bash
# Cloner le dépôt
git clone https://github.com/your-org/dremiodbt.git

# Naviguer vers le répertoire du projet
cd dremiodbt

# Vérifier le contenu
ls -la
```

**Struttura prevista:**
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

### Passaggio 2: configurare l'ambiente

#### Crea file di ambiente

```bash
# Copier le fichier d'environnement exemple
cp .env.example .env

# Éditer la configuration (optionnel)
nano .env  # ou utiliser votre éditeur préféré
```

#### Variabili d'ambiente

**Configurazione di base:**
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

### Passaggio 3: installare le dipendenze Python

#### Crea l'ambiente virtuale

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Linux/macOS:
source venv/bin/activate

# Windows:
.\venv\Scripts\activate
```

#### Requisiti di installazione

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

**Pacchetti chiave installati:**
- `pyarrow>=21.0.0` - Cliente del volo Arrow
- `pandas>=2.3.0` - Manipolazione dei dati
- `dbt-core>=1.10.0` - Trasformazione dei dati
- `sqlalchemy>=2.0.0` - Connettività del database
- `pyyaml>=6.0.0` - Gestione della configurazione

### Passaggio 4: avviare i servizi Docker

#### Avvia i servizi principali

```bash
# Démarrer tous les services
docker-compose up -d

# Ou utiliser Makefile (si disponible)
make up
```

**Servizi iniziati:**
-PostgreSQL (porta 5432)
- Dremio (porte 9047, 32010)
-Apache Superset (porta 8088)
-MinIO (porte 9000, 9001)
-Elasticsearch (porta 9200)

#### Avvia Airbyte (scrivi separato)

```bash
# Démarrer les services Airbyte
docker-compose -f docker-compose-airbyte.yml up -d
```

**Servizi Airbyte avviati:**
-Server Airbyte (porta 8001)
- Interfaccia utente Web Airbyte (porta 8000)
- Lavoratore Airbyte
- Airbyte temporale
-Database Airbyte

#### Controlla lo stato dei servizi

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

##Verifica

### Passaggio 5: controlla i servizi

#### 1. PostgreSQL

```bash
# Tester la connexion
docker exec -it postgres psql -U postgres -d dremio_db -c "SELECT version();"
```

**Risultato previsto:**
```
PostgreSQL 16.x on x86_64-pc-linux-gnu
```

#### 2. Dremio

**Interfaccia Web:**
```
http://localhost:9047
```

**Prima connessione:**
- Nome utente: `admin`
- Password: `admin123`
- Ti verrà richiesto di creare un account amministratore al primo accesso

**Testa la connessione:**
```bash
# Tester le point de terminaison HTTP
curl http://localhost:9047/apiv2/login
```

#### 3. Airbyte

**Interfaccia Web:**
```
http://localhost:8000
```

**Identificatori predefiniti:**
- E-mail: `airbyte@example.com`
- Password: `password`

**Prova l'API:**
```bash
# Vérification de santé
curl http://localhost:8001/health
```

**Risposta prevista:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-16T12:00:00Z"
}
```

#### 4. Superset Apache

**Interfaccia Web:**
```
http://localhost:8088
```

**Identificatori predefiniti:**
- Nome utente: `admin`
- Password: `admin`

**Testa la connessione:**
```bash
curl http://localhost:8088/health
```

#### 5. MiniIO

**Interfaccia utente della console:**
```
http://localhost:9001
```

**Credenziali:**
- Nome utente: `minioadmin`
- Password: `minioadmin123`

**Prova l'API S3:**
```bash
# Installer le client MinIO
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configurer
./mc alias set local http://localhost:9000 minioadmin minioadmin123

# Tester
./mc ls local
```

#### 6. Ricerca elastica

**Testa la connessione:**
```bash
# Vérification de santé
curl http://localhost:9200/_cluster/health

# Obtenir les informations
curl http://localhost:9200
```

**Risposta prevista:**
```json
{
  "name": "elasticsearch",
  "cluster_name": "docker-cluster",
  "version": {
    "number": "8.15.0"
  }
}
```

### Passaggio 6: esegui controlli di integrità

```bash
# Exécuter le script de vérification de santé complet
python scripts/health_check.py

# Ou utiliser Makefile
make health-check
```

**Risultato previsto:**
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

## Configurazione post-installazione

### 1. Inizializzare Dremio

```bash
# Exécuter le script d'initialisation
python scripts/init_dremio.py
```

**Crea:**
- Utente amministratore
- Sorgenti predefinite (PostgreSQL, MinIO)
- Set di dati di esempio

### 2. Inizializza il superset

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

### 3. Configura dbt

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

### 4. Configura Airbyte

**Tramite l'interfaccia Web (http://localhost:8000):**

1. Completa la procedura guidata di configurazione
2. Configura la prima sorgente (es: PostgreSQL)
3. Configura la destinazione (es: MinIO S3)
4. Creare la connessione
5. Esegui la prima sincronizzazione

**Tramite API:**
```bash
# Voir docs/i18n/fr/guides/airbyte-integration.md pour les détails
python scripts/configure_airbyte.py
```

---

## Struttura delle directory dopo l'installazione

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

## Risoluzione dei problemi

### Problemi comuni

#### 1. Porta già utilizzata

**Errore:**
```
Error: bind: address already in use
```

**Soluzione:**
```bash
# Trouver le processus utilisant le port (exemple: 9047)
sudo lsof -i :9047

# Terminer le processus
sudo kill -9 <PID>

# Ou changer le port dans docker-compose.yml
```

#### 2. Memoria insufficiente

**Errore:**
```
ERROR: Insufficient memory available
```

**Soluzione:**
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

#### 3. I servizi non si avviano

**Controlla i log:**
```bash
# Voir tous les logs des services
docker-compose logs

# Voir un service spécifique
docker-compose logs dremio
docker-compose logs airbyte-server

# Suivre les logs en temps réel
docker-compose logs -f
```

#### 4. Problemi di rete

**Reimposta rete Docker:**
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

#### 5. Problemi di permessi (Linux)

**Soluzione:**
```bash
# Corriger les permissions des répertoires de données
sudo chown -R $USER:$USER data/ docker-volume/

# Corriger les permissions du socket Docker
sudo chmod 666 /var/run/docker.sock
```

---

## Disinstallazione

### Interrompi i servizi

```bash
# Arrêter les services principaux
docker-compose down

# Arrêter Airbyte
docker-compose -f docker-compose-airbyte.yml down
```

### Elimina dati (facoltativo)

```bash
# Supprimer les volumes (ATTENTION: Supprime toutes les données)
docker-compose down -v
docker-compose -f docker-compose-airbyte.yml down -v

# Supprimer les répertoires de données locaux
rm -rf data/ docker-volume/ logs/
```

### Elimina le immagini Docker

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

## Passaggi successivi

Dopo l'installazione riuscita:

1. **Configura origini dati** - Consulta la [Guida alla configurazione](configuration.md)
2. **Tutorial sui primi passi** - Vedi [Primi passi](first-steps.md)
3. **Configurazione Airbyte** - Consulta la [Guida all'integrazione di Airbyte](../guides/airbyte-integration.md)
4. **Dremio Setup** - Consulta la [Guida all'installazione di Dremio](../guides/dremio-setup.md)
5. **Crea modelli dbt** - Consulta la [Guida allo sviluppo dbt](../guides/dbt-development.md)
6. **Crea dashboard**: consulta la [Guida ai dashboard superset](../guides/superset-dashboards.md)

---

## Supporto

Per problemi di installazione:

- **Documentazione**: [Guida alla risoluzione dei problemi](../guides/troubleshooting.md)
- **Problemi di GitHub**: https://github.com/your-org/dremiodbt/issues
- **Comunità**: https://github.com/your-org/dremiodbt/discussions

---

**Versione della guida all'installazione**: 3.2.0  
**Ultimo aggiornamento**: 2025-10-16  
**Mantenuto da**: Team della piattaforma dati