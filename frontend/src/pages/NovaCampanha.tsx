import { useState, useRef, useCallback } from 'react'

interface CopyFields {
  tag: string
  linha1: string
  bloco_vermelho: string
  bloco_dourado: string
  corpo: string
  cta: string
}

interface GeradoFile {
  formato: string
  arquivo: string
}

type Status = 'idle' | 'gerando' | 'concluido' | 'erro'

const INITIAL_COPY: CopyFields = {
  tag: 'BLACK LINE AGENCY // MKTG',
  linha1: '',
  bloco_vermelho: '',
  bloco_dourado: '',
  corpo: '',
  cta: '',
}

// ── Subcomponents ────────────────────────────────────────────────────────────

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  )
}

function StatusBadge({ status, erro }: { status: Status; erro: string | null }) {
  if (status === 'idle') return null

  const config = {
    gerando: {
      bg: 'bg-bl-gold/10 border-bl-gold/30',
      dot: 'bg-bl-gold animate-pulse',
      text: 'text-bl-gold',
      label: 'Gerando...',
    },
    concluido: {
      bg: 'bg-emerald-500/10 border-emerald-500/30',
      dot: 'bg-emerald-500',
      text: 'text-emerald-400',
      label: 'Concluído',
    },
    erro: {
      bg: 'bg-red-500/10 border-red-500/30',
      dot: 'bg-red-500',
      text: 'text-red-400',
      label: erro || 'Erro na geração',
    },
  }[status]

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm ${config.bg}`}>
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${config.dot}`} />
      <span className={`font-medium ${config.text}`}>{config.label}</span>
    </div>
  )
}

