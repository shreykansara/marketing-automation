import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Plus, 
  Trash2, 
  TrendingUp, 
  MessageSquare,
  ChevronDown,
  ChevronUp,
  History,
  Send,
  Loader2,
  AlertCircle,
  X
} from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';
import { API_BASE_URL } from '../config';

const LeadsPage = ({ setSystemStatus }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedLead, setExpandedLead] = useState(null);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newLeadCompany, setNewLeadCompany] = useState("");
  const [deletingLead, setDeletingLead] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);
    try {
      // Standardize to 127.0.0.1 to avoid localhost vs 127.0.0.1 issues
      const res = await fetch(`${API_BASE_URL}/api/leads`);
      if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
      const data = await res.json();
      setLeads(data);
    } catch (err) {
      console.error("Leads fetch failed", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePromote = async (leadId) => {
    setSystemStatus('processing');
    try {
      const res = await fetch(`${API_BASE_URL}/api/deals/promote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_id: leadId })
      });
      if (res.ok) {
        await fetchLeads();
        setSystemStatus('idle');
      }
    } catch (err) {
      console.error("Promotion failed", err);
      setSystemStatus('error');
    }
  };

  const handleAddLead = async () => {
    if (!newLeadCompany.trim()) return;
    try {
      setSystemStatus('processing');
      const res = await fetch(`${API_BASE_URL}/api/leads/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: newLeadCompany })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      await fetchLeads();
      setSystemStatus('idle');
      setShowAddModal(false);
      setNewLeadCompany("");
    } catch (err) {
       alert(err.message);
       setSystemStatus('error');
    }
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
      } else {
        setSystemStatus('error');
      }
    } catch (err) {
      setSystemStatus('error');
    }
  };


  const regenerateLeads = async () => {
    setSystemStatus('processing');
    try {
      await fetch(`${API_BASE_URL}/api/leads/generate`, { method: 'POST' });
      await fetchLeads();
      setSystemStatus('idle');
    } catch (err) {
      setSystemStatus('error');
    }
  };

  return (
    <div className="page-container">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Lead Manager</h1>
          <p className="header-desc">Consolidated intent groups ready for conversion</p>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            <Plus size={18} />
            New Lead
          </button>
          <button className="btn btn-outline" onClick={regenerateLeads} style={{background: 'rgba(255,255,255,0.05)', color: 'white', border: '1px solid var(--glass-border)'}}>
            <TrendingUp size={18} />
            Sync Intelligence
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner glass">
          <AlertCircle size={20} color="var(--accent-danger)" />
          <span>Error connecting to Intelligence API: {error}</span>
          <button className="btn btn-text btn-sm" onClick={fetchLeads}>Retry</button>
        </div>
      )}

      <div className="leads-list">
        {loading ? (
          <div className="empty-state"><div className="loader"></div></div>
        ) : leads.length > 0 ? (
          leads.map(lead => (
            <LeadCard 
              key={lead._id} 
              lead={lead} 
              isExpanded={expandedLead === lead._id}
              onToggle={() => setExpandedLead(expandedLead === lead._id ? null : lead._id)}
              onPromote={() => handlePromote(lead._id)}
              onDelete={() => setDeletingLead(lead)}
              refresh={fetchLeads}
            />
          ))
        ) : !error && (
          <div className="empty-state glass">
            <Users size={48} />
            <h3>No leads are available currently</h3>
            <p>Try syncing intelligence or scanning new signals to populate your list.</p>
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
        message={`Are you sure you want to delete the lead for "${deletingLead?.company}"? This will drop it from the pipeline and instantly archive the company registry.`}
        confirmText="Delete & Archive Company"
        type="danger"
      />

      <style jsx>{`
        .leads-list {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .error-banner {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem 1.5rem;
          margin-bottom: 2rem;
          background: rgba(239, 68, 68, 0.1);
          border-color: rgba(239, 68, 68, 0.2);
          font-weight: 600;
        }
        .btn-sm { padding: 0.4rem 0.8rem; font-size: 0.8rem; }

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

const LeadCard = ({ lead, isExpanded, onToggle, onPromote, refresh, onDelete }) => {
  return (
    <div className={`lead-card glass animate-fade-in ${isExpanded ? 'expanded' : ''}`}>
      <div className="lead-main" onClick={onToggle}>
        <div className="lead-info">
          <div className="company-info">
            <h3 className="outfit">{lead.company}</h3>
            <span className="signal-count">{lead.signal_ids?.length || 0} Signals Linked</span>
          </div>
          <div className="relevance-group">
            <span className="relevance-label">Intent Score</span>
            <div className="score-row">
              <span className="relevance-value outfit">{Math.round(lead.relevance || 0)}%</span>
              <div className="relevance-bar">
                <div className="relevance-fill" style={{ width: `${lead.relevance || 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lead-actions">
          <div className="action-buttons">
            <button 
              className="btn btn-primary btn-sm" 
              onClick={(e) => { e.stopPropagation(); onPromote(); }}
            >
              Promote to Deal
            </button>
            <button 
              className="btn-icon mini delete-card-btn" 
              onClick={(e) => { e.stopPropagation(); onDelete(); }}
              title="Delete Lead & Archive"
            >
              <Trash2 size={16} />
            </button>
            <button className="btn-icon mini" title="View Logs">
              {isExpanded ? <ChevronUp size={20} /> : <MessageSquare size={18} />}
            </button>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="lead-details animate-fade-in">
          <LogManager 
            type="lead" 
            parentId={lead._id} 
            logs={lead.logs || []} 
            onUpdate={refresh} 
          />
        </div>
      )}

      <style jsx>{`
        .lead-card {
          overflow: hidden;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .lead-main {
          padding: 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
        }

        .lead-info {
          display: flex;
          align-items: center;
          gap: 5rem;
          flex: 1;
        }

        .company-info h3 {
          font-size: 1.6rem;
          font-weight: 800;
          text-transform: capitalize;
          margin-bottom: 0.4rem;
        }

        .signal-count {
          font-size: 0.9rem;
          color: var(--accent-primary);
          font-weight: 800;
          background: rgba(99, 102, 241, 0.1);
          padding: 0.25rem 0.75rem;
          border-radius: 6px;
        }

        .relevance-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          flex: 1;
          max-width: 300px;
        }

        .relevance-label {
          font-size: 0.75rem;
          font-weight: 800;
          text-transform: uppercase;
          color: var(--text-muted);
          letter-spacing: 0.08em;
        }

        .score-row {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .relevance-value {
          font-size: 1.5rem;
          font-weight: 900;
          color: var(--text-main);
          min-width: 60px;
        }

        .relevance-bar {
          height: 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          overflow: hidden;
          flex: 1;
        }

        .relevance-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--accent-primary), var(--accent-info));
          border-radius: 4px;
        }

        .lead-actions {
          display: flex;
          align-items: center;
        }
        
        .action-buttons {
          display: flex;
          gap: 1.25rem;
          align-items: center;
        }

        .delete-card-btn { color: var(--text-muted); opacity: 0; pointer-events: none; transition: all 0.2s; }
        .lead-main:hover .delete-card-btn { opacity: 1; pointer-events: auto; }
        .delete-card-btn:hover { color: var(--accent-danger); border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.1); }

        .lead-details {
          padding: 0 2rem 2.5rem 2rem;
          border-top: 1px solid var(--glass-border);
          background: rgba(0, 0, 0, 0.15);
        }
      `}</style>
    </div>
  );
};

