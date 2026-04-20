import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, UserPlus, Filter, Search, Mail } from 'lucide-react';
import { API_BASE_URL } from '../config';

const LeadManagement = ({ onConvertToDeal }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/leads`);
      const data = await res.json();
      setLeads(data);
    } catch (e) {
      console.error("Lead sync failed", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  return (
    <div className="leads-view">
      <div className="lead-header">
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Account Console</h1>
          <p style={{ color: 'var(--text-dim)' }}>Aggregated market intent by company</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="stat-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Target color="#38bdf8" />
            <div>
              <div className="stat-label">Identified Leads</div>
              <div className="stat-value">{leads.length}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="lead-table-wrapper">
        <table className="lead-table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Intent Score</th>
              <th>Priority</th>
              <th>Signals</th>
              <th>Categories</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="6" className="empty-state">Filtering market noise...</td></tr>
            ) : leads.length === 0 ? (
              <tr><td colSpan="6" className="empty-state">No qualifying leads detected yet.</td></tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead._id}>
                  <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{lead.company}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                      <div className="intent-pill" style={{ width: 36, height: 36, fontSize: '0.9rem' }}>
                        {lead.intent_score}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`score-pill`} style={{ 
                      background: lead.priority === 'high' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(148, 163, 184, 0.1)',
                      color: lead.priority === 'high' ? '#10b981' : 'var(--text-dim)'
                    }}>
                      {lead.priority}
                    </span>
                  </td>
                  <td className="mono">{lead.signal_count}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      {Object.keys(lead.categories || {}).map(cat => (
                        <span key={cat} style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>#{cat}</span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button 
                        className="btn-premium btn-primary btn-sm"
                        onClick={() => onConvertToDeal(lead._id)}
                      >
                        <UserPlus size={14} /> Promote
                      </button>
                      <a 
                        href="https://mail.google.com/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-premium btn-ghost btn-sm"
                        title="Open Gmail"
                        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '32px' }}
                      >
                        <Mail size={14} />
                      </a>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LeadManagement;
