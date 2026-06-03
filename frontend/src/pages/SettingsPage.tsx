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
