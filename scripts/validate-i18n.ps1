# ============================================================================# ============================================================================

# Script de Validation Documentation Multilingue# Script de Validation Documentation Multilingue

# Version: 1.0.0# Version: 1.0.0

# Date: 19 Octobre 2025# Date: 19 Octobre 2025

# ============================================================================# ============================================================================



Write-Host "`n========================================" -ForegroundColor CyanWrite-Host "`n========================================" -ForegroundColor Cyan

Write-Host "  VALIDATION DOCUMENTATION MULTILINGUE" -ForegroundColor CyanWrite-Host "  VALIDATION DOCUMENTATION MULTILINGUE" -ForegroundColor Cyan

Write-Host "========================================`n" -ForegroundColor CyanWrite-Host "========================================`n" -ForegroundColor Cyan



$targetVersion = "3.3.1"$targetVersion = "3.3.1"

$targetDate = "2025-10-19"$targetDate = "2025-10-19"

$expectedLanguages = 17$expectedLanguages = 17



Write-Host "Verification version: $targetVersion" -ForegroundColor YellowWrite-Host "Verification version: $targetVersion" -ForegroundColor Yellow

Write-Host "Verification date: $targetDate" -ForegroundColor YellowWrite-Host "Verification date: $targetDate" -ForegroundColor Yellow

Write-Host "Langues attendues: $expectedLanguages`n" -ForegroundColor YellowWrite-Host "Langues attendues: $expectedLanguages`n" -ForegroundColor Yellow



# Compter les fichiers# Compter les fichiers

$readmeFiles = Get-ChildItem -Path "docs/i18n/*/README.md"$readmeFiles = Get-ChildItem -Path "docs/i18n/*/README.md"

$fileCount = $readmeFiles.Count$fileCount = $readmeFiles.Count



Write-Host "TEST 1: Nombre de fichiers" -ForegroundColor CyanWrite-Host "TEST 1: Nombre de fichiers" -ForegroundColor Cyan

if ($fileCount -eq $expectedLanguages) {if ($fileCount -eq $expectedLanguages) {

    Write-Host "  [OK] $fileCount fichiers trouves" -ForegroundColor Green    Write-Host "  [OK] $fileCount fichiers trouves" -ForegroundColor Green

} else {} else {

    Write-Host "  [FAIL] $fileCount fichiers trouves (attendu: $expectedLanguages)" -ForegroundColor Red    Write-Host "  [FAIL] $fileCount fichiers trouves (attendu: $expectedLanguages)" -ForegroundColor Red

}}



# Verifier les versions# Verifier les versions

Write-Host "`nTEST 2: Versions" -ForegroundColor CyanWrite-Host "`nTEST 2: Versions" -ForegroundColor Cyan

$versionMatches = $readmeFiles | Select-String -Pattern $targetVersion$versionMatches = $readmeFiles | Select-String -Pattern $targetVersion

$versionCount = ($versionMatches | Select-Object -Unique Path).Count$versionCount = ($versionMatches | Select-Object -Unique Path).Count



if ($versionCount -eq $expectedLanguages) {if ($versionCount -eq $expectedLanguages) {

    Write-Host "  [OK] $versionCount/$expectedLanguages fichiers avec version $targetVersion" -ForegroundColor Green    Write-Host "  [OK] $versionCount/$expectedLanguages fichiers avec version $targetVersion" -ForegroundColor Green

} else {} else {

    Write-Host "  [FAIL] $versionCount/$expectedLanguages fichiers avec version $targetVersion" -ForegroundColor Red    Write-Host "  [FAIL] $versionCount/$expectedLanguages fichiers avec version $targetVersion" -ForegroundColor Red

}    $missingVersion = $readmeFiles | Where-Object {

        (Select-String -Path $_ -Pattern $targetVersion) -eq $null

# Verifier les dates    }

Write-Host "`nTEST 3: Dates" -ForegroundColor Cyan    foreach ($file in $missingVersion) {

$dateMatches = $readmeFiles | Select-String -Pattern $targetDate        Write-Host "    - Manquant: $($file.Directory.Name)" -ForegroundColor Yellow

$dateCount = ($dateMatches | Select-Object -Unique Path).Count    }

}

if ($dateCount -eq $expectedLanguages) {

    Write-Host "  [OK] $dateCount/$expectedLanguages fichiers avec date $targetDate" -ForegroundColor Green# Verifier les dates

} else {Write-Host "`nTEST 3: Dates" -ForegroundColor Cyan

    Write-Host "  [FAIL] $dateCount/$expectedLanguages fichiers avec date $targetDate" -ForegroundColor Red$dateMatches = $readmeFiles | Select-String -Pattern $targetDate

}$dateCount = ($dateMatches | Select-Object -Unique Path).Count



# Verifier les anciennes versionsif ($dateCount -eq $expectedLanguages) {

Write-Host "`nTEST 4: Anciennes versions" -ForegroundColor Cyan    Write-Host "  [OK] $dateCount/$expectedLanguages fichiers avec date $targetDate" -ForegroundColor Green

$oldVersionMatches = $readmeFiles | Select-String -Pattern "3\.2\.5"} else {

$oldVersionCount = ($oldVersionMatches | Select-Object -Unique Path).Count    Write-Host "  [FAIL] $dateCount/$expectedLanguages fichiers avec date $targetDate" -ForegroundColor Red

}

