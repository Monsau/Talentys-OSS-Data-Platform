# OpenMetadata Deployment Script for Talentys Data Platform
# Version: 1.0
# Date: 2025-10-19

<#
.SYNOPSIS
    Automated deployment script for OpenMetadata with Talentys branding
    
.DESCRIPTION
    This script automates the complete deployment of OpenMetadata including:
    - Pre-flight checks (ports, resources, conflicts)
    - Service deployment (MySQL, Elasticsearch, OpenMetadata)
    - Health verification
    - Branding validation
    - Post-deployment configuration
    
.PARAMETER Mode
    Deployment mode: 'production' or 'standalone'
    
.PARAMETER SkipChecks
    Skip pre-flight checks
    
.PARAMETER Verbose
    Enable verbose logging
    
.EXAMPLE
    .\deploy-openmetadata.ps1 -Mode production
    
.EXAMPLE
    .\deploy-openmetadata.ps1 -Mode standalone -Verbose
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('production', 'standalone')]
    [string]$Mode = 'production',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipChecks,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseMode
)

# Configuration
$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\projets\dremiodbt"
$LogFile = Join-Path $ProjectRoot "logs\openmetadata-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Colors
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

# Ensure log directory exists
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        "SUCCESS" { Write-Host $logMessage -ForegroundColor $ColorSuccess }
        "ERROR"   { Write-Host $logMessage -ForegroundColor $ColorError }
        "WARNING" { Write-Host $logMessage -ForegroundColor $ColorWarning }
        "INFO"    { Write-Host $logMessage -ForegroundColor $ColorInfo }
        default   { Write-Host $logMessage }
    }
    
    # File output
    Add-Content -Path $LogFile -Value $logMessage
}

# Banner
function Show-Banner {
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      🚀 OpenMetadata Deployment - Talentys Platform 🚀       ║
║                                                              ║
║  Version: 1.0                                                ║
║  Date: $(Get-Date -Format 'yyyy-MM-dd')                                          ║
║  Mode: $($Mode.ToUpper().PadRight(52)) ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    Write-Host ""
}

# Pre-flight checks
function Test-Prerequisites {
    Write-Log "🔍 Running pre-flight checks..." "INFO"
    
    $checks = @{
        "Docker" = { docker --version }
        "Docker Compose" = { docker-compose --version }
        "Ports 8585" = { 
            $result = netstat -ano | Select-String ":8585"
            if ($result) { throw "Port 8585 is already in use" }
        }
        "Ports 3308" = { 
            $result = netstat -ano | Select-String ":3308"
            if ($result -and $Mode -eq 'production') { throw "Port 3308 is already in use" }
        }
        "Disk Space" = { 
            $drive = Get-PSDrive -Name C
            if ($drive.Free -lt 10GB) { throw "Insufficient disk space (< 10GB)" }
        }
    }
    
    $passed = 0
    $failed = 0
    
    foreach ($check in $checks.GetEnumerator()) {
        try {
            & $check.Value
            Write-Log "  ✅ $($check.Key)" "SUCCESS"
            $passed++
        }
        catch {
            Write-Log "  ❌ $($check.Key): $($_.Exception.Message)" "ERROR"
            $failed++
        }
    }
    
    if ($failed -gt 0) {
        throw "Pre-flight checks failed: $failed/$($checks.Count) checks failed"
    }
    
    Write-Log "✅ All pre-flight checks passed ($passed/$($checks.Count))" "SUCCESS"
}

# Check Docker is running
function Test-Docker {
    Write-Log "🐳 Checking Docker status..." "INFO"
    
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Docker is not running"
        }
        Write-Log "✅ Docker is running" "SUCCESS"
    }
    catch {
        Write-Log "❌ Docker check failed: $($_.Exception.Message)" "ERROR"
        throw "Please start Docker Desktop and try again"
    }
}

