import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./index.css";

function MyCryptocurrency() {
  const { username } = useParams();
  const navigate = useNavigate();
  const [cryptos, setCryptos] = useState([]);

  // RAG Search State'leri
  const [ragQuery, setRagQuery] = useState("");
  const [ragResults, setRagResults] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  const handleLogout = () => {
    localStorage.clear(); 
    navigate("/login");
  };

  // KULLANICI VERİLERİNİ ÇEKME (Auth Service - Gateway Port 8000)
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/auth/users/${username}/cryptos`);
        const data = await res.json(); 
        if (Array.isArray(data)) {
          const formatted = data.map((sym, index) => ({
            id: Date.now() + index,
            symbol: sym,
            imageUrl: null,
            predictionInfo: null,
            loading: false,
            lookback: 30,
            futureDays: 15
          }));
          setCryptos(formatted);
        }
      } catch (err) { 
        console.error("Yükleme hatası:", err); 
      }
    };
    if (username) fetchUserData();
  }, [username]);

  // VERİTABANINA KAYDETME (Auth Service - Gateway Port 8000)
  const saveToDb = async (listToSave) => {
    const targetList = listToSave || cryptos;
    const symbolsOnly = targetList.map(c => c.symbol).filter(s => s.trim() !== "");
    try {
      await fetch(`http://localhost:8000/api/auth/users/${username}/update-cryptos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ types: symbolsOnly })
      });
    } catch (err) { 
      console.error("Kayıt hatası:", err); 
    }
  };

  const addCrypto = () => {
    setCryptos([...cryptos, { 
      id: Date.now(), 
      symbol: "", 
      imageUrl: null, 
      predictionInfo: null,
      loading: false, 
      lookback: 30, 
      futureDays: 15 
    }]);
  };

  const removeCrypto = (id) => {
    const newList = cryptos.filter(c => c.id !== id);
    setCryptos(newList);
    saveToDb(newList);
  };

  const handleUpdate = (id, field, value) => {
    setCryptos(prev => prev.map(c => 
      c.id === id ? { ...c, [field]: field === "symbol" ? value.toUpperCase() : value } : c
    ));
  };

  // 1. TAHMİN ÇALIŞTIRMA (ML Engine - Gateway Port 8000)
  const runPrediction = async (id) => {
    const target = cryptos.find(c => c.id === id);
    if (!target.symbol) return;

    setCryptos(prev => prev.map(c => c.id === id ? { ...c, loading: true } : c));

    try {
      const query = `symbol=${target.symbol}&lookback=${target.lookback}&future_days=${target.futureDays}`;
      const res = await fetch(`http://localhost:8000/api/ml/predict?${query}`);
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Tahmin hesaplanamadı");

      setCryptos(prev => prev.map(c => 
        c.id === id ? { 
          ...c, 
          // Grafik görseli Gateway üzerinden sunulur
          imageUrl: `http://localhost:8000/api/ml${data.graph}`,          
          predictionInfo: {
            algorithm: data.algorithm,
            valLoss: data.val_loss,
            nextDayPrice: data.predicted_next_day
          },
          loading: false 
        } : c
      ));
    } catch (err) {
      setCryptos(prev => prev.map(c => c.id === id ? { ...c, loading: false } : c));
      alert("Hata: " + err.message);
    }
  };

  // 2. RAG VEKTÖR ARAMASI (RAG News Service - Gateway Port 8000)
  const runRagSearch = async () => {
    if (!ragQuery.trim()) return;
    setRagLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/rag/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: ragQuery, top_k: 3 }),
      });
      const data = await res.json();
      if (res.ok) {
        setRagResults(data.results);
      } else {
        alert(data.detail || "Search failed");
      }
    } catch (err) {
      console.error(err);
      alert("Error connecting to RAG search service");
    } finally {
      setRagLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-4 container">
      {/* ÜST BAR */}
      <div className="container-top flex justify-between items-center border-b pb-3">
        <h1 className="text-xl font-semibold">My Cryptocurrency ({username})</h1>
        <button 
          onClick={handleLogout}
          style={{
            backgroundColor: 'transparent',
            color: '#ff4d4d',
            border: '1px solid #ff4d4d',
            borderRadius: '8px',
            padding: '5px 12px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#fff5f5'}
          onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
        >
          Logout
        </button>
      </div>

      {/* RAG SEARCH SECTION */}
      <div style={{ borderBottom: '1px solid #eee', paddingBottom: '20px', marginTop: '15px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '8px' }}>
          Market Insight Search (RAG Engine)
        </h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            style={{ flex: 1, padding: '8px', border: '1px solid #ddd', borderRadius: '8px', fontSize: '13px' }}
            value={ragQuery}
            onChange={(e) => setRagQuery(e.target.value)}
            placeholder="Ask about crypto news or trends (e.g., BTC halving effects)..."
          />
          <button
            style={{ backgroundColor: '#7c3aed', color: 'white', padding: '8px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '13px' }}
            onClick={runRagSearch}
            disabled={ragLoading}
          >
            {ragLoading ? "..." : "Search"}
          </button>
        </div>

        {ragResults && (
          <div style={{ backgroundColor: '#f3e8ff', padding: '10px', borderRadius: '8px', marginTop: '10px', fontSize: '12px' }}>
            <p style={{ fontWeight: '600', color: '#581c87', marginBottom: '4px' }}>Vector Search Results:</p>
            <pre style={{ backgroundColor: '#fff', padding: '8px', borderRadius: '6px', border: '1px solid #e9d5ff', overflowX: 'auto' }}>
              {JSON.stringify(ragResults, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* TAKİP EDİLEN KRİPTOLAR */}
      <div className="container-bottom space-y-4">
        <h2>Followed Cryptos</h2>

        {cryptos.map((crypto) => (
          <div key={crypto.id} className="space-y-2" style={{ marginBottom: '30px', borderBottom: '1px solid #eee', paddingBottom: '20px' }}>
            
            {/* Sembol Input */}
            <input
              className="p-2 border rounded-xl w-full"
              value={crypto.symbol}
              onChange={(e) => handleUpdate(crypto.id, "symbol", e.target.value)}
              onBlur={() => saveToDb()} 
              placeholder="BTC-USDT"
            />

            {/* Parametre Inputları */}
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: '11px', color: '#666', display: 'block' }}>Analiz Gün (Lookback)</label>
                <input
                  type="number"
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '8px' }}
                  value={crypto.lookback}
                  onChange={(e) => handleUpdate(crypto.id, "lookback", e.target.value)}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: '11px', color: '#666', display: 'block' }}>Tahmin Gün (Future Days)</label>
                <input
                  type="number"
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '8px' }}
                  value={crypto.futureDays}
                  onChange={(e) => handleUpdate(crypto.id, "futureDays", e.target.value)}
                />
              </div>
            </div>
            
            <button
              className="p-2 bg-blue-600 text-white rounded-xl result w-full"
              style={{ marginTop: '10px' }}
              onClick={() => runPrediction(crypto.id)}
              disabled={crypto.loading || !crypto.symbol}
            >
              {crypto.loading ? "Analyzing Neural Networks..." : "Run AI Guess"}
            </button>

            <button 
              onClick={() => removeCrypto(crypto.id)}
              style={{ color: 'red', background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'center', fontSize: '14px', marginTop: '5px' }}
            >
              Remove this crypto
            </button>

            {/* TAHMİN SONUCU BİLGİLERİ VE GRAFİK */}
            {crypto.predictionInfo && (
              <div style={{ backgroundColor: '#f8fafc', padding: '10px', borderRadius: '8px', marginTop: '10px', fontSize: '12px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Selected Model: <strong>{crypto.predictionInfo.algorithm}</strong></span>
                  <span>Validation Loss: <strong>{crypto.predictionInfo.valLoss?.toFixed(5)}</strong></span>
                </div>
                <div>
                  Next Day Target Price: <strong style={{ color: '#2563eb' }}>${crypto.predictionInfo.nextDayPrice?.toFixed(2)}</strong>
                </div>
              </div>
            )}

            {crypto.imageUrl && (
              <div className="mt-2">
                <img 
                  src={crypto.imageUrl} 
                  alt={`${crypto.symbol} Forecast Chart`} 
                  className="rounded-xl w-full" 
                  style={{ borderRadius: '12px', marginTop: '10px' }} 
                />
              </div>
            )}
          </div>
        ))}

        <button 
          className="p-2 bg-green-600 text-white rounded-xl w-full" 
          onClick={addCrypto}
          style={{ backgroundColor: '#16a34a', color: 'white', padding: '10px', borderRadius: '12px', border: 'none', width: '100%', cursor: 'pointer' }}
        >
          + Add another crypto
        </button>
      </div>
    </div>
  );
}

export default MyCryptocurrency;