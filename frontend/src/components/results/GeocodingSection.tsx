import { motion } from 'framer-motion'
import { Navigation, Cpu, AlertTriangle } from 'lucide-react'

interface HEREResultsCardProps {
  primaryResult: any
  confidence: number
  alternatives?: any[]
}

export function HEREResultsCard({ primaryResult, confidence, alternatives }: HEREResultsCardProps) {
  const address = primaryResult?.address || {}
  const position = primaryResult?.position || {}

  return (
    <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
      <div className="flex items-start space-x-4 mb-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <Navigation className="w-5 h-5 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[#2C2C2C] mb-2">HERE Maps Geocoding</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-[#6B6B6B] mb-1">Primary Location</h4>
              <p className="text-[#2C2C2C] font-medium">{primaryResult?.title || address?.label || 'N/A'}</p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-[#6B6B6B] mb-1">Coordinates</h4>
              <p className="text-[#2C2C2C] font-mono text-sm">
                {position.lat && position.lng ? `${position.lat.toFixed(5)}, ${position.lng.toFixed(5)}` : 'N/A'}
              </p>
            </div>
          </div>

          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-[#6B6B6B]">Confidence Score</h4>
              <span className="text-lg font-bold text-[#4A7C59]">{Math.round(confidence * 100)}%</span>
            </div>
            <div className="h-2 bg-[#E8E0D1] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#4A7C59] transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, confidence * 100))}%` }}
              />
            </div>
          </div>

          {alternatives && alternatives.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-[#6B6B6B] mb-2">Alternatives Found</h4>
              <p className="text-sm text-[#6B6B6B]">{alternatives.length} other location{alternatives.length !== 1 ? 's' : ''} available</p>
            </div>
          )}

          {(address.street || address.district || address.subdistrict || address.postalCode) && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-[#2C2C2C] mb-2">Address Breakdown</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {address.street && (
                  <div>
                    <span className="text-[#6B6B6B]">Street:</span> {address.street}
                  </div>
                )}
                {address.district && (
                  <div>
                    <span className="text-[#6B6B6B]">District:</span> {address.district}
                  </div>
                )}
                {address.subdistrict && (
                  <div>
                    <span className="text-[#6B6B6B]">Subdistrict:</span> {address.subdistrict}
                  </div>
                )}
                {address.postalCode && (
                  <div>
                    <span className="text-[#6B6B6B]">Postal Code:</span> {address.postalCode}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface MLResultsCardProps {
  topResult: any
}

export function MLResultsCard({ topResult }: MLResultsCardProps) {
  if (!topResult) {
    return (
      <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-[#D4B08A]/10 rounded-full flex items-center justify-center">
              <Cpu className="w-5 h-5 text-[#D4B08A]" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[#2C2C2C] mb-2">ML Geocoding</h3>
            <p className="text-[#6B6B6B]">No ML geocoding results available</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <Cpu className="w-5 h-5 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[#2C2C2C] mb-2">ML Geocoding</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-[#6B6B6B] mb-1">Location</h4>
              <p className="text-[#2C2C2C] font-medium">
                {topResult.city || topResult.district || 'N/A'}
                {topResult.state && `, ${topResult.state}`}
                {topResult.pincode && ` ${topResult.pincode}`}
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-[#6B6B6B] mb-1">Coordinates</h4>
              <p className="text-[#2C2C2C] font-mono text-sm">
                {topResult.lat && topResult.lon ? `${topResult.lat.toFixed(5)}, ${topResult.lon.toFixed(5)}` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

interface GeocodingComparisonProps {
  hereCoords: { lat: number; lng: number } | undefined
  mlCoords: { lat: number; lng: number } | undefined
  distanceKm: number | null
}

export function GeocodingComparison({ hereCoords, mlCoords, distanceKm }: GeocodingComparisonProps) {
  return (
    <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[#2C2C2C] mb-4">Geocoding Comparison</h3>

          {distanceKm !== null ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[#6B6B6B]">Coordinate Mismatch</span>
                <span className={`text-lg font-bold ${distanceKm > 3 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>
                  {distanceKm.toFixed(2)} km
                </span>
              </div>

              <div className="h-2 bg-[#E8E0D1] rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${distanceKm > 3 ? 'bg-[#E76F51]' : 'bg-[#4A7C59]'}`}
                  style={{ width: `${Math.min(100, Math.max(0, (distanceKm / 10) * 100))}%` }}
                />
              </div>

              <p className="text-sm text-[#6B6B6B]">
                {distanceKm > 3
                  ? 'Significant mismatch detected. Consider manual verification.'
                  : 'Good agreement between geocoding systems.'
                }
              </p>
            </div>
          ) : (
            <p className="text-[#6B6B6B]">Unable to calculate coordinate comparison</p>
          )}
        </div>
      </div>
    </div>
  )
}