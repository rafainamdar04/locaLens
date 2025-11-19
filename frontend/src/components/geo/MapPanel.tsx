import React, { useEffect, useRef } from 'react'
import { MapPin } from 'lucide-react'

type MapPanelProps = {
  here_coords?: { lat: number; lng: number }
  ml_coords?: { lat: number; lng: number }
  distance_km?: number
  city_match?: boolean
  pincode_match?: boolean
  here_confidence?: number
}

export function MapPanel({
  here_coords,
  ml_coords,
  distance_km,
  city_match,
  pincode_match,
  here_confidence
}: MapPanelProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

  useEffect(() => {
    if (!mapRef.current || !here_coords) return

    // Initialize HERE Maps
    if (!(window as any).H) {
      const script = document.createElement('script')
      script.src = 'https://js.api.here.com/v3/3.1/mapsjs-core.js'
      script.async = true
      script.onload = () => {
        loadMapDependencies()
      }
      document.head.appendChild(script)
    } else {
      initializeMap()
    }

    function loadMapDependencies() {
      const scripts = [
        'https://js.api.here.com/v3/3.1/mapsjs-service.js',
        'https://js.api.here.com/v3/3.1/mapsjs-ui.js',
        'https://js.api.here.com/v3/3.1/mapsjs-mapevents.js'
      ]

      let loaded = 0
      scripts.forEach(src => {
        const script = document.createElement('script')
        script.src = src
        script.async = true
        script.onload = () => {
          loaded++
          if (loaded === scripts.length) {
            // Load CSS
            const link = document.createElement('link')
            link.rel = 'stylesheet'
            link.href = 'https://js.api.here.com/v3/3.1/mapsjs-ui.css'
            document.head.appendChild(link)
            initializeMap()
          }
        }
        document.head.appendChild(script)
      })
    }

    function initializeMap() {
      if (!mapRef.current || !here_coords || mapInstanceRef.current) return

      const H = (window as any).H
      const platform = new H.service.Platform({
        apikey: '0Ujnzdn36SL3-czu110iMsG1kE3JzEV6JNRWW0Ps3rQ'
      })

      const defaultLayers = platform.createDefaultLayers()
      const map = new H.Map(
        mapRef.current,
        defaultLayers.vector.normal.map,
        {
          zoom: ml_coords ? 12 : 14,
          center: here_coords
        }
      )

      const behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map))
      const ui = H.ui.UI.createDefault(map, defaultLayers)

      // HERE pin (mint accent)
      const hereSvg = `<svg width="32" height="40" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 0C7.163 0 0 7.163 0 16c0 12 16 24 16 24s16-12 16-24c0-8.837-7.163-16-16-16z" fill="#10B981"/>
        <circle cx="16" cy="16" r="6" fill="white"/>
      </svg>`
      const hereIcon = new H.map.Icon(hereSvg)
      const hereMarker = new H.map.Marker(here_coords, { icon: hereIcon })
      map.addObject(hereMarker)

      // Confidence circle around HERE point
      if (here_confidence !== undefined) {
        const radiusMeters = (1 - here_confidence) * 5000 // Max 5km radius for low confidence
        const circle = new H.map.Circle(here_coords, radiusMeters, {
          style: {
            strokeColor: 'rgba(16, 185, 129, 0.4)',
            fillColor: 'rgba(16, 185, 129, 0.1)',
            lineWidth: 2
          }
        })
        map.addObject(circle)
      }

      // ML pin (soft blue accent)
      if (ml_coords) {
        const mlSvg = `<svg width="32" height="40" xmlns="http://www.w3.org/2000/svg">
          <path d="M16 0C7.163 0 0 7.163 0 16c0 12 16 24 16 24s16-12 16-24c0-8.837-7.163-16-16-16z" fill="#A7D0E6"/>
          <circle cx="16" cy="16" r="6" fill="white"/>
        </svg>`
        const mlIcon = new H.map.Icon(mlSvg)
        const mlMarker = new H.map.Marker(ml_coords, { icon: mlIcon })
        map.addObject(mlMarker)

        // Dashed mismatch line
        const lineString = new H.geo.LineString()
        lineString.pushPoint(here_coords)
        lineString.pushPoint(ml_coords)
        const line = new H.map.Polyline(lineString, {
          style: {
            strokeColor: '#D97A4A',
            lineWidth: 3,
            lineDash: [5, 5]
          }
        })
        map.addObject(line)

        // Zoom to show both markers
        const group = new H.map.Group()
        group.addObjects([hereMarker, mlMarker])
        map.getViewModel().setLookAtData({ bounds: group.getBoundingBox() })
      }

      mapInstanceRef.current = map
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.dispose()
        mapInstanceRef.current = null
      }
    }
  }, [here_coords, ml_coords, here_confidence])

  if (!here_coords) {
    return (
      <div className="card p-6 text-center text-brand-graphite/60">
        <MapPin className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p>No geospatial coordinates available</p>
      </div>
    )
  }

  const getSeverityColor = () => {
    if (!distance_km) return 'bg-gray-400'
    if (distance_km < 3) return 'bg-green-500'
    if (distance_km < 15) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="card overflow-hidden">
      <div ref={mapRef} className="w-full h-96" />
      
      {distance_km !== undefined && (
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${getSeverityColor()}`} />
              <span className="text-sm font-medium text-brand-graphite">
                Mismatch Distance: {distance_km.toFixed(2)} km
              </span>
            </div>
            <div className="flex gap-3 text-xs">
              <span className={city_match ? 'text-green-600' : 'text-red-600'}>
                City: {city_match ? '✓' : '✗'}
              </span>
              <span className={pincode_match ? 'text-green-600' : 'text-red-600'}>
                Pincode: {pincode_match ? '✓' : '✗'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
