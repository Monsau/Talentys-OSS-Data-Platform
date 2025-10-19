# ====================================
# OPENMETADATA TALENTYS STARTUP SCRIPT
# ====================================
# This script starts the OpenMetadata stack with Talentys branding
# and verifies that everything is working correctly.

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  OPENMETADATA TALENTYS - STARTUP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set location to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "  Docker Status - OK" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - Docker is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if required files exist
$requiredFiles = @(
    "openmetadata/conf/talentys-logo.png",
    "openmetadata/conf/customization.json",
    "openmetadata/Dockerfile",
    "docker-compose.yml"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  File ${file} - OK" -ForegroundColor Green
    } else {
        Write-Host "  ERROR - Missing file ${file}" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[2/6] Building Talentys OpenMetadata image..." -ForegroundColor Yellow
Write-Host ""

docker-compose build openmetadata-server
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to build OpenMetadata image!" -ForegroundColor Red
    exit 1
}
Write-Host "  Build successful!" -ForegroundColor Green

Write-Host ""
Write-Host "[3/6] Starting MySQL and Elasticsearch..." -ForegroundColor Yellow
Write-Host ""

docker-compose up -d mysql elasticsearch

# Wait for MySQL to be healthy
Write-Host "  Waiting for MySQL to be ready..."
$maxRetries = 30
$retry = 0
while ($retry -lt $maxRetries) {
    $healthStatus = docker inspect openmetadata-mysql --format='{{.State.Health.Status}}' 2>$null
    if ($healthStatus -eq "healthy") {
        Write-Host "  MySQL Status - HEALTHY" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $retry++
    Write-Host "  Retry $retry of $maxRetries..." -ForegroundColor Gray
}

if ($retry -eq $maxRetries) {
    Write-Host "  ERROR - MySQL failed to start!" -ForegroundColor Red
    docker-compose logs mysql
    exit 1
}

# Wait for Elasticsearch to be healthy
Write-Host "  Waiting for Elasticsearch to be ready..."
$retry = 0
while ($retry -lt $maxRetries) {
    $healthStatus = docker inspect dremio-elasticsearch --format='{{.State.Health.Status}}' 2>$null
    if ($healthStatus -eq "healthy") {
        Write-Host "  Elasticsearch Status - HEALTHY" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $retry++
    Write-Host "  Retry $retry of $maxRetries..." -ForegroundColor Gray
}

if ($retry -eq $maxRetries) {
    Write-Host "  ERROR - Elasticsearch failed to start!" -ForegroundColor Red
    docker-compose logs elasticsearch
    exit 1
}

Write-Host ""
Write-Host "[4/6] Starting OpenMetadata server with Talentys branding..." -ForegroundColor Yellow
Write-Host ""

docker-compose up -d openmetadata-server

# Wait for OpenMetadata to be healthy
Write-Host "  Waiting for OpenMetadata to be ready (this may take 2-3 minutes)..."
$maxRetries = 60
$retry = 0
while ($retry -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -Method GET -UseBasicParsing -TimeoutSec 5 2>$null
        if ($response.StatusCode -eq 200) {
            Write-Host "  OpenMetadata Status - HEALTHY" -ForegroundColor Green
            break
        }
    } catch {
        # Service not ready yet
    }
    Start-Sleep -Seconds 3
    $retry++
    Write-Host "  Retry $retry of $maxRetries..." -ForegroundColor Gray
}

if ($retry -eq $maxRetries) {
    Write-Host "  ERROR - OpenMetadata failed to start!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Checking logs..." -ForegroundColor Yellow
    docker-compose logs --tail=50 openmetadata-server
    exit 1
}

Write-Host ""
Write-Host "[5/6] Verifying Talentys branding..." -ForegroundColor Yellow
Write-Host ""

# Check if customization is loaded
try {
    $config = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/system/config" -Method GET -UseBasicParsing
    Write-Host "  Configuration API - OK" -ForegroundColor Green
} catch {
    Write-Host "  WARNING - Could not verify configuration" -ForegroundColor Yellow
}

# Check if logo is accessible
try {
    $logo = Invoke-WebRequest -Uri "http://localhost:8585/static/talentys-logo.png" -Method GET -UseBasicParsing
    if ($logo.StatusCode -eq 200) {
        Write-Host "  Talentys Logo - ACCESSIBLE" -ForegroundColor Green
    }
} catch {
    Write-Host "  WARNING - Logo not accessible yet (may load after first UI access)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[6/6] Service Status Summary" -ForegroundColor Yellow
Write-Host ""

docker-compose ps | Select-String -Pattern "mysql|elasticsearch|openmetadata"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  OpenMetadata UI: http://localhost:8585" -ForegroundColor White
Write-Host "  API Documentation: http://localhost:8585/swagger-ui" -ForegroundColor White
Write-Host "  Default Credentials: admin / admin" -ForegroundColor White
Write-Host ""
Write-Host "Branding:" -ForegroundColor Cyan
Write-Host "  Logo: Talentys Data" -ForegroundColor White
Write-Host "  Theme: Talentys Blue (#0066CC)" -ForegroundColor White
Write-Host "  Application: Talentys Data Platform - Metadata Hub" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8585 in your browser" -ForegroundColor White
Write-Host "  2. Login with admin/admin" -ForegroundColor White
Write-Host "  3. Verify Talentys logo appears in navbar" -ForegroundColor White
Write-Host "  4. Check color scheme is Talentys blue" -ForegroundColor White
Write-Host "  5. Add Dremio as data source" -ForegroundColor White
Write-Host ""
Write-Host "To view logs: docker-compose logs -f openmetadata-server" -ForegroundColor Gray
Write-Host "To stop services: docker-compose down" -ForegroundColor Gray
Write-Host ""
