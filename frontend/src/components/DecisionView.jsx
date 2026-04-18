import React, { useState } from 'react';
import { Mail, Send, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';

const DecisionView = ({ deal, onRefresh }) => {
  const [generating, setGenerating] = useState(false);
  const [sending, setSending] = useState(false);
  const [emailDraft, setEmailDraft] = useState({ subject: '', body: '' });
  const [recipient, setRecipient] = useState('contact@company.com');

  // Reset state when selection changes
  // Must be called BEFORE the early return to follow Rules of Hooks
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

  const handleGenerate = async () => {
    setEmailDraft({ subject: '', body: '' }); // Immediate visual feedback
    setGenerating(true);
    try {
      const res = await fetch(`http://localhost:8000/api/deals/${deal._id}/generate-outreach`, { method: 'POST' });
      const data = await res.json();
      setEmailDraft(data);
    } catch (e) {
      console.error("AI Generation failed", e);
    }
    setGenerating(false);
  };

  const handleSend = async () => {
    setSending(true);
    try {
      const res = await fetch(`http://localhost:8000/api/deals/${deal._id}/send-outreach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to_email: recipient,
          subject: emailDraft.subject,
          body: emailDraft.body
        })
      });
      if (res.ok) {
        alert("Email sent successfully via SMTP!");
        onRefresh();
        setEmailDraft({ subject: '', body: '' });
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (e) {
      console.error("Send failed", e);
    }
    setSending(false);
  };

  return (
    <div className="deal-view">
      <div className="premium-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, textTransform: 'capitalize' }}>{deal.company_name}</h1>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
              <span className={`status-badge status-${deal.status}`}>{deal.status}</span>
              <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>Intention: {deal.intent_score}/100</span>
            </div>
          </div>
          <div className="intent-pill">{deal.intent_score}</div>
        </div>

        <div className="outreach-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={18} color="#38bdf8" />
              AI Outreach Engine
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
              <Mail size={32} color="var(--text-dim)" style={{ marginBottom: '1rem' }} />
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
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button 
                  className="btn-premium btn-primary" 
                  onClick={handleSend}
                  disabled={sending}
                >
                  <Send size={18} /> {sending ? "Dispatching..." : "Send via SMTP"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DecisionView;
