import { motion } from 'framer-motion'
import { MapPin, CheckCircle } from 'lucide-react'

interface CoreAddressCardProps {
  rawAddress: string
  cleanedAddress: string
  components: Record<string, any>
}

export function CoreAddressCard({ rawAddress, cleanedAddress, components }: CoreAddressCardProps) {
  const primaryComponents = ['city', 'pincode', 'country']
  const otherComponents = Object.entries(components).filter(([key]) => !primaryComponents.includes(key.toLowerCase()))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.1 }}
      className="mb-8"
    >
      <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
        <div className="flex items-start space-x-4 mb-6">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              <MapPin className="w-6 h-6 text-[#4A7C59]" />
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-[#2C2C2C] mb-4">Address Analysis</h2>

            {/* Raw Address */}
            <div className="mb-4">
              <h3 className="text-sm font-medium text-[#6B6B6B] mb-2">Raw Input</h3>
              <p className="text-[#6B6B6B] line-through italic">{rawAddress}</p>
            </div>

            {/* Cleaned Address */}
            <div className="mb-4">
              <h3 className="text-sm font-medium text-[#2C2C2C] mb-2">Standardized Address</h3>
              <p className="text-lg text-[#2C2C2C] font-medium leading-relaxed">{cleanedAddress}</p>
            </div>

            {/* Primary Components */}
            {Object.keys(components).length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-[#2C2C2C] mb-3">Key Components</h3>
                <div className="flex flex-wrap gap-2">
                  {primaryComponents.map(key => {
                    const value = components[key] || components[key.toLowerCase()]
                    if (!value) return null
                    return (
                      <span
                        key={key}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#4A7C59]/10 text-[#4A7C59] border border-[#4A7C59]/20"
                      >
                        <span className="font-semibold mr-1">{key}:</span> {String(value)}
                      </span>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Other Components */}
            {otherComponents.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-[#2C2C2C] mb-3">Additional Details</h3>
                <div className="flex flex-wrap gap-2">
                  {otherComponents.map(([key, value]) => (
                    <span
                      key={key}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#E8E0D1] text-[#2C2C2C]"
                    >
                      <span className="font-semibold mr-1">{key}:</span> {String(value)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}