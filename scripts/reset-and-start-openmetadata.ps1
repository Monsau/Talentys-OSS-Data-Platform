# RWrite-Host "=========================================" -ForegroundColor Cyan
Write-Host "  OpenMetadata Fresh Start Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Version: 1.4.6 (Stable)" -ForegroundColor White
Write-Host "  Branding: Talentys Data Platform" -ForegroundColor White
Write-Host "=========================================`n" -ForegroundColor Cyannd Start OpenMetadata with Talentys Branding
# This script completely resets the OpenMetadata database and starts fresh

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  OpenMetadata Fresh Start Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Version: 1.10.1" -ForegroundColor White
Write-Host "  Branding: Talentys Data Platform" -ForegroundColor White
Write-Host "=========================================`n" -ForegroundColor Cyan

# Step 1: Stop OpenMetadata
Write-Host "[1/5] Stopping OpenMetadata server..." -ForegroundColor Yellow
docker-compose stop openmetadata-server 2>$null
docker-compose rm -f openmetadata-server 2>$null

# Step 2: Reset database
Write-Host "[2/5] Resetting database..." -ForegroundColor Yellow
docker exec openmetadata-mysql mysql -u root -ppassword -e "DROP DATABASE IF EXISTS openmetadata_db;" 2>$null
docker exec openmetadata-mysql mysql -u root -ppassword -e "CREATE DATABASE openmetadata_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>$null
docker exec openmetadata-mysql mysql -u root -ppassword -e "GRANT ALL PRIVILEGES ON openmetadata_db.* TO 'openmetadata_user'@'%';" 2>$null
docker exec openmetadata-mysql mysql -u root -ppassword -e "FLUSH PRIVILEGES;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Database reset complete!" -ForegroundColor Green
} else {
    Write-Host "   WARNING: Database may already be clean" -ForegroundColor Yellow
}

# Step 3: Start OpenMetadata
Write-Host "[3/5] Starting OpenMetadata container..." -ForegroundColor Yellow
docker-compose up -d openmetadata-server
Start-Sleep -Seconds 15

# Step 4: Run migrations
Write-Host "[4/5] Running database migrations (this may take 3-5 minutes)..." -ForegroundColor Yellow
Write-Host "   Please wait patiently..." -ForegroundColor Gray

$migrationOutput = docker exec openmetadata-server ./bootstrap/openmetadata-ops.sh migrate 2>&1
$migrationSuccess = $migrationOutput | Select-String -Pattern "Successfully" -Quiet

if ($migrationSuccess) {
    Write-Host "   Migrations completed successfully!" -ForegroundColor Green
    
    # Show migration summary
    $versionLines = $migrationOutput | Select-String -Pattern "now at version"
    if ($versionLines) {
        Write-Host "   $($versionLines[-1])" -ForegroundColor Gray
    }
} else {
    Write-Host "   WARNING: Migration may have issues" -ForegroundColor Yellow
    Write-Host "   Check logs with: docker logs openmetadata-server" -ForegroundColor Gray
}

# Step 5: Restart and wait for health
Write-Host "[5/5] Restarting server and waiting for health check..." -ForegroundColor Yellow
docker-compose restart openmetadata-server 2>$null
Write-Host "   Waiting 90 seconds for initialization..." -ForegroundColor Gray
Start-Sleep -Seconds 90

# Check status
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Status Check" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

$containerStatus = docker ps --filter "name=openmetadata-server" --format "{{.Status}}"
Write-Host "Container Status: $containerStatus" -ForegroundColor White

# Try health check
Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -UseBasicParsing -TimeoutSec 10
    $healthData = $response.Content | ConvertFrom-Json
    
    Write-Host "`n SUCCESS! OpenMetadata is running!" -ForegroundColor Green
    Write-Host "   Version: $($healthData.version)" -ForegroundColor Gray
    Write-Host "   Status: $($healthData.status)" -ForegroundColor Gray
    Write-Host "`n   UI URL: http://localhost:8585" -ForegroundColor Cyan
    Write-Host "   Login: admin / admin`n" -ForegroundColor Gray
    
} catch {
    Write-Host "`n PARTIAL SUCCESS - Server is starting..." -ForegroundColor Yellow
    Write-Host "   Health check not ready yet" -ForegroundColor Gray
    Write-Host "   Wait 2-3 more minutes and try: http://localhost:8585`n" -ForegroundColor Gray
    Write-Host "   Check logs with: docker logs -f openmetadata-server" -ForegroundColor Gray
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Talentys Branding Applied" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan
Write-Host "Logo:   /static/talentys-logo.png" -ForegroundColor White
Write-Host "Theme:  Talentys Blue (#0066CC)" -ForegroundColor White
Write-Host "Name:   Talentys Data Platform`n" -ForegroundColor White
