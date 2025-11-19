import { motion } from 'framer-motion'
import { MapPin, CheckCircle, AlertTriangle, XCircle, Clock, Target, Zap, TrendingUp, Award, Shield, Navigation } from 'lucide-react'
import { haversineKmSafe } from '../../utils/geo'

interface ComprehensiveResultsCardProps {
  event: any
  processingTime: number
}

export function ComprehensiveResultsCard({ event, processingTime }: ComprehensiveResultsCardProps) {
  const fused = typeof event.confidence === 'number' ? event.confidence : (typeof event.fused_confidence === 'number' ? event.fused_confidence : 0)
  const integrity = event.integrity?.score ?? 0

  const here_coords = event.here_results?.primary_result?.position || event.here_results?.primary_result
  const ml_coords = event.ml_results?.top_result ? {
    lat: event.ml_results.top_result.lat,
    lng: event.ml_results.top_result.lon
  } : undefined
  const distance_km = haversineKmSafe(here_coords, ml_coords) || null
  const here_confidence = event.here_results?.confidence || event.here_results?.primary_result?.scoring?.queryScore || 0

  const health = event.health || 'UNCERTAIN'

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'OK': return <CheckCircle className="w-6 h-6 text-[#4A7C59]" />
      case 'BAD': return <XCircle className="w-6 h-6 text-[#E76F51]" />
      default: return <AlertTriangle className="w-6 h-6 text-[#6B6B6B]" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white border border-[#E8E0D1] rounded-xl shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className="bg-[#4A7C59] px-8 py-6 text-white">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center">
            <MapPin className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-medium text-white">Address Analysis</h3>
            <p className="text-[#E8E0D1] text-sm">Comprehensive intelligence report</p>
          </div>
        </div>
      </div>

      <div className="p-8 space-y-8">
        {/* Health Status */}
        <div className="flex items-center justify-between p-6 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              {getHealthIcon(health)}
            </div>
            <div>
              <div className="text-xl font-medium text-[#2C2C2C]">Address Health: {health}</div>
              <div className="text-sm text-[#6B6B6B]">Overall validation status</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-[#6B6B6B]">Processing Time</div>
            <div className="text-lg font-medium text-[#2C2C2C]">{processingTime}ms</div>
          </div>
        </div>

        {/* Address Section */}
        <div className="bg-white rounded-xl border border-[#E8E0D1] shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              <MapPin className="w-5 h-5 text-[#4A7C59]" />
            </div>
            <h2 className="text-xl font-medium text-[#2C2C2C]">Address Analysis</h2>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-[#E76F51] rounded-full"></div>
                  <h3 className="text-sm font-medium text-[#6B6B6B] uppercase tracking-wide">Raw Input</h3>
                </div>
                <p className="text-[#6B6B6B] line-through italic text-sm leading-relaxed pl-4 border-l-2 border-[#E8E0D1]">
                  {event.raw_address || ''}
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-[#4A7C59] rounded-full"></div>
                  <h3 className="text-sm font-medium text-[#6B6B6B] uppercase tracking-wide">Standardized Address</h3>
                </div>
                <p className="text-[#2C2C2C] font-medium text-base leading-relaxed pl-4 border-l-2 border-[#E8E0D1]">
                  {event.cleaned_address || event.cleaned || ''}
                </p>
              </div>
            </div>

            {event.cleaned_components && Object.keys(event.cleaned_components).length > 0 && (
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-[#6B6B6B] uppercase tracking-wide flex items-center space-x-2">
                  <div className="w-2 h-2 bg-[#4A7C59] rounded-full"></div>
                  <span>Address Components</span>
                </h3>
                <div className="flex flex-wrap gap-3">
                  {Object.entries(event.cleaned_components).map(([key, value]) => (
                    <div
                      key={key}
                      className="px-4 py-2 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1] shadow-sm"
                    >
                      <span className="text-xs font-bold text-[#2C2C2C] uppercase tracking-wider">{key}:</span>
                      <span className="text-sm font-medium text-[#6B6B6B] ml-2">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quality Metrics Section */}
        <div className="bg-white rounded-xl border border-[#E8E0D1] shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              <Target className="w-5 h-5 text-[#4A7C59]" />
            </div>
            <h2 className="text-xl font-medium text-[#2C2C2C]">Quality Metrics</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-3">
                <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-3xl font-medium text-[#2C2C2C] mb-1">{(fused * 100).toFixed(1)}%</div>
              <div className="text-sm text-[#6B6B6B]">Confidence Score</div>
              <div className="mt-3 bg-[#E8E0D1] rounded-full h-2">
                <div
                  className="bg-[#4A7C59] h-2 rounded-full transition-all duration-500"
                  style={{ width: `${fused * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="text-center p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center mb-3">
                <div className="w-12 h-12 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
                  <Shield className="w-6 h-6 text-[#4A7C59]" />
                </div>
              </div>
              <div className="text-3xl font-medium text-[#2C2C2C] mb-1">{integrity.toFixed(1)}%</div>
              <div className="text-sm text-[#6B6B6B]">Integrity Score</div>
              <div className="mt-3 bg-[#E8E0D1] rounded-full h-2">
                <div
                  className="bg-[#4A7C59] h-2 rounded-full transition-all duration-500"
                  style={{ width: `${integrity}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Geocoding Section */}
        <div className="bg-white rounded-xl border border-[#E8E0D1] shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-full flex items-center justify-center">
              <Zap className="w-5 h-5 text-[#4A7C59]" />
            </div>
            <h2 className="text-xl font-medium text-[#2C2C2C]">Geocoding Results</h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* HERE Results */}
            <div className="p-6 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-[#4A7C59] rounded-lg flex items-center justify-center">
                  <Navigation className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-lg font-bold text-[#2C2C2C]">HERE Geocoding</h3>
              </div>
              {event.here_results?.primary_result ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 px-3 bg-white rounded-lg">
                    <span className="text-sm font-medium text-[#6B6B6B]">Coordinates:</span>
                    <span className="text-sm font-mono text-[#2C2C2C]">{here_coords?.lat?.toFixed(6)}, {here_coords?.lng?.toFixed(6)}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 px-3 bg-white rounded-lg">
                    <span className="text-sm font-medium text-[#6B6B6B]">Confidence:</span>
                    <span className={`text-sm font-bold ${here_confidence < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{(here_confidence * 100).toFixed(1)}%</span>
                  </div>
                  {event.here_results.alternatives && (
                    <div className="flex justify-between items-center py-2 px-3 bg-white rounded-lg">
                      <span className="text-sm font-medium text-[#6B6B6B]">Alternatives:</span>
                      <span className="text-sm font-bold text-[#2C2C2C]">{event.here_results.alternatives.length}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-[#E8E0D1] rounded-xl flex items-center justify-center mx-auto mb-3">
                    <XCircle className="w-6 h-6 text-[#6B6B6B]" />
                  </div>
                  <p className="text-[#6B6B6B] font-medium">No results available</p>
                </div>
              )}
            </div>

            {/* ML Results */}
            <div className="p-6 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-[#4A7C59] rounded-lg flex items-center justify-center">
                  <Target className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-lg font-bold text-[#2C2C2C]">ML Geocoding</h3>
              </div>
              {event.ml_results?.top_result ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 px-3 bg-white rounded-lg">
                    <span className="text-sm font-medium text-[#6B6B6B]">Coordinates:</span>
                    <span className="text-sm font-mono text-[#2C2C2C]">{ml_coords?.lat?.toFixed(6)}, {ml_coords?.lng?.toFixed(6)}</span>
                  </div>
                  {event.ml_results.top_result.confidence && (
                    <div className="flex justify-between items-center py-2 px-3 bg-white rounded-lg">
                      <span className="text-sm font-medium text-[#6B6B6B]">Confidence:</span>
                      <span className={`text-sm font-bold ${event.ml_results.top_result.confidence < 0.5 ? 'text-[#E76F51]' : 'text-[#4A7C59]'}`}>{(event.ml_results.top_result.confidence * 100).toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-[#E8E0D1] rounded-xl flex items-center justify-center mx-auto mb-3">
                    <XCircle className="w-6 h-6 text-[#6B6B6B]" />
                  </div>
                  <p className="text-[#6B6B6B] font-medium">No results available</p>
                </div>
              )}
            </div>
          </div>

          {/* Comparison */}
          {distance_km !== null && (
            <div className="mt-6 p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
              <div className="flex items-center justify-center space-x-3">
                <div className="w-8 h-8 bg-[#4A7C59] rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-white" />
                </div>
                <div className="text-center">
                  <div className="text-sm font-medium text-[#6B6B6B]">Coordinate Difference</div>
                  <div className="text-lg font-bold text-[#2C2C2C]">{distance_km.toFixed(3)} km</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Additional Information */}
        {(event.anomaly || event.self_heal) && (
          <div className="bg-white rounded-xl border border-[#E8E0D1] shadow-sm p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-[#4A7C59]/10 rounded-xl flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-[#4A7C59]" />
              </div>
              <h2 className="text-xl font-bold text-[#2C2C2C]">Additional Insights</h2>
            </div>

            <div className="space-y-4">
              {event.anomaly && (
                <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-[#E76F51] rounded-xl flex items-center justify-center flex-shrink-0">
                      <AlertTriangle className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-[#E76F51] mb-2">Anomaly Detection</h3>
                      <div className="text-[#6B6B6B]">
                        {event.anomaly.detected ? (
                          <div className="space-y-2">
                            <p className="font-medium">Anomalies detected in the address processing</p>
                            {event.anomaly.reasons && event.anomaly.reasons.length > 0 && (
                              <ul className="space-y-1 ml-4">
                                {event.anomaly.reasons.map((reason: string, idx: number) => (
                                  <li key={idx} className="text-sm flex items-start space-x-2">
                                    <span className="text-[#E76F51] mt-1">•</span>
                                    <span>{reason}</span>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        ) : (
                          <p className="font-medium text-[#4A7C59]">No anomalies detected</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {event.self_heal && (
                <div className="p-4 bg-[#FAF7F0] rounded-xl border border-[#E8E0D1]">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-[#4A7C59] rounded-xl flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-[#4A7C59] mb-2">Self-Healing Actions</h3>
                      <div className="text-[#6B6B6B]">
                        {event.self_heal_actions ? (
                          <p className="font-medium">Self-healing corrections were applied to improve the address data</p>
                        ) : (
                          <p className="font-medium">No self-healing actions were required</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Summary */}
        {event.summary?.human_readable && (
          <div className="bg-[#4A7C59] rounded-xl p-6 text-white">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center border border-white/20">
                <Award className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-xl font-bold text-white">Summary</h2>
            </div>
            <p className="text-white/90 leading-relaxed text-base">{event.summary.human_readable}</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}