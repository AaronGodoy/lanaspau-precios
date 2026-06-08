import { useEffect, useState, useCallback } from 'react';
import { Plus, Edit2, Trash2, Search } from 'lucide-react';
import SectionCard from '../components/SectionCard';
import { api } from '../services/api';

interface Customer {
  id: number;
  rut: string;
  nombre: string;
  telefono: string;
  email: string;
  direccion: string;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  
  const [showModal, setShowModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [form, setForm] = useState({
    rut: '', nombre: '', telefono: '', email: '', direccion: ''
  });

  const fetchCustomers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/customers', { params: { q: search } });
      setCustomers(res.data);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const delay = setTimeout(fetchCustomers, 300);
    return () => clearTimeout(delay);
  }, [fetchCustomers]);

  const handleSave = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      if (editingCustomer) {
        await api.put(`/customers/${editingCustomer.id}`, form);
      } else {
        await api.post('/customers', form);
      }
      setShowModal(false);
      fetchCustomers();
    } catch (err: unknown) {
      if (err instanceof Error && 'response' in err && (err as { response?: { data?: { detail?: string } } }).response?.data?.detail) {
        alert((err as { response: { data: { detail: string } } }).response.data.detail);
      } else {
        alert('Error al guardar cliente');
      }
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Seguro que deseas eliminar este cliente?')) return;
    try {
      await api.delete(`/customers/${id}`);
      fetchCustomers();
    } catch {
      alert('Error al eliminar');
    }
  };

  const openCreate = () => {
    setEditingCustomer(null);
    setForm({ rut: '', nombre: '', telefono: '', email: '', direccion: '' });
    setShowModal(true);
  };

  const openEdit = (c: Customer) => {
    setEditingCustomer(c);
    setForm({
      rut: c.rut || '',
      nombre: c.nombre,
      telefono: c.telefono || '',
      email: c.email || '',
      direccion: c.direccion || ''
    });
    setShowModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Buscar por nombre o RUT..."
            className="w-full rounded-2xl border border-slate-200 py-3 pl-10 pr-4 outline-none focus:border-brand-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button onClick={openCreate} className="flex items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 py-3 text-sm font-semibold text-white hover:bg-brand-600 transition-colors">
          <Plus size={18} />
          Nuevo Cliente
        </button>
      </div>

      <SectionCard title="Directorio de Clientes">
        {loading ? (
          <div className="py-8 text-center text-slate-500">Cargando...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium rounded-tl-xl">Nombre</th>
                  <th className="px-4 py-3 font-medium">RUT</th>
                  <th className="px-4 py-3 font-medium">Contacto</th>
                  <th className="px-4 py-3 font-medium rounded-tr-xl text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map(c => (
                  <tr key={c.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-4 font-medium text-slate-900">{c.nombre}</td>
                    <td className="px-4 py-4">{c.rut || '-'}</td>
                    <td className="px-4 py-4">
                      {c.telefono && <div>{c.telefono}</div>}
                      {c.email && <div className="text-xs text-slate-400">{c.email}</div>}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button onClick={() => openEdit(c)} className="p-2 text-slate-400 hover:text-brand-600 rounded-lg hover:bg-brand-50"><Edit2 size={16} /></button>
                        <button onClick={() => handleDelete(c.id)} className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50"><Trash2 size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
                {customers.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-slate-500">No hay clientes registrados.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold text-slate-900 mb-6">
              {editingCustomer ? 'Editar Cliente' : 'Nuevo Cliente'}
            </h2>
            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Nombre *</label>
                <input required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">RUT</label>
                <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.rut} onChange={e => setForm({...form, rut: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <label className="block text-sm font-medium text-slate-700">Teléfono
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.telefono} onChange={e => setForm({...form, telefono: e.target.value})} />
                </label>
                <label className="block text-sm font-medium text-slate-700">Email
                  <input type="email" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
                </label>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Dirección</label>
                <textarea className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" rows={2} value={form.direccion} onChange={e => setForm({...form, direccion: e.target.value})}></textarea>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 rounded-xl px-4 py-3 font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200">Cancelar</button>
                <button type="submit" className="flex-1 rounded-xl bg-brand-500 px-4 py-3 font-bold text-white hover:bg-brand-600">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}