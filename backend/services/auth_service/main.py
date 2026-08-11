import os
import msgspec
from fastapi import FastAPI, HTTPException, Request
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Auth Microservice", version="1.0")

class UserAuthSchema(msgspec.Struct):
    username: str
    password: str

# MySQL Pool
db_host = os.getenv("DB_HOST", "127.0.0.1")
dbconfig = {
    "host": str(db_host).strip(),
    "user": str(os.getenv("DB_USER", "root")).strip(),
    "password": str(os.getenv("DB_PASS", "BnYnMySQLHspActm26a")).strip(),
    "database": str(os.getenv("DB_NAME", "Cryptocurrency")).strip(),
    "port": int(os.getenv("DB_PORT", 3306))
}
cnxpool = pooling.MySQLConnectionPool(pool_name="auth_pool", pool_size=3, **dbconfig)

def get_db():
    return cnxpool.get_connection()

@app.post("/signup", status_code=201)
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

@app.post("/login")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)