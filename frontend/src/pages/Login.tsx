import { motion } from 'framer-motion'
import AuthForm from '../components/AuthForm'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen flex bg-[#FAF7F0]">
      {/* Left Side - Description (1/4) */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="w-1/4 flex items-center justify-center p-8 bg-[#FAF7F0]"
      >
        <div className="max-w-sm space-y-6">
          <div className="space-y-4">
            <h1 className="text-4xl lg:text-5xl font-bold text-[#2C2C2C] leading-tight">
              LocaLens
            </h1>
            <p className="text-lg text-[#6B6B6B] leading-relaxed">
              Intelligent geospatial analysis powered by HERE Technologies, delivering actionable insights for location-based decision making.
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-[#4A7C59] rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">✓</span>
              </div>
              <span className="text-[#2C2C2C] font-medium text-sm">HERE Maps Integration</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-[#4A7C59] rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">✓</span>
              </div>
              <span className="text-[#2C2C2C] font-medium text-sm">AI-Powered Intelligence</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-[#4A7C59] rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">✓</span>
              </div>
              <span className="text-[#2C2C2C] font-medium text-sm">Real-time Geospatial Analysis</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-[#4A7C59] rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">✓</span>
              </div>
              <span className="text-[#2C2C2C] font-medium text-sm">Advanced Location Insights</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Right Side - Auth Form (3/4) */}
      <motion.div
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="w-3/4 flex items-center justify-center p-8 bg-white"
      >
        <AuthForm />
      </motion.div>
    </div>
  )
}