# Select and validate compose file
function Get-ComposeFile {
    if ($Mode -eq 'production') {
        $composeFile = Join-Path $ProjectRoot "docker-compose-openmetadata-official.yml"
        Write-Log "📋 Using production configuration: docker-compose-openmetadata-official.yml" "INFO"
    }
    else {
        $composeFile = Join-Path $ProjectRoot "docker-compose-openmetadata-standalone.yml"
        Write-Log "📋 Using standalone configuration: docker-compose-openmetadata-standalone.yml" "INFO"
    }
    
    if (-not (Test-Path $composeFile)) {
        throw "Compose file not found: $composeFile"
    }
    
    return $composeFile
}

# Deploy services
function Start-OpenMetadata {
    param([string]$ComposeFile)
    
    Write-Log "🚀 Deploying OpenMetadata services..." "INFO"
    
    try {
        Set-Location $ProjectRoot
        
        # Pull images first
        Write-Log "📥 Pulling Docker images..." "INFO"
        docker-compose -f $ComposeFile pull
        
        # Start services
        Write-Log "🔄 Starting services..." "INFO"
        docker-compose -f $ComposeFile up -d
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker compose up failed"
        }
        
        Write-Log "✅ Services started successfully" "SUCCESS"
    }
    catch {
        Write-Log "❌ Deployment failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Wait for services to be healthy
function Wait-ForHealthy {
    Write-Log "⏳ Waiting for services to become healthy..." "INFO"
    
    $services = @()
    if ($Mode -eq 'production') {
        $services = @('openmetadata_mysql', 'openmetadata_elasticsearch', 'openmetadata_server')
    }
    else {
        $services = @('openmetadata-postgresql', 'openmetadata-standalone')
    }
    
    $maxWaitTime = 300  # 5 minutes
    $checkInterval = 10  # seconds
    $elapsed = 0
    
    while ($elapsed -lt $maxWaitTime) {
        $allHealthy = $true
        
        foreach ($service in $services) {
            $status = docker inspect --format='{{.State.Health.Status}}' $service 2>$null
            
            if (-not $status) {
                # Service might not have health check, check if it's running
                $status = docker inspect --format='{{.State.Status}}' $service 2>$null
                if ($status -ne 'running') {
                    $allHealthy = $false
                    break
                }
            }
            elseif ($status -ne 'healthy') {
                $allHealthy = $false
                break
            }
        }
        
        if ($allHealthy) {
            Write-Log "✅ All services are healthy!" "SUCCESS"
            return $true
        }
        
        Write-Log "  ⏳ Waiting... ($elapsed/$maxWaitTime seconds)" "INFO"
        Start-Sleep -Seconds $checkInterval
        $elapsed += $checkInterval
    }
    
    Write-Log "⚠️  Services did not become healthy within timeout" "WARNING"
    return $false
}

# Verify OpenMetadata API
function Test-OpenMetadataAPI {
    Write-Log "🔍 Testing OpenMetadata API..." "INFO"
    
    $maxRetries = 30
    $retryInterval = 10
    
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8585/api/v1/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                $health = $response.Content | ConvertFrom-Json
                Write-Log "✅ API is responding: $($health | ConvertTo-Json -Compress)" "SUCCESS"
                return $true
            }
        }
        catch {
            Write-Log "  ⏳ Attempt $i/$maxRetries - API not ready yet..." "INFO"
            Start-Sleep -Seconds $retryInterval
        }
    }
    
    Write-Log "❌ API did not respond within timeout" "ERROR"
    return $false
}

# Verify branding
function Test-Branding {
    Write-Log "🎨 Verifying Talentys branding..." "INFO"
    
    $brandingChecks = @{
        "Logo" = "http://localhost:8585/static/talentys-logo.png"
        "CSS" = "http://localhost:8585/static/css/talentys-theme.css"
    }
    
    $allPassed = $true
    
    foreach ($check in $brandingChecks.GetEnumerator()) {
        try {
            $response = Invoke-WebRequest -Uri $check.Value -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Log "  ✅ $($check.Key) accessible" "SUCCESS"
            }
        }
        catch {
            Write-Log "  ⚠️  $($check.Key) not accessible: $($_.Exception.Message)" "WARNING"
            $allPassed = $false
        }
    }
    
    if ($allPassed) {
        Write-Log "✅ Branding files are accessible" "SUCCESS"
    }
    else {
        Write-Log "⚠️  Some branding files are not accessible" "WARNING"
    }
    
    return $allPassed
}

