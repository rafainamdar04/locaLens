import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { AUTH_CONFIG } from '../config/auth'

interface User {
  id: string
  username: string
  role: 'user' | 'admin'
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<boolean>
  signup: (username: string, password: string, role: 'user' | 'admin') => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on app start
    const savedUser = localStorage.getItem('locallens_user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (error) {
        localStorage.removeItem('locallens_user')
      }
    }

    // Initialize admin account if not exists
    const users = JSON.parse(localStorage.getItem('locallens_users') || '[]')
    const adminExists = users.some((u: any) => u.username === 'admin')
    if (!adminExists) {
      users.push({
        id: 'admin-001',
        username: 'admin',
        password: 'Admin123',
        role: 'admin'
      })
      localStorage.setItem('locallens_users', JSON.stringify(users))
    }

    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true)

    // Simulate API call - in real app, this would call your backend
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Get users from localStorage (in real app, this would come from backend)
    const users = JSON.parse(localStorage.getItem('locallens_users') || '[]')
    const foundUser = users.find((u: any) => u.username === username && u.password === password)

    if (foundUser) {
      const userData = { id: foundUser.id, username: foundUser.username, role: foundUser.role }
      setUser(userData)
      localStorage.setItem('locallens_user', JSON.stringify(userData))
      setIsLoading(false)
      return true
    }

    setIsLoading(false)
    return false
  }

  const signup = async (username: string, password: string, role: 'user' | 'admin'): Promise<boolean> => {
    setIsLoading(true)

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Get existing users
    const users = JSON.parse(localStorage.getItem('locallens_users') || '[]')

    // Check if user already exists
    if (users.some((u: any) => u.username === username)) {
      setIsLoading(false)
      return false
    }

    // Don't allow 'admin' as username for regular users
    if (username === 'admin') {
      setIsLoading(false)
      return false
    }

    // Create new user
    const newUser = {
      id: Date.now().toString(),
      username,
      password, // In real app, this would be hashed
      role
    }

    users.push(newUser)
    localStorage.setItem('locallens_users', JSON.stringify(users))

    const userData = { id: newUser.id, username: newUser.username, role: newUser.role }
    setUser(userData)
    localStorage.setItem('locallens_user', JSON.stringify(userData))

    setIsLoading(false)
    return true
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('locallens_user')
  }

  const value = {
    user,
    login,
    signup,
    logout,
    isLoading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}