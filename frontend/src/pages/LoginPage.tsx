import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage() {
  const { login, loading, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('admin@lanaspau.cl');
  const [password, setPassword] = useState('Admin1234!');
  const [error, setError] = useState('');

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch {
      setError('No fue posible iniciar sesion. Revisa email y clave.');
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="grid w-full max-w-5xl gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl bg-slate-900 p-8 text-white shadow-xl relative overflow-hidden">
          <img src="/logo.png" alt="Lanas Pau" className="absolute top-4 right-4 w-24 h-24 object-cover rounded-full shadow-lg opacity-80" />
          <p className="text-sm uppercase tracking-[0.3em] text-brand-100">Lanas Pau</p>
          <h1 className="mt-4 text-4xl font-semibold">Calcula el mejor precio de venta para cada lana.</h1>
          <p className="mt-4 max-w-xl text-base text-slate-200">Registra costos reales, incluye IVA, gastos adicionales y obt?n una recomendacion clara de precio minimo, recomendado y premium.</p>
        </section>
        <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-semibold text-slate-900">Iniciar sesion</h2>
          <p className="mt-2 text-sm text-slate-500">Usa el usuario administrador cargado por defecto para comenzar.</p>
          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <label className="block text-sm font-medium text-slate-700">Email
              <input className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label className="block text-sm font-medium text-slate-700">Contrasena
              <input type="password" className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3" value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
            {error ? <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{error}</p> : null}
            <button type="submit" disabled={loading} className="w-full rounded-2xl bg-brand-500 px-4 py-3 text-base font-semibold text-white hover:bg-brand-600 disabled:opacity-60">
              {loading ? 'Ingresando...' : 'Entrar al sistema'}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
