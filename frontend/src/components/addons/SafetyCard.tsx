import { Shield, AlertTriangle, CheckCircle, Moon, Sun, Camera, Building, Route, Clock, MapPin, Hospital } from 'lucide-react'
import Card from '../Card'

interface SafetyCardProps {
  data: any // Using any for flexibility with backend data structure changes
}

export default function SafetyCard({ data }: SafetyCardProps) {
  // Handle both old and new data structures (prefer `score` normalized 0-1)
  const score = data?.score ?? data?.safety_score ?? 0
  const breakdown = data?.breakdown || {}
  const issues = data?.issues || []
  const recommendations = data?.recommendations || []
  const safety_factors = data?.safety_factors || {}
  const explanation = data?.explanation || null

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

  const getCrimeRateColor = (rate: string) => {
    switch (rate) {
      case 'high': return 'text-red-600'
      case 'medium': return 'text-yellow-600'
      case 'low': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <Card>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getScoreColor(score)}`}>
            <Shield className="w-6 h-6" />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">Safety Score</h3>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(score)}`}>
              {Math.round(score * 100)}%
            </div>
          </div>

          <div className="mb-4">
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  score >= 0.8 ? 'bg-green-500' : score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${score * 100}%` }}
              />
            </div>
            {explanation && <div className="text-xs text-gray-600 mt-2">{explanation}</div>}
          </div>

          {/* Enhanced Safety Breakdown */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-sm font-bold text-gray-900">
                {breakdown.traffic_safety_penalty?.toFixed(1) || '0.0'}
              </div>
              <div className="text-xs text-gray-600">Traffic Penalty</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-sm font-bold text-gray-900">
                {breakdown.route_safety_penalty?.toFixed(1) || '0.0'}
              </div>
              <div className="text-xs text-gray-600">Route Penalty</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-sm font-bold text-green-600">
                +{breakdown.places_safety_bonuses?.toFixed(1) || '0.0'}
              </div>
              <div className="text-xs text-gray-600">Safety Bonus</div>
            </div>
          </div>

          {/* Route Conditions */}
          {safety_factors.route_conditions && safety_factors.route_conditions.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <Route className="w-4 h-4 text-gray-600" />
                <h4 className="text-sm font-medium text-gray-900">Route Conditions</h4>
              </div>
              <div className="flex flex-wrap gap-1">
                {safety_factors.route_conditions.map((condition: string, index: number) => (
                  <span key={index} className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                    {condition.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
              {safety_factors.route_details && (
                <div className="mt-2 text-xs text-gray-600">
                  {safety_factors.route_details.length_km && (
                    <span>{safety_factors.route_details.length_km.toFixed(1)}km • </span>
                  )}
                  {safety_factors.route_details.estimated_time_min && (
                    <span>{Math.round(safety_factors.route_details.estimated_time_min)}min</span>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Nearby Safety Features */}
          {safety_factors.security_features && (
            <div className="mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <MapPin className="w-4 h-4 text-gray-600" />
                <h4 className="text-sm font-medium text-gray-900">Nearby Safety Features</h4>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {safety_factors.security_features.nearest_police_m && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <Building className="w-4 h-4" />
                    <span className="text-xs">Police: {safety_factors.security_features.nearest_police_m}m</span>
                  </div>
                )}
                {safety_factors.security_features.places_features?.includes('hospital_nearby') && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <Hospital className="w-4 h-4" />
                    <span className="text-xs">Hospital nearby</span>
                  </div>
                )}
                {safety_factors.security_features.places_features?.includes('security_cameras') && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <Camera className="w-4 h-4" />
                    <span className="text-xs">Security cameras</span>
                  </div>
                )}
                {safety_factors.security_features.cameras && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <Camera className="w-4 h-4" />
                    <span className="text-xs">Area cameras</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Location Safety Factors */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className={`text-lg font-bold ${getCrimeRateColor(safety_factors.crime_rate)}`}>
                {safety_factors.crime_rate || 'unknown'}
              </div>
              <div className="text-xs text-gray-600">Crime Rate</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className={`text-lg font-bold ${safety_factors.lighting_conditions === 'poor' ? 'text-red-600' : 'text-green-600'}`}>
                {safety_factors.lighting_conditions || 'unknown'}
              </div>
              <div className="text-xs text-gray-600">Lighting</div>
            </div>
          </div>

          {/* Time-based Risk */}
          {breakdown.time_modifier < 0 && (
            <div className="flex items-center space-x-2 mb-4 p-2 bg-yellow-50 rounded-lg">
              <Moon className="w-4 h-4 text-yellow-600" />
              <span className="text-xs text-yellow-800">Night/evening delivery increases safety risks</span>
            </div>
          )}

          {/* Traffic Concerns */}
          {safety_factors.traffic_concerns && safety_factors.traffic_concerns.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Traffic Safety Concerns</h4>
              <div className="flex flex-wrap gap-1">
                {safety_factors.traffic_concerns.slice(0, 3).map((concern: any, index: number) => (
                  <span key={index} className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                    {concern.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Issues */}
          {issues.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Safety Issues</h4>
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
          {recommendations.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Safety Recommendations</h4>
              <div className="space-y-1">
                {recommendations.slice(0, 2).map((rec: any, index: number) => (
                  <div key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-gray-600">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="text-xs text-gray-500 leading-relaxed">
            Safety score evaluates crime rates, lighting conditions, traffic risks, route conditions, and nearby security features for delivery operations.
          </p>
        </div>
      </div>
    </Card>
  )
}