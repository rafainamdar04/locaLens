# Geospatial Components Documentation

## Overview
Professional, map-focused React components for visualizing address geocoding results, spatial analysis, and administrative boundaries.

---

## Components

### 1. MapPanel
Interactive HERE Maps component showing geocoding comparison.

**Props:**
```typescript
{
  here_coords?: { lat: number; lng: number }
  ml_coords?: { lat: number; lng: number }
  distance_km?: number
  city_match?: boolean
  pincode_match?: boolean
  here_confidence?: number
}
```

**Features:**
- Dual-pin display (HERE: mint, ML: sky blue)
- Dashed mismatch line between pins
- Confidence circle around HERE pin
- Distance badge with severity colors
- City/Pincode match indicators

**Usage:**
```tsx
<MapPanel
  here_coords={{ lat: 12.9716, lng: 77.5946 }}
  ml_coords={{ lat: 12.9750, lng: 77.6000 }}
  distance_km={0.5}
  city_match={true}
  pincode_match={true}
  here_confidence={0.92}
/>
```

---

### 2. GeospatialInsightsSummary
Human-friendly summary card with confidence badge.

**Props:**
```typescript
{
  integrity_score?: number        // 0-1 range
  here_confidence?: number        // 0-1 range
  distance_km?: number
  consensus_score?: number        // 0-1 range
  city_match?: boolean
  pincode_match?: boolean
}
```

**Features:**
- Auto-generates 1-2 sentence summary
- HIGH/MEDIUM/LOW confidence badge
- Key metrics display
- Gradient background

**Usage:**
```tsx
<GeospatialInsightsSummary
  integrity_score={0.85}
  here_confidence={0.92}
  distance_km={0.5}
  consensus_score={0.88}
  city_match={true}
  pincode_match={true}
/>
```

---

### 3. AdministrativeHierarchy
Displays administrative boundaries and location details.

**Props:**
```typescript
{
  state?: string
  district?: string
  sub_district?: string
  locality?: string
  pincode?: string
  pincode_centroid_distance_km?: number
}
```

**Features:**
- Icon-based hierarchy display
- State → District → Sub-District → Locality
- Pincode with centroid distance
- Graceful fallback for missing data

**Usage:**
```tsx
<AdministrativeHierarchy
  state="Karnataka"
  district="Bangalore Urban"
  locality="Indiranagar"
  pincode="560038"
  pincode_centroid_distance_km={1.2}
/>
```

---

### 4. RadarChart
4-axis spatial quality visualization.

**Props:**
```typescript
{
  city_match?: boolean
  pincode_match?: boolean
  boundary_check?: boolean
  reachability_score?: number     // 0-1 range
}
```

**Features:**
- SVG-based radar chart
- 4 axes: City, Pincode, Boundary, Reachability
- Color-coded by score (green/yellow/red)
- Overall score display

**Usage:**
```tsx
<RadarChart
  city_match={true}
  pincode_match={true}
  boundary_check={true}
  reachability_score={0.85}
/>
```

---

### 5. MLvsHEREComparison
Side-by-side comparison of interpretation methods.

**Props:**
```typescript
{
  ml_results?: {
    pincode?: string
    city?: string
    state?: string
    similarity?: number
    coordinates?: { lat: number; lng: number }
  }
  here_results?: {
    primary_result?: {
      title?: string
      position?: { lat: number; lng: number }
      scoring?: { queryScore?: number }
      address?: {
        city?: string
        state?: string
        postalCode?: string
      }
    }
  }
}
```

**Features:**
- Dual-panel layout (text-based vs map-based)
- Coordinates display
- Confidence progress bars
- Explanatory notes

**Usage:**
```tsx
<MLvsHEREComparison
  ml_results={{
    city: "Bangalore",
    state: "Karnataka",
    pincode: "560001",
    similarity: 0.89,
    coordinates: { lat: 12.9716, lng: 77.5946 }
  }}
  here_results={{
    primary_result: {
      position: { lat: 12.9716, lng: 77.5946 },
      scoring: { queryScore: 0.92 },
      address: {
        city: "Bengaluru",
        state: "Karnataka",
        postalCode: "560001"
      }
    }
  }}
/>
```

---

### 6. SpatialHealthTag
Prominent confidence badge based on mismatch distance.

**Props:**
```typescript
{
  distance_km?: number
}
```

**Features:**
- HIGH: <3km (green)
- MEDIUM: 3-15km (yellow)
- LOW: >15km (red)
- Human-readable descriptions
- Exact distance display

**Usage:**
```tsx
<SpatialHealthTag distance_km={0.5} />
```

---

### 7. Timeline
Vertical processing timeline showing interpretation steps.

**Props:**
```typescript
{
  raw_address?: string
  cleaned?: string
  pincode_detected?: string
  here_result?: string
  ml_result?: string
  mismatch_detected?: boolean
  consensus?: string
  trace?: string[]              // Optional backend trace
}
```

**Features:**
- Vertical step-by-step display
- Color-coded status (completed/warning/error)
- Supports backend trace array
- Step count summary

