import type { Profile, ExperienceItem, ProjectItem, EducationItem, ProfileLinks, AnalysisListItem, Analysis, JobApplication, AdminUserResponse } from '../types'

const BASE_URL = '/api'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()

  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  })

  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('No autorizado')
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Error desconocido' }))
    throw new Error(error.detail || 'Error en la solicitud')
  }

  if (res.status === 204) return null as T
  return res.json()
}

async function requestForm<T>(path: string, formData: FormData): Promise<T> {
  const token = getToken()

  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  })

  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('No autorizado')
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Error desconocido' }))
    throw new Error(error.detail || 'Error en la solicitud')
  }

  return res.json()
}

export const authApi = {
  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
}

export const profileApi = {
  get: () => request<Profile>('/profile/'),
  parseCV: (text: string) =>
    request<Profile>('/profile/parse-cv', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),
  uploadCV: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return requestForm<Profile>('/profile/upload-cv', formData)
  },
  update: (data: {
    full_name?: string
    professional_title?: string
    email?: string
    skills?: string[]
    experience?: ExperienceItem[]
    projects?: ProjectItem[]
    education?: EducationItem[]
    languages?: string[]
    links?: ProfileLinks
  }) =>
    request<Profile>('/profile/', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
}

export const analysisApi = {
  list: () => request<AnalysisListItem[]>('/analysis/'),
  get: (id: string) => request<Analysis>(`/analysis/${id}`),
  create: (jobText: string) =>
    request<Analysis>('/analysis/', {
      method: 'POST',
      body: JSON.stringify({ job_text: jobText }),
    }),
  delete: (id: string) => request<null>(`/analysis/${id}`, { method: 'DELETE' }),
}

export const trackerApi = {
  list: () => request<JobApplication[]>('/tracker/'),
  create: (data: Partial<JobApplication>) =>
    request<JobApplication>('/tracker/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: string, data: Partial<JobApplication>) =>
    request<JobApplication>(`/tracker/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: string) => request<null>(`/tracker/${id}`, { method: 'DELETE' }),
}