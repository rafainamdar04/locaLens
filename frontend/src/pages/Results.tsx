import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { processAddress, getDeliveryNavigation, getSafetyAssessment, type EventPayload } from '../api/client'
import { AddressHeader } from '../components/results/AddressHeader'
import { ComprehensiveResultsCard } from '../components/results/ComprehensiveResultsCard'
import { DeliveryNavigationCard, SafetyAssessmentCard } from '../components/results/LogisticsCards'
import { ArrowLeft } from 'lucide-react'

export default function Results() {
  const navigate = useNavigate()
  const { state } = useLocation() as { state?: { address?: string; addons?: string[]; event?: EventPayload; processing_time_ms?: number } }

  const [event, setEvent] = useState<EventPayload | null>(state?.event || null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [processingTime, setProcessingTime] = useState<number>(state?.processing_time_ms || 0)
  const [deliveryNavigation, setDeliveryNavigation] = useState<any>(null)
  const [safetyAssessment, setSafetyAssessment] = useState<any>(null)
  const [additionalDataLoading, setAdditionalDataLoading] = useState(false)

  useEffect(() => {
    if (state?.address && !event && !loading) {
      processAddressFromState()
    }
  }, [state, event, loading])

  useEffect(() => {
    if (event && !deliveryNavigation && !safetyAssessment && !additionalDataLoading) {
      fetchAdditionalData()
    }
  }, [event, deliveryNavigation, safetyAssessment, additionalDataLoading])

  const processAddressFromState = async () => {
    if (!state?.address) return

    setLoading(true)
    setError(null)

    try {
      const response = await processAddress(state.address, state.addons as any || 'all')
      setEvent(response.event)
      setProcessingTime(response.processing_time_ms)
    } catch (err) {
      console.error('Processing error:', err)
      setError(err instanceof Error ? err.message : 'Failed to process address')
    } finally {
      setLoading(false)
    }
  }

  const fetchAdditionalData = async () => {
    if (!event) return

    // Get coordinates from geocoding results
    const coords = event.here_results?.primary_result?.position ||
                  (event.here_results?.primary_result ? {
                    lat: event.here_results.primary_result.lat,
                    lng: event.here_results.primary_result.lon
                  } : null) ||
                  (event.ml_results?.top_result ? {
                    lat: event.ml_results.top_result.lat,
                    lng: event.ml_results.top_result.lon
                  } : null)

    if (!coords) return

    setAdditionalDataLoading(true)
    try {
      // Fetch delivery navigation (from nearest warehouse)
      const deliveryData = await getDeliveryNavigation({ lat: coords.lat, lon: coords.lng })
      setDeliveryNavigation(deliveryData)

      // Fetch safety assessment
      const safetyData = await getSafetyAssessment(coords.lat, coords.lng)
      setSafetyAssessment(safetyData)
    } catch (err) {
      console.error('Failed to fetch additional data:', err)
      // Don't show error to user
    } finally {
      setAdditionalDataLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A7C59] mx-auto mb-4"></div>
          <p className="text-[#2C2C2C] text-lg">Analyzing your address...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="bg-white border border-[#E8E0D1] rounded-xl shadow-sm max-w-md p-8">
          <div className="text-center">
            <div className="text-[#E76F51] text-4xl mb-4">⚠️</div>
            <h3 className="text-lg font-semibold text-[#2C2C2C] mb-2">Processing Failed</h3>
            <p className="text-[#6B6B6B] mb-4">{error}</p>
            <button onClick={() => navigate('/')} className="bg-[#F49C8E] hover:bg-[#E37A7A] text-white px-6 py-3 rounded-xl font-medium shadow-md transition-all">
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!event) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="bg-white border border-[#E8E0D1] rounded-xl shadow-sm max-w-md p-8">
          <div className="text-center">
            <div className="text-4xl mb-4">🏠</div>
            <h3 className="text-lg font-semibold text-[#2C2C2C] mb-2">No Results Available</h3>
            <p className="text-[#6B6B6B] mb-4">Please enter an address to analyze.</p>
            <button onClick={() => navigate('/')} className="bg-[#A5E8D3] hover:bg-[#2F4D35] text-[#2C2C2C] px-6 py-3 rounded-xl font-medium shadow-md transition-all">
              Go to Home
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Extract data for components
  const fused = typeof event.confidence === 'number' ? event.confidence : (typeof event.fused_confidence === 'number' ? event.fused_confidence : 0)
  const integrity = event.integrity?.score ?? 0

  const health = event.health || 'UNCERTAIN'

  return (
    <div className="min-h-screen bg-[#FAF7F0]">
      {/* Header */}
      <div className="bg-white border-b border-[#E8E0D1]">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 text-[#4A7C59] hover:text-[#3A5A45] transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-medium">Back to Home</span>
            </button>
            <h1 className="text-2xl font-semibold text-[#2C2C2C]">Address Intelligence Results</h1>
            <div className="w-24"></div> {/* Spacer for centering */}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Address Header & Health */}
        <AddressHeader
          health={health}
          processingTime={processingTime}
        keyMetrics={{
            confidence: fused,
            integrity: integrity / 100, // Convert to 0-1 scale
          }}
        />

        {/* Comprehensive Results Card */}
        <ComprehensiveResultsCard
          event={event}
          processingTime={processingTime}
        />

        {/* Delivery & Safety Intelligence */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="text-2xl font-semibold text-[#2C2C2C] mb-6">Delivery & Safety Intelligence</h2>
          <div className="grid gap-6 lg:grid-cols-2">
            <DeliveryNavigationCard
              data={deliveryNavigation}
            />
            <SafetyAssessmentCard
              data={safetyAssessment}
            />
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex justify-center pt-8 border-t border-[#E8E0D1]"
        >
          <button
            onClick={() => navigate('/')}
            className="bg-[#4A7C59] hover:bg-[#3A5A45] text-white font-medium py-3 px-8 rounded-xl transition-all duration-200 flex items-center space-x-2 shadow-sm hover:shadow-md"
          >
            <span>Analyze Another Address</span>
          </button>
        </motion.div>
      </div>
    </div>
  )
}