if ($oldVersionCount -eq 0) {

    Write-Host "  [OK] Aucune version 3.2.5 trouvee" -ForegroundColor Green# Verifier les anciennes versions

} else {Write-Host "`nTEST 4: Anciennes versions" -ForegroundColor Cyan

    Write-Host "  [WARN] $oldVersionCount fichiers contiennent encore 3.2.5" -ForegroundColor Yellow$oldVersionMatches = $readmeFiles | Select-String -Pattern "3\.2\.5"

}$oldVersionCount = ($oldVersionMatches | Select-Object -Unique Path).Count



# Verifier les anciennes datesif ($oldVersionCount -eq 0) {

Write-Host "`nTEST 5: Anciennes dates" -ForegroundColor Cyan    Write-Host "  [OK] Aucune version 3.2.5 trouvee" -ForegroundColor Green

$oldDateMatches = $readmeFiles | Select-String -Pattern "2025-10-15"} else {

$oldDateCount = ($oldDateMatches | Select-Object -Unique Path).Count    Write-Host "  [WARN] $oldVersionCount fichiers contiennent encore 3.2.5" -ForegroundColor Yellow

    foreach ($match in ($oldVersionMatches | Select-Object -Unique Path)) {

if ($oldDateCount -eq 0) {        $lang = Split-Path (Split-Path $match.Path -Parent) -Leaf

    Write-Host "  [OK] Aucune date 2025-10-15 trouvee" -ForegroundColor Green        Write-Host "    - $lang" -ForegroundColor Yellow

} else {    }

    Write-Host "  [WARN] $oldDateCount fichiers contiennent encore 2025-10-15" -ForegroundColor Yellow}

}

# Verifier les anciennes dates

# Verifier l'encodage UTF-8Write-Host "`nTEST 5: Anciennes dates" -ForegroundColor Cyan

Write-Host "`nTEST 6: Encodage UTF-8" -ForegroundColor Cyan$oldDateMatches = $readmeFiles | Select-String -Pattern "2025-10-15"

$encodingIssues = 0$oldDateCount = ($oldDateMatches | Select-Object -Unique Path).Count

foreach ($file in $readmeFiles) {

    try {if ($oldDateCount -eq 0) {

        $null = Get-Content $file -Raw -Encoding UTF8    Write-Host "  [OK] Aucune date 2025-10-15 trouvee" -ForegroundColor Green

    }} else {

    catch {    Write-Host "  [WARN] $oldDateCount fichiers contiennent encore 2025-10-15" -ForegroundColor Yellow

        $lang = Split-Path (Split-Path $file.FullName -Parent) -Leaf}

        Write-Host "  [ERR] $lang - Erreur encodage" -ForegroundColor Red

        $encodingIssues++# Verifier l'encodage UTF-8

    }Write-Host "`nTEST 6: Encodage UTF-8" -ForegroundColor Cyan

}$encodingIssues = 0

