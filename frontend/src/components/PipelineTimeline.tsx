import { motion } from 'framer-motion'
import { useState } from 'react'
import { ChevronDownIcon } from '@heroicons/react/24/outline'

export default function PipelineTimeline({ steps }: { steps: any[] }) {
  return (
    <div className="space-y-3">
      {steps.map((s, i) => (
        <motion.div
          key={s.name}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
          className="card p-4 flex items-start gap-3"
        >
          <div className="mt-1 text-center w-12">
            <div className={`h-8 w-8 rounded-full flex items-center justify-center ${s.status === 'pass' ? 'bg-emerald-50 text-emerald-600' : s.status === 'warn' ? 'bg-amber-50 text-amber-600' : 'bg-red-50 text-red-600'}`}>
              {s.status === 'pass' ? '✓' : s.status === 'warn' ? '!' : '×'}
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold">{s.name}</div>
                <div className="text-xs text-gray-500">{s.summary}</div>
              </div>
              <div className="text-xs text-gray-500">{s.time ?? ''}</div>
            </div>
            {s.details && (
              <details className="mt-2 text-xs text-gray-700 bg-gray-50 rounded p-2 border border-gray-100">
                <summary className="flex items-center gap-2 cursor-pointer">Details <ChevronDownIcon className="h-4 w-4" /></summary>
                <pre className="text-[11px] mt-2 overflow-auto">{JSON.stringify(s.details, null, 2)}</pre>
              </details>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  )
}
