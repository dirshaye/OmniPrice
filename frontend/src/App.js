import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import Dashboard from './pages/dashboard/Dashboard';
import Products from './pages/products/Products';
import Pricing from './pages/pricing/Pricing';
import Competitors from './pages/competitors/Competitors';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/*"
        element={
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/products" element={<Products />} />
                <Route path="/pricing" element={<Pricing />} />
                <Route path="/competitors" element={<Competitors />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </Layout>
        }
      />
    </Routes>
  );
}

export default App;