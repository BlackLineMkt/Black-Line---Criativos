import sys
import json
import uuid
import tempfile
import traceback
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import bl_gerar  # noqa: E402 — must come after sys.path manipulation

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool

app = FastAPI(title="BL Criativos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = ROOT / "output"
HISTORICO_PATH = ROOT / "historico.json"

OUTPUT_DIR.mkdir(exist_ok=True)


def _render_sync(campanha: dict, formatos: list[str]) -> list[dict]:
    """Blocking render — run in threadpool so the event loop stays free."""
    gerados = []
    for fmt in formatos:
        if fmt == "feed":
            out = bl_gerar.render_feed(campanha, OUTPUT_DIR)
            gerados.append({"formato": "feed", "arquivo": out.name})
        elif fmt == "story":
            out = bl_gerar.render_story(campanha, OUTPUT_DIR)
            gerados.append({"formato": "story", "arquivo": out.name})
    return gerados


def _update_historico(entry: dict) -> None:
    historico: list = []
    if HISTORICO_PATH.exists():
        try:
            historico = json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
        except Exception:
            historico = []
    historico.insert(0, entry)
    HISTORICO_PATH.write_text(
        json.dumps(historico, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@app.post("/gerar")
async def gerar(
    imagem: UploadFile = File(...),
    dados: str = Form(...),
):
    # Parse request data — force UTF-8 to avoid Windows cp1252 mis-decoding
    try:
        dados_dict = json.loads(dados.encode('utf-8').decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="'dados' não é um JSON válido.")

    for key in ("nome", "formatos", "copy"):
        if key not in dados_dict:
            raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: '{key}'")

    if not isinstance(dados_dict["copy"], dict):
        raise HTTPException(status_code=400, detail="'copy' deve ser um objeto JSON.")

    if not isinstance(dados_dict["formatos"], list) or not dados_dict["formatos"]:
        raise HTTPException(status_code=400, detail="'formatos' deve ser uma lista não vazia.")

    required_copy = {"tag", "linha1", "bloco_vermelho", "bloco_dourado", "corpo", "cta"}
    missing = required_copy - set(dados_dict["copy"].keys())
    if missing:
        raise HTTPException(status_code=400, detail=f"Campos de copy ausentes: {sorted(missing)}")

    # Save uploaded image to a temp file
    suffix = Path(imagem.filename or "img.jpg").suffix or ".jpg"
    content = await imagem.read()

    tmp_path = Path(tempfile.mktemp(suffix=suffix))
    tmp_path.write_bytes(content)

    try:
        copy_payload = dados_dict["copy"]
        # Ensure corpo is always a list, not a raw string
        if isinstance(copy_payload.get("corpo"), str):
            copy_payload["corpo"] = [l for l in copy_payload["corpo"].split("\n") if l.strip()]
        campanha = {
            "nome": dados_dict["nome"],
            "imagem": str(tmp_path),
            "formatos": dados_dict["formatos"],
            "copy": copy_payload,
            "layout": dados_dict.get("layout", "padrao"),
        }
        gerados = await run_in_threadpool(_render_sync, campanha, dados_dict["formatos"])
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"\n[ERRO /gerar] {repr(exc)}\n{tb}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=f"Erro na geração: {exc!r}")
    finally:
        tmp_path.unlink(missing_ok=True)

    entry = {
        "id": str(uuid.uuid4()),
        "nome": dados_dict["nome"],
        "data": datetime.now().isoformat(timespec="seconds"),
        "formatos": dados_dict["formatos"],
        "arquivos": [g["arquivo"] for g in gerados],
    }
    _update_historico(entry)

    return {"gerados": gerados, "entrada": entry}


@app.get("/download/{filename}")
async def download(filename: str):
    safe_name = Path(filename).name  # strip any path traversal
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(str(file_path), media_type="image/png", filename=safe_name)


@app.get("/historico")
async def historico():
    if not HISTORICO_PATH.exists():
        return []
    try:
        return json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