**Usage:**
```tsx
<Timeline
  raw_address="123 MG Road Bangalore"
  cleaned="123, MG Road, Bengaluru, 560001"
  pincode_detected="560001"
  here_result="MG Road, Bengaluru"
  ml_result="Bengaluru"
  mismatch_detected={false}
  consensus="high"
/>
```

---

## Design System

### Colors
- **Mint (Forest Green)**: #2F4D35 / `brand-forest`
- **Terracotta**: #D97A4A / `brand-terracotta`
- **Sky Blue**: #A7D0E6 / `brand-sky`
- **Warm Beige**: #F5F3EE / `brand-beige`
- **Soft Graphite**: #3D3D3D / `brand-graphite`

### Spacing Scale
- Small: 16px (gap-4)
- Medium: 24px (gap-6)
- Large: 32px (gap-8)

### Typography
- **Font**: Inter (Google Fonts)
- **Heading**: font-semibold, text-lg
- **Body**: text-sm, text-brand-graphite
- **Caption**: text-xs, text-gray-500

### Cards
- Border radius: rounded-xl
- Shadow: shadow-sm
- Border: border border-gray-100
- Background: bg-white

---

## Integration Example

```tsx
import { MapPanel } from '../components/geo/MapPanel'
import { GeospatialInsightsSummary } from '../components/geo/GeospatialInsightsSummary'
import { AdministrativeHierarchy } from '../components/geo/AdministrativeHierarchy'
import { RadarChart } from '../components/geo/RadarChart'
import { MLvsHEREComparison } from '../components/geo/MLvsHEREComparison'
import { SpatialHealthTag } from '../components/geo/SpatialHealthTag'
import { Timeline } from '../components/geo/Timeline'

function Results({ event }) {
  return (
    <div className="space-y-8">
      <SpatialHealthTag distance_km={event.distance_km} />
      
      <GeospatialInsightsSummary
        integrity_score={event.integrity.score / 100}
        here_confidence={event.here_results.confidence}
        distance_km={event.distance_km}
      />
      
      <MapPanel
        here_coords={event.here_results.primary_result.position}
        ml_coords={event.ml_results.top_result}
        distance_km={event.distance_km}
      />
      
      <div className="grid gap-6 lg:grid-cols-3">
        <AdministrativeHierarchy {...event.admin_data} />
        <RadarChart {...event.quality_metrics} />
      </div>
      
      <MLvsHEREComparison
        ml_results={event.ml_results}
        here_results={event.here_results}
      />
      
      <Timeline {...event.processing_steps} />
    </div>
  )
}
```

---

## Backwards Compatibility

All components:
- ✅ Handle missing/undefined props gracefully
- ✅ Display fallback UI when data unavailable
- ✅ Use optional chaining for nested properties
- ✅ TypeScript types allow undefined for all props
- ✅ No breaking changes to existing API contracts

---

## Performance Considerations

### MapPanel
- Lazy-loads HERE Maps SDK scripts
- Initializes map only once (useRef)
- Disposes map instance on unmount
- Debounces coordinate updates

### RadarChart
- Pure SVG (no external libraries)
- Lightweight calculation
- Memoizable component

### Timeline
- Virtual scrolling for long traces (future)
- Conditional rendering of steps

---

## Testing Checklist

- [ ] MapPanel renders with both pins
- [ ] MapPanel shows confidence circle
- [ ] MapPanel displays distance badge
- [ ] GeospatialInsightsSummary generates correct summary
- [ ] AdministrativeHierarchy displays all available fields
- [ ] RadarChart renders all 4 axes
- [ ] MLvsHEREComparison shows both panels
- [ ] SpatialHealthTag shows correct confidence level
- [ ] Timeline displays all processing steps
- [ ] All components handle missing data gracefully
- [ ] Responsive layout works on mobile/tablet/desktop

---

## Future Enhancements

### MapPanel
- Add zoom controls
- Marker clustering for multiple results
- Route drawing for delivery paths
- Satellite/terrain view toggle

### Timeline
- Expandable step details
- Duration estimates per step
- Error state visualization
- Export timeline as JSON

### RadarChart
- Customizable axis labels
- Animation on render
- Tooltip on hover
- Export as SVG/PNG

---

## Troubleshooting

### MapPanel not rendering?
- Check HERE API key is configured
- Verify coordinates are valid (lat/lng)
- Check browser console for script loading errors
- Ensure `mapRef` div has height set

### Components showing "N/A"?
- This is expected when backend data is missing
- Check API response structure matches props
- Verify optional chaining is working
- Review backend logs for processing errors

### Styling issues?
- Ensure Tailwind is configured correctly
- Check brand colors are in `tailwind.config.cjs`
- Verify Inter font is loaded
- Clear browser cache and rebuild

---

## Support

For issues or questions:
1. Check `ENHANCEMENT_SUMMARY.md` for implementation details
2. Review backend logs for data availability
3. Test with `test_backend_compatibility.py`
4. Verify TypeScript types match API responses
