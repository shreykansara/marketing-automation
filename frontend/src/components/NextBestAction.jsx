import React, { useState } from 'react';
import { Sparkles, Send, CheckCircle } from 'lucide-react';

const NextBestAction = ({ deal, onActionTriggered }) => {
  const [loadingAction, setLoadingAction] = useState(null);

  if (!deal) {
    return (
      <div className="empty-state">
        <Sparkles size={32} />
        <p>Select a deal from the pipeline to see AI-driven recommendations and actions.</p>
      </div>
    );
  }

  const handleTriggerAction = async (action, idx) => {
    setLoadingAction(idx);
    try {
      const response = await fetch(`http://localhost:8000/api/deals/${deal.id}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_type: action.type,
          stakeholder_name: action.stakeholder_name || null
        })
      });
      const data = await response.json();
      if (data.status === 'success') {
        onActionTriggered(); // Refresh deals
      }
    } catch (e) {
      console.error(e);
    }
    setLoadingAction(null);
  };

  return (
    <div className="action-panel">
      <div className="company-info" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{deal.company}</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Stage: <strong>{deal.stage}</strong> | Value: <strong>${deal.value.toLocaleString()}</strong></p>
      </div>
      
      <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Sparkles size={18} color="var(--brand-primary)" />
        Recommended Actions
      </h4>

      {deal.next_actions && deal.next_actions.length > 0 ? (
        deal.next_actions.map((action, idx) => (
          <div key={idx} className="action-card">
            <div className="action-header">
              {action.type === 'follow_up' && "Follow-up Required"}
              {action.type === 'send_docs' && "Integration Docs Pending"}
              {action.type === 'schedule_call' && "Compliance Review"}
              {action.type === 'outreach' && "Initial Outreach"}
              {action.type === 'identify_stakeholder' && "Stakeholder Missing"}
              {action.type === 'monitor' && "On Track"}
            </div>
            <p className="action-desc">{action.message}</p>
            
            {action.type !== 'monitor' && action.type !== 'identify_stakeholder' && (
              <button 
                className="btn btn-primary"
                onClick={() => handleTriggerAction(action, idx)}
                disabled={loadingAction === idx}
              >
                {loadingAction === idx ? (
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
            )}
            {(action.type === 'monitor' || action.type === 'identify_stakeholder') && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                <CheckCircle size={14} color="var(--status-active)" /> 
                {action.type === 'identify_stakeholder' ? "Manual Action Required" : "System Monitoring"}
              </div>
            )}
          </div>
        ))
      ) : (
        <p className="action-desc">No specific actions recommended at this stage.</p>
      )}

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
                  <span>Contacted: {s.contacted ? 'Yes' : 'No'}</span>
                  <span>Responded: {s.responded ? 'Yes' : 'No'}</span>
                  <span>Intent: {s.intent_score}%</span>
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
