# OpenMetadata Deployment Script - Simplified Version
# Author: Talentys Data Team
# Date: 2025-10-19

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('production', 'standalone')]
    [string]$Mode = 'production'
)

# Set error action
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = "C:\projets\dremiodbt"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "openmetadata-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Create log directory
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Console output
    switch ($Level) {
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "ERROR"   { Write-Host $logMessage -ForegroundColor Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        default   { Write-Host $logMessage -ForegroundColor Cyan }
    }
    
    # File output
    Add-Content -Path $LogFile -Value $logMessage
}

# Start deployment
Write-Log "========================================" "INFO"
Write-Log "OpenMetadata Deployment Script" "INFO"
Write-Log "Mode: $Mode" "INFO"
Write-Log "========================================" "INFO"

try {
    # Set compose file
    $composeFile = if ($Mode -eq 'production') {
        Join-Path $ProjectRoot "docker-compose-openmetadata-official.yml"
    } else {
        Join-Path $ProjectRoot "docker-compose-openmetadata-standalone.yml"
    }
    
    Write-Log "Using compose file: $composeFile" "INFO"
    
    # Check Docker
    Write-Log "Checking Docker..." "INFO"
    $dockerVersion = docker --version
    if ($LASTEXITCODE -ne 0) {
        throw "Docker is not running"
    }
    Write-Log "Docker version: $dockerVersion" "SUCCESS"
    
    # Check compose file exists
    if (!(Test-Path $composeFile)) {
        throw "Compose file not found: $composeFile"
    }
    Write-Log "Compose file found" "SUCCESS"
    
    # Pull images
    Write-Log "Pulling Docker images..." "INFO"
    Set-Location $ProjectRoot
    docker-compose -f $composeFile pull
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to pull Docker images"
    }
    Write-Log "Images pulled successfully" "SUCCESS"
    
    # Start services
    Write-Log "Starting services..." "INFO"
    docker-compose -f $composeFile up -d
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start services"
    }
    Write-Log "Services started successfully" "SUCCESS"
    
    # Wait for services
    Write-Log "Waiting for services to initialize (180 seconds)..." "INFO"
    Start-Sleep -Seconds 180
    
    # Check service status
    Write-Log "Checking service status..." "INFO"
    $containers = docker-compose -f $composeFile ps
    Write-Log "Container status:" "INFO"
    Write-Log $containers "INFO"
    
    # Test API health
    Write-Log "Testing OpenMetadata API..." "INFO"
    Start-Sleep -Seconds 30
    
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -Method GET -TimeoutSec 10
        Write-Log "API Health Check: OK" "SUCCESS"
        Write-Log "Response: $($health.Content)" "INFO"
    }
    catch {
        Write-Log "API not yet ready (this is normal on first start)" "WARNING"
        Write-Log "You can check later at: http://localhost:8585" "INFO"
    }
    
    # Show access information
    Write-Log "" "INFO"
    Write-Log "========================================" "SUCCESS"
    Write-Log "DEPLOYMENT COMPLETED!" "SUCCESS"
    Write-Log "========================================" "SUCCESS"
    Write-Log "" "INFO"
    Write-Log "OpenMetadata UI: http://localhost:8585" "SUCCESS"
    Write-Log "Default credentials: admin / admin" "SUCCESS"
    Write-Log "" "INFO"
    Write-Log "API Endpoint: http://localhost:8585/api" "INFO"
    Write-Log "Health Check: http://localhost:8585/api/v1/health" "INFO"
    Write-Log "Swagger UI: http://localhost:8585/swagger-ui" "INFO"
    Write-Log "" "INFO"
    
    if ($Mode -eq 'production') {
        Write-Log "Services deployed:" "INFO"
        Write-Log "  - MySQL: localhost:3308" "INFO"
        Write-Log "  - Elasticsearch: localhost:9200" "INFO"
        Write-Log "  - OpenMetadata Server: localhost:8585" "INFO"
        Write-Log "  - Ingestion (Airflow): localhost:8080" "INFO"
    }
    else {
        Write-Log "Services deployed:" "INFO"
        Write-Log "  - PostgreSQL: localhost:5433" "INFO"
        Write-Log "  - OpenMetadata Standalone: localhost:8585" "INFO"
    }
    
    Write-Log "" "INFO"
    Write-Log "Log file: $LogFile" "INFO"
    Write-Log "" "INFO"
    Write-Log "Next steps:" "INFO"
    Write-Log "1. Open http://localhost:8585 in your browser" "INFO"
    Write-Log "2. Login with admin / admin" "INFO"
    Write-Log "3. Configure Dremio connector" "INFO"
    Write-Log "4. Start metadata ingestion" "INFO"
    Write-Log "" "INFO"
    
    # Open browser
    Write-Log "Opening OpenMetadata UI in browser..." "INFO"
    Start-Process "http://localhost:8585"
    
}
catch {
    Write-Log "========================================" "ERROR"
    Write-Log "DEPLOYMENT FAILED!" "ERROR"
    Write-Log "========================================" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "Log file: $LogFile" "ERROR"
    Write-Log "" "ERROR"
    
    # Offer cleanup
    $response = Read-Host "Do you want to stop services? (yes/no)"
    if ($response -eq 'yes') {
        Write-Log "Stopping services..." "INFO"
        docker-compose -f $composeFile down
        Write-Log "Services stopped" "INFO"
    }
    
    exit 1
}

Write-Log "Deployment script completed" "SUCCESS"
