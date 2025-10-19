"""
RAG API - FastAPI service for Retrieval Augmented Generation
Supports document uploads (PDF, Word, Excel, etc.) and database ingestion
Automatically stores uploaded documents to S3/MinIO
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
import psycopg2
import os
import json
from datetime import datetime
import hashlib

# Document processing imports
import PyPDF2
import docx
import pandas as pd
import io
import re

# S3/MinIO imports
from minio import Minio
from minio.error import S3Error

app = FastAPI(
    title="RAG API",
    description="Retrieval Augmented Generation API with document upload support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize MinIO on startup"""
    print("🚀 Starting RAG API...")
    if init_minio():
        print(f"✅ MinIO initialized - Documents will be stored in bucket: {MINIO_BUCKET}")
    else:
        print("⚠️ MinIO initialization failed - Documents will NOT be stored to S3")
    print("✅ RAG API ready!")

# Configuration
EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://embedding-service:8001")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
COLLECTION_NAME = "data_platform_knowledge"
EMBEDDING_DIM = 384
MAX_TEXT_LENGTH = 65535

# PostgreSQL configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "dremio-postgres"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "database": os.getenv("POSTGRES_DB", "business_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres123")
}

# Dremio configuration
DREMIO_CONFIG = {
    "host": os.getenv("DREMIO_HOST", "dremio"),
    "port": int(os.getenv("DREMIO_PORT", 31010)),
    "username": os.getenv("DREMIO_USER", "admin"),
    "password": os.getenv("DREMIO_PASSWORD", "admin123")
}

# MinIO/S3 configuration for document storage
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ai-documents")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Initialize MinIO client
minio_client = None

def init_minio():
    """Initialize MinIO client and create bucket if not exists"""
    global minio_client
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        
        # Create bucket if it doesn't exist
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"✅ Created MinIO bucket: {MINIO_BUCKET}")
        else:
            print(f"✅ MinIO bucket already exists: {MINIO_BUCKET}")
        
        return True
    except S3Error as e:
        print(f"❌ MinIO initialization error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ MinIO connection error: {str(e)}")
        return False

def upload_to_s3(file_bytes: bytes, filename: str, metadata: Dict) -> Optional[str]:
    """
    Upload document to MinIO S3 bucket
    Returns: S3 object path or None if failed
    """
    if minio_client is None:
        print("⚠️ MinIO client not initialized, skipping S3 upload")
        return None
    
    try:
        # Generate unique object name with timestamp and hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
        file_ext = filename.split('.')[-1] if '.' in filename else 'bin'
        
        # Object path: year/month/day/timestamp_hash_filename
        date_path = datetime.now().strftime("%Y/%m/%d")
        object_name = f"{date_path}/{timestamp}_{file_hash}_{filename}"
        
        # Prepare metadata for S3
        s3_metadata = {
            "original-filename": filename,
            "upload-date": datetime.now().isoformat(),
            "file-hash": hashlib.md5(file_bytes).hexdigest(),
            "content-type": get_content_type(filename),
        }
        
        # Add custom metadata
        if metadata.get("tags"):
            s3_metadata["tags"] = str(metadata["tags"])
        if metadata.get("source"):
            s3_metadata["source"] = str(metadata["source"])
        
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            data=io.BytesIO(file_bytes),
            length=len(file_bytes),
            content_type=get_content_type(filename),
            metadata=s3_metadata
        )
        
        print(f"✅ Uploaded to S3: {MINIO_BUCKET}/{object_name}")
        return f"s3://{MINIO_BUCKET}/{object_name}"
    
    except S3Error as e:
        print(f"❌ S3 upload error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return None

def get_content_type(filename: str) -> str:
    """Get MIME content type based on file extension"""
    ext_map = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'csv': 'text/csv',
        'txt': 'text/plain',
        'md': 'text/markdown',
        'json': 'application/json'
    }
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return ext_map.get(ext, 'application/octet-stream')

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    model: str = "llama3.1"
    temperature: float = 0.7

class IngestRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[Dict]] = None
    source: str = "manual"

class PostgresIngestRequest(BaseModel):
    table: str
    text_column: str
    metadata_columns: Optional[List[str]] = None

