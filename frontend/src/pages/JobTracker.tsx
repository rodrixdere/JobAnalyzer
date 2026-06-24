import { useState, useEffect } from 'react'
import { Plus, ExternalLink, Filter, X } from 'lucide-react'
import { trackerApi } from '../services/api'
import { JobApplication, JobStatus, JobType } from '../types'

const STATUS_COLORS: Record<JobStatus, string> = {
  Inbox: 'bg-gray-400',
  Applied: 'bg-yellow-500',
  Interview: 'bg-blue-500',
  Offered: 'bg-purple-500',
  Accepted: 'bg-green-500',
  Rejected: 'bg-red-500',
}

const STATUSES: JobStatus[] = ['Inbox', 'Applied', 'Interview', 'Offered', 'Accepted', 'Rejected']
const TYPES: JobType[] = ['Remote', 'Hybrid', 'On-site']

interface JobFormData {
  job_title: string
  company: string
  status: JobStatus
  type: JobType | ''
  date_applied: string
  interview_date: string
  deadline: string
  keywords: string
  link: string
  notes: string
}

const EMPTY_FORM: JobFormData = {
  job_title: '',
  company: '',
  status: 'Inbox',
  type: '',
  date_applied: '',
  interview_date: '',
  deadline: '',
  keywords: '',
  link: '',
  notes: '',
}

