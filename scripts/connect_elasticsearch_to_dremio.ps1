# ========================================
# Script de Connexion Elasticsearch a Dremio
# ========================================

Write-Host "`n Configuration de la source Elasticsearch dans Dremio..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$dremioUrl = "http://localhost:9047"
$username = "admin"
$password = "talentys123"

# Fonction pour obtenir le token
function Get-DremioToken {
    $loginUrl = "$dremioUrl/apiv2/login"
    $body = @{
        userName = $username
        password = $password
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri $loginUrl -Method Post -Body $body -ContentType "application/json"
        return $response.token
    }
    catch {
        Write-Host "Erreur de connexion a Dremio: $_" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour supprimer une source existante
function Remove-DremioSource {
    param($token, $sourceName)
    
    $headers = @{
        "Authorization" = "_dremio$token"
        "Content-Type" = "application/json"
    }
    
    try {
        $catalogUrl = "$dremioUrl/api/v3/catalog/by-path/$sourceName"
        $source = Invoke-RestMethod -Uri $catalogUrl -Method Get -Headers $headers
        
        if ($source) {
            $deleteUrl = "$dremioUrl/api/v3/catalog/$($source.id)?tag=$($source.tag)"
            Invoke-RestMethod -Uri $deleteUrl -Method Delete -Headers $headers
            Write-Host "  ✓ Source '$sourceName' supprimée" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    catch {
        Write-Host "  ℹ️  Source '$sourceName' n'existe pas (OK)" -ForegroundColor Gray
    }
}

# Fonction pour créer la source Elasticsearch
function New-ElasticsearchSource {
    param($token)
    
    $headers = @{
        "Authorization" = "_dremio$token"
        "Content-Type" = "application/json"
    }
    
    $elasticSource = @{
        entityType = "source"
        name = "Elasticsearch_Logs"
        type = "ELASTIC"
        config = @{
            hostList = @(
                @{
                    hostname = "dremio-elasticsearch"
                    port = 9200
                }
            )
            authenticationType = "ANONYMOUS"
            scriptsEnabled = $true
            showHiddenIndices = $false
            sslEnabled = $false
            showIdColumn = $false
            readTimeoutMillis = 60000
            scrollTimeoutMillis = 60000
            usePainless = $true
            useWhitelist = $true
            scrollSize = 4000
            allowPushdownOnNormalizedOrAnalyzedFields = $true
            warnOnRowCountMismatch = $true
        }
        metadataPolicy = @{
            authTTLMs = 86400000
            namesRefreshMs = 3600000
            datasetRefreshAfterMs = 3600000
            datasetExpireAfterMs = 10800000
            datasetUpdateMode = "PREFETCH_QUERIED"
            deleteUnavailableDatasets = $true
            autoPromoteDatasets = $false
        }
        accelerationGracePeriodMs = 10800000
        accelerationRefreshPeriodMs = 3600000
        accelerationNeverExpire = $false
        accelerationNeverRefresh = $false
    } | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri "$dremioUrl/api/v3/catalog" -Method Post -Headers $headers -Body $elasticSource
        Write-Host "  ✓ Source 'Elasticsearch_Logs' créée avec succès!" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Host "  ❌ Erreur lors de la création: $_" -ForegroundColor Red
        Write-Host "     Détails: $($_.Exception.Message)" -ForegroundColor Gray
        return $null
    }
}

# Fonction pour créer des index de test
function New-TestIndices {
    Write-Host "`n📊 Création d'index de test dans Elasticsearch..." -ForegroundColor Cyan
    
    # Index 1: application_logs
    $log1 = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        level = "INFO"
        message = "Application started successfully"
        service = "api-gateway"
        environment = "production"
    } | ConvertTo-Json
    
    # Index 2: user_events
    $event1 = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        event_type = "login"
        user_id = "user123"
        ip_address = "192.168.1.100"
        success = $true
    } | ConvertTo-Json
    
    # Index 3: performance_metrics
    $metric1 = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        cpu_usage = 45.6
        memory_usage = 78.2
        disk_io = 1024
        network_throughput = 2048
    } | ConvertTo-Json
    
    try {
        # Créer les documents
        Invoke-RestMethod -Uri "http://localhost:9200/application_logs/_doc/1" -Method Put -Body $log1 -ContentType "application/json" | Out-Null
        Invoke-RestMethod -Uri "http://localhost:9200/user_events/_doc/1" -Method Put -Body $event1 -ContentType "application/json" | Out-Null
        Invoke-RestMethod -Uri "http://localhost:9200/performance_metrics/_doc/1" -Method Put -Body $metric1 -ContentType "application/json" | Out-Null
        
        Write-Host "  ✓ Index 'application_logs' créé" -ForegroundColor Green
        Write-Host "  ✓ Index 'user_events' créé" -ForegroundColor Green
        Write-Host "  ✓ Index 'performance_metrics' créé" -ForegroundColor Green
        
        return $true
    }
    catch {
        Write-Host "  ⚠️  Erreur lors de la création des index: $_" -ForegroundColor Yellow
        return $false
    }
}

# Script principal
Write-Host "1. Connexion à Dremio..." -ForegroundColor White
$token = Get-DremioToken

if ($token) {
    Write-Host "  ✓ Token obtenu: $($token.Substring(0, 20))..." -ForegroundColor Green
    Write-Host ""
    
    Write-Host "2. Suppression de l'ancienne source (si existe)..." -ForegroundColor White
    Remove-DremioSource -token $token -sourceName "Elasticsearch_Logs"
    Write-Host ""
    
    Write-Host "3. Création d'index de test..." -ForegroundColor White
    $indexCreated = New-TestIndices
    Write-Host ""
    
    Write-Host "4. Création de la nouvelle source Elasticsearch..." -ForegroundColor White
    $source = New-ElasticsearchSource -token $token
    
    if ($source) {
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host "✅ SUCCÈS ! Elasticsearch_Logs est maintenant connecté !" -ForegroundColor Green
        Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Prochaines étapes:" -ForegroundColor Yellow
        Write-Host "  1. Ouvrir Dremio: http://localhost:9047" -ForegroundColor White
        Write-Host "  2. Rafraîchir la page (F5)" -ForegroundColor White
        Write-Host "  3. Aller dans Sources → Elasticsearch_Logs" -ForegroundColor White
        Write-Host "  4. Vous devriez voir:" -ForegroundColor White
        Write-Host "     • application_logs" -ForegroundColor Cyan
        Write-Host "     • user_events" -ForegroundColor Cyan
        Write-Host "     • performance_metrics" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🔍 Test rapide:" -ForegroundColor Yellow
        Write-Host '  SELECT * FROM "Elasticsearch_Logs".application_logs LIMIT 10' -ForegroundColor Gray
        Write-Host ""
    }
}
else {
    Write-Host "❌ Impossible de se connecter à Dremio" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifications:" -ForegroundColor Yellow
    Write-Host "  1. Dremio est-il démarré ? docker ps | grep dremio" -ForegroundColor White
    Write-Host "  2. URL correcte ? http://localhost:9047" -ForegroundColor White
    Write-Host "  3. Credentials ? admin / talentys123" -ForegroundColor White
    Write-Host ""
}
