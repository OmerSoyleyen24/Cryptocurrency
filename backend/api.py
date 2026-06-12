import os
import uuid
import json
import requests
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import talib
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Input, Flatten, Dropout

# Load .env file
load_dotenv()

# CRITICAL: Prevent GUI errors on Render (Linux) servers
matplotlib.use('Agg') 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
CORS(app, resources={r"/*": {
    "origins": ["https://omersoyleyen-cryptocurrency.netlify.app"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_DIR = os.path.join(os.getcwd(), "graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)

# MySQL Connection Pool
cnxpool = None
try:
    db_host = os.getenv("DB_HOST")
    if db_host:
        try:
            db_port = int(os.getenv("DB_PORT", 3306))
        except:
            db_port = 3306

        dbconfig = {
            "host": str(db_host).strip(),
            "user": str(os.getenv("DB_USER")).strip(),
            "password": str(os.getenv("DB_PASS")).strip(),
            "database": str(os.getenv("DB_NAME")).strip(),
            "port": db_port
        }
        
        # use_pure=True: Eliminates C dependencies, ensures Python 3.12 compatibility.
        # pool_size=2: Prevents 'Max Connections' overflow error on Clever-Cloud.
        cnxpool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=2,
            use_pure=True,
            **dbconfig
        )
        print("✅ Database connection pool created successfully.")
    else:
        print("❌ ERROR: DB_HOST environment variable is missing!")
except Exception as e:
    print(f"❌ Database pool initialization failed: {str(e)}")

# Get database connection from the pool
def get_db_connection():
    global cnxpool
    if cnxpool is None:
        # Retry connection if the server was temporarily down
        try:
            db_port = int(os.getenv("DB_PORT", 3306))
            dbconfig = {
                "host": str(os.getenv("DB_HOST")).strip(),
                "user": str(os.getenv("DB_USER")).strip(),
                "password": str(os.getenv("DB_PASS")).strip(),
                "database": str(os.getenv("DB_NAME")).strip(),
                "port": db_port
            }
            cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=2, use_pure=True, **dbconfig)
            return cnxpool.get_connection()
        except Exception as retry_error:
            raise Exception(f"Database Pool is None. Real crash reason: {str(retry_error)}")
    return cnxpool.get_connection()

# ---------------------------
# Graph Service Route
# ---------------------------
@app.route('/graph/<filename>')
def serve_graph(filename):
    return send_from_directory(GRAPH_DIR, filename)

# ---------------------------
# AUTH & USER ROUTES
# ---------------------------

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")
    if not username or not password: return jsonify({"error": "Missing info"}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone(): return jsonify({"error": "User already exists"}), 400
        
        cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", 
                       (username, generate_password_hash(password)))
        conn.commit()
        return jsonify({"msg": "Registration successful"}), 201
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE username=%s", (data.get("username"),))
        row = cursor.fetchone()
        if row and check_password_hash(row['password'], data.get("password")):
            return jsonify({"msg": "Login successful"}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/users/<username>/cryptos", methods=["GET"])
def get_user_cryptos(username):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT types FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        if row and row['types']:
            val = row['types']
            return jsonify(json.loads(val) if isinstance(val, str) else val)
        return jsonify([])
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/users/<username>/update-cryptos", methods=["POST"])
def update_user_cryptos(username):
    data = request.get_json()
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET types=%s WHERE username=%s", (json.dumps(data.get("types", [])), username))
        conn.commit()
        return jsonify({"msg": "Updated successfully"}), 200
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------------------------
# MODELS (Dynamic Multi-Step)
# ---------------------------

def build_lstm(input_shape, future_days):
    m = Sequential([
        Input(shape=input_shape), 
        LSTM(64, return_sequences=True), 
        Dropout(0.2), 
        LSTM(32), 
        Dropout(0.2), 
        Dense(future_days)
    ])
    m.compile(optimizer="adam", loss="mse")
    return m

def build_gru(input_shape, future_days):
    m = Sequential([
        Input(shape=input_shape), 
        GRU(64, return_sequences=True), 
        Dropout(0.2), 
        GRU(32), 
        Dropout(0.2), 
        Dense(future_days)
    ])
    m.compile(optimizer="adam", loss="mse")
    return m

def build_dense(input_shape, future_days):
    m = Sequential([
        Input(shape=input_shape), 
        Flatten(), 
        Dense(64, activation='relu'), 
        Dropout(0.2), 
        Dense(future_days)
    ])
    m.compile(optimizer="adam", loss="mse")
    return m

# ---------------------------
# PREDICT ROUTE
# ---------------------------

@app.route("/predict")
def predict():
    symbol = request.args.get("symbol")
    try:
        lookback = int(request.args.get("lookback", 30))
        future_days = int(request.args.get("future_days", 15))
    except (ValueError, TypeError):
        lookback, future_days = 30, 15

    if not symbol: 
        return jsonify({"error": "Symbol is required"}), 400

    try:
        # 1. FETCH DATA
        fetch_limit = min(1500, max(1000, lookback * 5)) 
        url = f"https://api.kucoin.com/api/v1/market/candles?type=1day&symbol={symbol}&limit={fetch_limit}"
        r = requests.get(url)
        raw_data = r.json().get("data")
        
        if not raw_data:
            return jsonify({"error": "Data could not be fetched"}), 400

        df = pd.DataFrame(raw_data, columns=["time","open","close","high","low","volume","turnover"])
        df["time"] = pd.to_datetime(df["time"].astype(int), unit="s")
        df = df.astype({"open":float, "close":float, "high":float, "low":float, "volume":float})
        df = df.sort_values("time", ascending=True).reset_index(drop=True)

        # 2. TECHNICAL ANALYSIS
        df["MA10"] = talib.SMA(df["close"], 10)
        df["MA20"] = talib.SMA(df["close"], 20)
        df["RSI"] = talib.RSI(df["close"], 14)
        df["MACD"], _, _ = talib.MACD(df["close"])
        df["MFI"] = talib.MFI(df["high"], df["low"], df["close"], df["volume"], timeperiod=14)
        df["CCI"] = talib.CCI(df["high"], df["low"], df["close"], timeperiod=14)
        df["AROON_UP"], df["AROON_DOWN"] = talib.AROON(df["high"], df["low"], timeperiod=14)
        df["TRIX"] = talib.TRIX(df["close"], timeperiod=15)
        
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        features = ["open", "high", "low", "close", "volume", "MA10", "MA20", "RSI", "MACD", "MFI", "CCI", "AROON_UP", "AROON_DOWN", "TRIX"]
        
        f_scaler = MinMaxScaler()
        scaled_data = f_scaler.fit_transform(df[features])
        p_scaler = MinMaxScaler()
        p_scaler.fit(df[["close"]])

        # 3. PREPARE DATASET (Direct multi-step forecasting target)
        X, y = [], []
        for i in range(lookback, len(scaled_data) - future_days + 1):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i:i+future_days, 3]) 
        X, y = np.array(X), np.array(y)

        if len(X) == 0: return jsonify({"error": "Insufficient data"}), 400

        # Build models with dynamic input shape
        input_shape = (X.shape[1], X.shape[2])
        model_pool = {
            "LSTM": build_lstm(input_shape, future_days), 
            "GRU": build_gru(input_shape, future_days), 
            "Dense": build_dense(input_shape, future_days)
        }
        
        best_model, best_name, min_loss = None, "", float('inf')

        for name, model_obj in model_pool.items():
            hist = model_obj.fit(X, y, epochs=50, batch_size=32, verbose=0, validation_split=0.1)
            v_loss = hist.history['val_loss'][-1]
            if v_loss < min_loss:
                min_loss, best_model, best_name = v_loss, model_obj, name

        # 4. PREDICTION
        curr_batch = scaled_data[-lookback:].reshape((1, lookback, len(features)))
        future_preds_scaled = best_model.predict(curr_batch, verbose=0)[0]
        
        # 5. INVERSE SCALING
        final_preds = p_scaler.inverse_transform(future_preds_scaled.reshape(-1, 1)).flatten()

        # 6. PLOTTING
        img_id = f"{uuid.uuid4()}.png"
        save_path = os.path.join(GRAPH_DIR, img_id)

        plt.figure(figsize=(10, 5))
        past_dates = df["time"].tail(lookback).reset_index(drop=True)
        past_closes = df["close"].tail(lookback).reset_index(drop=True)
        
        real_last_date = past_dates.iloc[-1]
        future_dates = [real_last_date + pd.Timedelta(days=i) for i in range(1, future_days + 1)]
        
        plt.plot(past_dates, past_closes, label="Real Past", color="blue", lw=2)
        plt.plot(future_dates, final_preds, label=f"AI Forecast ({best_name})", color="red", ls="--", marker="o", ms=4)
        
        plt.title(f"{symbol} Price Prediction Projection ({best_name})")
        plt.xlabel("Date")
        plt.ylabel("Price (USDT)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gcf().autofmt_xdate() 
        plt.savefig(save_path)
        plt.close()

        return jsonify({
            "symbol": symbol,
            "algorithm": best_name,
            "val_loss": float(min_loss),
            "predicted_next_day": float(final_preds[0]),
            "graph": f"{request.host_url.rstrip('/')}/graph/{img_id}"
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
