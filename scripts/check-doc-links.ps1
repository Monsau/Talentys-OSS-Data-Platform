# ============================================================================
# Script de Vérification des Liens Documentation
# Version: 1.0.0
# Date: 19 Octobre 2025
# ============================================================================

param(
    [switch]$Fix,
    [switch]$Verbose
)

Write-Host "`n[Verification des Liens Documentation]" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$brokenLinks = @()
$validLinks = @()
$fixedLinks = @()

# Fichiers à vérifier
$docsToCheck = @(
    "README.md",
    "RELEASE_NOTES_v3.3.0.md",
    "CHAT_UI_FIX_RESOLUTION.md",
    "DOCUMENTATION_UPDATE.md",
    "DEPLOIEMENT_COMPLET.md",
    "DOCUMENTATION_INDEX.md",
    "CHANGELOG.md"
)

foreach ($docFile in $docsToCheck) {
    if (-not (Test-Path $docFile)) {
        Write-Host "⏭️  Ignoré: $docFile (fichier non trouvé)" -ForegroundColor Gray
        continue
    }
    
    Write-Host "`n📄 Analyse: $docFile" -ForegroundColor Yellow
    
    $content = Get-Content $docFile -Raw -Encoding UTF8
    
    # Pattern pour les liens Markdown vers fichiers locaux
    # [text](path.md) ou [text](path/to/file.md)
    $pattern = '\[([^\]]+)\]\(([^)]+\.md(?:#[^\)]*)?)\)'
    $matches = [regex]::Matches($content, $pattern)
    
    if ($matches.Count -eq 0) {
        Write-Host "   ℹ️  Aucun lien .md trouvé" -ForegroundColor Gray
        continue
    }
    
    foreach ($match in $matches) {
        $linkText = $match.Groups[1].Value
        $linkPath = $match.Groups[2].Value
        
        # Extraire le chemin sans l'ancre
        $pathOnly = $linkPath -replace '#.*$', ''
        
        # Skip si lien externe (http/https)
        if ($pathOnly -match '^https?://') {
            continue
        }
        
        # Résoudre le chemin relatif
        $baseDir = Split-Path -Parent (Resolve-Path $docFile)
        
        # Si le chemin commence par /, c'est relatif à la racine
        if ($pathOnly.StartsWith('/')) {
            $fullPath = Join-Path (Get-Location) $pathOnly.TrimStart('/')
        } else {
            $fullPath = Join-Path $baseDir $pathOnly
        }
        
        # Normaliser le chemin
        try {
            $fullPath = [System.IO.Path]::GetFullPath($fullPath)
        } catch {
            Write-Host "   ❌ [$linkText]($linkPath)" -ForegroundColor Red
            Write-Host "      Erreur: Chemin malformé" -ForegroundColor Red
            $brokenLinks += @{
                File = $docFile
                Text = $linkText
                Path = $linkPath
                Reason = "Malformed path"
            }
            continue
        }
        
        # Vérifier si le fichier existe
        if (Test-Path $fullPath) {
            $validLinks += @{
                File = $docFile
                Text = $linkText
                Path = $linkPath
            }
            if ($Verbose) {
                Write-Host "   ✅ [$linkText]($linkPath)" -ForegroundColor Green
            }
        } else {
            Write-Host "   ❌ [$linkText]($linkPath)" -ForegroundColor Red
            Write-Host "      Attendu: $fullPath" -ForegroundColor Gray
            
            $brokenLinks += @{
                File = $docFile
                Text = $linkText
                Path = $linkPath
                Expected = $fullPath
                Reason = "File not found"
            }
        }
    }
}

# ============================================================================
# RÉSUMÉ
# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   RESUME" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[OK] Liens valides:  $($validLinks.Count)" -ForegroundColor Green
Write-Host "[KO] Liens casses:   $($brokenLinks.Count)" -ForegroundColor Red

if ($brokenLinks.Count -gt 0) {
    Write-Host "`nDetails des Liens Casses:" -ForegroundColor Yellow
    Write-Host "========================================`n" -ForegroundColor Yellow
    
    $brokenLinks | ForEach-Object {
        Write-Host "   Fichier: $($_.File)" -ForegroundColor White
        Write-Host "   Lien:    [$($_.Text)]($($_.Path))" -ForegroundColor Red
        Write-Host "   Raison:  $($_.Reason)" -ForegroundColor Gray
        if ($_.Expected) {
            Write-Host "   Attendu: $($_.Expected)" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    if (-not $Fix) {
        Write-Host "Conseil: Utilisez -Fix pour proposer des corrections automatiques`n" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nTous les liens sont valides!`n" -ForegroundColor Green
}

# ============================================================================
# MODE FIX
# ============================================================================

if ($Fix -and $brokenLinks.Count -gt 0) {
    Write-Host "[MODE CORRECTION ACTIVE]" -ForegroundColor Magenta
    Write-Host "========================================`n" -ForegroundColor Magenta
    
    # Grouper par fichier
    $byFile = $brokenLinks | Group-Object -Property File
    
    foreach ($group in $byFile) {
        $file = $group.Name
        Write-Host "📝 Fichier: $file" -ForegroundColor Yellow
        
        $content = Get-Content $file -Raw -Encoding UTF8
        $modified = $false
        
        foreach ($link in $group.Group) {
            # Proposer des corrections
            $suggestions = @()
            
            # Chercher des fichiers similaires
            $fileName = [System.IO.Path]::GetFileName($link.Path)
            $similarFiles = Get-ChildItem -Recurse -Filter $fileName -ErrorAction SilentlyContinue
            
            if ($similarFiles) {
                foreach ($similar in $similarFiles) {
                    $relativePath = Resolve-Path -Relative $similar.FullName
                    $suggestions += $relativePath
                }
            }
            
            if ($suggestions.Count -gt 0) {
                Write-Host "   Suggestions pour [$($link.Text)]($($link.Path)):" -ForegroundColor Cyan
                for ($i = 0; $i -lt $suggestions.Count; $i++) {
                    Write-Host "      $($i+1). $($suggestions[$i])" -ForegroundColor Gray
                }
                
                # Auto-fix si une seule suggestion
                if ($suggestions.Count -eq 1) {
                    $newPath = $suggestions[0] -replace '\\', '/'
                    $oldLink = "[$($link.Text)]($($link.Path))"
                    $newLink = "[$($link.Text)]($newPath)"
                    
                    $content = $content -replace [regex]::Escape($oldLink), $newLink
                    $modified = $true
                    $fixedLinks += @{
                        File = $file
                        Old = $oldLink
                        New = $newLink
                    }
                    Write-Host "      [OK] Correction appliquee: $newPath" -ForegroundColor Green
                }
            } else {
                Write-Host "   [WARN] Aucune suggestion trouvee pour: $($link.Path)" -ForegroundColor Yellow
            }
        }
        
        if ($modified) {
            Set-Content -Path $file -Value $content -Encoding UTF8
            Write-Host "   [SAVE] Fichier sauvegarde`n" -ForegroundColor Green
        }
    }
    
    if ($fixedLinks.Count -gt 0) {
        Write-Host "`n[SUCCESS] $($fixedLinks.Count) liens corriges!" -ForegroundColor Green
    }
}

# ============================================================================
# EXIT CODE
# ============================================================================

if ($brokenLinks.Count -gt 0) {
    exit 1
} else {
    exit 0
}
