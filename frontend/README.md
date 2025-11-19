# LocaLens Frontend

Clean, modern React + Vite + Tailwind UI for the LocaLens geospatial AI tool.

## Tech Stack
- React + Vite + TypeScript
- Tailwind CSS (mint-first palette)
- Framer Motion (soft transitions)
- React Query (API calls / caching)
- Heroicons
- Headless UI (collapsible sections)

## Getting Started

```bash
# From repo root
cd frontend

# Install deps
npm install

# Start dev server
npm run dev

# Open
http://127.0.0.1:5173
```

Backend should be running at `http://127.0.0.1:8000` (CORS already open).

## Branding & Styling
- Primary: Mint Green `#4ADE80`
- Accents: `#D1FAE5` (mint-100), `#38BDF8` (sky-400)
- Background: off-white `#FAFAFA`
- Cards: white, `rounded-2xl`, `shadow-md`, `border-gray-100`
- Typography: Inter

## Pages
- Home: centered input card, textarea + “Process Address” button
- Results: collapsible cards for each section (Cleaned Address, Integrity, ML, HERE, Diagnostics, Confidence, Anomalies, Self-Heal, Raw event)

## Components
- Card, MetricBadge, CollapseSection, ConfidenceGauge, LoadingSpinner, ErrorBanner, Timeline

## Tips
- Update API base URL in `src/api/client.ts` if backend host/port differs
- Adjust thresholds/color rules in UI if your backend logic changes
- Build for production: `npm run build` then `npm run preview`
