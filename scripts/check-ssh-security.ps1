# Script de vérification de sécurité pour clés SSH exposées
# Date : 19 octobre 2025

$CompromisedKey = "AAAAC3NzaC1lZDI1NTE5AAAAIA7wCKDWfHU7GgKd3dhp8nFt6UFrVM7nGz9OJfnV0RRQ"

Write-Host "`n============================================" -ForegroundColor Red
Write-Host "  VERIFICATION SECURITE - CLES SSH EXPOSEES" -ForegroundColor Red
Write-Host "============================================`n" -ForegroundColor Red

# 1. Vérifier que les fichiers locaux sont supprimés
Write-Host "[1/5] Verification suppression fichiers locaux..." -ForegroundColor Yellow

$keyFiles = @(
    "ai-services\ollama\models\id_ed25519",
    "ai-services\ollama\models\id_ed25519.pub"
)

$filesFound = $false
foreach ($file in $keyFiles) {
    if (Test-Path $file) {
        Write-Host "  [!] TROUVE: $file" -ForegroundColor Red
        $filesFound = $true
    } else {
        Write-Host "  [OK] Supprime: $file" -ForegroundColor Green
    }
}

if ($filesFound) {
    Write-Host "`n  Action requise: Supprimer les fichiers trouves!" -ForegroundColor Red
    Write-Host "  Commande: rm ai-services\ollama\models\id_ed25519*`n" -ForegroundColor Yellow
} else {
    Write-Host "  Tous les fichiers locaux sont supprimes.`n" -ForegroundColor Green
}

# 2. Vérifier les clés SSH système
Write-Host "[2/5] Verification cles SSH systeme (~/.ssh)..." -ForegroundColor Yellow

$sshPath = Join-Path $env:USERPROFILE ".ssh"
if (Test-Path $sshPath) {
    $sshFiles = Get-ChildItem $sshPath -Filter "*.pub" -ErrorAction SilentlyContinue
    
    $foundInSystem = $false
    foreach ($file in $sshFiles) {
        $content = Get-Content $file.FullName -Raw
        if ($content -match $CompromisedKey) {
            Write-Host "  [!] CLE COMPROMISE TROUVEE: $($file.Name)" -ForegroundColor Red
            $foundInSystem = $true
        }
    }
    
    if (-not $foundInSystem) {
        Write-Host "  [OK] Aucune cle compromise dans ~/.ssh`n" -ForegroundColor Green
    } else {
        Write-Host "  Action requise: Supprimer/remplacer les cles trouvees!`n" -ForegroundColor Red
    }
} else {
    Write-Host "  [OK] Pas de dossier ~/.ssh (normal)`n" -ForegroundColor Gray
}

# 3. Guide GitHub
Write-Host "[3/5] Verification GitHub (manuel)..." -ForegroundColor Yellow
Write-Host "  1. Ouvrir: https://github.com/settings/keys" -ForegroundColor Cyan
Write-Host "  2. Chercher la cle: $CompromisedKey" -ForegroundColor Gray
Write-Host "  3. Si trouvee -> DELETE immediatement!`n" -ForegroundColor Red

$response = Read-Host "  Avez-vous verifie GitHub? (o/n)"
if ($response -eq "o") {
    $found = Read-Host "  Cle trouvee sur GitHub? (o/n)"
    if ($found -eq "o") {
        Write-Host "  [!] ACTION REQUISE: Supprimer la cle de GitHub maintenant!`n" -ForegroundColor Red
    } else {
        Write-Host "  [OK] Pas de cle compromise sur GitHub`n" -ForegroundColor Green
    }
} else {
    Write-Host "  [!] ATTENTION: Verification GitHub non effectuee!`n" -ForegroundColor Yellow
}

# 4. Vérifier l'historique Git
Write-Host "[4/5] Verification historique Git local..." -ForegroundColor Yellow

$exposedCommit = git log --all --oneline | Select-String "05bdc59"
if ($exposedCommit) {
    Write-Host "  [!] Commit d'exposition present dans l'historique local" -ForegroundColor Red
    Write-Host "  Commit: 05bdc59 (feat: v1.1.0 - Complete i18n...)" -ForegroundColor Gray
    Write-Host "  Note: Ce commit est sur GitHub et contient la cle privee`n" -ForegroundColor Yellow
} else {
    Write-Host "  [?] Commit d'exposition non trouve (peut-etre nettoye)`n" -ForegroundColor Gray
}

# 5. Résumé et Actions
Write-Host "[5/5] Résumé et Actions Recommandées..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ACTIONS A COMPLETER MANUELLEMENT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. [ ] Verifier GitHub SSH Keys:" -ForegroundColor White
Write-Host "   https://github.com/settings/keys" -ForegroundColor Gray
Write-Host ""
Write-Host "2. [ ] Verifier Deploy Keys des repos:" -ForegroundColor White
Write-Host "   https://github.com/Monsau/Talentys-OSS-Data-Platform/settings/keys" -ForegroundColor Gray
Write-Host ""
Write-Host "3. [ ] Si cle utilisee ailleurs:" -ForegroundColor White
Write-Host "   - GitLab: https://gitlab.com/-/profile/keys" -ForegroundColor Gray
Write-Host "   - Serveurs personnels: grep dans ~/.ssh/authorized_keys" -ForegroundColor Gray
Write-Host ""
Write-Host "4. [ ] Si cle trouvee, generer nouvelles cles:" -ForegroundColor White
Write-Host "   ssh-keygen -t ed25519 -C `"votre-email@example.com`"" -ForegroundColor Gray
Write-Host ""
Write-Host "5. [ ] Considerer nettoyage historique Git:" -ForegroundColor White
Write-Host "   - Option A: git-filter-repo (recommande)" -ForegroundColor Gray
Write-Host "   - Option B: BFG Repo-Cleaner" -ForegroundColor Gray
Write-Host "   - Option C: Laisser tel quel (moins securise)" -ForegroundColor Gray
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  INFORMATIONS CLE COMPROMISE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Type: ED25519" -ForegroundColor Gray
Write-Host "Fingerprint: (calculer avec ssh-keygen -lf)" -ForegroundColor Gray
Write-Host "Exposition: https://github.com/Monsau/Talentys-OSS-Data-Platform/blob/05bdc59/ai-services/ollama/models/id_ed25519" -ForegroundColor Gray
Write-Host "Status: COMPROMISE - NE PLUS UTILISER" -ForegroundColor Red
Write-Host ""

Write-Host "Pour plus de details, voir: SECURITY_SSH_KEY_CHECK.md`n" -ForegroundColor Cyan

# Proposer d'ouvrir le navigateur
$openBrowser = Read-Host "Ouvrir GitHub SSH Keys dans le navigateur? (o/n)"
if ($openBrowser -eq "o") {
    Start-Process "https://github.com/settings/keys"
}

Write-Host "`nVerification terminee.`n" -ForegroundColor Green
