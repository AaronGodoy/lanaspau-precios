import { useEffect, useState, useCallback } from 'react';
import { Plus, Search, Edit2, Trash2, X, Settings2 } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import axios from 'axios';
import { api } from '../services/api';
import type { Product } from '../services/types';
import { formatCurrency } from '../utils/format';
import type { Supplier } from './SuppliersPage';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [showMargins, setShowMargins] = useState(false);

  const [form, setForm] = useState({
    nombre: '', marca: '', categoria: '', color: '', gramaje: '', proveedor_id: '' as number | string,
    stock: 0,
    stock_minimo: 5,
    costo_inicial_total: '',
    compra_incluye_iva: false,
    margen_minimo_porcentaje: '',
    margen_recomendado_porcentaje: '',
    margen_premium_porcentaje: ''
  });

  const fetchProducts = useCallback(async (currentSearch: string = search) => {
    setLoading(true);
    try {
      const [prodRes, suppRes] = await Promise.all([
        api.get('/products', { params: { q: currentSearch } }),
        api.get('/suppliers')
      ]);
      setProducts(prodRes.data);
      setSuppliers(suppRes.data);
    } catch (err) {
      console.error(err);
      alert('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const delay = setTimeout(() => {
      fetchProducts(search);
    }, 0);
    return () => clearTimeout(delay);
  }, [search, fetchProducts]);

  const openCreateModal = () => {
    setEditingProduct(null);
    setForm({ nombre: '', marca: '', categoria: '', color: '', gramaje: '', proveedor_id: '', stock: 0, stock_minimo: 5, costo_inicial_total: '', compra_incluye_iva: false, margen_minimo_porcentaje: '', margen_recomendado_porcentaje: '', margen_premium_porcentaje: '' });
    setShowMargins(false);
    setShowModal(true);
  };

  const openEditModal = (p: Product) => {
    setEditingProduct(p);
    setForm({
      nombre: p.nombre,
      marca: p.marca || '',
      categoria: p.categoria || '',
      color: p.color || '',
      gramaje: p.gramaje || '',
      proveedor_id: p.proveedor_id || '',
      stock: p.stock || 0,
      stock_minimo: p.stock_minimo || 5,
      costo_inicial_total: p.costo_inicial_total?.toString() || '',
      compra_incluye_iva: p.compra_incluye_iva || false,  
      margen_minimo_porcentaje: p.margen_minimo_porcentaje?.toString() || '',
      margen_recomendado_porcentaje: p.margen_recomendado_porcentaje?.toString() || '',
      margen_premium_porcentaje: p.margen_premium_porcentaje?.toString() || ''
    });
    setShowMargins(!!(p.margen_minimo_porcentaje || p.margen_recomendado_porcentaje || p.margen_premium_porcentaje));
    setShowModal(true);
  };
  
  const handleDelete = async (id: number) => {
    if (!confirm('¿Estás seguro de eliminar este producto?')) return;
    try {
      await api.delete(`/products/${id}`);
      fetchProducts();
    } catch {
      alert('Error al eliminar producto.');
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...form,
        proveedor_id: form.proveedor_id ? Number(form.proveedor_id) : null,
        costo_inicial_total: form.costo_inicial_total ? Number(form.costo_inicial_total) : null,
        margen_minimo_porcentaje: form.margen_minimo_porcentaje ? Number(form.margen_minimo_porcentaje) : null,
        margen_recomendado_porcentaje: form.margen_recomendado_porcentaje ? Number(form.margen_recomendado_porcentaje) : null,
        margen_premium_porcentaje: form.margen_premium_porcentaje ? Number(form.margen_premium_porcentaje) : null,
      };

      if (editingProduct) {
        // Exclude initial cost logic from PUT updates
        const { costo_inicial_total, compra_incluye_iva, ...updatePayload } = payload;
        await api.put(`/products/${editingProduct.id}`, updatePayload);
      } else {
        await api.post('/products', payload);
      }
      setShowModal(false);
      fetchProducts();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        alert(err.response?.data?.detail || 'Error al guardar producto.');
      } else {
        alert('Error al guardar producto.');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Buscar por nombre, codigo, marca o color..."
            className="w-full rounded-2xl border border-slate-200 py-3 pl-10 pr-4 outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button onClick={openCreateModal} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-brand-500 px-6 py-3 font-semibold text-white hover:bg-brand-600">
          <Plus size={18} />
          Nuevo producto
        </button>
      </div>
      
      <SectionCard title="Catálogo activo">
        {loading ? <p className="text-slate-500">Cargando productos...</p> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-slate-500">
                  <th className="pb-3 font-medium">Código</th>
                  <th className="pb-3 font-medium">Nombre / Color</th>
                  <th className="pb-3 font-medium text-center">Stock</th>
                  <th className="pb-3 font-medium text-right">Último Costo</th>
                  <th className="pb-3 font-medium text-right">Precio Rec.</th>
                  <th className="pb-3 font-medium text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {products.map((p) => (
                  <tr key={p.id} className="group hover:bg-slate-50">
                    <td className="py-4 font-medium text-slate-900">{p.codigo_producto}</td>
                    <td className="py-4">
                      <p className="text-slate-900">{p.nombre}</p>
                      <p className="text-xs text-slate-500">{p.marca} {p.color ? `· ${p.color}` : ''}</p>
                    </td>
                    <td className="py-4 text-center font-semibold text-slate-700">
                      {p.stock > 0 ? p.stock : <span className="text-red-500 bg-red-50 px-2 py-0.5 rounded text-xs">Sin stock</span>}
                    </td>
                    <td className="py-4 text-right font-medium text-slate-900">{formatCurrency(p.latest_cost_total)}</td>
                    <td className="py-4 text-right font-semibold text-brand-600">{formatCurrency(p.latest_recommended_price)}</td>
                    <td className="py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button onClick={() => openEditModal(p)} className="p-2 text-slate-400 hover:text-brand-600 rounded-lg hover:bg-brand-50"><Edit2 size={16} /></button>
                        <button onClick={() => handleDelete(p.id)} className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50"><Trash2 size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
                {products.length === 0 && (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">No se encontraron productos.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm overflow-y-auto">
          <div className="w-full max-w-xl rounded-3xl bg-white p-6 shadow-2xl my-auto">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold text-slate-900">{editingProduct ? 'Editar Producto' : 'Nuevo Producto'}</h3>
                {editingProduct && <p className="text-sm text-slate-500 mt-1">Código: {editingProduct.codigo_producto}</p>}
                {!editingProduct && <p className="text-sm text-slate-500 mt-1">El código se generará automáticamente.</p>}
              </div>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600"><X size={24} /></button>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Nombre
                  <input required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
                </label>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Stock Inicial / Actual
                  <input type="number" required min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.stock} onChange={e => setForm({...form, stock: Number(e.target.value)})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Alerta Stock Mínimo
                  <input type="number" required min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.stock_minimo} onChange={e => setForm({...form, stock_minimo: Number(e.target.value)})} />
                </label>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Proveedor
                  <select className="mt-1 w-full rounded-xl border border-slate-200 p-2.5 bg-white" value={form.proveedor_id} onChange={e => setForm({...form, proveedor_id: e.target.value})}>
                    <option value="">-- Seleccionar Proveedor --</option>
                    {suppliers.map(s => (
                      <option key={s.id} value={s.id}>{s.nombre}</option>
                    ))}
                  </select>
                </label>
                <label className="block text-sm font-medium text-slate-700">Marca
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.marca} onChange={e => setForm({...form, marca: e.target.value})} />
                </label>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Categoría
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.categoria} onChange={e => setForm({...form, categoria: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Color
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.color} onChange={e => setForm({...form, color: e.target.value})} />
                </label>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Gramaje
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" placeholder="Ej: 100g" value={form.gramaje} onChange={e => setForm({...form, gramaje: e.target.value})} />
                </label>
              </div>

              {!editingProduct && (
                <div className="mt-6 border-t border-slate-100 pt-4">
                  <h4 className="text-sm font-semibold text-slate-900 mb-3">Costo inicial (Opcional)</h4>
                  <p className="text-xs text-slate-500 mb-3">Ingresa el costo TOTAL de tu compra para generar el cálculo inicial automáticamente (se dividirá por el stock ingresado arriba).</p>
                  <div className="grid grid-cols-2 gap-4">
                    <label className="block text-sm font-medium text-slate-700">Valor de compra TOTAL
                      <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.costo_inicial_total} onChange={e => setForm({...form, costo_inicial_total: e.target.value})} />
                    </label>
                    <div className="flex items-center mt-6">
                      <label className="flex items-center gap-2 text-sm font-medium text-slate-700 cursor-pointer">
                        <input type="checkbox" className="h-5 w-5 rounded border-slate-300 text-brand-500 focus:ring-brand-500" checked={form.compra_incluye_iva} onChange={e => setForm({...form, compra_incluye_iva: e.target.checked})} />
                        El valor incluye IVA
                      </label>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-6 border-t border-slate-100 pt-4">
                <button type="button" onClick={() => setShowMargins(!showMargins)} className="flex items-center gap-2 text-sm font-medium text-brand-600 hover:text-brand-700">
                  <Settings2 size={16} />
                  {showMargins ? 'Ocultar reglas comerciales' : 'Configurar reglas comerciales específicas'}
                </button>
                
                {showMargins && (
                  <div className="mt-4 rounded-xl bg-slate-50 p-4 space-y-3 border border-slate-200">
                    <p className="text-xs text-slate-500 mb-3">Si dejas estos campos vacíos, se usarán los márgenes globales de la configuración principal.</p>
                    <div className="grid grid-cols-3 gap-3">
                      <label className="block text-xs font-medium text-slate-700">Margen Mínimo (%)
                        <input type="number" step="0.1" className="mt-1 w-full rounded-lg border border-slate-200 p-2" placeholder="Ej: 20" value={form.margen_minimo_porcentaje} onChange={e => setForm({...form, margen_minimo_porcentaje: e.target.value})} />
                      </label>
                      <label className="block text-xs font-medium text-slate-700">Margen Recomendado (%)
                        <input type="number" step="0.1" className="mt-1 w-full rounded-lg border border-slate-200 p-2" placeholder="Ej: 35" value={form.margen_recomendado_porcentaje} onChange={e => setForm({...form, margen_recomendado_porcentaje: e.target.value})} />
                      </label>
                      <label className="block text-xs font-medium text-slate-700">Margen Premium (%)
                        <input type="number" step="0.1" className="mt-1 w-full rounded-lg border border-slate-200 p-2" placeholder="Ej: 45" value={form.margen_premium_porcentaje} onChange={e => setForm({...form, margen_premium_porcentaje: e.target.value})} />
                      </label>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => setShowModal(false)} className="rounded-xl px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100">Cancelar</button>
                <button type="submit" className="rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-700">Guardar producto</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
