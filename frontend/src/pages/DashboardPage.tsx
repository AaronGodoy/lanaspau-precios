import { useEffect, useState } from 'react';
import { Package, TrendingUp, ShoppingCart } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { api } from '../services/api';
import { formatCurrency } from '../utils/format';

interface DashboardStats {
  inversion_total: number;
  venta_potencial: number;
  ganancia_estimada: number;
  ventas_hoy: number;
  productos_hoy: number;
  grafico_ventas: { name: string; total: number }[];
  grafico_top_productos: { name: string; cantidad: number }[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean, payload?: { name: string; value: number }[], label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-xl shadow-lg border border-slate-100">
        <p className="font-semibold text-slate-900 mb-1">{label}</p>
        <p className="text-brand-600 font-medium">
          {payload[0].name === 'total' ? formatCurrency(payload[0].value) : `${payload[0].value} un.`}
        </p>
      </div>
    );
  }
  return null;
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/sales/stats/dashboard');
        setStats(res.data);
      } catch (err) {
        console.error("Error fetching dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-start gap-4">
          <div className="p-3 bg-brand-50 text-brand-600 rounded-2xl">
            <ShoppingCart size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Ventas de Hoy</p>
            <h3 className="text-2xl font-bold text-slate-900">{loading ? '...' : formatCurrency(stats?.ventas_hoy || 0)}</h3>
            <p className="text-xs text-brand-600 font-medium mt-1">{loading ? '...' : stats?.productos_hoy} productos vendidos</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-start gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
            <Package size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Inversión en Inventario</p>
            <h3 className="text-2xl font-bold text-slate-900">{loading ? '...' : formatCurrency(stats?.inversion_total || 0)}</h3>
            <p className="text-xs text-slate-500 mt-1">Costo total de stock actual</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-start gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-2xl">
            <TrendingUp size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Venta Potencial Total</p>
            <h3 className="text-2xl font-bold text-slate-900">{loading ? '...' : formatCurrency(stats?.venta_potencial || 0)}</h3>
            <p className="text-xs text-emerald-600 font-medium mt-1">
              Ganancia est.: {loading ? '...' : formatCurrency(stats?.ganancia_estimada || 0)}
            </p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Ventas Últimos 7 Días">
          <div className="h-[300px] mt-4">
            {!loading && stats?.grafico_ventas && (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.grafico_ventas} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorVentas" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} tickFormatter={(value) => `$${value/1000}k`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="total" stroke="#f97316" strokeWidth={3} fillOpacity={1} fill="url(#colorVentas)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </SectionCard>

        <SectionCard title="Top 5 Productos Más Vendidos">
          <div className="h-[300px] mt-4">
            {!loading && stats?.grafico_top_productos && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.grafico_top_productos} layout="vertical" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f1f5f9" />
                  <XAxis type="number" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} width={120} />
                  <Tooltip content={<CustomTooltip />} cursor={{fill: '#f8fafc'}} />
                  <Bar dataKey="cantidad" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
