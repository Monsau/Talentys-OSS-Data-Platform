# AI Services Deployment Script
# Quick start script for deploying the complete AI stack

Write-Host "🚀 AI Services Deployment Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host ""
Write-Host "📦 Starting AI services..." -ForegroundColor Yellow
docker-compose -f docker-compose-ai.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host ""
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow

# Check MinIO
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ MinIO: Running (http://localhost:9001)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  MinIO: Not ready yet" -ForegroundColor Yellow
}

# Check Ollama
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Ollama: Running (http://localhost:11434)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama: Not ready yet" -ForegroundColor Yellow
}

# Check RAG API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ RAG API: Running (http://localhost:8002)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  RAG API: Not ready yet" -ForegroundColor Yellow
}

# Check Chat UI
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Chat UI: Running (http://localhost:8501)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Chat UI: Not ready yet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔍 Checking LLM models..." -ForegroundColor Yellow
$models = docker exec ollama ollama list 2>&1
if ($models -match "llama3.1") {
    Write-Host "✅ Llama 3.1 model is installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Llama 3.1 model not found" -ForegroundColor Yellow
    Write-Host "📥 Downloading Llama 3.1 model (this may take a few minutes)..." -ForegroundColor Yellow
    docker exec ollama ollama pull llama3.1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Llama 3.1 model downloaded successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to download model" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 AI Services Deployment Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Service URLs:" -ForegroundColor Yellow
Write-Host "   Chat UI:       http://localhost:8501" -ForegroundColor White
Write-Host "   RAG API:       http://localhost:8002" -ForegroundColor White
Write-Host "   MinIO Console: http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor White
Write-Host "   Ollama API:    http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Open Chat UI: http://localhost:8501" -ForegroundColor White
Write-Host "   2. Upload documents via sidebar" -ForegroundColor White
Write-Host "   3. Ask questions about your data" -ForegroundColor White
Write-Host "   4. View stored documents in MinIO console" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - S3 Storage: docs\guides\S3_STORAGE_INTEGRATION.md" -ForegroundColor White
Write-Host "   - Quick Guide: docs\AI_DEPLOYMENT_QUICK.md" -ForegroundColor White
Write-Host "   - Full Guide:  AI_SERVICES_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "🛠️  Useful Commands:" -ForegroundColor Yellow
Write-Host "   View logs:     docker-compose -f docker-compose-ai.yml logs -f" -ForegroundColor White
Write-Host "   Stop services: docker-compose -f docker-compose-ai.yml stop" -ForegroundColor White
Write-Host "   Restart:       docker-compose -f docker-compose-ai.yml restart" -ForegroundColor White
Write-Host ""