foreach ($file in $readmeFiles) {

if ($encodingIssues -eq 0) {    try {

    Write-Host "  [OK] Encodage UTF-8 valide pour toutes les langues" -ForegroundColor Green        $content = Get-Content $file -Raw -Encoding UTF8

} else {        # Verifier la presence de caracteres speciaux selon la langue

    Write-Host "  [WARN] $encodingIssues problemes d'encodage detectes" -ForegroundColor Yellow        $lang = Split-Path (Split-Path $file.FullName -Parent) -Leaf

}        

        $specialChars = @{

# Statistiques par langue            "ar" = "العربية"

Write-Host "`n========================================" -ForegroundColor Cyan            "cn" = "中文"

Write-Host "  DETAILS PAR LANGUE" -ForegroundColor Cyan            "jp" = "日本語"

Write-Host "========================================`n" -ForegroundColor Cyan            "ko" = "한국어"

            "ru" = "Русский"

$langNames = @{            "hi" = "हिन्दी"

    "ar" = "Arabe"        }

    "cn" = "Chinois"        

    "de" = "Allemand"        if ($specialChars.ContainsKey($lang)) {

    "es" = "Espagnol"            if ($content -notmatch [regex]::Escape($specialChars[$lang])) {

    "fr" = "Francais"                Write-Host "  [WARN] $lang - Caracteres speciaux manquants" -ForegroundColor Yellow

    "hi" = "Hindi"                $encodingIssues++

    "id" = "Indonesien"            }

    "it" = "Italien"        }

    "jp" = "Japonais"    }

    "ko" = "Coreen"    catch {

    "nl" = "Neerlandais"        Write-Host "  [ERR] $lang - Erreur encodage: $($_.Exception.Message)" -ForegroundColor Red

    "pl" = "Polonais"        $encodingIssues++

    "pt" = "Portugais"    }

    "ru" = "Russe"}

    "se" = "Suedois"

    "tr" = "Turc"if ($encodingIssues -eq 0) {

    "vi" = "Vietnamien"    Write-Host "  [OK] Encodage UTF-8 valide pour toutes les langues" -ForegroundColor Green

}} else {

    Write-Host "  [WARN] $encodingIssues problemes d'encodage detectes" -ForegroundColor Yellow

foreach ($file in $readmeFiles | Sort-Object) {}

    $lang = Split-Path (Split-Path $file.FullName -Parent) -Leaf

    $langName = $langNames[$lang]# Statistiques par langue

    $content = Get-Content $file -Raw -Encoding UTF8Write-Host "`n========================================" -ForegroundColor Cyan

    Write-Host "  DETAILS PAR LANGUE" -ForegroundColor Cyan

    $hasVersion = $content -match $targetVersionWrite-Host "========================================`n" -ForegroundColor Cyan

    $hasDate = $content -match $targetDate

    $langNames = @{

    $status = if ($hasVersion -and $hasDate) { "[OK]" } else { "[!!]" }    "ar" = "Arabe"

    $color = if ($hasVersion -and $hasDate) { "Green" } else { "Red" }    "cn" = "Chinois"

        "de" = "Allemand"

    $line = "  $status $lang ($langName)"    "es" = "Espagnol"

    if (-not $hasVersion) { $line += " - VERSION MANQUANTE" }    "fr" = "Francais"

    if (-not $hasDate) { $line += " - DATE MANQUANTE" }    "hi" = "Hindi"

        "id" = "Indonesien"

    Write-Host $line -ForegroundColor $color    "it" = "Italien"

}    "jp" = "Japonais"

    "ko" = "Coreen"

# Resume final    "nl" = "Neerlandais"

Write-Host "`n========================================" -ForegroundColor Cyan    "pl" = "Polonais"

Write-Host "  RESUME FINAL" -ForegroundColor Cyan    "pt" = "Portugais"

Write-Host "========================================`n" -ForegroundColor Cyan    "ru" = "Russe"

    "se" = "Suedois"

$allTestsPassed = (    "tr" = "Turc"

    $fileCount -eq $expectedLanguages -and    "vi" = "Vietnamien"

    $versionCount -eq $expectedLanguages -and}

    $dateCount -eq $expectedLanguages -and

    $oldVersionCount -eq 0 -andforeach ($file in $readmeFiles | Sort-Object) {

    $oldDateCount -eq 0 -and    $lang = Split-Path (Split-Path $file.FullName -Parent) -Leaf

    $encodingIssues -eq 0    $langName = $langNames[$lang]

)    $content = Get-Content $file -Raw -Encoding UTF8

    

if ($allTestsPassed) {    $hasVersion = $content -match $targetVersion

    Write-Host "STATUT: TOUS LES TESTS PASSES" -ForegroundColor Green    $hasDate = $content -match $targetDate

    Write-Host "`nLa documentation multilingue est a jour et valide!`n" -ForegroundColor Green    

    exit 0    $status = if ($hasVersion -and $hasDate) { "[OK]" } else { "[!!]" }

} else {    $color = if ($hasVersion -and $hasDate) { "Green" } else { "Red" }

    Write-Host "STATUT: CERTAINS TESTS ONT ECHOUE" -ForegroundColor Red    

    Write-Host "`nVerifiez les problemes ci-dessus.`n" -ForegroundColor Yellow    Write-Host "  $status $lang ($langName)" -ForegroundColor $color -NoNewline

    exit 1    

}    if (-not $hasVersion) { Write-Host " - VERSION MANQUANTE" -ForegroundColor Red -NoNewline }

    if (-not $hasDate) { Write-Host " - DATE MANQUANTE" -ForegroundColor Red -NoNewline }
    
    Write-Host ""
}

# Resume final
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUME FINAL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allTestsPassed = (
    $fileCount -eq $expectedLanguages -and
    $versionCount -eq $expectedLanguages -and
    $dateCount -eq $expectedLanguages -and
    $oldVersionCount -eq 0 -and
    $oldDateCount -eq 0 -and
    $encodingIssues -eq 0
)

if ($allTestsPassed) {
    Write-Host "STATUT: " -NoNewline
    Write-Host "TOUS LES TESTS PASSES" -ForegroundColor Green
    Write-Host "`nLa documentation multilingue est a jour et valide!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "STATUT: " -NoNewline
    Write-Host "CERTAINS TESTS ONT ECHOUE" -ForegroundColor Red
    Write-Host "`nVerifiez les problemes ci-dessus.`n" -ForegroundColor Yellow
    exit 1
}
