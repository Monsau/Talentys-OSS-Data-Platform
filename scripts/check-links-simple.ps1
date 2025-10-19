# Simple Documentation Links Checker
# Version: 1.0.0

$brokenLinks = @()
$validLinks = 0

$docsToCheck = @(
    "README.md",
    "RELEASE_NOTES_v3.3.0.md", 
    "CHAT_UI_FIX_RESOLUTION.md",
    "DOCUMENTATION_UPDATE.md",
    "DEPLOIEMENT_COMPLET.md",
    "DOCUMENTATION_INDEX.md",
    "CHANGELOG.md"
)

Write-Host "`nVerification des Liens Documentation`n" -ForegroundColor Cyan

foreach ($docFile in $docsToCheck) {
    if (-not (Test-Path $docFile)) {
        continue
    }
    
    Write-Host "Analyse: $docFile" -ForegroundColor Yellow
    
    $content = Get-Content $docFile -Raw -Encoding UTF8
    $pattern = '\[([^\]]+)\]\(([^)]+\.md)\)'
    $matches = [regex]::Matches($content, $pattern)
    
    foreach ($match in $matches) {
        $linkText = $match.Groups[1].Value
        $linkPath = $match.Groups[2].Value
        
        # Skip anchors
        $pathOnly = $linkPath -replace '#.*$', ''
        
        # Skip external links
        if ($pathOnly -match '^https?://') {
            continue
        }
        
        # Build full path
        $baseDir = Split-Path -Parent (Resolve-Path $docFile)
        
        if ($pathOnly.StartsWith('/')) {
            $fullPath = Join-Path (Get-Location) $pathOnly.TrimStart('/')
        } else {
            $fullPath = Join-Path $baseDir $pathOnly
        }
        
        # Check if exists
        if (Test-Path $fullPath) {
            $validLinks++
            Write-Host "  [OK] $linkPath" -ForegroundColor Green
        } else {
            Write-Host "  [KO] $linkPath" -ForegroundColor Red
            Write-Host "       Expected: $fullPath" -ForegroundColor Gray
            $brokenLinks += "$docFile : [$linkText]($linkPath)"
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESUME" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Liens valides:  $validLinks" -ForegroundColor Green
Write-Host "Liens casses:   $($brokenLinks.Count)" -ForegroundColor Red

if ($brokenLinks.Count -gt 0) {
    Write-Host "`nLiens casses trouves:" -ForegroundColor Yellow
    $brokenLinks | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
} else {
    Write-Host "`nTous les liens sont valides!`n" -ForegroundColor Green
    exit 0
}
