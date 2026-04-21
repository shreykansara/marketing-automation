import React, { useState, useEffect } from 'react';
import { 
  Target, 
  Trash2, 
  TrendingUp, 
  Clock, 
  MessageSquare,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Mail,
  Zap,
  Search,
  Plus,
  X,
  History
} from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';
import { API_BASE_URL } from '../config';

const LeadsPage = ({ setSystemStatus }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedLead, setExpandedLead] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newLeadCompany, setNewLeadCompany] = useState("");
  const [deletingLead, setDeletingLead] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/leads`);
      const data = await res.json();
      setLeads(data);
    } catch (err) {
      console.error("Leads fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(lead => 
    lead.company_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddLead = async () => {
    if (!newLeadCompany.trim()) return;
    try {
      setSystemStatus('processing');
      const res = await fetch(`${API_BASE_URL}/api/leads/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: newLeadCompany })
      });
      if (res.ok) {
        await fetchLeads();
        setSystemStatus('idle');
        setShowAddModal(false);
        setNewLeadCompany("");
      } else { setSystemStatus('error'); }
    } catch (err) { setSystemStatus('error'); }
  };

  const handleDeleteLead = async () => {
    if (!deletingLead) return;
    try {
      setSystemStatus('processing');
      const res = await fetch(`${API_BASE_URL}/api/leads/${deletingLead._id}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchLeads();
        setSystemStatus('idle');
        setDeletingLead(null);
      } else { setSystemStatus('error'); }
    } catch (err) { setSystemStatus('error'); }
  };

  const promoteLead = async (leadId) => {
    try {
      setSystemStatus('processing');
      const res = await fetch(`${API_BASE_URL}/api/deals/promote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_id: leadId })
      });
      if (res.ok) {
        await fetchLeads();
        setSystemStatus('idle');
      } else { setSystemStatus('error'); }
    } catch (err) { setSystemStatus('error'); }
  };

  return (
    <div className="page-container">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Qualified Leads</h1>
          <p className="header-desc">AI-prioritized prospects curated from market signals</p>
        </div>
        
        <div className="header-actions">
          <div className="search-box glass">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Filter leads..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button className="action-btn-icon glass" title="Add Manual Lead" onClick={() => setShowAddModal(true)}>
            <Plus size={18} />
          </button>
        </div>
      </header>

      <div className="leads-list">
        {loading ? (
          <div className="empty-state"><div className="loader"></div></div>
        ) : filteredLeads.length > 0 ? (
          filteredLeads.map(lead => (
            <LeadCard 
              key={lead._id} 
              lead={lead} 
              isExpanded={expandedLead === lead._id}
              onToggle={() => setExpandedLead(expandedLead === lead._id ? null : lead._id)}
              onDelete={() => setDeletingLead(lead)}
              onPromote={() => promoteLead(lead._id)}
              refresh={fetchLeads}
            />
          ))
        ) : (
          <div className="empty-state glass">
            <Target size={48} />
            <h3>No qualified leads</h3>
            <p>Scanning intelligence database... New leads appear as signals are ingested.</p>
          </div>
        )}
      </div>

      {showAddModal && (
        <div className="modal-overlay animate-fade-in">
          <div className="modal-content glass animate-slide-up">
            <div className="modal-header">
              <h2 className="outfit">Register Manual Lead</h2>
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
                  value={newLeadCompany}
                  onChange={(e) => setNewLeadCompany(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddLead()}
                />
              </div>
            </div>
            <div className="modal-footer">
               <button className="secondary-btn" onClick={() => setShowAddModal(false)}>Cancel</button>
               <button className="primary-btn" onClick={handleAddLead}>Create Lead</button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal 
        isOpen={!!deletingLead}
        onClose={() => setDeletingLead(null)}
        onConfirm={handleDeleteLead}
        title="Delete Lead & Archive"
        message={`Are you sure you want to delete the lead for "${deletingLead?.company_name}"? This will drop it from the pipeline.`}
        confirmText="Delete Lead"
        type="danger"
      />

      <style>{`
        .header-actions { display: flex; align-items: center; gap: 1.5rem; }
        .search-box { 
          display: flex; 
          align-items: center; 
          gap: 0.75rem; 
          padding: 0.5rem 1.25rem; 
          border-radius: 12px; 
          min-width: 320px; 
          background: rgba(255, 255, 255, 0.03); 
          border: 1px solid var(--glass-border);
          transition: all 0.2s;
        }
        .search-box:focus-within {
          border-color: var(--accent-primary);
          background: rgba(255, 255, 255, 0.06);
        }
        .search-box input { background: none; border: none; color: white; width: 100%; outline: none; font-size: 1rem; }
        .action-btn-icon { width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border); color: var(--text-muted); cursor: pointer; border-radius: 12px; transition: all 0.2s; }
        .action-btn-icon:hover { background: rgba(255, 255, 255, 0.08); color: var(--text-main); border-color: rgba(255, 255, 255, 0.2); }
        .leads-list { display: flex; flex-direction: column; gap: 1.5rem; }
        .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
        .modal-content { background: rgba(20, 24, 40, 0.95); width: 100%; max-width: 450px; padding: 2.5rem; border-radius: 24px; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .modal-header h2 { font-size: 1.5rem; font-weight: 800; }
        .close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; }
        .glass-input { width: 100%; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--glass-border); border-radius: 12px; padding: 0.85rem 1.25rem; color: white; outline: none; transition: border-color 0.2s; }
        .glass-input:focus { border-color: var(--accent-primary); }
        .input-field label { display: block; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.75rem; letter-spacing: 0.05em; }
        .modal-footer { margin-top: 2.5rem; display: flex; justify-content: flex-end; gap: 1rem; }
        .primary-btn { padding: 0.85rem 1.75rem; background: var(--accent-primary); color: white; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; }
        .secondary-btn { padding: 0.85rem 1.75rem; background: rgba(255, 255, 255, 0.05); color: var(--text-main); border: 1px solid var(--glass-border); border-radius: 12px; font-weight: 800; cursor: pointer; }
      `}</style>
    </div>
  );
};

const LeadCard = ({ lead, isExpanded, onToggle, refresh, onDelete, onPromote }) => {
  return (
    <div className={`lead-card glass animate-fade-in ${isExpanded ? 'expanded' : ''}`}>
      <div className="lead-main" onClick={onToggle}>
        <div className="lead-info">
          <div className="company-info">
            <h3 className="outfit">{lead.company_name}</h3>
            <span className="signal-count">{lead.signals?.length || 0} Signals Linked</span>
          </div>
          <div className="relevance-group">
            <span className="relevance-label">Intent Score</span>
            <div className="relevance-bar-bg"><div className="relevance-bar-fill" style={{width: `${lead.relevance_score}%`}}></div></div>
            <span className="relevance-value outfit">{Math.round(lead.relevance_score)}%</span>
          </div>
        </div>
        
        <div className="lead-actions">
          <button className="btn btn-primary btn-sm" onClick={(e) => { e.stopPropagation(); onPromote(); }}><TrendingUp size={14} /> Promote to Deal</button>
          <button className="btn-icon mini delete-btn" onClick={(e) => { e.stopPropagation(); onDelete(); }}><Trash2 size={16} /></button>
          <button className="btn-icon mini">{isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}</button>
        </div>
      </div>

      {isExpanded && (
        <div className="lead-details animate-fade-in">
          <div className="details-grid">
            <div className="signals-panel">
              <h4 className="section-title"><Zap size={14} /> Underlying Intelligence</h4>
              <div className="signals-mini-list">
                {lead.signals?.map(s => (
                  <div key={s._id} className="signal-mini-item glass">
                    <strong>{s.title}</strong>
                    <p>{s.content.substring(0, 80)}...</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="logs-panel">
              <LogManager type="lead" parentId={lead._id} logs={lead.logs || []} onUpdate={refresh} />
            </div>
          </div>
        </div>
      )}

      <style>{`
        .lead-card { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); overflow: hidden; }
        .lead-main { padding: 1.5rem 2rem; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        .lead-info { display: flex; align-items: center; gap: 4rem; flex: 1; }
        .company-info h3 { font-size: 1.5rem; font-weight: 800; text-transform: capitalize; margin-bottom: 0.2rem; }
        .signal-count { font-size: 0.8rem; color: var(--text-muted); font-weight: 700; opacity: 0.8; }
        .relevance-group { display: flex; align-items: center; gap: 1rem; flex: 1; max-width: 400px; }
        .relevance-label { font-size: 0.7rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); letter-spacing: 0.05em; width: 100px; }
        .relevance-bar-bg { flex: 1; height: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden; }
        .relevance-bar-fill { height: 100%; background: var(--accent-primary); border-radius: 3px; box-shadow: 0 0 10px var(--accent-primary); }
        .relevance-value { font-size: 1.1rem; font-weight: 800; width: 45px; }
        .lead-actions { display: flex; align-items: center; gap: 1.5rem; }
        .delete-btn { color: var(--text-muted); opacity: 0; pointer-events: none; transition: all 0.2s; }
        .lead-main:hover .delete-btn { opacity: 1; pointer-events: auto; }
        .delete-btn:hover { color: var(--accent-danger); }
        .lead-details { padding: 2rem; border-top: 1px solid var(--glass-border); background: rgba(0, 0, 0, 0.1); }
        .details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; }
        .section-title { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; }
        .signals-mini-list { display: flex; flex-direction: column; gap: 1rem; }
        .signal-mini-item { padding: 1rem; font-size: 0.85rem; border-radius: 10px; }
        .signal-mini-item p { margin-top: 0.5rem; color: var(--text-muted); line-height: 1.5; }
      `}</style>
    </div>
  );
};

export const LogManager = ({ type, parentId, logs, onUpdate }) => {
  const [newLog, setNewLog] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, logId: null });

  const handleAddLog = async () => {
    if (!newLog.trim()) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/${type}s/${parentId}/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newLog })
      });
      if (res.ok) {
        setNewLog("");
        setIsAdding(false);
        onUpdate();
      }
    } catch (err) {}
  };

  const handleDeleteLog = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/${type}s/${parentId}/logs/${deleteModal.logId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setDeleteModal({ isOpen: false, logId: null });
        onUpdate();
      }
    } catch (err) {}
  };

  return (
    <div className="log-manager">
      <div className="section-header-row">
        <h4 className="section-title"><Clock size={14} /> Activity Intelligence</h4>
        <button className="btn-text" onClick={() => setIsAdding(true)}>+ Add Entry</button>
      </div>

      <div className="logs-list">
        {logs.length > 0 ? (
          [...logs]
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .map((log, index) => (
            <div key={log._id || index} className="log-entry glass">
              <div className="log-bullet"></div>
              <div className="log-content">
                <div className="log-meta">
                  <span className="log-type">{log.type}</span>
                  <span className="log-date">{new Date(log.timestamp).toLocaleString()}</span>
                </div>
                <div className="log-msg">{log.message}</div>
              </div>
              <button className="btn-icon mini delete-btn" onClick={() => setDeleteModal({ isOpen: true, logId: log._id })}><Trash2 size={14} /></button>
            </div>
          ))
        ) : (
          <div className="empty-logs">No intelligence logs recorded.</div>
        )}
      </div>

      {isAdding && (
        <div className="log-input-area animate-slide-up">
          <textarea 
            autoFocus 
            className="glass-input log-textarea" 
            placeholder="Type intelligence log..." 
            value={newLog} 
            onChange={(e) => setNewLog(e.target.value)} 
          />
          <div className="log-input-actions">
            <button className="btn-text" onClick={() => setIsAdding(false)}>Cancel</button>
            <button className="btn btn-primary btn-sm" onClick={handleAddLog}>Save Intelligence</button>
          </div>
        </div>
      )}

      <ConfirmModal 
        isOpen={deleteModal.isOpen} 
        onClose={() => setDeleteModal({ isOpen: false, logId: null })} 
        onConfirm={handleDeleteLog} 
        title="Delete Log" 
        message="Are you sure you want to delete this log entry?" 
        type="danger" 
      />

      <style>{`
        .section-header-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.5rem; }
        .btn-text { background: none; border: none; color: var(--accent-primary); font-size: 0.75rem; font-weight: 800; cursor: pointer; }
        .logs-list { 
          display: flex; 
          flex-direction: column; 
          gap: 0.75rem; 
          max-height: 300px; 
          overflow-y: auto; 
          padding-right: 0.5rem;
        }
        .logs-list::-webkit-scrollbar { width: 4px; }
        .logs-list::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
        .logs-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        .logs-list::-webkit-scrollbar-thumb:hover { background: var(--accent-primary); }
        .log-entry { padding: 1rem; display: flex; gap: 1rem; position: relative; }
        .log-bullet { width: 4px; height: 100%; position: absolute; left: 0; top: 0; background: var(--accent-primary); opacity: 0.3; }
        .log-content { flex: 1; }
        .log-meta { display: flex; gap: 1rem; font-size: 0.65rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.25rem; }
        .log-msg { font-size: 0.9rem; line-height: 1.4; }
        .empty-logs { font-size: 0.85rem; color: var(--text-muted); font-style: italic; }
        .log-input-area { margin-top: 1rem; }
        .log-textarea { width: 100%; min-height: 80px; margin-bottom: 0.5rem; font-size: 0.9rem; padding: 0.75rem; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); border-radius: 8px; color: white; resize: vertical; }
        .log-input-actions { display: flex; justify-content: flex-end; gap: 1rem; }
      `}</style>
    </div>
  );
};

export default LeadsPage;