export default function JobTracker() {
  const [jobs, setJobs] = useState<JobApplication[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState<JobStatus | ''>('')
  const [showModal, setShowModal] = useState(false)
  const [editingJob, setEditingJob] = useState<JobApplication | null>(null)
  const [form, setForm] = useState<JobFormData>(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    trackerApi.list()
      .then(setJobs)
      .catch(() => setJobs([]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = jobs.filter(j => {
    const matchText = filter === '' ||
      j.job_title.toLowerCase().includes(filter.toLowerCase()) ||
      j.company.toLowerCase().includes(filter.toLowerCase()) ||
      j.keywords.some(k => k.toLowerCase().includes(filter.toLowerCase()))
    const matchStatus = statusFilter === '' || j.status === statusFilter
    return matchText && matchStatus
  })

  function openCreate() {
    setEditingJob(null)
    setForm(EMPTY_FORM)
    setError(null)
    setShowModal(true)
  }

  function openEdit(job: JobApplication) {
    setEditingJob(job)
    setForm({
      job_title: job.job_title,
      company: job.company,
      status: job.status,
      type: job.type || '',
      date_applied: job.date_applied || '',
      interview_date: job.interview_date || '',
      deadline: job.deadline || '',
      keywords: job.keywords.join(', '),
      link: job.link || '',
      notes: job.notes || '',
    })
    setError(null)
    setShowModal(true)
  }

  async function handleSave() {
    if (!form.job_title.trim() || !form.company.trim()) {
      setError('Job title and company are required')
      return
    }
    setSaving(true)
    setError(null)

    const data = {
      job_title: form.job_title,
      company: form.company,
      status: form.status,
      type: form.type || undefined,
      date_applied: form.date_applied || undefined,
      interview_date: form.interview_date || undefined,
      deadline: form.deadline || undefined,
      keywords: form.keywords ? form.keywords.split(',').map(k => k.trim()).filter(Boolean) : [],
      link: form.link || undefined,
      notes: form.notes || undefined,
    }

    try {
      if (editingJob) {
        const updated = await trackerApi.update(editingJob.id, data)
        setJobs(prev => prev.map(j => j.id === updated.id ? updated : j))
      } else {
        const created = await trackerApi.create(data)
        setJobs(prev => [created, ...prev])
      }
      setShowModal(false)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id: string) {
    await trackerApi.delete(id)
    setJobs(prev => prev.filter(j => j.id !== id))
    setShowModal(false)
  }

  async function handleStatusChange(job: JobApplication, status: JobStatus) {
    const updated = await trackerApi.update(job.id, { status })
    setJobs(prev => prev.map(j => j.id === updated.id ? updated : j))
  }

  const modal = showModal && (
    <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50">
      <div className="bg-white rounded-t-2xl sm:rounded-xl shadow-xl w-full sm:max-w-lg">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">{editingJob ? 'Edit Application' : 'Add Application'}</h2>
          <button onClick={() => setShowModal(false)}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Job Title *</label>
              <input value={form.job_title} onChange={e => setForm(p => ({ ...p, job_title: e.target.value }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Company *</label>
              <input value={form.company} onChange={e => setForm(p => ({ ...p, company: e.target.value }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
              <select value={form.status} onChange={e => setForm(p => ({ ...p, status: e.target.value as JobStatus }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm">
                {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
              <select value={form.type} onChange={e => setForm(p => ({ ...p, type: e.target.value as JobType }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm">
                <option value="">Select type</option>
                {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Date Applied</label>
              <input type="date" value={form.date_applied} onChange={e => setForm(p => ({ ...p, date_applied: e.target.value }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Interview Date</label>
              <input type="date" value={form.interview_date} onChange={e => setForm(p => ({ ...p, interview_date: e.target.value }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Deadline</label>
              <input type="date" value={form.deadline} onChange={e => setForm(p => ({ ...p, deadline: e.target.value }))}
                className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Keywords (comma separated)</label>
            <input value={form.keywords} onChange={e => setForm(p => ({ ...p, keywords: e.target.value }))}
              placeholder="React, TypeScript, Node.js"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Link</label>
            <input value={form.link} onChange={e => setForm(p => ({ ...p, link: e.target.value }))}
              placeholder="https://..."
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Notes</label>
            <textarea value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm resize-none" />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
        </div>
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
          {editingJob ? (
            <button onClick={() => handleDelete(editingJob.id)} className="text-red-500 hover:text-red-600 text-sm">Delete</button>
          ) : <div />}
          <div className="flex gap-3">
            <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-gray-500">Cancel</button>
            <button onClick={handleSave} disabled={saving}
              className="px-4 py-2 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold disabled:opacity-50">
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Job Tracker</h1>
          <p className="text-gray-500 mt-1 text-sm">Track and manage your job applications</p>
        </div>
        <button onClick={openCreate}
          className="flex items-center gap-2 px-3 md:px-4 py-2 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold">
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Add Job</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-4 p-3 md:p-4 flex items-center gap-3">
        <Filter className="w-4 h-4 text-gray-400 shrink-0" />
        <input type="text" value={filter} onChange={e => setFilter(e.target.value)}
          placeholder="Filter by title, company, keyword..."
          className="flex-1 px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm min-w-0" />
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as JobStatus | '')}
          className="px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm shrink-0">
          <option value="">All</option>
          {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* Desktop table */}
      <div className="hidden md:block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#F5F0E8] border-b border-gray-200">
              <tr>
                {['Job Title', 'Company', 'Status', 'Type', 'Date Applied', 'Interview', 'Deadline', 'Keywords', 'Link'].map(h => (
                  <th key={h} className="text-left px-5 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="px-6 py-8 text-center text-sm text-gray-400">Loading...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={9} className="px-6 py-8 text-center text-sm text-gray-400">No jobs found. Add your first application.</td></tr>
              ) : filtered.map(job => (
                <tr key={job.id} onClick={() => openEdit(job)}
                  className="border-b border-gray-100 last:border-0 hover:bg-[#F5F0E8]/50 transition-colors cursor-pointer">
                  <td className="px-5 py-4 text-sm font-medium text-gray-900">{job.job_title}</td>
                  <td className="px-5 py-4 text-sm text-gray-500">{job.company}</td>
                  <td className="px-5 py-4" onClick={e => e.stopPropagation()}>
                    <select value={job.status} onChange={e => handleStatusChange(job, e.target.value as JobStatus)}
                      className={`${STATUS_COLORS[job.status]} text-white text-xs px-3 py-1 rounded-full border-0 cursor-pointer focus:outline-none`}>
                      {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-500">{job.type || '-'}</td>
                  <td className="px-5 py-4 text-sm text-gray-500">{job.date_applied || '-'}</td>
                  <td className="px-5 py-4 text-sm text-gray-500">{job.interview_date || '-'}</td>
                  <td className="px-5 py-4 text-sm text-gray-500">{job.deadline || '-'}</td>
                  <td className="px-5 py-4">
                    <div className="flex flex-wrap gap-1">
                      {job.keywords.slice(0, 2).map(k => (
                        <span key={k} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">{k}</span>
                      ))}
                      {job.keywords.length > 2 && (
                        <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">+{job.keywords.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-5 py-4" onClick={e => e.stopPropagation()}>
                    {job.link && (
                      <a href={job.link} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="w-4 h-4 text-[#6C63FF]" />
                      </a>
                    )}
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
        ) : filtered.length === 0 ? (
          <p className="text-center text-sm text-gray-400 py-8">No jobs found. Add your first application.</p>
        ) : filtered.map(job => (
          <div key={job.id} onClick={() => openEdit(job)}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 cursor-pointer hover:border-gray-300 transition-colors">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{job.job_title}</p>
                <p className="text-xs text-gray-500 mt-0.5">{job.company}</p>
              </div>
              <div className="flex items-center gap-2 ml-2" onClick={e => e.stopPropagation()}>
                <select value={job.status} onChange={e => handleStatusChange(job, e.target.value as JobStatus)}
                  className={`${STATUS_COLORS[job.status]} text-white text-xs px-2 py-1 rounded-full border-0 cursor-pointer focus:outline-none`}>
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                {job.link && (
                  <a href={job.link} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>
                    <ExternalLink className="w-4 h-4 text-[#6C63FF]" />
                  </a>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {job.type && (
                <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">{job.type}</span>
              )}
              {job.keywords.slice(0, 3).map(k => (
                <span key={k} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">{k}</span>
              ))}
            </div>
            {job.date_applied && (
              <p className="text-xs text-gray-400 mt-2">Applied: {job.date_applied}</p>
            )}
          </div>
        ))}
      </div>

      {modal}
    </div>
  )
}