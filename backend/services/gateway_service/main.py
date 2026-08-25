import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Gateway", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "auth": "http://127.0.0.1:8001",
    "ml": "http://127.0.0.1:8002",
    "rag": "http://127.0.0.1:8003"
}

client = httpx.AsyncClient()

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(request: Request, path: str):
    # request.url.path kullanarak /api/auth/login yolunu direkt koruyoruz
    query_str = f"?{request.query_params}" if request.query_params else ""
    url = f"{SERVICES['auth']}{request.url.path}{query_str}"
    
    print("--- PROXY TEST (AUTH) ---")
    print(f"Gelen Yol: {request.url.path}")
    print(f"Hedef URL: {url}")
    
    return await proxy_request(request, url)

@app.api_route("/api/ml/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def ml_proxy(request: Request, path: str):
    query_str = f"?{request.query_params}" if request.query_params else ""
    url = f"{SERVICES['ml']}{request.url.path}{query_str}"
    return await proxy_request(request, url)

@app.api_route("/api/rag/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def rag_proxy(request: Request, path: str):
    query_str = f"?{request.query_params}" if request.query_params else ""
    url = f"{SERVICES['rag']}{request.url.path}{query_str}"
    return await proxy_request(request, url)

async def proxy_request(request: Request, url: str):
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    try:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)