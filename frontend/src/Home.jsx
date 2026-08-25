import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./index.css";

function Home() {
  const [symbol, setSymbol] = useState("BTC-USDT");
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(false);

  // RAG Search State'leri
  const [ragQuery, setRagQuery] = useState("");
  const [ragResults, setRagResults] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  const navigate = useNavigate();

  // 1. TAHMİN ÇALIŞTIRMA (PREDICT)
  const runPrediction = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/ml/predict?symbol=${symbol}`);
      const data = await res.json();
      if (res.ok) {
        setPredictionData(data);
      } else {
        alert(data.detail || "Prediction error");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-6 container">
      {/* ÜST BAR */}
      <div className="container-top flex justify-between items-center">
        <h1 className="text-xl font-semibold">Crypto AI Systems Engine</h1>

        <div className="flex gap-2">
          <button className="login" onClick={() => navigate("/login")}>
            Login
          </button>
          <button className="signup" onClick={() => navigate("/signup")}>
            Signup
          </button>
        </div>
      </div>

      {/* TAHMİN FORMU */}
      <div className="container-bottom space-y-2">
        <h2>Crypto Symbol</h2>

        <input
          className="p-2 border rounded-xl w-full"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="e.g. BTC-USDT"
        />

        <button
          className="p-2 bg-blue-600 text-white rounded-xl result w-full"
          onClick={runPrediction}
          disabled={loading}
        >
          {loading ? "Analyzing Models..." : "Run AI Prediction"}
        </button>
      </div>

      {/* TAHMİN SONUÇLARI VE GRAFİK */}
      {predictionData && (
        <div className="mt-4 p-4 border rounded-xl space-y-3 bg-gray-50">
          <div className="flex justify-between text-sm font-medium">
            <span>Algorithm: <strong>{predictionData.algorithm}</strong></span>
            <span>Next Day Target: <strong>${predictionData.predicted_next_day?.toFixed(2)}</strong></span>
          </div>

          <img
            src={`${API_BASE_URL}${predictionData.graph}`}
            alt="Prediction Chart"
            className="rounded-xl w-full border"
          />
        </div>
      )}

    </div>
  );
}

export default Home;