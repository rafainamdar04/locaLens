type Item = { time?: string; title: string; description?: string }

export default function Timeline({ items = [] as Item[] }) {
  if (!items.length) return <p className="text-sm text-gray-500">No self-healing actions performed.</p>
  return (
    <ol className="relative ml-3 border-l border-gray-200">
      {items.map((it, i) => (
        <li key={i} className="mb-6 ml-4">
          <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-brand-mint ring-4 ring-brand-mint100" />
          <time className="mb-1 text-xs font-medium text-gray-500">{it.time || ''}</time>
          <h4 className="text-sm font-semibold">{it.title}</h4>
          {it.description && <p className="text-sm text-gray-600">{it.description}</p>}
        </li>
      ))}
    </ol>
  )
}
