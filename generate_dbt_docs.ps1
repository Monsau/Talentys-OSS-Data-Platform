# Script PowerShell pour générer et servir la documentation dbt avec lineage
# Usage : clic droit > Exécuter avec PowerShell OU .\generate_dbt_docs.ps1

$projectRoot = "C:\projets\dremiodbt"
Set-Location $projectRoot
.\venv\Scripts\Activate.ps1
Set-Location "$projectRoot\dbt"

Write-Host "=== Génération de la documentation dbt ==="
dbt docs generate

Write-Host "`n=== Lancement du serveur de documentation ==="
Write-Host "📊 La documentation sera disponible sur: http://localhost:8080"
Write-Host "🔗 Le lineage interactif sera visible dans l'onglet 'Lineage Graph'"
Write-Host "`n💡 Appuyez sur Ctrl+C pour arrêter le serveur`n"

dbt docs serve --port 8080