export const LogManager = ({ type, parentId, logs, onUpdate }) => {
  const [newLog, setNewLog] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, logId: null });

  const handleAddLog = async () => {
    if (!newLog.trim()) return;
    setSubmitting(true);
    try {
      const endpoint = `${API_BASE_URL}/api/${type}s/${parentId}/logs`;
      await fetch(endpoint, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newLog })
      });
      setNewLog("");
      onUpdate();
    } catch (err) {
      console.error("Log add failed", err);
    } finally {
      setSubmitting(false);
    }
  };

  const confirmDelete = async () => {
    const { logId } = deleteModal;
    try {
      const endpoint = `${API_BASE_URL}/api/${type}s/${parentId}/logs/${logId}`;
      const res = await fetch(endpoint, { method: 'DELETE' });
      if (res.ok) onUpdate();
    } catch (err) {
      console.error("Log delete failed", err);
    } finally {
      setDeleteModal({ isOpen: false, logId: null });
    }
  };

  return (
    <div className="log-manager">
      <ConfirmModal 
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, logId: null })}
        onConfirm={confirmDelete}
        title="Delete Intelligence Log"
        message="This action will permanently remove this entry from the activity timeline. This cannot be undone."
      />
      <div className="log-header">
        <History size={18} />
        <span className="outfit">Activity Timeline</span>
      </div>

      <div className="logs-list">
        {logs.length > 0 ? (
          logs.map((log, index) => (
            <div key={log.log_id || index} className="log-entry glass">
              <div className="log-bullet"></div>
              <div className="log-content">
                <div className="log-meta">
                  <span className="log-type">{log.type?.replace(/_/g, ' ')}</span>
                  <span className="log-time">{new Date(log.timestamp).toLocaleString()}</span>
                </div>
                <p className="log-msg">{log.message}</p>
              </div>
              <button 
                className="btn-icon mini delete-btn" 
                onClick={() => setDeleteModal({ isOpen: true, logId: log.log_id })}
                title="Delete Intelligence Log"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))
        ) : (
          <p className="empty-logs">No activity recorded yet.</p>
        )}
      </div>

      <div className="add-log-box glass">
        <input 
          type="text" 
          placeholder="Append intelligence or status..." 
          value={newLog}
          onChange={(e) => setNewLog(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAddLog()}
        />
        <button className="btn btn-primary btn-icon mini" onClick={handleAddLog} disabled={submitting}>
          {submitting ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
        </button>
      </div>

      <style jsx>{`
        .log-manager {
          padding-top: 2rem;
        }
        .log-header {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          color: var(--text-muted);
          font-size: 0.9rem;
          font-weight: 800;
          margin-bottom: 1.5rem;
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }
        .logs-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin-bottom: 2rem;
        }
        .log-entry {
          display: flex;
          gap: 1.25rem;
          padding: 1.25rem;
          position: relative;
          background: rgba(255, 255, 255, 0.02);
        }
        .log-bullet {
          width: 10px;
          height: 10px;
          background: var(--accent-primary);
          border-radius: 50%;
          margin-top: 6px;
          box-shadow: 0 0 10px var(--accent-primary);
        }
        .log-content { flex: 1; }
        .log-meta {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.4rem;
        }
        .log-type {
          font-size: 0.8rem;
          text-transform: uppercase;
          font-weight: 900;
          color: var(--accent-primary);
        }
        .log-time {
          font-size: 0.75rem;
          color: var(--text-muted);
          font-weight: 600;
        }
        .log-msg { font-size: 1rem; color: var(--text-main); line-height: 1.5; }
        .empty-logs { color: var(--text-muted); font-size: 1rem; text-align: center; padding: 2rem; }
        
        .add-log-box {
          display: flex;
          padding: 0.6rem 0.6rem 0.6rem 1.25rem;
          gap: 0.75rem;
          border-radius: 14px;
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid var(--glass-border);
        }
        .add-log-box input {
          background: none;
          border: none;
          flex: 1;
          color: white;
          outline: none;
          font-size: 1rem;
        }
        .delete-btn { opacity: 0; color: var(--accent-danger); transition: 0.2s; border-color: rgba(239, 68, 68, 0.2); }
        .delete-btn:hover { background: rgba(239, 68, 68, 0.1); border-color: var(--accent-danger); }
        .log-entry:hover .delete-btn { opacity: 1; }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
};

export default LeadsPage;
