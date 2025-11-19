import React from 'react'
import { MapPinned, Building2, Navigation, Hash } from 'lucide-react'

type AdministrativeHierarchyProps = {
  state?: string
  district?: string
  sub_district?: string
  locality?: string
  pincode?: string
  pincode_centroid_distance_km?: number
}

export function AdministrativeHierarchy({
  state,
  district,
  sub_district,
  locality,
  pincode,
  pincode_centroid_distance_km
}: AdministrativeHierarchyProps) {
  
  const hasData = state || district || sub_district || locality || pincode

  if (!hasData) {
    return (
      <div className="card p-6 text-center text-brand-graphite/60">
        <Building2 className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p>Administrative hierarchy data not available</p>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className="p-2 bg-brand-terracotta/10 rounded-lg">
          <Building2 className="w-5 h-5 text-brand-terracotta" />
        </div>
        <h3 className="text-lg font-semibold text-brand-graphite">
          Administrative Hierarchy
        </h3>
      </div>

      <div className="space-y-3">
        {state && (
          <div className="flex items-center gap-3 p-3 bg-brand-beige rounded-lg">
            <MapPinned className="w-5 h-5 text-brand-forest flex-shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-brand-graphite/60 uppercase tracking-wide">
                State
              </div>
              <div className="text-sm font-medium text-brand-graphite">
                {state}
              </div>
            </div>
          </div>
        )}

        {district && (
          <div className="flex items-center gap-3 p-3 bg-brand-beige rounded-lg">
            <Building2 className="w-5 h-5 text-brand-forest flex-shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-brand-graphite/60 uppercase tracking-wide">
                District
              </div>
              <div className="text-sm font-medium text-brand-graphite">
                {district}
              </div>
            </div>
          </div>
        )}

        {sub_district && (
          <div className="flex items-center gap-3 p-3 bg-brand-beige rounded-lg">
            <Navigation className="w-5 h-5 text-brand-forest flex-shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-brand-graphite/60 uppercase tracking-wide">
                Sub-District
              </div>
              <div className="text-sm font-medium text-brand-graphite">
                {sub_district}
              </div>
            </div>
          </div>
        )}

        {locality && (
          <div className="flex items-center gap-3 p-3 bg-brand-beige rounded-lg">
            <Hash className="w-5 h-5 text-brand-forest flex-shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-brand-graphite/60 uppercase tracking-wide">
                Locality
              </div>
              <div className="text-sm font-medium text-brand-graphite">
                {locality}
              </div>
            </div>
          </div>
        )}

        {pincode && (
          <div className="flex items-center gap-3 p-3 bg-gradient-to-r from-brand-sky/10 to-brand-beige rounded-lg border border-brand-sky/20">
            <Hash className="w-5 h-5 text-brand-sky flex-shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-brand-graphite/60 uppercase tracking-wide">
                Pincode
              </div>
              <div className="text-sm font-medium text-brand-graphite">
                {pincode}
                {pincode_centroid_distance_km !== undefined && (
                  <span className="ml-2 text-xs text-brand-graphite/60">
                    ({pincode_centroid_distance_km.toFixed(1)} km from centroid)
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
