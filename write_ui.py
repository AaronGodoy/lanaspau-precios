from pathlib import Path
from textwrap import dedent

root = Path(r'd:\Python\LanasPau\frontend')
files = {
  'src/pages/CalculatorPage.tsx': dedent('''
    import { useState, useEffect } from 'react';
    import { Calculator, Check, ArrowRight } from 'lucide-react';
    import SectionCard from '../components/SectionCard';
    import { api } from '../services/api';
    import type { CalculationResult, Product } from '../services/types';
    import { formatCurrency, formatPercent } from '../utils/format';

    export default function CalculatorPage() {
      const [products, setProducts] = useState<Product[]>([]);
      const [form, setForm] = useState({
        producto_id: '',
        cantidad: '1',
        valor_compra: '',
        compra_incluye_iva: false,
        costo_envio: '0',
        costo_retiro: '0',
        otros_costos: '0'
      });
      const [result, setResult] = useState<CalculationResult | null>(null);
      const [loading, setLoading] = useState(false);

      useEffect(() => {
        api.get('/products').then(res => setProducts(res.data));
      }, []);

      const handleCalculate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
          const payload = {
            ...form,
            producto_id: form.producto_id ? Number(form.producto_id) : null,
            cantidad: Number(form.cantidad) || 1,
            valor_compra: Number(form.valor_compra),
            costo_envio: Number(form.costo_envio),
            costo_retiro: Number(form.costo_retiro),
            otros_costos: Number(form.otros_costos)
          };
          const res = await api.post('/pricing/calculate', payload);
          setResult(res.data);
        } finally {
          setLoading(false);
        }
      };

      const handleSave = async () => {
        if (!result?.producto_id) return alert('Selecciona un producto para guardar el costo.');
        try {
          await api.post('/costs', {
            ...form,
            producto_id: Number(form.producto_id),
            cantidad: Number(form.cantidad) || 1,
            valor_compra: Number(form.valor_compra),
            costo_envio: Number(form.costo_envio),
            costo_retiro: Number(form.costo_retiro),
            otros_costos: Number(form.otros_costos)
          });
          alert('Costo y precio guardados en el historial del producto exitosamente.');
          setResult(null);
          setForm(f => ({ ...f, valor_compra: '', costo_envio: '0', costo_retiro: '0', otros_costos: '0' }));
        } catch (error) {
          alert('Error al guardar.');
        }
      };

      return (
        <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <SectionCard title="Ingreso de costos" subtitle="Digita los valores totales reales de tu compra. El sistema calculará el valor por unidad.">
            <form onSubmit={handleCalculate} className="space-y-4">
              <label className="block text-sm font-medium text-slate-700">Producto (Opcional)
                <select className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.producto_id} onChange={e => setForm({...form, producto_id: e.target.value})}>
                  <option value="">Cálculo libre (sin guardar)</option>
                  {products.map(p => <option key={p.id} value={p.id}>{p.codigo_producto} - {p.nombre}</option>)}
                </select>
              </label>

              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Cantidad comprada
                  <input type="number" required min="1" className="mt-1 w-full rounded-xl border border-slate-200 p-3 bg-brand-50" value={form.cantidad} onChange={e => setForm({...form, cantidad: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Valor de compra TOTAL
                  <input type="number" required min="1" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.valor_compra} onChange={e => setForm({...form, valor_compra: e.target.value})} />
                </label>
              </div>
              
              <div className="flex items-center pb-2">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700 cursor-pointer">
                  <input type="checkbox" className="h-5 w-5 rounded border-slate-300 text-brand-500 focus:ring-brand-500" checked={form.compra_incluye_iva} onChange={e => setForm({...form, compra_incluye_iva: e.target.checked})} />
                  El valor de compra incluye IVA
                </label>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <label className="block text-sm font-medium text-slate-700">Envío total
                  <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.costo_envio} onChange={e => setForm({...form, costo_envio: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Retiro total
                  <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.costo_retiro} onChange={e => setForm({...form, costo_retiro: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Otros total
                  <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.otros_costos} onChange={e => setForm({...form, otros_costos: e.target.value})} />
                </label>
              </div>

              <button type="submit" disabled={loading || !form.valor_compra} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-4 text-base font-semibold text-white hover:bg-slate-800 disabled:opacity-50">
                <Calculator size={20} />
                Calcular precios sugeridos (POR UNIDAD)
              </button>
            </form>
          </SectionCard>

          <div className="space-y-6">
            {result ? (
              <>
                <div className="rounded-2xl border border-brand-200 bg-brand-50 p-6">
                  <h3 className="mb-4 text-lg font-semibold text-brand-900">Resultados por Unidad</h3>
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="rounded-xl bg-white p-4 shadow-sm border border-brand-100">
                      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Precio Mínimo</p>
                      <p className="mt-1 text-xl font-semibold text-slate-900">{formatCurrency(result.precio_minimo)}</p>
                    </div>
                    <div className="rounded-xl bg-brand-500 p-4 shadow-md text-white ring-4 ring-brand-500/20">
                      <p className="text-xs font-medium text-brand-100 uppercase tracking-wide flex items-center gap-1"><Check size={14}/> Recomendado</p>
                      <p className="mt-1 text-2xl font-bold">{formatCurrency(result.precio_recomendado)}</p>
                    </div>
                    <div className="rounded-xl bg-white p-4 shadow-sm border border-brand-100">
                      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Precio Premium</p>
                      <p className="mt-1 text-xl font-semibold text-slate-900">{formatCurrency(result.precio_premium)}</p>
                    </div>
                  </div>

                  <div className="mt-6 flex flex-col gap-3 rounded-xl bg-white/60 p-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Costo Total Real (Unidad)</span>
                      <span className="font-semibold text-slate-900">{formatCurrency(result.costo_total)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Margen Esperado</span>
                      <span className="font-semibold text-brand-600">{formatPercent(result.margen_estimado)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Utilidad Neta por Unidad</span>
                      <span className="font-semibold text-emerald-600">+{formatCurrency(result.utilidad_estimada)}</span>
                    </div>
                  </div>

                  {form.producto_id && (
                    <button onClick={handleSave} className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 py-4 text-base font-semibold text-white hover:bg-brand-700 shadow-md">
                      Guardar en historial del producto
                      <ArrowRight size={18} />
                    </button>
                  )}
                </div>
                
                <SectionCard title="¿Por qué este precio?">
                  <ul className="space-y-2 text-sm text-slate-600">
                    {result.explicacion.map((text, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="mt-0.5 text-brand-500">•</span>
                        {text}
                      </li>
                    ))}
                  </ul>
                </SectionCard>
              </>
            ) : (
              <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-slate-400">
                <Calculator size={48} className="mb-4 opacity-20" />
                <p>Ingresa los costos totales y la cantidad. El sistema calculará automáticamente los valores por unidad para recomendarte un precio.</p>
              </div>
            )}
          </div>
        </div>
      );
    }
  ''').strip() + '\n',

  'src/pages/ProductsPage.tsx': dedent('''
    import { useEffect, useState } from 'react';
    import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';
    import SectionCard from '../components/SectionCard';
    import { api } from '../services/api';
    import type { Product } from '../services/types';
    import { formatCurrency } from '../utils/format';

    export default function ProductsPage() {
      const [products, setProducts] = useState<Product[]>([]);
      const [search, setSearch] = useState('');
      const [loading, setLoading] = useState(true);
      
      const [showModal, setShowModal] = useState(false);
      const [editingProduct, setEditingProduct] = useState<Product | null>(null);
      const [form, setForm] = useState({
        codigo_producto: '', nombre: '', marca: '', categoria: '', color: '', gramaje: '', proveedor: 'Lanas Pau'
      });

      const fetchProducts = () => {
        setLoading(true);
        api.get('/products', { params: { q: search } })
          .then((res) => setProducts(res.data))
          .finally(() => setLoading(false));
      };

      useEffect(() => {
        fetchProducts();
      }, [search]);

      const openCreateModal = () => {
        setEditingProduct(null);
        setForm({ codigo_producto: '', nombre: '', marca: '', categoria: '', color: '', gramaje: '', proveedor: 'Lanas Pau' });
        setShowModal(true);
      };

      const openEditModal = (p: Product) => {
        setEditingProduct(p);
        setForm({
          codigo_producto: p.codigo_producto,
          nombre: p.nombre,
          marca: p.marca || '',
          categoria: p.categoria || '',
          color: p.color || '',
          gramaje: p.gramaje || '',
          proveedor: p.proveedor || 'Lanas Pau'
        });
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
          if (editingProduct) {
            await api.put(`/products/${editingProduct.id}`, form);
          } else {
            await api.post('/products', form);
          }
          setShowModal(false);
          fetchProducts();
        } catch (err: any) {
          alert(err.response?.data?.detail || 'Error al guardar producto.');
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
                      <th className="pb-3 font-medium">Categoría</th>
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
                        <td className="py-4 text-slate-600">{p.categoria || '-'}</td>
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
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
              <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-slate-900">{editingProduct ? 'Editar Producto' : 'Nuevo Producto'}</h3>
                  <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600"><X size={24} /></button>
                </div>
                <form onSubmit={handleSave} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <label className="block text-sm font-medium text-slate-700">Código
                      <input required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.codigo_producto} onChange={e => setForm({...form, codigo_producto: e.target.value})} />
                    </label>
                    <label className="block text-sm font-medium text-slate-700">Nombre
                      <input required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
                    </label>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <label className="block text-sm font-medium text-slate-700">Marca
                      <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.marca} onChange={e => setForm({...form, marca: e.target.value})} />
                    </label>
                    <label className="block text-sm font-medium text-slate-700">Categoría
                      <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.categoria} onChange={e => setForm({...form, categoria: e.target.value})} />
                    </label>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <label className="block text-sm font-medium text-slate-700">Color
                      <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.color} onChange={e => setForm({...form, color: e.target.value})} />
                    </label>
                    <label className="block text-sm font-medium text-slate-700">Gramaje
                      <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" placeholder="Ej: 100g" value={form.gramaje} onChange={e => setForm({...form, gramaje: e.target.value})} />
                    </label>
                  </div>
                  <div className="mt-6 flex justify-end gap-3">
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
  ''').strip() + '\n',
}

for rel, content in files.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
