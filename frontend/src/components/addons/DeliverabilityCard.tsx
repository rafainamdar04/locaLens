import { Package, Truck, MapPin, CheckCircle, AlertTriangle, Clock } from 'lucide-react'
import Card from '../Card'

interface DeliverabilityCardProps {
  data: any // Using any for flexibility with backend data structure changes
}

export default function DeliverabilityCard({ data }: DeliverabilityCardProps) {
  // Handle both old and new data structures
  const score = data?.score ?? data?.deliverability_score ?? 0
  const breakdown = data?.breakdown || {}
  const logistics_details = data?.logistics_details || {}
  const issues = data?.issues || data?.error ? [] : []
  const reasons = data?.reasons || []

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'warning': return 'text-yellow-600 bg-yellow-50'
      default: return 'text-blue-600 bg-blue-50'
    }
  }

  const hasBonuses = breakdown.bonuses && Object.values(breakdown.bonuses).some((b: any) => b > 0)
  const hasPenalties = breakdown.penalties && Object.values(breakdown.penalties).some((p: any) => p > 0)

  return (
    <Card>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getScoreColor(score)}`}>
            <Package className="w-6 h-6" />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">Deliverability Score</h3>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(score)}`}>
              {score}%
            </div>
          </div>

          <div className="mb-4">
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>

          {/* Logistics Details */}
          {logistics_details && Object.keys(logistics_details).length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Logistics Information</h4>
              <div className="grid grid-cols-2 gap-3">
                {logistics_details.estimated_delivery_time_min && (
                  <div className="text-center p-2 bg-blue-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">{logistics_details.estimated_delivery_time_min}</div>
                    <div className="text-xs text-gray-600">Est. Delivery Time (min)</div>
                  </div>
                )}
                {logistics_details.distance_km && (
                  <div className="text-center p-2 bg-blue-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">{logistics_details.distance_km.toFixed(1)}</div>
                    <div className="text-xs text-gray-600">Distance (km)</div>
                  </div>
                )}
                {logistics_details.parking_distance_m !== undefined && (
                  <div className="text-center p-2 bg-green-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">{logistics_details.parking_distance_m}</div>
                    <div className="text-xs text-gray-600">Parking Distance (m)</div>
                  </div>
                )}
                {logistics_details.has_loading_zone && (
                  <div className="text-center p-2 bg-green-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">✓</div>
                    <div className="text-xs text-gray-600">Loading Zone</div>
                  </div>
                )}
              </div>
              
              {/* Special conditions */}
              <div className="flex flex-wrap gap-2 mt-3">
                {logistics_details.requires_special_vehicle && (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                    Special Vehicle Required
                  </span>
                )}
                {logistics_details.construction_alert && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                    Construction Zone
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Bonuses and Penalties */}
          {(hasBonuses || hasPenalties) && (
            <div className="mb-4">
              <div className="grid grid-cols-2 gap-2 text-xs">
                {hasBonuses && (
                  <div className="text-green-600">
                    <div className="font-medium">Bonuses:</div>
                    {breakdown.bonuses.routable > 0 && <div>+{breakdown.bonuses.routable} Routable</div>}
                    {breakdown.bonuses.near_road > 0 && <div>+{breakdown.bonuses.near_road} Near Road</div>}
                    {breakdown.bonuses.area_type > 0 && <div>+{breakdown.bonuses.area_type} Area Type</div>}
                  </div>
                )}
                {hasPenalties && (
                  <div className="text-red-600">
                    <div className="font-medium">Penalties:</div>
                    {breakdown.penalties.mismatch_km > 0 && <div>-{breakdown.penalties.mismatch_km}km Mismatch</div>}
                    {breakdown.penalties.unroutable > 0 && <div>-{breakdown.penalties.unroutable} Unroutable</div>}
                    {breakdown.penalties.restricted_access > 0 && <div>-{breakdown.penalties.restricted_access} Restricted</div>}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Issues */}
          {issues.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Delivery Challenges</h4>
              <div className="space-y-2">
                {issues.slice(0, 2).map((issue: any, index: number) => (
                  <div key={index} className={`p-2 rounded-md ${getSeverityColor(issue.severity || 'info')}`}>
                    <p className="text-xs">{issue.explanation || issue}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {reasons.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Delivery Tips</h4>
              <div className="space-y-1">
                {reasons.slice(0, 2).map((reason: any, index: number) => (
                  <div key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-gray-600">{reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Components */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-lg font-bold text-gray-900">{Math.round(breakdown.components?.integrity_0_100 || 0)}</div>
              <div className="text-xs text-gray-600">Address Quality</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-lg font-bold text-gray-900">{Math.round((breakdown.components?.here_conf_0_1 || 0) * 100)}%</div>
              <div className="text-xs text-gray-600">Map Confidence</div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
