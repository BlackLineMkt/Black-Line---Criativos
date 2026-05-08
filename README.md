# BL Criativos

Gerador de criativos da Black Line Agency — identidade INK RIOT.

---

## Pré-requisitos

- **Python 3.10+** com Pillow instalado
- **Node.js 18+**
- Fontes na pasta `fonts/` (veja `bl_gerar.py` para instruções)

---

## Iniciar o backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend disponível em: http://localhost:8000

---

## Iniciar o frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Acessar

http://localhost:5173

---

## Estrutura

```
D:\BL Criativos\
├── bl_gerar.py          # gerador Python (Pillow) — não editar
├── campanha.json        # exemplo de campanha
├── output/              # PNGs gerados
├── historico.json       # histórico de campanhas (criado automaticamente)
├── fonts/               # fontes TTF/OTF (copiar manualmente)
├── backend/
│   ├── main.py          # FastAPI — POST /gerar, GET /download, GET /historico
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.tsx
        ├── pages/
        │   ├── NovaCampanha.tsx
        │   └── Historico.tsx
        └── components/
            └── Sidebar.tsx
```

---

## Fontes necessárias (copiar para `fonts/`)

| Arquivo | Fonte |
|---|---|
| `NimbusRoman-Bold.otf` | URW Base35 / TeX Live |
| `Poppins-Bold.ttf` | Google Fonts |
| `Poppins-Medium.ttf` | Google Fonts |
| `LiberationMono-Bold.ttf` | Liberation Fonts (RedHat) |
| `LiberationMono-Regular.ttf` | Liberation Fonts (RedHat) |

Sem as fontes, o script usa o fallback padrão do Pillow e imprime avisos.
