import clsx from 'clsx'

export default function ConfidenceGauge({ value = 0 }: { value?: number }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)))
  const level = pct >= 80 ? 'high' : pct >= 50 ? 'medium' : 'low'
  const barColor = {
    high: 'bg-[#4A7C59]',
    medium: 'bg-[#D4B08A]',
    low: 'bg-[#E76F51]'
  }[level]
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-[#6B6B6B]">Fused Confidence</span>
        <span className={clsx('text-sm font-semibold',
          level === 'high' && 'text-[#4A7C59]',
          level === 'medium' && 'text-[#D4B08A]',
          level === 'low' && 'text-[#E76F51]'
        )}>{pct}%</span>
      </div>
      <div className="h-3 w-full rounded-full bg-[#E8E0D1]">
        <div className={`h-3 rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
