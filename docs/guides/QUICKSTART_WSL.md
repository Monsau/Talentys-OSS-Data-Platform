# Quick Start avec WSL

## 🚀 Démarrage rapide (WSL uniquement)

### 1. Ouvrir WSL et naviguer vers le projet

```bash
wsl
cd /mnt/c/projets/dremiodbt
```

### 2. Initialiser tout l'environnement

```bash
# Copier la configuration
cp .env.example .env

# Créer et activer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances et démarrer les services
bash scripts/init.sh
```

### 3. Accéder aux interfaces

- **Dremio**: http://localhost:9047
- **OpenMetadata**: http://localhost:8585

### 4. Configurer Dremio (première fois)

1. Aller sur http://localhost:9047
2. Créer un compte admin
3. Créer l'utilisateur `dremio_user` / `dremio_password`
4. Exécuter le script SQL dans `dremio/scripts/setup.sql`

### 5. Exécuter dbt

```bash
cd dbt
dbt debug
dbt run
dbt test
cd ..
```

### 6. Lancer l'ingestion

```bash
bash scripts/run-ingestion.sh
```

### 7. Vérifier dans OpenMetadata

Aller sur http://localhost:8585 pour voir les métadonnées et la lignée.

## 🛠️ Commandes utiles

```bash
# Voir les conteneurs
docker ps

# Voir les logs
docker logs dremio
docker logs dbt-postgres

# Arrêter tout
cd docker && docker-compose down

# Redémarrer un service
docker-compose restart dremio

# Tester la connexion Dremio
bash scripts/test-dremio-connection.sh
```

## 📝 Notes importantes

- Toujours travailler depuis **WSL** pour les commandes Docker et Python
- Les fichiers sont accessibles à `/mnt/c/projets/dremiodbt` dans WSL
- Les services sont accessibles sur `localhost` depuis Windows et WSL
- Utilisez `source venv/bin/activate` pour activer l'environnement Python
