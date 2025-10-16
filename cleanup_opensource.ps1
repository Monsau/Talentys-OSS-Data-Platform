# 🧹 OPENSOURCE CLEANUP SCRIPT
# ================================
# Nettoie le projet avant mise en open source
# Date: October 16, 2025

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$script:CleanupLog = @()
$script:FilesRemoved = 0
$script:BytesFreed = 0

# Couleurs
function Write-Header($message) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Info($message) {
    if ($Verbose) {
        Write-Host "ℹ️  $message" -ForegroundColor Blue
    }
}

function Get-FormattedSize($bytes) {
    if ($bytes -ge 1GB) {
        return "{0:N2} GB" -f ($bytes / 1GB)
    } elseif ($bytes -ge 1MB) {
        return "{0:N2} MB" -f ($bytes / 1MB)
    } elseif ($bytes -ge 1KB) {
        return "{0:N2} KB" -f ($bytes / 1KB)
    } else {
        return "$bytes bytes"
    }
}

function Remove-ItemSafely {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        try {
            $size = (Get-ChildItem $Path -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            
            if ($DryRun) {
                Write-Info "[DRY RUN] Would remove: $Path ($(Get-FormattedSize $size))"
                $script:CleanupLog += "WOULD REMOVE: $Path - $Description"
            } else {
                Remove-Item $Path -Recurse -Force
                Write-Success "Removed: $Description ($(Get-FormattedSize $size))"
                $script:FilesRemoved++
                $script:BytesFreed += $size
                $script:CleanupLog += "REMOVED: $Path - $Description"
            }
        } catch {
            Write-Warning "Could not remove $Path : $_"
            $script:CleanupLog += "ERROR: $Path - $_"
        }
    } else {
        Write-Info "Not found (already clean): $Description"
    }
}

# ========================================
# MAIN CLEANUP
# ========================================

Write-Header "🧹 OPENSOURCE CLEANUP SCRIPT"

if ($DryRun) {
    Write-Warning "DRY RUN MODE - No files will be deleted"
}

# Vérifier qu'on est dans le bon répertoire
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "ERROR: Not in project root directory!"
    Write-Error "Please run this script from the project root (where pyproject.toml is)"
    exit 1
}

Write-Success "Project root directory confirmed"
Write-Info "Starting cleanup process...`n"

# ========================================
# 1. BACKUPS ET ARCHIVES
# ========================================

Write-Header "📦 Cleaning Backups and Archives"

Remove-ItemSafely "backup_20251015_224849" "Old backup directory"
Remove-ItemSafely "archive" "Archive directory"
Get-ChildItem -Filter "*.backup" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Backup file: $($_.Name)"
}
Get-ChildItem -Filter "*.bak" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Backup file: $($_.Name)"
}
Get-ChildItem -Filter "*.old" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Old file: $($_.Name)"
}

# ========================================
# 2. LOGS
# ========================================

Write-Header "📝 Cleaning Logs"

Remove-ItemSafely "logs" "Logs directory"
Get-ChildItem -Filter "*.log" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Log file: $($_.Name)"
}

# ========================================
# 3. FICHIERS TEMPORAIRES
# ========================================

Write-Header "🗑️  Cleaning Temporary Files"

# Rapports temporaires
Get-ChildItem -Filter "*_COMPLETE.md" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Temporary report: $($_.Name)"
}
Get-ChildItem -Filter "*_REPORT.json" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Temporary report: $($_.Name)"
}
Get-ChildItem -Filter "*_REPORT.md" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Temporary report: $($_.Name)"
}

# Phase files
Get-ChildItem -Filter "PHASE*.md" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Phase file: $($_.Name)"
}

# TODO files
Get-ChildItem -Filter "TODO*.md" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "TODO file: $($_.Name)"
}

# ========================================
# 4. SCRIPTS DE DÉVELOPPEMENT
# ========================================

Write-Header "🔧 Cleaning Development Scripts"

$devScripts = @(
    "cleanup_and_reorganize_i18n.py",
    "create_professional_i18n_docs.py",
    "fix_business_overview.py",
    "reorganize_project.py",
    "verify_professional_docs.py"
)

foreach ($script in $devScripts) {
    Remove-ItemSafely $script "Development script: $script"
}

# ========================================
# 5. PYTHON ARTIFACTS
# ========================================

Write-Header "🐍 Cleaning Python Artifacts"

Get-ChildItem -Filter "__pycache__" -Recurse -Directory | ForEach-Object {
    Remove-ItemSafely $_.FullName "Python cache: $($_.Name)"
}
Get-ChildItem -Filter "*.pyc" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Python cache: $($_.Name)"
}
Get-ChildItem -Filter "*.pyo" -Recurse | ForEach-Object {
    Remove-ItemSafely $_.FullName "Python cache: $($_.Name)"
}

# ========================================
# 6. VÉRIFICATION .ENV
# ========================================

Write-Header "🔒 Verifying Credentials Safety"

if (Test-Path ".env") {
    Write-Success ".env file exists (good for development)"
    Write-Warning "⚠️  CRITICAL: Verify .env is in .gitignore before commit!"
    Write-Warning "⚠️  Run: git check-ignore .env"
} else {
    Write-Info ".env file not found (will use .env.example)"
}

if (Test-Path ".env.example") {
    Write-Success ".env.example exists (good for users)"
} else {
    Write-Warning "⚠️  .env.example not found - create it from template!"
}

