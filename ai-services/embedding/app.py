"""
Embedding Service - Convert text to vector embeddings
Using sentence-transformers (all-MiniLM-L6-v2 model)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
import os

app = FastAPI(
    title="Embedding Service",
    description="Text to vector embedding service",
    version="1.0.0"
)

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
model = None

@app.on_event("startup")
def load_model():
    """Load the embedding model on startup"""
    global model
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded successfully. Dimension: {model.get_sentence_embedding_dimension()}")

class EmbedRequest(BaseModel):
    texts: List[str]

@app.get("/")
def root():
    return {
        "service": "Embedding Service",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "status": "healthy"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "embedding-service",
        "model_loaded": model is not None
    }

@app.get("/model/info")
def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_name": MODEL_NAME,
        "dimensions": model.get_sentence_embedding_dimension(),
        "max_seq_length": model.max_seq_length
    }

@app.post("/embed")
def embed_texts(request: EmbedRequest):
    """Convert texts to embeddings"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    try:
        embeddings = model.encode(request.texts, convert_to_numpy=True)
        return {
            "embeddings": embeddings.tolist(),
            "model": MODEL_NAME,
            "dimensions": model.get_sentence_embedding_dimension(),
            "count": len(request.texts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
