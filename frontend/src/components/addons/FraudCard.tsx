import { ShieldAlert } from 'lucide-react'

type FraudData = {
  fraud_risk?: number
  flags?: string[]
  anomaly_count?: number
  explanation?: string
  error?: string
}

export default function FraudCard({ data }: { data: FraudData }) {
  if (data?.error) {
    return (
      <div className="bg-white rounded-2xl shadow-sm p-8 border-2 border-red-200 min-h-[220px] flex flex-col justify-center">
        <div className="flex items-center gap-2 mb-2">
          <ShieldAlert className="w-6 h-6 text-red-500" />
          <h4 className="text-base font-semibold text-brand-graphite">Fraud Check</h4>
        </div>
        <p className="text-sm text-red-500">Could not compute</p>
      </div>
    )
  }

  const score = data?.fraud_risk ?? 0
  const scoreColor = score <= 0.3 ? 'bg-brand-forest text-white' : score <= 0.6 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
  const description = score <= 0.3 
    ? 'No suspicious patterns detected.' 
    : score <= 0.6 
    ? 'Some patterns worth reviewing.'
    : 'Multiple suspicious signals found.'

  const flags = Array.isArray(data?.flags) ? data.flags : []

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8 border-2 border-gray-200 min-h-[220px] flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-brand-terracotta" />
            <h4 className="text-base font-semibold text-brand-graphite">Fraud Check</h4>
          </div>
          <span className={`text-xs font-bold px-4 py-2 rounded-full ${scoreColor}`} title="Fraud risk score. Higher means more suspicious patterns detected.">
            {Math.round(score * 100)}%
          </span>
        </div>
        <p className="text-sm text-gray-700 leading-relaxed mb-4">{description}</p>
        {flags.length > 0 ? (
          <div className="space-y-2">
            <span className="text-xs text-gray-500">Signals detected:</span>
            <div className="flex flex-wrap gap-2">
              {flags.slice(0, 6).map((flag, i) => (
                <span key={i} className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-yellow-50 text-yellow-700 border border-yellow-200" title="Fraud signal detected by the system.">
                  {flag}
                </span>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">No fraud signals detected</p>
        )}
      </div>
      {data?.anomaly_count !== undefined && data.anomaly_count > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Anomalies</span>
            <span className="font-medium text-brand-graphite">{data.anomaly_count}</span>
          </div>
        </div>
      )}
      {data?.explanation && (
        <div className="mt-4 text-xs text-gray-600">
          <span className="font-medium text-brand-graphite">Explanation: </span>{data.explanation}
        </div>
      )}
    </div>
  )
}
