import React from 'react'

interface AnimatedMapLinesProps {
  className?: string
}

export const AnimatedMapLines: React.FC<AnimatedMapLinesProps> = ({ className = '' }) => {
  // Generate random curved paths that look like shipping routes
  const generatePath = (index: number) => {
    const startX = Math.random() * 100
    const startY = Math.random() * 100
    const endX = Math.random() * 100
    const endY = Math.random() * 100

    // Create a curved path with control points
    const controlX1 = (startX + endX) / 2 + (Math.random() - 0.5) * 30
    const controlY1 = (startY + endY) / 2 + (Math.random() - 0.5) * 30
    const controlX2 = (startX + endX) / 2 + (Math.random() - 0.5) * 30
    const controlY2 = (startY + endY) / 2 + (Math.random() - 0.5) * 30

    return `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`
  }

  const paths = Array.from({ length: 8 }, (_, i) => ({
    id: i,
    path: generatePath(i),
    delay: Math.random() * 3,
    duration: 4 + Math.random() * 4
  }))

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      <style>
        {`
          @keyframes routeFlow {
            0%, 100% {
              opacity: 0.2;
              stroke-dashoffset: 0;
            }
            50% {
              opacity: 0.4;
              stroke-dashoffset: -20;
            }
          }
        `}
      </style>
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4A7C59" stopOpacity="0.25" />
            <stop offset="50%" stopColor="#6B8F7C" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#4A7C59" stopOpacity="0.25" />
          </linearGradient>
        </defs>

        {paths.map(({ id, path, delay, duration }) => (
          <path
            key={id}
            d={path}
            stroke="url(#routeGradient)"
            strokeWidth="1.2"
            fill="none"
            strokeLinecap="round"
            strokeDasharray="4,8"
            style={{
              animation: `routeFlow ${duration}s ease-in-out infinite`,
              animationDelay: `${delay}s`,
            }}
          />
        ))}
      </svg>
    </div>
  )
}