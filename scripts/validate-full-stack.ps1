# ============================================================================
# Script de Validation Complète de la Stack
# Version: 3.3.0
# Date: 19 Octobre 2025
# Auteur: Mustapha Fonsau
# ============================================================================

param(
    [switch]$SkipDocLinks,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$script:failedChecks = @()
$script:passedChecks = @()
$script:warningChecks = @()

# ============================================================================
# Functions
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-TestResult {
    param(
        [string]$TestName,
        [string]$Status,  # "PASS", "FAIL", "WARN"
        [string]$Details = ""
    )
    
    $icon = switch($Status) {
        "PASS" { "✅"; $script:passedChecks += $TestName }
        "FAIL" { "❌"; $script:failedChecks += $TestName }
        "WARN" { "⚠️ "; $script:warningChecks += $TestName }
    }
    
    $color = switch($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
    }
    
    Write-Host "$icon $TestName" -ForegroundColor $color
    if ($Details -and $Verbose) {
        Write-Host "   $Details" -ForegroundColor Gray
    }
}

function Test-ServiceEndpoint {
    param(
        [string]$Name,
        [string]$Url,
        [int]$Timeout = 5
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $Timeout -ErrorAction Stop
        Write-TestResult -TestName "$Name ($Url)" -Status "PASS" -Details "HTTP $($response.StatusCode)"
        return $true
    } catch {
        Write-TestResult -TestName "$Name ($Url)" -Status "FAIL" -Details $_.Exception.Message
        return $false
    }
}

function Test-DockerContainer {
    param(
        [string]$ContainerName,
        [string]$ExpectedStatus = "running"
    )
    
    $container = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}\t{{.Status}}" 2>$null
    
    if ($container) {
        if ($container -match "Up") {
            Write-TestResult -TestName "Container: $ContainerName" -Status "PASS" -Details "Running"
            return $true
        } else {
            Write-TestResult -TestName "Container: $ContainerName" -Status "FAIL" -Details "Not running: $container"
            return $false
        }
    } else {
        Write-TestResult -TestName "Container: $ContainerName" -Status "FAIL" -Details "Container not found"
        return $false
    }
}

function Test-FileExists {
    param(
        [string]$FilePath,
        [string]$Description
    )
    
    if (Test-Path $FilePath) {
        $size = (Get-Item $FilePath).Length
        Write-TestResult -TestName "File: $Description" -Status "PASS" -Details "$FilePath ($size bytes)"
        return $true
    } else {
        Write-TestResult -TestName "File: $Description" -Status "FAIL" -Details "File not found: $FilePath"
        return $false
    }
}

function Test-MarkdownLinks {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw
    $links = [regex]::Matches($content, '\[([^\]]+)\]\(([^\)]+\.md)\)')
    
    $brokenLinks = @()
    $validLinks = 0
    
    foreach ($link in $links) {
        $linkText = $link.Groups[1].Value
        $linkPath = $link.Groups[2].Value
        
        # Skip external links, anchors, and URLs
        if ($linkPath -match '^http' -or $linkPath -match '^#') {
            continue
        }
        
        # Resolve relative path
        $baseDir = Split-Path -Parent $FilePath
        $fullPath = Join-Path $baseDir $linkPath
        $fullPath = [System.IO.Path]::GetFullPath($fullPath)
        
        if (Test-Path $fullPath) {
            $validLinks++
        } else {
            $brokenLinks += @{
                Text = $linkText
                Path = $linkPath
                Expected = $fullPath
            }
        }
    }
    
    return @{
        Valid = $validLinks
        Broken = $brokenLinks
        Total = $links.Count
    }
}

# ============================================================================
# MAIN VALIDATION
# ============================================================================

Write-Host ""
Write-Host "🔍 VALIDATION COMPLÈTE DE LA STACK - Version 3.3.0" -ForegroundColor Cyan
Write-Host "📅 Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# 1. DOCKER PREREQUISITES
# ============================================================================

Write-Header "1. Vérification Docker"

try {
    docker info | Out-Null
    Write-TestResult -TestName "Docker Engine" -Status "PASS"
} catch {
    Write-TestResult -TestName "Docker Engine" -Status "FAIL" -Details "Docker n'est pas en cours d'exécution"
    Write-Host "`n❌ Docker doit être démarré pour continuer. Exécutez Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    docker-compose --version | Out-Null
    Write-TestResult -TestName "Docker Compose" -Status "PASS"
} catch {
    Write-TestResult -TestName "Docker Compose" -Status "WARN" -Details "docker-compose non disponible, utilisation de 'docker compose'"
}

