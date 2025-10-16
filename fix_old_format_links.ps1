# Script final de correction complète
# Uniformise TOUS les README des traductions

$languages = @("fr", "es", "pt", "cn", "jp", "ru", "ar")

Write-Host "`n=== CORRECTION COMPLETE DES 7 ANCIENS FICHIERS ===" -ForegroundColor Cyan

foreach ($lang in $languages) {
    $readmePath = "docs\i18n\$lang\README.md"
    
    if (Test-Path $readmePath) {
        $content = Get-Content $readmePath -Raw -Encoding UTF8
        
        # Correction du lien English (plusieurs formats possibles)
        $newContent = $content -replace '\[English\]\(README\.md\)', '[English](../../../README.md)'
        $newContent = $newContent -replace '\[English\]\(\.\./en/README\.md\)', '[English](../../../README.md)'
        $newContent = $newContent -replace '\[Anglais\]\(README\.md\)', '[English](../../../README.md)'
        
        # Mise à jour version
        $newContent = $newContent -replace 'Version\s*:\s*3\.1\.0', 'Version: 3.2.5'
        $newContent = $newContent -replace 'Version\s*:\s*3\.2\.0', 'Version: 3.2.5'
        
        if ($content -ne $newContent) {
            Set-Content $readmePath $newContent -Encoding UTF8 -NoNewline
            Write-Host "Corrected: $lang" -ForegroundColor Green
        } else {
            Write-Host "Already OK: $lang" -ForegroundColor Gray
        }
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
