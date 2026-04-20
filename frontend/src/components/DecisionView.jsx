import React, { useState } from 'react';
import { Mail, Send, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

const DecisionView = ({ deal, onRefresh }) => {
  const [generating, setGenerating] = useState(false);
  const [emailDraft, setEmailDraft] = useState({ subject: '', body: '' });
  const [recipient, setRecipient] = useState('contact@company.com');
  const [syncing, setSyncing] = useState(false);

  // Reset state when selection changes
  React.useEffect(() => {
    if (deal?._id) {
      setEmailDraft({ subject: '', body: '' });
    }
  }, [deal?._id]);

  if (!deal) {
    return (
      <div className="empty-state" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Select a deal to activate intelligence
      </div>
    );
  }

  const handleSync = async () => {
    setSyncing(true);
    try {
      await fetch(`${API_BASE_URL}/api/deals/${deal._id}/sync`, { method: 'POST' });
      onRefresh();
    } catch (e) {
      console.error("Sync failed", e);
    }
    setSyncing(false);
  };

  const handleApproveSuggestion = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/deals/${deal._id}/suggestions/approve`, { method: 'POST' });
      if (res.ok) onRefresh();
    } catch (e) {
      console.error("Approval failed", e);
    }
  };

  const handleRejectSuggestion = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/deals/${deal._id}/suggestions/reject`, { method: 'POST' });
      if (res.ok) onRefresh();
    } catch (e) {
      console.error("Rejection failed", e);
    }
  };

  const handleGenerate = async () => {
    setEmailDraft({ subject: '', body: '' }); // Immediate visual feedback
    setGenerating(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/deals/${deal._id}/generate-outreach`, { method: 'POST' });
      const data = await res.json();
      setEmailDraft(data);
    } catch (e) {
      console.error("AI Generation failed", e);
    }
    setGenerating(false);
  };

  const handleSaveDraft = async () => {
    try {
      const res = await fetch(API_BASE_URL + '/api/emails/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: emailDraft.subject,
          body: emailDraft.body,
          recipient: recipient,
          deal_id: deal._id
        })
      });
      if (res.ok) {
        alert("Draft saved to Email Hub.");
      }
    } catch (e) {
      console.error("Draft save failed", e);
    }
  };

  return (
    <div className="deal-view">
      <div className="premium-card">
        {/* HEADER */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, textTransform: 'capitalize' }}>{deal.company_name}</h1>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
              <span className={`status-badge status-${deal.status}`}>{deal.status}</span>
              <button 
                className="btn-premium btn-ghost btn-sm" 
                onClick={handleSync}
                style={{ height: 'auto', padding: '0.2rem 0.5rem', fontSize: '0.7rem' }}
              >
                {syncing ? "Checking..." : "Sync Inbox"}
              </button>
            </div>
          </div>
          <div className="intent-pill">{deal.intent_score}</div>
        </div>

        {/* AI SUGGESTION BANNER */}
        {deal.status_suggestion && (
          <div className="suggestion-banner" style={{ marginBottom: '2rem', padding: '1.5rem', borderRadius: '12px', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid var(--brand-primary)' }}>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Sparkles color="var(--brand-primary)" size={24} />
              <div style={{ flex: 1 }}>
                <h4 style={{ fontWeight: 700, color: 'var(--brand-primary)' }}>AI Recommendation</h4>
                <p style={{ margin: '0.5rem 0', fontSize: '0.9rem' }}>
                  Based on the latest reply, AI suggests moving status to <strong style={{ textTransform: 'uppercase' }}>{deal.status_suggestion.suggested_status}</strong>.
                </p>
                <div style={{ fontSize: '0.8rem', fontStyle: 'italic', opacity: 0.8, marginBottom: '1rem' }}>
                  "{deal.status_suggestion.reason}"
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button className="btn-premium btn-primary btn-sm" onClick={handleApproveSuggestion}>Apply Status</button>
                  <button className="btn-premium btn-ghost btn-sm" onClick={handleRejectSuggestion}>Dismiss</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* REPLIES HISTORY */}
        {deal.emails_received?.length > 0 && (
          <div style={{ marginBottom: '2rem' }}>
            <label className="panel-title" style={{ marginBottom: '1rem', display: 'block' }}>Inbound Intelligence</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {deal.emails_received.map((email, i) => (
                <div key={i} style={{ padding: '1rem', borderRadius: '8px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.8rem' }}>From: {email.from}</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{new Date(email.timestamp).toLocaleString()}</span>
                  </div>
                  <div style={{ fontSize: '0.85rem' }}>{email.body}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* OUTREACH ENGINE */}
        <div className="outreach-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Mail size={18} color="#38bdf8" />
              Outreach Engine
            </h3>
            <button 
              className="btn-premium btn-ghost btn-sm"
              onClick={handleGenerate}
              disabled={generating}
            >
              {generating ? "Calibrating..." : "Regenerate Draft"}
            </button>
          </div>

          {!emailDraft.subject && !generating ? (
            <div style={{ textAlign: 'center', padding: '3rem', border: '1px dashed var(--border-glass)', borderRadius: '12px' }}>
              <Sparkles size={32} color="var(--text-dim)" style={{ marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-dim)' }}>No draft active. Start the intelligence engine.</p>
              <button className="btn-premium btn-primary" style={{ margin: '1.5rem auto' }} onClick={handleGenerate}>
                Generate AI Outreach
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <label className="panel-title" style={{ marginBottom: '0.5rem', display: 'block' }}>Recipient</label>
                <input 
                  type="text" 
                  className="email-editor" 
                  style={{ minHeight: 'auto', padding: '0.8rem' }}
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                />
              </div>
              <div>
                <label className="panel-title" style={{ marginBottom: '0.5rem', display: 'block' }}>Subject</label>
                <input 
                  type="text" 
                  className="email-editor" 
                  style={{ minHeight: 'auto', padding: '0.8rem' }}
                  value={emailDraft.subject}
                  onChange={(e) => setEmailDraft({...emailDraft, subject: e.target.value})}
                />
              </div>
              <div>
                <label className="panel-title" style={{ marginBottom: '0.5rem', display: 'block' }}>Body Content</label>
                <textarea 
                  className="email-editor"
                  value={emailDraft.body}
                  onChange={(e) => setEmailDraft({...emailDraft, body: e.target.value})}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                <button 
                  className="btn-premium btn-ghost" 
                  onClick={handleSaveDraft}
                >
                  Save Draft
                </button>
                <a 
                  href={`https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(recipient)}&su=${encodeURIComponent(emailDraft.subject)}&body=${encodeURIComponent(emailDraft.body)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-premium btn-primary"
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}
                >
                  <Send size={18} /> Open in Gmail
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DecisionView;
