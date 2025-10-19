# Start OpenMetadata Standalone with Talentys Branding
# Simple all-in-one setup without complex migrations

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  OpenMetadata Standalone Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Version: 1.5.3 (Stable All-in-One)" -ForegroundColor White
Write-Host "  Database: PostgreSQL 15" -ForegroundColor White
Write-Host "  Branding: Talentys Data Platform" -ForegroundColor White
Write-Host "=========================================`n" -ForegroundColor Cyan

# Step 1: Stop any existing OpenMetadata
Write-Host "[1/4] Stopping existing OpenMetadata containers..." -ForegroundColor Yellow
docker-compose stop openmetadata-server mysql elasticsearch 2>$null
docker stop openmetadata-standalone openmetadata-postgresql 2>$null
docker rm -f openmetadata-standalone openmetadata-postgresql 2>$null
Write-Host "   Cleanup complete!" -ForegroundColor Green

# Step 2: Start new standalone setup
Write-Host "[2/4] Starting OpenMetadata standalone..." -ForegroundColor Yellow
docker-compose -f docker-compose-openmetadata-standalone.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Containers started successfully!" -ForegroundColor Green
} else {
    Write-Host "   ERROR: Failed to start containers" -ForegroundColor Red
    exit 1
}

# Step 3: Wait for initialization
Write-Host "[3/4] Waiting for OpenMetadata initialization (2-3 minutes)..." -ForegroundColor Yellow
Write-Host "   This may take a while on first start..." -ForegroundColor Gray

$maxAttempts = 12
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts -and -not $healthy) {
    $attempt++
    Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            Write-Host "   OpenMetadata is HEALTHY!" -ForegroundColor Green
        }
    } catch {
        # Still starting...
    }
}

# Step 4: Final status
Write-Host "[4/4] Final status check..." -ForegroundColor Yellow

if ($healthy) {
    Write-Host "`n==========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! OpenMetadata is Running" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    
    $healthData = (Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -UseBasicParsing).Content | ConvertFrom-Json
    
    Write-Host "`nOpenMetadata Status:" -ForegroundColor Cyan
    Write-Host "  Version: $($healthData.version)" -ForegroundColor White
    Write-Host "  Status: $($healthData.status)" -ForegroundColor White
    
    Write-Host "`nAccess Information:" -ForegroundColor Cyan
    Write-Host "  URL: http://localhost:8585" -ForegroundColor White
    Write-Host "  Username: admin" -ForegroundColor White
    Write-Host "  Password: admin" -ForegroundColor White
    
    Write-Host "`nTalentys Branding:" -ForegroundColor Cyan
    Write-Host "  Logo: Loaded from /static/talentys-logo.png" -ForegroundColor White
    Write-Host "  Theme: Talentys Blue (#0066CC)" -ForegroundColor White
    Write-Host "  Name: Talentys Data Platform" -ForegroundColor White
    
    Write-Host "`nContainer Status:" -ForegroundColor Cyan
    docker ps --filter "name=openmetadata" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Host "`n==========================================" -ForegroundColor Green
    Write-Host "  Ready to use!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    
} else {
    Write-Host "`n==========================================" -ForegroundColor Yellow
    Write-Host "  PARTIAL SUCCESS - Still Initializing" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
    
    Write-Host "`nOpenMetadata is starting but not ready yet." -ForegroundColor White
    Write-Host "This can take up to 5 minutes on first launch.`n" -ForegroundColor White
    
    Write-Host "Container Status:" -ForegroundColor Cyan
    docker ps --filter "name=openmetadata" --format "table {{.Names}}\t{{.Status}}"
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "  1. Wait 2-3 more minutes" -ForegroundColor White
    Write-Host "  2. Try accessing: http://localhost:8585" -ForegroundColor White
    Write-Host "  3. Check logs with: docker logs -f openmetadata-standalone" -ForegroundColor White
    
    Write-Host "`nIf problems persist after 5 minutes:" -ForegroundColor Yellow
    Write-Host "  docker logs openmetadata-standalone --tail 50" -ForegroundColor Gray
}

Write-Host ""
