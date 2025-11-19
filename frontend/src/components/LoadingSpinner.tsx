export default function LoadingSpinner() {
  return (
    <div className="flex items-center gap-3">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-[#4A7C59] border-t-transparent" />
      <span className="text-sm text-[#6B6B6B]">Processing...</span>
    </div>
  )
}
