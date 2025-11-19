import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, LogOut, ArrowRight } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../api/client'

export default function Home() {
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!address.trim()) return

    setLoading(true)
    try {
      const response = await api.post('/process_v3', {
        raw_address: address,
        addons: ['deliverability', 'safety']
      })
      navigate('/results', { state: { data: response.data, address } })
    } catch (error) {
      console.error('Error processing address:', error)
      // Handle error
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#FAF7F0]">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-[#E8E0D1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-[#2C2C2C]">LocaLens</h1>
              <span className="text-sm text-[#6B6B6B]">
                Welcome, {user?.username}
              </span>
            </div>
            <button
              onClick={logout}
              className="flex items-center space-x-2 text-[#6B6B6B] hover:text-[#2C2C2C] transition-colors"
            >
              <LogOut size={18} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-2xl text-center">
          <h1 className="text-3xl font-semibold text-[#2C2C2C] mb-4">
            LocaLens
          </h1>
          <p className="text-lg text-[#6B6B6B] mb-8">
            Intelligent geospatial analysis powered by HERE Technologies, delivering actionable insights for location-based decision making.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="relative">
              <MapPin className="absolute left-4 top-4 h-5 w-5 text-[#6B6B6B]" />
              <textarea
                id="address"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full pl-12 pr-4 py-4 border border-[#E8E0D1] rounded-lg focus:ring-2 focus:ring-[#4A7C59] focus:border-transparent resize-none text-[#2C2C2C] placeholder-[#6B6B6B]"
                placeholder="Enter an address to analyze..."
                rows={2}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#4A7C59] text-white py-3 px-6 rounded-lg hover:bg-[#3a5f47] transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <span>Analyzing...</span>
              ) : (
                <>
                  <span>Analyze Address</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Quick Examples */}
          <div className="mt-8">
            <p className="text-sm text-[#6B6B6B] mb-4">Try these examples:</p>
            <div className="flex flex-wrap justify-center gap-3">
              <button
                onClick={() => setAddress("Connaught Place, New Delhi 110001")}
                className="text-sm px-4 py-2 bg-white border border-[#E8E0D1] rounded-lg hover:border-[#4A7C59] transition-colors text-[#2C2C2C]"
              >
                Connaught Place, New Delhi
              </button>
              <button
                onClick={() => setAddress("18 Marine Drive, Fort, Mumbai 400001")}
                className="text-sm px-4 py-2 bg-white border border-[#E8E0D1] rounded-lg hover:border-[#4A7C59] transition-colors text-[#2C2C2C]"
              >
                Marine Drive, Mumbai
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
