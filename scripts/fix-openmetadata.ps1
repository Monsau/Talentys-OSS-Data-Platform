# ====================================
# QUICK FIX - OpenMetadata Secrets Manager
# ====================================

Write-Host "Fixing OpenMetadata Secrets Manager configuration..." -ForegroundColor Cyan

# Remove the problematic SECRET_MANAGER variable from docker-compose
$composePath = "docker-compose.yml"
$content = Get-Content $composePath -Raw

# Option: Comment out the SECRET_MANAGER line
$content = $content -replace '(\s+- SECRET_MANAGER=.+)', '      # $1  # Disabled - causes error in 1.10.1'

Set-Content -Path $composePath -Value $content

Write-Host "Configuration fixed!" -ForegroundColor Green
Write-Host "`nRestarting OpenMetadata..." -ForegroundColor Yellow

docker-compose stop openmetadata-server
docker-compose rm -f openmetadata-server
docker-compose up -d openmetadata-server

Write-Host "`nWaiting for initialization (2 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

Write-Host "`nChecking health..." -ForegroundColor Cyan
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "`n SUCCESS - OpenMetadata is HEALTHY!" -ForegroundColor Green
    Write-Host $health.Content
    Write-Host "`nAccess UI: http://localhost:8585" -ForegroundColor Cyan
    Write-Host "Credentials: admin / admin" -ForegroundColor Yellow
} catch {
    Write-Host "`nStill initializing. Check logs:" -ForegroundColor Yellow
    Write-Host "docker logs openmetadata-server -f" -ForegroundColor Gray
}
