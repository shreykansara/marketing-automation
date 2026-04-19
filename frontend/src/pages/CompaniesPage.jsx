import React, { useState, useEffect } from 'react';
import {
  Building2,
  Search,
  Mail,
  Plus,
  X,
  Save,
  ArrowRight,
  TrendingUp,
  History,
  Archive,
  RefreshCw,
  Info
} from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';

const CompaniesPage = ({ setSystemStatus }) => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingCompany, setEditingCompany] = useState(null);
  const [newEmail, setNewEmail] = useState("");
  const [archivingCompany, setArchivingCompany] = useState(null);
  const [viewFilter, setViewFilter] = useState('active');

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/companies');
      const data = await res.json();
      setCompanies(data);
    } catch (err) {
      console.error("Failed to fetch companies", err);
    } finally {
      setLoading(false);
    }
  };

  const saveEmails = async (companyId, emails) => {
    try {
      setSystemStatus('processing');
      const res = await fetch(`http://127.0.0.1:8000/api/companies/${companyId}/emails`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_ids: emails })
      });
      if (res.ok) {
        await fetchCompanies();
        setSystemStatus('idle');
        setEditingCompany(null);
      } else {
        setSystemStatus('error');
      }
    } catch (err) {
      setSystemStatus('error');
    }
  };

  const toggleArchiveStatus = async (company, force = false) => {
    if (!force && !company.is_archived && (company.is_deal_active || company.is_lead_active)) {
      setArchivingCompany(company);
      return;
    }

    try {
      setSystemStatus('processing');
      const res = await fetch(`http://127.0.0.1:8000/api/companies/${company._id}/archive`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_archived: !company.is_archived })
      });
      if (res.ok) {
        await fetchCompanies();
        setSystemStatus('idle');
        setArchivingCompany(null);
      } else {
        setSystemStatus('error');
      }
    } catch (err) {
      setSystemStatus('error');
    }
  };

  const filteredCompanies = companies.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesView = viewFilter === 'archived' ? c.is_archived : !c.is_archived;
    return matchesSearch && matchesView;
  });

  return (
    <div className="page-container">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Company Registry</h1>
          <p className="header-desc">Manage identities and contact information for all tracked entities</p>
        </div>

        <div className="header-actions">
          <div className="view-toggles glass">
            <button
              className={`toggle-btn ${viewFilter === 'active' ? 'active' : ''}`}
              onClick={() => setViewFilter('active')}
            >
              Active Organizations
            </button>
            <button
              className={`toggle-btn ${viewFilter === 'archived' ? 'active' : ''}`}
              onClick={() => setViewFilter('archived')}
            >
              Archived
            </button>
          </div>

          <div className="search-box glass">
            <Search size={18} />
            <input
              type="text"
              placeholder="Filter registry..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </header>

      <div className="registry-grid">
        {loading ? (
          <div className="empty-state"><div className="loader"></div></div>
        ) : filteredCompanies.length > 0 ? (
          filteredCompanies.map(company => (
            <div key={company._id} className={`company-card glass animate-fade-in ${company.is_archived ? 'archived' : ''}`}>
              <div className="card-header">
                <div className="brand-info">
                  <div className="company-icon glass">
                    <Building2 size={24} />
                  </div>
                  <div>
                    <h3 className="outfit capitalize-text">{company.name}</h3>
                    <div className="discovery-info">
                      <History size={12} />
                      <span>First seen: {new Date(company.first_seen_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="status-tags">
                  {company.is_archived && <span className="tag archive-tag">Archived</span>}
                  {!company.is_archived && company.is_deal_active && <span className="tag deal">Active Deal</span>}
                  {!company.is_archived && company.is_lead_active && <span className="tag lead">Qualified Lead</span>}
                  {!company.is_archived && !company.is_deal_active && !company.is_lead_active && <span className="tag registry">New Entry</span>}
                </div>
              </div>

              <div className="card-body">
                <div className="email-section">
                  <div className="section-header">
                    <Mail size={16} />
                    <span>Contact Directory</span>
                    <div className="action-buttons">
                      <button
                        className="icon-btn tooltip-host"
                        onClick={() => toggleArchiveStatus(company)}
                      >
                        {company.is_archived ? <RefreshCw size={15} /> : <Archive size={15} />}
                        <span className="tooltip">{company.is_archived ? "Restore Focus" : "Archive Company"}</span>
                      </button>
                      <button
                        className="edit-btn"
                        onClick={() => {
                          setEditingCompany(company);
                          setNewEmail("");
                        }}
                      >
                        Manage Contacts
                      </button>
                    </div>
                  </div>

                  <div className="email-chips">
                    {company.email_ids && company.email_ids.length > 0 ? (
                      company.email_ids.map((email, idx) => (
                        <div key={idx} className="email-chip glass">{email}</div>
                      ))
                    ) : (
                      <span className="no-comms">No contact information registered yet</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state glass">
            <Building2 size={48} />
            <h3>{viewFilter === 'active' ? 'No active companies found' : 'No archived companies'}</h3>
            <p>{viewFilter === 'active'
              ? 'The registry will automatically populate as new signals are ingested.'
              : 'Companies you archive will appear here.'}</p>
          </div>
        )}
      </div>

      {editingCompany && (
        <div className="modal-overlay animate-fade-in">
          <div className="modal-content glass animate-slide-up">
            <div className="modal-header">
              <h2 className="outfit">Manage Identity: {editingCompany.name}</h2>
              <button className="close-btn" onClick={() => setEditingCompany(null)}><X size={20} /></button>
            </div>

            <div className="modal-body">
              <div className="input-field">
                <label>Add New Email ID</label>
                <div className="inline-add">
                  <input
                    type="email"
                    placeholder="identity@company.com"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && newEmail) {
                        setEditingCompany({ ...editingCompany, email_ids: [...(editingCompany.email_ids || []), newEmail] });
                        setNewEmail("");
                      }
                    }}
                  />
                  <button
                    className="add-btn-circle"
                    onClick={() => {
                      if (newEmail) {
                        setEditingCompany({ ...editingCompany, email_ids: [...(editingCompany.email_ids || []), newEmail] });
                        setNewEmail("");
                      }
                    }}
                  >
                    <Plus size={20} />
                  </button>
                </div>
              </div>

              <div className="email-list-edit">
                <label>Registered Emails ({editingCompany.email_ids?.length || 0})</label>
                <div className="edit-chips-container">
                  {editingCompany.email_ids?.map((email, idx) => (
                    <div key={idx} className="edit-chip">
                      <span>{email}</span>
                      <button onClick={() => {
                        setEditingCompany({
                          ...editingCompany,
                          email_ids: editingCompany.email_ids.filter((_, i) => i !== idx)
                        });
                      }}><X size={14} /></button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="secondary-btn" onClick={() => setEditingCompany(null)}>Cancel</button>
              <button
                className="primary-btn"
                onClick={() => saveEmails(editingCompany._id, editingCompany.email_ids)}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={!!archivingCompany}
        onClose={() => setArchivingCompany(null)}
        onConfirm={() => toggleArchiveStatus(archivingCompany, true)}
        title="Warning: Pipeline Data Will Be Lost"
        message={`Are you sure you want to archive this company? This organization is currently active in your pipeline. Archiving will instantly delete their corresponding ${archivingCompany?.is_deal_active ? 'Deal' : 'Lead'} record.`}
        confirmText="Archive and Delete Pipeline Entry"
        type="danger"
      />

      <style jsx>{`
        .capitalize-text {
          text-transform: capitalize;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .search-box {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.6rem 1.25rem;
          border-radius: 12px;
          min-width: 300px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--glass-border);
        }

        .view-toggles {
          display: flex;
          padding: 0.25rem;
          border-radius: 12px;
          border: 1px solid var(--glass-border);
          background: rgba(0, 0, 0, 0.2);
        }

        .toggle-btn {
          background: transparent;
          border: none;
          color: var(--text-muted);
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-weight: 700;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .toggle-btn.active {
          background: rgba(255,255,255,0.05);
          color: white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        .search-box input {
          background: none;
          border: none;
          color: white;
          width: 100%;
          outline: none;
          font-size: 0.95rem;
        }

        .registry-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 1.5rem;
        }

        .company-card {
          padding: 1.5rem;
          transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .company-card.archived {
          opacity: 0.6;
          filter: grayscale(1);
        }
        .company-card:hover {
          transform: translateY(-4px);
          border-color: rgba(99, 102, 241, 0.3);
          opacity: 1;
          filter: grayscale(0);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1.5rem;
        }

        .brand-info {
           display: flex;
           gap: 1.25rem;
           align-items: center;
        }

        .company-icon {
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px;
          color: var(--accent-primary);
          background: rgba(255, 255, 255, 0.03);
        }

        .brand-info h3 {
          font-size: 1.35rem;
          font-weight: 800;
          margin-bottom: 0.2rem;
        }

        .discovery-info {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .status-tags {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
          align-items: flex-end;
        }

        .tag {
          font-size: 0.65rem;
          font-weight: 800;
          text-transform: uppercase;
          padding: 0.2rem 0.6rem;
          border-radius: 4px;
          letter-spacing: 0.05em;
        }
        .tag.deal { background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.2); }
        .tag.lead { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
        .tag.registry { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2); }
        .tag.archive-tag { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }

        .card-body {
          padding-top: 1.25rem;
          border-top: 1px solid var(--glass-border);
        }

        .section-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          font-weight: 800;
          color: var(--text-muted);
          margin-bottom: 0.75rem;
        }

        .action-buttons {
          margin-left: auto;
          display: flex;
          align-items: center;
          gap: 0.7rem;
        }

        .icon-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: color 0.2s;
        }
        .icon-btn:hover { color: var(--text-main); }
        
        .tooltip-host { position: relative; }
        .tooltip {
          position: absolute;
          bottom: 100%;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0,0,0,0.8);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.7rem;
          white-space: nowrap;
          pointer-events: none;
          opacity: 0;
          transition: opacity 0.2s;
        }
        .tooltip-host:hover .tooltip { opacity: 1; margin-bottom: 5px; }

        .edit-btn {
          background: none;
          border: none;
          color: var(--accent-primary);
          font-weight: 700;
          font-size: 0.75rem;
          cursor: pointer;
          padding: 0.25rem 0.5rem;
          border-radius: 6px;
        }
        .edit-btn:hover { background: rgba(255, 255, 255, 0.05); }

        .email-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .email-chip {
          padding: 0.4rem 0.85rem;
          font-size: 0.8rem;
          border-radius: 8px;
          border: 1px solid var(--glass-border);
          color: var(--text-main);
          font-weight: 600;
        }

        .no-comms {
          font-size: 0.8rem;
          color: var(--text-muted);
          font-style: italic;
        }

        /* Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 2rem;
        }

        .modal-content {
          background: rgba(20, 24, 40, 0.95);
          width: 100%;
          max-width: 500px;
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

        .close-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
        }

        .modal-body {
           display: flex;
           flex-direction: column;
           gap: 2rem;
        }

        .input-field label, .email-list-edit label {
          display: block;
          font-size: 0.8rem;
          font-weight: 800;
          text-transform: uppercase;
          color: var(--text-muted);
          margin-bottom: 0.75rem;
          letter-spacing: 0.05em;
        }

        .inline-add {
          display: flex;
          gap: 0.75rem;
        }

        .inline-add input {
          flex: 1;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          border-radius: 12px;
          padding: 0.85rem 1.25rem;
          color: white;
          outline: none;
          transition: border-color 0.2s;
        }
        .inline-add input:focus { border-color: var(--accent-primary); }

        .add-btn-circle {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background: var(--accent-primary);
          border: none;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }

        .edit-chips-container {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          max-height: 200px;
          overflow-y: auto;
        }

        .edit-chip {
           display: flex;
           align-items: center;
           justify-content: space-between;
           background: rgba(255, 255, 255, 0.05);
           padding: 0.75rem 1rem;
           border-radius: 10px;
        }

        .edit-chip span { font-size: 0.9rem; font-weight: 600; }
        .edit-chip button { background: none; border: none; color: var(--accent-danger); cursor: pointer; }

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
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
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

export default CompaniesPage;
