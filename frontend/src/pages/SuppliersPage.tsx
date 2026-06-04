import { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Truck } from 'lucide-react';
import { api } from '../services/api';
import SectionCard from '../components/SectionCard';

export interface Supplier {
  id: number;
  nombre: string;
  contacto?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  notas?: string;
  activo: boolean;
}

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  
  const [form, setForm] = useState({
    nombre: '',
    contacto: '',
    telefono: '',
    email: '',
    direccion: '',
    notas: ''
  });

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/suppliers');
      setSuppliers(res.data);
    } catch (err) {
      console.error(err);
      alert('Error al cargar proveedores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const openCreateModal = () => {
    setEditingSupplier(null);
    setForm({ nombre: '', contacto: '', telefono: '', email: '', direccion: '', notas: '' });
    setShowModal(true);
  };

  const openEditModal = (s: Supplier) => {
    setEditingSupplier(s);
    setForm({
      nombre: s.nombre,
      contacto: s.contacto || '',
      telefono: s.telefono || '',
      email: s.email || '',
      direccion: s.direccion || '',
      notas: s.notas || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Estás seguro de eliminar este proveedor?')) return;
    try {
      await api.delete(`/suppliers/${id}`);
      fetchSuppliers();
    } catch (err) {
      alert('Error al eliminar');
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingSupplier) {
        await api.put(`/suppliers/${editingSupplier.id}`, form);
      } else {
        await api.post('/suppliers', form);
      }
      setShowModal(false);
      fetchSuppliers();
    } catch (err) {
      alert('Error al guardar el proveedor');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-slate-900">Directorio de Proveedores</h1>
        <button onClick={openCreateModal} className="flex items-center gap-2 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 transition-colors">
          <Plus size={18} />
          Nuevo Proveedor
        </button>
      </div>

      <SectionCard title="Lista de Proveedores">
        {loading ? (
          <p className="text-slate-500 p-4">Cargando proveedores...</p>
        ) : suppliers.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <Truck size={48} className="mx-auto mb-4 opacity-20" />
            <p>No tienes proveedores registrados.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {suppliers.map(s => (
              <div key={s.id} className="border border-slate-200 p-5 rounded-2xl bg-white hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-lg text-slate-900 leading-tight">{s.nombre}</h3>
                  <div className="flex gap-2">
                    <button onClick={() => openEditModal(s)} className="text-slate-400 hover:text-brand-600"><Edit2 size={16} /></button>
                    <button onClick={() => handleDelete(s.id)} className="text-slate-400 hover:text-red-600"><Trash2 size={16} /></button>
                  </div>
                </div>
                
                <div className="space-y-2 text-sm text-slate-600">
                  {s.contacto && <p><span className="font-medium text-slate-400">Contacto:</span> {s.contacto}</p>}
                  {s.telefono && <p><span className="font-medium text-slate-400">Teléfono:</span> {s.telefono}</p>}
                  {s.email && <p><span className="font-medium text-slate-400">Email:</span> {s.email}</p>}
                  {s.direccion && <p className="truncate"><span className="font-medium text-slate-400">Dirección:</span> {s.direccion}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-xl">
            <h2 className="text-xl font-bold text-slate-900 mb-6">
              {editingSupplier ? 'Editar Proveedor' : 'Nuevo Proveedor'}
            </h2>
            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Nombre Empresa / Marca *</label>
                <input required className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Persona de Contacto</label>
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.contacto} onChange={e => setForm({...form, contacto: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Teléfono / WhatsApp</label>
                  <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.telefono} onChange={e => setForm({...form, telefono: e.target.value})} />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700">Email</label>
                <input type="email" className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700">Dirección Física</label>
                <input className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" value={form.direccion} onChange={e => setForm({...form, direccion: e.target.value})} />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700">Notas / Condiciones de envío</label>
                <textarea className="mt-1 w-full rounded-xl border border-slate-200 p-2.5" rows={3} value={form.notas} onChange={e => setForm({...form, notas: e.target.value})} />
              </div>

              <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-slate-100">
                <button type="button" onClick={() => setShowModal(false)} className="rounded-xl px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100">Cancelar</button>
                <button type="submit" className="rounded-xl bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">Guardar Proveedor</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
