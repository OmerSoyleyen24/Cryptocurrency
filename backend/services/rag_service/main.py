import os
import msgspec
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG Intelligence Service", version="1.0")

class RAGQuerySchema(msgspec.Struct):
    query: str
    top_k: int = 3

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
qdrant_client = QdrantClient(":memory:")
COLLECTION_NAME = "crypto_market_insights"

try:
    collections = [c.name for c in qdrant_client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
except Exception as e:
    print(f"Qdrant Error: {e}")

@app.post("/search")
async def rag_search(request: Request):
    try:
        body = await request.body()
        payload = msgspec.json.decode(body, type=RAGQuerySchema)
        
        dummy_vector = np.random.rand(384).tolist()
        
        search_result = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=dummy_vector,
            limit=payload.top_k
        )
        return {"query": payload.query, "results": search_result.points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)