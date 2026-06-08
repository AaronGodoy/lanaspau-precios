import { useEffect, useState } from 'react';
import { ShoppingCart, Plus, Minus, Trash2, CheckCircle2 } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import { api } from '../services/api';
import type { Product } from '../services/types';
import { formatCurrency } from '../utils/format';

interface CartItem {
  product: Product;
  quantity: number;
}

export default function SalesPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [metodoPago, setMetodoPago] = useState('Efectivo');
  const [notas, setNotas] = useState('');
  
  const [cashRegister, setCashRegister] = useState<{id: number, monto_inicial: number} | null>(null);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [registerForm, setRegisterForm] = useState({ monto_inicial: 0, notas: '' });
  const [closeForm, setCloseForm] = useState({ monto_final_real: 0, notas: '' });

  const [customers, setCustomers] = useState<{id: number, nombre: string, rut: string}[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState('');
  
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [regRes, custRes] = await Promise.all([
          api.get('/cash-registers/current'),
          api.get('/customers')
        ]);
        if (regRes.data) {
          setCashRegister(regRes.data);
        } else {
          setShowRegisterModal(true);
        }
        setCustomers(custRes.data);
      } catch (err) {
        console.error("Error fetching initial data", err);
      }
    };
    fetchInitialData();
  }, []);
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const res = await api.get('/products', { params: { q: search } });
        setProducts(res.data);
      } finally {
        setLoading(false);
      }
    };
    
    const delay = setTimeout(fetchProducts, 300);
    return () => clearTimeout(delay);
  }, [search]);

  const addToCart = (product: Product) => {
    if (product.stock <= 0) {
      alert('Este producto no tiene stock disponible.');
      return;
    }
    
    const existing = cart.find(item => item.product.id === product.id);
    if (existing) {
      if (existing.quantity >= product.stock) {
        alert('No puedes agregar más que el stock disponible.');
        return;
      }
      setCart(cart.map(item => 
        item.product.id === product.id 
          ? { ...item, quantity: item.quantity + 1 } 
          : item
      ));
    } else {
      setCart([...cart, { product, quantity: 1 }]);
    }
  };

  const updateQuantity = (productId: number, delta: number) => {
    setCart(cart.map(item => {
      if (item.product.id === productId) {
        const newQuantity = item.quantity + delta;
        if (newQuantity <= 0) return item;
        if (newQuantity > item.product.stock) {
          alert('No puedes superar el stock disponible.');
          return item;
        }
        return { ...item, quantity: newQuantity };
      }
      return item;
    }));
  };

  const removeFromCart = (productId: number) => {
    setCart(cart.filter(item => item.product.id !== productId));
  };

  const total = cart.reduce((sum, item) => sum + ((item.product.latest_recommended_price || 0) * item.quantity), 0);

  const handleSubmit = async () => {
    if (cart.length === 0) return;
    if (!cashRegister) {
      alert('Debes abrir la caja antes de vender.');
      return;
    }
    setIsSubmitting(true);
    
    try {
      const payload = {
        metodo_pago: metodoPago,
        notas: notas,
        cliente_id: selectedCustomer ? Number(selectedCustomer) : null,
        caja_id: cashRegister.id,
        items: cart.map(item => ({
          producto_id: item.product.id,
          cantidad: item.quantity,
          precio_unitario: item.product.latest_recommended_price || 0
        }))
      };
      
      await api.post('/sales', payload);
      alert('¡Venta registrada con éxito!');
      setCart([]);
      setNotas('');
      setSearch('');
      setSelectedCustomer('');
      // Refrescar productos para actualizar stock
      const res = await api.get('/products');
      setProducts(res.data);
    } catch (err: unknown) {
      if (err instanceof Error && 'response' in err && (err as { response?: { data?: { detail?: string } } }).response?.data?.detail) {
        alert((err as { response: { data: { detail: string } } }).response.data.detail);
      } else {
        alert('Error al procesar la venta');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/cash-registers/open', registerForm);
      setCashRegister(res.data);
      setShowRegisterModal(false);
    } catch (err: unknown) {
      alert('Error al abrir la caja.');
    }
  };

  const handleCloseRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cashRegister) return;
    try {
      await api.post(`/cash-registers/${cashRegister.id}/close`, closeForm);
      setCashRegister(null);
      setShowCloseModal(false);
      alert('Caja cerrada con éxito.');
      setShowRegisterModal(true); // obligar a abrir otra
    } catch (err: unknown) {
      alert('Error al cerrar la caja.');
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-6">
      {/* Columna Izquierda: Buscador de productos */}
      <div className="space-y-4">
        <div className="flex justify-between items-center bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Turno Actual</h2>
            <p className="text-sm text-slate-500">Caja #{cashRegister?.id || '-'}</p>
          </div>
          <button 
            onClick={() => setShowCloseModal(true)}
            className="px-4 py-2 bg-red-50 text-red-600 font-semibold rounded-xl hover:bg-red-100 transition-colors"
          >
            Cerrar Caja
          </button>
        </div>
        
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar producto para vender..."
            className="w-full rounded-2xl border border-slate-200 py-4 pl-5 pr-4 outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-lg shadow-sm"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {loading ? (
            <p className="col-span-full text-slate-500 text-center py-8">Buscando productos...</p>
          ) : products.filter(p => p.stock > 0).length === 0 ? (
            <p className="col-span-full text-slate-500 text-center py-8">No hay productos con stock para vender.</p>
          ) : (
            products.filter(p => p.stock > 0).map(product => (
              <div 
                key={product.id} 
                onClick={() => addToCart(product)}
                className="bg-white rounded-2xl border border-slate-200 p-4 cursor-pointer hover:border-brand-400 hover:shadow-md transition-all group"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-1 rounded">{product.codigo_producto}</span>
                  <span className="text-xs font-medium text-brand-600 bg-brand-50 px-2 py-1 rounded">Stock: {product.stock}</span>
                </div>
                <h3 className="font-semibold text-slate-900 leading-tight mb-1 group-hover:text-brand-600">{product.nombre}</h3>
                <p className="text-xs text-slate-500 mb-3">{product.marca} {product.color ? `- ${product.color}` : ''}</p>
                <p className="text-lg font-bold text-slate-900">{formatCurrency(product.latest_recommended_price)}</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Columna Derecha: Carrito de Venta */}
      <div className="sticky top-6">
        <SectionCard title="Detalle de Venta">
          {cart.length === 0 ? (
            <div className="py-12 text-center text-slate-400 flex flex-col items-center">
              <ShoppingCart size={48} className="mb-4 opacity-20" />
              <p>El carrito está vacío</p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="max-h-[40vh] overflow-y-auto pr-2 space-y-3">
                {cart.map(item => (
                  <div key={item.product.id} className="flex flex-col gap-2 p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <div className="flex justify-between">
                      <span className="font-medium text-sm text-slate-900">{item.product.nombre}</span>
                      <button onClick={() => removeFromCart(item.product.id)} className="text-slate-400 hover:text-red-500"><Trash2 size={16} /></button>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3 bg-white rounded-lg border border-slate-200 p-1">
                        <button onClick={() => updateQuantity(item.product.id, -1)} className="p-1 text-slate-500 hover:text-brand-600"><Minus size={14} /></button>
                        <span className="text-sm font-semibold w-6 text-center">{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.product.id, 1)} className="p-1 text-slate-500 hover:text-brand-600"><Plus size={14} /></button>
                      </div>
                      <span className="font-semibold text-brand-600">
                        {formatCurrency((item.product.latest_recommended_price || 0) * item.quantity)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t border-slate-100 pt-4 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 font-medium text-sm">Cliente</span>
                  <select 
                    value={selectedCustomer} 
                    onChange={e => setSelectedCustomer(e.target.value)}
                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium outline-none focus:border-brand-500 w-1/2"
                  >
                    <option value="">Cliente genérico (Boleta)</option>
                    {customers.map(c => (
                      <option key={c.id} value={c.id}>{c.nombre}</option>
                    ))}
                  </select>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-500 font-medium">Método de pago</span>
                  <select 
                    value={metodoPago} 
                    onChange={e => setMetodoPago(e.target.value)}
                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium outline-none focus:border-brand-500"
                  >
                    <option value="Efectivo">Efectivo</option>
                    <option value="Transferencia">Transferencia</option>
                    <option value="Tarjeta/Transbank">Tarjeta / Transbank</option>
                  </select>
                </div>
                
                <div>
                  <input 
                    type="text" 
                    placeholder="Notas (opcional)" 
                    value={notas}
                    onChange={e => setNotas(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2.5 text-sm outline-none focus:border-brand-500"
                  />
                </div>

                <div className="flex justify-between items-end bg-slate-900 text-white p-4 rounded-2xl">
                  <span className="font-medium text-slate-300">Total a cobrar</span>
                  <span className="text-3xl font-bold">{formatCurrency(total)}</span>
                </div>

                <button 
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center gap-2 bg-brand-500 text-white font-semibold text-lg py-4 rounded-2xl hover:bg-brand-600 disabled:opacity-50 transition-colors"
                >
                  <CheckCircle2 size={24} />
                  {isSubmitting ? 'Procesando...' : 'Completar Venta'}
                </button>
              </div>
            </div>
          )}
        </SectionCard>
      </div>

      {/* Modal Abrir Caja */}
      {showRegisterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
              Apertura de Caja
            </h2>
            <p className="text-sm text-slate-500 mb-4">Para comenzar a vender, ingresa el monto inicial (sencillo) en caja.</p>
            <form onSubmit={handleOpenRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Monto Inicial Efectivo ($)</label>
                <input type="number" required min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={registerForm.monto_inicial} onChange={e => setRegisterForm({...registerForm, monto_inicial: Number(e.target.value)})} />
              </div>
              <button type="submit" className="w-full rounded-xl bg-brand-500 px-4 py-3 font-bold text-white hover:bg-brand-600">Abrir Caja y Comenzar</button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Cerrar Caja */}
      {showCloseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Cierre de Caja</h2>
            <form onSubmit={handleCloseRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Monto Final Real (Efectivo contado)</label>
                <input type="number" required min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={closeForm.monto_final_real} onChange={e => setCloseForm({...closeForm, monto_final_real: Number(e.target.value)})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Notas / Novedades</label>
                <textarea className="mt-1 w-full rounded-xl border border-slate-200 p-3" rows={2} value={closeForm.notas} onChange={e => setCloseForm({...closeForm, notas: e.target.value})}></textarea>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowCloseModal(false)} className="flex-1 rounded-xl px-4 py-3 font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200">Cancelar</button>
                <button type="submit" className="flex-1 rounded-xl bg-red-600 px-4 py-3 font-bold text-white hover:bg-red-700">Cerrar Turno</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
