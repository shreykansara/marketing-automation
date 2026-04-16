import React, { useState, useEffect, Component } from 'react';
import { Activity, RefreshCcw, TrendingUp, ChevronRight, Zap, Target, Globe, ExternalLink, Calendar, MapPin, Building2, BarChart3, Database, AlertCircle } from 'lucide-react';
import NextBestAction from './components/NextBestAction';

// 4. Add Error Boundary (HIGHLY RECOMMENDED)
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error, errorInfo) { console.error("Uncaught error:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="loading-container" style={{ color: '#ef4444' }}>
          <AlertCircle size={48} />
          <h2>Something went wrong.</h2>
          <p>The dashboard encountered a rendering error. Please check the console or try refreshing.</p>
          <button className="btn btn-primary" onClick={() => window.location.reload()}>Refresh Page</button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [signals, setSignals] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [leads, setLeads] = useState([]);
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [generatingLeads, setGeneratingLeads] = useState(false);
  const [generatingDeals, setGeneratingDeals] = useState(false);

  const fetchPipelineInfo = async () => {
    setLoading(true);
    try {
      const [sigRes, leadRes, dealRes, compRes] = await Promise.all([
        fetch('http://localhost:8000/api/signals'),
        fetch('http://localhost:8000/api/leads'),
        fetch('http://localhost:8000/api/deals'),
        fetch('http://localhost:8000/api/companies')
      ]);
      const sigData = await sigRes.json();
      const leadData = await leadRes.json();
      const dealData = await dealRes.json();
      const compData = await compRes.json();

      // 2. Default Data Normalization (IMPORTANT)
      const rawSignals = sigData.data || [];
      const normalizedSignals = rawSignals.map(sig => {
        // 5. Debug Logging (TEMPORARY)
        if (!sig.signal_types || !Array.isArray(sig.signal_types)) {
          console.warn("Invalid or missing signal_types on signal:", sig);
        }
        
        return {
          ...sig,
          signal_types: Array.isArray(sig.signal_types) ? sig.signal_types : [],
          confidence: sig.confidence ?? 0,
          source: sig.source ?? "Unknown Source",
          company_name: sig.company_name ?? "Unknown Company"
        };
      });

      setSignals(normalizedSignals);
      setLeads(leadData.data || []);
      setDeals(dealData.data || []);
      setCompanies(compData.data || []);

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

  const handleSyncSignals = async () => {
    setSyncing(true);
    try {
      await fetch('http://localhost:8000/api/signals/ingest', { method: 'POST' });
      await fetchPipelineInfo();
    } catch (e) { console.error(e); }
    setSyncing(false);
  };

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

  const getSignalTypeColor = (type) => {
    const map = {
      'funding': 'bg-sapphire',
      'product_launch': 'bg-emerald',
      'hiring_sales': 'bg-amber',
      'hiring_engineering': 'bg-violet',
      'partnership': 'bg-indigo'
    };
    return map[type] || 'bg-gray';
  };

  const mainContent = (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="brand-lockup">
          <div className="logo-icon">
            <TrendingUp size={24} color="white" />
          </div>
          <div>
            <h1>Blostem Intelligence</h1>
            <p className="dashboard-subtitle">Market Signals &bull; Lead Activation &bull; Pipeline Velocity</p>
          </div>
        </div>
        <div className="header-actions">
           <button className={`btn btn-accent ${syncing ? 'pulsing' : ''}`} onClick={handleSyncSignals} disabled={syncing}>
            <Database size={16} /> {syncing ? "Syncing Live Data..." : "Sync Real-World Data"}
          </button>
          <button className="btn btn-secondary" onClick={handleGenerateLeads} disabled={generatingLeads}>
            <Target size={16} /> {generatingLeads ? "Analyzing..." : "Generate Leads"}
          </button>
          <button className="btn btn-primary" onClick={handleGenerateDeals} disabled={generatingDeals}>
            <Zap size={16} /> {generatingDeals ? "Converting..." : "Generate Deals"}
          </button>
        </div>
      </header>

      {loading && !signals.length ? (
        <div className="loading-container">
          <div className="loader"></div>
          <p>Processing neural market signals...</p>
        </div>
      ) : (
        <div className="funnel-layout">
          
          {/* Top Section: Account Intelligence Bar */}
          <section className="top-accounts-section">
            <div className="section-header-inline">
               <Building2 size={18} />
               <h3>Top Market Accounts</h3>
               <span className="count-tag">{companies.length} Tracking</span>
            </div>
            <div className="accounts-grid">
              {companies.slice(0, 6).map(company => (
                <div key={company.normalized_name} className="account-mini-card">
                  <div className="account-info">
                    <span className="account-name">{company.name}</span>
                    <span className="account-meta">{company.signals_count} signals tracked</span>
                  </div>
                  <BarChart3 size={14} className="account-icon" />
                </div>
              ))}
              {companies.length === 0 && <div className="placeholder-text">Sync data to reveal top accounts...</div>}
            </div>
          </section>

          <div className="funnel-columns-container">
            {/* COLUMN 1: SIGNALS */}
            <div className="flow-column signal-column">
              <div className="flow-header">
                <h3><Globe size={18} color="var(--brand-primary)" /> Live Signal Stream</h3>
                <span className="badge">{signals.length} Filtered</span>
              </div>
              <div className="flow-list">
                {signals.map(sig => (
                  <div key={sig.id || sig.fingerprint} className="flow-card signal-rich-card">
                    <div className="card-top">
                      <div className="company-info-row">
                        <strong className="signal-company">{sig.company_name}</strong>
                        <div className="signal-types-row">
                          {/* 1. Defensive Rendering (CRITICAL) & 3. Fallback UI */}
                          {(sig.signal_types || []).map(t => (
                            <span key={t} className={`tiny-badge ${getSignalTypeColor(t)}`}>{t}</span>
                          ))}
                          {(sig.signal_types || []).length === 0 && (
                            <span className="text-gray-400" style={{ fontSize: '0.65rem', opacity: 0.6 }}>No signals classified</span>
                          )}
                        </div>
                      </div>
                      <div className="signal-confidence">
                         <div className="confidence-label">Conf.</div>
                         <div className="confidence-val">{(sig.confidence * 100).toFixed(0)}%</div>
                      </div>
                    </div>
                    <div className="card-body">
                      {sig.raw_text ? sig.raw_text.split('. ')[0] : "No description available"}...
                    </div>
                    <div className="card-footer">
                      <div className="footer-meta">
                        <span className="source-tag">{sig.source}</span>
                        <span className="time-tag"><Calendar size={10} /> {sig.timestamp ? new Date(sig.timestamp).toLocaleDateString() : 'N/A'}</span>
                      </div>
                      {sig.source_url && (
                        <a href={sig.source_url} target="_blank" rel="noreferrer" className="source-link">
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
                {signals.length === 0 && <div className="empty-state">No real-time signals detected. Try syncing data.</div>}
              </div>
            </div>

            <div className="flow-connector">
               <ChevronRight size={24} color="var(--border-strong)" />
            </div>

            {/* COLUMN 2: LEADS */}
            <div className="flow-column lead-column">
              <div className="flow-header">
                <h3><Target size={18} color="#059669" /> High-Intent Leads</h3>
                <span className="badge">{leads.length} Active</span>
              </div>
              <div className="flow-list">
                {leads.map(lead => {
                  const isHighIntent = lead.intent_score >= 60;
                  return (
                    <div key={lead.company} className={`flow-card lead-card ${isHighIntent ? 'high-intent' : ''}`}>
                      <div className="card-top">
                        <strong className="lead-company">{lead.company}</strong>
                        <div className={`intent-score-pill ${isHighIntent ? 'bg-green' : 'bg-gray'}`}>
                          {lead.intent_score} INTENT
                        </div>
                      </div>
                      <div className="card-desc">
                         <div className="lead-stat">
                            <Zap size={10} /> {lead.signals?.length || 0} signals
                         </div>
                         <div className="lead-latest">
                            Latest: {lead.signals?.[lead.signals.length - 1]?.signal_type || 'Market Intel'}
                         </div>
                      </div>
                    </div>
                  );
                })}
                {leads.length === 0 && <div className="empty-state">Generate leads from market signals.</div>}
              </div>
            </div>

            <div className="flow-connector">
               <ChevronRight size={24} color="var(--border-strong)" />
            </div>

            {/* COLUMN 3: DEALS */}
            <div className="flow-column deal-column">
              <div className="flow-header">
                <h3><Activity size={18} color="#ea580c" /> Deal Pipeline</h3>
                <span className="badge">${(totalPipeline / 1000).toFixed(0)}k Value</span>
              </div>
              <div className="flow-list">
                {deals.map(deal => {
                  const isStalled = deal.status === 'Stalled';
                  const isHighPriority = deal.priority_level === 'High';
                  const isSelected = selectedDeal?.id === deal.id;
                  
                  let cardClass = "flow-card deal-clickable deal-rich-card";
                  if (isSelected) cardClass += " selected-border";
                  if (isStalled) cardClass += " stalled-deal";
                  if (isHighPriority) cardClass += " high-priority";

                  return (
                    <div key={deal.id} className={cardClass} onClick={() => setSelectedDeal(deal)}>
                      <div className="card-top">
                        <strong className="deal-company">{deal.company}</strong>
                        <div className="deal-meta-pills">
                           {isHighPriority && <span className="tiny-badge bg-red-strong">High Priority</span>}
                           <span className="tiny-badge bg-glass">{deal.status}</span>
                        </div>
                      </div>
                      <div className="deal-value-row">
                        <TrendingUp size={12} /> ${deal.value?.toLocaleString()}
                      </div>
                      <div className="card-desc risk-indicator">
                        {deal.risk_reason && deal.risk_reason !== "No issues detected" ? (
                          <span className="risk-warning">!!! {deal.risk_reason}</span>
                        ) : (
                          <span className="health-check">Healthy Pipeline</span>
                        )}
                      </div>
                      {deal.next_action && deal.next_action !== "Monitor Deal" && (
                         <div className="action-suggestion">
                            <span className="suggestion-label">Suggested:</span> {deal.next_action}
                         </div>
                      )}
                    </div>
                  );
                })}
                {deals.length === 0 && <div className="empty-state">No pipeline deals detected.</div>}
              </div>
            </div>
          </div>

          {/* Bottom Panel: Insight View Details pane */}
          <div className="insight-view-wrapper">
            <div className="insight-pane-glass">
              <h2 className="section-title">Account Activation Intelligence</h2>
              <NextBestAction deal={selectedDeal} onActionTriggered={fetchPipelineInfo} />
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <ErrorBoundary>
      {mainContent}
    </ErrorBoundary>
  );
}

export default App;
