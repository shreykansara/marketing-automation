import React, { useState, useEffect } from 'react';
import { Activity, RefreshCcw, TrendingUp, ChevronRight, Zap, Target } from 'lucide-react';
import NextBestAction from './components/NextBestAction';

function App() {
  const [signals, setSignals] = useState([]);
  const [leads, setLeads] = useState([]);
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [generatingLeads, setGeneratingLeads] = useState(false);
  const [generatingDeals, setGeneratingDeals] = useState(false);

  const fetchPipelineInfo = async () => {
    setLoading(true);
    try {
      const [sigRes, leadRes, dealRes] = await Promise.all([
        fetch('http://localhost:8000/api/signals'),
        fetch('http://localhost:8000/api/leads'),
        fetch('http://localhost:8000/api/deals')
      ]);
      const sigData = await sigRes.json();
      const leadData = await leadRes.json();
      const dealData = await dealRes.json();

      setSignals(sigData.data || []);
      setLeads(leadData.data || []);
      setDeals(dealData.data || []);

      if (selectedDeal) {
        const updatedSelected = (dealData.data || []).find(d => d.id === selectedDeal.id);
        if (updatedSelected) setSelectedDeal(updatedSelected);
      }
    } catch (e) {
      console.error("Failed to fetch pipeline info", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPipelineInfo();
  }, []);

  const handleGenerateLeads = async () => {
    setGeneratingLeads(true);
    try {
      await fetch('http://localhost:8000/api/leads/generate', { method: 'POST' });
      await fetchPipelineInfo();
    } catch(e) { console.error(e); }
    setGeneratingLeads(false);
  };

  const handleGenerateDeals = async () => {
    setGeneratingDeals(true);
    try {
      await fetch('http://localhost:8000/api/deals/auto-generate', { method: 'POST' });
      await fetchPipelineInfo();
    } catch(e) { console.error(e); }
    setGeneratingDeals(false);
  };

  const totalPipeline = deals.reduce((acc, deal) => acc + (deal.value || 0), 0);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <h1>B2B Pipeline Intelligence</h1>
          <p className="dashboard-subtitle">Full Funnel Transparency: Signals → Leads → Deals</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-secondary" onClick={handleGenerateLeads} disabled={generatingLeads}>
            {generatingLeads ? "..." : "Generate Leads"}
          </button>
          <button className="btn btn-primary" onClick={handleGenerateDeals} disabled={generatingDeals}>
            {generatingDeals ? "..." : "Generate Deals"}
          </button>
          <button className="btn btn-secondary" onClick={fetchPipelineInfo}>
            <RefreshCcw size={16} /> Refresh
          </button>
        </div>
      </header>

      {loading && !signals.length ? (
        <div className="loading-container">
          <div className="loader"></div>
          <p>Loading funnel intelligence...</p>
        </div>
      ) : (
        <div className="funnel-layout">
          {/* Top Panel: Flow Visualization */}
          <div className="flow-container">
            
            {/* COLUMN 1: SIGNALS */}
            <div className="flow-column">
              <div className="flow-header">
                <h3><Zap size={18} color="#0284c7" /> Signals</h3>
                <span className="badge">{signals.length} Extracted</span>
              </div>
              <div className="flow-list">
                {signals.map(sig => (
                  <div key={sig.id || Math.random()} className="flow-card">
                    <div className="card-top">
                      <strong>{sig.company}</strong>
                      <span className="tiny-badge bg-blue">{sig.signal_type}</span>
                    </div>
                    <div className="card-desc">{new Date(sig.timestamp).toLocaleDateString()}</div>
                  </div>
                ))}
                {signals.length === 0 && <div className="empty-state">No signals found</div>}
              </div>
            </div>

            <div className="flow-connector">
               <ChevronRight size={32} color="var(--border-strong)" />
            </div>

            {/* COLUMN 2: LEADS */}
            <div className="flow-column">
              <div className="flow-header">
                <h3><Target size={18} color="#059669" /> Leads</h3>
                <span className="badge">{leads.length} Scored</span>
              </div>
              <div className="flow-list">
                {leads.map(lead => {
                  const isHighIntent = lead.intent_score >= 60;
                  return (
                    <div key={lead.company} className={`flow-card ${isHighIntent ? 'high-intent' : ''}`}>
                      <div className="card-top">
                        <strong>{lead.company}</strong>
                        <span className={`tiny-badge ${isHighIntent ? 'bg-green' : 'bg-gray'}`}>
                          {lead.intent_score} Intent
                        </span>
                      </div>
                      <div className="card-desc">
                        {lead.signals?.length || 0} signals | latest: {lead.signals?.[0]?.signal_type || 'Unknown'}
                      </div>
                    </div>
                  );
                })}
                {leads.length === 0 && <div className="empty-state">No leads generated</div>}
              </div>
            </div>

            <div className="flow-connector">
               <ChevronRight size={32} color="var(--border-strong)" />
            </div>

            {/* COLUMN 3: DEALS */}
            <div className="flow-column">
              <div className="flow-header">
                <h3><Activity size={18} color="#ea580c" /> Deals</h3>
                <span className="badge">${(totalPipeline / 1000).toFixed(0)}k Pipeline</span>
              </div>
              <div className="flow-list">
                {deals.map(deal => {
                  const isStalled = deal.status === 'Stalled';
                  const isHighPriority = deal.priority_level === 'High';
                  const isSelected = selectedDeal?.id === deal.id;
                  
                  let cardClass = "flow-card deal-clickable";
                  if (isSelected) cardClass += " selected-border";
                  else if (isStalled) cardClass += " stalled-deal";
                  else if (isHighPriority) cardClass += " high-priority";

                  return (
                    <div key={deal.id} className={cardClass} onClick={() => setSelectedDeal(deal)}>
                      <div className="card-top">
                        <strong>{deal.company}</strong>
                        <div style={{display:'flex', gap:'4px'}}>
                           {isHighPriority && <span className="tiny-badge bg-red">High Priority</span>}
                           <span className="tiny-badge bg-gray">{deal.status}</span>
                        </div>
                      </div>
                      <div className="card-desc risk-text">
                        {deal.risk_reason && deal.risk_reason !== "No issues detected" ? `Risk: ${deal.risk_reason}` : "Pipeline Healthy"}
                      </div>
                      {deal.next_action && deal.next_action !== "Monitor Deal" && (
                         <div className="card-desc action-text">
                            Next: {deal.next_action}
                         </div>
                      )}
                    </div>
                  );
                })}
                {deals.length === 0 && <div className="empty-state">No pipeline deals</div>}
              </div>
            </div>
          </div>

          {/* Bottom Panel: Insight View Details pane */}
          <div className="insight-pane">
            <h2 className="section-title">Activation Intelligence Pane</h2>
            <NextBestAction deal={selectedDeal} onActionTriggered={fetchPipelineInfo} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
