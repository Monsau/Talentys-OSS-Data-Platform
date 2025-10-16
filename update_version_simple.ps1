# Mise à jour version Dremio 24.0 → 26.0
Write-Host "Mise à jour Dremio 24.0 vers 26.0..." -ForegroundColor Cyan

$files = Get-ChildItem -Path "docs\i18n" -Recurse -Filter "*.md"
$count = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $newContent = $content
    
    # Remplacements
    $newContent = $newContent -replace 'Version\*\*: 24\.0', 'Version**: 26.0'
    $newContent = $newContent -replace 'DREMIO_VERSION=24\.0', 'DREMIO_VERSION=26.0'
    $newContent = $newContent -replace 'dremio/dremio-oss:24\.0', 'dremio/dremio-oss:26.0'
    $newContent = $newContent -replace 'Dremio \| 24\.0 \|', 'Dremio | 26.0 |'
    $newContent = $newContent -replace 'Dremio 24\.0\+', 'Dremio 26.0+'
    $newContent = $newContent -replace 'dremio-jdbc-driver-24\.0\.0\.jar', 'dremio-jdbc-driver-26.0.0.jar'
    $newContent = $newContent -replace '<version>24\.0\.0</version>', '<version>26.0.0</version>'
    $newContent = $newContent -replace 'v24\.0', 'v26.0'
    $newContent = $newContent -replace '0\.50\.33, 24\.0, 1\.10\+', '0.50.33, 26.0, 1.10+'
    $newContent = $newContent -replace '\*\*Dremio\*\* v24\.0', '**Dremio** v26.0'
    
    if ($content -ne $newContent) {
        Set-Content -Path $file.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "✓ $($file.Name)" -ForegroundColor Green
        $count++
    }
}

Write-Host "`n$count fichier(s) mis à jour" -ForegroundColor Cyan
Write-Host "Version Dremio: 24.0 → 26.0 OSS" -ForegroundColor Green
