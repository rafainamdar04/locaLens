import { MapPinIcon } from '@heroicons/react/24/outline'

export default function Navbar() {
  return (
    <header className="sticky top-0 z-10 backdrop-blur bg-white/70 border-b border-gray-100">
      <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-brand-mint text-white shadow-md">
            <MapPinIcon className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-lg font-semibold tracking-tight">LocaLens</h1>
            <p className="text-xs text-gray-500">Geospatial AI Insights</p>
          </div>
        </div>
      </div>
    </header>
  )
}
