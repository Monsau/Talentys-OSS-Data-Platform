# ============================================================================
# ORCHESTRATION COMPLETE - DATA PLATFORM AUTO-BUILD
# ============================================================================
# 
# Déploie automatiquement:
#   - Infrastructure Docker (Dremio, PostgreSQL, MinIO, Elasticsearch, Superset)
#   - Environnement dbt + modèles
#   - Synchronisation Dremio → PostgreSQL
#   - Dashboards Superset automatiques
#   - Dashboard Open Data HTML
#
# Usage: .\deploy_all.ps1
# ============================================================================

$ErrorActionPreference = "Continue"
$startTime = Get-Date

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║       DATA PLATFORM AUTO-BUILD ORCHESTRATION               ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║  Déploiement automatique complet de la plateforme          ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$stepsCompleted = @()
$stepsFailed = @()

function Log-Step {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $icon = switch ($Level) {
        "INFO"    { "ℹ️" }
        "SUCCESS" { "✅" }
        "ERROR"   { "❌" }
        "WARNING" { "⚠️" }
        default   { "•" }
    }
    
    $color = switch ($Level) {
        "INFO"    { "White" }
        "SUCCESS" { "Green" }
        "ERROR"   { "Red" }
        "WARNING" { "Yellow" }
        default   { "White" }
    }
    
    Write-Host "[$timestamp] $icon $Message" -ForegroundColor $color
}

# ============================================================================
# ÉTAPE 0: VÉRIFICATION DES PRÉREQUIS
# ============================================================================

Log-Step "Vérification des prérequis..." "INFO"

# Docker
try {
    docker --version | Out-Null
    Log-Step "Docker installé" "SUCCESS"
} catch {
    Log-Step "Docker n'est pas installé" "ERROR"
    exit 1
}

# Docker Compose
try {
    docker-compose --version | Out-Null
    Log-Step "Docker Compose installé" "SUCCESS"
} catch {
    Log-Step "Docker Compose n'est pas installé" "ERROR"
    exit 1
}

# Python
try {
    python --version | Out-Null
    Log-Step "Python installé" "SUCCESS"
} catch {
    Log-Step "Python n'est pas installé" "ERROR"
    exit 1
}

$stepsCompleted += "Prerequisites"

# ============================================================================
# ÉTAPE 1: DÉPLOIEMENT INFRASTRUCTURE DOCKER
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 1: DÉPLOIEMENT INFRASTRUCTURE DOCKER" "INFO"
Log-Step "═" * 60 "INFO"

# Arrêter les conteneurs existants
Log-Step "Arrêt des conteneurs existants..." "INFO"
docker-compose down 2>&1 | Out-Null

# Démarrer l'infrastructure
Log-Step "Démarrage Dremio + PostgreSQL + MinIO + Elasticsearch..." "INFO"
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Log-Step "Infrastructure démarrée" "SUCCESS"
    $stepsCompleted += "Infrastructure"
    
    # Attendre que les services soient prêts
    Log-Step "Attente du démarrage des services (60 secondes)..." "INFO"
    Start-Sleep -Seconds 60
} else {
    Log-Step "Échec du démarrage de l'infrastructure" "ERROR"
    $stepsFailed += "Infrastructure"
}

# ============================================================================
# ÉTAPE 2: DÉPLOIEMENT APACHE SUPERSET
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 2: DÉPLOIEMENT APACHE SUPERSET" "INFO"
Log-Step "═" * 60 "INFO"

Log-Step "Démarrage Apache Superset..." "INFO"
docker-compose -f docker-compose-superset.yml up -d

if ($LASTEXITCODE -eq 0) {
    Log-Step "Superset démarré" "SUCCESS"
    $stepsCompleted += "Superset"
    
    Log-Step "Attente du démarrage de Superset (30 secondes)..." "INFO"
    Start-Sleep -Seconds 30
} else {
    Log-Step "Échec du démarrage de Superset" "ERROR"
    $stepsFailed += "Superset"
}

# ============================================================================
# ÉTAPE 3: CONFIGURATION ENVIRONNEMENT DBT
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 3: CONFIGURATION ENVIRONNEMENT DBT" "INFO"
Log-Step "═" * 60 "INFO"

# Vérifier si le venv existe
if (!(Test-Path "venv_dremio_311")) {
    Log-Step "Création de l'environnement virtuel..." "INFO"
    python -m venv venv_dremio_311
}

# Activer le venv et installer les dépendances
Log-Step "Installation des dépendances Python..." "INFO"
& "venv_dremio_311\Scripts\pip.exe" install -r requirements.txt -q

if ($LASTEXITCODE -eq 0) {
    Log-Step "Environnement dbt configuré" "SUCCESS"
    $stepsCompleted += "dbt Environment"
} else {
    Log-Step "Échec de la configuration dbt" "ERROR"
    $stepsFailed += "dbt Environment"
}

# ============================================================================
# ÉTAPE 4: EXÉCUTION MODELES DBT
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 4: EXÉCUTION MODELES DBT" "INFO"
Log-Step "═" * 60 "INFO"

Push-Location dbt

# dbt run
Log-Step "Exécution du modèle phase3_all_in_one..." "INFO"
& "..\venv_dremio_311\Scripts\dbt.exe" run --select phase3_all_in_one

