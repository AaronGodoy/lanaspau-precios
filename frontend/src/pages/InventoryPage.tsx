import { useEffect, useState } from 'react';
import { AlertTriangle, TrendingDown } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import { api } from '../services/api';
import { formatCurrency } from '../utils/format';

interface LowStockAlert {
  producto_id: number;
  codigo_producto: string;
  nombre: string;
  stock_actual: number;
  stock_minimo: number;
}

interface Sale {
  id: number;
  total: number;
  metodo_pago: string;
  fecha_venta: string;
  items: any[];
}

export default function InventoryPage() {
  const [alerts, setAlerts] = useState<LowStockAlert[]>([]);
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [alertsRes, salesRes] = await Promise.all([
          api.get('/sales/alerts/low-stock'),
          api.get('/sales')
        ]);
        setAlerts(alertsRes.data);
        setSales(salesRes.data);
      } catch (err) {
        console.error("Error cargando inventario", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-red-50 border border-red-100 p-6 rounded-3xl flex items-center gap-4">
          <div className="bg-red-100 p-4 rounded-full text-red-600">
            <AlertTriangle size={32} />
          </div>
          <div>
            <p className="text-red-600 font-medium">Alertas de Stock</p>
            <h3 className="text-3xl font-bold text-red-700">{alerts.length} productos</h3>
            <p className="text-sm text-red-500 mt-1">Por debajo del mínimo</p>
          </div>
        </div>
        
        <div className="bg-brand-50 border border-brand-100 p-6 rounded-3xl flex items-center gap-4">
          <div className="bg-brand-100 p-4 rounded-full text-brand-600">
            <TrendingDown size={32} />
          </div>
          <div>
            <p className="text-brand-600 font-medium">Ventas Recientes</p>
            <h3 className="text-3xl font-bold text-brand-700">{sales.length}</h3>
            <p className="text-sm text-brand-500 mt-1">Registradas en el sistema</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SectionCard title="Productos con Stock Crítico">
          {loading ? <p className="text-slate-500">Cargando alertas...</p> : alerts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-500">Todo en orden. No hay productos con stock crítico.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map(alert => (
                <div key={alert.producto_id} className="flex justify-between items-center p-4 bg-white border border-red-100 rounded-2xl shadow-sm">
                  <div>
                    <span className="text-xs font-semibold text-slate-400">{alert.codigo_producto}</span>
                    <h4 className="font-semibold text-slate-900">{alert.nombre}</h4>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-500 mb-1">Mínimo: {alert.stock_minimo}</p>
                    <p className="font-bold text-red-600 bg-red-50 px-3 py-1 rounded-lg">
                      Actual: {alert.stock_actual}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard title="Últimas Ventas">
          {loading ? <p className="text-slate-500">Cargando ventas...</p> : sales.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-500">Aún no hay ventas registradas.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sales.slice(0, 10).map(sale => (
                <div key={sale.id} className="flex justify-between items-center p-4 bg-slate-50 border border-slate-100 rounded-2xl">
                  <div>
                    <p className="font-semibold text-slate-900">Venta #{sale.id}</p>
                    <p className="text-xs text-slate-500">
                      {new Date(sale.fecha_venta).toLocaleString()} · {sale.metodo_pago || 'N/A'}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">{sale.items.length} productos distintos</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-slate-900 text-lg">{formatCurrency(sale.total)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  );
}
