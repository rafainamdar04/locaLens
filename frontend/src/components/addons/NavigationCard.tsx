import { Truck, Route, Clock, AlertTriangle, CheckCircle, MapPin } from 'lucide-react'
import Card from '../Card'

interface NavigationCardProps {
  data: any // Using any for flexibility with backend data structure changes
}

export default function NavigationCard({ data }: NavigationCardProps) {
  // Handle both old and new data structures
  const score = data?.navigation_score ?? 0
  const breakdown = data?.breakdown || {}
  const issues = data?.issues || []
  const suggestions = data?.suggestions || []
  const route_details = data?.route_details || {}

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

  return (
    <Card>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getScoreColor(score)}`}>
            <Route className="w-6 h-6" />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">Navigation Score</h3>
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

          {/* Route Details */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {route_details.route_length_km > 0 ? `${route_details.route_length_km.toFixed(1)} km` : 'Distance N/A'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {route_details.estimated_time_min > 0 ? `${route_details.estimated_time_min} min` : 'Time N/A'}
              </span>
            </div>
          </div>

          {/* Route Complexity Indicators */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            {route_details.complex_turns_count > 0 && (
              <div className="flex items-center space-x-1 text-xs text-orange-600">
                <AlertTriangle className="w-3 h-3" />
                <span>{route_details.complex_turns_count} complex turns</span>
              </div>
            )}
            {route_details.roundabout_count > 0 && (
              <div className="flex items-center space-x-1 text-xs text-blue-600">
                <Route className="w-3 h-3" />
                <span>{route_details.roundabout_count} roundabouts</span>
              </div>
            )}
            {route_details.traffic_light_count > 0 && (
              <div className="flex items-center space-x-1 text-xs text-yellow-600">
                <Truck className="w-3 h-3" />
                <span>{route_details.traffic_light_count} traffic lights</span>
              </div>
            )}
          </div>

          {/* Issues */}
          {issues.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Navigation Challenges</h4>
              <div className="space-y-2">
                {issues.slice(0, 2).map((issue: any, index: number) => (
                  <div key={index} className={`p-2 rounded-md ${getSeverityColor(issue.severity || 'info')}`}>
                    <p className="text-xs">{issue.explanation || issue}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Navigation Tips</h4>
              <div className="space-y-1">
                {suggestions.slice(0, 2).map((suggestion: any, index: number) => (
                  <div key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-gray-600">{suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="text-xs text-gray-500 leading-relaxed">
            Navigation score assesses route complexity, entry accessibility, and driving challenges for delivery operations.
          </p>
        </div>
      </div>
    </Card>
  )
}