if ($LASTEXITCODE -eq 0) {
    Log-Step "Modèle dbt exécuté" "SUCCESS"
    $stepsCompleted += "dbt Models"
} else {
    Log-Step "Échec de l'exécution dbt" "ERROR"
    $stepsFailed += "dbt Models"
}

# dbt test
Log-Step "Exécution des tests dbt..." "INFO"
& "..\venv_dremio_311\Scripts\dbt.exe" test

Pop-Location

# ============================================================================
# ÉTAPE 5: SYNCHRONISATION DREMIO → POSTGRESQL
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 5: SYNCHRONISATION DREMIO → POSTGRESQL" "INFO"
Log-Step "═" * 60 "INFO"

if (Test-Path "scripts\sync_dremio_realtime.py") {
    Log-Step "Synchronisation des données Dremio..." "INFO"
    & "venv_dremio_311\Scripts\python.exe" "scripts\sync_dremio_realtime.py"
    
    if ($LASTEXITCODE -eq 0) {
        Log-Step "Synchronisation réussie" "SUCCESS"
        $stepsCompleted += "Dremio Sync"
    } else {
        Log-Step "Échec de la synchronisation" "ERROR"
        $stepsFailed += "Dremio Sync"
    }
} else {
    Log-Step "Script de synchronisation introuvable" "WARNING"
}

# ============================================================================
# ÉTAPE 6: CRÉATION DASHBOARDS SUPERSET
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 6: CRÉATION DASHBOARDS SUPERSET" "INFO"
Log-Step "═" * 60 "INFO"

# Dashboard 1: PostgreSQL
if (Test-Path "scripts\populate_superset.py") {
    Log-Step "Création Dashboard 1 (PostgreSQL)..." "INFO"
    & "venv_dremio_311\Scripts\python.exe" "scripts\populate_superset.py"
}

# Dashboard 2: Dremio
if (Test-Path "scripts\rebuild_dremio_dashboard.py") {
    Log-Step "Création Dashboard 2 (Dremio)..." "INFO"
    & "venv_dremio_311\Scripts\python.exe" "scripts\rebuild_dremio_dashboard.py"
}

$stepsCompleted += "Superset Dashboards"

# ============================================================================
# ÉTAPE 7: GÉNÉRATION DASHBOARD OPEN DATA
# ============================================================================

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "ÉTAPE 7: GÉNÉRATION DASHBOARD OPEN DATA" "INFO"
Log-Step "═" * 60 "INFO"

if (Test-Path "scripts\generate_opendata_dashboard.py") {
    Log-Step "Génération du dashboard HTML Open Data..." "INFO"
    & "venv_dremio_311\Scripts\python.exe" "scripts\generate_opendata_dashboard.py"
    $stepsCompleted += "Open Data Dashboard"
} else {
    Log-Step "Script Open Data introuvable, skip" "WARNING"
}

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================

$elapsed = (Get-Date) - $startTime
$elapsedSeconds = [math]::Round($elapsed.TotalSeconds, 1)

Write-Host ""
Log-Step "═" * 60 "INFO"
Log-Step "RÉSUMÉ DU DÉPLOIEMENT" "INFO"
Log-Step "═" * 60 "INFO"

Write-Host ""
Write-Host "✅ ÉTAPES COMPLÉTÉES:" -ForegroundColor Green
foreach ($step in $stepsCompleted) {
    Write-Host "   ✅ $step" -ForegroundColor Green
}

if ($stepsFailed.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ ÉTAPES ÉCHOUÉES:" -ForegroundColor Red
    foreach ($step in $stepsFailed) {
        Write-Host "   ❌ $step" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 DASHBOARDS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "   • Dremio UI: http://localhost:9047 (admin/admin123)"
Write-Host "   • Superset Dashboard 1: http://localhost:8088/superset/dashboard/1/"
Write-Host "   • Superset Dashboard 2 (Dremio): http://localhost:8088/superset/dashboard/2/"
Write-Host "   • Open Data HTML: file:///c:/projets/dremiodbt/opendata/dashboard.html"

Write-Host ""
Write-Host "🔄 SYNCHRONISATION:" -ForegroundColor Cyan
Write-Host "   • Manuel: python scripts\sync_dremio_realtime.py"
Write-Host "   • Auto: python scripts\sync_dremio_realtime.py --continuous 5"

Write-Host ""
Write-Host "📄 DOCUMENTATION:" -ForegroundColor Cyan
Write-Host "   • SUPERSET_DREMIO_FINAL.md (guide complet)"
Write-Host "   • PHASE3_COMPLETE_SUMMARY.md"

Write-Host ""
Log-Step "Temps total: $elapsedSeconds secondes" "INFO"
Write-Host ""
Log-Step "═" * 60 "INFO"

if ($stepsFailed.Count -eq 0) {
    Write-Host "🎉 DÉPLOIEMENT COMPLET RÉUSSI!" -ForegroundColor Green
} else {
    Write-Host "⚠️ DÉPLOIEMENT PARTIEL - Vérifiez les erreurs ci-dessus" -ForegroundColor Yellow
}

Log-Step "═" * 60 "INFO"
Write-Host ""
