import { BarChart3, Calculator, FileSpreadsheet, Package, Settings, Users, ShoppingCart, AlertTriangle } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const baseItems = [
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { to: '/sales', label: 'Vender (POS)', icon: ShoppingCart },
  { to: '/products', label: 'Productos', icon: Package },
  { to: '/inventory', label: 'Control de Stock', icon: AlertTriangle },
  { to: '/calculator', label: 'Calculadora', icon: Calculator },
  { to: '/reports', label: 'Reportes', icon: FileSpreadsheet },
];

const adminItems = [
  { to: '/settings', label: 'Configuracion', icon: Settings },
  { to: '/users', label: 'Usuarios', icon: Users },
];

export default function Sidebar() {
  const { user } = useAuth();
  const items = user?.rol === 'administrador' ? [...baseItems, ...adminItems] : baseItems;
  return (
    <aside className="w-full rounded-3xl bg-slate-900 p-5 text-slate-100 lg:min-h-[calc(100vh-3rem)] lg:w-72">
      <div className="mb-8 flex items-center gap-3">
        <img src="/logo.png" alt="Lanas Pau Logo" className="w-14 h-14 object-cover rounded-full bg-white p-0.5" />
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-brand-100">Lanas Pau</p>
          <h1 className="mt-1 text-xl font-semibold">Precios de lana</h1>
        </div>
      </div>
      <nav className="space-y-2">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${isActive ? 'bg-brand-500 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}>
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
