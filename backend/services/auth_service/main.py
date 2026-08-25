import os
import msgspec
from fastapi import FastAPI, HTTPException, Request
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Auth Microservice", version="1.0")

class UserAuthSchema(msgspec.Struct):
    username: str
    password: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React Vite frontend'ine izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],  # GET, PUT, POST dahil tüm metotlara izin ver
    allow_headers=["*"],  # Tüm başlıklara izin ver
)

# MySQL Pool Ayarları
db_host = os.getenv("DB_HOST", "127.0.0.1")
dbconfig = {
    "host": str(db_host).strip(),
    "user": str(os.getenv("DB_USER")).strip(),
    "password": str(os.getenv("DB_PASS")).strip(),
    "database": str(os.getenv("DB_NAME")).strip(),
    "port": int(os.getenv("DB_PORT"))
}
cnxpool = pooling.MySQLConnectionPool(pool_name="auth_pool", pool_size=3, **dbconfig)

def get_db():
    return cnxpool.get_connection()

@app.post("/api/auth/signup", status_code=201)
async def signup(request: Request):
    body = await request.body()
    user = msgspec.json.decode(body, type=UserAuthSchema)
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username=%s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Kullanıcı zaten var")
        
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s,%s)",
            (user.username, generate_password_hash(user.password))
        )
        conn.commit()
        return {"msg": "Kayıt başarılı"}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/auth/login")
async def login(request: Request):
    body = await request.body()
    user = msgspec.json.decode(body, type=UserAuthSchema)
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT password FROM users WHERE username=%s", (user.username,))
        row = cursor.fetchone()
        if row and check_password_hash(row['password'], user.password):
            return {"msg": "Giriş başarılı"}
        raise HTTPException(status_code=401, detail="Geçersiz bilgiler")
    finally:
        cursor.close()
        conn.close()

@app.get("/api/auth/users/{username}/cryptos")
async def get_user_cryptos(username: str):
    # Kullanıcının kripto listesini getiren uç nokta
    return {"username": username, "cryptos": []}

@app.put("/api/auth/users/{username}/update-cryptos")
async def update_user_cryptos(username: str, request: Request):
    # Kullanıcının kripto listesini güncelleyen uç nokta
    body = await request.json()
    return {"msg": f"{username} için kriptolar güncellendi", "data": body}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)