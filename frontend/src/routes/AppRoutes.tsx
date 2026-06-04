import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from '../layouts/AppLayout';
import { useAuth } from '../hooks/useAuth';
import CalculatorPage from '../pages/CalculatorPage';
import DashboardPage from '../pages/DashboardPage';
import InventoryPage from '../pages/InventoryPage';
import LoginPage from '../pages/LoginPage';
import ProductsPage from '../pages/ProductsPage';
import ReportsPage from '../pages/ReportsPage';
import SalesPage from '../pages/SalesPage';
import SettingsPage from '../pages/SettingsPage';
import SuppliersPage from '../pages/SuppliersPage';
import UsersPage from '../pages/UsersPage';

function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="sales" element={<SalesPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="suppliers" element={<SuppliersPage />} />
        <Route path="calculator" element={<CalculatorPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="users" element={<UsersPage />} />
      </Route>
    </Routes>
  );
}
