import React, { useState, useEffect } from 'react';
import { 
  Mail, 
  Search, 
  ChevronRight, 
  Clock, 
  User, 
  AlertCircle,
  Inbox,
  Send,
  Building2,
  ArrowRight,
  Tag
} from 'lucide-react';
import { API_BASE_URL } from '../config';

const EmailPage = () => {
  const [emails, setEmails] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchEmails();
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/companies`);
      const data = await res.json();
      setCompanies(data);
    } catch(err) {}
  };

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/emails`);
      const data = await res.json();
      setEmails(data);
      if (data.length > 0 && !selectedEmail) {
        setSelectedEmail(data[0]);
      }
    } catch (err) {
      console.error("Email fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredEmails = emails.filter(e => 
    e.subject?.toLowerCase().includes(search.toLowerCase()) ||
    e.sender?.toLowerCase().includes(search.toLowerCase()) ||
    e.receiver?.toLowerCase().includes(search.toLowerCase()) ||
    e.company_name?.toLowerCase().includes(search.toLowerCase())
  );

  const [tagCompanyId, setTagCompanyId] = useState("");
  const [tagging, setTagging] = useState(false);
  const [isEditingTag, setIsEditingTag] = useState(false);
  
  const [suggestedLog, setSuggestedLog] = useState("");
  const [isGeneratingLog, setIsGeneratingLog] = useState(false);
  const [showLogInput, setShowLogInput] = useState(false);

  useEffect(() => {
    if (selectedEmail) {
       setTagCompanyId("");
       setIsEditingTag(false);
       setSuggestedLog("");
       setShowLogInput(false);
    }
  }, [selectedEmail]);

  const handleSuggestLog = async () => {
    setIsGeneratingLog(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/emails/${selectedEmail._id}/suggest-log`);
      const data = await res.json();
      setSuggestedLog(data.suggestion);
      setShowLogInput(true);
    } catch(e) {
      console.error(e);
    } finally {
      setIsGeneratingLog(false);
    }
  };

  const handleConfirmLog = async () => {
    try {
      setTagging(true); // Reusing tagging state for busy indicator
      const res = await fetch(`${API_BASE_URL}/api/emails/${selectedEmail._id}/log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: suggestedLog })
      });
      if (res.ok) {
        await fetchEmails();
        setSelectedEmail(prev => ({ ...prev, is_logged: true, is_loggable: false }));
        setShowLogInput(false);
      }
    } catch(e) {
      console.error(e);
    } finally {
      setTagging(false);
    }
  };

  const handleTagSubmit = async () => {
    if (!tagCompanyId) return;
    setTagging(true);
    try {
      let extEmail = selectedEmail.sender;
      if (selectedEmail.sender.toLowerCase().includes('blostem')) {
         extEmail = selectedEmail.receiver;
      }
      
      const payload = { company_id: tagCompanyId, company_email: extEmail };
      const res = await fetch(`${API_BASE_URL}/api/emails/${selectedEmail._id}/company`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        await fetchEmails();
        setSelectedEmail(prev => ({ 
           ...prev, 
           company_id: tagCompanyId, 
           company_name: data.company_name 
        }));
        setIsEditingTag(false);
      }
    } catch(e) {
      console.error(e);
    } finally {
      setTagging(false);
    }
  };

  return (
    <div className="page-container email-page">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Communication Engine</h1>
          <p className="header-desc">Unified inbox for all prospect interactions</p>
        </div>
        
        <div className="search-bar glass">
          <Search size={16} color="var(--text-muted)" />
          <input 
            type="text" 
            placeholder="Search conversations..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </header>

      <div className="email-layout">
        <aside className="email-list-pane glass">
          {loading ? (
            <div className="empty-state"><div className="loader"></div></div>
          ) : filteredEmails.length > 0 ? (
            filteredEmails.map(email => (
              <div 
                key={email._id} 
                className={`email-item glass-hover ${selectedEmail?._id === email._id ? 'active' : ''} ${!email.is_logged ? 'unlogged' : ''}`}
                onClick={() => setSelectedEmail(email)}
              >
                <div className="item-header">
                  <span className="item-sender">{email.sender}</span>
                  <span className="item-time">{new Date(email.timestamp).toLocaleDateString()}</span>
                </div>
                <div style={{marginBottom: '0.25rem'}}>
                  {email.company_name ? (
                     <span className="inline-tag active"><Building2 size={10} /> {email.company_name}</span>
                  ) : (
                     <span className="inline-tag inactive"><Tag size={10} /> Unlinked</span>
                  )}
                </div>
                <h4 className="item-subject">{email.subject}</h4>
                <p className="item-snippet">{email.body?.substring(0, 60)}...</p>
                {email.is_loggable && (
                  <div className="unlogged-badge">
                    <AlertCircle size={10} />
                    Needs Logging
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="empty-state">
              <Inbox size={32} />
              <p>No messages found</p>
            </div>
          )}
        </aside>

        <main className="email-view-pane glass">
          {selectedEmail ? (
            <div className="email-content animate-fade-in">
              <div className="view-header">
                <h2 className="outfit">{selectedEmail.subject}</h2>
                <div className="view-meta">
                  <div className="meta-row">
                    <span className="meta-label">From:</span>
                    <span className="meta-value">{selectedEmail.sender}</span>
                  </div>
                  <div className="meta-row">
                    <span className="meta-label">To:</span>
                    <span className="meta-value">{selectedEmail.receiver}</span>
                  </div>
                  <div className="meta-row">
                    <span className="meta-label">Date:</span>
                    <span className="meta-value">{new Date(selectedEmail.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="meta-row" style={{marginTop: '0.5rem'}}>
                    <span className="meta-label">Company:</span>
                    {selectedEmail.company_name ? (
                       <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                         <span className="company-badge"><Building2 size={12} /> {selectedEmail.company_name}</span>
                         <button className="btn-text" onClick={() => setIsEditingTag(!isEditingTag)} style={{fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)'}}>
                           Manage Link
                         </button>
                       </div>
                    ) : (
                       <span className="company-badge unlinked"><Tag size={12} /> Unlinked</span>
                    )}
                  </div>
                </div>
              </div>

              {(!selectedEmail.company_id || isEditingTag) && (
                <div className="action-banner glass auth-tag-banner">
                  <Tag size={20} color="var(--text-main)" style={{marginTop: '8px'}} />
                  <div className="manual-tag-form">
                    <div style={{marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.95rem'}}>
                        {isEditingTag ? 'Relink Conversation' : 'Link Conversation to Company'}
                    </div>
                    <div style={{fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem'}}>
                       {isEditingTag 
                         ? "Selecting a new company will securely unlink this email from the previous record." 
                         : "Assigning this email automatically pushes the external email address to the company's registry."}
                    </div>
                    <div className="tag-controls">
                      <select 
                        className="glass-input small" 
                        value={tagCompanyId} 
                        onChange={e => setTagCompanyId(e.target.value)}
                      >
                         <option value="">Select Company...</option>
                         {companies.map(c => <option key={c._id} value={c._id}>{c.name}</option>)}
                      </select>
                      <button 
                        className="btn btn-primary btn-sm" 
                        disabled={!tagCompanyId || tagging}
                        onClick={handleTagSubmit}
                      >
                         {tagging ? 'Linking...' : 'Link Email'}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedEmail.is_loggable && (
                <div className="action-banner glass log-banner animate-fade-in">
                  <Clock size={20} color="var(--accent-primary)" style={{marginTop: '4px'}} />
                  <div style={{flex: 1}}>
                    {!showLogInput ? (
                      <div className="banner-flex">
                        <div className="banner-text">
                          <strong>Active Relationship:</strong> This communication is linked to <strong>{selectedEmail.company_name}</strong>. Generate an AI summary to log this interaction to the pipeline.
                        </div>
                        <button className="btn btn-primary btn-sm" onClick={handleSuggestLog} disabled={isGeneratingLog}>
                          {isGeneratingLog ? 'Summarizing...' : 'Log Activity'} <ArrowRight size={14} />
                        </button>
                      </div>
                    ) : (
                      <div className="log-confirm-box">
                        <div style={{marginBottom: '0.75rem', fontWeight: 600, fontSize: '0.9rem'}}>Suggested Timeline Entry:</div>
                        <textarea 
                          className="glass-input log-textarea"
                          value={suggestedLog}
                          onChange={(e) => setSuggestedLog(e.target.value)}
                        />
                        <div className="log-footer">
                          <button className="btn-text" onClick={() => setShowLogInput(false)} style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Cancel</button>
                          <button className="btn btn-primary btn-sm" onClick={handleConfirmLog} disabled={tagging}>
                            {tagging ? 'Logging...' : 'Confirm & Push to Pipeline'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="view-body">
                {selectedEmail.body}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <Mail size={48} />
              <h3>Select a conversation</h3>
              <p>Choose an email from the left to read the full content.</p>
            </div>
          )}
        </main>
      </div>

      <style jsx>{`
        .email-page { height: calc(100vh - 4rem); display: flex; flex-direction: column; }
        .email-layout { display: flex; flex: 1; gap: 1.5rem; min-height: 0; }
        
        /* List Pane */
        .email-list-pane {
          width: 380px;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
          background: rgba(15, 18, 30, 0.4);
        }

        .email-item {
          padding: 1.25rem;
          border-bottom: 1px solid var(--glass-border);
          cursor: pointer;
          transition: 0.2s;
          position: relative;
        }

        .email-item.active { background: rgba(255, 255, 255, 0.05); }
        .email-item.unlogged { border-l: 3px solid var(--accent-warning); }

        .item-header { display: flex; justify-content: space-between; margin-bottom: 0.25rem; font-size: 0.75rem; color: var(--text-muted); }
        .item-sender { font-weight: 700; color: var(--accent-primary); }
        .item-subject { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .item-snippet { font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; }

        .unlogged-badge {
          display: flex;
          align-items: center;
          gap: 0.35rem;
          margin-top: 0.5rem;
          font-size: 0.65rem;
          font-weight: 800;
          color: var(--accent-warning);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        /* View Pane */
        .email-view-pane { flex: 1; overflow-y: auto; background: rgba(15, 18, 30, 0.2); }
        .email-content { padding: 2.5rem; }
        .view-header { border-bottom: 1px solid var(--glass-border); padding-bottom: 2rem; margin-bottom: 2rem; }
        .view-header h2 { font-size: 1.8rem; margin-bottom: 1.5rem; }
        .view-meta { display: flex; flex-direction: column; gap: 0.5rem; }
        .meta-row { display: flex; align-items: center; gap: 1rem; font-size: 0.9rem; }
        .meta-label { color: var(--text-muted); font-weight: 600; width: 60px; }
        .meta-value { font-weight: 500; }

        .action-banner {
          display: flex;
          align-items: center;
          gap: 1.25rem;
          padding: 1.25rem;
          margin-bottom: 2rem;
          background: rgba(245, 158, 11, 0.1);
          border-color: rgba(245, 158, 11, 0.2);
        }
        .banner-text { font-size: 0.9rem; flex: 1; }
        .btn-sm { padding: 0.5rem 1rem; font-size: 0.85rem; }

        .btn-text {
          background: none;
          border: none;
          cursor: pointer;
        }
        .btn-text:hover { color: var(--accent-primary) !important; }

        .view-body {
          font-size: 1.05rem;
          line-height: 1.7;
          color: #e2e8f0;
          white-space: pre-wrap;
        }

        @media (max-width: 1200px) {
          .email-list-pane { width: 300px; }
        }

        .search-bar {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 0.5rem 1rem;
          background: rgba(15, 18, 50, 0.4);
          border: 1px solid var(--glass-border);
          border-radius: 10px;
          flex: 1;
          max-width: 400px;
        }

        .search-bar input {
          background: none;
          border: none;
          color: white;
          width: 100%;
          outline: none;
          font-size: 0.95rem;
        }

        .inline-tag {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.65rem;
          font-weight: 800;
          text-transform: uppercase;
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
        }
        .inline-tag.active { background: rgba(99, 102, 241, 0.15); color: var(--accent-primary); border: 1px solid rgba(99, 102, 241, 0.3); }
        .inline-tag.inactive { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); }
        
        .company-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          font-size: 0.8rem;
          font-weight: 800;
          padding: 0.3rem 0.8rem;
          border-radius: 6px;
          background: rgba(99, 102, 241, 0.15);
          color: var(--accent-primary);
          border: 1px solid rgba(99, 102, 241, 0.3);
        }
        .company-badge.unlinked { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); border-color: rgba(255, 255, 255, 0.1); }

        .auth-tag-banner {
          background: rgba(255, 255, 255, 0.02);
          border: 1px dashed rgba(255, 255, 255, 0.2);
          align-items: flex-start;
        }
        
        .manual-tag-form { flex: 1; }
        
        .banner-flex { display: flex; align-items: center; gap: 1.5rem; width: 100%; }
        .log-confirm-box { width: 100%; }
        .log-textarea {
          width: 100%;
          min-height: 80px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          border-radius: 10px;
          color: white;
          padding: 0.75rem;
          font-family: inherit;
          font-size: 0.95rem;
          resize: vertical;
          margin-bottom: 1rem;
        }
        .log-footer { display: flex; justify-content: flex-end; gap: 1rem; align-items: center; }

        .tag-controls {
          display: flex;
          gap: 1rem;
          align-items: center;
          flex-wrap: wrap;
        }

        .glass-input.small {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--glass-border);
          border-radius: 8px;
          padding: 0.4rem 0.8rem;
          color: white;
          font-size: 0.85rem;
          outline: none;
        }
        .glass-input.small option { background: var(--bg-deep); }
      `}</style>
    </div>
  );
};

export default EmailPage;
