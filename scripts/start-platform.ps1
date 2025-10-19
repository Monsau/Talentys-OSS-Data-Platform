#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Vérifie la disponibilité des ports et démarre la plateforme de données

.DESCRIPTION
    Ce script vérifie que tous les ports requis sont disponibles avant de démarrer
    les services Docker Compose. Il évite les conflits de ports et fournit un diagnostic
    complet en cas de problème.

.PARAMETER CheckOnly
    Vérifie uniquement les ports sans démarrer les services

.PARAMETER Service
    Démarre uniquement un service spécifique et ses dépendances

.PARAMETER Force
    Force le démarrage même si des ports sont occupés

.EXAMPLE
    .\start-platform.ps1
    Vérifie les ports et démarre tous les services

.EXAMPLE
    .\start-platform.ps1 -CheckOnly
    Vérifie uniquement la disponibilité des ports

.EXAMPLE
    .\start-platform.ps1 -Service openmetadata-server
    Démarre uniquement OpenMetadata et ses dépendances
#>

param(
    [switch]$CheckOnly,
    [string]$Service,
    [switch]$Force
)

# Configuration des ports requis
$portsConfig = @{
    # Dremio
    "Dremio UI"           = 9047
    "Dremio JDBC"         = 31010
    "Dremio ODBC"         = 45678
    "Dremio Arrow Flight" = 32010
    
    # Databases
    "PostgreSQL"          = 5432
    "MySQL"               = 3307
    
    # Object Storage
    "MinIO API"           = 9000
    "MinIO Console"       = 9001
    
    # Catalog
    "Polaris Catalog"     = 8181
    
    # Search & Metadata
    "Elasticsearch HTTP"  = 9200
    "Elasticsearch Trans" = 9300
    "OpenMetadata API"    = 8585
    "OpenMetadata Admin"  = 8586
    
    # Orchestration
    "Airflow UI"          = 8080
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-PortAvailable {
    param(
        [int]$Port
    )
    
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue -InformationLevel Quiet
        return -not $connection
    }
    catch {
        return $true  # Si erreur, considérer le port comme disponible
    }
}

function Get-ProcessOnPort {
    param(
        [int]$Port
    )
    
    try {
        $netstat = netstat -ano | Select-String ":$Port\s" | Select-String "LISTENING"
        if ($netstat) {
            $processId = ($netstat -split '\s+')[-1]
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                return "$($process.ProcessName) (PID: $processId)"
            }
            return "PID: $processId"
        }
        return $null
    }
    catch {
        return $null
    }
}

function Show-Banner {
    Write-ColorOutput "`n========================================" "Cyan"
    Write-ColorOutput "  DATA PLATFORM - PORT CHECKER" "Cyan"
    Write-ColorOutput "  Version 3.3.1 - OpenMetadata 1.10.1" "Cyan"
    Write-ColorOutput "========================================`n" "Cyan"
}

function Test-AllPorts {
    Write-ColorOutput "`n[*] Port verification...`n" "Yellow"
    
    $availablePorts = @()
    $occupiedPorts = @()
    
    foreach ($service in $portsConfig.GetEnumerator() | Sort-Object Value) {
        $port = $service.Value
        $serviceName = $service.Key
        
        $available = Test-PortAvailable -Port $port
        
        if ($available) {
            Write-ColorOutput "  ✅ Port $port ($serviceName) - DISPONIBLE" "Green"
            $availablePorts += $port
        }
        else {
            $process = Get-ProcessOnPort -Port $port
            Write-ColorOutput "  ❌ Port $port ($serviceName) - OCCUPÉ par $process" "Red"
            $occupiedPorts += @{Port = $port; Service = $serviceName; Process = $process}
        }
    }
    
    Write-ColorOutput "`n[*] Summary:" "Cyan"
    Write-ColorOutput "  Available ports: $($availablePorts.Count)" "Green"
    Write-ColorOutput "  Occupied ports: $($occupiedPorts.Count)" "Red"
    
    return @{
        Available = $availablePorts
        Occupied = $occupiedPorts
    }
}

