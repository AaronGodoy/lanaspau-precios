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

import CustomersPage from '../pages/CustomersPage';

function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AdminRoute({ children }: { children: React.ReactElement }) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.rol !== 'administrador') return <Navigate to="/sales" replace />;
  return children;
}

function IndexRedirect() {
  const { user } = useAuth();
  if (user?.rol === 'administrador') return <Navigate to="/dashboard" replace />;
  return <Navigate to="/sales" replace />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<IndexRedirect />} />
      <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="sales" element={<SalesPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        
        <Route path="dashboard" element={<AdminRoute><DashboardPage /></AdminRoute>} />
        <Route path="products" element={<AdminRoute><ProductsPage /></AdminRoute>} />
        <Route path="suppliers" element={<AdminRoute><SuppliersPage /></AdminRoute>} />
        <Route path="customers" element={<AdminRoute><CustomersPage /></AdminRoute>} />
        <Route path="calculator" element={<AdminRoute><CalculatorPage /></AdminRoute>} />
        <Route path="reports" element={<AdminRoute><ReportsPage /></AdminRoute>} />
        <Route path="settings" element={<AdminRoute><SettingsPage /></AdminRoute>} />
        <Route path="users" element={<AdminRoute><UsersPage /></AdminRoute>} />
      </Route>
    </Routes>
  );
}
