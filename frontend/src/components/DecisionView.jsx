import React, { useState } from 'react';
import { Send, AlertTriangle, ShieldAlert, Clock, Sparkles, User, Mail, ChevronRight } from 'lucide-react';

const DecisionView = ({ deal, onTriggerEvaluate }) => {
  const [loadingAction, setLoadingAction] = useState(false);

  if (!deal) {
    return (
      <div className="main-view mono" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)' }}>
        <div style={{ textAlign: 'center' }}>
          <Sparkles size={48} style={{ marginBottom: '1rem', opacity: 0.3 }} />
          <p>SELECT A DEAL TO INITIALIZE INTELLIGENCE VIEW</p>
        </div>
      </div>
    );
  }

  const handleRunCycle = async () => {
    setLoadingAction(true);
    try {
      await onTriggerEvaluate(deal.id);
    } catch (e) { console.error(e); }
    setLoadingAction(false);
  };

  const getActionColor = (action) => {
    if (action === 'trigger_outreach') return 'var(--brand-primary)';
    if (action === 'escalate') return 'var(--status-escalated)';
    if (action === 'delay_action') return 'var(--status-stalled)';
    return 'var(--text-main)';
  };

  const isEscalation = deal.decision === 'escalate';
  const isOutreach = deal.decision === 'trigger_outreach';
  const isDelay = deal.decision === 'delay_action';

  return (
    <div className="main-view">
      <div className="top-nav">
        <div className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
           WORKSPACE / {deal.company.toUpperCase()} / <span style={{ color: 'var(--text-main)' }}>ADAPTIVE_LOOP_STATE</span>
        </div>
        <button className="btn btn-ghost" onClick={handleRunCycle} disabled={loadingAction}>
          <ShieldAlert size={16} /> {loadingAction ? "Evaluating..." : "Run Intelligence Cycle"}
        </button>
      </div>

      <div className="decision-container">
        <div className="decision-hero">
          <div className="decision-label">Current System Decision</div>
          <div className="decision-action" style={{ color: getActionColor(deal.decision) }}>
            {deal.decision?.replace('_', ' ').toUpperCase() || "MONITORING"}
          </div>
          <div className="decision-reasoning">
            {deal.next_action || "System is observing market signals for relevant triggers."}
          </div>

          <div className="decision-stats">
            <div className="stat-card">
              <div className="stat-label">Health State</div>
              <div className="stat-value" style={{ color: `var(--status-${deal.status?.toLowerCase()})` }}>
                {deal.status}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Urgency Score</div>
              <div className="stat-value">{deal.urgency_score}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Decision Reason</div>
              <div className="stat-value mono" style={{ fontSize: '0.9rem', color: 'var(--brand-accent)' }}>
                {deal.decision_reason || "INITIAL_STATE"}
              </div>
            </div>
          </div>
        </div>

        {/* Action Detail Panels */}
        {isEscalation && (
          <div className="stat-card" style={{ borderLeft: '4px solid var(--status-escalated)' }}>
             <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <User size={18} color="var(--status-escalated)" />
                Escalation Target
             </h4>
             <p style={{ color: 'var(--text-main)', fontSize: '1.1rem' }}>
                Route to: <strong className="mono">{deal.escalate_to || "manual_review"}</strong>
             </p>
             <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                System has detected a deadlock or high-priority failure that requires human intervention.
             </p>
          </div>
        )}

        {isDelay && (
          <div className="stat-card" style={{ borderLeft: '4px solid var(--status-stalled)' }}>
             <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <Clock size={18} color="var(--status-stalled)" />
                Cooldown Logic
             </h4>
             <p style={{ color: 'var(--text-main)', fontSize: '1.1rem' }}>
                Remaining: <strong className="mono">72h WINDOW ACTIVE</strong>
             </p>
             <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                Automation is paused to prevent repetition and maintain domain reputation.
             </p>
          </div>
        )}

        {/* If Outreach was recently generated, the history will show it, 
            but we could show a "Pending Sequence" preview if we added that to the deal object.
            For now, the user sees the decision to trigger it. */}
      </div>
    </div>
  );
};

export default DecisionView;
