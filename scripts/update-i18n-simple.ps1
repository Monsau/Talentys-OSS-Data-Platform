# ============================================================================
# Script de Mise a Jour Documentation Multilingue
# Version: 1.0.0
# Date: 19 Octobre 2025
# ============================================================================

param(
    [string]$NewVersion = "3.3.1",
    [string]$UpdateDate = "2025-10-19",
    [switch]$DryRun
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MISE A JOUR DOCUMENTATION MULTILINGUE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Version cible: $NewVersion" -ForegroundColor Yellow
Write-Host "Date: $UpdateDate" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "Mode: DRY RUN (aucune modification)`n" -ForegroundColor Magenta
} else {
    Write-Host "Mode: PRODUCTION (modifications appliquees)`n" -ForegroundColor Green
}

# Liste des repertoires de langues
$langDirs = @(
    "docs/i18n/ar",
    "docs/i18n/cn",
    "docs/i18n/de",
    "docs/i18n/es",
    "docs/i18n/fr",
    "docs/i18n/hi",
    "docs/i18n/id",
    "docs/i18n/it",
    "docs/i18n/jp",
    "docs/i18n/ko",
    "docs/i18n/nl",
    "docs/i18n/pl",
    "docs/i18n/pt",
    "docs/i18n/ru",
    "docs/i18n/se",
    "docs/i18n/tr",
    "docs/i18n/vi"
)

$updatedFiles = 0
$skippedFiles = 0
$errorFiles = 0

foreach ($langDir in $langDirs) {
    $readmePath = Join-Path $langDir "README.md"
    $langCode = Split-Path $langDir -Leaf
    
    if (-not (Test-Path $readmePath)) {
        Write-Host "  [SKIP] $langCode - Fichier non trouve" -ForegroundColor Yellow
        $skippedFiles++
        continue
    }
    
    try {
        $content = Get-Content $readmePath -Raw -Encoding UTF8
        $originalContent = $content
        
        # Remplacer toutes les versions 3.2.5
        $content = $content -replace '3\.2\.5', $NewVersion
        
        # Remplacer les dates communes
        $content = $content -replace '2025-10-15', $UpdateDate
        $content = $content -replace '15 octobre 2025', '19 octobre 2025'
        $content = $content -replace 'October 15, 2025', 'October 19, 2025'
        $content = $content -replace '15 de octubre de 2025', '19 de octubre de 2025'
        $content = $content -replace '15\. Oktober 2025', '19. Oktober 2025'
        $content = $content -replace '15 ottobre 2025', '19 ottobre 2025'
        $content = $content -replace '15 de outubro de 2025', '19 de outubro de 2025'
        
        # Verifier si des changements ont ete faits
        if ($content -ne $originalContent) {
            if (-not $DryRun) {
                Set-Content -Path $readmePath -Value $content -Encoding UTF8
                Write-Host "  [UPD] $langCode - Mis a jour" -ForegroundColor Green
            } else {
                Write-Host "  [DRY] $langCode - Serait mis a jour" -ForegroundColor Cyan
            }
            $updatedFiles++
        } else {
            Write-Host "  [OK]  $langCode - Deja a jour" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  [ERR] $langCode - Erreur: $($_.Exception.Message)" -ForegroundColor Red
        $errorFiles++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUME" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Fichiers mis a jour: $updatedFiles" -ForegroundColor Green
Write-Host "Fichiers ignores:    $skippedFiles" -ForegroundColor Yellow
Write-Host "Erreurs:             $errorFiles" -ForegroundColor Red
Write-Host "Total langues:       $($langDirs.Count)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`nMode DRY RUN - Executez sans -DryRun pour appliquer" -ForegroundColor Magenta
} else {
    Write-Host "`nMise a jour terminee!" -ForegroundColor Green
    
    # Creer un changelog simple
    $changelogContent = @"
# Documentation Multilingue - Mise a Jour v$NewVersion

Date: $UpdateDate
Fichiers mis a jour: $updatedFiles / $($langDirs.Count)

## Changements

Version: 3.2.5 -> $NewVersion
Date: 2025-10-15 -> $UpdateDate

## Langues Mises a Jour

"@

    foreach ($langDir in $langDirs) {
        $langCode = Split-Path $langDir -Leaf
        $readmePath = Join-Path $langDir "README.md"
        if (Test-Path $readmePath) {
            $changelogContent += "- $langCode`n"
        }
    }

    $changelogContent += @"

## Verification

Pour verifier:
Get-ChildItem -Path docs/i18n/*/README.md | Select-String -Pattern "$NewVersion"

Script: scripts/update-i18n-docs.ps1
Execute: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

    $changelogPath = "docs/i18n/UPDATE_LOG_$($NewVersion).md"
    Set-Content -Path $changelogPath -Value $changelogContent -Encoding UTF8
    Write-Host "Log cree: $changelogPath`n" -ForegroundColor Cyan
}

Write-Host ""
exit $(if ($errorFiles -gt 0) {1} else {0})