function LivePreview({
  previewUrl,
  copy,
  formato,
  hasImage,
}: {
  previewUrl: string | null
  copy: CopyFields
  formato: 'feed' | 'story'
  hasImage: boolean
}) {
  const isStory = formato === 'story'
  const aspectClass = isStory ? 'aspect-[9/16]' : 'aspect-square'

  const corpoLines = copy.corpo.split('\n').filter((l) => l.trim())

  return (
    <div
      className={`relative overflow-hidden rounded-lg w-full ${aspectClass} bg-gray-900`}
      style={{
        backgroundImage: previewUrl ? `url(${previewUrl})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black/65" />

      {/* Content */}
      <div className="absolute inset-0 flex flex-col p-4 gap-2 overflow-hidden">
        {/* Tag */}
        {copy.tag && (
          <div className="inline-flex">
            <span
              className="text-[9px] font-mono px-2 py-1 rounded"
              style={{ background: '#0D0D0D', color: '#C69A3B' }}
            >
              {copy.tag}
            </span>
          </div>
        )}

        {/* Linha 1 */}
        {copy.linha1 && (
          <h2
            className="font-bold leading-tight text-white"
            style={{ fontSize: isStory ? '14px' : '16px', textShadow: '2px 2px 0 #000' }}
          >
            {copy.linha1}
          </h2>
        )}

        {/* Bloco Vermelho */}
        {copy.bloco_vermelho && (
          <div
            className="text-white font-bold text-center py-1.5 px-2 rounded text-xs"
            style={{ background: '#BE1919' }}
          >
            {copy.bloco_vermelho}
          </div>
        )}

        {/* Bloco Dourado */}
        {copy.bloco_dourado && (
          <div
            className="font-bold text-xs py-1 px-2 rounded inline-flex"
            style={{ background: '#C69A3B', color: '#0D0D0D' }}
          >
            {copy.bloco_dourado}
          </div>
        )}

        {/* Divider */}
        {(copy.bloco_dourado || copy.bloco_vermelho) && corpoLines.length > 0 && (
          <div className="h-px w-full" style={{ background: '#2a2a2a' }} />
        )}

        {/* Corpo */}
        {corpoLines.length > 0 && (
          <div className="flex flex-col gap-0.5">
            {corpoLines.slice(0, 4).map((line, i) => (
              <p key={i} className="text-gray-300 leading-snug" style={{ fontSize: '9px' }}>
                {line}
              </p>
            ))}
          </div>
        )}

        {/* CTA */}
        {copy.cta && (
          <div
            className="font-mono text-[9px] px-2 py-1 rounded inline-flex mt-auto"
            style={{ background: '#0D0D0D', color: '#C69A3B' }}
          >
            {copy.cta}
          </div>
        )}

        {/* Watermark */}
        <div
          className="text-center font-mono mt-auto"
          style={{ fontSize: '7px', color: '#666' }}
        >
          @blackline.mkt
        </div>
      </div>

      {/* Empty state overlay */}
      {!hasImage && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-bl-muted mb-1" style={{ fontSize: '28px' }}>
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#666"
                strokeWidth="1.5"
                className="mx-auto"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
            <p className="text-bl-muted text-xs">Sem imagem</p>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function NovaCampanha() {
  const [nome, setNome] = useState('')
  const [imagem, setImagem] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [formatos, setFormatos] = useState({ feed: true, story: false })
  const [copy, setCopy] = useState<CopyFields>(INITIAL_COPY)
  const [status, setStatus] = useState<Status>('idle')
  const [gerados, setGerados] = useState<GeradoFile[]>([])
  const [erro, setErro] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [previewFormato, setPreviewFormato] = useState<'feed' | 'story'>('feed')

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) return
    setImagem(file)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(URL.createObjectURL(file))
    setStatus('idle')
    setGerados([])
    setErro(null)
  }, [previewUrl])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const setCopyField = (field: keyof CopyFields) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => setCopy((prev) => ({ ...prev, [field]: e.target.value }))

  const toggleFormato = (fmt: 'feed' | 'story') => {
    setFormatos((prev) => {
      const next = { ...prev, [fmt]: !prev[fmt] }
      // Sync preview tab
      if (!next[fmt] && previewFormato === fmt) {
        setPreviewFormato(fmt === 'feed' ? 'story' : 'feed')
      }
      return next
    })
  }

  const handleGenerate = async () => {
    if (!nome.trim()) { setErro('Informe o nome da campanha.'); return }
    if (!imagem) { setErro('Selecione uma imagem de fundo.'); return }
    const selectedFormatos = (Object.keys(formatos) as ('feed' | 'story')[]).filter(
      (k) => formatos[k],
    )
    if (selectedFormatos.length === 0) {
      setErro('Selecione ao menos um formato.')
      return
    }

    const corpoLines = copy.corpo.split('\n').filter((l) => l.trim())
    const dados = {
      nome: nome.trim(),
      formatos: selectedFormatos,
      copy: { ...copy, corpo: corpoLines },
    }

    const fd = new FormData()
    fd.append('imagem', imagem)
    fd.append('dados', JSON.stringify(dados))

    setStatus('gerando')
    setErro(null)
    setGerados([])

    try {
      const res = await fetch('/api/gerar', { method: 'POST', body: fd })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Erro desconhecido.' }))
        throw new Error(err.detail || 'Erro na geração.')
      }
      const data = await res.json()
      setGerados(data.gerados)
      setStatus('concluido')
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Erro na geração.')
      setStatus('erro')
    }
  }

  const isGenerating = status === 'gerando'
  const hasImage = !!previewUrl

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-8 py-5 border-b border-bl-border">
        <div className="flex items-baseline gap-3">
          <h1 className="text-lg font-semibold text-bl-text">Nova Campanha</h1>
          <span className="text-xs text-bl-muted font-mono">INK RIOT</span>
        </div>
      </div>

      {/* Body: two-panel layout */}
      <div className="flex-1 overflow-hidden flex gap-0">
        {/* ── Left: Form ────────────────────────────────────────────── */}
        <div className="flex-1 min-w-0 overflow-y-auto px-8 py-6 flex flex-col gap-5">
          {/* Campaign name */}
          <div className="card p-5">
            <Field label="Nome da campanha">
              <input
                className="input-field"
                placeholder="ex: verao-2026-tatoo"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                disabled={isGenerating}
              />
            </Field>
          </div>

          {/* Image upload */}
          <div className="card p-5">
            <label className="label">Imagem de fundo</label>
            <div
              className={[
                'relative border-2 border-dashed rounded-lg transition-colors duration-150 cursor-pointer',
                isDragOver
                  ? 'border-bl-gold bg-bl-gold/5'
                  : hasImage
                  ? 'border-bl-border hover:border-bl-gold/50'
                  : 'border-bl-border hover:border-bl-gold/50',
              ].join(' ')}
              style={{ minHeight: '120px' }}
              onClick={() => !isGenerating && fileInputRef.current?.click()}
              onDrop={isGenerating ? undefined : handleDrop}
              onDragOver={(e) => { e.preventDefault(); if (!isGenerating) setIsDragOver(true) }}
              onDragLeave={() => setIsDragOver(false)}
            >
              {hasImage && imagem ? (
                <div className="flex items-center gap-4 p-4">
                  <img
                    src={previewUrl!}
                    alt="preview"
                    className="w-16 h-16 object-cover rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-bl-text font-medium truncate">{imagem.name}</p>
                    <p className="text-xs text-bl-muted mt-0.5">
                      {(imagem.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                    <button
                      className="mt-2 text-xs text-bl-gold hover:underline"
                      onClick={(e) => {
                        e.stopPropagation()
                        if (!isGenerating) fileInputRef.current?.click()
                      }}
                    >
                      Trocar imagem
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center gap-2 py-8 px-4 text-center">
                  <svg
                    width="28"
                    height="28"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#C69A3B"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  <p className="text-sm text-bl-text">
                    Arraste ou{' '}
                    <span className="text-bl-gold">clique para selecionar</span>
                  </p>
                  <p className="text-xs text-bl-muted">JPG, PNG, WEBP</p>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFile(file)
              }}
              disabled={isGenerating}
            />
          </div>

          {/* Format selection */}
          <div className="card p-5">
            <label className="label">Formatos</label>
            <div className="grid grid-cols-2 gap-3">
              {([
                { key: 'feed', label: 'Feed', sub: '1080 × 1080' },
                { key: 'story', label: 'Story', sub: '1080 × 1920' },
              ] as const).map(({ key, label, sub }) => (
                <button
                  key={key}
                  onClick={() => !isGenerating && toggleFormato(key)}
                  className={[
                    'flex flex-col items-start gap-1 p-3.5 rounded-lg border transition-all duration-150',
                    formatos[key]
                      ? 'border-bl-gold bg-bl-gold/10 text-bl-gold'
                      : 'border-bl-border bg-bl-bg text-bl-muted hover:border-bl-muted',
                  ].join(' ')}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={[
                        'w-4 h-4 rounded flex items-center justify-center border transition-colors',
                        formatos[key]
                          ? 'bg-bl-gold border-bl-gold'
                          : 'border-bl-muted',
                      ].join(' ')}
                    >
                      {formatos[key] && (
                        <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                          <path d="M2 6l3 3 5-5" stroke="#0D0D0D" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      )}
                    </span>
                    <span className="text-sm font-medium">{label}</span>
                  </div>
                  <span className="text-xs font-mono ml-6">{sub}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Copy fields */}
          <div className="card p-5 flex flex-col gap-4">
            <h3 className="text-xs font-semibold text-bl-muted uppercase tracking-widest">
              Copy
            </h3>

            <Field label="Tag">
              <input
                className="input-field font-mono text-xs"
                placeholder="BLACK LINE AGENCY // MKTG"
                value={copy.tag}
                onChange={setCopyField('tag')}
                disabled={isGenerating}
              />
            </Field>

            <Field label="Linha 1 — Headline">
              <input
                className="input-field text-base font-bold"
                placeholder="NÃO PARA. NÃO DESISTE."
                value={copy.linha1}
                onChange={setCopyField('linha1')}
                disabled={isGenerating}
              />
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Bloco Vermelho">
                <input
                  className="input-field"
                  placeholder="TRÁFEGO QUE CONVERTE"
                  value={copy.bloco_vermelho}
                  onChange={setCopyField('bloco_vermelho')}
                  disabled={isGenerating}
                />
              </Field>
              <Field label="Bloco Dourado">
                <input
                  className="input-field"
                  placeholder="VOCÊ ESTÁ NO LUGAR CERTO"
                  value={copy.bloco_dourado}
                  onChange={setCopyField('bloco_dourado')}
                  disabled={isGenerating}
                />
              </Field>
            </div>

            <Field label="Corpo do texto (uma linha por item)">
              <textarea
                className="input-field resize-none font-mono text-xs leading-relaxed"
                rows={4}
                placeholder={'Estratégia feita para estúdios.\nMais agendamentos, menos improviso.\nTambém cuidamos do tráfego pago.'}
                value={copy.corpo}
                onChange={setCopyField('corpo')}
                disabled={isGenerating}
              />
            </Field>

            <Field label="CTA">
              <input
                className="input-field font-mono"
                placeholder="FALE CONOSCO >>"
                value={copy.cta}
                onChange={setCopyField('cta')}
                disabled={isGenerating}
              />
            </Field>
          </div>

          {/* Status + Generate */}
          <div className="flex flex-col gap-3 pb-2">
            <StatusBadge status={status} erro={erro} />
            <button
              className="btn-gold"
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                  </svg>
                  Gerando...
                </span>
              ) : (
                'GERAR CRIATIVOS'
              )}
            </button>
          </div>
        </div>

        {/* ── Right: Preview + Downloads ───────────────────────────── */}
        <div
          className="w-72 xl:w-80 flex-shrink-0 border-l border-bl-border overflow-y-auto px-5 py-6 flex flex-col gap-5"
          style={{ background: '#0a0a0a' }}
        >
          {/* Preview header + format tabs */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-bl-muted uppercase tracking-widest">
                Preview
              </span>
              <div className="flex gap-1">
                {(['feed', 'story'] as const).map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setPreviewFormato(fmt)}
                    className={[
                      'px-2.5 py-1 text-xs rounded font-mono transition-colors',
                      previewFormato === fmt
                        ? 'bg-bl-gold text-black'
                        : 'text-bl-muted hover:text-bl-text',
                    ].join(' ')}
                  >
                    {fmt}
                  </button>
                ))}
              </div>
            </div>
            <LivePreview
              previewUrl={previewUrl}
              copy={copy}
              formato={previewFormato}
              hasImage={hasImage}
            />
            <p className="text-[10px] text-bl-muted text-center mt-2 font-mono">
              Preview aproximado — resultado final gerado pelo Python
            </p>
          </div>

          {/* Generated files */}
          {gerados.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-medium text-bl-muted uppercase tracking-widest">
                  Arquivos Gerados
                </span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              </div>
              <div className="flex flex-col gap-2">
                {gerados.map((g) => {
                  const label = g.formato === 'feed' ? '1080 × 1080' : '1080 × 1920'
                  const badgeColor = g.formato === 'feed' ? 'text-blue-400 bg-blue-500/10 border-blue-500/20' : 'text-purple-400 bg-purple-500/10 border-purple-500/20'
                  return (
                    <div
                      key={g.arquivo}
                      className="card-2 p-3 flex items-center justify-between gap-3"
                    >
                      <div className="flex flex-col gap-1 min-w-0">
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border uppercase self-start ${badgeColor}`}>
                          {g.formato}
                        </span>
                        <span className="text-[10px] text-bl-muted font-mono">{label}</span>
                      </div>
                      <a
                        href={`/api/download/${g.arquivo}`}
                        download={g.arquivo}
                        className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-bl-gold border border-bl-gold/30 hover:bg-bl-gold/10 transition-colors"
                      >
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="7 10 12 15 17 10" />
                          <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                        PNG
                      </a>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
