# ============================================================================
# 🚀 Dremio + dbt Platform - Quick Deploy Script (Windows PowerShell)
# ============================================================================

# Enable strict mode
$ErrorActionPreference = "Stop"

# Colors
function Write-Header { Write-Host $args -ForegroundColor Cyan }
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Yellow }

# ============================================================================
# MAIN DEPLOYMENT
# ============================================================================

function Main {
    Clear-Host
    
    Write-Header "╔════════════════════════════════════════════════════════════════╗"
    Write-Header "║        🚀 Dremio + dbt Platform - Quick Deploy               ║"
    Write-Header "╚════════════════════════════════════════════════════════════════╝"
    Write-Host ""
    
    Write-Info "This script will deploy:"
    Write-Host "  • Dremio 26 OSS"
    Write-Host "  • PostgreSQL 15"
    Write-Host "  • Elasticsearch 7.17"
    Write-Host "  • MinIO"
    Write-Host "  • dbt with 12 models"
    Write-Host "  • 80K+ test records"
    Write-Host ""
    
    Pause
    
    # ========================================================================
    # Step 1: Check Prerequisites
    # ========================================================================
    Write-Header "`n[1/8] Checking Prerequisites"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    $allOk = $true
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "Docker found: $dockerVersion"
    } catch {
        Write-Error "Docker not found"
        $allOk = $false
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose found: $composeVersion"
    } catch {
        Write-Error "Docker Compose not found"
        $allOk = $false
    }
    
    # Check Python
    try {
        $pythonVersion = python --version
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python not found"
        $allOk = $false
    }
    
    if (-not $allOk) {
        Write-Error "Missing prerequisites! Please install required tools."
        exit 1
    }
    
    # ========================================================================
    # Step 2: Start Docker Services
    # ========================================================================
    Write-Header "`n[2/8] Starting Docker Services"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    Write-Info "Starting containers..."
    docker-compose up -d
    
    Write-Success "Docker services started!"
    Write-Info "Waiting for services to be ready (30s)..."
    Start-Sleep -Seconds 30
    
    # ========================================================================
    # Step 3: Create Python Virtual Environment
    # ========================================================================
    Write-Header "`n[3/8] Setting Up Python Environment"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if (Test-Path "venv") {
        Write-Info "Virtual environment already exists"
    } else {
        Write-Info "Creating virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment created!"
    }
    
    Write-Info "Installing Python packages..."
    & "venv\Scripts\pip.exe" install --upgrade pip -q
    & "venv\Scripts\pip.exe" install -r requirements.txt -q
    Write-Success "Python packages installed!"
    
    # ========================================================================
    # Step 4: Generate Test Data
    # ========================================================================
    Write-Header "`n[4/8] Generating Test Data"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    Write-Info "Generating 80K+ records..."
    & "venv\Scripts\python.exe" scripts\generate_all_data.py
    Write-Success "Data generated!"
    
    # ========================================================================
    # Step 5: Wait for Services
    # ========================================================================
    Write-Header "`n[5/8] Waiting for Services to be Ready"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    Write-Info "Waiting for Dremio (may take 2-3 minutes on first start)..."
    $timeout = 120
    $elapsed = 0
    $ready = $false
    
    while ($elapsed -lt $timeout) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9047" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            Write-Success "Dremio is ready!"
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 5
            $elapsed += 5
            Write-Host "." -NoNewline
        }
    }
    
    if (-not $ready) {
        Write-Error "Dremio not ready after ${timeout}s"
        exit 1
    }
    
    # ========================================================================
    # Step 6: Setup dbt
    # ========================================================================
    Write-Header "`n[6/8] Setting Up dbt"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    Push-Location dbt
    Write-Info "Testing dbt connection..."
    & "..\venv\Scripts\dbt.exe" debug
    Pop-Location
    
    # ========================================================================
    # Step 7: Manual Configuration Reminder
    # ========================================================================
    Write-Header "`n[7/8] Configure Dremio Sources"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    Write-Warning "MANUAL STEP REQUIRED:"
    Write-Host ""
    Write-Host "1. Open Dremio UI: http://localhost:9047"
    Write-Host "2. Login: dremio / dremio123"
    Write-Host "3. Add sources:"
    Write-Host "   • PostgreSQL: Host=postgres, Port=5432, DB=business_db, User=postgres, Password=postgres123"
    Write-Host "   • Elasticsearch: Host=elasticsearch, Port=9200"
    Write-Host "   • MinIO: Endpoint=minio:9000, Access=minioadmin, Secret=minioadmin123, Bucket=sales_data"
    Write-Host ""
    
    Pause
    
    # ========================================================================
    # Step 8: Run dbt
    # ========================================================================
    Write-Header "`n[8/8] Running dbt Models"
    Write-Header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    Push-Location dbt
    
    Write-Info "Running dbt models..."
    & "..\venv\Scripts\dbt.exe" run
    
    Write-Info "Running dbt tests..."
    & "..\venv\Scripts\dbt.exe" test
    
    Pop-Location
    
    # ========================================================================
    # Success!
    # ========================================================================
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║               🎉 DEPLOYMENT SUCCESSFUL! 🎉                    ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    Write-Header "📊 Access your platform:"
    Write-Host "  • Dremio UI:        http://localhost:9047"
    Write-Host "  • MinIO Console:    http://localhost:9001"
    Write-Host "  • Elasticsearch:    http://localhost:9200"
    Write-Host "  • PostgreSQL:       localhost:5432"
    Write-Host ""
    
    Write-Header "🔐 Credentials:"
    Write-Host "  • Dremio:     dremio / dremio123"
    Write-Host "  • MinIO:      minioadmin / minioadmin123"
    Write-Host "  • PostgreSQL: postgres / postgres123"
    Write-Host ""
    
    Write-Header "📁 Next steps:"
    Write-Host "  1. Check service status:    docker-compose ps"
    Write-Host "  2. Run example queries in Dremio UI"
    Write-Host "  3. Explore data in `$scratch.marts"
    Write-Host ""
    
    Write-Header "📚 Documentation:"
    Write-Host "  • Quick Start: QUICKSTART.md"
    Write-Host "  • Full Report: DBT_COMPLETION_REPORT.md"
    Write-Host ""
}

# Run main
Main
