import { motion, useAnimation } from 'framer-motion'
import { useEffect } from 'react'

export default function ConfidenceGaugeRadial({ value = 0 }: { value?: number }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)))
  const radius = 62
  const stroke = 12
  const normalizedRadius = radius - stroke / 2
  const circumference = normalizedRadius * 2 * Math.PI
  const dashArray = circumference

  const controls = useAnimation()

  useEffect(() => {
    // Animate from 0 to final
    controls.start({ pathLength: pct / 100, transition: { duration: 1.25, ease: 'easeOut' } })
  }, [pct, controls])

  const color = pct >= 80 ? '#059669' : pct >= 50 ? '#D97706' : '#DC2626'

  return (
    <div className="flex items-center gap-6">
      <svg height={radius * 2} width={radius * 2} className="block">
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4ADE80" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>
        </defs>
        <g transform={`translate(${radius}, ${radius})`}>
          <circle
            r={normalizedRadius}
            fill="transparent"
            stroke="#f3f4f6"
            strokeWidth={stroke}
          />
          <motion.circle
            r={normalizedRadius}
            fill="transparent"
            stroke="url(#gradient)"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={dashArray}
            strokeDashoffset={dashArray}
            style={{ rotate: -90 }}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: pct / 100 }}
            transition={{ duration: 1.2, ease: 'circOut' }}
          />
        </g>
      </svg>
      <div className="flex flex-col">
        <div className="text-sm text-gray-500">Confidence</div>
        <div className="text-2xl font-semibold" style={{ color }}>{pct}%</div>
        <div className="text-xs text-gray-500">Fused score across ML, HERE & LLM</div>
      </div>
    </div>
  )
}
