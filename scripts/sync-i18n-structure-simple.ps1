# Script de Synchronisation Structure i18n - Version Simplifiee
# Cree la structure de documentation complete pour toutes les langues

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Configuration
$SOURCE_LANG = "fr"
$TARGET_LANGS = @("ar", "cn", "de", "es", "hi", "id", "it", "jp", "ko", "nl", "pl", "pt", "ru", "se", "tr", "vi")
$BASE_PATH = "docs\i18n"

$LANG_NAMES = @{
    "ar" = "Arabic"; "cn" = "Chinese"; "de" = "German"; "es" = "Spanish"
    "hi" = "Hindi"; "id" = "Indonesian"; "it" = "Italian"; "jp" = "Japanese"
    "ko" = "Korean"; "nl" = "Dutch"; "pl" = "Polish"; "pt" = "Portuguese"
    "ru" = "Russian"; "se" = "Swedish"; "tr" = "Turkish"; "vi" = "Vietnamese"
}

Write-Host "`n========================================"
Write-Host "SYNCHRONISATION STRUCTURE i18n" -ForegroundColor Yellow
Write-Host "========================================`n"

# Recuperer la structure francaise
Write-Host "Analyse de la structure source (FR)..." -ForegroundColor Cyan
$frFiles = Get-ChildItem -Path "$BASE_PATH\$SOURCE_LANG" -Recurse -File -Name | Where-Object { $_ -notmatch "^(DOCUMENTATION_|MISE_A_JOUR_)" }

Write-Host "Fichiers trouvés: $($frFiles.Count)" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n[DRY RUN MODE - Aucune modification]" -ForegroundColor Yellow
}

Write-Host "`n----------------------------------------"

$totalCreated = 0
$totalSkipped = 0

# Pour chaque langue cible
foreach ($lang in $TARGET_LANGS) {
    Write-Host "`nTraitement: $lang ($($LANG_NAMES[$lang]))..." -ForegroundColor Yellow
    
    $created = 0
    $skipped = 0
    
    foreach ($file in $frFiles) {
        $targetPath = Join-Path "$BASE_PATH\$lang" $file
        $targetDir = Split-Path $targetPath -Parent
        
        # Verifier si le fichier existe deja
        if (Test-Path $targetPath) {
            $skipped++
            continue
        }
        
        if (-not $DryRun) {
            # Creer le dossier si necessaire
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            # Determiner le titre
            $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file)
            $title = $fileName -replace '-', ' ' -replace '_', ' '
            $title = (Get-Culture).TextInfo.ToTitleCase($title.ToLower())
            
            # Creer le contenu placeholder
            $langName = $LANG_NAMES[$lang]
            $lines = @()
            $lines += "# $title"
            $lines += ""
            $lines += "> **Language**: $langName"
            $lines += "> **Version**: 3.3.1  "
            $lines += "> **Date**: October 19, 2025"
            $lines += ""
            $lines += "---"
            $lines += ""
            $lines += "## Documentation In Progress"
            $lines += ""
            $lines += "This document is currently being translated from the French version."
            $lines += ""
            $lines += "For complete documentation, please refer to:"
            $lines += "- [Main Documentation](../../../README.md)"
            $lines += "- [French Documentation](../fr/$file)"
            $lines += ""
            $lines += "---"
            $lines += ""
            $lines += "## Available Languages"
            $lines += ""
            $lines += "We support **17 languages**. See [docs/i18n/](../) for all languages."
            $lines += ""
            $lines += "---"
            $lines += ""
            $lines += "## Contributing"
            $lines += ""
            $lines += "Help us translate this documentation!"
            $lines += ""
            $lines += "1. Fork the repository"
            $lines += "2. Translate from: [../fr/$file](../fr/$file)"
            $lines += "3. Submit a Pull Request"
            $lines += ""
            $lines += "See our [Contribution Guide](../../../docs/development/README.md)."
            $lines += ""
            $lines += "---"
            $lines += ""
            $lines += "**[<- Back to $langName Documentation](../README.md)**"
            
            # Ecrire le fichier
            $lines | Out-File -FilePath $targetPath -Encoding UTF8
        }
        
        $created++
        Write-Host "  + $file" -ForegroundColor Green
    }
    
    $totalCreated += $created
    $totalSkipped += $skipped
    
    Write-Host "  Resume: $created crees, $skipped ignores" -ForegroundColor Cyan
}

Write-Host "`n========================================"
Write-Host "SYNCHRONISATION TERMINEE" -ForegroundColor Green
Write-Host "========================================`n"

Write-Host "Statistiques:" -ForegroundColor Yellow
Write-Host "  - Langues traitees: $($TARGET_LANGS.Count)"
Write-Host "  - Fichiers source: $($frFiles.Count)"
Write-Host "  - Total cree: $totalCreated"
Write-Host "  - Total ignore: $totalSkipped"

if (-not $DryRun) {
    Write-Host "`nProchaine etape:"
    Write-Host "  git add docs/i18n/"
    Write-Host "  git commit -m" -NoNewline
    Write-Host ' "docs: Add i18n structure placeholders for 16 languages"'
}
