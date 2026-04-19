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
  Zap,
  Search,
  Plus,
  X
} from 'lucide-react';
import { LogManager } from './LeadsPage';
import ConfirmModal from '../components/ConfirmModal';
import { API_BASE_URL } from '../config';

const DealsPage = ({ setSystemStatus }) => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedDeal, setExpandedDeal] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newDealCompany, setNewDealCompany] = useState("");
  const [deletingDeal, setDeletingDeal] = useState(null);

  useEffect(() => {
    fetchDeals();
  }, []);

  const fetchDeals = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/deals`);
      const data = await res.json();
      setDeals(data);
    } catch (err) {
      console.error("Deals fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredDeals = deals.filter(deal => 
    deal.company.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddDeal = async () => {
    if (!newDealCompany.trim()) return;
    try {
      setSystemStatus('processing');
      const res = await fetch(`${API_BASE_URL}/api/deals/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: newDealCompany })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      await fetchDeals();
      setSystemStatus('idle');
      setShowAddModal(false);
      setNewDealCompany("");
    } catch (err) {
       alert(err.message);
       setSystemStatus('error');
    }
  };

  const handleDeleteDeal = async () => {
    if (!deletingDeal) return;
    try {
      setSystemStatus('processing');
      const res = await fetch(`${API_BASE_URL}/api/deals/${deletingDeal._id}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchDeals();
        setSystemStatus('idle');
        setDeletingDeal(null);
      } else {
        setSystemStatus('error');
      }
    } catch (err) {
      setSystemStatus('error');
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
          <div className="search-box glass">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search companies..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <button 
            className="action-btn-icon glass" 
            title="Add Manual Deal"
            onClick={() => setShowAddModal(true)}
          >
            <Plus size={18} />
          </button>

          <button  
            className="action-btn-icon glass" 
            title="Sync Intelligence"
            onClick={async () => {
              setSystemStatus('processing');
              try {
                await fetch(`${API_BASE_URL}/api/leads/generate`, { method: 'POST' });
                await fetchDeals();
                setSystemStatus('idle');
              } catch (err) { setSystemStatus('error'); }
            }}
          >
            <TrendingUp size={18} />
          </button>
        </div>
      </header>

      <div className="deals-list">
        {loading ? (
          <div className="empty-state"><div className="loader"></div></div>
        ) : filteredDeals.length > 0 ? (
          filteredDeals.map(deal => (
            <DealCard 
              key={deal._id} 
              deal={deal} 
              isExpanded={expandedDeal === deal._id}
              onToggle={() => setExpandedDeal(expandedDeal === deal._id ? null : deal._id)}
              onDelete={() => setDeletingDeal(deal)}
              refresh={fetchDeals}
            />
          ))
        ) : (
          <div className="empty-state glass">
            <Briefcase size={48} />
            <h3>{searchQuery ? "No matching deals" : "Pipeline Empty"}</h3>
            <p>{searchQuery ? "Refine your search parameters." : "Promote qualified leads to start tracking deals here."}</p>
          </div>
        )}
      </div>

      {showAddModal && (
        <div className="modal-overlay animate-fade-in">
          <div className="modal-content glass animate-slide-up">
            <div className="modal-header">
              <h2 className="outfit">Register Manual Deal</h2>
              <button className="close-btn" onClick={() => setShowAddModal(false)}><X size={20} /></button>
            </div>
            <div className="modal-body">
              <div className="input-field">
                <label>Company Name</label>
                <input 
                  autoFocus
                  type="text" 
                  className="glass-input"
                  placeholder="e.g. Acme Corp"
                  value={newDealCompany}
                  onChange={(e) => setNewDealCompany(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddDeal()}
                />
              </div>
              <p className="helper-text" style={{marginTop:'1rem', fontSize:'0.8rem', color:'var(--text-muted)'}}>
                If this company is currently a lead, it will automatically be promoted to an active deal.
              </p>
            </div>
            <div className="modal-footer">
               <button className="secondary-btn" onClick={() => setShowAddModal(false)}>Cancel</button>
               <button className="primary-btn" onClick={handleAddDeal}>Create Deal</button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal 
        isOpen={!!deletingDeal}
        onClose={() => setDeletingDeal(null)}
        onConfirm={handleDeleteDeal}
        title="Delete Deal & Archive"
        message={`Are you sure you want to delete the deal for "${deletingDeal?.company}"? This will drop it from the pipeline and instantly archive the company registry.`}
        confirmText="Delete & Archive Company"
        type="danger"
      />

      <style jsx>{`
        .header-actions {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .search-box {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.5rem 1.25rem;
          border-radius: 12px;
          min-width: 320px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--glass-border);
        }

        .search-box input {
          background: none;
          border: none;
          color: white;
          width: 100%;
          outline: none;
          font-size: 0.9rem;
        }

        .action-btn-icon {
          width: 42px;
          height: 42px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--glass-border);
          color: var(--text-muted);
          cursor: pointer;
          border-radius: 12px;
          transition: all 0.2s;
        }
        
        .action-btn-icon:hover {
          background: rgba(255, 255, 255, 0.08);
          color: var(--text-main);
          border-color: rgba(255, 255, 255, 0.2);
        }

        .deals-list {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        /* Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .modal-content {
          background: rgba(20, 24, 40, 0.95);
          width: 100%;
          max-width: 450px;
          padding: 2.5rem;
          border-radius: 24px;
        }
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }
        .modal-header h2 { font-size: 1.5rem; font-weight: 800; }
        .close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; }
        .glass-input {
          width: 100%;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          border-radius: 12px;
          padding: 0.85rem 1.25rem;
          color: white;
          outline: none;
          transition: border-color 0.2s;
        }
        .glass-input:focus { border-color: var(--accent-primary); }
        .input-field label {
          display: block;
          font-size: 0.8rem;
          font-weight: 800;
          text-transform: uppercase;
          color: var(--text-muted);
          margin-bottom: 0.75rem;
          letter-spacing: 0.05em;
        }
        .modal-footer {
          margin-top: 2.5rem;
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
        }
        .primary-btn {
          padding: 0.85rem 1.75rem;
          background: var(--accent-primary);
          color: white;
          border: none;
          border-radius: 12px;
          font-weight: 800;
          cursor: pointer;
        }
        .secondary-btn {
           padding: 0.85rem 1.75rem;
           background: rgba(255, 255, 255, 0.05);
           color: var(--text-main);
           border: 1px solid var(--glass-border);
           border-radius: 12px;
           font-weight: 800;
           cursor: pointer;
        }
      `}</style>
    </div>
  );
};

const DealCard = ({ deal, isExpanded, onToggle, refresh, onDelete }) => {
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
            <button 
              className="btn-icon mini delete-btn" 
              onClick={(e) => { e.stopPropagation(); onDelete(); }}
              title="Delete Deal & Archive"
            >
              <Trash2 size={16} />
            </button>
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
          gap: 1rem;
        }

        .delete-btn { color: var(--text-muted); opacity: 0; pointer-events: none; transition: all 0.2s; }
        .deal-main:hover .delete-btn { opacity: 1; pointer-events: auto; }
        .delete-btn:hover { color: var(--accent-danger); border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.1); }

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
