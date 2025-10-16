# Script de mise à jour de la version Dremio : 24.0 → 26.0
# Date: 16 octobre 2025

Write-Host "=== MISE À JOUR VERSION DREMIO 24.0 → 26.0 ===" -ForegroundColor Cyan

$files = @(
    # French files
    "docs\i18n\fr\architecture\components.md",
    "docs\i18n\fr\architecture\deployment.md",
    "docs\i18n\fr\getting-started\installation.md",
    "docs\i18n\fr\getting-started\configuration.md",
    "docs\i18n\fr\api\dremio-api.md",
    "docs\i18n\fr\TRANSLATION_COMPLETE.md",
    "docs\i18n\fr\VERIFICATION_COMPLETE.md",
    
    # English files
    "docs\i18n\en\architecture\components.md",
    "docs\i18n\en\architecture\deployment.md",
    "docs\i18n\en\getting-started\installation.md",
    "docs\i18n\en\getting-started\configuration.md",
    "docs\i18n\en\api\dremio-api.md"
)

$replacements = @{
    'Version**: 24.0' = 'Version**: 26.0';
    'DREMIO_VERSION=24.0' = 'DREMIO_VERSION=26.0';
    'dremio/dremio-oss:24.0' = 'dremio/dremio-oss:26.0';
    'Dremio | 24.0 |' = 'Dremio | 26.0 |';
    'Dremio 24.0+' = 'Dremio 26.0+';
    'dremio-jdbc-driver-24.0.0.jar' = 'dremio-jdbc-driver-26.0.0.jar';
    '<version>24.0.0</version>' = '<version>26.0.0</version>';
    'v24.0' = 'v26.0';
    '0.50.33, 24.0, 1.10+' = '0.50.33, 26.0, 1.10+';
    '**Dremio** v24.0' = '**Dremio** v26.0'
}

$totalChanges = 0

foreach ($file in $files) {
    $fullPath = Join-Path $PSScriptRoot $file
    
    if (Test-Path $fullPath) {
        Write-Host "`nTraitement: $file" -ForegroundColor Yellow
        $content = Get-Content $fullPath -Raw
        $originalContent = $content
        $fileChanges = 0
        
        foreach ($old in $replacements.Keys) {
            $new = $replacements[$old]
            $matches = ([regex]::Matches($content, [regex]::Escape($old))).Count
            
            if ($matches -gt 0) {
                $content = $content -replace [regex]::Escape($old), $new
                Write-Host "  ✓ Remplacé '$old' → '$new' ($matches occurrence(s))" -ForegroundColor Green
                $fileChanges += $matches
            }
        }
        
        if ($content -ne $originalContent) {
            Set-Content -Path $fullPath -Value $content -NoNewline
            Write-Host "  → $fileChanges changement(s) effectué(s)" -ForegroundColor Cyan
            $totalChanges += $fileChanges
        } else {
            Write-Host "  → Aucun changement nécessaire" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠ Fichier non trouvé: $fullPath" -ForegroundColor Red
    }
}

Write-Host "`n=== RÉSUMÉ ===" -ForegroundColor Cyan
Write-Host "Total de changements: $totalChanges" -ForegroundColor Green
Write-Host "Version Dremio: 24.0 → 26.0 OSS" -ForegroundColor Green
Write-Host "`n✓ Mise à jour terminée!" -ForegroundColor Green
