import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

export default function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 text-red-700 px-4 py-3 flex items-start gap-3">
      <ExclamationTriangleIcon className="h-5 w-5 mt-0.5" />
      <div>
        <p className="text-sm font-semibold">Something went wrong</p>
        <p className="text-sm">{message}</p>
      </div>
    </div>
  )
}
