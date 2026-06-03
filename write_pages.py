from pathlib import Path
from textwrap import dedent

root = Path(r'd:\Python\LanasPau\frontend')
files = {
  'src/pages/ProductsPage.tsx': dedent('''
    import { useEffect, useState } from 'react';
    import { Plus, Search } from 'lucide-react';
    import SectionCard from '../components/SectionCard';
    import { api } from '../services/api';
    import type { Product } from '../services/types';
    import { formatCurrency } from '../utils/format';

    export default function ProductsPage() {
      const [products, setProducts] = useState<Product[]>([]);
      const [search, setSearch] = useState('');
      const [loading, setLoading] = useState(true);

      useEffect(() => {
        api.get('/products', { params: { q: search } })
          .then((res) => setProducts(res.data))
          .finally(() => setLoading(false));
      }, [search]);

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
            <button className="inline-flex items-center justify-center gap-2 rounded-2xl bg-brand-500 px-6 py-3 font-semibold text-white hover:bg-brand-600">
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
                      </tr>
                    ))}
                    {products.length === 0 && (
                      <tr>
                        <td colSpan={5} className="py-8 text-center text-slate-500">No se encontraron productos.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>
        </div>
      );
    }
  ''').strip() + '\n',

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
          <SectionCard title="Ingreso de costos" subtitle="Digita los valores reales de tu compra.">
            <form onSubmit={handleCalculate} className="space-y-4">
              <label className="block text-sm font-medium text-slate-700">Producto (Opcional)
                <select className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.producto_id} onChange={e => setForm({...form, producto_id: e.target.value})}>
                  <option value="">Cálculo libre (sin guardar)</option>
                  {products.map(p => <option key={p.id} value={p.id}>{p.codigo_producto} - {p.nombre}</option>)}
                </select>
              </label>

              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Valor de compra
                  <input type="number" required min="1" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.valor_compra} onChange={e => setForm({...form, valor_compra: e.target.value})} />
                </label>
                <div className="flex items-center pt-8">
                  <label className="flex items-center gap-2 text-sm font-medium text-slate-700 cursor-pointer">
                    <input type="checkbox" className="h-5 w-5 rounded border-slate-300 text-brand-500 focus:ring-brand-500" checked={form.compra_incluye_iva} onChange={e => setForm({...form, compra_incluye_iva: e.target.checked})} />
                    El valor incluye IVA
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <label className="block text-sm font-medium text-slate-700">Envío
                  <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.costo_envio} onChange={e => setForm({...form, costo_envio: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Retiro
                  <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.costo_retiro} onChange={e => setForm({...form, costo_retiro: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Otros
                  <input type="number" min="0" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={form.otros_costos} onChange={e => setForm({...form, otros_costos: e.target.value})} />
                </label>
              </div>

              <button type="submit" disabled={loading || !form.valor_compra} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-4 text-base font-semibold text-white hover:bg-slate-800 disabled:opacity-50">
                <Calculator size={20} />
                Calcular precios sugeridos
              </button>
            </form>
          </SectionCard>

          <div className="space-y-6">
            {result ? (
              <>
                <div className="rounded-2xl border border-brand-200 bg-brand-50 p-6">
                  <h3 className="mb-4 text-lg font-semibold text-brand-900">Resultados del cálculo</h3>
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
                      <span className="text-slate-600">Costo Total Real</span>
                      <span className="font-semibold text-slate-900">{formatCurrency(result.costo_total)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Margen Esperado</span>
                      <span className="font-semibold text-brand-600">{formatPercent(result.margen_estimado)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Utilidad Neta por unidad</span>
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
                <p>Ingresa los costos y presiona calcular para ver los precios recomendados basados en tus reglas comerciales.</p>
              </div>
            )}
          </div>
        </div>
      );
    }
  ''').strip() + '\n',

  'src/pages/ReportsPage.tsx': dedent('''
    import { Download, FileText, Package, History } from 'lucide-react';
    import SectionCard from '../components/SectionCard';
    import { downloadFile } from '../services/api';

    export default function ReportsPage() {
      const handleDownload = (path: string, name: string) => {
        downloadFile(`/reports/${path}?format=xlsx`, `${name}.xlsx`);
      };

      return (
        <div className="max-w-4xl space-y-6">
          <SectionCard title="Exportación de datos" subtitle="Descarga la información en formato Excel (.xlsx) para analizarla o respaldarla.">
            <div className="mt-4 grid gap-4 sm:grid-cols-3">
              
              <div className="flex flex-col items-center rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:border-brand-300 hover:shadow-md">
                <div className="mb-4 rounded-full bg-blue-50 p-4 text-blue-600">
                  <Package size={32} />
                </div>
                <h3 className="font-semibold text-slate-900">Catálogo de Productos</h3>
                <p className="mt-2 mb-6 text-xs text-slate-500">Lista completa de productos con su último costo y precio recomendado.</p>
                <button onClick={() => handleDownload('products', 'Catalogo_Revesderecho')} className="mt-auto inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800">
                  <Download size={16} /> Descargar
                </button>
              </div>

              <div className="flex flex-col items-center rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:border-brand-300 hover:shadow-md">
                <div className="mb-4 rounded-full bg-emerald-50 p-4 text-emerald-600">
                  <FileText size={32} />
                </div>
                <h3 className="font-semibold text-slate-900">Inventario Valorizado</h3>
                <p className="mt-2 mb-6 text-xs text-slate-500">Valor potencial de venta y costo total invertido por cada producto.</p>
                <button onClick={() => handleDownload('inventory', 'Inventario_Valorizado')} className="mt-auto inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800">
                  <Download size={16} /> Descargar
                </button>
              </div>

              <div className="flex flex-col items-center rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:border-brand-300 hover:shadow-md">
                <div className="mb-4 rounded-full bg-purple-50 p-4 text-purple-600">
                  <History size={32} />
                </div>
                <h3 className="font-semibold text-slate-900">Historial de Precios</h3>
                <p className="mt-2 mb-6 text-xs text-slate-500">Registro histórico de todos los cálculos de costos y cambios de precios.</p>
                <button onClick={() => handleDownload('pricing-history', 'Historial_Precios')} className="mt-auto inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800">
                  <Download size={16} /> Descargar
                </button>
              </div>

            </div>
          </SectionCard>
        </div>
      );
    }
  ''').strip() + '\n',

  'src/pages/SettingsPage.tsx': dedent('''
    import { useEffect, useState } from 'react';
    import { Save } from 'lucide-react';
    import SectionCard from '../components/SectionCard';
    import { api } from '../services/api';
    import type { SettingsData } from '../services/types';

    export default function SettingsPage() {
      const [settings, setSettings] = useState<SettingsData | null>(null);
      const [loading, setLoading] = useState(false);

      useEffect(() => {
        api.get('/settings').then(res => setSettings(res.data));
      }, []);

      const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!settings) return;
        setLoading(true);
        try {
          await api.put('/settings', settings);
          alert('Configuración actualizada correctamente.');
        } catch {
          alert('Error al guardar la configuración.');
        } finally {
          setLoading(false);
        }
      };

      if (!settings) return <p>Cargando configuración...</p>;

      return (
        <div className="max-w-2xl">
          <SectionCard title="Reglas comerciales" subtitle="Define los porcentajes por defecto para el cálculo de precios.">
            <form onSubmit={handleSubmit} className="mt-4 space-y-6">
              
              <div className="grid grid-cols-3 gap-4">
                <label className="block text-sm font-medium text-slate-700">Margen Mínimo (%)
                  <input type="number" step="0.1" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={settings.margen_minimo_porcentaje} onChange={e => setSettings({...settings, margen_minimo_porcentaje: Number(e.target.value)})} />
                </label>
                <label className="block text-sm font-medium text-slate-700 text-brand-600">Margen Recomendado (%)
                  <input type="number" step="0.1" className="mt-1 w-full rounded-xl border border-brand-200 p-3 ring-1 ring-brand-100" value={settings.margen_recomendado_porcentaje} onChange={e => setSettings({...settings, margen_recomendado_porcentaje: Number(e.target.value)})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Margen Premium (%)
                  <input type="number" step="0.1" className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={settings.margen_premium_porcentaje} onChange={e => setSettings({...settings, margen_premium_porcentaje: Number(e.target.value)})} />
                </label>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">IVA por defecto (%)
                  <input type="number" step="0.1" className="mt-1 w-full rounded-xl border border-slate-200 p-3 bg-slate-50" value={settings.iva_porcentaje_default} onChange={e => setSettings({...settings, iva_porcentaje_default: Number(e.target.value)})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Redondeo comercial
                  <select className="mt-1 w-full rounded-xl border border-slate-200 p-3" value={settings.redondeo_precio} onChange={e => setSettings({...settings, redondeo_precio: e.target.value as any})}>
                    <option value="ninguno">Sin redondeo (Ej: $1.234)</option>
                    <option value="100">A la centena (Ej: $1.200)</option>
                    <option value="500">A los 500 (Ej: $1.500)</option>
                    <option value="1000">A la luca (Ej: $1.000)</option>
                  </select>
                </label>
              </div>

              <hr className="border-slate-100" />

              <button type="submit" disabled={loading} className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-6 py-3 font-semibold text-white hover:bg-slate-800 disabled:opacity-50">
                <Save size={18} />
                Guardar cambios
              </button>
            </form>
          </SectionCard>
        </div>
      );
    }
  ''').strip() + '\n',

  'src/pages/UsersPage.tsx': dedent('''
    import { useEffect, useState } from 'react';
    import { UserPlus } from 'lucide-react';
    import SectionCard from '../components/SectionCard';
    import { api } from '../services/api';
    import type { User } from '../services/types';
    import { formatDate } from '../utils/format';

    export default function UsersPage() {
      const [users, setUsers] = useState<User[]>([]);

      useEffect(() => {
        api.get('/users').then(res => setUsers(res.data));
      }, []);

      return (
        <div className="space-y-6">
          <div className="flex justify-end">
            <button className="inline-flex items-center gap-2 rounded-2xl bg-brand-500 px-6 py-3 font-semibold text-white hover:bg-brand-600">
              <UserPlus size={18} />
              Nuevo usuario
            </button>
          </div>
          
          <SectionCard title="Usuarios del sistema">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-500">
                    <th className="pb-3 font-medium">Nombre</th>
                    <th className="pb-3 font-medium">Email</th>
                    <th className="pb-3 font-medium">Rol</th>
                    <th className="pb-3 font-medium">Estado</th>
                    <th className="pb-3 font-medium">Creación</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50">
                      <td className="py-4 font-medium text-slate-900">{u.nombre}</td>
                      <td className="py-4 text-slate-600">{u.email}</td>
                      <td className="py-4"><span className="rounded-lg bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600 uppercase">{u.rol}</span></td>
                      <td className="py-4">
                        <span className={`inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium ${u.activo ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                          <span className={`h-1.5 w-1.5 rounded-full ${u.activo ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                          {u.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="py-4 text-slate-500">{formatDate(u.fecha_creacion)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>
      );
    }
  ''').strip() + '\n',
}

for rel, content in files.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
