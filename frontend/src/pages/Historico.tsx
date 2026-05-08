import { useState, useEffect } from 'react'

interface HistoricoEntry {
  id: string
  nome: string
  data: string
  formatos: string[]
  arquivos: string[]
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function FormatBadge({ fmt }: { fmt: string }) {
  const styles: Record<string, string> = {
    feed:  'text-blue-400 bg-blue-500/10 border-blue-500/20',
    story: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  }
  return (
    <span
      className={`text-[10px] font-mono px-1.5 py-0.5 rounded border uppercase ${styles[fmt] ?? 'text-bl-muted border-bl-border'}`}
    >
      {fmt}
    </span>
  )
}

export default function Historico() {
  const [entries, setEntries] = useState<HistoricoEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/historico')
      .then((r) => {
        if (!r.ok) throw new Error('Erro ao carregar histórico.')
        return r.json()
      })
      .then((data: HistoricoEntry[]) => {
        setEntries(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-8 py-5 border-b border-bl-border">
        <div className="flex items-baseline gap-3">
          <h1 className="text-lg font-semibold text-bl-text">Histórico</h1>
          {!loading && (
            <span className="text-xs text-bl-muted font-mono">
              {entries.length} {entries.length === 1 ? 'campanha' : 'campanhas'}
            </span>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3 text-bl-muted">
              <svg className="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              <span className="text-sm">Carregando...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {error}
          </div>
        )}

        {!loading && !error && entries.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#2a2a2a" strokeWidth="1.5">
              <circle cx="12" cy="12" r="9" />
              <polyline points="12 7 12 12 15 15" />
            </svg>
            <div className="text-center">
              <p className="text-bl-text text-sm font-medium">Nenhuma campanha gerada ainda</p>
              <p className="text-bl-muted text-xs mt-1">
                Gere seu primeiro criativo em{' '}
                <a href="/nova-campanha" className="text-bl-gold hover:underline">
                  Nova Campanha
                </a>
              </p>
            </div>
          </div>
        )}

        {!loading && !error && entries.length > 0 && (
          <div className="flex flex-col gap-3 max-w-3xl">
            {entries.map((entry) => (
              <div key={entry.id} className="card p-5">
                <div className="flex items-start justify-between gap-4">
                  {/* Left info */}
                  <div className="flex flex-col gap-2 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-bl-text text-sm">
                        {entry.nome}
                      </span>
                      <div className="flex gap-1.5">
                        {entry.formatos.map((f) => (
                          <FormatBadge key={f} fmt={f} />
                        ))}
                      </div>
                    </div>
                    <span className="text-xs text-bl-muted font-mono">
                      {formatDate(entry.data)}
                    </span>
                    {/* File list */}
                    <div className="flex flex-col gap-1 mt-1">
                      {entry.arquivos.map((arq) => (
                        <span key={arq} className="text-xs text-bl-muted font-mono truncate">
                          {arq}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Download buttons */}
                  <div className="flex flex-col gap-2 flex-shrink-0">
                    {entry.arquivos.map((arq) => {
                      const isFeed = arq.includes('feed')
                      return (
                        <a
                          key={arq}
                          href={`/api/download/${arq}`}
                          download={arq}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-bl-gold border border-bl-gold/30 hover:bg-bl-gold/10 transition-colors whitespace-nowrap"
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="7 10 12 15 17 10" />
                            <line x1="12" y1="15" x2="12" y2="3" />
                          </svg>
                          {isFeed ? 'Feed' : 'Story'}
                        </a>
                      )
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
