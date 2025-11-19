import React from 'react'
import { BookText, Map } from 'lucide-react'

type MLvsHEREComparisonProps = {
  ml_results?: {
    top_result?: { lat: number; lon: number; city?: string; state?: string; pincode?: string }
    confidence?: number
  }
  here_results?: {
    primary_result?: {
      title?: string
      position?: { lat: number; lng: number }
      scoring?: { queryScore?: number }
      address?: { city?: string; state?: string; postalCode?: string }
    }
    confidence?: number
  }
}

export function MLvsHEREComparison({
  ml_results,
  here_results
}: MLvsHEREComparisonProps) {
  
  const mlTop = ml_results?.top_result
  const mlCity = mlTop?.city
  const mlState = mlTop?.state
  const mlPin = mlTop?.pincode
  const mlCoords = mlTop ? { lat: mlTop.lat, lng: mlTop.lon } : undefined
  const mlConf = typeof ml_results?.confidence === 'number' ? ml_results?.confidence : undefined

  const here = here_results?.primary_result || {}
  // Use top-level confidence if available, else fallback to queryScore
  const hereConfidence = typeof here_results?.confidence === 'number'
    ? here_results.confidence
    : (here.scoring?.queryScore ?? 0)

  return (
    <div className="card overflow-hidden">
      <div className="bg-gradient-to-r from-brand-sky/10 to-brand-beige p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-brand-graphite">
          Interpretation Comparison
        </h3>
        <p className="text-sm text-brand-graphite/70 mt-1">
          Two approaches to understanding your address
        </p>
      </div>

      <div className="grid md:grid-cols-2 divide-x divide-gray-200">
        {/* Text-based (ML) */}
        <div className="p-6 bg-blue-50/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-brand-sky/20 rounded-lg">
              <BookText className="w-5 h-5 text-brand-sky" />
            </div>
            <div>
              <h4 className="font-semibold text-brand-graphite">Text-Based</h4>
              <p className="text-xs text-brand-graphite/60">ML interpretation</p>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            {mlCity && (
              <div>
                <span className="text-brand-graphite/60">City: </span>
                <span className="font-medium text-brand-graphite">{mlCity}</span>
              </div>
            )}
            {mlState && (
              <div>
                <span className="text-brand-graphite/60">State: </span>
                <span className="font-medium text-brand-graphite">{mlState}</span>
              </div>
            )}
            {mlPin && (
              <div>
                <span className="text-brand-graphite/60">Pincode: </span>
                <span className="font-medium text-brand-graphite">{mlPin}</span>
              </div>
            )}
            {mlCoords && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <span className="text-xs text-brand-graphite/60">Coordinates</span>
                <div className="text-xs font-mono text-brand-graphite mt-1">
                  {mlCoords.lat.toFixed(6)}, {mlCoords.lng.toFixed(6)}
                </div>
              </div>
            )}
            {typeof mlConf === 'number' && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-brand-graphite/60">Confidence</span>
                  <span className="text-xs font-bold text-brand-graphite">
                    {(mlConf * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-brand-sky h-2 rounded-full transition-all"
                    style={{ width: `${mlConf * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 p-3 bg-white/50 rounded-lg border border-brand-sky/20">
            <p className="text-xs text-brand-graphite/70 italic">
              ML estimates the most likely location from textual patterns and known PIN/city anchors.
            </p>
          </div>
        </div>

        {/* Map-based (HERE) */}
        <div className="p-6 bg-green-50/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-brand-forest/20 rounded-lg">
              <Map className="w-5 h-5 text-brand-forest" />
            </div>
            <div>
              <h4 className="font-semibold text-brand-graphite">Map-Based</h4>
              <p className="text-xs text-brand-graphite/60">HERE Maps API</p>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            {here.address?.city && (
              <div>
                <span className="text-brand-graphite/60">City: </span>
                <span className="font-medium text-brand-graphite">{here.address.city}</span>
              </div>
            )}
            {here.address?.state && (
              <div>
                <span className="text-brand-graphite/60">State: </span>
                <span className="font-medium text-brand-graphite">{here.address.state}</span>
              </div>
            )}
            {here.address?.postalCode && (
              <div>
                <span className="text-brand-graphite/60">Pincode: </span>
                <span className="font-medium text-brand-graphite">{here.address.postalCode}</span>
              </div>
            )}
            {here.position && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <span className="text-xs text-brand-graphite/60">Coordinates</span>
                <div className="text-xs font-mono text-brand-graphite mt-1">
                  {here.position.lat.toFixed(6)}, {here.position.lng.toFixed(6)}
                </div>
              </div>
            )}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-brand-graphite/60">Confidence</span>
                <span className="text-xs font-bold text-brand-graphite">
                  {(hereConfidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-brand-forest h-2 rounded-full transition-all"
                  style={{ width: `${hereConfidence * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 bg-white/50 rounded-lg border border-brand-forest/20">
            <p className="text-xs text-brand-graphite/70 italic">
              HERE returns authoritative map coordinates based on street and place databases.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
