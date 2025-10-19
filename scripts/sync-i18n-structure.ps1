# Script de Synchronisation Structure i18n
# Crée la structure de documentation complète pour toutes les langues

$ErrorActionPreference = "Stop"

# Configuration
$SOURCE_LANG = "fr"
$TARGET_LANGS = @("ar", "cn", "de", "es", "hi", "id", "it", "jp", "ko", "nl", "pl", "pt", "ru", "se", "tr", "vi")
$BASE_PATH = "docs\i18n"

# Noms des langues pour les README (ASCII uniquement pour éviter problèmes PowerShell)
$LANG_NAMES = @{
    "ar" = "Arabic"
    "cn" = "Chinese"
    "de" = "German"
    "es" = "Spanish"
    "hi" = "Hindi"
    "id" = "Indonesian"
    "it" = "Italian"
    "jp" = "Japanese"
    "ko" = "Korean"
    "nl" = "Dutch"
    "pl" = "Polish"
    "pt" = "Portuguese"
    "ru" = "Russian"
    "se" = "Swedish"
    "tr" = "Turkish"
    "vi" = "Vietnamese"
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SYNCHRONISATION STRUCTURE i18n" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Récupérer la structure française
Write-Host "Analyse de la structure source (FR)..." -ForegroundColor Cyan
$frFiles = Get-ChildItem -Path "$BASE_PATH\$SOURCE_LANG" -Recurse -File -Name

Write-Host "Fichiers trouvés: $($frFiles.Count)" -ForegroundColor Green
Write-Host "`nFichiers à synchroniser:" -ForegroundColor Cyan
foreach ($file in $frFiles) {
    Write-Host "  - $file" -ForegroundColor White
}

Write-Host "`n----------------------------------------" -ForegroundColor Cyan

# Pour chaque langue cible
foreach ($lang in $TARGET_LANGS) {
    Write-Host "`nTraitement: $lang ($($LANG_NAMES[$lang]))..." -ForegroundColor Yellow
    
    $created = 0
    $skipped = 0
    
    foreach ($file in $frFiles) {
        $targetPath = Join-Path "$BASE_PATH\$lang" $file
        $targetDir = Split-Path $targetPath -Parent
        
        # Créer le dossier si nécessaire
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Vérifier si le fichier existe déjà
        if (Test-Path $targetPath) {
            $skipped++
            continue
        }
        
        # Déterminer le titre basé sur le nom du fichier
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file)
        $title = $fileName -replace '-', ' ' -replace '_', ' '
        $title = (Get-Culture).TextInfo.ToTitleCase($title.ToLower())
        
        # Créer le contenu placeholder (sans here-string pour éviter les problèmes Unicode)
        $langName = $LANG_NAMES[$lang]
        $content = "# $title`n`n"
        $content += "> Language: $langName`n"
        $content += "> Version: 3.3.1`n"
        $content += "> Date: October 19, 2025`n`n"
        $content += "---`n`n"
        $content += "## Documentation In Progress`n`n"
        $content += "This document is currently being translated from the French version.`n`n"
        $content += "For complete documentation, please refer to:`n"
        $content += "- [Main Documentation](../../../README.md)`n"
        $content += "- [French Documentation](../fr/$file)`n`n"
        $content += "---`n`n"
        $content += "## Available Languages`n`n"
        $content += "We support **17 languages**:`n`n"
        $content += "- [Francais (FR)](../fr/)`n"
        $content += "- [English (EN)](../../../README.md)`n"
        $content += "- [Espanol (ES)](../es/)`n"
        $content += "- [Portugues (PT)](../pt/)`n"
        $content += "- [Deutsch (DE)](../de/)`n"
        $content += "- [Svenska (SE)](../se/)`n"
        $content += "- [Nederlands (NL)](../nl/)`n"
        $content += "- [Italiano (IT)](../it/)`n"
        $content += "- [Polski (PL)](../pl/)`n"
        $content += "- [Arabic (AR)](../ar/)`n"
        $content += "- [Chinese (CN)](../cn/)`n"
        $content += "- [Japanese (JP)](../jp/)`n"
        $content += "- [Korean (KO)](../ko/)`n"
        $content += "- [Russian (RU)](../ru/)`n"
        $content += "- [Hindi (HI)](../hi/)`n"
        $content += "- [Turkish (TR)](../tr/)`n"
        $content += "- [Vietnamese (VI)](../vi/)`n"
        $content += "- [Indonesian (ID)](../id/)`n`n"
        $content += "---`n`n"
        $content += "## Contributing`n`n"
        $content += "Help us translate this documentation!`n`n"
        $content += "1. Fork the repository`n"
        $content += "2. Translate the French version: [../fr/$file](../fr/$file)`n"
        $content += "3. Submit a Pull Request`n`n"
        $content += "See our [Contribution Guide](../../../docs/development/README.md) for details.`n`n"
        $content += "---`n`n"
        $content += "**[<- Back to $langName Documentation](../README.md)**`n"
        
        # Écrire le fichier
        Set-Content -Path $targetPath -Value $content -Encoding UTF8
        $created++
        Write-Host "  ✓ Created: $file" -ForegroundColor Green
    }
    
    Write-Host "`n  Résumé $lang : $created créés, $skipped ignorés" -ForegroundColor Cyan
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SYNCHRONISATION TERMINÉE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Statistiques finales
Write-Host "Statistiques:" -ForegroundColor Yellow
Write-Host "  - Langues traitées: $($TARGET_LANGS.Count)" -ForegroundColor White
Write-Host "  - Fichiers source: $($frFiles.Count)" -ForegroundColor White
Write-Host "  - Total potentiel: $($TARGET_LANGS.Count * $frFiles.Count) fichiers" -ForegroundColor White

Write-Host "`nProchaine etape:" -ForegroundColor Cyan
Write-Host "  git add docs/i18n/" -ForegroundColor White
Write-Host "  git commit -m `"docs: Add i18n structure placeholders for 16 languages`"" -ForegroundColor White
