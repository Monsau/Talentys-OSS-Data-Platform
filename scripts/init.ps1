# PowerShell initialization script for Windows

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Initializing Dremio + dbt + OpenMetadata" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Docker is running
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Start Docker services
Write-Host "`nStarting Docker services..." -ForegroundColor Yellow
Set-Location docker
docker-compose up -d
Set-Location ..
Write-Host "Docker services started" -ForegroundColor Green

# Wait for services
Write-Host "`nWaiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check Dremio
Write-Host "`nChecking Dremio..." -ForegroundColor Yellow
$dremioReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9047" -UseBasicParsing -TimeoutSec 2
        $dremioReady = $true
        break
    } catch {
        Write-Host "Waiting for Dremio to be ready..."
        Start-Sleep -Seconds 5
    }
}
if ($dremioReady) {
    Write-Host "Dremio is ready at http://localhost:9047" -ForegroundColor Green
} else {
    Write-Host "Dremio failed to start" -ForegroundColor Red
}

# Install Python dependencies
Write-Host "`nInstalling Python dependencies from requirements.txt..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "requirements.txt not found, installing manually..." -ForegroundColor Yellow
    pip install dbt-core dbt-dremio
    pip install "openmetadata-ingestion[postgres,dbt]"
    Write-Host "Python dependencies installed" -ForegroundColor Green
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Initialization complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "1. Access Dremio at http://localhost:9047"
Write-Host "2. Access OpenMetadata at http://localhost:8585"
Write-Host "3. Run 'dbt debug' in the dbt folder"
Write-Host "4. Run '.\scripts\run-ingestion.ps1'"
