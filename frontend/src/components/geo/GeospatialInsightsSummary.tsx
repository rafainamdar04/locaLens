import React from 'react'
import { Sparkles, MapPin } from 'lucide-react'

type GeospatialInsightsSummaryProps = {
  integrity_score?: number
  here_confidence?: number
  // distance_km intentionally omitted from rendering to avoid duplication with MapPanel
  distance_km?: number
  city_match?: boolean
  pincode_match?: boolean
}

export function GeospatialInsightsSummary({
  integrity_score = 0,
  here_confidence = 0,
  distance_km,
  city_match,
  pincode_match
}: GeospatialInsightsSummaryProps) {
  
  const generateSummary = (): string => {
    const parts: string[] = []
    
    // Overall quality assessment
    const i = integrity_score ?? 0
    const h = here_confidence ?? 0
    const avg = (i + h) / 2
    if (avg >= 0.8) {
      parts.push('High overall quality and agreement across methods')
    } else if (avg >= 0.6) {
      parts.push('Generally good quality with minor uncertainties')
    } else if (avg >= 0.4) {
      parts.push('Moderate quality—review recommended before using')
    } else {
      parts.push('Low overall confidence—requires verification')
    }
    
    // Spatial analysis (kept narrative-only; exact km shown in MapPanel)
    if (typeof distance_km === 'number') {
      if (distance_km < 3) {
        parts.push('Spatial agreement looks strong')
      } else if (distance_km < 15) {
        parts.push('Spatial agreement is mixed')
      } else {
        parts.push('Spatial disagreement is significant')
      }
    }
    
    // Match indicators
    if (city_match === true && pincode_match === true) {
      parts.push('City and pincode both align with authoritative sources')
    } else if (city_match === false || pincode_match === false) {
      parts.push('Administrative mismatch detected—verify city or pincode')
    }
    
    return parts.join('. ') + '.'
  }

  const getConfidenceLevel = (): { label: string; color: string } => {
    const i = integrity_score ?? 0
    const h = here_confidence ?? 0
    const avgScore = (i + h) / 2
    if (avgScore >= 0.75) return { label: 'HIGH CONFIDENCE', color: 'bg-green-100 text-green-800 border-green-300' }
    if (avgScore >= 0.5) return { label: 'MEDIUM CONFIDENCE', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' }
    return { label: 'LOW CONFIDENCE', color: 'bg-red-100 text-red-800 border-red-300' }
  }

  const confidence = getConfidenceLevel()

  return (
    <div className="card p-6 bg-gradient-to-br from-brand-beige to-white border-2 border-brand-sky/30">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-brand-forest/10 rounded-xl">
          <Sparkles className="w-6 h-6 text-brand-forest" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-brand-graphite">
              Key Geospatial Insights
            </h3>
            <span className={`px-3 py-1 text-xs font-bold rounded-full border ${confidence.color}`}>
              {confidence.label}
            </span>
          </div>
          <p className="text-brand-graphite/80 leading-relaxed">
            {generateSummary()}
          </p>
          
          <div className="mt-4 flex gap-6 text-sm">
            <div className="flex items-center gap-2" title="Completeness of address components (0-100%)">
              <div className="w-2 h-2 rounded-full bg-brand-forest" />
              <span className="text-brand-graphite/70">
                Integrity: {(integrity_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center gap-2" title="HERE geocoding match strength (0-100%)">
              <div className="w-2 h-2 rounded-full bg-brand-terracotta" />
              <span className="text-brand-graphite/70">
                HERE: {(here_confidence * 100).toFixed(0)}%
              </span>
            </div>
            {/* Exact mismatch distance is shown in MapPanel to avoid duplication */}
          </div>
        </div>
      </div>
    </div>
  )
}
