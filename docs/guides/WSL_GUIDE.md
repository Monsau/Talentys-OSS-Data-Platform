# Guide d'utilisation avec WSL (Windows Subsystem for Linux)

## 🐧 Configuration WSL

Ce projet utilise **WSL (Windows Subsystem for Linux)** pour exécuter Docker et tous les services.

## Prérequis

- Windows 10/11 avec WSL2 installé
- Docker Desktop avec intégration WSL2 activée
- Distribution Linux (Ubuntu recommandé)

## Installation WSL2

```powershell
# Installer WSL2 (si pas déjà fait)
wsl --install

# Ou installer une distribution spécifique
wsl --install -d Ubuntu

# Mettre à jour vers WSL2
wsl --set-default-version 2

# Vérifier l'installation
wsl --list --verbose
```

## Configuration Docker Desktop pour WSL2

1. Ouvrir **Docker Desktop**
2. Aller dans **Settings** → **General**
3. Cocher **"Use the WSL 2 based engine"**
4. Aller dans **Settings** → **Resources** → **WSL Integration**
5. Activer l'intégration avec votre distribution Ubuntu

## 🚀 Utilisation

### Option 1: Tout exécuter dans WSL (Recommandé)

```bash
# Ouvrir un terminal WSL
wsl

# Naviguer vers le projet (le chemin Windows est accessible via /mnt/c/)
cd /mnt/c/projets/dremiodbt

# Copier le fichier d'environnement
cp .env.example .env

# Créer un environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser l'environnement
bash scripts/init.sh

# Tester la connexion Dremio
bash scripts/test-dremio-connection.sh

# Lancer l'ingestion
bash scripts/run-ingestion.sh
```

### Option 2: Depuis PowerShell avec commandes WSL

```powershell
# Depuis PowerShell Windows
cd C:\projets\dremiodbt

# Exécuter les commandes dans WSL
wsl bash scripts/init.sh

# Ou accéder au shell WSL
wsl
```

## 📁 Chemins de fichiers

### Depuis Windows → WSL
```
C:\projets\dremiodbt  →  /mnt/c/projets/dremiodbt
```

### Depuis WSL → Windows
```
/mnt/c/projets/dremiodbt  →  C:\projets\dremiodbt
```

## 🐳 Docker dans WSL

### Vérifier Docker

```bash
# Dans WSL
docker --version
docker ps
docker-compose --version
```

### Démarrer les services

```bash
# Dans WSL, depuis le répertoire du projet
cd /mnt/c/projets/dremiodbt/docker
docker-compose up -d

# Vérifier les conteneurs
docker ps

# Voir les logs
docker logs dremio
docker logs dbt-postgres
```

### Arrêter les services

```bash
cd /mnt/c/projets/dremiodbt/docker
docker-compose down

# Avec suppression des volumes
docker-compose down -v
```

## 🔧 Configuration spécifique WSL

### Chemins dans les fichiers de configuration

Les fichiers YAML peuvent référencer des chemins de deux façons :

**1. Chemin WSL (recommandé pour l'exécution dans WSL)**
```yaml
dbtCatalogFilePath: /mnt/c/projets/dremiodbt/dbt/target/catalog.json
```

**2. Chemin Windows (pour les outils Windows)**
```yaml
dbtCatalogFilePath: c:\projets\dremiodbt\dbt\target\catalog.json
```

### Variables d'environnement

```bash
# Dans .bashrc ou .zshrc
export PROJECT_ROOT="/mnt/c/projets/dremiodbt"
export DBT_PROFILES_DIR="$PROJECT_ROOT/dbt"
```

## 🌐 Accès aux services

Les services restent accessibles depuis Windows :

- **Dremio UI**: http://localhost:9047
- **OpenMetadata UI**: http://localhost:8585
- **PostgreSQL**: localhost:5432

## 🐍 Python dans WSL

### Installation de Python

```bash
# Mettre à jour les paquets
sudo apt update
sudo apt upgrade

# Installer Python 3.10 (recommandé)
sudo apt install python3.10 python3.10-venv python3-pip

# Vérifier l'installation
python3 --version
pip3 --version
```

### Environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer
source venv/bin/activate

# Désactiver
deactivate
```

## 📝 Scripts adaptés pour WSL

Tous les scripts `.sh` fonctionnent nativement dans WSL :

```bash
# Scripts disponibles
bash scripts/init.sh
bash scripts/run-ingestion.sh
bash scripts/test-dremio-connection.sh
```

## 🔍 Dépannage WSL

### Problème : Docker n'est pas accessible

```bash
# Vérifier que Docker Desktop est démarré
# Redémarrer l'intégration WSL dans Docker Desktop Settings

# Vérifier le socket Docker
ls -la /var/run/docker.sock
```

### Problème : Permissions denied

```bash
# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrer WSL
exit
wsl --shutdown
wsl
```

### Problème : Chemins de fichiers

```bash
# Utiliser toujours les chemins absolus
# Pour WSL: /mnt/c/projets/dremiodbt
# Pour Windows: C:\projets\dremiodbt

# Convertir un chemin Windows vers WSL
wslpath 'C:\projets\dremiodbt'
# Output: /mnt/c/projets/dremiodbt

# Convertir un chemin WSL vers Windows
wslpath -w '/mnt/c/projets/dremiodbt'
# Output: C:\projets\dremiodbt
```

### Problème : Performances lentes

```bash
# Travailler directement dans le système de fichiers WSL (plus rapide)
# Au lieu de /mnt/c/projets/dremiodbt
# Utiliser ~/projects/dremiodbt

# Copier le projet dans WSL
cp -r /mnt/c/projets/dremiodbt ~/projects/
cd ~/projects/dremiodbt
```

## ⚡ Optimisations

### 1. Utiliser le système de fichiers WSL natif

```bash
# Plus rapide que /mnt/c/
mkdir -p ~/projects
cd ~/projects
cp -r /mnt/c/projets/dremiodbt .
cd dremiodbt
```

### 2. Configuration .wslconfig

Créer `C:\Users\<VotreNom>\.wslconfig` :

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
```

### 3. Configuration Docker

Dans Docker Desktop → Settings → Resources:
- Memory: 8 GB
- CPUs: 4
- Swap: 2 GB

## 🎯 Workflow recommandé

```bash
# 1. Ouvrir Windows Terminal avec Ubuntu (WSL)
# 2. Naviguer vers le projet
cd /mnt/c/projets/dremiodbt

# 3. Activer l'environnement virtuel
source venv/bin/activate

# 4. Travailler normalement
dbt run
metadata ingest -c openmetadata/ingestion/dremio-ingestion.yaml

# 5. Éditer les fichiers avec VS Code depuis WSL
code .
```

## 🔗 Ressources

- [Documentation WSL](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/windows/wsl/)
- [VS Code Remote - WSL](https://code.visualstudio.com/docs/remote/wsl)

## ✅ Checklist WSL

- [ ] WSL2 installé et configuré
- [ ] Distribution Ubuntu installée
- [ ] Docker Desktop avec intégration WSL2 activée
- [ ] Docker accessible depuis WSL (`docker ps` fonctionne)
- [ ] Python 3.10+ installé dans WSL
- [ ] pip installé dans WSL
- [ ] Projet accessible depuis WSL (`/mnt/c/projets/dremiodbt`)
- [ ] Variables d'environnement configurées
- [ ] Scripts `.sh` exécutables (`chmod +x scripts/*.sh`)
