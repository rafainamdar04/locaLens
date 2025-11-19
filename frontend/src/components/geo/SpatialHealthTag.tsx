import React from 'react'
import { CheckCircle2, AlertCircle, XCircle } from 'lucide-react'

type SpatialHealthTagProps = {
  distance_km?: number
}

export function SpatialHealthTag({ distance_km }: SpatialHealthTagProps) {
  
  const getHealthLevel = () => {
    if (distance_km === undefined) {
      return {
        level: 'UNKNOWN',
        color: 'bg-gray-100 text-gray-700 border-gray-300',
        icon: AlertCircle,
        description: 'Spatial confidence not calculated'
      }
    }
    
    if (distance_km < 3) {
      return {
        level: 'HIGH CONFIDENCE',
        color: 'bg-green-100 text-green-800 border-green-300',
        icon: CheckCircle2,
        description: 'Excellent spatial agreement - both methods align closely'
      }
    }
    
    if (distance_km < 15) {
      return {
        level: 'MEDIUM CONFIDENCE',
        color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        icon: AlertCircle,
        description: 'Acceptable spatial variance - minor differences detected'
      }
    }
    
    return {
      level: 'LOW CONFIDENCE',
      color: 'bg-red-100 text-red-800 border-red-300',
      icon: XCircle,
      description: 'Significant spatial discrepancy - verification recommended'
    }
  }

  const health = getHealthLevel()
  const Icon = health.icon

  return (
    <div className={`card p-4 border-2 ${health.color}`}>
      <div className="flex items-center gap-3">
        <Icon className="w-6 h-6 flex-shrink-0" />
        <div className="flex-1">
          <div className="font-bold text-sm mb-1">
            {health.level}
          </div>
          <div className="text-xs opacity-90">
            {health.description}
          </div>
          {distance_km !== undefined && (
            <div className="mt-2 text-xs font-mono">
              Mismatch: {distance_km.toFixed(2)} km
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
