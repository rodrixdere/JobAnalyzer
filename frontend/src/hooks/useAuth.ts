import { useState, useEffect } from 'react'

interface AuthUser {
  is_admin: boolean
}

export function useAuth(): AuthUser {
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(r => r.json())
        .then(user => setIsAdmin(user.is_admin))
        .catch(() => {})
    } catch {}
  }, [])

  return { is_admin: isAdmin }
}