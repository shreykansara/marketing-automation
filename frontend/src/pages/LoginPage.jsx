import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User, Key, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handlePrototypeAccess = () => {
    setEmail('test.automation@blostem.ai');
    setPassword('blostem2026');
    setIsLogin(true);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const result = await login(email, password);
        if (result.success) {
          navigate('/');
        } else {
          setError(result.message);
        }
      } else {
        const result = await register({ email, password, full_name: fullName, invite_code: inviteCode });
        if (result.success) {
          setIsLogin(true);
          setError('Registration successful! Please login.');
        } else {
          setError(result.message);
        }
      }
    } catch (err) {
      setError('An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card glass animate-fade-in">
        <div className="auth-header">
          <div className="logo-box">
             <img src="/logo.png" alt="Blostem" className="auth-logo" />
          </div>
          <h1 className="outfit">{isLogin ? 'Welcome Back' : 'Join Blostem'}</h1>
          <p className="auth-subtitle">{isLogin ? 'Intelligence-driven sales automation' : 'Invite-only early access'}</p>
        </div>

        {error && (
          <div className={`auth-alert ${error.includes('successful') ? 'success' : 'error'}`}>
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="input-group">
              <User className="input-icon" size={18} />
              <input 
                type="text" 
                placeholder="Full Name" 
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="input-group">
            <Mail className="input-icon" size={18} />
            <input 
              type="email" 
              placeholder="Email Address" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <Lock className="input-icon" size={18} />
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {!isLogin && (
            <div className="input-group invite">
              <Key className="input-icon" size={18} />
              <input 
                type="text" 
                placeholder="Invitation Code" 
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                required
              />
            </div>
          )}

          <button className="auth-submit btn btn-primary" disabled={loading}>
            {loading ? <Loader2 className="animate-spin" size={18} /> : (
              <>
                {isLogin ? 'Login Intelligence' : 'Unlock Access'}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          {isLogin && (
            <div className="prototype-hint glass-hover" onClick={handlePrototypeAccess}>
              <span className="outfit">PROTOTYPE ACCESS</span>
              <p>One-click auto-fill for MVP testing</p>
            </div>
          )}
          <button className="btn-text" onClick={() => { setIsLogin(!isLogin); setError(''); }}>
            {isLogin ? "Don't have an invite? Join Waitlist" : "Already have an account? Login"}
          </button>
        </div>
      </div>

      <style jsx>{`
        .auth-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), transparent),
                      radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.1), transparent),
                      var(--bg-deep);
          padding: 2rem;
        }

        .auth-card {
          width: 100%;
          max-width: 420px;
          padding: 3rem;
          background: rgba(20, 24, 38, 0.6);
          border-radius: 28px;
        }

        .auth-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }

        .logo-box {
          width: 64px;
          height: 64px;
          margin: 0 auto 1.5rem;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          border-radius: 16px;
          padding: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .auth-logo { width: 100%; height: 100%; object-fit: contain; }

        .auth-header h1 {
          font-size: 2rem;
          font-weight: 800;
          margin-bottom: 0.5rem;
        }

        .auth-subtitle {
          color: var(--text-muted);
          font-size: 0.95rem;
        }

        .auth-alert {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          border-radius: 12px;
          font-size: 0.85rem;
          margin-bottom: 2rem;
        }

        .auth-alert.error {
          background: rgba(239, 68, 68, 0.1);
          color: #fca5a5;
          border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .auth-alert.success {
          background: rgba(16, 185, 129, 0.1);
          color: #6ee7b7;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .auth-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .input-group {
          position: relative;
        }

        .input-icon {
          position: absolute;
          left: 1rem;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-muted);
          pointer-events: none;
        }

        .input-group input {
          width: 100%;
          padding: 1rem 1rem 1rem 3rem;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          border-radius: 14px;
          color: white;
          outline: none;
          transition: all 0.2s;
          font-size: 0.95rem;
        }

        .input-group input:focus {
          border-color: var(--accent-primary);
          background: rgba(255, 255, 255, 0.08);
          box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }

        .input-group.invite input {
          border-color: rgba(99, 102, 241, 0.3);
          background: rgba(99, 102, 241, 0.05);
        }

        .auth-submit {
          margin-top: 1.5rem;
          padding: 1rem;
          border-radius: 14px;
          font-size: 1rem;
          font-weight: 700;
        }

        .auth-footer {
          margin-top: 2rem;
          text-align: center;
        }

        .btn-text {
          background: none;
          border: none;
          color: var(--text-muted);
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          transition: color 0.2s;
        }

        .btn-text:hover {
          color: var(--accent-primary);
        }

        .prototype-hint {
          margin-bottom: 2rem;
          padding: 1.25rem;
          background: rgba(99, 102, 241, 0.05);
          border: 1px dashed rgba(99, 102, 241, 0.3);
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.2s;
          text-align: center;
        }

        .prototype-hint:hover {
          background: rgba(99, 102, 241, 0.1);
          border-style: solid;
          transform: translateY(-2px);
        }

        .prototype-hint span {
          display: block;
          font-size: 0.7rem;
          font-weight: 800;
          letter-spacing: 1px;
          color: var(--accent-primary);
          margin-bottom: 0.25rem;
        }

        .prototype-hint p {
          font-size: 0.8rem;
          color: var(--text-muted);
          margin: 0;
        }

        .animate-spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoginPage;
