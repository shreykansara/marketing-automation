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
  ArrowRight
} from 'lucide-react';

const EmailPage = () => {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/emails');
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
    e.receiver?.toLowerCase().includes(search.toLowerCase())
  );

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
                <h4 className="item-subject">{email.subject}</h4>
                <p className="item-snippet">{email.body?.substring(0, 60)}...</p>
                {!email.is_logged && (
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
                </div>
              </div>

              {!selectedEmail.is_logged && (
                <div className="action-banner glass">
                  <AlertCircle size={20} color="var(--accent-warning)" />
                  <div className="banner-text">
                    <strong>Action Required:</strong> This interaction hasn't been logged to a Lead or Deal yet. Update the relevant timeline to ensure accurate intelligence.
                  </div>
                  <button className="btn btn-primary btn-sm">
                    Log Activity <ArrowRight size={14} />
                  </button>
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
      `}</style>
    </div>
  );
};

export default EmailPage;
