import { MapPin } from 'lucide-react'

type NeighborhoodData = {
  neighborhood_score?: number
  score?: number
  city?: string
  density?: string
  poi_count?: number
  safety_index?: number
  explanation?: string
  error?: string
}

export default function NeighborhoodCard({ data }: { data: NeighborhoodData }) {
  if (data?.error) {
    return (
      <div className="bg-white rounded-2xl shadow-sm p-6 border border-red-100">
        <div className="flex items-center gap-2 mb-2">
          <MapPin className="w-5 h-5 text-red-500" />
          <h4 className="text-sm font-medium text-brand-graphite">Neighborhood</h4>
        </div>
        <p className="text-xs text-red-500">Could not compute</p>
      </div>
    )
  }

  const score = data?.score ?? data?.neighborhood_score ?? 0
  const scoreColor = score >= 0.7 ? 'bg-brand-forest text-white' : score >= 0.4 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8 border-2 border-gray-200 min-h-[220px] flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <MapPin className="w-6 h-6 text-brand-terracotta" />
            <h4 className="text-base font-semibold text-brand-graphite">Neighborhood</h4>
          </div>
          {score > 0 && (
            <span className={`text-xs font-bold px-4 py-2 rounded-full ${scoreColor}`} title="Neighborhood score. Higher means better amenities and safety.">
              {Math.round(score * 100)}%
            </span>
          )}
        </div>
        <p className="text-sm text-gray-700 leading-relaxed mb-4">Context about the area around this address.</p>
        <div className="space-y-3 text-sm">
          {data?.city && (
            <div className="flex justify-between">
              <span className="text-gray-500">City</span>
              <span className="font-medium text-brand-graphite">{data.city}</span>
            </div>
          )}
          {data?.density && (
            <div className="flex justify-between">
              <span className="text-gray-500">Density</span>
              <span className="font-medium text-brand-graphite capitalize" title="Density describes how crowded or sparse the area is.">{data.density}</span>
            </div>
          )}
          {data?.poi_count !== undefined && (
            <div className="flex justify-between">
              <span className="text-gray-500">Points of Interest</span>
              <span className="font-medium text-brand-graphite" title="Number of amenities, shops, and services nearby.">{data.poi_count}</span>
            </div>
          )}
          {data?.safety_index !== undefined && (
            <div className="flex justify-between">
              <span className="text-gray-500">Safety Index</span>
              <span className="font-medium text-brand-graphite" title="Safety index estimates how safe the area is.">{Math.round(data.safety_index * 100)}%</span>
            </div>
          )}
        </div>
      </div>
      {data?.explanation && (
        <div className="mt-4 text-xs text-gray-600">
          <span className="font-medium text-brand-graphite">Explanation: </span>{data.explanation}
        </div>
      )}
    </div>
  )
}
