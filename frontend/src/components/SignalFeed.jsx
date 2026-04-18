import React from 'react';
import { Radio, Zap, ExternalLink, Clock } from 'lucide-react';

const SignalFeed = ({ signals, loading }) => {
  return (
    <div className="glass-panel">
      <div className="panel-header">
        <div className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Radio size={14} className="pulsing" color="#38bdf8" />
          Live Market Intel
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--brand-primary)' }}>
          {signals.length} Active
        </div>
      </div>
      
      <div className="signal-list">
        {loading ? (
          <div className="empty-state">Syncing neural feed...</div>
        ) : signals.length === 0 ? (
          <div className="empty-state">No signals detected in current cycle.</div>
        ) : (
          signals.map((sig, idx) => (
            <div key={sig._id || idx} className="signal-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span className="signal-category">
                  {sig.category || 'general'}
                </span>
                <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--brand-primary)' }}>
                  {sig.relevance_score ? `${Math.round(sig.relevance_score)}%` : ''}
                </span>
              </div>
              
              <h3 className="signal-title">{sig.title}</h3>
              
              <div className="signal-meta">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Clock size={12} />
                  {new Date(sig.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <a href={sig.url} target="_blank" rel="noreferrer" style={{ color: 'inherit' }}>
                  <ExternalLink size={12} />
                </a>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SignalFeed;
