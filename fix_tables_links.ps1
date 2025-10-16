# Correction finale des tableaux avec liens English

$files = @("fr", "es", "pt", "cn", "jp", "ru", "ar")

Write-Host "`n=== CORRECTION DES TABLEAUX ===" -ForegroundColor Cyan

foreach ($lang in $files) {
    $readmePath = "docs\i18n\$lang\README.md"
    
    if (Test-Path $readmePath) {
        $content = Get-Content $readmePath -Raw -Encoding UTF8
        
        # Corriger le tableau avec lien vers ../en/
        $newContent = $content -replace '\| English \| EN \| \[docs/i18n/en/\]\(\.\./en/README\.md\) \|', '| English | EN | [README.md](../../../README.md) |'
        
        if ($content -ne $newContent) {
            Set-Content $readmePath $newContent -Encoding UTF8 -NoNewline
            Write-Host "Fixed table in: $lang" -ForegroundColor Green
        } else {
            Write-Host "No table found in: $lang" -ForegroundColor Gray
        }
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
