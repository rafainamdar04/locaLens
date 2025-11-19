import React from 'react'

type RadarChartProps = {
  city_match?: boolean
  pincode_match?: boolean
  boundary_check?: boolean
  reachability_score?: number
}

export function RadarChart({
  city_match,
  pincode_match,
  boundary_check,
  reachability_score = 0.5
}: RadarChartProps) {
  
  // Convert boolean/score to 0-1 values
  const values = {
    'City Match': city_match ? 1 : 0,
    'Pincode Match': pincode_match ? 1 : 0,
    'Boundary Check': boundary_check ? 1 : 0,
    'Reachability': reachability_score
  }

  const labels = Object.keys(values)
  const scores = Object.values(values)
  
  // Calculate radar chart points
  const centerX = 100
  const centerY = 100
  const maxRadius = 80
  const angleStep = (Math.PI * 2) / labels.length

  const getPoint = (index: number, value: number) => {
    const angle = angleStep * index - Math.PI / 2
    const radius = maxRadius * value
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    }
  }

  const axisPoints = labels.map((_, i) => {
    const angle = angleStep * i - Math.PI / 2
    return {
      x: centerX + maxRadius * Math.cos(angle),
      y: centerY + maxRadius * Math.sin(angle)
    }
  })

  const dataPoints = scores.map((value, i) => getPoint(i, value))
  const polygonPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z'

  const getColorForValue = (value: number) => {
    if (value > 0.8) return '#10B981' // green
    if (value > 0.5) return '#F59E0B' // amber
    return '#EF4444' // red
  }

  const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-brand-graphite mb-4">
        Spatial Quality Metrics
      </h3>
      
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 200 200" className="w-64 h-64">
          {/* Background circles */}
          <circle cx={centerX} cy={centerY} r={maxRadius} fill="none" stroke="#E5E7EB" strokeWidth="1" />
          <circle cx={centerX} cy={centerY} r={maxRadius * 0.66} fill="none" stroke="#E5E7EB" strokeWidth="1" />
          <circle cx={centerX} cy={centerY} r={maxRadius * 0.33} fill="none" stroke="#E5E7EB" strokeWidth="1" />
          
          {/* Axis lines */}
          {axisPoints.map((point, i) => (
            <line
              key={i}
              x1={centerX}
              y1={centerY}
              x2={point.x}
              y2={point.y}
              stroke="#D1D5DB"
              strokeWidth="1"
            />
          ))}
          
          {/* Data polygon */}
          <path
            d={polygonPath}
            fill={getColorForValue(avgScore)}
            fillOpacity="0.2"
            stroke={getColorForValue(avgScore)}
            strokeWidth="2"
          />
          
          {/* Data points */}
          {dataPoints.map((point, i) => (
            <circle
              key={i}
              cx={point.x}
              cy={point.y}
              r="4"
              fill={getColorForValue(scores[i])}
            />
          ))}
          
          {/* Labels */}
          {labels.map((label, i) => {
            const angle = angleStep * i - Math.PI / 2
            const labelRadius = maxRadius + 20
            const x = centerX + labelRadius * Math.cos(angle)
            const y = centerY + labelRadius * Math.sin(angle)
            
            return (
              <text
                key={i}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="text-xs fill-brand-graphite font-medium"
              >
                {label}
              </text>
            )
          })}
        </svg>
      </div>

      <div className="mt-4 space-y-2">
        {labels.map((label, i) => (
          <div key={i} className="flex items-center justify-between text-sm">
            <span className="text-brand-graphite/70">{label}</span>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: getColorForValue(scores[i]) }} />
              <span className="font-medium text-brand-graphite">
                {(scores[i] * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-brand-graphite/70">Overall Score</span>
          <span className="text-lg font-bold" style={{ color: getColorForValue(avgScore) }}>
            {(avgScore * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  )
}
