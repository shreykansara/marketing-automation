import React from 'react';
import { Briefcase, ChevronRight } from 'lucide-react';

const DealList = ({ deals, selectedDeal, onSelectDeal }) => {
  return (
    <div className="glass-panel" style={{ width: '380px' }}>
      <div className="panel-header">
        <div className="panel-title">Active Pipeline</div>
        <div style={{ fontSize: '0.7rem', color: 'var(--brand-primary)' }}>
          {deals.length} Open
        </div>
      </div>
      
      <div className="signal-list">
        {deals.length === 0 ? (
          <div className="empty-state">No active deals. Promote a lead to start.</div>
        ) : (
          deals.map((deal) => (
            <div 
              key={deal._id} 
              className={`signal-card ${selectedDeal?._id === deal._id ? 'active' : ''}`}
              onClick={() => onSelectDeal(deal)}
              style={{ 
                borderLeft: selectedDeal?._id === deal._id ? '4px solid var(--brand-primary)' : '1px solid var(--border-glass)',
                background: selectedDeal?._id === deal._id ? 'var(--bg-accent)' : 'var(--bg-card)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className={`status-dot status-${deal.status}`} />
                  <span style={{ fontWeight: 800, textTransform: 'capitalize' }}>{deal.company_name}</span>
                </div>
                <ChevronRight size={16} color="var(--text-muted)" />
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', fontSize: '0.7rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>
                  Intent: <span style={{ color: 'var(--brand-primary)', fontWeight: 800 }}>{deal.intent_score}</span>
                </span>
                <span style={{ color: 'var(--text-muted)' }}>
                  {deal.emails_sent?.length || 0} Emails
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DealList;
