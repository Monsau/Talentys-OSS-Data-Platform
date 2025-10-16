# OPENSOURCE CLEANUP SCRIPT
# Nettoie le projet avant mise en open source
# Date: October 16, 2025

param(
    [switch]$DryRun,
    [switch]$Force
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "OPENSOURCE CLEANUP SCRIPT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be deleted`n" -ForegroundColor Yellow
}

# Check project root
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "ERROR: Not in project root directory!" -ForegroundColor Red
    exit 1
}

Write-Host "Project root confirmed`n" -ForegroundColor Green

$FilesRemoved = 0

# Function to remove safely
function Remove-ItemSafely {
    param([string]$Path, [string]$Description)
    
    if (Test-Path $Path) {
        $size = (Get-ChildItem $Path -Recurse -Force -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        
        if ($DryRun) {
            Write-Host "[DRY RUN] Would remove: $Description ($sizeMB MB)" -ForegroundColor Yellow
        } else {
            try {
                Remove-Item $Path -Recurse -Force
                Write-Host "Removed: $Description ($sizeMB MB)" -ForegroundColor Green
                $script:FilesRemoved++
            } catch {
                Write-Host "Could not remove $Path : $_" -ForegroundColor Red
            }
        }
    }
}

# ========================================
# CLEANUP SECTIONS
# ========================================

Write-Host "`n=== Cleaning Backups and Archives ===" -ForegroundColor Cyan
Remove-ItemSafely "backup_20251015_224849" "Old backup directory"
Remove-ItemSafely "archive" "Archive directory"

Write-Host "`n=== Cleaning Logs ===" -ForegroundColor Cyan
Remove-ItemSafely "logs" "Logs directory"

Write-Host "`n=== Cleaning Temporary Files ===" -ForegroundColor Cyan
Get-ChildItem -Filter "*_COMPLETE.md" | ForEach-Object {
    Remove-ItemSafely $_.FullName "Report: $($_.Name)"
}
Get-ChildItem -Filter "*_REPORT.json" | ForEach-Object {
    Remove-ItemSafely $_.FullName "Report: $($_.Name)"
}
Get-ChildItem -Filter "*_REPORT.md" | ForEach-Object {
    Remove-ItemSafely $_.FullName "Report: $($_.Name)"
}
Get-ChildItem -Filter "PHASE*.md" | ForEach-Object {
    Remove-ItemSafely $_.FullName "Phase: $($_.Name)"
}
Get-ChildItem -Filter "TODO*.md" | ForEach-Object {
    Remove-ItemSafely $_.FullName "TODO: $($_.Name)"
}

Write-Host "`n=== Cleaning Development Scripts ===" -ForegroundColor Cyan
$devScripts = @(
    "cleanup_and_reorganize_i18n.py",
    "create_professional_i18n_docs.py",
    "fix_business_overview.py",
    "reorganize_project.py",
    "verify_professional_docs.py"
)
foreach ($script in $devScripts) {
    Remove-ItemSafely $script "Dev script: $script"
}

Write-Host "`n=== Cleaning Python Artifacts ===" -ForegroundColor Cyan
Get-ChildItem -Filter "__pycache__" -Recurse -Directory | ForEach-Object {
    Remove-ItemSafely $_.FullName "Python cache: $($_.FullName)"
}

Write-Host "`n=== Checking Credentials ===" -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host ".env file exists (verify it is in .gitignore!)" -ForegroundColor Yellow
} else {
    Write-Host ".env file not found" -ForegroundColor Green
}

if (Test-Path ".env.example") {
    Write-Host ".env.example exists" -ForegroundColor Green
} else {
    Write-Host ".env.example NOT FOUND - create it!" -ForegroundColor Red
}

Write-Host "`n=== Checking Documentation ===" -ForegroundColor Cyan
$docs = @("README.md", "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md")
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "$doc exists" -ForegroundColor Green
    } else {
        Write-Host "$doc MISSING!" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "MODE: DRY RUN (no files deleted)" -ForegroundColor Yellow
} else {
    Write-Host "MODE: ACTIVE" -ForegroundColor Green
    Write-Host "Files Removed: $FilesRemoved" -ForegroundColor Green
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Verify credentials:"
Write-Host "   git check-ignore .env"
Write-Host ""
Write-Host "2. Scan for secrets:"
Write-Host "   git grep -i password | grep -v example"
Write-Host ""
Write-Host "3. Test clean install:"
Write-Host "   Follow README.md instructions"
Write-Host ""
Write-Host "4. Final check:"
Write-Host "   git status"
Write-Host ""

if ($DryRun) {
    Write-Host "Run without -DryRun to actually delete files" -ForegroundColor Yellow
} else {
    Write-Host "Cleanup complete!" -ForegroundColor Green
}

Write-Host ""
