# Script de Connexion Elasticsearch a Dremio
Write-Host "`n Configuration Elasticsearch..." -ForegroundColor Cyan

# Configuration
$dremioUrl = "http://localhost:9047"
$user = "admin"
$pass = "talentys123"

# 1. Creer des index de test
Write-Host "`n1. Creation index de test..." -ForegroundColor White

$log = '{"timestamp":"2025-10-19T12:00:00","level":"INFO","message":"Test log","service":"api"}'
$event = '{"timestamp":"2025-10-19T12:00:00","event_type":"login","user_id":"user1","success":true}'
$metric = '{"timestamp":"2025-10-19T12:00:00","cpu_usage":45.6,"memory_usage":78.2}'

try {
    Invoke-RestMethod -Uri "http://localhost:9200/application_logs/_doc/1" -Method Put -Body $log -ContentType "application/json" | Out-Null
    Invoke-RestMethod -Uri "http://localhost:9200/user_events/_doc/1" -Method Put -Body $event -ContentType "application/json" | Out-Null
    Invoke-RestMethod -Uri "http://localhost:9200/performance_metrics/_doc/1" -Method Put -Body $metric -ContentType "application/json" | Out-Null
    Write-Host "   OK - 3 index crees" -ForegroundColor Green
}
catch {
    Write-Host "   Erreur: $_" -ForegroundColor Yellow
}

# 2. Connexion a Dremio
Write-Host "`n2. Connexion a Dremio..." -ForegroundColor White

$loginBody = @{
    userName = $user
    password = $pass
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$dremioUrl/apiv2/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.token
    Write-Host "   OK - Token obtenu" -ForegroundColor Green
}
catch {
    Write-Host "   Erreur: $_" -ForegroundColor Red
    exit 1
}

# 3. Supprimer l'ancienne source si elle existe
Write-Host "`n3. Nettoyage ancienne source..." -ForegroundColor White

$headers = @{
    "Authorization" = "_dremio$token"
    "Content-Type" = "application/json"
}

try {
    $oldSource = Invoke-RestMethod -Uri "$dremioUrl/api/v3/catalog/by-path/Elasticsearch_Logs" -Method Get -Headers $headers
    if ($oldSource) {
        $deleteUrl = "$dremioUrl/api/v3/catalog/$($oldSource.id)?tag=$($oldSource.tag)"
        Invoke-RestMethod -Uri $deleteUrl -Method Delete -Headers $headers | Out-Null
        Write-Host "   OK - Ancienne source supprimee" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}
catch {
    Write-Host "   OK - Pas d'ancienne source" -ForegroundColor Gray
}

# 4. Creer la nouvelle source
Write-Host "`n4. Creation source Elasticsearch_Logs..." -ForegroundColor White

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
    Write-Host "   OK - Source creee avec succes!" -ForegroundColor Green
}
catch {
    Write-Host "   Erreur: $_" -ForegroundColor Red
    exit 1
}

# Succes
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " SUCCES! Elasticsearch_Logs connecte" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nProchaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Ouvrir Dremio: http://localhost:9047" -ForegroundColor White
Write-Host "  2. Rafraichir (F5)" -ForegroundColor White
Write-Host "  3. Sources > Elasticsearch_Logs" -ForegroundColor White
Write-Host "  4. Voir les 3 index:" -ForegroundColor White
Write-Host "     - application_logs" -ForegroundColor Cyan
Write-Host "     - user_events" -ForegroundColor Cyan
Write-Host "     - performance_metrics" -ForegroundColor Cyan
Write-Host ""