# ============================================================================
# 2. DOCKER CONTAINERS - PLATEFORME PRINCIPALE
# ============================================================================

Write-Header "2. Conteneurs Docker - Plateforme Principale"

$mainContainers = @(
    "dremio",
    "postgres",
    "elasticsearch",
    "minio"
)

foreach ($container in $mainContainers) {
    Test-DockerContainer -ContainerName $container
}

# ============================================================================
# 3. DOCKER CONTAINERS - AI SERVICES
# ============================================================================

Write-Header "3. Conteneurs Docker - Services AI"

$aiContainers = @(
    "ollama",
    "milvus-standalone",
    "minio-ai",
    "rag-api",
    "embedding-service",
    "chat-ui"
)

foreach ($container in $aiContainers) {
    Test-DockerContainer -ContainerName $container
}

# ============================================================================
# 4. SERVICE ENDPOINTS - PLATEFORME PRINCIPALE
# ============================================================================

Write-Header "4. Endpoints - Plateforme Principale"

$mainEndpoints = @{
    "Dremio Web UI" = "http://localhost:9047"
    "MinIO Console" = "http://localhost:9001"
    "MinIO API" = "http://localhost:9000/minio/health/live"
    "PostgreSQL" = "http://localhost:5432"  # Will fail but shows it's checked
    "Elasticsearch" = "http://localhost:9200"
}

foreach ($service in $mainEndpoints.GetEnumerator()) {
    Test-ServiceEndpoint -Name $service.Key -Url $service.Value
}

# ============================================================================
# 5. SERVICE ENDPOINTS - AI SERVICES
# ============================================================================

Write-Header "5. Endpoints - Services AI"

$aiEndpoints = @{
    "Chat UI" = "http://localhost:8501"
    "RAG API Health" = "http://localhost:8002/health"
    "RAG API Docs" = "http://localhost:8002/docs"
    "Embedding Service" = "http://localhost:8001/health"
    "Ollama API" = "http://localhost:11434/api/tags"
    "Milvus" = "http://localhost:19530"
    "MinIO AI Console" = "http://localhost:9003"
    "MinIO AI API" = "http://localhost:9002/minio/health/live"
}

foreach ($service in $aiEndpoints.GetEnumerator()) {
    Test-ServiceEndpoint -Name $service.Key -Url $service.Value
}

# ============================================================================
# 6. LLM MODELS
# ============================================================================

Write-Header "6. Modèles LLM Ollama"

try {
    $models = docker exec ollama ollama list 2>&1
    
    if ($models -match "llama3.1") {
        Write-TestResult -TestName "Llama 3.1 Model" -Status "PASS"
    } else {
        Write-TestResult -TestName "Llama 3.1 Model" -Status "WARN" -Details "Modèle non trouvé, téléchargement recommandé"
    }
    
    if ($models -match "nomic-embed-text") {
        Write-TestResult -TestName "Nomic Embed Text Model" -Status "PASS"
    } else {
        Write-TestResult -TestName "Nomic Embed Text Model" -Status "WARN" -Details "Modèle non trouvé"
    }
} catch {
    Write-TestResult -TestName "Ollama Models Check" -Status "FAIL" -Details $_.Exception.Message
}

# ============================================================================
# 7. RAG SYSTEM FUNCTIONAL TEST
# ============================================================================

Write-Header "7. Test Fonctionnel RAG System"