# ========================================
# 7. VÉRIFICATION GITIGNORE
# ========================================

Write-Header "📋 Verifying .gitignore"

if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    
    $requiredPatterns = @(".env", "__pycache__", "*.pyc", "logs/", "backup*/", "*.log")
    $missingPatterns = @()
    
    foreach ($pattern in $requiredPatterns) {
        if ($gitignoreContent -notmatch [regex]::Escape($pattern)) {
            $missingPatterns += $pattern
        }
    }
    
    if ($missingPatterns.Count -eq 0) {
        Write-Success ".gitignore contains all required patterns"
    } else {
        Write-Warning "⚠️  .gitignore missing patterns:"
        foreach ($pattern in $missingPatterns) {
            Write-Warning "   - $pattern"
        }
    }
} else {
    Write-Error "❌ .gitignore not found!"
}

# ========================================
# 8. SCAN DE SÉCURITÉ
# ========================================

Write-Header "🔍 Security Scan"

Write-Info "Scanning for potential credentials in code..."

$suspiciousPatterns = @(
    @{Pattern='password\s*=\s*[''"](?!.*example|.*changeme|.*your_)'; Name="Hardcoded password"},
    @{Pattern='token\s*=\s*[''"](?!.*example|.*your_)'; Name="Hardcoded token"},
    @{Pattern='api[_-]?key\s*=\s*[''"](?!.*example|.*your_)'; Name="Hardcoded API key"},
    @{Pattern='secret\s*=\s*[''"](?!.*example|.*your_)'; Name="Hardcoded secret"}
)

$foundIssues = @()

Get-ChildItem -Recurse -Include *.py,*.yml,*.yaml,*.json,*.sh,*.ps1 | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    
    foreach ($check in $suspiciousPatterns) {
        if ($content -match $check.Pattern) {
            $foundIssues += "$($_.FullName): $($check.Name)"
        }
    }
}

if ($foundIssues.Count -eq 0) {
    Write-Success "No obvious credentials found in code"
} else {
    Write-Warning "⚠️  Found $($foundIssues.Count) potential credential issues:"
    foreach ($issue in $foundIssues | Select-Object -First 10) {
        Write-Warning "   - $issue"
    }
    if ($foundIssues.Count -gt 10) {
        Write-Warning "   ... and $($foundIssues.Count - 10) more"
    }
}

# ========================================
# 9. VÉRIFICATION DOCUMENTATION
# ========================================

Write-Header "📚 Verifying Documentation"

$requiredDocs = @(
    @{File="README.md"; Description="Main README"},
    @{File="LICENSE"; Description="License file"},
    @{File="CONTRIBUTING.md"; Description="Contributing guidelines"},
    @{File="CODE_OF_CONDUCT.md"; Description="Code of Conduct"},
    @{File="SECURITY.md"; Description="Security policy"},
    @{File=".env.example"; Description="Environment example"}
)

foreach ($doc in $requiredDocs) {
    if (Test-Path $doc.File) {
        Write-Success "$($doc.Description) exists"
    } else {
        Write-Warning "⚠️  Missing: $($doc.Description) ($($doc.File))"
    }
}

# ========================================
# 10. RÉSUMÉ
# ========================================

Write-Header "📊 CLEANUP SUMMARY"

if ($DryRun) {
    Write-Host "MODE: DRY RUN (no files were deleted)" -ForegroundColor Yellow
} else {
    Write-Host "MODE: ACTIVE (files were deleted)" -ForegroundColor Green
}

Write-Host "`nStatistics:" -ForegroundColor Cyan
Write-Host "  Files/Folders Removed: $script:FilesRemoved"
Write-Host "  Space Freed: $(Get-FormattedSize $script:BytesFreed)"

Write-Host "`nLog Entries: $($script:CleanupLog.Count)" -ForegroundColor Cyan

if ($Verbose -and $script:CleanupLog.Count -gt 0) {
    Write-Host "`nDetailed Log:" -ForegroundColor Cyan
    $script:CleanupLog | ForEach-Object { Write-Host "  $_" }
}

# ========================================
# NEXT STEPS
# ========================================

Write-Header "✅ NEXT STEPS"

Write-Host "Before pushing to open source:"
Write-Host ""
Write-Host "1. 🔒 Verify credentials:"
Write-Host "   git grep -i 'password.*=' | grep -v 'example'"
Write-Host "   git grep -i 'token.*=' | grep -v 'example'"
Write-Host ""
Write-Host "2. 📝 Update documentation:"
Write-Host "   - Review README.md"
Write-Host "   - Update SECURITY.md (add contact email)"
Write-Host "   - Update CODE_OF_CONDUCT.md (add contact email)"
Write-Host ""
Write-Host "3. 🧪 Test clean install:"
Write-Host "   git clone (new-location)"
Write-Host "   Follow README instructions"
Write-Host ""
Write-Host "4. 🔍 Run security scan:"
Write-Host "   pip install detect-secrets"
Write-Host "   detect-secrets scan"
Write-Host ""
Write-Host "5. ✅ Final checks:"
Write-Host "   git status"
Write-Host "   git check-ignore .env"
Write-Host "   git ls-files | wc -l"
Write-Host ""

if (-not $DryRun) {
    Write-Success "🎉 Cleanup complete!"
} else {
    Write-Warning "Run without -DryRun to actually clean files"
}

Write-Host ""
