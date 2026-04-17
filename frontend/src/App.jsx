import React, { useState, useEffect } from 'react';
import DealList from './components/DealList';
import DecisionView from './components/DecisionView';
import HistoryTimeline from './components/HistoryTimeline';
import { RefreshCcw, Database } from 'lucide-react';

function App() {
  const [deals, setDeals] = useState([]);
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const fetchDeals = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/deals');
      const data = await res.json();
      const sortedDeals = data.data || [];
      setDeals(sortedDeals);
      
      // Persist selection if possible
      if (selectedDeal) {
        const updated = sortedDeals.find(d => d.id === selectedDeal.id);
        if (updated) setSelectedDeal(updated);
      } else if (sortedDeals.length > 0) {
        setSelectedDeal(sortedDeals[0]);
      }
    } catch (e) {
      console.error("Failed to fetch deals", e);
    }
    setLoading(false);
  };

  const handleEvaluateAndTrigger = async (dealId) => {
    try {
      await fetch(`http://localhost:8000/api/deals/${dealId}/evaluate-and-trigger`, { method: 'POST' });
      await fetchDeals();
    } catch (e) {
      console.error("Evaluation failed", e);
    }
  };

  const handleFullSync = async () => {
    setSyncing(true);
    try {
      // Step 1: Ingest signals
      await fetch('http://localhost:8000/api/signals/ingest', { method: 'POST' });
      // Step 2: Auto-generate deals
      await fetch('http://localhost:8000/api/deals/auto-generate', { method: 'POST' });
      await fetchDeals();
    } catch (e) {
      console.error("Sync failed", e);
    }
    setSyncing(false);
  };

  useEffect(() => {
    fetchDeals();
  }, []);

  return (
    <div className="app-container">
      {/* LEFT: Selection Sidebar */}
      <DealList 
        deals={deals} 
        selectedDeal={selectedDeal} 
        onSelectDeal={setSelectedDeal} 
      />

      {/* CENTER: Intelligence View */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <DecisionView 
          deal={selectedDeal} 
          onTriggerEvaluate={handleEvaluateAndTrigger}
        />
        
        {/* Sync Controls (Overlay bottom left of main view) */}
        <div style={{ position: 'fixed', bottom: '2rem', left: '340px', display: 'flex', gap: '1rem' }}>
           <button className="btn btn-primary" onClick={handleFullSync} disabled={syncing}>
             <Database size={16} /> {syncing ? "Syncing..." : "Full System Sync"}
           </button>
           <button className="btn btn-ghost" onClick={fetchDeals} disabled={loading}>
             <RefreshCcw size={16} className={loading ? 'pulsing' : ''} /> Refresh Pipeline
           </button>
        </div>
      </div>

      {/* RIGHT: Memory View */}
      <HistoryTimeline 
        history={selectedDeal?.decision_history || []} 
      />
    </div>
  );
}

export default App;
