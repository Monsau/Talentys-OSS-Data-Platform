# Test S3 Integration Script
# Tests document upload with S3 storage

Write-Host "🧪 Testing S3 Integration" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

$RAG_API = "http://localhost:8002"
$testsPassed = 0
$testsFailed = 0

# Helper function to test endpoint
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET"
    )
    
    Write-Host "Testing: $Name..." -NoNewline
    try {
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        }
        if ($response.StatusCode -eq 200) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        return $false
    }
}

# Test 1: RAG API Health
Write-Host "📋 Test 1: RAG API Health Check" -ForegroundColor Yellow
if (Test-Endpoint -Name "RAG API Health" -Url "$RAG_API/health") {
    $testsPassed++
} else {
    $testsFailed++
}
Write-Host ""

# Test 2: List Documents (should work even if empty)
Write-Host "📋 Test 2: List Documents Endpoint" -ForegroundColor Yellow
if (Test-Endpoint -Name "List Documents" -Url "$RAG_API/documents/list") {
    $testsPassed++
    try {
        $response = Invoke-RestMethod -Uri "$RAG_API/documents/list" -Method Get
        Write-Host "  📊 Found $($response.count) documents in bucket" -ForegroundColor Cyan
    } catch {
        Write-Host "  ⚠️  Could not parse response" -ForegroundColor Yellow
    }
} else {
    $testsFailed++
}
Write-Host ""

# Test 3: Create test file and upload
Write-Host "📋 Test 3: Upload Test Document" -ForegroundColor Yellow
$testFile = "test_document_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$testContent = @"
This is a test document for S3 integration testing.
Created on: $(Get-Date)
Purpose: Verify that documents are correctly stored in MinIO S3 bucket.

Test Content:
- Line 1: Hello from the test
- Line 2: This is a second line
- Line 3: Third line for chunking test
"@

# Create test file
Set-Content -Path $testFile -Value $testContent
Write-Host "  Created test file: $testFile" -ForegroundColor Cyan

# Upload file
try {
    Write-Host "  Uploading file..." -NoNewline
    
    $form = @{
        file = Get-Item -Path $testFile
        tags = "test,automation,s3-integration"
    }
    
    $response = Invoke-RestMethod -Uri "$RAG_API/upload/document" -Method Post -Form $form -TimeoutSec 30
    
    if ($response.status -eq "success") {
        Write-Host " ✅ PASS" -ForegroundColor Green
        Write-Host "  📄 Filename: $($response.filename)" -ForegroundColor Cyan
        Write-Host "  📊 Chunks: $($response.chunks)" -ForegroundColor Cyan
        Write-Host "  💾 Storage: $($response.storage_status)" -ForegroundColor Cyan
        Write-Host "  📍 S3 Path: $($response.s3_path)" -ForegroundColor Cyan
        $testsPassed++
        
        # Save S3 path for later tests
        $script:uploadedS3Path = $response.s3_path
        $script:uploadedFilename = $response.filename
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    $testsFailed++
}

# Cleanup test file
Remove-Item -Path $testFile -ErrorAction SilentlyContinue
Write-Host ""

# Test 4: Verify document appears in list
Write-Host "📋 Test 4: Verify Document in List" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$RAG_API/documents/list?max_results=100" -Method Get
    $found = $false
    foreach ($doc in $response.documents) {
        if ($doc.object_name -match [regex]::Escape($script:uploadedFilename)) {
            $found = $true
            Write-Host "  ✅ Document found in S3 bucket" -ForegroundColor Green
            Write-Host "  📄 Name: $($doc.object_name)" -ForegroundColor Cyan
            Write-Host "  📦 Size: $($doc.size) bytes" -ForegroundColor Cyan
            Write-Host "  📅 Modified: $($doc.last_modified)" -ForegroundColor Cyan
            break
        }
    }
    
    if ($found) {
        $testsPassed++
    } else {
        Write-Host "  ❌ Document not found in list" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ❌ FAIL - Error: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 5: MinIO Console Access
Write-Host "📋 Test 5: MinIO Console Access" -ForegroundColor Yellow
if (Test-Endpoint -Name "MinIO Console" -Url "http://localhost:9001") {
    $testsPassed++
    Write-Host "  🌐 MinIO Console: http://localhost:9001" -ForegroundColor Cyan
    Write-Host "  👤 Username: minioadmin" -ForegroundColor Cyan
    Write-Host "  🔑 Password: minioadmin" -ForegroundColor Cyan
} else {
    $testsFailed++
}
Write-Host ""

# Test Results Summary
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 Test Results Summary" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Tests Passed: $testsPassed" -ForegroundColor Green
Write-Host "❌ Tests Failed: $testsFailed" -ForegroundColor Red
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "🎉 All tests passed! S3 integration is working correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Open Chat UI: http://localhost:8501" -ForegroundColor White
    Write-Host "   2. Upload documents and verify S3 storage status" -ForegroundColor White
    Write-Host "   3. Check MinIO Console to view stored files" -ForegroundColor White
    Write-Host "   4. Try asking questions about uploaded documents" -ForegroundColor White
} else {
    Write-Host "⚠️  Some tests failed. Please check the errors above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   - Check if all services are running: docker-compose -f docker-compose-ai.yml ps" -ForegroundColor White
    Write-Host "   - View logs: docker-compose -f docker-compose-ai.yml logs" -ForegroundColor White
    Write-Host "   - Restart services: docker-compose -f docker-compose-ai.yml restart" -ForegroundColor White
}
Write-Host ""
