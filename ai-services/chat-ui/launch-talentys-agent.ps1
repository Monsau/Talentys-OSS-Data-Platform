# Talentys AI Agent - Launch Script
# Starts both Chat UI and Admin Console

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  🎨 Talentys AI Agent Launcher" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if streamlit is installed
Write-Host "`n[1/5] Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠️  Streamlit not found. Installing dependencies..." -ForegroundColor Yellow
        cd ai-services\chat-ui
        pip install -r requirements-admin.txt
        cd ..\..
    } else {
        Write-Host "  ✓ Dependencies OK" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    exit 1
}

# Create config directory if not exists
Write-Host "`n[2/5] Setting up configuration..." -ForegroundColor Yellow
if (!(Test-Path "ai-services\chat-ui\config")) {
    New-Item -Path "ai-services\chat-ui\config" -ItemType Directory -Force | Out-Null
    Write-Host "  ✓ Config directory created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Config directory exists" -ForegroundColor Green
}

# Create __init__.py in config folder
if (!(Test-Path "ai-services\chat-ui\config\__init__.py")) {
    New-Item -Path "ai-services\chat-ui\config\__init__.py" -ItemType File -Force | Out-Null
}

Write-Host "`n[3/5] Starting services..." -ForegroundColor Yellow

# Start Chat UI in background
Write-Host "  🚀 Starting Chat UI on port 8501..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ai-services\chat-ui'; Write-Host 'Chat UI Running on http://localhost:8501' -ForegroundColor Green; streamlit run app.py --server.port 8501 --server.headless true"

Start-Sleep -Seconds 3

# Start Admin Console in background
Write-Host "  🚀 Starting Admin Console on port 8502..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ai-services\chat-ui'; Write-Host 'Admin Console Running on http://localhost:8502' -ForegroundColor Green; streamlit run admin.py --server.port 8502 --server.headless true"

Start-Sleep -Seconds 5

Write-Host "`n[4/5] Checking service status..." -ForegroundColor Yellow

# Check Chat UI
try {
    $chatResponse = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host "  ✓ Chat UI is running" -ForegroundColor Green
} catch {
    Write-Host "  ⏳ Chat UI is starting..." -ForegroundColor Yellow
}

# Check Admin Console
try {
    $adminResponse = Invoke-WebRequest -Uri "http://localhost:8502" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host "  ✓ Admin Console is running" -ForegroundColor Green
} catch {
    Write-Host "  ⏳ Admin Console is starting..." -ForegroundColor Yellow
}

Write-Host "`n[5/5] Launch complete!" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  🎉 Services Started Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`n📋 Access Your Interfaces:" -ForegroundColor White
Write-Host ""
Write-Host "  🤖 Chat UI (Main Interface)" -ForegroundColor Cyan
Write-Host "     → http://localhost:8501" -ForegroundColor White
Write-Host "     For end users to chat with AI" -ForegroundColor Gray
Write-Host ""
Write-Host "  🎨 Admin Console (Management)" -ForegroundColor Cyan
Write-Host "     → http://localhost:8502" -ForegroundColor White
Write-Host "     Customize theme, manage users, settings" -ForegroundColor Gray
Write-Host "     Default login: admin / talentys2025" -ForegroundColor Yellow
Write-Host ""

Write-Host "⚙️  Configuration:" -ForegroundColor White
Write-Host "  • Theme: Talentys branding applied ✓" -ForegroundColor Gray
Write-Host "  • Colors: #0066CC (Primary Blue) ✓" -ForegroundColor Gray
Write-Host "  • Logo: https://talentys.eu/logo.png ✓" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Quick Actions:" -ForegroundColor White
Write-Host "  [1] Open Chat UI in browser" -ForegroundColor Cyan
Write-Host "  [2] Open Admin Console in browser" -ForegroundColor Cyan
Write-Host "  [3] View documentation" -ForegroundColor Cyan
Write-Host "  [4] Stop all services" -ForegroundColor Cyan
Write-Host "  [Q] Quit launcher" -ForegroundColor Cyan
Write-Host ""

do {
    $choice = Read-Host "Enter your choice [1-4, Q]"
    
    switch ($choice) {
        "1" {
            Write-Host "  🌐 Opening Chat UI..." -ForegroundColor Green
            Start-Process "http://localhost:8501"
        }
        "2" {
            Write-Host "  🌐 Opening Admin Console..." -ForegroundColor Green
            Start-Process "http://localhost:8502"
        }
        "3" {
            Write-Host "  📖 Opening documentation..." -ForegroundColor Green
            $docPath = "ai-services\chat-ui\README-ADMIN.md"
            if (Test-Path $docPath) {
                notepad $docPath
            } else {
                Write-Host "  ⚠️  Documentation not found at $docPath" -ForegroundColor Yellow
            }
        }
        "4" {
            Write-Host "`n  🛑 Stopping services..." -ForegroundColor Yellow
            
            # Find and kill streamlit processes on ports 8501 and 8502
            $processes = Get-NetTCPConnection -LocalPort 8501,8502 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
            
            foreach ($pid in $processes) {
                try {
                    Stop-Process -Id $pid -Force
                    Write-Host "  ✓ Stopped process $pid" -ForegroundColor Green
                } catch {
                    Write-Host "  ✗ Failed to stop process $pid" -ForegroundColor Red
                }
            }
            
            Write-Host "  ✓ All services stopped" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "Q" {
            Write-Host "`n  👋 Goodbye!" -ForegroundColor Cyan
            break
        }
        default {
            Write-Host "  ⚠️  Invalid choice. Please enter 1-4 or Q" -ForegroundColor Yellow
        }
    }
    
    if ($choice -ne "Q") {
        Write-Host ""
    }
    
} while ($choice -ne "Q")

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  Made with ❤️  by Talentys" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