class DremioIngestRequest(BaseModel):
    sql_query: str
    text_column: str
    metadata_columns: Optional[List[str]] = None

# ============================================
# DOCUMENT PROCESSING FUNCTIONS (NEW)
# ============================================

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from Word document"""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Word document: {str(e)}")

def extract_text_from_excel(file_bytes: bytes, filename: str) -> str:
    """Extract text from Excel file"""
    try:
        # Try reading as Excel
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        else:
            df = pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
        
        # Convert dataframe to text representation
        text_parts = []
        for idx, row in df.iterrows():
            row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            text_parts.append(row_text)
        
        return "\n".join(text_parts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")

def extract_text_from_csv(file_bytes: bytes) -> str:
    """Extract text from CSV file"""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        
        # Convert dataframe to text representation
        text_parts = []
        for idx, row in df.iterrows():
            row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            text_parts.append(row_text)
        
        return "\n".join(text_parts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV file: {str(e)}")

def extract_text_from_json(file_bytes: bytes) -> str:
    """Extract text from JSON file"""
    try:
        data = json.loads(file_bytes.decode('utf-8'))
        
        # Convert JSON to readable text
        def json_to_text(obj, prefix=""):
            if isinstance(obj, dict):
                parts = []
                for key, val in obj.items():
                    parts.append(json_to_text(val, f"{prefix}{key}: "))
                return "\n".join(parts)
            elif isinstance(obj, list):
                parts = []
                for i, item in enumerate(obj):
                    parts.append(json_to_text(item, f"{prefix}[{i}] "))
                return "\n".join(parts)
            else:
                return f"{prefix}{obj}"
        
        return json_to_text(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read JSON file: {str(e)}")

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from uploaded file based on file type"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
        return extract_text_from_docx(file_bytes)
    elif filename_lower.endswith('.xlsx') or filename_lower.endswith('.xls'):
        return extract_text_from_excel(file_bytes, filename)
    elif filename_lower.endswith('.csv'):
        return extract_text_from_csv(file_bytes)
    elif filename_lower.endswith('.json'):
        return extract_text_from_json(file_bytes)
    elif filename_lower.endswith('.txt') or filename_lower.endswith('.md'):
        return file_bytes.decode('utf-8')
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {filename}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better context preservation"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for delimiter in ['. ', '.\n', '! ', '?\n', '\n\n']:
                last_break = text[start:end].rfind(delimiter)
                if last_break != -1:
                    end = start + last_break + len(delimiter)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else end
    
    return chunks

# ============================================
# MILVUS OPERATIONS
# ============================================

def create_milvus_collection():
    """Create Milvus collection if not exists"""
    try:
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
        
        if utility.has_collection(COLLECTION_NAME):
            return Collection(COLLECTION_NAME)
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=MAX_TEXT_LENGTH),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1000)
        ]
        
        schema = CollectionSchema(fields=fields, description="Data platform knowledge base")
        collection = Collection(name=COLLECTION_NAME, schema=schema)
        
        # Create index
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 1024}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Milvus collection: {str(e)}")

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings from embedding service"""
    try:
        response = httpx.post(
            f"{EMBEDDING_SERVICE_URL}/embed",
            json={"texts": texts},
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()["embeddings"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get embeddings: {str(e)}")

def query_ollama(prompt: str, model: str = "llama3.1", temperature: float = 0.7) -> str:
    """Query Ollama LLM"""
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            timeout=120.0
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query Ollama: {str(e)}")

def ingest_data(texts: List[str], metadatas: Optional[List[Dict]] = None, source: str = "manual") -> int:
    """Ingest data into Milvus"""
    if not texts:
        return 0
    
    # Prepare metadata
    if metadatas is None:
        metadatas = [{}] * len(texts)
    
    # Get embeddings
    embeddings = get_embeddings(texts)
    
    # Insert into Milvus
    collection = create_milvus_collection()
    collection.load()
    
    data = [
        embeddings,
        texts,
        metadatas,
        [source] * len(texts)
    ]
    
    collection.insert(data)
    collection.flush()
    
    return len(texts)

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
def root():
    return {
        "service": "RAG API",
        "version": "1.0.0",
        "features": ["query", "ingest", "document_upload", "postgres", "dremio"],
        "status": "healthy"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "rag-api", "version": "1.0.0"}

@app.get("/models")
def list_models():
    """List available LLM models"""
    try:
        response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=10.0)
        response.raise_for_status()
        models = response.json().get("models", [])
        return {"models": [m["name"] for m in models]}
    except Exception as e:
        return {"models": ["llama3.1", "mistral", "phi3"], "note": "Default models, Ollama may be unavailable"}

@app.post("/query")
def query_rag(request: QueryRequest):
    """Query the RAG system"""
    try:
        # Get query embedding
        query_embeddings = get_embeddings([request.question])
        query_embedding = query_embeddings[0]
        
        # Search Milvus
        collection = create_milvus_collection()
        collection.load()
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=request.top_k,
            output_fields=["text", "metadata", "source"]
        )
        
        # Extract sources
        sources = []
        context_parts = []
        
        for hits in results:
            for hit in hits:
                # Access Milvus Hit entity fields using dictionary .get() on entity object
                entity = hit.entity
                sources.append({
                    "text": entity.get("text"),
                    "score": float(hit.distance),
                    "metadata": entity.get("metadata") or {},
                    "source": entity.get("source")
                })
                context_parts.append(entity.get("text"))
        
        # Build prompt
        context = "\n\n".join(context_parts)
        prompt = f"""Based on the following context, answer the question. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {request.question}

Answer:"""
        
        # Query LLM
        answer = query_ollama(prompt, model=request.model, temperature=request.temperature)
        
        return {
            "question": request.question,
            "answer": answer,
            "sources": sources,
            "model": request.model,
            "top_k": request.top_k
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# ============================================
# DOCUMENT UPLOAD ENDPOINT (NEW)
# ============================================

@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    source: str = Form(None),
    tags: str = Form(None)
):
    """
    Upload and ingest a document (PDF, Word, Excel, CSV, JSON, TXT, Markdown)
    Automatically stores original file to MinIO S3 bucket
    """
    try:
        # Read file content
        file_bytes = await file.read()
        
        # Upload to S3/MinIO FIRST (preserve original)
        s3_path = upload_to_s3(file_bytes, file.filename, {
            "source": source,
            "tags": tags
        })
        
        # Extract text from file
        extracted_text = extract_text_from_file(file_bytes, file.filename)
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Chunk the text
        chunks = chunk_text(extracted_text, chunk_size=1000, overlap=200)
        
        # Prepare metadata
        file_hash = hashlib.md5(file_bytes).hexdigest()
        base_metadata = {
            "filename": file.filename,
            "upload_date": datetime.now().isoformat(),
            "file_type": file.filename.split('.')[-1].lower(),
            "file_hash": file_hash,
            "file_size_bytes": len(file_bytes),
            "file_size_mb": round(len(file_bytes) / (1024 * 1024), 2),
            "tags": [tag.strip() for tag in tags.split(',')] if tags else [],
            "s3_path": s3_path  # Store S3 location in metadata
        }
        
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            metadatas.append(chunk_metadata)
        
        # Determine source
        doc_source = source if source else f"uploaded:{file.filename}"
        
        # Ingest into vector database
        count = ingest_data(chunks, metadatas, doc_source)
        
        return {
            "message": f"Successfully ingested document: {file.filename}",
            "filename": file.filename,
            "chunks": count,
            "file_type": file.filename.split('.')[-1].lower(),
            "file_size_mb": round(len(file_bytes) / (1024 * 1024), 2),
            "source": doc_source,
            "s3_path": s3_path,
            "s3_bucket": MINIO_BUCKET if s3_path else None,
            "storage_status": "stored" if s3_path else "not_stored"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@app.get("/documents/list")
def list_documents(prefix: str = None, max_results: int = 100):
    """
    List documents stored in S3/MinIO bucket
    """
    if minio_client is None:
        raise HTTPException(status_code=503, detail="MinIO not available")
    
    try:
        documents = []
        objects = minio_client.list_objects(
            MINIO_BUCKET,
            prefix=prefix,
            recursive=True
        )
        
        count = 0
        for obj in objects:
            if count >= max_results:
                break
            
            # Get object metadata
            stat = minio_client.stat_object(MINIO_BUCKET, obj.object_name)
            
            documents.append({
                "object_name": obj.object_name,
                "size_bytes": obj.size,
                "size_mb": round(obj.size / (1024 * 1024), 2),
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                "content_type": stat.content_type if stat else None,
                "metadata": stat.metadata if stat else {},
                "s3_path": f"s3://{MINIO_BUCKET}/{obj.object_name}"
            })
            count += 1
        
        return {
            "bucket": MINIO_BUCKET,
            "count": len(documents),
            "documents": documents
        }
    
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.get("/documents/download/{year}/{month}/{day}/{filename}")
def download_document(year: str, month: str, day: str, filename: str):
    """
    Download original document from S3/MinIO
    """
    if minio_client is None:
        raise HTTPException(status_code=503, detail="MinIO not available")
    
    try:
        object_name = f"{year}/{month}/{day}/{filename}"
        
        # Get object
        response = minio_client.get_object(MINIO_BUCKET, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        
        # Get content type from metadata
        stat = minio_client.stat_object(MINIO_BUCKET, object_name)
        content_type = stat.content_type if stat else "application/octet-stream"
        
        return Response(
            content=data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename.split("_", 2)[-1]}"'
            }
        )
    
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Document not found")
        raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.delete("/documents/delete/{year}/{month}/{day}/{filename}")
