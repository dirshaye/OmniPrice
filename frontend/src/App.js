import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import Dashboard from './pages/dashboard/Dashboard';
import Products from './pages/products/Products';
import Pricing from './pages/pricing/Pricing';
import Competitors from './pages/competitors/Competitors';
import Analytics from './pages/Analytics';
import LLMPlayground from './pages/llm/LLMPlayground';
import { useAuth } from './contexts/AuthContext';

function ProtectedApp() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/competitors" element={<Competitors />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/llm" element={<LLMPlayground />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return null;
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/dashboard" replace /> : <RegisterPage />}
      />
      <Route
        path="/*"
        element={user ? <ProtectedApp /> : <Navigate to="/login" replace />}
      />
    </Routes>
  );
}

export default App;
