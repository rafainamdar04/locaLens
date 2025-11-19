import { Outlet } from 'react-router-dom'

export default function App() {
  return (
    <div className="relative min-h-screen bg-[#FAF7F0]">
      <div className="relative z-10">
        <Outlet />
      </div>
    </div>
  )
}
