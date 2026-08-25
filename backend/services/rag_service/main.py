import os
import httpx
import msgspec
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG Intelligence Service", version="1.0")

# CORS İzinleri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RAGQuerySchema(msgspec.Struct):
    query: str
    top_k: int = 3

qdrant_client = QdrantClient(location=":memory:")
COLLECTION_NAME = "crypto_market_insights"

# İnternetten canlı kripto verilerini çekip Qdrant'a yükleyen fonksiyon
async def fetch_and_store_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,  # Daha fazla coin (BTC, ETH vb. rahat bulunsun diye 50 yaptık)
            "page": 1,
            "sparkline": "false"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            if response.status_code == 200:
                coins = response.json()
                points = []
                
                for idx, coin in enumerate(coins):
                    name = coin.get("name")
                    symbol = coin.get("symbol", "").upper()
                    price = coin.get("current_price", 0) or 0.0
                    change = coin.get("price_change_percentage_24h", 0) or 0.0
                    market_cap = coin.get("market_cap", 0) or 0
                    
                    text_content = (
                        f"Cryptocurrency: {name} ({symbol}). "
                        f"Current Price: ${price:,.2f} USD. "
                        f"24h Price Change: {change:.2f}%. "
                        f"Market Capitalization: ${market_cap:,.0f}."
                    )
                    
                    vector = np.random.rand(384).tolist()
                    
                    points.append(
                        PointStruct(
                            id=idx + 1,
                            vector=vector,
                            payload={
                                "text": text_content, 
                                "symbol": symbol, 
                                "name": name
                            }
                        )
                    )
                
                collections = [c.name for c in qdrant_client.get_collections().collections]
                if COLLECTION_NAME not in collections:
                    qdrant_client.create_collection(
                        collection_name=COLLECTION_NAME,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                    )
                
                qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
                print(f"Başarılı: {len(points)} adet canlı kripto verisi yüklendi!")
            else:
                print("API'den veri alınamadı.")
    except Exception as e:
        print(f"Canlı Veri Çekme Hatası: {e}")

@app.on_event("startup")
async def startup_event():
    await fetch_and_store_crypto_data()

@app.post("/api/rag/search")
async def rag_search(request: Request):
    try:
        body = await request.body()
        payload = msgspec.json.decode(body, type=RAGQuerySchema)
        
        user_query = payload.query.strip().upper()
        dummy_vector = np.random.rand(384).tolist()
        
        # Kullanıcının yazdığı ifade ile eşleşen (symbol veya name içinde geçen) kayıtları filtreleyelim
        # Eğer kullanıcı sembol yazdıysa (örn: BTC) doğrudan payload filtresi kuruyoruz
        search_filter = None
        if user_query:
            # Sembol veya İsim eşleşmesi için Qdrant filtresi (Oto-algılama)
            search_filter = Filter(
                should=[
                    FieldCondition(key="symbol", match=MatchValue(value=user_query)),
                    FieldCondition(key="name", match=MatchValue(value=payload.query.strip()))
                ]
            )

        try:
            # Önce filtreli arama deneriz
            search_result = qdrant_client.search(
                collection_name=COLLECTION_NAME,
                query_vector=dummy_vector,
                query_filter=search_filter,
                limit=payload.top_k,
                with_payload=True
            )
            
            # Eğer filtreyle eşleşen hiç bulamazsa, filtresiz genel arama yapar ki boş dönmesin
            if not search_result:
                search_result = qdrant_client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=dummy_vector,
                    limit=payload.top_k,
                    with_payload=True
                )

            formatted_results = [
                {"id": point.id, "score": point.score, "payload": point.payload}
                for point in search_result
            ]
        except AttributeError:
            # Alternatif qdrant-client sürümleri için fallback
            search_result = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=dummy_vector,
                query_filter=search_filter,
                limit=payload.top_k,
                with_payload=True
            )
            formatted_results = [
                {"id": point.id, "score": point.score, "payload": point.payload}
                for point in search_result.points
            ]
        
        return {"query": payload.query, "results": formatted_results}
    except Exception as e:
        print(f"Arama Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)