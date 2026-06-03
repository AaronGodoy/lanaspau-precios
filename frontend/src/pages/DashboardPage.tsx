import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Boxes, DollarSign, HandCoins, Percent } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import StatCard from '../components/StatCard';
import { api } from '../services/api';
import type { DashboardData } from '../services/types';
import { formatCurrency, formatDate, formatPercent } from '../utils/format';

const emptyData: DashboardData = { total_productos: 0, promedio_margen: 0, total_invertido_inventario: 0, valor_potencial_venta: 0, productos_mejor_margen: [], productos_menor_margen: [], ultimos_productos: [] };

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>(emptyData);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/pricing/dashboard').then((response) => setData(response.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Productos activos" value={String(data.total_productos)} hint="Catalogo disponible para cotizar." icon={<Boxes size={18} />} />
        <StatCard label="Margen promedio" value={formatPercent(data.promedio_margen)} hint="Promedio de margenes estimados." icon={<Percent size={18} />} />
        <StatCard label="Inversion total" value={formatCurrency(data.total_invertido_inventario)} hint="Costo real acumulado del inventario." icon={<HandCoins size={18} />} />
        <StatCard label="Venta potencial" value={formatCurrency(data.valor_potencial_venta)} hint="Total sugerido al precio recomendado." icon={<DollarSign size={18} />} />
      </div>
      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <SectionCard title="Mejores margenes" subtitle="Visualiza los productos con mejor rentabilidad sugerida.">
          {loading ? <p className="text-sm text-slate-500">Cargando dashboard...</p> : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.productos_mejor_margen}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="codigo_producto" />
                  <YAxis />
                  <Tooltip formatter={(value: number | string | Array<number | string>) => typeof value === 'number' ? formatPercent(value) : value} />
                  <Bar dataKey="margen_estimado" fill="#f97316" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </SectionCard>
        <SectionCard title="Ultimos productos" subtitle="Altas mas recientes del catalogo.">
          <div className="space-y-3">
            {data.ultimos_productos.map((item) => (
              <div key={item.producto_id} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                <p className="font-medium text-slate-900">{item.nombre}</p>
                <p className="text-sm text-slate-500">{item.codigo_producto} ? {item.categoria || 'Sin categoria'}</p>
                <p className="mt-2 text-sm text-slate-500">{formatDate(item.fecha || null)}</p>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <SectionCard title="Top margen" subtitle="Mayor porcentaje estimado sobre el precio recomendado.">
          <div className="space-y-3">
            {data.productos_mejor_margen.map((item) => (
              <div key={item.producto_id} className="flex items-center justify-between rounded-2xl border border-slate-100 px-4 py-3">
                <div><p className="font-medium text-slate-900">{item.nombre}</p><p className="text-sm text-slate-500">{item.codigo_producto}</p></div>
                <span className="text-sm font-semibold text-emerald-600">{formatPercent(item.margen_estimado)}</span>
              </div>
            ))}
          </div>
        </SectionCard>
        <SectionCard title="Menor margen" subtitle="Productos a revisar por baja rentabilidad.">
          <div className="space-y-3">
            {data.productos_menor_margen.map((item) => (
              <div key={item.producto_id} className="flex items-center justify-between rounded-2xl border border-slate-100 px-4 py-3">
                <div><p className="font-medium text-slate-900">{item.nombre}</p><p className="text-sm text-slate-500">{item.codigo_producto}</p></div>
                <span className="text-sm font-semibold text-amber-600">{formatPercent(item.margen_estimado)}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
