import { LogOut } from 'lucide-react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../hooks/useAuth';

const titles: Record<string, string> = {
  '/dashboard': 'Dashboard general',
  '/products': 'Catalogo de productos',
  '/calculator': 'Calculadora de precios',
  '/reports': 'Reportes exportables',
  '/settings': 'Configuracion comercial',
  '/users': 'Gestion de usuarios',
};

export default function AppLayout() {
  const location = useLocation();
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen p-4 lg:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 lg:flex-row">
        <Sidebar />
        <main className="flex-1 space-y-6">
          <header className="rounded-3xl border border-slate-200 bg-white px-6 py-5 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-slate-500">Panel de trabajo</p>
                <h1 className="text-2xl font-semibold text-slate-900">{titles[location.pathname] || 'Lanas Pau Pricing'}</h1>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-800">{user?.nombre}</p>
                  <p className="text-xs uppercase tracking-wide text-slate-500">{user?.rol}</p>
                </div>
                <button type="button" onClick={logout} className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50">
                  <LogOut size={16} />
                  Salir
                </button>
              </div>
            </div>
          </header>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
