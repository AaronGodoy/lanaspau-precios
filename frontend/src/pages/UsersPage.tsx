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
