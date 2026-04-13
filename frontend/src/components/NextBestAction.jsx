import React, { useState } from 'react';
import { Sparkles, Send, CheckCircle, AlertTriangle, Lightbulb, Zap } from 'lucide-react';

const NextBestAction = ({ deal, onActionTriggered }) => {
  const [loadingAction, setLoadingAction] = useState(false);

  if (!deal) {
    return (
      <div className="empty-state">
        <Sparkles size={32} />
        <p>Select a deal from the pipeline to see AI-driven recommendations and actions.</p>
      </div>
    );
  }

  const handleTriggerAction = async () => {
    setLoadingAction(true);
    try {
      const response = await fetch(`http://localhost:8000/api/deals/${deal.id}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_type: "fallback", // Generic logic ping to mitigate risk via activity trace in MVP
          stakeholder_name: null
        })
      });
      const data = await response.json();
      if (data.status === 'success') {
        onActionTriggered(); // Refresh deals
      }
    } catch (e) {
      console.error(e);
    }
    setLoadingAction(false);
  };

  return (
    <div className="action-panel">
      <div className="company-info" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{deal.company}</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Stage: <strong>{deal.stage}</strong> | Value: <strong>${deal.value ? deal.value.toLocaleString() : '0'}</strong>
          <br/>
          Activation Step: <strong style={{ color: "var(--brand-primary)", marginTop: '4px', display: 'inline-block' }}>{deal.activation_step || "Not Started"}</strong>
        </p>
      </div>
      
      <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Zap size={18} color="var(--brand-primary)" />
        AI Intelligence Panel
      </h4>

      <div className="action-card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: deal.status === "Active" ? 'var(--status-active)' : 'var(--status-risk)', fontWeight: 'bold', marginBottom: '0.25rem' }}>
            <AlertTriangle size={16} /> Problem Identified
          </div>
          <p style={{ color: 'var(--text-main)', fontSize: '0.95rem', marginLeft: '1.5rem' }}>
            {deal.risk_reason || "No immediate risk factors detected."}
          </p>
        </div>

        <div style={{ marginBottom: '1.25rem', padding: '1rem', backgroundColor: '#f0f9ff', borderRadius: '8px', border: '1px solid #bae6fd' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#0369a1', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            <Lightbulb size={16} /> Recommended Action
          </div>
          <p style={{ color: '#0c4a6e', fontSize: '1rem', fontWeight: '500', marginLeft: '1.5rem', marginBottom: '0.5rem' }}>
            {deal.next_action || "Monitor Deal"}
          </p>
          <div style={{ marginLeft: '1.5rem', fontSize: '0.8rem', color: '#0ea5e9', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Sparkles size={12} /> Confidence Score: <strong>{deal.action_confidence ? (deal.action_confidence * 100).toFixed(0) : 0}%</strong>
          </div>
        </div>

        <button 
          className="btn btn-primary"
          onClick={handleTriggerAction}
          disabled={loadingAction || (!deal.next_action || deal.next_action.includes("Monitor"))}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {loadingAction ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="loader" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>
              Processing...
            </span>
          ) : (
            <>
              <Send size={14} /> Simulate Action
            </>
          )}
        </button>
      </div>

      {deal.stakeholders && (
        <div style={{ marginTop: '2rem' }}>
          <h4 style={{ marginBottom: '1rem' }}>Key Stakeholders</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {deal.stakeholders.map((s, i) => (
              <div key={i} style={{ padding: '0.8rem', backgroundColor: 'var(--bg-base)', borderRadius: '6px', border: '1px solid var(--border-light)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <strong>{s.name}</strong>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{s.role}</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  <span style={{ color: s.contacted ? 'var(--status-active)' : 'var(--text-secondary)' }}>Contacted: {s.contacted ? 'Yes' : 'No'}</span>
                  <span style={{ color: s.responded ? 'var(--status-active)' : (!s.contacted ? 'var(--text-secondary)' : 'var(--status-risk)') }}>Responded: {s.responded ? 'Yes' : 'No'}</span>
                  {s.intent_score !== undefined && <span>Intent: {s.intent_score}%</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default NextBestAction;
