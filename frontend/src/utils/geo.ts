export type LatLng = { lat: number; lng: number }

export function isFiniteLatLng(p?: Partial<LatLng> | null): p is LatLng {
  return !!p && Number.isFinite((p as any).lat) && Number.isFinite((p as any).lng)
}

// Haversine distance in kilometers, returns undefined if invalid inputs
export function haversineKmSafe(a?: Partial<LatLng> | null, b?: Partial<LatLng> | null): number | undefined {
  if (!isFiniteLatLng(a) || !isFiniteLatLng(b)) return undefined
  const R = 6371
  const dLat = ((b.lat - a.lat) * Math.PI) / 180
  const dLon = ((b.lng - a.lng) * Math.PI) / 180
  const s1 = Math.sin(dLat / 2)
  const s2 = Math.sin(dLon / 2)
  const aa = s1 * s1 + Math.cos((a.lat * Math.PI) / 180) * Math.cos((b.lat * Math.PI) / 180) * s2 * s2
  const c = 2 * Math.atan2(Math.sqrt(aa), Math.sqrt(1 - aa))
  const d = R * c
  return Number.isFinite(d) ? d : undefined
}
