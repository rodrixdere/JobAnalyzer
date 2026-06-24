import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import MyProfile from './pages/MyProfile'
import JobCompatibility from './pages/JobCompatibility'
import JobTracker from './pages/JobTracker'
import Login from './pages/Login'
import AdminPanel from './pages/AdminPanel'

function PrivateLayout({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return (
    <div className="min-h-screen bg-[#F5F0E8]">
      <Sidebar />
      <main className="md:ml-56 pt-16 md:pt-0 px-4 md:px-8 py-4 md:py-8">
        {children}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateLayout><Dashboard /></PrivateLayout>} />
        <Route path="/profile" element={<PrivateLayout><MyProfile /></PrivateLayout>} />
        <Route path="/compatibility" element={<PrivateLayout><JobCompatibility /></PrivateLayout>} />
        <Route path="/tracker" element={<PrivateLayout><JobTracker /></PrivateLayout>} />
        <Route path="/admin" element={<PrivateLayout><AdminPanel /></PrivateLayout>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}