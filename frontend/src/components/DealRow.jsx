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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <tr 
      className={`deal-row ${selected ? 'selected' : ''}`}
      onClick={() => onClick(deal)}
    >
      <td className="company-cell">
        <div className="company-logo-placeholder">
          <Building2 size={16} color="white" />
        </div>
        {deal.company}
      </td>
      <td>{deal.stage}</td>
      <td>{formatCurrency(deal.value)}</td>
      <td>{getStatusBadge(deal.status)}</td>
      <td>{new Date(deal.last_activity).toLocaleDateString()}</td>
    </tr>
  );
};

export default DealRow;
