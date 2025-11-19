import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface AuthFormProps {
  onSuccess?: () => void
}

export default function AuthForm({ onSuccess }: AuthFormProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, signup, isLoading } = useAuth()
  const navigate = useNavigate()

  const validatePassword = (password: string): { isValid: boolean; message: string } => {
    if (password.length < 8) {
      return { isValid: false, message: 'Password must be at least 8 characters long' }
    }
    if (!/[A-Z]/.test(password)) {
      return { isValid: false, message: 'Password must contain at least one uppercase letter' }
    }
    if (!/[a-z]/.test(password)) {
      return { isValid: false, message: 'Password must contain at least one lowercase letter' }
    }
    if (!/\d/.test(password)) {
      return { isValid: false, message: 'Password must contain at least one number' }
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      return { isValid: false, message: 'Password must contain at least one special character' }
    }
    return { isValid: true, message: 'Strong password!' }
  }

  const getPasswordStrength = (password: string): { level: string; color: string } => {
    const validation = validatePassword(password)
    if (!validation.isValid) return { level: 'Weak', color: 'text-red-600' }
    if (password.length >= 12) return { level: 'Very Strong', color: 'text-green-600' }
    if (password.length >= 10) return { level: 'Strong', color: 'text-green-500' }
    return { level: 'Good', color: 'text-yellow-600' }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    if (!password.trim()) {
      setError('Please enter a password')
      return
    }

    if (!isLogin) {
      const passwordValidation = validatePassword(password)
      if (!passwordValidation.isValid) {
        setError(passwordValidation.message)
        return
      }
    }

    try {
      let success = false
      if (isLogin) {
        success = await login(username, password)
      } else {
        success = await signup(username, password, 'user')
      }

      if (success) {
        if (username === 'admin' && password === 'Admin123') {
          window.location.href = '/admin/dashboard'
        } else {
          onSuccess ? onSuccess() : navigate('/')
        }
      } else {
        setError(isLogin ? 'Invalid username or password' : 'Username already exists')
      }
    } catch (err) {
      setError('An error occurred. Please try again.')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white p-8 rounded-2xl shadow-lg border border-[#E8E0D1] w-full max-w-md"
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-[#2C2C2C] mb-2">
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="text-[#6B6B6B]">
          {isLogin ? 'Sign in to your account' : 'Join LocalLens today'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-[#2C2C2C] mb-2">
            Username
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 border border-[#E8E0D1] rounded-xl focus:ring-2 focus:ring-[#4A7C59] focus:border-transparent transition-all"
            placeholder="Enter your username"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-[#2C2C2C] mb-2">
            Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 border border-[#E8E0D1] rounded-xl focus:ring-2 focus:ring-[#4A7C59] focus:border-transparent transition-all"
            placeholder="Enter your password"
            disabled={isLoading}
          />
          {!isLogin && password && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#6B6B6B]">Password strength:</span>
                <span className={`font-medium ${getPasswordStrength(password).color}`}>
                  {getPasswordStrength(password).level}
                </span>
              </div>
              <div className="w-full bg-[#E8E0D1] rounded-full h-2 mt-1">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    getPasswordStrength(password).level === 'Weak' ? 'bg-red-500 w-1/4' :
                    getPasswordStrength(password).level === 'Good' ? 'bg-yellow-500 w-2/3' :
                    getPasswordStrength(password).level === 'Strong' ? 'bg-green-500 w-4/5' :
                    'bg-green-600 w-full'
                  }`}
                ></div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-lg">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-[#4A7C59] hover:bg-[#3A5A45] disabled:bg-[#6B6B6B] text-white py-3 px-4 rounded-xl font-medium transition-all hover:shadow-lg disabled:cursor-not-allowed"
        >
          {isLoading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
        </button>
      </form>

      <div className="mt-6 text-center">
        <button
          onClick={() => {
            setIsLogin(!isLogin)
            setError('')
            setUsername('')
            setPassword('')
          }}
          className="text-[#4A7C59] hover:text-[#3A5A45] text-sm font-medium transition-colors"
          disabled={isLoading}
        >
          {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
        </button>
      </div>
    </motion.div>
  )
}