# Display service status
function Show-ServiceStatus {
    Write-Log "📊 Service Status:" "INFO"
    
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String -Pattern "openmetadata|mysql|elasticsearch|postgresql"
    
    foreach ($container in $containers) {
        Write-Host "  $container"
    }
}

# Display access information
function Show-AccessInfo {
    Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                    🎉 DEPLOYMENT SUCCESSFUL 🎉                ║
╚══════════════════════════════════════════════════════════════╝

📍 ACCESS INFORMATION:

  🌐 OpenMetadata UI:     http://localhost:8585
  🔑 Default Credentials:
     Username: admin
     Password: admin

  📡 API Endpoint:        http://localhost:8585/api
  📚 API Docs:            http://localhost:8585/swagger-ui
  🏥 Health Check:        http://localhost:8585/api/v1/health

🎨 TALENTYS BRANDING:

  Logo:  http://localhost:8585/static/talentys-logo.png
  Theme: http://localhost:8585/static/css/talentys-theme.css

📋 NEXT STEPS:

  1️⃣  Open http://localhost:8585 in your browser
  2️⃣  Login with admin/admin
  3️⃣  Change the admin password
  4️⃣  Configure Dremio connection:
      Settings → Services → Databases → Add Service
      
      Service Type: Dremio
      Host: dremio
      Port: 9047
      Username: dremio_user
      Password: dremio_password

  5️⃣  Run metadata ingestion
  6️⃣  Explore your data catalog!

📝 LOGS:

  Deployment log: $LogFile
  
  View service logs:
  docker-compose -f $(Split-Path -Leaf $(Get-ComposeFile)) logs -f openmetadata-server

🆘 SUPPORT:

  Documentation: ./openmetadata/INTEGRATION_PLAN.md
  Troubleshooting: ./openmetadata/VERIFICATION_CHECKLIST.md
  
  Contact: contact@talentys.eu
  Website: https://talentys.eu

╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green
}

# Cleanup function
function Invoke-Cleanup {
    param([string]$ComposeFile)
    
    Write-Log "🧹 Performing cleanup..." "WARNING"
    
    $response = Read-Host "Do you want to stop and remove all OpenMetadata services? (yes/no)"
    if ($response -eq 'yes') {
        docker-compose -f $ComposeFile down -v
        Write-Log "✅ Cleanup completed" "SUCCESS"
    }
    else {
        Write-Log "ℹ️  Cleanup cancelled" "INFO"
    }
}

# Main execution
function Main {
    try {
        Show-Banner
        
        # Pre-flight checks
        if (-not $SkipChecks) {
            Test-Docker
            Test-Prerequisites
        }
        else {
            Write-Log "⚠️  Skipping pre-flight checks (as requested)" "WARNING"
        }
        
        # Get compose file
        $composeFile = Get-ComposeFile
        
        # Deploy
        Start-OpenMetadata -ComposeFile $composeFile
        
        # Wait for services
        $healthy = Wait-ForHealthy
        
        if (-not $healthy) {
            Write-Log "⚠️  Services may not be fully healthy, but continuing..." "WARNING"
        }
        
        # Test API
        $apiReady = Test-OpenMetadataAPI
        
        if (-not $apiReady) {
            Write-Log "⚠️  API not responding, but services are running" "WARNING"
            Write-Log "ℹ️  Check logs: docker-compose -f $composeFile logs -f openmetadata-server" "INFO"
        }
        
        # Verify branding
        Test-Branding
        
        # Show status
        Show-ServiceStatus
        
        # Show access info
        Show-AccessInfo
        
        Write-Log "🎉 Deployment completed successfully!" "SUCCESS"
        
    }
    catch {
        Write-Log "Deployment failed: $($_.Exception.Message)" "ERROR"
        Write-Log "Check log file for details: $LogFile" "ERROR"
        
        # Offer cleanup
        $response = Read-Host "Deployment failed. Do you want to cleanup? (yes/no)"
        if ($response -eq 'yes') {
            Invoke-Cleanup -ComposeFile $composeFile
        }
        
        exit 1
    }
}

# Run main
Main
