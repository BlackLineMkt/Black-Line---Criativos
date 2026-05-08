import { NavLink, useLocation } from 'react-router-dom'

const navItems = [
  {
    label: 'Nova Campanha',
    to: '/nova-campanha',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <line x1="12" y1="8" x2="12" y2="16" />
        <line x1="8" y1="12" x2="16" y2="12" />
      </svg>
    ),
  },
  {
    label: 'Histórico',
    to: '/historico',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" />
        <polyline points="12 7 12 12 15 15" />
      </svg>
    ),
  },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside
      className="w-56 flex-shrink-0 flex flex-col bg-bl-card border-r border-bl-border"
      style={{ minHeight: '100vh' }}
    >
      {/* Logo */}
      <div className="px-5 pt-7 pb-6 border-b border-bl-border">
        <div className="flex flex-col gap-0.5">
          <span className="text-xs font-mono text-bl-muted tracking-[0.2em] uppercase">
            Black Line
          </span>
          <span
            className="text-xl font-bold tracking-tight"
            style={{ color: '#C69A3B', letterSpacing: '-0.01em' }}
          >
            CRIATIVOS
          </span>
        </div>
        <div
          className="mt-3 h-px w-8"
          style={{ background: '#C69A3B', opacity: 0.4 }}
        />
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5">
        <span className="px-2 mb-2 text-[10px] font-medium text-bl-muted uppercase tracking-widest">
          Menu
        </span>
        {navItems.map((item) => {
          const isActive =
            location.pathname === item.to ||
            (item.to === '/nova-campanha' && location.pathname === '/')

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={[
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                isActive
                  ? 'text-bl-gold bg-bl-gold/10 border border-bl-gold/20'
                  : 'text-bl-muted hover:text-bl-text hover:bg-bl-card-2',
              ].join(' ')}
            >
              <span className={isActive ? 'text-bl-gold' : ''}>{item.icon}</span>
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-bl-border">
        <p className="text-[10px] text-bl-muted font-mono">
          BL Criativos v0.1
        </p>
        <p className="text-[10px] text-bl-muted/60 font-mono">
          @blackline.mkt
        </p>
      </div>
    </aside>
  )
}