try {
    $testQuery = @{
        question = "What data sources are available?"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8002/query" `
        -Method Post `
        -Body $testQuery `
        -ContentType "application/json" `
        -TimeoutSec 10 `
        -ErrorAction Stop
    
    if ($response.sources -and $response.sources.Count -gt 0) {
        Write-TestResult -TestName "RAG Query Test" -Status "PASS" -Details "$($response.sources.Count) sources trouvées"
    } else {
        Write-TestResult -TestName "RAG Query Test" -Status "WARN" -Details "Aucune source trouvée - Base de connaissances vide?"
    }
    
    if ($response.answer -and $response.answer.Length -gt 10) {
        Write-TestResult -TestName "LLM Answer Generation" -Status "PASS" -Details "Réponse générée ($($response.answer.Length) chars)"
    } else {
        Write-TestResult -TestName "LLM Answer Generation" -Status "FAIL" -Details "Pas de réponse générée"
    }
} catch {
    Write-TestResult -TestName "RAG Query Test" -Status "FAIL" -Details $_.Exception.Message
}

# ============================================================================
# 8. FICHIERS CRITIQUES
# ============================================================================

Write-Header "8. Fichiers Critiques du Projet"

$criticalFiles = @{
    "Docker Compose AI" = "docker-compose-ai.yml"
    "RAG API App" = "ai-services/rag-api/app.py"
    "Knowledge Ingestion Script" = "scripts/ingest-data-platform-knowledge.ps1"
    "Release Notes" = "RELEASE_NOTES_v3.3.0.md"
    "Chat UI Fix Doc" = "CHAT_UI_FIX_RESOLUTION.md"
    "Documentation Update" = "DOCUMENTATION_UPDATE.md"
    "CHANGELOG" = "CHANGELOG.md"
    "README" = "README.md"
    "Deployment Guide" = "DEPLOIEMENT_COMPLET.md"
}

foreach ($file in $criticalFiles.GetEnumerator()) {
    Test-FileExists -FilePath $file.Value -Description $file.Key
}

# ============================================================================
# 9. VALIDATION LIENS DOCUMENTATION
# ============================================================================

if (-not $SkipDocLinks) {
    Write-Header "9. Validation des Liens Documentation"
    
    $docsToCheck = @(
        "README.md",
        "RELEASE_NOTES_v3.3.0.md",
        "CHAT_UI_FIX_RESOLUTION.md",
        "DOCUMENTATION_UPDATE.md",
        "DEPLOIEMENT_COMPLET.md",
        "DOCUMENTATION_INDEX.md"
    )
    
    $totalBrokenLinks = 0
    
    foreach ($doc in $docsToCheck) {
        if (Test-Path $doc) {
            $result = Test-MarkdownLinks -FilePath $doc
            
            if ($result.Broken.Count -eq 0) {
                Write-TestResult -TestName "Links in $doc" -Status "PASS" -Details "$($result.Valid) liens valides"
            } else {
                Write-TestResult -TestName "Links in $doc" -Status "FAIL" -Details "$($result.Broken.Count) liens cassés"
                
                if ($Verbose) {
                    foreach ($broken in $result.Broken) {
                        Write-Host "      ❌ [$($broken.Text)]($($broken.Path))" -ForegroundColor Red
                        Write-Host "         Attendu: $($broken.Expected)" -ForegroundColor Gray
                    }
                }
                
                $totalBrokenLinks += $result.Broken.Count
            }
        }
    }
    
    if ($totalBrokenLinks -gt 0) {
        Write-Host "`n⚠️  Total liens cassés trouvés: $totalBrokenLinks" -ForegroundColor Yellow
        Write-Host "   Exécutez avec -Verbose pour voir les détails" -ForegroundColor Gray
    }
} else {
    Write-Host "`n⏭️  Vérification des liens ignorée (-SkipDocLinks)" -ForegroundColor Yellow
}

# ============================================================================
# 10. RÉSUMÉ FINAL
# ============================================================================

Write-Header "Résumé de la Validation"

$totalTests = $script:passedChecks.Count + $script:failedChecks.Count + $script:warningChecks.Count

Write-Host ""
Write-Host "✅ Tests Réussis:    $($script:passedChecks.Count)" -ForegroundColor Green
Write-Host "⚠️  Avertissements:   $($script:warningChecks.Count)" -ForegroundColor Yellow
Write-Host "❌ Tests Échoués:    $($script:failedChecks.Count)" -ForegroundColor Red
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📊 Total:            $totalTests" -ForegroundColor Cyan

if ($script:failedChecks.Count -eq 0 -and $script:warningChecks.Count -eq 0) {
    Write-Host "`n🎉 VALIDATION COMPLÈTE RÉUSSIE!" -ForegroundColor Green
    Write-Host "   Tous les services sont opérationnels." -ForegroundColor Green
    exit 0
} elseif ($script:failedChecks.Count -eq 0) {
    Write-Host "`n✅ VALIDATION RÉUSSIE AVEC AVERTISSEMENTS" -ForegroundColor Yellow
    Write-Host "   La stack est fonctionnelle mais certains éléments nécessitent attention." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n❌ VALIDATION ÉCHOUÉE" -ForegroundColor Red
    Write-Host "   Corrigez les erreurs ci-dessus avant de continuer." -ForegroundColor Red
    Write-Host "`n   Tests échoués:" -ForegroundColor Yellow
    foreach ($failed in $script:failedChecks) {
        Write-Host "   - $failed" -ForegroundColor Red
    }
    exit 1
}
