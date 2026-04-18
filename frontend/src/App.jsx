import React, { useState, useEffect } from 'react';
import SignalFeed from './components/SignalFeed';
import LeadManagement from './components/LeadManagement';
import DealList from './components/DealList';
import DecisionView from './components/DecisionView';
import { Layout, Compass, Zap, RefreshCcw, Briefcase } from 'lucide-react';

function App() {
  const [viewMode, setViewMode] = useState('pipeline'); // pipeline, market
  const [signals, setSignals] = useState([]);
  const [deals, setDeals] = useState([]);
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch Signals
      const sigRes = await fetch('http://localhost:8000/api/signals');
      const sigData = await sigRes.json();
      setSignals(sigData);

      // Fetch Deals
      const dealRes = await fetch('http://localhost:8000/api/deals');
      const dealData = await dealRes.json();
      setDeals(dealData);
      
      if (selectedDeal) {
        const updated = dealData.find(d => d._id === selectedDeal._id);
        if (updated) setSelectedDeal(updated);
      }
    } catch (e) {
      console.error("Neural sync failed", e);
    }
    setLoading(false);
  };

  const handleConvertToDeal = async (leadId) => {
    try {
      const res = await fetch('http://localhost:8000/api/deals/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_id: leadId })
      });
      if (res.ok) {
        await fetchData();
        setViewMode('pipeline');
        alert("Lead successfully promoted to ACTIVE pipeline.");
      }
    } catch (e) {
      console.error("Conversion failed", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-shell">
      {/* SIDEBAR NAVIGATION */}
      <nav className="sidebar-nav">
        <div className="nav-brand" style={{ fontSize: '1.5rem', fontWeight: 900 }}>B</div>
        
        <div 
          className={`nav-link ${viewMode === 'market' ? 'active' : ''}`}
          onClick={() => setViewMode('market')}
        >
          <Compass size={22} />
        </div>

        <div 
          className={`nav-link ${viewMode === 'pipeline' ? 'active' : ''}`}
          onClick={() => setViewMode('pipeline')}
        >
          <Briefcase size={22} />
        </div>

        <div style={{ marginTop: 'auto' }}>
          <div className="nav-link" onClick={fetchData}>
            <RefreshCcw size={20} className={loading ? 'pulsing' : ''} />
          </div>
        </div>
      </nav>

      {/* MAIN CONTENT AREA */}
      <main className="main-content">
        {viewMode === 'market' ? (
          <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr' }}>
            <LeadManagement onConvertToDeal={handleConvertToDeal} />
          </div>
        ) : (
          <div className="dashboard-grid">
            {/* COLUMN 1: LIVE SIGNALS */}
            <SignalFeed signals={signals} loading={loading} />

            {/* COLUMN 2: ACTIVE PIPELINE */}
            <DealList 
              deals={deals} 
              selectedDeal={selectedDeal} 
              onSelectDeal={setSelectedDeal} 
            />

            {/* COLUMN 3: ACTIVATION ZONE */}
            <DecisionView 
              deal={selectedDeal} 
              onRefresh={fetchData} 
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
