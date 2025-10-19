# Scripts - AI Services Deployment & Testing

This directory contains PowerShell scripts for deploying and testing the AI services stack.

## Available Scripts

### 1. deploy-ai-services.ps1

**Purpose:** Automated deployment of the complete AI stack with health checks.

**Usage:**
```powershell
.\scripts\deploy-ai-services.ps1
```

**What it does:**
- ✅ Checks Docker is running
- ✅ Starts all AI services (MinIO, Ollama, Milvus, RAG API, Chat UI)
- ✅ Waits for services to be ready
- ✅ Checks health of each service
- ✅ Downloads Llama 3.1 model if not present
- ✅ Displays service URLs and next steps

**Output Example:**
```
🚀 AI Services Deployment Script
=================================

📋 Checking prerequisites...
✅ Docker is running

📦 Starting AI services...
⏳ Waiting for services to be ready...

🏥 Checking service health...
✅ MinIO: Running (http://localhost:9001)
✅ Ollama: Running (http://localhost:11434)
✅ RAG API: Running (http://localhost:8002)
✅ Chat UI: Running (http://localhost:8501)

🔍 Checking LLM models...
✅ Llama 3.1 model is installed

🎉 AI Services Deployment Complete!
```

**Time:** ~5-10 minutes (including model download)

---

### 2. test-s3-integration.ps1

**Purpose:** Automated testing of S3/MinIO storage integration.

**Usage:**
```powershell
.\scripts\test-s3-integration.ps1
```

**What it does:**
- ✅ Tests RAG API health endpoint
- ✅ Tests document listing endpoint
- ✅ Creates and uploads test document
- ✅ Verifies S3 storage status
- ✅ Checks document appears in list
- ✅ Tests MinIO console access
- ✅ Provides detailed test results

**Tests Performed:**
1. **RAG API Health Check** - Verifies API is responding
2. **List Documents Endpoint** - Tests document listing
3. **Upload Test Document** - Creates and uploads test file
4. **Verify Document in List** - Confirms upload succeeded
5. **MinIO Console Access** - Checks console is accessible

**Output Example:**
```
🧪 Testing S3 Integration
=========================

📋 Test 1: RAG API Health Check
Testing: RAG API Health... ✅ PASS

📋 Test 2: List Documents Endpoint
Testing: List Documents... ✅ PASS
  📊 Found 3 documents in bucket

📋 Test 3: Upload Test Document
  Created test file: test_document_20251018_143022.txt
  Uploading file... ✅ PASS
  📄 Filename: test_document_20251018_143022.txt
  📊 Chunks: 3
  💾 Storage: stored
  📍 S3 Path: s3://ai-documents/2025/10/18/...

📋 Test 4: Verify Document in List
  ✅ Document found in S3 bucket
  📄 Name: 2025/10/18/1729267200_a1b2c3d4_test_document_20251018_143022.txt
  📦 Size: 256 bytes
  📅 Modified: 2025-10-18T14:30:22Z

📋 Test 5: MinIO Console Access
Testing: MinIO Console... ✅ PASS
  🌐 MinIO Console: http://localhost:9001
  👤 Username: minioadmin
  🔑 Password: minioadmin

═══════════════════════════════════════
📊 Test Results Summary
═══════════════════════════════════════

✅ Tests Passed: 5
❌ Tests Failed: 0

🎉 All tests passed! S3 integration is working correctly.
```

**Time:** ~30 seconds

---

## Prerequisites

### System Requirements
- Windows with PowerShell 5.1 or higher
- Docker Desktop running
- Docker Compose installed
- Internet connection (for model downloads)

### Before Running Scripts
1. Ensure Docker Desktop is running
2. Navigate to project root: `cd c:\projets\dremiodbt`
3. Make sure docker-compose-ai.yml exists

---

## Common Usage Patterns

### First-Time Deployment

```powershell
# 1. Deploy all services
.\scripts\deploy-ai-services.ps1

# 2. Wait for deployment to complete (~5-10 minutes)

# 3. Test the integration
.\scripts\test-s3-integration.ps1

# 4. Open Chat UI
start http://localhost:8501
```

### After Code Changes

```powershell
# Rebuild and restart services
docker-compose -f docker-compose-ai.yml up -d --build

# Test the changes
.\scripts\test-s3-integration.ps1
```

### Troubleshooting

```powershell
# View logs
docker-compose -f docker-compose-ai.yml logs -f

# Restart specific service
docker-compose -f docker-compose-ai.yml restart rag-api

# Stop all services
docker-compose -f docker-compose-ai.yml stop

# Remove all services and data
docker-compose -f docker-compose-ai.yml down -v
```

---

## Service URLs (After Deployment)

| Service | URL | Credentials |
|---------|-----|-------------|
| Chat UI | http://localhost:8501 | None |
| RAG API | http://localhost:8002 | None |
| MinIO Console | http://localhost:9001 | minioadmin/minioadmin |
| Ollama API | http://localhost:11434 | None |

---

## Expected Results

### Successful Deployment
- All 5 tests pass in test-s3-integration.ps1
- Chat UI loads at http://localhost:8501
- MinIO console accessible at http://localhost:9001
- Documents upload with S3 storage confirmation

### Troubleshooting Failed Tests

**If RAG API health fails:**
```powershell
docker logs rag-api
docker-compose -f docker-compose-ai.yml restart rag-api
```

**If MinIO fails:**
```powershell
docker logs minio-ai
docker-compose -f docker-compose-ai.yml restart minio
```

**If Ollama model missing:**
```powershell
docker exec ollama ollama pull llama3.1
```

---

## Advanced Usage

### Running Specific Tests

Edit `test-s3-integration.ps1` to comment out tests you don't want to run.

### Custom Configuration

Modify docker-compose-ai.yml for:
- Different MinIO credentials
- Custom bucket names
- Different LLM models
- Resource limits

### Performance Monitoring

```powershell
# Monitor resource usage
docker stats

# Check MinIO bucket size
docker exec minio-ai du -sh /data

# View Milvus collection info
docker exec milvus curl localhost:9091/healthz
```

---

## Next Steps

After successful deployment and testing:

1. **Upload Documents**
   - Open Chat UI: http://localhost:8501
   - Use sidebar to upload PDFs, Word docs, Excel files
   - Verify S3 storage status

2. **Query Documents**
   - Ask questions about uploaded documents
   - Check sources include S3 paths

3. **Browse S3 Storage**
   - Open MinIO console: http://localhost:9001
   - Browse ai-documents bucket
   - View uploaded files

4. **Production Setup**
   - Change MinIO credentials
   - Enable HTTPS
   - Add authentication
   - Configure backups

---

## Documentation

- [S3 Storage Integration](../docs/guides/S3_STORAGE_INTEGRATION.md)
- [Quick Deployment Guide](../docs/AI_DEPLOYMENT_QUICK.md)
- [Implementation Summary](../S3_IMPLEMENTATION_COMPLETE.md)
- [AI Services Guide](../AI_SERVICES_GUIDE.md)

---

## Support

If you encounter issues:

1. Check Docker is running
2. View service logs: `docker-compose -f docker-compose-ai.yml logs`
3. Restart services: `docker-compose -f docker-compose-ai.yml restart`
4. Check documentation in `docs/` folder
