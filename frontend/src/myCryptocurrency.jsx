import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./index.css";

function MyCryptocurrency() {
  const { username } = useParams();
  const navigate = useNavigate();
  const [cryptos, setCryptos] = useState([]);

  const handleLogout = () => {
    localStorage.clear(); 
    navigate("/login");
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const res = await fetch(`https://cryptocurrency-production.up.railway.app/users/${username}/cryptos`);
        const data = await res.json(); 
        if (Array.isArray(data)) {
          const formatted = data.map((sym, index) => ({
            id: Date.now() + index,
            symbol: sym,
            imageUrl: null,
            loading: false,
            lookback: 30,
            futureDays: 15
          }));
          setCryptos(formatted);
        }
      } catch (err) { console.error("Yükleme hatası:", err); }
    };
    if (username) fetchUserData();
  }, [username]);

  const saveToDb = async (listToSave) => {
    const targetList = listToSave || cryptos;
    const symbolsOnly = targetList.map(c => c.symbol).filter(s => s.trim() !== "");
    try {
      await fetch(`https://cryptocurrency-production.up.railway.app/users/${username}/update-cryptos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ types: symbolsOnly })
      });
    } catch (err) { console.error("Kayıt hatası:", err); }
  };

  const addCrypto = () => {
    setCryptos([...cryptos, { 
      id: Date.now(), 
      symbol: "", 
      imageUrl: null, 
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

  const runPrediction = async (id) => {
    const target = cryptos.find(c => c.id === id);
    if (!target.symbol) return;
    setCryptos(prev => prev.map(c => c.id === id ? { ...c, loading: true } : c));

    try {
      const query = `symbol=${target.symbol}&lookback=${target.lookback}&future_days=${target.futureDays}`;
      const res = await fetch(`https://cryptocurrency-production.up.railway.app/predict?${query}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      setCryptos(prev => prev.map(c => 
        c.id === id ? { ...c, imageUrl: data.graph, loading: false } : c
      ));
    } catch (err) {
      setCryptos(prev => prev.map(c => c.id === id ? { ...c, loading: false } : c));
      alert("Hata: " + err.message);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-4 container">
      {/* ÜST KISIM: Eski Tasarım */}
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

            {/* Yeni Eklenen Parametre Inputları (Eski Stile Uygun) */}
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: '11px', color: '#666', display: 'block' }}>Analiz Gün</label>
                <input
                  type="number"
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '8px' }}
                  value={crypto.lookback}
                  onChange={(e) => handleUpdate(crypto.id, "lookback", e.target.value)}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: '11px', color: '#666', display: 'block' }}>Tahmin Gün</label>
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
              {crypto.loading ? "Loading..." : "Run guess"}
            </button>

            <button 
              onClick={() => removeCrypto(crypto.id)}
              style={{ color: 'red', background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'center', fontSize: '14px', marginTop: '5px' }}
            >
              Remove this crypto
            </button>

            {crypto.imageUrl && (
              <div className="mt-2">
                <img src={crypto.imageUrl} alt="Graph" className="rounded-xl w-full" style={{ borderRadius: '12px', marginTop: '10px' }} />
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
