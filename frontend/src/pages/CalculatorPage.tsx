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
