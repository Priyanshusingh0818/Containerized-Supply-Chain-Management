import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import Items from './pages/Items';
import Transactions from './pages/Transactions';
import Analytics from './pages/Analytics';
import AuditLog from './pages/AuditLog';
import { SocketProvider } from './components/SocketProvider';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <SocketProvider>
        <div className="min-h-screen bg-gray-50">
          <Navbar user={user} onLogout={handleLogout} />
          <Toaster position="top-right" />
          <main className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/items" element={<Items user={user} />} />
              <Route path="/transactions" element={<Transactions user={user} />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/audit" element={<AuditLog />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </SocketProvider>
    </Router>
  );
}

export default App;