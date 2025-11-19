import { motion } from 'framer-motion'
import { ReactNode } from 'react'

export default function Card({ title, subtitle, children, className = '' }: {
  title?: string
  subtitle?: string
  children: ReactNode
  className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`card ${className}`}
    >
      {(title || subtitle) && (
        <div className="border-b border-[#E8E0D1] px-6 py-4">
          {title && <h3 className="text-base font-semibold text-[#2C2C2C]">{title}</h3>}
          {subtitle && <p className="text-sm text-[#6B6B6B] mt-0.5">{subtitle}</p>}
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </motion.div>
  )
}
