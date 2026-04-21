import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Compass, 
  Users, 
  Briefcase, 
  Mail,
  Building2,
  LogOut,
  User as UserIcon
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar glass">
      <div className="sidebar-header">
        <div className="logo-container">
          <img src="/logo.png" alt="Blostem Logo" className="logo-img glass" />
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

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-avatar">
            <UserIcon size={16} />
          </div>
          <div className="user-info">
            <span className="user-name">{user?.full_name || 'User'}</span>
            <span className="user-email">{user?.email}</span>
          </div>
        </div>
        <button className="logout-btn glass-hover" onClick={logout} title="Log Out">
          <LogOut size={18} />
        </button>
      </div>

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

        .sidebar-footer {
          padding: 1.25rem;
          border-top: 1px solid var(--glass-border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.5rem;
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex: 1;
          overflow: hidden;
        }

        .user-avatar {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.05);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--accent-primary);
          flex-shrink: 0;
        }

        .user-info {
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .user-name {
          font-size: 0.85rem;
          font-weight: 700;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .user-email {
          font-size: 0.7rem;
          color: var(--text-muted);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .logout-btn {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          border: none;
          background: none;
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.2s;
        }

        .logout-btn:hover {
          color: var(--accent-danger);
          background: rgba(239, 68, 68, 0.1);
        }

        .logo-container {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .logo-img {
          width: 34px;
          height: 34px;
          object-fit: contain;
          padding: 4px;
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
          .logo-text, .user-info, .sidebar-footer { display: none; }
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
