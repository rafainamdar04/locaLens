import { Home } from 'lucide-react'

type PropertyRiskData = {
  risk_score?: number
  score?: number
  flood_risk?: number
  fire_access_risk?: number
  road_connectivity_index?: number
  hospital_access_risk?: number
  explanation?: string
  reasons?: string[]
  missing_data?: string[]
  error?: string
}

export default function PropertyRiskCard({ data }: { data: PropertyRiskData }) {
  if (data?.error) {
    return (
      <div className="bg-white rounded-2xl shadow-sm p-6 border border-red-100">
        <div className="flex items-center gap-2 mb-2">
          <Home className="w-5 h-5 text-red-500" />
          <h4 className="text-sm font-medium text-brand-graphite">Property Risk</h4>
        </div>
        <p className="text-xs text-red-500">Could not compute</p>
      </div>
    )
  }

  const score = data?.score ?? data?.risk_score ?? 0;
  const scoreColor = score <= 0.3 ? 'bg-brand-forest text-white' : score <= 0.6 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';
  const description = score <= 0.3
    ? 'Low risk environment for this property.'
    : score <= 0.6
    ? 'Moderate risk factors detected.'
    : 'Higher risk factors present.';

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8 border-2 border-gray-200 min-h-[220px] flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Home className="w-6 h-6 text-brand-terracotta" />
            <h4 className="text-base font-semibold text-brand-graphite">Property Risk</h4>
          </div>
          <span className={`text-xs font-bold px-4 py-2 rounded-full ${scoreColor}`} title="Property risk score. Lower means safer property.">
            {Math.round(score * 100)}%
          </span>
        </div>
        <p className="text-sm text-gray-700 leading-relaxed mb-4">{description}</p>
        <div className="space-y-3 text-sm">
          {data?.flood_risk !== undefined && (
            <div className="flex justify-between">
              <span className="text-gray-500">Flood Risk</span>
              <span className={`font-medium ${data.flood_risk > 0.5 ? 'text-red-600' : 'text-brand-forest'}`} title="Likelihood of flooding at this location.">{Math.round(data.flood_risk * 100)}%</span>
            </div>
          )}
          {data?.fire_access_risk !== undefined && (
            <div className="flex justify-between">
              <span className="text-gray-500">Fire Access</span>
              <span className={`font-medium ${data.fire_access_risk > 0.5 ? 'text-red-600' : 'text-brand-forest'}`} title="Difficulty for fire services to reach this property.">{Math.round(data.fire_access_risk * 100)}%</span>
            </div>
          )}
          {data?.road_connectivity_index !== undefined && (
            <div className="flex justify-between">
              <span className="text-gray-500">Road Access</span>
              <span className="font-medium text-brand-graphite" title="How well the property is connected to roads.">{Math.round(data.road_connectivity_index * 100)}%</span>
            </div>
          )}
          {data?.hospital_access_risk !== undefined && (
            <div className="flex justify-between">
              <span className="text-gray-500">Hospital Access</span>
              <span className={`font-medium ${data.hospital_access_risk > 0.5 ? 'text-red-600' : 'text-brand-forest'}`} title="Difficulty for ambulances to reach this property.">{Math.round(data.hospital_access_risk * 100)}%</span>
            </div>
          )}
        </div>
      </div>
      {(data?.reasons?.length || data?.missing_data?.length) && (
        <div className="mt-4 border-t pt-3">
          {data?.reasons?.length ? (
            <div className="text-xs text-gray-700">
              <div className="font-medium text-brand-graphite mb-1">Why this risk</div>
              <ul className="list-disc list-inside">
                {data.reasons.map((r, i) => (
                  <li key={i}>{r.replace(/_/g, ' ')}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {data?.missing_data?.length ? (
            <div className="text-xs text-gray-600 mt-2">
              <div className="font-medium text-brand-graphite mb-1">Missing data</div>
              <ul className="list-disc list-inside">
                {data.missing_data.map((m, i) => (
                  <li key={i}>{m.replace(/_/g, ' ')}</li>
                ))}
              </ul>
            </div>
          ) : null}
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
