import { useEffect, useState } from 'react';
import { AlertTriangle, TrendingDown, TrendingUp, DollarSign, RefreshCw, PackagePlus, AlertCircle } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import { api } from '../services/api';
import { formatCurrency } from '../utils/format';
import { Product } from '../services/types';

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

interface InventoryMovement {
  id: number;
  producto_id: number;
  tipo: string;
  cantidad: number;
  costo_unitario?: number;
  motivo?: string;
  fecha: string;
}

export default function InventoryPage() {
  const [alerts, setAlerts] = useState<LowStockAlert[]>([]);
  const [recentSales, setRecentSales] = useState<Sale[]>([]);
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [showMovementModal, setShowMovementModal] = useState(false);
  const [movementForm, setMovementForm] = useState({
    producto_id: '',
    tipo: 'ingreso',
    cantidad: 1,
    costo_unitario: '',
    motivo: ''
  });


  const fetchData = async () => {
    setLoading(true);
    try {
      const [alertsRes, salesRes, movementsRes, productsRes] = await Promise.all([
        api.get('/sales/alerts/low-stock'),
        api.get('/sales', { params: { limit: 5 } }),
        api.get('/inventory/movements', { params: { limit: 10 } }),
        api.get('/products')
      ]);
      setAlerts(alertsRes.data);
      setRecentSales(salesRes.data);
      setMovements(movementsRes.data);
      setProducts(productsRes.data);
    } catch (err) {
      console.error("Error cargando inventario", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRegisterMovement = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/inventory/movements', {
        producto_id: Number(movementForm.producto_id),
        tipo: movementForm.tipo,
        cantidad: Number(movementForm.cantidad),
        costo_unitario: movementForm.costo_unitario ? Number(movementForm.costo_unitario) : null,
        motivo: movementForm.motivo
      });
      setShowMovementModal(false);
      fetchData(); // Recargar todo para actualizar stock y movimientos
      setMovementForm({ producto_id: '', tipo: 'ingreso', cantidad: 1, costo_unitario: '', motivo: '' });
    } catch (err) {
      alert('Error al registrar el movimiento');
    }
  };

  const getMovementIcon = (tipo: string) => {
    switch(tipo) {
      case 'ingreso': return <PackagePlus size={16} className="text-emerald-500" />;
      case 'merma': return <AlertCircle size={16} className="text-red-500" />;
      case 'devolucion': return <RefreshCw size={16} className="text-blue-500" />;
      default: return <AlertTriangle size={16} className="text-orange-500" />;
    }
  };

  const getMovementLabel = (tipo: string) => {
    switch(tipo) {
      case 'ingreso': return 'Ingreso';
      case 'merma': return 'Merma';
      case 'devolucion': return 'Devolución';
      default: return 'Ajuste';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-slate-900">Control de Inventario</h1>
        <button onClick={() => setShowMovementModal(true)} className="flex items-center gap-2 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 transition-colors">
          <RefreshCw size={18} />
          Registrar Movimiento
        </button>
      </div>
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
            <h3 className="text-3xl font-bold text-brand-700">{recentSales.length}</h3>
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

        <SectionCard title="Últimos Movimientos de Inventario">
          {loading ? (
            <p className="text-slate-500 p-4">Cargando movimientos...</p>
          ) : movements.length === 0 ? (
            <p className="text-slate-500 p-4">No hay movimientos recientes.</p>
          ) : (
            <div className="space-y-4">
              {movements.map(m => {
                const prod = products.find(p => p.id === m.producto_id);
                return (
                  <div key={m.id} className="flex justify-between items-center p-4 border border-slate-100 rounded-2xl bg-slate-50">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-white rounded-xl shadow-sm">
                        {getMovementIcon(m.tipo)}
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900">{prod?.nombre || `Producto #${m.producto_id}`}</p>
                        <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
                          <span className="font-medium">{getMovementLabel(m.tipo)}</span>
                          <span>•</span>
                          <span>{new Date(m.fecha).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${m.tipo === 'merma' ? 'text-red-600' : 'text-slate-900'}`}>
                        {m.tipo === 'merma' ? '-' : '+'}{m.cantidad} un.
                      </p>
                      {m.motivo && <p className="text-xs text-slate-400 mt-1">{m.motivo}</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </SectionCard>

        <SectionCard title="Últimas Ventas">
          {loading ? (
            <p className="text-slate-500 p-4">Cargando ventas...</p>
          ) : recentSales.length === 0 ? (
            <p className="text-slate-500 p-4">No hay ventas registradas aún.</p>
          ) : (
            <div className="space-y-4">
              {recentSales.map(s => (
                <div key={s.id} className="flex justify-between items-center p-4 border border-slate-100 rounded-2xl bg-white shadow-sm hover:shadow transition-shadow">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                      <DollarSign size={24} />
                    </div>
                    <div>
                      <p className="font-bold text-slate-900">Venta #{s.id}</p>
                      <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                        <span className="capitalize">{s.metodo_pago}</span>
                        <span>•</span>
                        <span>{new Date(s.fecha_venta).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-emerald-600">{formatCurrency(s.total)}</p>
                    <p className="text-xs text-slate-500 mt-1">{s.items.length} productos</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>

      {/* Modal Registro de Movimiento */}
      {showMovementModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
              <RefreshCw size={24} className="text-brand-500" />
              Registrar Movimiento
            </h2>
            <form onSubmit={handleRegisterMovement} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Producto *</label>
                <select required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5 bg-white" value={movementForm.producto_id} onChange={e => setMovementForm({...movementForm, producto_id: e.target.value})}>
                  <option value="">-- Seleccionar Producto --</option>
                  {products.map(p => (
                    <option key={p.id} value={p.id}>{p.nombre} (Stock: {p.stock})</option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Tipo de Movimiento *</label>
                  <select required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5 bg-white" value={movementForm.tipo} onChange={e => setMovementForm({...movementForm, tipo: e.target.value})}>
                    <option value="ingreso">Ingreso (+)</option>
                    <option value="merma">Merma (-)</option>
                    <option value="devolucion">Devolución (+)</option>
                    <option value="ajuste">Ajuste (+/-)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Cantidad *</label>
                  <input type="number" required min="1" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={movementForm.cantidad} onChange={e => setMovementForm({...movementForm, cantidad: Number(e.target.value)})} />
                </div>
              </div>

              {movementForm.tipo === 'ingreso' && (
                <div>
                  <label className="block text-sm font-medium text-slate-700">Costo Unitario (Opcional)</label>
                  <input type="number" step="0.01" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" placeholder="Ej: 1500" value={movementForm.costo_unitario} onChange={e => setMovementForm({...movementForm, costo_unitario: e.target.value})} />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-700">Motivo / Notas</label>
                <textarea className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" rows={2} placeholder="Ej: Mercadería dañada en transporte" value={movementForm.motivo} onChange={e => setMovementForm({...movementForm, motivo: e.target.value})} />
              </div>

              <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-slate-100">
                <button type="button" onClick={() => setShowMovementModal(false)} className="rounded-xl px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100">Cancelar</button>
                <button type="submit" className="rounded-xl bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">Registrar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
