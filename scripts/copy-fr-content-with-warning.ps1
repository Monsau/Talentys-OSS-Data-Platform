# Copie du Contenu Français vers Toutes les Langues
# Cette version copie le contenu FR avec un avertissement au début

$ErrorActionPreference = "Stop"

$SOURCE = "docs\i18n\fr"
$LANGS = @("en", "ar", "cn", "de", "es", "hi", "id", "it", "jp", "ko", "nl", "pl", "pt", "ru", "se", "tr", "vi")

$LANG_NAMES = @{
    "en" = "English"
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

Write-Host "`n========================================"
Write-Host "COPIE CONTENU FR VERS TOUTES LES LANGUES" -ForegroundColor Yellow
Write-Host "========================================`n"

Write-Host "Mode: Copie avec avertissement de traduction automatique" -ForegroundColor Cyan
Write-Host "Le contenu francais sera copie avec un header indiquant" -ForegroundColor Cyan
Write-Host "qu'il necessite une traduction.`n" -ForegroundColor Cyan

$totalCopied = 0
$totalFiles = 0

foreach ($lang in $LANGS) {
    Write-Host "`n[$($lang.ToUpper())] Traitement: $($LANG_NAMES[$lang])..." -ForegroundColor Yellow
    
    $files = Get-ChildItem -Path $SOURCE -Recurse -File -Name | Where-Object { 
        $_ -notmatch "DOCUMENTATION_|MISE_A_JOUR_|RESUME_" -and $_ -match "\.md$"
    }
    
    $totalFiles = $files.Count
    $copied = 0
    
    foreach ($file in $files) {
        $source_file = Join-Path $SOURCE $file
        $target_file = Join-Path "docs\i18n\$lang" $file
        $target_dir = Split-Path $target_file -Parent
        
        if (-not (Test-Path $target_dir)) {
            New-Item -ItemType Directory -Path $target_dir -Force | Out-Null
        }
        
        # Lire le contenu source
        $content = Get-Content -Path $source_file -Raw -Encoding UTF8
        
        # Ajouter un header d'avertissement
        $langName = $LANG_NAMES[$lang]
        $warning = @"
> ⚠️ **Translation Required**
> 
> This document is currently in **French** and needs translation to **$langName**.
> If you speak $langName, please help us translate this content!
> 
> See: [Contribution Guide](../../../docs/development/README.md)

---

"@
        
        # Combiner warning + contenu
        $newContent = $warning + $content
        
        # Écrire le fichier
        Set-Content -Path $target_file -Value $newContent -Encoding UTF8
        
        $copied++
        $totalCopied++
        Write-Host "  + $file" -ForegroundColor Green
    }
    
    Write-Host "  Resume: $copied fichiers copies" -ForegroundColor Cyan
}

Write-Host "`n========================================"
Write-Host "COPIE TERMINEE" -ForegroundColor Green
Write-Host "========================================`n"

Write-Host "Statistiques:" -ForegroundColor Yellow
Write-Host "  - Langues traitees: $($LANGS.Count)"
Write-Host "  - Fichiers par langue: $totalFiles"
Write-Host "  - Total copie: $totalCopied"

Write-Host "`nNote: Tous les fichiers contiennent maintenant le contenu francais" -ForegroundColor Cyan
Write-Host "avec un avertissement indiquant qu'une traduction est necessaire." -ForegroundColor Cyan

Write-Host "`nProchaine etape:" -ForegroundColor Yellow
Write-Host "  git add docs/i18n/"
Write-Host "  git status"
