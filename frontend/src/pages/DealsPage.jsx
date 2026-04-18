import React, { useState, useEffect } from 'react';
import { 
  Briefcase, 
  Trash2, 
  Target, 
  MessageSquare,
  ChevronDown,
  ChevronUp,
  History,
  TrendingUp,
  AlertTriangle,
  Mail,
  Zap
} from 'lucide-react';
import { LogManager } from './LeadsPage';

const DealsPage = ({ setSystemStatus }) => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedDeal, setExpandedDeal] = useState(null);
  const [sortMode, setSortMode] = useState('weighted');

  useEffect(() => {
    fetchDeals();
  }, [sortMode]);

  const fetchDeals = async () => {
    setLoading(true);
    try {
      const endpoint = sortMode === 'weighted' 
        ? 'http://127.0.0.1:8000/api/deals' 
        : 'http://127.0.0.1:8000/api/deals/relevance-logs';
      const res = await fetch(endpoint);
      const data = await res.json();
      setDeals(data);
    } catch (err) {
      console.error("Deals fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Active Pipeline</h1>
          <p className="header-desc">Prioritize and track high-urgency business deals</p>
        </div>
        
        <div className="header-actions">
          <button className="btn btn-outline" onClick={async () => {
            setSystemStatus('processing');
            try {
              await fetch('http://127.0.0.1:8000/api/leads/generate', { method: 'POST' });
              await fetchDeals();
              setSystemStatus('idle');
            } catch (err) { setSystemStatus('error'); }
          }}>
            <TrendingUp size={18} />
            Sync Intelligence
          </button>
          
          <div className="toggle-group glass">
            <button 
              className={`toggle-btn ${sortMode === 'weighted' ? 'active' : ''}`}
              onClick={() => setSortMode('weighted')}
            >
              Smart Urgency
            </button>
            <button 
              className={`toggle-btn ${sortMode === 'logs_only' ? 'active' : ''}`}
              onClick={() => setSortMode('logs_only')}
            >
              Action Intensity
            </button>
          </div>
        </div>
      </header>

      <div className="deals-list">
        {loading ? (
          <div className="empty-state"><div className="loader"></div></div>
        ) : deals.length > 0 ? (
          deals.map(deal => (
            <DealCard 
              key={deal._id} 
              deal={deal} 
              isExpanded={expandedDeal === deal._id}
              onToggle={() => setExpandedDeal(expandedDeal === deal._id ? null : deal._id)}
              refresh={fetchDeals}
            />
          ))
        ) : (
          <div className="empty-state glass">
            <Briefcase size={48} />
            <h3>Pipeline Empty</h3>
            <p>Promote qualified leads to start tracking deals here.</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .toggle-group {
          display: flex;
          padding: 0.35rem;
          border-radius: 14px;
          gap: 0.25rem;
        }
        .toggle-btn {
          padding: 0.6rem 1.25rem;
          border: none;
          background: none;
          color: var(--text-muted);
          font-weight: 800;
          font-size: 0.85rem;
          cursor: pointer;
          border-radius: 10px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .toggle-btn.active {
          background: var(--accent-primary);
          color: white;
          box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        .deals-list {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
      `}</style>
    </div>
  );
};

const DealCard = ({ deal, isExpanded, onToggle, refresh }) => {
  const getSeverity = (score) => {
    if (score >= 80) return 'critical';
    if (score >= 50) return 'active';
    return 'neutral';
  };

  return (
    <div className={`deal-card glass animate-fade-in ${getSeverity(deal.relevance)} ${isExpanded ? 'expanded' : ''}`}>
      <div className="deal-main" onClick={onToggle}>
        <div className="deal-info">
          <div className="deal-brand">
            <div className="deal-icon glass">
              <Zap size={20} />
            </div>
            <div>
              <h3 className="outfit">{deal.company}</h3>
              <div className="deal-comms">
                <Mail size={14} />
                <span>{deal.emails?.length || 0} Communications</span>
              </div>
            </div>
          </div>

          <div className="urgency-meter">
            <div className="meter-header">
              <TrendingUp size={14} />
              <span>Pipeline Score</span>
            </div>
            <div className="score-display">
               <span className="meter-value outfit">{Math.round(deal.relevance)}%</span>
               <div className="urgency-tag">{deal.relevance >= 80 ? 'Critical' : deal.relevance >= 50 ? 'Urgent' : 'Steady'}</div>
            </div>
          </div>
        </div>
        
        <div className="deal-actions">
          <div className="action-stack">
            {deal.relevance >= 80 && <div className="hot-pulse-outer"><div className="hot-pulse-inner"></div></div>}
            <button className="btn-icon mini">
              {isExpanded ? <ChevronUp size={20} /> : <MessageSquare size={18} />}
            </button>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="deal-details animate-fade-in">
          <div className="details-grid">
            <div className="logs-panel">
              <LogManager 
                type="deal" 
                parentId={deal._id} 
                logs={deal.logs || []} 
                onUpdate={refresh} 
              />
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .deal-card {
          border-left: 6px solid transparent;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          overflow: hidden;
        }
        .deal-card.critical { border-left-color: var(--accent-danger); }
        .deal-card.active { border-left-color: var(--accent-warning); }
        .deal-card.neutral { border-left-color: var(--accent-primary); }

        .deal-main {
          padding: 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
        }

        .deal-info {
          display: flex;
          align-items: center;
          gap: 6rem;
          flex: 1;
        }

        .deal-brand {
          display: flex;
          align-items: center;
          gap: 1.5rem;
          min-width: 280px;
        }

        .deal-icon {
          width: 54px;
          height: 54px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--accent-primary);
          border-radius: 14px;
          background: rgba(255, 255, 255, 0.03);
        }

        .deal-brand h3 {
          font-size: 1.75rem;
          font-weight: 800;
          text-transform: capitalize;
          margin-bottom: 0.3rem;
        }

        .deal-comms {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          font-size: 0.85rem;
          color: var(--text-muted);
          font-weight: 700;
        }

        .urgency-meter {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
        }

        .meter-header {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          font-size: 0.75rem;
          font-weight: 800;
          text-transform: uppercase;
          color: var(--text-muted);
          letter-spacing: 0.1em;
        }

        .score-display {
          display: flex;
          align-items: center;
          gap: 1.25rem;
        }

        .meter-value {
          font-size: 2rem;
          font-weight: 900;
          color: var(--text-main);
        }

        .urgency-tag {
          font-size: 0.75rem;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          font-weight: 800;
          padding: 0.25rem 0.6rem;
          border-radius: 4px;
          background: rgba(255, 255, 255, 0.05);
          color: var(--text-muted);
        }

        .hot-pulse-outer {
          position: relative;
          width: 14px;
          height: 14px;
        }
        
        .hot-pulse-inner {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          background: var(--accent-danger);
          box-shadow: 0 0 12px var(--accent-danger);
          animation: pulse-ring 2s infinite ease-out;
        }

        @keyframes pulse-ring {
          0% { transform: scale(0.8); opacity: 1; }
          100% { transform: scale(3); opacity: 0; }
        }

        .deal-actions {
          display: flex;
          align-items: center;
        }
        
        .action-stack {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .deal-details {
          padding: 0 2rem 3rem 2rem;
          border-top: 1px solid var(--glass-border);
          background: rgba(0, 0, 0, 0.15);
        }
      `}</style>
    </div>
  );
};

export default DealsPage;
