import { motion } from 'framer-motion'
import { Route, MapPin, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

interface RoutingCardProps {
  data: any
}

export function RoutingCard({ data }: RoutingCardProps) {
  // Accept multiple possible field names and units from backend
  const distanceKm =
    data?.distance_km ?? (data?.distance_m ? data.distance_m / 1000 : (typeof data?.distance === 'number' ? data.distance : undefined))

  const timeMinutes =
    data?.time_minutes ?? data?.duration_min ?? (typeof data?.time === 'number' ? data.time : undefined)

  const reachable = data?.reachable === undefined ? null : Boolean(data.reachable)

  const hasRouting = distanceKm !== undefined || timeMinutes !== undefined || reachable !== null

  const formatTime = (minutes?: number) => {
    if (minutes === undefined || minutes === null) return 'Unknown'
    const hrs = Math.floor(minutes / 60)
    const mins = Math.round(minutes % 60)
    return hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`
  }

  const formatDistance = (km?: number) => {
    if (km === undefined || km === null) return 'Unknown'
    if (km >= 1000) return `${(km / 1000).toFixed(1)} Mm`
    if (km >= 1) return `${km.toFixed(1)} km`
    return `${Math.round(km * 1000)} m`
  }

  const explanation = data?.explanation || data?.note || data?.reason || null

  if (!hasRouting) {
    return (
      <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              <Route className="w-5 h-5 text-[#4A7C59]" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[#2C2C2C] mb-4">Routing Data</h3>
            <p className="text-[#6B6B6B]">Routing data not available</p>
            {explanation ? <p className="text-sm text-[#6B6B6B] mt-2">{explanation}</p> : null}
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
            <Route className="w-5 h-5 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[#2C2C2C] mb-4">Routing Data</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-[#FAF7F0] rounded-lg">
              <div className="text-2xl font-bold text-[#4A7C59] mb-1">{formatDistance(distanceKm)}</div>
              <div className="text-sm text-[#6B6B6B]">Distance</div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-lg">
              <div className="text-2xl font-bold text-[#4A7C59] mb-1">{formatTime(timeMinutes)}</div>
              <div className="text-sm text-[#6B6B6B]">Travel Time</div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-lg">
              <div className={`text-2xl font-bold mb-1 ${reachable === null ? 'text-[#D4B08A]' : reachable ? 'text-[#4A7C59]' : 'text-[#E76F51]'}`}>
                {reachable === null ? 'Unknown' : reachable ? '✓' : '✗'}
              </div>
              <div className="text-sm text-[#6B6B6B]">Reachable</div>
            </div>
          </div>
          {explanation ? <p className="text-sm text-[#6B6B6B] mt-3">{explanation}</p> : null}
        </div>
      </div>
    </div>
  )
}

interface PlacesCardProps {
  data: any
}

export function PlacesCard({ data }: PlacesCardProps) {
  const totalPlaces = typeof data?.total_found === 'number' ? data.total_found : (data?.places?.length ?? 0)
  const categories = data?.categories || []
  const topPlaces = data?.places?.slice?.(0, 5) || []
  const explanation = data?.explanation || data?.note || null

  return (
    <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-[#D4B08A]/10 rounded-full flex items-center justify-center">
            <MapPin className="w-5 h-5 text-[#D4B08A]" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[#2C2C2C] mb-4">Places Data</h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[#6B6B6B]">Total Places Found</span>
              <span className="text-2xl font-bold text-[#2C2C2C]">{totalPlaces}</span>
            </div>

            {totalPlaces === 0 ? (
              <div className="p-4 bg-[#FAF7F0] rounded-lg border border-[#E8E0D1]">
                <p className="text-[#6B6B6B] text-sm">No places data available. Provide POI data to improve safety and delivery insights.</p>
                {explanation ? <p className="text-sm text-[#6B6B6B] mt-2">{explanation}</p> : null}
              </div>
            ) : (
              <div>
                <h4 className="text-sm font-medium text-[#2C2C2C] mb-2">Available Categories</h4>
                <div className="flex flex-wrap gap-2 mb-3">
                  {categories.map((category: string, index: number) => (
                    <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#4A7C59]/10 text-[#4A7C59]">
                      {category}
                    </span>
                  ))}
                </div>

                <h4 className="text-sm font-medium text-[#2C2C2C] mb-2">Top Nearby Places</h4>
                <div className="space-y-2">
                  {topPlaces.length === 0 ? (
                    <div className="text-sm text-[#6B6B6B]">No detailed places list available.</div>
                  ) : (
                    topPlaces.map((p: any, i: number) => (
                      <div key={i} className="flex items-center justify-between py-1">
                        <div className="text-sm text-[#2C2C2C]">{p.name || p.title || 'Unnamed'}</div>
                        <div className="text-sm text-[#6B6B6B]">{p.category || p.type || ''}</div>
                      </div>
                    ))
                  )}
                </div>
                {explanation ? <p className="text-sm text-[#6B6B6B] mt-3">{explanation}</p> : null}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

interface ValidationCardProps {
  data: any
}

export function ValidationCard({ data }: ValidationCardProps) {
  const geospatialChecks = data?.geospatial_checks || {}
  const anomalyDetection = data?.anomaly_detection || {}
  const poiAnalysis = data?.poi_analysis || {}
  const reverseGeocoding = data?.reverse_geocoding || {}

  const getStatusIcon = (status: boolean | undefined) => {
    if (status === true) return <CheckCircle className="w-4 h-4 text-[#4A7C59]" />
    if (status === false) return <XCircle className="w-4 h-4 text-[#E76F51]" />
    return <AlertTriangle className="w-4 h-4 text-[#D4B08A]" />
  }

  const getStatusColor = (status: boolean | undefined) => {
    if (status === true) return 'text-[#4A7C59]'
    if (status === false) return 'text-[#E76F51]'
    return 'text-[#D4B08A]'
  }

  return (
    <div className="bg-white border border-[#E8E0D1] rounded-xl p-6 shadow-sm">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-[#4A7C59]" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[#2C2C2C] mb-4">Validation & Intelligence</h3>

          <div className="space-y-6">
            {/* Geospatial Checks */}
            <div>
              <h4 className="text-sm font-medium text-[#2C2C2C] mb-3">Geospatial Checks</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-1">
                  <span className="text-[#6B6B6B]">Boundary Compliance</span>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(geospatialChecks.boundary_compliance)}
                    <span className={`text-sm font-medium ${getStatusColor(geospatialChecks.boundary_compliance)}`}>
                      {geospatialChecks.boundary_compliance === true ? 'Pass' : geospatialChecks.boundary_compliance === false ? 'Fail' : 'Unknown'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between py-1">
                  <span className="text-[#6B6B6B]">Distance Analysis</span>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(geospatialChecks.distance_analysis)}
                    <span className={`text-sm font-medium ${getStatusColor(geospatialChecks.distance_analysis)}`}>
                      {geospatialChecks.distance_analysis === true ? 'Valid' : geospatialChecks.distance_analysis === false ? 'Invalid' : 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Anomaly Detection */}
            <div>
              <h4 className="text-sm font-medium text-[#2C2C2C] mb-3">Anomaly Detection</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-1">
                  <span className="text-[#6B6B6B]">Anomalies Detected</span>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(anomalyDetection.detected)}
                    <span className={`text-sm font-medium ${getStatusColor(anomalyDetection.detected)}`}>
                      {anomalyDetection.detected === true ? 'Yes' : anomalyDetection.detected === false ? 'No' : 'Unknown'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between py-1">
                  <span className="text-[#6B6B6B]">Anomaly Count</span>
                  <span className="text-sm font-medium text-[#2C2C2C]">{anomalyDetection.reasons?.length ?? 0}</span>
                </div>
                {anomalyDetection.reasons?.length ? (
                  <div className="text-sm text-[#6B6B6B] mt-2">{anomalyDetection.reasons[0]}</div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}