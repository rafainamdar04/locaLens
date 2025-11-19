import clsx from 'clsx'

export type MetricLevel = 'high' | 'medium' | 'low' | 'info'

export default function MetricBadge({ label, value, level = 'info' }: {
  label: string
  value?: string | number
  level?: MetricLevel
}) {
  const color = {
    high: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    medium: 'bg-amber-50 text-amber-700 ring-amber-200',
    low: 'bg-red-50 text-red-700 ring-red-200',
    info: 'bg-brand-mint100 text-emerald-700 ring-emerald-200'
  }[level]

  return (
    <span className={clsx('badge ring-1', color)}>
      <span className="font-semibold">{label}</span>
      {value !== undefined && <span className="text-gray-600">{String(value)}</span>}
    </span>
  )
}