def delete_document(year: str, month: str, day: str, filename: str):
    """
    Delete document from S3/MinIO (does not remove from vector DB)
    """
    if minio_client is None:
        raise HTTPException(status_code=503, detail="MinIO not available")
    
    try:
        object_name = f"{year}/{month}/{day}/{filename}"
        minio_client.remove_object(MINIO_BUCKET, object_name)
        
        return {
            "message": f"Document deleted: {object_name}",
            "object_name": object_name,
            "bucket": MINIO_BUCKET
        }
    
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Document not found")
        raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.post("/ingest/bulk")
def ingest_bulk(request: IngestRequest):
    """Bulk ingest documents"""
    try:
        count = ingest_data(request.texts, request.metadatas, request.source)
        return {"message": f"Successfully ingested {count} documents", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/ingest/postgres")
def ingest_from_postgres(request: PostgresIngestRequest):
    """Ingest data from PostgreSQL table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Build query
        columns = [request.text_column]
        if request.metadata_columns:
            columns.extend(request.metadata_columns)
        
        query = f"SELECT {', '.join(columns)} FROM {request.table}"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found in table {request.table}")
        
        # Prepare data
        texts = [str(row[0]) for row in rows if row[0]]
        metadatas = []
        
        if request.metadata_columns:
            for row in rows:
                metadata = {}
                for i, col in enumerate(request.metadata_columns):
                    metadata[col] = str(row[i + 1])
                metadatas.append(metadata)
        
        # Ingest
        count = ingest_data(texts, metadatas, f"postgres:{request.table}")
        
        return {"message": f"Successfully ingested {count} records from PostgreSQL table {request.table}", "count": count}
    
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"PostgreSQL error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/ingest/dremio")
def ingest_from_dremio(request: DremioIngestRequest):
    """Ingest data from Dremio SQL query"""
    try:
        conn = psycopg2.connect(
            host=DREMIO_CONFIG["host"],
            port=DREMIO_CONFIG["port"],
            user=DREMIO_CONFIG["username"],
            password=DREMIO_CONFIG["password"],
            database="Dremio"
        )
        cursor = conn.cursor()
        
        cursor.execute(request.sql_query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No data returned from query")
        
        # Find text column index
        text_col_idx = column_names.index(request.text_column)
        
        # Prepare data
        texts = [str(row[text_col_idx]) for row in rows if row[text_col_idx]]
        metadatas = []
        
        if request.metadata_columns:
            for row in rows:
                metadata = {}
                for col in request.metadata_columns:
                    if col in column_names:
                        col_idx = column_names.index(col)
                        metadata[col] = str(row[col_idx])
                metadatas.append(metadata)
        
        # Ingest
        count = ingest_data(texts, metadatas, "dremio:query")
        
        return {"message": f"Successfully ingested {count} records from Dremio", "count": count}
    
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Dremio error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
