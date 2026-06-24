import { useState, useEffect } from 'react'
import { Plus, X, ShieldOff, Shield, Trash2, Users, UserCheck, UserX, ShieldCheck, Eye, EyeOff } from 'lucide-react'
import { AdminUserResponse } from '../types'

const adminApi = {
  list: () => fetch('/api/admin/users', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  }).then(r => r.json()) as Promise<AdminUserResponse[]>,

  create: (email: string, password: string, is_admin: boolean) =>
    fetch('/api/admin/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ email, password, is_admin }),
    }).then(r => r.json()) as Promise<AdminUserResponse>,

  toggle: (id: string, is_active: boolean) =>
    fetch(`/api/admin/users/${id}/toggle`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ is_active }),
    }).then(r => r.json()) as Promise<AdminUserResponse>,

  delete: (id: string) =>
    fetch(`/api/admin/users/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    }),
}

const stats = (total: number, active: number, paused: number, admins: number) => [
  { label: 'Total Users', value: total, color: 'bg-blue-500', icon: Users },
  { label: 'Active Users', value: active, color: 'bg-green-500', icon: UserCheck },
  { label: 'Paused Users', value: paused, color: 'bg-yellow-500', icon: UserX },
  { label: 'Admins', value: admins, color: 'bg-purple-500', icon: ShieldCheck },
]

export default function AdminPanel() {
  const [users, setUsers] = useState<AdminUserResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', is_admin: false })
  const [showPassword, setShowPassword] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    adminApi.list()
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setLoading(false))
  }, [])

  async function handleCreate() {
    if (!form.email.trim() || !form.password.trim()) {
      setError('Email and password are required')
      return
    }
    setSaving(true)
    setError(null)
    try {
      const user = await adminApi.create(form.email, form.password, form.is_admin)
      setUsers(prev => [user, ...prev])
      setShowModal(false)
      setForm({ email: '', password: '', is_admin: false })
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleToggle(user: AdminUserResponse) {
    const updated = await adminApi.toggle(user.id, !user.is_active)
    setUsers(prev => prev.map(u => u.id === updated.id ? updated : u))
  }

  async function handleDelete(id: string) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return
    await adminApi.delete(id)
    setUsers(prev => prev.filter(u => u.id !== id))
  }

  function formatDate(date: string | null) {
    if (!date) return 'Never'
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    })
  }

  const totalUsers = users.length
  const activeUsers = users.filter(u => u.is_active).length
  const pausedUsers = users.filter(u => !u.is_active).length
  const adminUsers = users.filter(u => u.is_admin).length

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-500 mt-1 text-sm">Manage users and monitor platform activity</p>
        </div>
        <button
          onClick={() => { setShowModal(true); setError(null) }}
          className="flex items-center gap-2 px-3 md:px-4 py-2 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Add User</span>
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {stats(totalUsers, activeUsers, pausedUsers, adminUsers).map(stat => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-gray-200">
              <div className={`${stat.color} w-10 h-10 rounded-lg mb-3 flex items-center justify-center`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <div className="text-2xl md:text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-xs md:text-sm text-gray-500">{stat.label}</div>
            </div>
          )
        })}
      </div>

      {/* Desktop table */}
      <div className="hidden md:block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#F5F0E8] border-b border-gray-200">
              <tr>
                {['Email', 'Status', 'Role', 'Last Seen', 'Created', 'Actions'].map(h => (
                  <th key={h} className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-400">Loading...</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-400">No users found.</td></tr>
              ) : users.map(user => (
                <tr key={user.id} className="border-b border-gray-100 last:border-0 hover:bg-[#F5F0E8]/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {user.is_active ? 'Active' : 'Paused'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${user.is_admin ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                      {user.is_admin ? 'Admin' : 'User'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(user.last_seen)}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(user.created_at)}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleToggle(user)} title={user.is_active ? 'Pause' : 'Activate'}
                        className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                        {user.is_active ? <ShieldOff className="w-4 h-4 text-yellow-500" /> : <Shield className="w-4 h-4 text-green-500" />}
                      </button>
                      <button onClick={() => handleDelete(user.id)} title="Delete"
                        className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile cards */}
      <div className="md:hidden space-y-3">
        {loading ? (
          <p className="text-center text-sm text-gray-400 py-8">Loading...</p>
        ) : users.length === 0 ? (
          <p className="text-center text-sm text-gray-400 py-8">No users found.</p>
        ) : users.map(user => (
          <div key={user.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{user.email}</p>
                <p className="text-xs text-gray-500 mt-0.5">Last seen: {formatDate(user.last_seen)}</p>
              </div>
              <div className="flex gap-1.5 ml-2">
                <button onClick={() => handleToggle(user)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                  {user.is_active ? <ShieldOff className="w-4 h-4 text-yellow-500" /> : <Shield className="w-4 h-4 text-green-500" />}
                </button>
                <button onClick={() => handleDelete(user.id)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            </div>
            <div className="flex gap-2">
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {user.is_active ? 'Active' : 'Paused'}
              </span>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${user.is_admin ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                {user.is_admin ? 'Admin' : 'User'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-0 sm:p-4">
          <div className="bg-white rounded-t-2xl sm:rounded-xl shadow-xl w-full sm:max-w-md">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">Create User</h2>
              <button onClick={() => setShowModal(false)}><X className="w-5 h-5 text-gray-400" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Email</label>
                <input type="email" value={form.email}
                  onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                  className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Password</label>
                <div className="relative">
                  <input type={showPassword ? 'text' : 'password'} value={form.password}
                    onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                    className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm pr-10" />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <input type="checkbox" id="is_admin" checked={form.is_admin}
                  onChange={e => setForm(p => ({ ...p, is_admin: e.target.checked }))}
                  className="w-4 h-4 accent-[#6C63FF]" />
                <label htmlFor="is_admin" className="text-sm text-gray-700">Grant admin privileges</label>
              </div>
              {error && <p className="text-red-500 text-sm">{error}</p>}
            </div>
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-gray-500">Cancel</button>
              <button onClick={handleCreate} disabled={saving}
                className="px-4 py-2 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold disabled:opacity-50">
                {saving ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}