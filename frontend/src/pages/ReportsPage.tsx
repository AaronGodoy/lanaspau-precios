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
            <button onClick={() => handleDownload('products', 'Catalogo_Lanas_Pau')} className="mt-auto inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800">
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
