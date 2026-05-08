import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import NovaCampanha from './pages/NovaCampanha'
import Historico from './pages/Historico'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-full bg-bl-bg">
        <Sidebar />
        <main className="flex-1 min-w-0 flex flex-col overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/nova-campanha" replace />} />
            <Route path="/nova-campanha" element={<NovaCampanha />} />
            <Route path="/historico" element={<Historico />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
