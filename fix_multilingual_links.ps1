# Script de correction des liens multilingues
# Corrige tous les liens "English" pour pointer vers README.md racine

$languages = @("fr", "es", "pt", "cn", "jp", "ru", "ar", "de", "ko", "hi", "id", "tr", "vi", "it", "nl", "pl", "se")

Write-Host "`n=== CORRECTION DES LIENS MULTILINGUES ===" -ForegroundColor Cyan

$corrected = 0

foreach ($lang in $languages) {
    $readmePath = "docs\i18n\$lang\README.md"
    
    if (Test-Path $readmePath) {
        $content = Get-Content $readmePath -Raw -Encoding UTF8
        
        # Corrections
        $newContent = $content -replace '\[English\]\(\.\./en/README\.md\)', '[English](../../../README.md)'
        $newContent = $newContent -replace '\*\*\[English\]\(\.\./en/README\.md\)\*\*', '**[English](../../../README.md)**'
        $newContent = $newContent -replace 'Version.*:.*3\.1\.0', 'Version**: 3.2.5'
        $newContent = $newContent -replace '**Version**: 3\.1\.0', '**Version**: 3.2.5'
        
        if ($content -ne $newContent) {
            Set-Content $readmePath $newContent -Encoding UTF8 -NoNewline
            Write-Host "Corrected: $lang/README.md" -ForegroundColor Green
            $corrected++
        }
    }
}

Write-Host "`nFiles corrected: $corrected" -ForegroundColor Green
Write-Host "Done!" -ForegroundColor Cyan

