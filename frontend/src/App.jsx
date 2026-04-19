import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ExplorePage from './pages/ExplorePage';
import LeadsPage from './pages/LeadsPage';
import DealsPage from './pages/DealsPage';
import EmailPage from './pages/EmailPage';
import CompaniesPage from './pages/CompaniesPage';

function App() {
  const [systemStatus, setSystemStatus] = useState('idle'); // 'idle', 'processing', 'error'

  return (
    <Router>
      <div className="app-shell">
        <Sidebar systemStatus={systemStatus} />
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route 
              path="/explore" 
              element={<ExplorePage setSystemStatus={setSystemStatus} />} 
            />
            <Route 
              path="/leads" 
              element={<LeadsPage setSystemStatus={setSystemStatus} />} 
            />
            <Route 
              path="/deals" 
              element={<DealsPage setSystemStatus={setSystemStatus} />} 
            />
            <Route 
              path="/emails" 
              element={<EmailPage setSystemStatus={setSystemStatus} />} 
            />
            <Route 
              path="/companies" 
              element={<CompaniesPage setSystemStatus={setSystemStatus} />} 
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
