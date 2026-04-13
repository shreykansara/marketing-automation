import React from 'react';
import { Building2 } from 'lucide-react';

const DealRow = ({ deal, selected, onClick }) => {
  const getStatusBadge = (status) => {
    // Handling case where status is 'At Risk' -> splitting on space and keeping first word for class
    const statusClass = status.replace(/\s+/g, '');
    return (
      <span className={`badge badge-status-${statusClass}`}>
        {status}
      </span>
    );
  };
  
  const getPriorityBadge = (priority) => {
    let color = 'green';
    if (priority === 'High') color = 'red';
    else if (priority === 'Medium') color = 'orange';
    
    return (
      <span style={{ 
        padding: '0.2rem 0.6rem', 
        borderRadius: '12px', 
        fontSize: '0.75rem', 
        fontWeight: 'bold',
        backgroundColor: color === 'red' ? '#fee2e2' : color === 'orange' ? '#fef3c7' : '#dcfce7',
        color: color === 'red' ? '#991b1b' : color === 'orange' ? '#92400e' : '#166534',
        border: `1px solid ${color === 'red' ? '#f87171' : color === 'orange' ? '#fbbf24' : '#86efac'}`
      }}>
        {priority || 'Low'}
      </span>
    );
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const isHighPriority = deal.priority_level === 'High' || deal.status === 'Stalled';

  return (
    <tr 
      className={`deal-row ${selected ? 'selected' : ''}`}
      onClick={() => onClick(deal)}
      style={isHighPriority ? { borderLeft: '4px solid #ef4444', backgroundColor: selected ? 'var(--bg-hover)' : '#fff5f5' } : {}}
    >
      <td className="company-cell">
        <div className="company-logo-placeholder">
          <Building2 size={16} color="white" />
        </div>
        {deal.company}
      </td>
      <td>{getPriorityBadge(deal.priority_level)}</td>
      <td>{deal.stage}</td>
      <td>{formatCurrency(deal.value)}</td>
      <td>{getStatusBadge(deal.status)}</td>
      <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={deal.risk_reason}>
        {deal.risk_reason}
      </td>
      <td>{new Date(deal.last_activity).toLocaleDateString()}</td>
    </tr>
  );
};

export default DealRow;
