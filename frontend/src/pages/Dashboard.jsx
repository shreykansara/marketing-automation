import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Zap,
  Users,
  Target,
  AlertCircle,
  ArrowUpRight,
  TrendingUp,
  MailWarning
} from 'lucide-react';

import { API_BASE_URL } from '../config';

const Dashboard = () => {
  const [stats, setStats] = useState({ signals: 0, leads: 0, deals: 0 });
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [sRes, lRes, dRes, eRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/signals`),
        fetch(`${API_BASE_URL}/api/leads`),
        fetch(`${API_BASE_URL}/api/deals`),
        fetch(`${API_BASE_URL}/api/emails`)
      ]);

      const signals = await sRes.json();
      const leads = await lRes.json();
      const deals = await dRes.json();
      const emails = await eRes.json();

      setStats({
        signals: signals.length,
        leads: leads.length,
        deals: deals.length
      });

      const newAlerts = [];
      const highSignals = signals.sort((a, b) => b.relevance_score - a.relevance_score).filter(s => s.relevance_score >= 80).slice(0, 2);
      highSignals.forEach(s => newAlerts.push({
        id: `sig-${s._id}`,
        type: 'signal',
        title: 'High Intent Signal',
        subject: s.title,
        severity: 'high',
        target: '/explore'
      }));

      const unlogged = emails.filter(e => e.is_logged === false).slice(0, 2);
      unlogged.forEach(e => newAlerts.push({
        id: `em-${e._id}`,
        type: 'email',
        title: 'Unlogged Response',
        subject: e.subject,
        severity: 'medium',
        target: '/emails'
      }));

      setAlerts(newAlerts);
      setLoading(false);
    } catch (err) {
      console.error("Failed to load dashboard data", err);
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Growth Command</h1>
          <p className="header-desc">AI-driven sales intelligence overview</p>
        </div>
        <div className="last-sync glass">
          <TrendingUp size={16} color="var(--accent-success)" />
          <span>Real-time Pulse</span>
        </div>
      </header>

      <div className="stats-grid">
        <StatCard
          icon={<Zap size={24} color="var(--accent-primary)" />}
          label="Market Signals"
          value={stats.signals}
          onClick={() => navigate('/explore')}
        />
        <StatCard
          icon={<Users size={24} color="var(--accent-warning)" />}
          label="Qualified Leads"
          value={stats.leads}
          onClick={() => navigate('/leads')}
        />
        <StatCard
          icon={<Target size={24} color="var(--accent-success)" />}
          label="Active Pipeline"
          value={stats.deals}
          onClick={() => navigate('/deals')}
        />
      </div>

      <div className="dashboard-sections">
        <section className="alerts-section">
          <div className="section-header">
            <h3 className="outfit"><AlertCircle size={20} /> Priority Alerts</h3>
          </div>

          <div className="alerts-list">
            {loading ? (
              <div className="empty-state">Loading alerts...</div>
            ) : alerts.length > 0 ? (
              alerts.map(alert => (
                <div
                  key={alert.id}
                  className="alert-item glass glass-hover animate-fade-in"
                  onClick={() => navigate(alert.target)}
                >
                  <div className={`alert-icon ${alert.severity}`}>
                    {alert.type === 'signal' ? <Zap size={18} /> : <MailWarning size={18} />}
                  </div>
                  <div className="alert-content">
                    <div className="alert-meta">
                      <span className="alert-title">{alert.title}</span>
                      <span className="alert-tag">Action Required</span>
                    </div>
                    <p className="alert-subject">{alert.subject}</p>
                  </div>
                  <ArrowUpRight size={18} className="alert-arrow" />
                </div>
              ))
            ) : (
              <div className="empty-state glass">
                <p>System monitoring active. No critical alerts.</p>
              </div>
            )}
          </div>
        </section>
      </div>

      <style>{`
        .last-sync {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1.25rem;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .section-header h3 {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 1.5rem;
        }

        .btn-text {
          background: none;
          border: none;
          color: var(--accent-primary);
          font-weight: 700;
          font-size: 0.95rem;
          cursor: pointer;
        }

        .alerts-list {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .alert-item {
          display: flex;
          align-items: center;
          gap: 1.5rem;
          padding: 1.5rem;
          cursor: pointer;
        }

        .alert-icon {
          width: 44px;
          height: 44px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .alert-icon.high { background: rgba(239, 68, 68, 0.1); color: var(--accent-danger); }
        .alert-icon.medium { background: rgba(245, 158, 11, 0.1); color: var(--accent-warning); }

        .alert-content { flex: 1; }

        .alert-meta {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.35rem;
        }

        .alert-title { font-weight: 800; font-size: 1.05rem; }
        .alert-tag { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; }
        .alert-subject { font-size: 0.95rem; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 800px; }

        .alert-arrow { color: var(--text-muted); opacity: 0; transition: all 0.3s ease; }
        .alert-item:hover .alert-arrow { opacity: 1; transform: translate(4px, -4px); color: var(--text-main); }
      `}</style>
    </div>
  );
};

const StatCard = ({ icon, label, value, onClick }) => (
  <div className="stat-card glass glass-hover animate-fade-in" onClick={onClick} style={{ cursor: 'pointer' }}>
    <div className="stat-header">
      {icon}
    </div>
    <div className="stat-main">
      <span className="stat-value outfit">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
    <style jsx>{`
      .stat-card {
        padding: 2rem;
        display: flex;
        flex-direction: column;
        gap: 2rem;
        transition: all 0.3s ease;
      }
      .stat-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent-primary);
        background: rgba(15, 18, 50, 0.4);
      }
      .stat-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
      }
      .stat-trend {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--accent-success);
        background: rgba(16, 185, 129, 0.1);
        padding: 0.4rem 0.75rem;
        border-radius: 8px;
      }
      .stat-main {
        display: flex;
        flex-direction: column;
      }
      .stat-value {
        font-size: 2.75rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 0.5rem;
      }
      .stat-label {
        font-size: 1.05rem;
        color: var(--text-muted);
        font-weight: 600;
      }
    `}</style>
  </div>
);

export default Dashboard;
