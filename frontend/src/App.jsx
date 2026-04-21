import React, { useState } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ExplorePage from './pages/ExplorePage';
import LeadsPage from './pages/LeadsPage';
import DealsPage from './pages/DealsPage';
import EmailPage from './pages/EmailPage';
import CompaniesPage from './pages/CompaniesPage';
import LoginPage from './pages/LoginPage';
import { AuthProvider, useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="auth-page">
        <div className="loader"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const AppContent = () => {
  const [systemStatus, setSystemStatus] = useState('idle');
  const { user } = useAuth();

  return (
    <div className="app-shell">
      {user && <Sidebar systemStatus={systemStatus} />}
      
      <main className={user ? "main-content" : "auth-content"}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/" element={
            <ProtectedRoute><Dashboard /></ProtectedRoute>
          } />
          <Route path="/explore" element={
            <ProtectedRoute><ExplorePage setSystemStatus={setSystemStatus} /></ProtectedRoute>
          } />
          <Route path="/leads" element={
            <ProtectedRoute><LeadsPage setSystemStatus={setSystemStatus} /></ProtectedRoute>
          } />
          <Route path="/deals" element={
            <ProtectedRoute><DealsPage setSystemStatus={setSystemStatus} /></ProtectedRoute>
          } />
          <Route path="/emails" element={
            <ProtectedRoute><EmailPage setSystemStatus={setSystemStatus} /></ProtectedRoute>
          } />
          <Route path="/companies" element={
            <ProtectedRoute><CompaniesPage setSystemStatus={setSystemStatus} /></ProtectedRoute>
          } />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
