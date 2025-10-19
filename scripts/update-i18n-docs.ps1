# ============================================================================
# Script de Mise à Jour Documentation Multilingue
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

# Liste des langues supportées
$languages = @(
    @{Code="ar"; Name="العربية"; Dir="docs/i18n/ar"},
    @{Code="cn"; Name="中文"; Dir="docs/i18n/cn"},
    @{Code="de"; Name="Deutsch"; Dir="docs/i18n/de"},
    @{Code="es"; Name="Español"; Dir="docs/i18n/es"},
    @{Code="fr"; Name="Français"; Dir="docs/i18n/fr"},
    @{Code="hi"; Name="हिन्दी"; Dir="docs/i18n/hi"},
    @{Code="id"; Name="Indonesia"; Dir="docs/i18n/id"},
    @{Code="it"; Name="Italiano"; Dir="docs/i18n/it"},
    @{Code="jp"; Name="日本語"; Dir="docs/i18n/jp"},
    @{Code="ko"; Name="한국어"; Dir="docs/i18n/ko"},
    @{Code="nl"; Name="Nederlands"; Dir="docs/i18n/nl"},
    @{Code="pl"; Name="Polski"; Dir="docs/i18n/pl"},
    @{Code="pt"; Name="Português"; Dir="docs/i18n/pt"},
    @{Code="ru"; Name="Русский"; Dir="docs/i18n/ru"},
    @{Code="se"; Name="Svenska"; Dir="docs/i18n/se"},
    @{Code="tr"; Name="Türkçe"; Dir="docs/i18n/tr"},
    @{Code="vi"; Name="Tiếng Việt"; Dir="docs/i18n/vi"}
)

$updatedFiles = 0
$skippedFiles = 0
$errorFiles = 0

foreach ($lang in $languages) {
    $readmePath = Join-Path $lang.Dir "README.md"
    
    if (-not (Test-Path $readmePath)) {
        Write-Host "  [SKIP] $($lang.Name) - Fichier non trouve" -ForegroundColor Yellow
        $skippedFiles++
        continue
    }
    
    try {
        $content = Get-Content $readmePath -Raw -Encoding UTF8
        $originalContent = $content
        
        # Patterns à remplacer selon la langue
        $versionPatterns = @(
            @{Old='**Version**: 3.2.5'; New="**Version**: $NewVersion"},
            @{Old='**Versione**: 3.2.5'; New="**Versione**: $NewVersion"},  # Italien
            @{Old='**版本**: 3.2.5'; New="**版本**: $NewVersion"},              # Chinois
            @{Old='**バージョン**: 3.2.5'; New="**バージョン**: $NewVersion"},   # Japonais
            @{Old='**버전**: 3.2.5'; New="**버전**: $NewVersion"},              # Coréen
            @{Old='**Версия**: 3.2.5'; New="**Версия**: $NewVersion"}        # Russe
        )
        
        # Remplacer les versions
        foreach ($pattern in $versionPatterns) {
            $content = $content -replace [regex]::Escape($pattern.Old), $pattern.New
        }
        
        # Remplacer toutes les occurrences de 3.2.5 par la nouvelle version
        $content = $content -replace '3\.2\.5', $NewVersion
        
        # Mettre à jour la date (formats variés)
        $datePatterns = @(
            '2025-10-15',
            '15 octobre 2025',
            '15 de octubre de 2025',
            '15. Oktober 2025',
            '15 ottobre 2025',
            '2025年10月15日',
            '15 października 2025',
            '15 de outubro de 2025',
            '15 октября 2025',
            '15 oktober 2025'
        )
        
        foreach ($datePattern in $datePatterns) {
            $content = $content -replace [regex]::Escape($datePattern), $UpdateDate
        }
        
        # Vérifier si des changements ont été faits
        if ($content -ne $originalContent) {
            if (-not $DryRun) {
                Set-Content -Path $readmePath -Value $content -Encoding UTF8
                Write-Host "  [UPD] $($lang.Name) - Mis a jour" -ForegroundColor Green
            } else {
                Write-Host "  [DRY] $($lang.Name) - Serait mis a jour" -ForegroundColor Cyan
            }
            $updatedFiles++
        } else {
            Write-Host "  [OK]  $($lang.Name) - Deja a jour" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  [ERR] $($lang.Name) - Erreur: $($_.Exception.Message)" -ForegroundColor Red
        $errorFiles++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUME" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Fichiers mis a jour: $updatedFiles" -ForegroundColor Green
Write-Host "Fichiers ignores:    $skippedFiles" -ForegroundColor Yellow
Write-Host "Erreurs:             $errorFiles" -ForegroundColor Red
Write-Host "Total langues:       $($languages.Count)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`nMode DRY RUN - Executez sans -DryRun pour appliquer" -ForegroundColor Magenta
} else {
    Write-Host "`nMise a jour terminee!" -ForegroundColor Green
}

Write-Host ""

# Créer un rapport de changelog multilingue
if (-not $DryRun -and $updatedFiles -gt 0) {
    $changelogContent = @"
# Documentation Multilingue - Mise à Jour v$NewVersion

**Date:** $UpdateDate  
**Fichiers mis à jour:** $updatedFiles / $($languages.Count)

## Changements

### Version
- **Ancienne:** 3.2.5
- **Nouvelle:** $NewVersion

### Date
- **Ancienne:** 2025-10-15 (et variantes)
- **Nouvelle:** $UpdateDate

## Langues Mises à Jour

"@

    foreach ($lang in $languages) {
        $readmePath = Join-Path $lang.Dir "README.md"
        if (Test-Path $readmePath) {
            $changelogContent += "- ✅ $($lang.Name) ($($lang.Code))`n"
        }
    }

    $changelogContent += @"

## Notes

- Toutes les occurrences de version 3.2.5 ont été remplacées par $NewVersion
- Les dates ont été mises à jour vers $UpdateDate
- Les formats de date localisés ont été préservés

## Vérification

Pour vérifier la mise à jour:
``````powershell
Get-ChildItem -Path docs/i18n/*/README.md -Recurse | Select-String -Pattern "$NewVersion"
``````

---

**Script:** scripts/update-i18n-docs.ps1  
**Exécuté:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

    $changelogPath = "docs/i18n/CHANGELOG_v$($NewVersion).md"
    Set-Content -Path $changelogPath -Value $changelogContent -Encoding UTF8
    Write-Host "Changelog cree: $changelogPath`n" -ForegroundColor Cyan
}

exit $(if ($errorFiles -gt 0) {1} else {0})
