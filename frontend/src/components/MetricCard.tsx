import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export default function MetricCard({ label, value, color = 'bg-brand-mint' }: { label: string; value: number; color?: string }) {
  const [display, setDisplay] = useState(0)
  useEffect(() => {
    let raf = 0
    const start = Date.now()
    const duration = 800
    const initial = 0
    const target = value
    const step = () => {
      const t = Math.min(1, (Date.now() - start) / duration)
      const cur = Math.round(initial + (target - initial) * t)
      setDisplay(cur)
      if (t < 1) raf = window.requestAnimationFrame(step)
    }
    raf = window.requestAnimationFrame(step)
    return () => window.cancelAnimationFrame(raf)
  }, [value])

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }} className="card p-3">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-xl font-semibold">{display}</div>
    </motion.div>
  )
}
