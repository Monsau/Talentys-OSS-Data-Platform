# Script PowerShell pour activer le venv et exécuter dbt run + dbt test
# Usage : clic droit > Exécuter avec PowerShell OU .\run_dbt.ps1

$projectRoot = "C:\projets\dremiodbt"
Set-Location $projectRoot
.\venv\Scripts\Activate.ps1
Set-Location "$projectRoot\dbt"
Write-Host "=== dbt run ==="
dbt run
Write-Host "=== dbt test ==="
dbt test
Write-Host "=== Terminé ==="
