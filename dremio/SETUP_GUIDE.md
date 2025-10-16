# Guide de Configuration Dremio pour PostgreSQL JDBC

## 🎯 Objectif

Configurer **Dremio 26.0** pour être accessible via le protocole PostgreSQL JDBC, permettant à **OpenMetadata 1.9.7** d'ingérer les métadonnées.

> **Note**: OpenMetadata 1.9.7 n'a pas de connecteur natif pour Dremio 26.0, nous utilisons donc l'interface PostgreSQL.

## 📋 Configuration Actuelle

### Ports exposés par Dremio

| Port  | Usage                          | Description                                    |
|-------|--------------------------------|------------------------------------------------|
| 9047  | Web UI                         | Interface d'administration Dremio              |
| 31010 | JDBC/PostgreSQL                | Interface compatible PostgreSQL (OpenMetadata) |
| 45678 | ODBC                           | Interface ODBC                                 |
| 32010 | Arrow Flight (optionnel)       | Protocol Arrow Flight haute performance        |

### Configuration dans `dremio.conf`

```hocon
postgres: {
  enabled: true
  port: 31010
}
```

Cette configuration active l'interface PostgreSQL sur le port 31010.

## 🔧 Étapes de Configuration

### 1. Démarrer Dremio

```powershell
cd docker
docker-compose up -d dremio
```

### 2. Configuration initiale via UI

1. Accéder à http://localhost:9047
2. Créer un compte administrateur
3. Compléter la configuration initiale

### 3. Créer un utilisateur pour OpenMetadata

Dans l'UI Dremio (http://localhost:9047):

1. Aller dans **Settings** → **Users**
2. Cliquer sur **Add User**
3. Créer l'utilisateur:
   - **Username**: `dremio_user`
   - **Password**: `dremio_password`
   - **Role**: Admin (ou créer un rôle spécifique)

### 4. Créer les sources de données

#### Option A: Via SQL (recommandé)

Exécuter le script fourni:

```sql
-- Dans Dremio SQL Runner
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Créer les tables d'exemple
-- Voir dremio/scripts/setup.sql
```

#### Option B: Via UI

1. Aller dans **Data Lakes** → **Sources**
2. Ajouter une source (ex: Sample Data, S3, Azure, etc.)
3. Créer des espaces (Spaces) pour `raw`, `staging`, `marts`

### 5. Tester la connexion PostgreSQL

#### Avec psql (si disponible)

```bash
psql -h localhost -p 31010 -U dremio_user -d dremio
```

#### Avec Python

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=31010,
    user='dremio_user',
    password='dremio_password',
    database='dremio'
)

cursor = conn.cursor()
cursor.execute("SELECT CURRENT_SCHEMA, CURRENT_USER;")
print(cursor.fetchone())
cursor.close()
conn.close()
```

#### Avec le script fourni

```powershell
# Windows
.\scripts\test-dremio-connection.ps1

# Git Bash
bash scripts/test-dremio-connection.sh
```

## 🔍 Vérification

### Vérifier que l'interface PostgreSQL est active

```bash
# Vérifier que le port 31010 écoute
netstat -an | findstr 31010

# Ou avec PowerShell
Test-NetConnection -ComputerName localhost -Port 31010
```

### Lister les schémas disponibles

```sql
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name NOT IN ('sys', 'INFORMATION_SCHEMA', 'information_schema');
```

### Lister les tables dans un schéma

```sql
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'raw';
```

## ⚙️ Configuration OpenMetadata

Le fichier `openmetadata/ingestion/dremio-ingestion.yaml` est déjà configuré:

```yaml
source:
  type: postgres
  serviceConnection:
    config:
      type: Postgres
      username: dremio_user
      password: dremio_password
      hostPort: localhost:31010
      database: dremio
```

## 🐛 Dépannage

### Erreur: "Connection refused on port 31010"

**Causes possibles:**
1. Dremio n'est pas démarré
2. L'interface PostgreSQL n'est pas activée dans `dremio.conf`
3. Le port n'est pas exposé dans `docker-compose.yml`

**Solution:**
```bash
# Vérifier les logs
docker logs dremio

# Redémarrer Dremio
docker-compose restart dremio
```

### Erreur: "Authentication failed for user dremio_user"

**Causes:**
- L'utilisateur n'existe pas dans Dremio
- Mot de passe incorrect

**Solution:**
1. Se connecter à l'UI Dremio (http://localhost:9047)
2. Créer ou réinitialiser l'utilisateur `dremio_user`

### Erreur: "Schema not found"

**Causes:**
- Les schémas `raw`, `staging`, `marts` n'existent pas

**Solution:**
```sql
-- Dans Dremio SQL Runner
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
```

### Les tables ne sont pas visibles

**Causes:**
- Permissions insuffisantes
- Les tables sont dans un espace (Space) non accessible

**Solution:**
1. Vérifier les permissions de l'utilisateur
2. Donner accès aux Spaces appropriés

## 📚 Références

- [Dremio JDBC Driver Documentation](https://docs.dremio.com/current/sonar/client-applications/drivers/jdbc-driver/)
- [Dremio PostgreSQL Protocol](https://docs.dremio.com/current/sonar/client-applications/postgres/)
- [OpenMetadata PostgreSQL Connector](https://docs.open-metadata.org/connectors/database/postgres)

## 🔐 Sécurité

### Pour la production:

1. **Utiliser SSL/TLS**
   ```hocon
   postgres: {
     enabled: true
     port: 31010
     ssl.enabled: true
   }
   ```

2. **Créer un utilisateur avec permissions limitées**
   - Accès en lecture seule
   - Accès uniquement aux schémas nécessaires

3. **Utiliser des secrets management**
   - Ne pas stocker les mots de passe en clair
   - Utiliser Azure Key Vault, AWS Secrets Manager, etc.

## ✅ Checklist de Configuration

- [ ] Dremio démarré et accessible sur http://localhost:9047
- [ ] Compte administrateur créé
- [ ] Utilisateur `dremio_user` créé avec mot de passe `dremio_password`
- [ ] Port 31010 accessible
- [ ] Connexion PostgreSQL testée avec succès
- [ ] Schémas `raw`, `staging`, `marts` créés
- [ ] Tables d'exemple créées (optionnel)
- [ ] Configuration OpenMetadata testée
