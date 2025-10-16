# PowerShell ingestion script for Windows

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Running Dremio to OpenMetadata Ingestion" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Run dbt
Write-Host "`nRunning dbt models..." -ForegroundColor Yellow
Set-Location "$projectRoot\dbt"
dbt deps
dbt debug
dbt run
dbt test
dbt docs generate
Set-Location $projectRoot
Write-Host "dbt models executed successfully" -ForegroundColor Green

# Run Dremio ingestion
Write-Host "`nRunning Dremio ingestion to OpenMetadata..." -ForegroundColor Yellow
metadata ingest -c openmetadata\ingestion\dremio-ingestion.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dremio ingestion completed successfully" -ForegroundColor Green
} else {
    Write-Host "Dremio ingestion failed" -ForegroundColor Red
    exit 1
}

# Run dbt ingestion
Write-Host "`nRunning dbt ingestion to OpenMetadata..." -ForegroundColor Yellow
metadata ingest -c openmetadata\ingestion\dbt-ingestion.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "dbt ingestion completed successfully" -ForegroundColor Green
} else {
    Write-Host "dbt ingestion failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Ingestion complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nCheck OpenMetadata at http://localhost:8585"
Write-Host "to view your ingested data and lineage"
