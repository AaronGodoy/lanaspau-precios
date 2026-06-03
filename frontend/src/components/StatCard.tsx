import type { ReactNode } from 'react';

export default function StatCard({ label, value, hint, icon }: { label: string; value: string; hint: string; icon: ReactNode }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between text-slate-500">
        <span className="text-sm font-medium">{label}</span>
        <span className="rounded-xl bg-brand-50 p-2 text-brand-600">{icon}</span>
      </div>
      <div className="text-2xl font-semibold text-slate-900">{value}</div>
      <p className="mt-2 text-sm text-slate-500">{hint}</p>
    </div>
  );
}
