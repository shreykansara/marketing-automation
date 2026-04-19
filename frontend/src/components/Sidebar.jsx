import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Compass, 
  Users, 
  Briefcase, 
  Mail,
  Building2
} from 'lucide-react';

const Sidebar = () => {
  return (
    <aside className="sidebar glass">
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="logo-icon glass">B</div>
          <span className="logo-text outfit">Blostem AI</span>
        </div>
      </div>

      <nav className="sidebar-links">
        <SidebarLink to="/" icon={<LayoutDashboard size={18} />} label="Dashboard" />
        <SidebarLink to="/explore" icon={<Compass size={18} />} label="Explore Signals" />
        <SidebarLink to="/leads" icon={<Users size={18} />} label="Lead Manager" />
        <SidebarLink to="/deals" icon={<Briefcase size={18} />} label="Active Pipeline" />
        <SidebarLink to="/emails" icon={<Mail size={18} />} label="Communications" />
        <SidebarLink to="/companies" icon={<Building2 size={18} />} label="Company Registry" />
      </nav>

      <style jsx>{`
        .sidebar {
          width: var(--sidebar-width);
          height: calc(100vh - 2rem);
          margin: 1rem;
          position: fixed;
          left: 0;
          top: 0;
          display: flex;
          flex-direction: column;
          z-index: 100;
          background: rgba(15, 18, 30, 0.85);
          overflow: hidden;
        }

        .sidebar-header {
          padding: 1.5rem 1.25rem;
        }

        .logo-container {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .logo-icon {
          width: 34px;
          height: 34px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--accent-primary);
          color: white;
          font-weight: 900;
          font-size: 1rem;
          border-radius: 8px;
        }

        .logo-text {
          font-weight: 800;
          font-size: 1.1rem;
          letter-spacing: -0.5px;
        }

        .sidebar-links {
          flex: 1;
          padding: 0 0.75rem;
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }

        /* Mobile Adjustments */
        @media (max-width: 1024px) {
          .sidebar { width: var(--sidebar-collapsed); }
          .logo-text { display: none; }
          .logo-container { justify-content: center; }
        }

        @media (max-width: 640px) {
          .sidebar { display: none; }
        }
      `}</style>
    </aside>
  );
};

const SidebarLink = ({ to, icon, label }) => (
  <NavLink
    to={to}
    className={({ isActive }) => `nav-item glass-hover ${isActive ? 'active' : ''}`}
  >
    <div className="icon-wrapper">{icon}</div>
    <span className="label-text">{label}</span>
    <style jsx>{`
      .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0.85rem;
        text-decoration: none;
        color: var(--text-muted);
        border-radius: 10px;
        transition: all 0.2s ease;
      }

      .nav-item.active {
        color: var(--text-main);
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid var(--glass-border);
      }

      .nav-item:hover {
        color: var(--text-main);
      }

      .icon-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.7;
      }

      .nav-item.active .icon-wrapper {
        color: var(--accent-primary);
        opacity: 1;
      }

      .label-text {
        font-size: 0.85rem;
        font-weight: 600;
      }
    `}</style>
  </NavLink>
);

export default Sidebar;
