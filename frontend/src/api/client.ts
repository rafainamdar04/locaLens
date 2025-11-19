import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000 // allow up to 120s to handle first-call warmups
})

export type Addon = 'deliverability' | 'property_risk' | 'fraud' | 'neighborhood' | 'safety'

export type EventAnomaly = {
  detected: boolean
  reasons?: string[]
  details?: Record<string, any>
}

export type EventPayload = {
  timestamp: number
  raw_address: string
  cleaned: string
  cleaned_address?: string
  cleaned_components?: Record<string, any>
  integrity?: Record<string, any>
  ml_results?: Record<string, any>
  here_results?: Record<string, any>
  // New canonical key for geospatial checks; legacy fallback geospatial_checks remains
  checks?: Record<string, any>
  geospatial_checks?: Record<string, any>
  // Canonical fused confidence scalar; legacy fused_confidence retained
  confidence?: number
  fused_confidence?: number
  anomaly?: EventAnomaly
  anomaly_detected?: boolean
  anomaly_reasons?: string[]
  anomaly_details?: Record<string, any>
  self_heal?: Record<string, any> | null
  self_heal_actions?: Record<string, any> | null
  addons?: Partial<Record<Addon, Record<string, any>>>
  health: 'OK' | 'UNCERTAIN' | 'BAD'
  processing_time_ms: number
  success: true
  trace?: string[]
  summary?: {
    human_readable?: string
  }
  // Additional data for new UI structure
  routing_data?: Record<string, any>
  places_data?: Record<string, any>
  validation_data?: Record<string, any>
  delivery_navigation?: Record<string, any>
  safety_assessment?: Record<string, any>
}

export type AddressResponse = {
  success: boolean
  processing_time_ms: number
  event: EventPayload
}

export async function processAddress(
  raw: string,
  addons?: Addon[] | 'all' | 'none'
): Promise<AddressResponse> {
  const params: Record<string, string> = {}
  if (addons && addons !== 'none') {
    params.addons = Array.isArray(addons) ? addons.join(',') : addons
  } else if (addons === 'none') {
    params.addons = 'none'
  }
  const { data } = await api.post('/process_v3', { raw_address: raw }, { params })
  return data
}

export async function getDeliveryNavigation(
  destination: { lat: number; lon: number },
  transportMode: string = 'car',
  serviceType: string = 'standard'
): Promise<any> {
  const { data } = await api.post('/delivery-navigation', {
    destination,
    transport_mode: transportMode,
    service_type: serviceType
  })
  return data
}

export async function getSafetyAssessment(lat: number, lon: number): Promise<any> {
  const { data } = await api.post('/residential-safety', {
    lat,
    lon
  })
  return data
}