function Show-OccupiedPortsSolution {
    param($OccupiedPorts)
    
    if ($OccupiedPorts.Count -eq 0) {
        return
    }
    
    Write-ColorOutput "`n[!] OCCUPIED PORTS DETECTED`n" "Yellow"
    Write-ColorOutput "Possible solutions:`n" "White"
    
    foreach ($portInfo in $OccupiedPorts) {
        $port = $portInfo.Port
        $service = $portInfo.Service
        $process = $portInfo.Process
        
        Write-ColorOutput "Port $port ($service) - Occupied by $process" "Red"
        Write-ColorOutput "  Solution 1: Stop the process" "White"
        if ($process -match "PID: (\d+)") {
            $pid = $matches[1]
            Write-ColorOutput "    Stop-Process -Id $pid -Force" "Gray"
        }
        
        Write-ColorOutput "  Solution 2: Change port in docker-compose.yml" "White"
        Write-ColorOutput "    Example: `"$($port + 1000):$port`"`n" "Gray"
    }
}

function Start-DockerServices {
    param(
        [string]$ServiceName
    )
    
    Write-ColorOutput "`n[*] Starting Docker services...`n" "Yellow"
    
    if ($ServiceName) {
        Write-ColorOutput "  Target service: $ServiceName" "Cyan"
        docker-compose up -d $ServiceName
    }
    else {
        Write-ColorOutput "  Starting all services" "Cyan"
        docker-compose up -d
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "`n✅ Services started successfully!`n" "Green"
        Show-ServiceStatus
    }
    else {
        Write-ColorOutput "`n❌ Error starting services`n" "Red"
        Write-ColorOutput "Check logs with: docker-compose logs`n" "Yellow"
    }
}

function Show-ServiceStatus {
    Write-ColorOutput "[*] Service status:`n" "Cyan"
    docker-compose ps
    
    Write-ColorOutput "`n[*] Access URLs:`n" "Cyan"
    Write-ColorOutput "  Dremio:        http://localhost:9047" "White"
    Write-ColorOutput "  OpenMetadata:  http://localhost:8585" "White"
    Write-ColorOutput "  Airflow:       http://localhost:8080" "White"
    Write-ColorOutput "  MinIO:         http://localhost:9001" "White"
    Write-ColorOutput "  Polaris:       http://localhost:8181" "White"
    Write-ColorOutput "  Elasticsearch: http://localhost:9200" "White"
}

function Show-QuickCommands {
    Write-ColorOutput "`n[*] Useful commands:`n" "Cyan"
    Write-ColorOutput "  View logs:              docker-compose logs -f [service]" "Gray"
    Write-ColorOutput "  Stop services:          docker-compose down" "Gray"
    Write-ColorOutput "  Restart service:        docker-compose restart [service]" "Gray"
    Write-ColorOutput "  Service status:         docker-compose ps" "Gray"
    Write-ColorOutput "  Remove volumes:         docker-compose down -v" "Gray"
}

# ============================================
# MAIN SCRIPT
# ============================================

Show-Banner

# Verifier que Docker est disponible
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "Docker is not installed or not in PATH" "Red"
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "Docker Compose is not installed or not in PATH" "Red"
    exit 1
}

# Vérifier les ports
$portStatus = Test-AllPorts

if ($CheckOnly) {
    if ($portStatus.Occupied.Count -gt 0) {
        Show-OccupiedPortsSolution -OccupiedPorts $portStatus.Occupied
        exit 1
    }
    else {
        Write-ColorOutput "`n✅ All ports are available!`n" "Green"
        exit 0
    }
}

# Si des ports sont occupés et pas de force
if ($portStatus.Occupied.Count -gt 0 -and -not $Force) {
    Show-OccupiedPortsSolution -OccupiedPorts $portStatus.Occupied
    Write-ColorOutput "`n[!] Use -Force to start despite occupied ports`n" "Yellow"
    exit 1
}

# Start services
Start-DockerServices -ServiceName $Service

Show-QuickCommands

Write-ColorOutput "`n✅ Platform ready!`n" "Green"
