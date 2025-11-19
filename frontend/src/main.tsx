import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import Login from './pages/Login'
import Home from './pages/Home'
import Results from './pages/Results'
import IndianIntelligenceDemo from './pages/IndianIntelligenceDemo'
import Dashboard from './pages/admin/Dashboard'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './index.css'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF7F0]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A7C59] mx-auto mb-4"></div>
          <p className="text-[#6B6B6B]">Loading...</p>
        </div>
      </div>
    )
  }

  return user ? <>{children}</> : <Navigate to="/login" replace />
}

// Public Route Component (redirects to appropriate page if already logged in)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF7F0]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A7C59] mx-auto mb-4"></div>
          <p className="text-[#6B6B6B]">Loading...</p>
        </div>
      </div>
    )
  }

  if (user) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

// Admin Route Component (only for the default admin user)
function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF7F0]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A7C59] mx-auto mb-4"></div>
          <p className="text-[#6B6B6B]">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (user.username !== 'admin') {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { path: 'login', element: <PublicRoute><Login /></PublicRoute> },
      { path: 'process', element: <Navigate to="/" replace /> },
      { path: 'home', element: <Navigate to="/" replace /> },
      { index: true, element: <ProtectedRoute><Home /></ProtectedRoute> },
      { path: 'results', element: <ProtectedRoute><Results /></ProtectedRoute> },
      { path: 'indian-intelligence', element: <ProtectedRoute><IndianIntelligenceDemo /></ProtectedRoute> },
      { path: 'admin/dashboard', element: <AdminRoute><Dashboard /></AdminRoute> }
    ]
  }
])

const queryClient = new QueryClient()

let root: ReactDOM.Root

const container = document.getElementById('root')!
if (!container) {
  throw new Error('Root element not found')
}

if (!(container as any).__react_root) {
  root = ReactDOM.createRoot(container)
  ;(container as any).__react_root = root
} else {
  root = (container as any).__react_root
}

root.render(
  <React.StrictMode>
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </AuthProvider>
  </React.StrictMode>
)
