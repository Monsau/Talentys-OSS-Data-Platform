# Guide de Connexion Manuelle Elasticsearch à Dremio

## Problème Résolu ✅

Elasticsearch est maintenant **démarré** et **opérationnel** sur le port 9200.

## Configuration Manuelle dans Dremio (5 minutes)

### Étape 1: Ouvrir Dremio

1. Ouvrir le navigateur: **http://localhost:9047**
2. Se connecter avec vos credentials habituels

### Étape 2: Supprimer l'ancienne source (si rouge)

1. Aller dans **Sources** (menu gauche)
2. Si vous voyez "Elasticsearch_Logs" avec une icône rouge ❌
3. Cliquer sur les **...** (3 points) à droite
4. Sélectionner **"Remove Source"**
5. Confirmer la suppression

### Étape 3: Créer la Nouvelle Source

1. Cliquer sur le bouton **"+ Add Source"** (en haut à droite)

2. Sélectionner **"Elasticsearch"** dans la liste

3. Remplir le formulaire:
   ```
   Name: Elasticsearch_Logs
   
   Host: dremio-elasticsearch
   Port: 9200
   
   Authentication: None (ou Anonymous)
   
   ☑ Enable scripts
   ☐ Show hidden indices  
   ☐ Enable SSL
   ☐ Show _id column
   
   Read Timeout: 60000
   Scroll Timeout: 60000
   Scroll Size: 4000
   ```

4. Cliquer sur **"Save"** en bas

### Étape 4: Vérifier la Connexion

1. Aller dans **Sources** → **Elasticsearch_Logs**

2. Vous devriez voir les index créés automatiquement par Elasticsearch:
   - `.ds-*` (index système - ignorez)
   - `application_logs` ← **Index créé!**
   - `user_events` ← **Index créé!**  
   - `performance_metrics` ← **Index potentiel**

3. Si la source apparaît en **vert** ✅ = succès!

### Étape 5: Tester une Requête

Dans l'onglet **SQL Runner**:

```sql
-- Afficher les logs d'application
SELECT * 
FROM "Elasticsearch_Logs"."application_logs" 
LIMIT 10;

-- Afficher les événements utilisateurs
SELECT * 
FROM "Elasticsearch_Logs"."user_events" 
LIMIT 10;
```

---

## Alternative: Créer Plus de Données de Test

Si vous voulez plus de données dans Elasticsearch, vous pouvez exécuter:

```powershell
# Créer 100 documents de logs
for ($i=1; $i -le 100; $i++) {
    $log = @{
        timestamp = (Get-Date).AddMinutes(-$i).ToString("yyyy-MM-ddTHH:mm:ss")
        level = @("INFO","WARN","ERROR")[(Get-Random -Maximum 3)]
        message = "Log message number $i"
        service = @("api-gateway","auth-service","data-processor")[(Get-Random -Maximum 3)]
        environment = "production"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:9200/application_logs/_doc/$i" `
        -Method Put -Body $log -ContentType "application/json" | Out-Null
}

Write-Host "100 logs crees!" -ForegroundColor Green
```

---

## Résumé

✅ **Elasticsearch démarré**: `dremio-elasticsearch` sur port 9200  
✅ **Index créés**: application_logs, user_events  
⏳ **Action requise**: Configurer manuellement dans Dremio (5 min)

---

## Troubleshooting

### Source apparaît rouge dans Dremio

**Cause**: Mauvaise configuration ou Elasticsearch non accessible

**Solution**:
1. Vérifier qu'Elasticsearch est en marche:
   ```powershell
   docker ps | Select-String elasticsearch
   ```
2. Tester la connexion:
   ```powershell
   curl http://localhost:9200
   ```
3. Re-créer la source avec le bon hostname: `dremio-elasticsearch`

### Aucun index visible

**Cause**: Aucune donnée dans Elasticsearch

**Solution**:
1. Créer des données de test (voir section Alternative ci-dessus)
2. Rafraîchir la source dans Dremio (icône refresh)

### Erreur "Connection refused"

**Cause**: Elasticsearch n'est pas démarré

**Solution**:
```powershell
docker-compose up -d elasticsearch
Start-Sleep -Seconds 20
docker logs dremio-elasticsearch --tail 20
```

---

**Support**: support@talentys.eu  
**Documentation**: Talentys Data Platform v1.1
