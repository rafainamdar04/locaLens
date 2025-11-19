import React from 'react'
import { CheckCircle, ArrowRight } from 'lucide-react'

type TimelineStep = {
  label: string
  value?: string
  status: 'completed' | 'warning' | 'error'
}

type TimelineProps = {
  raw_address?: string
  cleaned?: string
  pincode_detected?: string
  here_result?: string
  ml_result?: string
  mismatch_detected?: boolean
  trace?: string[]
}

export function Timeline({
  raw_address,
  cleaned,
  pincode_detected,
  here_result,
  ml_result,
  mismatch_detected,
  trace
}: TimelineProps) {
  
  // Build timeline steps
  const steps: TimelineStep[] = []

  if (raw_address) {
    steps.push({
      label: 'Raw Address Received',
      value: raw_address.length > 60 ? raw_address.slice(0, 60) + '...' : raw_address,
      status: 'completed'
    })
  }

  if (cleaned) {
    steps.push({
      label: 'Address Cleaned',
      value: cleaned.length > 60 ? cleaned.slice(0, 60) + '...' : cleaned,
      status: 'completed'
    })
  }

  if (pincode_detected) {
    steps.push({
      label: 'Pincode Identified',
      value: pincode_detected,
      status: 'completed'
    })
  }

  if (here_result) {
    steps.push({
      label: 'HERE Maps Geocoded',
      value: here_result,
      status: 'completed'
    })
  }

  if (ml_result) {
    steps.push({
      label: 'ML Text Analysis',
      value: ml_result,
      status: 'completed'
    })
  }

  if (mismatch_detected !== undefined) {
    steps.push({
      label: 'Spatial Comparison',
      value: mismatch_detected ? 'Mismatch detected' : 'Locations align',
      status: mismatch_detected ? 'warning' : 'completed'
    })
  }

  // If trace is provided, use it instead
  if (trace && trace.length > 0) {
    const traceSteps: TimelineStep[] = trace.map(t => ({
      label: t,
      status: 'completed'
    }))
    return renderTimeline(traceSteps)
  }

  return renderTimeline(steps)
}

function renderTimeline(steps: TimelineStep[]) {
  if (steps.length === 0) {
    return (
      <div className="card p-6 text-center text-brand-graphite/60">
        <p>Processing timeline not available</p>
      </div>
    )
  }

  const getStatusColor = (status: TimelineStep['status']) => {
    switch (status) {
      case 'completed': return 'bg-brand-forest text-white'
      case 'warning': return 'bg-yellow-500 text-white'
      case 'error': return 'bg-red-500 text-white'
    }
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-brand-graphite mb-6">
        How We Interpreted This Address
      </h3>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="flex gap-4">
            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStatusColor(step.status)}`}>
                {step.status === 'completed' && <CheckCircle className="w-4 h-4" />}
                {step.status === 'warning' && <span className="text-xs font-bold">!</span>}
                {step.status === 'error' && <span className="text-xs font-bold">×</span>}
              </div>
              {index < steps.length - 1 && (
                <div className="w-0.5 flex-1 bg-gray-200 my-1" style={{ minHeight: '24px' }} />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 pb-4">
              <div className="font-medium text-brand-graphite mb-1">
                {step.label}
              </div>
              {step.value && (
                <div className="text-sm text-brand-graphite/70 bg-brand-beige rounded px-3 py-2 mt-2">
                  {step.value}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200 flex items-center gap-2 text-sm text-brand-graphite/60">
        <ArrowRight className="w-4 h-4" />
        <span>Processing completed in {steps.length} steps</span>
      </div>
    </div>
  )
}
