import React, { useState, useEffect } from 'react';
import { Activity, RefreshCcw, TrendingUp } from 'lucide-react';
import DealRow from './components/DealRow';
import NextBestAction from './components/NextBestAction';

function App() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDeal, setSelectedDeal] = useState(null);

  const fetchDeals = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/deals');
      const data = await response.json();
      setDeals(data.data);
      if (selectedDeal) {
        // Update selected deal with new data
        const updatedSelected = data.data.find(d => d.id === selectedDeal.id);
        if (updatedSelected) setSelectedDeal(updatedSelected);
      }
    } catch (e) {
      console.error("Failed to fetch deals", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDeals();
  }, []);

  const totalPipeline = deals.reduce((acc, deal) => acc + deal.value, 0);
  const activeDeals = deals.filter(d => d.status === 'Active').length;
  const stalledDeals = deals.filter(d => d.status === 'Stalled').length;
  const atRiskDeals = deals.filter(d => d.status === 'At Risk').length;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <h1>Pipeline Intelligence</h1>
          <p className="dashboard-subtitle">Blostem Partner Activation Engine</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchDeals}>
          <RefreshCcw size={16} /> Refresh
        </button>
      </header>

      {loading && !deals.length ? (
        <div className="loading-container">
          <div className="loader"></div>
          <p>Loading intelligence data...</p>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-title">
                <TrendingUp size={16} color="var(--brand-primary)" />
                Total Pipeline
              </div>
              <div className="stat-value">
                ${(totalPipeline / 1000).toFixed(0)}k
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <Activity size={16} color="var(--status-active)" />
                Active Deals
              </div>
              <div className="stat-value">{activeDeals}</div>
            </div>
            <div className="stat-card">
              <div className="stat-title" style={{ color: "var(--status-risk)" }}>
                At Risk
              </div>
              <div className="stat-value">{atRiskDeals}</div>
            </div>
            <div className="stat-card">
              <div className="stat-title" style={{ color: "var(--status-stalled)" }}>
                Stalled
              </div>
              <div className="stat-value">{stalledDeals}</div>
            </div>
          </div>

          <div className="main-content">
            <div className="section-panel">
              <h2 className="section-title">Active Deals</h2>
              <div className="deals-table-wrapper">
                <table className="deals-table">
                  <thead>
                    <tr>
                      <th>COMPANY</th>
                      <th>STAGE</th>
                      <th>VALUE</th>
                      <th>STATUS</th>
                      <th>LAST ACTIVITY</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deals.map(deal => (
                      <DealRow 
                        key={deal.id} 
                        deal={deal} 
                        selected={selectedDeal?.id === deal.id}
                        onClick={setSelectedDeal}
                      />
                    ))}
                    {deals.length === 0 && (
                      <tr>
                        <td colSpan="5" className="empty-state" style={{ padding: '2rem' }}>
                          No deals found in pipeline.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="section-panel">
              <h2 className="section-title">Intelligence Engine</h2>
              <NextBestAction deal={selectedDeal} onActionTriggered={fetchDeals} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
