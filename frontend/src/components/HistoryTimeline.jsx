import React from 'react';
import { History, CheckCircle2, XCircle, Clock, Info } from 'lucide-react';

const HistoryTimeline = ({ history }) => {
  const getOutcomeClass = (outcome) => {
    if (outcome === 'replied') return 'outcome-replied';
    if (outcome === 'ignored' || outcome === 'bounced') return 'outcome-ignored';
    return 'outcome-pending';
  };

  const hasPattern = history?.filter(e => e.outcome === 'ignored').length >= 2;

  return (
    <div className="history-panel">
      <div className="history-header">
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <History size={18} /> Persistent Memory
        </h3>
      </div>
      
      {hasPattern && (
        <div className="pattern-insight">
          <div style={{ fontWeight: 'bold', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Info size={14} /> Behavioral Pattern
          </div>
          System detected 2+ ignored attempts. Escalation logic is now priority.
        </div>
      )}

      <div className="timeline">
        {history && history.length > 0 ? (
          history.slice().reverse().map((entry, idx) => (
            <div key={entry.id || idx} className="timeline-item">
              <div className={`timeline-dot ${getOutcomeClass(entry.outcome)}`}></div>
              <div className="timeline-content">
                <div className="timeline-action">
                  {entry.action === 'trigger_outreach' ? 'Outreach Sent' : 'Escalation Triggered'}
                </div>
                <div className="timeline-meta">
                   Intent: {entry.intent} &bull; Attempt #{entry.attempt_number}
                </div>
                <div className="mono" style={{ fontSize: '0.65rem', marginTop: '0.5rem', opacity: 0.6 }}>
                  {entry.outcome.toUpperCase()} &bull; {new Date(entry.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '2rem' }}>
            No historical actions recorded for this account.
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryTimeline;
