import { useNavigate } from 'react-router-dom'
import AuthForm from '../components/AuthForm'
import { useAuth } from '../contexts/AuthContext'

export default function Landing() {
  const navigate = useNavigate()
  const { user } = useAuth()

  const handleAuthSuccess = () => {
    if (user?.role === 'admin') {
      navigate('/health')
    } else {
      navigate('/home')
    }
  }

  return (
    <div className="min-h-screen bg-[#FAF7F0] flex items-center justify-center p-6">
      <div className="w-full max-w-md text-center">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-[#2C2C2C] mb-4">
            LocaLens
          </h1>
          <p className="text-lg text-[#6B6B6B]">
            Intelligent geospatial analysis powered by HERE Technologies, delivering actionable insights for location-based decision making.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-[#E8E0D1] p-8">
          <AuthForm onSuccess={handleAuthSuccess} />
        </div>

        <div className="mt-6 space-y-2">
          <div className="flex items-center justify-center space-x-3">
            <div className="w-2 h-2 bg-[#4A7C59] rounded-full"></div>
            <span className="text-[#2C2C2C] text-sm">HERE Maps Integration</span>
          </div>
          <div className="flex items-center justify-center space-x-3">
            <div className="w-2 h-2 bg-[#4A7C59] rounded-full"></div>
            <span className="text-[#2C2C2C] text-sm">AI-Powered Intelligence</span>
          </div>
          <div className="flex items-center justify-center space-x-3">
            <div className="w-2 h-2 bg-[#4A7C59] rounded-full"></div>
            <span className="text-[#2C2C2C] text-sm">Real-time Geospatial Analysis</span>
          </div>
          <div className="flex items-center justify-center space-x-3">
            <div className="w-2 h-2 bg-[#4A7C59] rounded-full"></div>
            <span className="text-[#2C2C2C] text-sm">Advanced Location Insights</span>
          </div>
        </div>
      </div>
    </div>
  )
}
