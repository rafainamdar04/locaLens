import { motion } from 'framer-motion'
import { CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react'

interface AddressHeaderProps {
  health: string
  processingTime: number
  keyMetrics: {
    confidence: number
    integrity: number
  }
}

export function AddressHeader({ health, processingTime, keyMetrics }: AddressHeaderProps) {
  const getHealthConfig = (health: string) => {
    switch (health) {
      case 'OK':
        return {
          icon: CheckCircle,
          color: '#4A7C59',
          bgColor: '#4A7C59',
          text: 'Healthy',
          description: 'This address appears reliable and ready for use.'
        }
      case 'UNCERTAIN':
        return {
          icon: AlertTriangle,
          color: '#6B6B6B',
          bgColor: '#6B6B6B',
          text: 'Needs Review',
          description: 'Some aspects need verification before critical use.'
        }
      default:
        return {
          icon: XCircle,
          color: '#E76F51',
          bgColor: '#E76F51',
          text: 'Requires Attention',
          description: 'Significant issues detected that require immediate attention.'
        }
    }
  }

  const healthConfig = getHealthConfig(health)
  const Icon = healthConfig.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mb-8"
    >
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Health Status */}
        <div className="lg:col-span-1">
          <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm text-center">
            <div className="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4 bg-green-700">
              <Icon className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-[#2C2C2C] mb-2">Address Health</h3>
            <p className="text-lg font-medium mb-2 text-green-700">
              {healthConfig.text}
            </p>
            <p className="text-sm text-[#6B6B6B]">{healthConfig.description}</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="lg:col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-[#6B6B6B]">Confidence Score</h4>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${keyMetrics.confidence < 0.5 ? 'text-red-500' : 'text-green-700'}`}>{Math.round(keyMetrics.confidence * 100)}%</div>
                </div>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${keyMetrics.confidence < 0.5 ? 'bg-red-500' : 'bg-green-700'}`}
                  style={{ width: `${Math.min(100, Math.max(0, keyMetrics.confidence * 100))}%` }}
                />
              </div>
            </div>

            <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-[#6B6B6B]">Completeness</h4>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${keyMetrics.integrity < 0.5 ? 'text-red-500' : 'text-green-700'}`}>{Math.round(keyMetrics.integrity * 100)}%</div>
                </div>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${keyMetrics.integrity < 0.5 ? 'bg-red-500' : 'bg-green-700'}`}
                  style={{ width: `${Math.min(100, Math.max(0, keyMetrics.integrity * 100))}%` }}
                />
              </div>
            </div>
          </div>

          {/* Processing Time */}
          <div className="mt-4 flex items-center justify-center text-sm text-[#6B6B6B]">
            <Clock className="w-4 h-4 mr-2" />
            Processed in {Math.round(processingTime)} ms
          </div>
        </div>
      </div>
    </motion.div>
  )
}