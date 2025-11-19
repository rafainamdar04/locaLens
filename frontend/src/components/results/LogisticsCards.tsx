import { motion } from 'framer-motion'
import { Truck, Route, Shield, Clock, MapPin, AlertTriangle, CheckCircle, Car, ParkingCircle, Target, TrendingUp, Navigation } from 'lucide-react'

interface Issue {
  tag?: string
  severity?: string
  explanation?: string
}

interface DeliverabilityCardProps {
  data: any
  routingData?: any
}

export function DeliverabilityCard({ data, routingData }: DeliverabilityCardProps) {
  // If no deliverability data or error, show not computed
  const hasDeliverability = data && !data.error && (data.score !== undefined || data.deliverability_score !== undefined)
  if (!hasDeliverability) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm"
      >
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              <Truck className="w-6 h-6 text-[#4A7C59]" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-[#2C2C2C]">Deliverability</h3>
            <p className="text-[#6B6B6B]">
              {data?.error ? `Deliverability analysis failed: ${data.error}` : 'Deliverability analysis not computed'}
            </p>
          </div>
        </div>
      </motion.div>
    )
  }

  const score = typeof data.score === 'number' ? data.score : (typeof data.deliverability_score === 'number' ? (data.deliverability_score / 100.0) : 0)
  const breakdown = data?.breakdown || {}
  const issues: Issue[] = data?.issues || []
  const explanation = data?.explanation || (Array.isArray(data?.reasons) ? data.reasons[0] : null)
  // Normalize breakdown values with safe fallbacks
  const integrityVal = breakdown?.components?.integrity_0_100 !== undefined
    ? (breakdown.components.integrity_0_100 / 100.0)
    : (breakdown.integrity !== undefined ? breakdown.integrity : (data.integrity_contribution !== undefined ? data.integrity_contribution : 0))
  const hereConfVal = (breakdown?.components?.here_conf_0_1 !== undefined)
    ? breakdown.components.here_conf_0_1
    : (data.here_confidence !== undefined ? data.here_confidence : 0)
  const mlSimVal = (breakdown?.components?.ml_sim_0_1 !== undefined)
    ? breakdown.components.ml_sim_0_1
    : (data.ml_similarity !== undefined ? data.ml_similarity : 0)

  // Convert minutes to hours and minutes
  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = Math.round(minutes % 60)
    if (hours > 0) {
      return `${hours}h ${mins}m`
    }
    return `${mins}m`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm"
    >
      <div className="flex items-start space-x-4 mb-6">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <Truck className="w-6 h-6 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-[#2C2C2C]">Deliverability</h3>
            <div className="text-right">
              <div className={`text-3xl font-bold ${score < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{Math.round(score * 100)}%</div>
                <div className="text-sm text-[#6B6B6B]">Overall Score</div>
                {explanation && <div className="text-xs text-[#6B6B6B] mt-1">{explanation}</div>}
            </div>
          </div>

          {/* Score Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className={`text-lg font-semibold ${integrityVal < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{Math.round(integrityVal * 100)}%</div>
              <div className="text-sm text-[#6B6B6B]">Integrity</div>
            </div>
            <div className="text-center">
              <div className={`text-lg font-semibold ${hereConfVal < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{Math.round(hereConfVal * 100)}%</div>
              <div className="text-sm text-[#6B6B6B]">HERE Confidence</div>
            </div>
            <div className="text-center">
              <div className={`text-lg font-semibold ${mlSimVal < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{Math.round(mlSimVal * 100)}%</div>
              <div className="text-sm text-[#6B6B6B]">ML Similarity</div>
            </div>
          </div>

          {/* Logistics Details */}
          <div className="space-y-4">
            {routingData && (
              <>
                <div className="flex items-center justify-between py-2 border-b border-[#E8E0D1]">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-[#6B6B6B]" />
                    <span className="text-[#6B6B6B]">Delivery Time</span>
                  </div>
                  <span className="font-medium text-[#2C2C2C]">{formatTime(routingData.time || 0)}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-[#E8E0D1]">
                  <div className="flex items-center space-x-2">
                    <Route className="w-4 h-4 text-[#6B6B6B]" />
                    <span className="text-[#6B6B6B]">Route Distance</span>
                  </div>
                  <span className="font-medium text-[#2C2C2C]">{routingData.distance?.toFixed(1) || 0} km</span>
                </div>
              </>
            )}

            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-2">
                <ParkingCircle className="w-4 h-4 text-[#6B6B6B]" />
                <span className="text-[#6B6B6B]">Parking Available</span>
              </div>
              <span className="font-medium text-[#E76F51]">None found</span>
            </div>
          </div>

          {/* Issues */}
          {issues.length > 0 && (
            <div className="mt-6 p-4 bg-[#FAF7F0] rounded-lg border border-[#E8E0D1]">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="w-5 h-5 text-[#E76F51] mt-0.5" />
                <div>
                  <h4 className="text-sm font-medium text-[#2C2C2C] mb-2">Issues Detected</h4>
                  <ul className="space-y-1">
                    {issues.map((issue: Issue, index: number) => (
                      <li key={index} className="text-sm text-[#6B6B6B]">
                        • {issue.explanation || issue.tag || JSON.stringify(issue)}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

interface NavigationCardProps {
  data: any
}

export function NavigationCard({ data }: NavigationCardProps) {
  const score = data?.score || null
  const routeComplexity = data?.route_complexity || 'simple'
  const accessType = data?.access_type || 'place-based'
  const roadQuality = data?.road_quality || 'good'
  const trafficScore = data?.traffic_score || 0
  const issues = data?.issues || []

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm"
    >
      <div className="flex items-start space-x-4 mb-6">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <Route className="w-6 h-6 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-[#2C2C2C]">Navigation</h3>
            <div className="text-right">
              {score !== null ? (
                <>
                  <div className="text-3xl font-bold text-[#4A7C59]">{Math.round(score * 100)}%</div>
                  <div className="text-sm text-[#6B6B6B]">Navigation Score</div>
                </>
              ) : (
                <div className="text-sm text-[#6B6B6B]">Not computed</div>
              )}
            </div>
          </div>

          {score === null ? (
            <div className="p-4 bg-[#FAF7F0] rounded-lg border border-[#E8E0D1]">
              <p className="text-[#6B6B6B] text-sm">
                Navigation analysis requires routing data to be populated. This includes route complexity,
                access patterns, and traffic conditions.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-[#E8E0D1]">
                <div className="flex items-center space-x-2">
                  <Route className="w-4 h-4 text-[#6B6B6B]" />
                  <span className="text-[#6B6B6B]">Route Complexity</span>
                </div>
                <span className="font-medium text-[#2C2C2C] capitalize">{routeComplexity}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-[#E8E0D1]">
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-[#6B6B6B]" />
                  <span className="text-[#6B6B6B]">Access Type</span>
                </div>
                <span className="font-medium text-[#2C2C2C] capitalize">{accessType}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-[#E8E0D1]">
                <div className="flex items-center space-x-2">
                  <Car className="w-4 h-4 text-[#6B6B6B]" />
                  <span className="text-[#6B6B6B]">Road Quality</span>
                </div>
                <span className="font-medium text-[#2C2C2C] capitalize">{roadQuality}</span>
              </div>

              <div className="flex items-center justify-between py-2">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-[#6B6B6B]" />
                  <span className="text-[#6B6B6B]">Traffic Conditions</span>
                </div>
                <span className="font-medium text-[#2C2C2C]">{Math.round(trafficScore * 100)}%</span>
              </div>
            </div>
          )}

          {/* Issues */}
          {issues.length === 0 && (
            <div className="mt-6 p-4 bg-[#4A7C59]/5 rounded-lg border border-[#4A7C59]/20">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-[#4A7C59]" />
                <span className="text-sm font-medium text-[#4A7C59]">No navigation issues detected</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

interface SafetyCardProps {
  data: any
  placesData?: any
}

export function SafetyCard({ data, placesData }: SafetyCardProps) {
  // If no safety data or error, show not computed
  const hasSafety = data && !data.error && (data.score !== undefined || data.safety_score !== undefined)
  if (!hasSafety) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm"
      >
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-[#D4B08A]/10 rounded-full flex items-center justify-center">
              <Shield className="w-6 h-6 text-[#D4B08A]" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-[#2C2C2C]">Safety</h3>
            <p className="text-[#6B6B6B]">
              {data?.error ? `Safety analysis failed: ${data.error}` : 'Safety analysis not computed'}
            </p>
          </div>
        </div>
      </motion.div>
    )
  }

  const score = typeof data.score === 'number' ? data.score : (typeof data.safety_score === 'number' ? data.safety_score : null)
  const explanation = data?.explanation || null
  const locationType = data?.location_type || 'residential building'
  const safetyFeatures = placesData?.safety_features || []
  const emergencyAccess = data?.emergency_access || 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.4 }}
      className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm"
    >
      <div className="flex items-start space-x-4 mb-6">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <Shield className="w-6 h-6 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-[#2C2C2C]">Safety</h3>
            <div className="text-right">
              {score !== null ? (
                <>
                  <div className={`text-3xl font-bold ${score < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{Math.round(score * 100)}%</div>
                  <div className="text-sm text-[#6B6B6B]">Safety Score</div>
                  {explanation && <div className="text-xs text-[#6B6B6B] mt-1">{explanation}</div>}
                </>
              ) : (
                <div className="text-sm text-[#6B6B6B]">Not computed</div>
              )}
            </div>
          </div>

          {score === null ? (
            <div className="p-4 bg-[#FAF7F0] rounded-lg border border-[#E8E0D1]">
              <p className="text-[#6B6B6B] text-sm">
                Safety analysis requires places data to be populated. This includes nearby police stations,
                hospitals, and emergency services.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-[#E8E0D1]">
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-[#6B6B6B]" />
                  <span className="text-[#6B6B6B]">Location Type</span>
                </div>
                <span className="font-medium text-[#2C2C2C] capitalize">{locationType}</span>
              </div>

              {safetyFeatures.length > 0 && (
                <div className="py-2 border-b border-[#E8E0D1]">
                  <div className="text-[#6B6B6B] mb-2">Nearby Safety Features</div>
                  <div className="flex flex-wrap gap-2">
                    {safetyFeatures.map((feature: string, index: number) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-[#4A7C59]/10 text-[#4A7C59]"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between py-2">
                <div className="flex items-center space-x-2">
                  <Shield className="w-4 h-4 text-[#6B6B6B]" />
                  <span className="text-[#6B6B6B]">Emergency Access</span>
                </div>
                <span className={`font-medium ${emergencyAccess < 0.5 ? 'text-[#E76F51]' : 'text-[#2C2C2C]'}`}>{Math.round(emergencyAccess * 100)}%</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

interface DeliveryNavigationCardProps {
  data: any
}

export function DeliveryNavigationCard({ data }: DeliveryNavigationCardProps) {
  const hasData = data && !data.error && data.routes && data.scores
  if (!hasData) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm"
      >
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-[#4A7C59]/10 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Truck className="w-8 h-8 text-[#4A7C59]" />
          </div>
          <h3 className="text-xl font-medium text-[#2C2C2C] mb-2">Delivery & Navigation</h3>
          <p className="text-[#6B6B6B]">
            {data?.error ? `Analysis failed: ${data.error}` : 'Delivery & navigation analysis not available'}
          </p>
        </div>
      </motion.div>
    )
  }

  const routes = data.routes || []
  const scores = data.scores || {}
  const recommendation = data.recommendation || ''
  const warehouse = data.warehouse || {}

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="bg-white border border-[#E8E0D1] rounded-xl shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className="bg-[#4A7C59] px-6 py-5 text-white">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
            <Truck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-medium text-white">Delivery & Navigation</h3>
            <p className="text-[#E8E0D1] text-sm">Route planning and logistics</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Warehouse Information */}
        {warehouse.name && (
          <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-[#4A7C59]" />
                </div>
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-[#2C2C2C] text-lg">{warehouse.name}</h4>
                <p className="text-[#6B6B6B] text-sm mb-3">{warehouse.address}</p>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div className="text-center">
                    <div className="font-medium text-[#2C2C2C]">{warehouse.distance_km} km</div>
                    <div className="text-[#6B6B6B]">Distance</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium text-[#2C2C2C]">{warehouse.capacity}</div>
                    <div className="text-[#6B6B6B]">Capacity</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium text-[#2C2C2C] capitalize">{data.service_type}</div>
                    <div className="text-[#6B6B6B]">Service</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Route Summary */}
        {routes.length > 0 && (
          <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
            <h4 className="font-medium text-[#2C2C2C] mb-3 flex items-center">
              <Route className="w-4 h-4 mr-2 text-[#4A7C59]" />
              Route Summary
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-medium text-[#2C2C2C]">{routes[0].distance_km} km</div>
                <div className="text-sm text-[#6B6B6B]">Distance</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-medium text-[#2C2C2C]">{routes[0].duration_min} min</div>
                <div className="text-sm text-[#6B6B6B]">ETA</div>
              </div>
            </div>
            {routes[0].traffic_delay_min > 0 && (
              <div className="mt-3 p-2 bg-[#D4B08A]/10 rounded-lg border border-[#D4B08A]/20">
                <div className="text-sm text-[#6B6B6B] flex items-center">
                  <Clock className="w-4 h-4 mr-1 text-[#D4B08A]" />
                  +{routes[0].traffic_delay_min} min traffic delay
                </div>
              </div>
            )}
          </div>
        )}

        {/* Performance Scores */}
        <div className="space-y-4">
          <h4 className="font-medium text-[#2C2C2C] flex items-center">
            <Target className="w-4 h-4 mr-2 text-[#4A7C59]" />
            Performance Metrics
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-2">
                <div className="w-8 h-8 bg-[#4A7C59]/10 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-xl font-medium text-[#2C2C2C]">{scores.delivery_efficiency?.score || 0}%</div>
              <div className="text-sm text-[#6B6B6B]">Efficiency</div>
              <div className="text-xs text-[#6B6B6B] mt-1">{scores.delivery_efficiency?.explanation || ''}</div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-2">
                <div className="w-8 h-8 bg-[#4A7C59]/10 rounded-lg flex items-center justify-center">
                  <Navigation className="w-4 h-4 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-xl font-medium text-[#2C2C2C]">{scores.navigation_ease?.score || 0}%</div>
              <div className="text-sm text-[#6B6B6B]">Navigation</div>
              <div className="text-xs text-[#6B6B6B] mt-1">{scores.navigation_ease?.explanation || ''}</div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-2">
                <div className="w-8 h-8 bg-[#4A7C59]/10 rounded-lg flex items-center justify-center">
                  <Shield className="w-4 h-4 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-xl font-medium text-[#2C2C2C]">{scores.traffic_safety?.score || 0}%</div>
              <div className="text-sm text-[#6B6B6B]">Traffic Safety</div>
              <div className="text-xs text-[#6B6B6B] mt-1">{scores.traffic_safety?.explanation || ''}</div>
            </div>
          </div>
        </div>

        {/* Route Instructions */}
        {routes.length > 0 && routes[0].instructions && routes[0].instructions.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-[#2C2C2C] flex items-center">
              <Route className="w-4 h-4 mr-2 text-[#4A7C59]" />
              Route Instructions
            </h4>
            <div className="bg-[#FAF7F0] rounded-xl border border-[#E8E0D1] p-4 max-h-40 overflow-y-auto">
              <div className="space-y-2">
                {routes[0].instructions.slice(0, 5).map((instruction: string, index: number) => (
                  <div key={index} className="text-sm text-[#6B6B6B] flex items-start space-x-2">
                    <span className="text-[#4A7C59] font-medium min-w-[20px] bg-[#4A7C59]/10 rounded px-1">{index + 1}.</span>
                    <span>{instruction}</span>
                  </div>
                ))}
                {routes[0].instructions.length > 5 && (
                  <div className="text-sm text-slate-500 italic">
                    ... and {routes[0].instructions.length - 5} more steps
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Recommendation */}
        {recommendation && (
          <div className="p-4 bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl text-white">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center border border-white/20 flex-shrink-0">
                <CheckCircle className="w-4 h-4 text-white" />
              </div>
              <div>
                <h4 className="font-bold text-white mb-1">Recommendation</h4>
                <div className="text-slate-200 text-sm">{recommendation}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

interface SafetyAssessmentCardProps {
  data: any
}

export function SafetyAssessmentCard({ data }: SafetyAssessmentCardProps) {
  const hasData = data && !data.error && data.scores
  if (!hasData) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="bg-white border border-[#E8E0D1] rounded-xl shadow-sm p-8"
      >
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-[#4A7C59]/10 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-[#4A7C59]" />
          </div>
          <h3 className="text-xl font-medium text-[#2C2C2C] mb-2">Safety Assessment</h3>
          <p className="text-[#6B6B6B]">
            {data?.error ? `Assessment failed: ${data.error}` : 'Safety assessment not available'}
          </p>
        </div>
      </motion.div>
    )
  }

  const scores = data.scores || {}
  const insights = data.detailed_insights || {}

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="bg-white border border-[#E8E0D1] rounded-xl shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className="bg-[#4A7C59] px-6 py-5 text-white">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-medium text-white">Safety Assessment</h3>
            <p className="text-[#E8E0D1] text-sm">Residential safety analysis</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Overall Score */}
        <div className="p-6 bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-2xl border border-emerald-200/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-emerald-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <div className="text-3xl font-bold text-emerald-900">{scores.overall_safety?.score || 0}%</div>
                <div className="text-sm font-medium text-emerald-700">Overall Safety Score</div>
              </div>
            </div>
            <div className="text-right max-w-xs">
              <div className="text-sm text-emerald-800">{scores.overall_safety?.explanation || ''}</div>
            </div>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="space-y-4">
          <h4 className="font-bold text-slate-900 flex items-center">
            <Target className="w-4 h-4 mr-2" />
            Safety Metrics
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-2">
                <div className="w-8 h-8 bg-[#4A7C59]/10 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-xl font-medium text-[#2C2C2C]">{scores.emergency_response?.score || 0}%</div>
              <div className="text-sm text-[#6B6B6B]">Emergency Response</div>
              <div className="text-xs text-[#6B6B6B] mt-1">{scores.emergency_response?.explanation || ''}</div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-2">
                <div className="w-8 h-8 bg-[#4A7C59]/10 rounded-lg flex items-center justify-center">
                  <MapPin className="w-4 h-4 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-xl font-medium text-[#2C2C2C]">{scores.accessibility?.score || 0}%</div>
              <div className="text-sm text-[#6B6B6B]">Accessibility</div>
              <div className="text-xs text-[#6B6B6B] mt-1">{scores.accessibility?.explanation || ''}</div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-2">
                <div className="w-8 h-8 bg-[#4A7C59]/10 rounded-lg flex items-center justify-center">
                  <Car className="w-4 h-4 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-xl font-medium text-[#2C2C2C]">{scores.traffic_impact?.score || 0}%</div>
              <div className="text-sm text-[#6B6B6B]">Traffic Impact</div>
              <div className="text-xs text-[#6B6B6B] mt-1">{scores.traffic_impact?.explanation || ''}</div>
            </div>
          </div>
        </div>

        {/* Detailed Insights */}
        <div className="space-y-6">
          {/* Emergency Services */}
          <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
            <h4 className="font-medium text-[#2C2C2C] mb-3 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2 text-[#D4B08A]" />
              Emergency Services (within 3km)
            </h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-2xl font-medium text-[#2C2C2C]">{insights.emergency_services?.hospitals || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Hospitals</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-2xl font-medium text-[#2C2C2C]">{insights.emergency_services?.police_stations || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Police Stations</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-2xl font-medium text-[#2C2C2C]">{insights.emergency_services?.fire_stations || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Fire Stations</div>
              </div>
            </div>
          </div>

          {/* Daily Amenities */}
          <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
            <h4 className="font-medium text-[#2C2C2C] mb-3 flex items-center">
              <CheckCircle className="w-4 h-4 mr-2 text-[#4A7C59]" />
              Daily Amenities (within 1.5km)
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-xl font-medium text-[#2C2C2C]">{insights.accessibility?.schools || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Schools</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-xl font-medium text-[#2C2C2C]">{insights.accessibility?.parks || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Parks</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-xl font-medium text-[#2C2C2C]">{insights.accessibility?.shopping || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Shopping</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border border-[#E8E0D1]">
                <div className="text-xl font-medium text-[#2C2C2C]">{insights.accessibility?.public_transport || 0}</div>
                <div className="text-sm text-[#6B6B6B]">Transport</div>
              </div>
            </div>
          </div>

          {/* Traffic Concerns */}
          <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
            <h4 className="font-medium text-[#2C2C2C] mb-2 flex items-center">
              <Car className="w-4 h-4 mr-2 text-[#D4B08A]" />
              Traffic Concerns (within 2km)
            </h4>
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-medium text-[#2C2C2C]">{insights.traffic?.incident_count || 0}</div>
              <div className="text-[#6B6B6B]">traffic incidents detected</div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="p-4 bg-[#4A7C59] rounded-xl text-white">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-4 h-4 text-white" />
            </div>
            <div>
              <h4 className="font-medium text-white mb-1">Safety Recommendation</h4>
              <div className="text-[#E8E0D1] text-sm">
                {scores.overall_safety?.score >= 80 ? 'Excellent residential choice with strong safety features and comprehensive emergency services.' :
                 scores.overall_safety?.score >= 60 ? 'Good residential option with solid safety considerations and adequate amenities.' :
                 'Consider additional security measures or explore alternative locations with better safety infrastructure.'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}