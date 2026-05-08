"""
Tests for bl_gerar.py — INK RIOT Creative Generator
Run with: python -m pytest tests/ -v
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image as PILImage
from PIL import ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
import bl_gerar as bl


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_synthetic_jpeg(w: int = 300, h: int = 300) -> Path:
    p = Path(tempfile.mktemp(suffix=".jpg"))
    PILImage.new("RGB", (w, h), color=(180, 120, 80)).save(str(p))
    return p


def _blank_canvas(w: int = 400, h: int = 400):
    img = PILImage.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    return img, draw


_COPY = {
    "tag":           "BLACK LINE AGENCY // MKTG",
    "linha1":        "NAO PARA. NAO DESISTE.",
    "bloco_vermelho": "TRAFEGO QUE CONVERTE",
    "bloco_dourado":  "VOCE ESTA NO LUGAR CERTO",
    "corpo":         ["Linha um de corpo texto.", "Linha dois tambem aqui."],
    "cta":           "FALE CONOSCO >>",
}


def _campanha_with_image() -> dict:
    src = _make_synthetic_jpeg(600, 600)
    return {
        "nome": "test-campanha",
        "imagem": str(src),
        "formatos": ["feed", "story"],
        "copy": dict(_COPY),
    }


# ── Task 1: CLI usage ─────────────────────────────────────────────────────────

def test_no_args_exits_with_usage():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "bl_gerar.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "Uso:" in result.stderr or "Uso:" in result.stdout


# ── Task 2: Font loader ───────────────────────────────────────────────────────

def test_load_font_missing_returns_default():
    font = bl.load_font("nimbus", 48)
    assert font is not None


def test_load_font_cache_hit():
    bl._font_cache.clear()
    f1 = bl.load_font("mono_bold", 17)
    f2 = bl.load_font("mono_bold", 17)
    assert f1 is f2


# ── Task 3: Background processing ────────────────────────────────────────────

def test_process_background_dimensions():
    src = _make_synthetic_jpeg()
    result = bl.process_background(str(src), 1080, 1080)
    assert result.size == (1080, 1080)
    assert result.mode == "RGBA"


def test_process_background_darkened():
    src = _make_synthetic_jpeg(300, 300)
    orig_lum = sum(PILImage.open(str(src)).convert("L").getdata()) / (300 * 300 * 255)
    result = bl.process_background(str(src), 300, 300)
    result_lum = sum(result.convert("L").getdata()) / (300 * 300 * 255)
    assert result_lum < orig_lum * 0.85


# ── Task 4: torn_block and drip ───────────────────────────────────────────────

def test_torn_block_fills_center():
    img, draw = _blank_canvas()
    bl.torn_block(draw, 50, 50, 200, 100, (190, 25, 25), seed=0)
    center = img.getpixel((150, 100))
    assert center[:3] == (190, 25, 25), f"Expected red at center, got {center}"


def test_torn_block_returns_bbox():
    img, draw = _blank_canvas()
    bbox = bl.torn_block(draw, 10, 20, 100, 50, (10, 8, 6), seed=1)
    assert bbox == (10, 20, 110, 70)


def test_drip_colors_tip():
    img, draw = _blank_canvas()
    bl.drip(draw, x=200, y0=50, length=80, color=(190, 25, 25), w=4)
    tip = img.getpixel((200, 129))
    assert tip[:3] == (190, 25, 25), f"Expected red at drip tip, got {tip}"


# ── Task 5: splatter and stamp ────────────────────────────────────────────────

def test_splatter_paints_pixels():
    img, draw = _blank_canvas()
    bl.splatter(draw, cx=200, cy=200, color=(10, 8, 6, 220),
                n=80, seed=0, max_dist=60)
    non_white = sum(
        1 for x in range(130, 270) for y in range(130, 270)
        if img.getpixel((x, y))[:3] != (255, 255, 255)
    )
    assert non_white > 0, "splatter painted nothing"


def test_stamp_places_pixels():
    img = PILImage.new("RGBA", (400, 100), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = bl.load_font("mono_bold", 40)
    bl.stamp(draw, "X", font, x=50, y=20, color=(245, 238, 225),
              shadow_color=(10, 8, 6), offset=3)
    pixels = list(img.getdata())
    non_white = [p for p in pixels if p[:3] != (255, 255, 255)]
    assert len(non_white) > 0


# ── Task 6: Text utilities ────────────────────────────────────────────────────

def test_measure_text_positive():
    font = bl.load_font("mono_bold", 30)
    w, h = bl.measure_text("HELLO", font)
    assert w > 0 and h > 0


def test_measure_text_accented():
    font = bl.load_font("poppins_medium", 26)
    w, h = bl.measure_text("NAO E VOCE TAMBEM TRAFEGO", font)
    assert w > 0


def test_wrap_text_breaks_long_line():
    font = bl.load_font("poppins_medium", 26)
    long_line = "Palavra " * 20
    lines = bl.wrap_text(long_line.strip(), font, max_width=800)
    assert len(lines) > 1


def test_sample_brightness_black():
    img = PILImage.new("RGBA", (100, 100), (0, 0, 0, 255))
    b = bl.sample_brightness(img, 0, 0, 100, 100)
    assert b < 0.05


def test_sample_brightness_white():
    img = PILImage.new("RGBA", (100, 100), (255, 255, 255, 255))
    b = bl.sample_brightness(img, 0, 0, 100, 100)
    assert b > 0.95


# ── Task 7: Feed compositor ───────────────────────────────────────────────────

def test_render_feed_creates_file():
    c = _campanha_with_image()
    out_dir = Path(tempfile.mkdtemp())
    out = bl.render_feed(c, out_dir)
    assert out.exists(), f"File not created: {out}"


def test_render_feed_dimensions():
    c = _campanha_with_image()
    out_dir = Path(tempfile.mkdtemp())
    out = bl.render_feed(c, out_dir)
    with PILImage.open(out) as im:
        assert im.size == (1080, 1080), f"Expected 1080x1080, got {im.size}"


def test_render_feed_accented_text():
    c = _campanha_with_image()
    c["copy"]["linha1"] = "NAO E VOCE TAMBEM ESTA ESTAO TRAFEGO"
    out_dir = Path(tempfile.mkdtemp())
    out = bl.render_feed(c, out_dir)
    assert out.exists()


# ── Task 8: Story compositor ──────────────────────────────────────────────────

def test_render_story_creates_file():
    c = _campanha_with_image()
    out_dir = Path(tempfile.mkdtemp())
    out = bl.render_story(c, out_dir)
    assert out.exists()


def test_render_story_dimensions():
    c = _campanha_with_image()
    out_dir = Path(tempfile.mkdtemp())
    out = bl.render_story(c, out_dir)
    with PILImage.open(out) as im:
        assert im.size == (1080, 1920)


def test_render_story_accented():
    c = _campanha_with_image()
    c["copy"]["bloco_vermelho"] = "ESTAO JUNTOS"
    out_dir = Path(tempfile.mkdtemp())
    out = bl.render_story(c, out_dir)
    assert out.exists()


# ── Task 9: Integration (main CLI) ────────────────────────────────────────────

def test_main_integration():
    tmp = Path(tempfile.mkdtemp())
    src = _make_synthetic_jpeg(600, 600)
    campanha = {
        "nome": "integ-test",
        "imagem": str(src),
        "formatos": ["feed", "story"],
        "copy": {
            "tag":           "BLACK LINE AGENCY // MKTG",
            "linha1":        "NAO PARA. NAO DESISTE.",
            "bloco_vermelho": "TRAFEGO QUE CONVERTE",
            "bloco_dourado":  "VOCE ESTA NO LUGAR CERTO",
            "corpo":         ["Linha um.", "Linha dois tambem."],
            "cta":           "FALE CONOSCO >>",
        },
    }
    json_path = tmp / "campanha.json"
    json_path.write_text(json.dumps(campanha, ensure_ascii=False), encoding="utf-8")
    out_dir = tmp / "output"
    out_dir.mkdir()

    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "bl_gerar.py"),
         str(json_path)],
        capture_output=True, text=True, cwd=str(tmp),
    )
    assert result.returncode == 0, f"CLI failed:\n{result.stdout}\n{result.stderr}"
    assert (out_dir / "integ-test_feed_1080x1080.png").exists()
    assert (out_dir / "integ-test_story_1080x1920.png").exists()
