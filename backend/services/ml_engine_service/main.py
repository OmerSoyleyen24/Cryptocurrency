import os
import uuid
import requests
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import talib
import msgspec
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Input, Flatten, Dropout
import mlflow
import mlflow.keras
from kafka import KafkaProducer

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
load_dotenv()
matplotlib.use('Agg')

app = FastAPI(title="AI/ML Forecasting Engine", version="1.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_DIR = os.path.join(BASE_DIR, "graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)
app.mount("/graph", StaticFiles(directory=GRAPH_DIR), name="graph")

# MLflow
MLRUNS_DIR = os.path.join(BASE_DIR, "mlruns").replace("\\", "/")
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", f"file:///{MLRUNS_DIR}"))
mlflow.set_experiment("Crypto_Time_Series_Forecasting")

# Kafka
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
try:
    kafka_producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: msgspec.json.encode(v)
    )
except Exception:
    kafka_producer = None

def send_to_kafka(topic: str, data: dict):
    if kafka_producer:
        try:
            kafka_producer.send(topic, data)
        except Exception as e:
            print(f"Kafka Send Error: {e}")

# Model Builders
def build_lstm(input_shape, future_days):
    m = Sequential([Input(shape=input_shape), LSTM(64, return_sequences=True), Dropout(0.2), LSTM(32), Dropout(0.2), Dense(future_days)])
    m.compile(optimizer="adam", loss="mse")
    return m

def build_gru(input_shape, future_days):
    m = Sequential([Input(shape=input_shape), GRU(64, return_sequences=True), Dropout(0.2), GRU(32), Dropout(0.2), Dense(future_days)])
    m.compile(optimizer="adam", loss="mse")
    return m

def build_dense(input_shape, future_days):
    m = Sequential([Input(shape=input_shape), Flatten(), Dense(64, activation='relu'), Dropout(0.2), Dense(future_days)])
    m.compile(optimizer="adam", loss="mse")
    return m

@app.get("/predict")
def predict(
    background_tasks: BackgroundTasks,
    symbol: str = Query(..., description="Sembol: BTC-USDT"),
    lookback: int = Query(30),
    future_days: int = Query(15)
):
    try:
        fetch_limit = min(1500, max(1000, lookback * 5))
        url = f"https://api.kucoin.com/api/v1/market/candles?type=1day&symbol={symbol}&limit={fetch_limit}"
        r = requests.get(url)
        raw_data = r.json().get("data")
        if not raw_data:
            raise HTTPException(status_code=400, detail="Veri çekilemedi")

        df = pd.DataFrame(raw_data, columns=["time","open","close","high","low","volume","turnover"])
        df["time"] = pd.to_datetime(df["time"].astype(int), unit="s")
        df = df.astype({"open":float, "close":float, "high":float, "low":float, "volume":float})
        df = df.sort_values("time", ascending=True).reset_index(drop=True)

        # Technical Indicators
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

        X, y = [], []
        for i in range(lookback, len(scaled_data) - future_days + 1):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i:i+future_days, 3])
        X, y = np.array(X), np.array(y)

        input_shape = (X.shape[1], X.shape[2])
        model_pool = {
            "LSTM": build_lstm(input_shape, future_days),
            "GRU": build_gru(input_shape, future_days),
            "Dense": build_dense(input_shape, future_days)
        }

        best_model, best_name, min_loss = None, "", float('inf')
        for name, model_obj in model_pool.items():
            hist = model_obj.fit(X, y, epochs=30, batch_size=32, verbose=0, validation_split=0.1)
            v_loss = hist.history['val_loss'][-1]
            if v_loss < min_loss:
                min_loss, best_model, best_name = v_loss, model_obj, name

        curr_batch = scaled_data[-lookback:].reshape((1, lookback, len(features)))
        future_preds_scaled = best_model.predict(curr_batch, verbose=0)[0]
        final_preds = p_scaler.inverse_transform(future_preds_scaled.reshape(-1, 1)).flatten()

        # MLflow Logging
        with mlflow.start_run(run_name=f"Pred_{symbol}"):
            mlflow.log_param("symbol", symbol)
            mlflow.log_param("selected_model", best_name)
            mlflow.log_metric("val_loss", float(min_loss))
            mlflow.log_metric("next_day_price", float(final_preds[0]))

        # Graph Generation
        img_id = f"{uuid.uuid4()}.png"
        save_path = os.path.join(GRAPH_DIR, img_id)
        plt.figure(figsize=(10, 5))
        past_dates = df["time"].tail(lookback).reset_index(drop=True)
        past_closes = df["close"].tail(lookback).reset_index(drop=True)
        future_dates = [past_dates.iloc[-1] + pd.Timedelta(days=i) for i in range(1, future_days + 1)]

        plt.plot(past_dates, past_closes, label="Real Past", color="blue", lw=2)
        plt.plot(future_dates, final_preds, label=f"AI Forecast ({best_name})", color="red", ls="--", marker="o")
        plt.title(f"{symbol} Price Prediction ({best_name})")
        plt.grid(True, alpha=0.3)
        plt.savefig(save_path)
        plt.close()

        # Kafka Event Dispatch
        predict_payload = {
            "graph": img_id, "symbol": symbol, "algorithm": best_name,
            "val_loss": float(min_loss), "predicted_price": float(final_preds[0])
        }
        background_tasks.add_task(send_to_kafka, "prediction_logs", predict_payload)

        return {
            "symbol": symbol, "algorithm": best_name,
            "val_loss": float(min_loss), "predicted_next_day": float(final_preds[0]),
            "graph": f"/graph/{img_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)