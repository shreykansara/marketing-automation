import React from 'react';
import { Target, AlertCircle, Clock, Zap } from 'lucide-react';

const DealList = ({ deals, selectedDeal, onSelectDeal }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="brand-title">
          <Target size={24} />
          <span>Blostem</span>
        </div>
      </div>
      <div className="deal-list">
        {deals.map(deal => {
          const isActive = selectedDeal?.id === deal.id;
          const statusClass = `status-dot status-${deal.status?.toLowerCase().replace(' ', '-') || 'active'}`;
          
          return (
            <div 
              key={deal.id} 
              className={`deal-card ${isActive ? 'active' : ''}`}
              onClick={() => onSelectDeal(deal)}
            >
              <div className="deal-card-header">
                <span className="deal-name">{deal.company}</span>
                <div className={statusClass}></div>
              </div>
              <div className="deal-meta">
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                   <Zap size={12} color={deal.urgency_score > 70 ? 'var(--status-risk)' : 'var(--text-dim)'} />
                   {deal.urgency_score}% Urgency
                </span>
                <span className="mono" style={{ fontSize: '0.65rem' }}>${(deal.value / 1000).toFixed(0)}k</span>
              </div>
            </div>
          );
        })}
        {deals.length === 0 && (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No deals found in pipeline.
          </div>
        )}
      </div>
    </div>
  );
};

export default DealList;
