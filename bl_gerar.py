# -*- coding: utf-8 -*-
"""
Black Line Agency -- Gerador de Criativos INK RIOT
Uso: python bl_gerar.py campanha.json
"""
import sys
import io
import os
import json
import math
import random
import platform
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError:
    print("Pillow nao encontrado. Instale com:  pip install Pillow", file=sys.stderr)
    sys.exit(1)

if platform.system() == "Windows":
    _impact  = Path("C:/Windows/Fonts/impact.ttf")
    _arialbd = Path("C:/Windows/Fonts/arialbd.ttf")
    FONT_DISPLAY = str(_impact if _impact.exists() else _arialbd)
    FONT_BOLD    = "C:/Windows/Fonts/arialbd.ttf"
    FONT_MED     = "C:/Windows/Fonts/arial.ttf"
    FONT_MONO    = "C:/Windows/Fonts/cour.ttf"
    FONT_MONOB   = "C:/Windows/Fonts/courbd.ttf"
else:
    FONT_DISPLAY = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf"
    FONT_BOLD    = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
    FONT_MED     = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
    FONT_MONO    = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
    FONT_MONOB   = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

# ── SECTION 1: CONSTANTS ─────────────────────────────────────────────────────

PRETO           = (10,  8,   6)
VERMELHO        = (190, 25,  25)
DOURADO         = (198, 154, 59)
BRANCO_QUENTE   = (245, 238, 225)
CREME           = (195, 185, 170)
DIVISOR         = (80,  72,  62)
WATERMARK_COLOR = (130, 120, 110)

FORMATS = {
    "feed":  {"w": 1080, "h": 1080, "margin_x": 54, "margin_y": 54},
    "story": {"w": 1080, "h": 1920, "margin_x": 60,
              "safe_top": 270, "safe_bottom": 1650},
}

FONT_SIZES = {
    "tag":            22,
    "linha1_feed":   128,   "linha1_story":  128,
    "bloco_vm_feed": 136,   "bloco_vm_story": 136,
    "bloco_do_feed": 120,   "bloco_do_story": 120,
    "corpo_feed":     30,   "corpo_story":     30,
    "cta_feed":       26,   "cta_story":       26,
    "watermark":      22,
}

# ── SECTION 2: FONT LOADER ───────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).parent

_FONT_SEARCH: dict = {
    "nimbus": [
        "fonts/NimbusRoman-Bold.otf",
        FONT_DISPLAY,
        "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf",
    ],
    "poppins_bold": [
        "fonts/Poppins-Bold.ttf",
        FONT_BOLD,
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "/usr/share/fonts/truetype/poppins/Poppins-Bold.ttf",
    ],
    "poppins_medium": [
        "fonts/Poppins-Medium.ttf",
        FONT_MED,
        "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
        "/usr/share/fonts/truetype/poppins/Poppins-Medium.ttf",
    ],
    "mono_bold": [
        "fonts/LiberationMono-Bold.ttf",
        FONT_MONOB,
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    ],
    "mono_regular": [
        "fonts/LiberationMono-Regular.ttf",
        FONT_MONO,
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ],
}

_font_cache: dict = {}


def _resolve_font_path(key: str):
    for candidate in _FONT_SEARCH.get(key, []):
        p = Path(candidate) if Path(candidate).is_absolute() else _SCRIPT_DIR / candidate
        if p.exists():
            return p
    return None


def load_font(key: str, size: int):
    cache_key = (key, size)
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    path = _resolve_font_path(key)
    font = None
    if path is not None:
        try:
            font = ImageFont.truetype(str(path), size)
        except OSError as e:
            print(f"AVISO: nao foi possivel carregar {path}: {e}", file=sys.stderr)
    if font is None:
        print(
            f"AVISO: fonte '{key}' nao encontrada. "
            f"Copie os TTF/OTF para {_SCRIPT_DIR / 'fonts'}",
            file=sys.stderr,
        )
        font = ImageFont.load_default()
    _font_cache[cache_key] = font
    return font


# ── SECTION 3: BACKGROUND PROCESSING ─────────────────────────────────────────

def _apply_gradient(
    img: Image.Image,
    y_start: int,
    y_end: int,
    alpha_at_start: int,
    alpha_at_end: int,
) -> None:
    """Mutates img (RGBA) by alpha-compositing a black gradient band."""
    w = img.width
    band_h = y_end - y_start
    if band_h <= 0:
        return
    overlay = Image.new("RGBA", (w, band_h), (0, 0, 0, 0))
    for i in range(band_h):
        t = i / max(band_h - 1, 1)
        alpha = int(alpha_at_start + (alpha_at_end - alpha_at_start) * t)
        row = Image.new("RGBA", (w, 1), (0, 0, 0, alpha))
        overlay.paste(row, (0, i))
    img.alpha_composite(overlay, dest=(0, y_start))


def process_background(src_path: str, w: int, h: int, seed: int = 42) -> Image.Image:
    """Loads, processes, and returns an RGBA image ready for compositing."""
    img = Image.open(src_path).convert("RGB").resize((w, h), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Brightness(img).enhance(0.85)
    img = ImageEnhance.Color(img).enhance(0.75)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert("RGBA")
    _apply_gradient(img, 0, min(380, h), 140, 0)
    _apply_gradient(img, max(0, h - 200), h, 0, 130)
    rng = random.Random(seed)
    for _ in range(35000):
        px = rng.randint(0, w - 1)
        py = rng.randint(0, h - 1)
        r, g, b, a = img.getpixel((px, py))
        delta = int(rng.randint(-40, 40) * 0.12)
        img.putpixel(
            (px, py),
            (
                max(0, min(255, r + delta)),
                max(0, min(255, g + delta)),
                max(0, min(255, b + delta)),
                a,
            ),
        )
    return img


# ── SECTION 4: GRAPHIC PRIMITIVES ────────────────────────────────────────────

def torn_block(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    color: tuple, seed: int,
) -> tuple:
    """28-point polygon simulating a torn-paper paint block. Returns bbox."""
    rng = random.Random(seed)
    pts = []
    # Top: left -> right, 7 points, y-jitter
    for i in range(7):
        pts.append((x + int(w * i / 6), y + rng.randint(-6, 6)))
    # Right: top -> bottom, 7 points, x-jitter
    for i in range(7):
        pts.append((x + w + rng.randint(-6, 6), y + int(h * i / 6)))
    # Bottom: right -> left, 7 points, y-jitter
    for i in range(7):
        pts.append((x + w - int(w * i / 6), y + h + rng.randint(-6, 6)))
    # Left: bottom -> top, 7 points, x-jitter
    for i in range(7):
        pts.append((x + rng.randint(-6, 6), y + h - int(h * i / 6)))
    draw.polygon(pts, fill=color)
    return (x, y, x + w, y + h)


def drip(
    draw: ImageDraw.ImageDraw,
    x: int, y0: int, length: int,
    color: tuple, w: int = 3,
) -> None:
    """Vertical ink drip with a bulb at the tip."""
    draw.line([(x, y0), (x, y0 + length)], fill=color, width=w)
    draw.ellipse([x - w, y0 + length - w, x + w, y0 + length + w], fill=color)


def splatter(
    draw: ImageDraw.ImageDraw,
    cx: int, cy: int,
    color: tuple, n: int,
    seed: int, max_dist: int,
) -> None:
    """n ink splatter dots radiating from (cx, cy). Every 3rd gets a trail."""
    rng = random.Random(seed)
    alpha = color[3] if len(color) == 4 else 200
    rgb = color[:3]
    for i in range(n):
        angle = rng.uniform(0, 2 * math.pi)
        dist  = rng.uniform(0, max_dist)
        r     = rng.randint(2, 10)
        sx    = cx + dist * math.cos(angle)
        sy    = cy + dist * math.sin(angle)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=rgb + (alpha,))
        if i % 3 == 0:
            trail_len = rng.randint(8, 18)
            back_angle = angle + math.pi
            ex = sx + trail_len * math.cos(back_angle)
            ey = sy + trail_len * math.sin(back_angle)
            draw.line([(sx, sy), (ex, ey)], fill=rgb + (int(alpha * 0.6),), width=2)


def stamp(
    draw: ImageDraw.ImageDraw,
    text: str, font,
    x: int, y: int,
    color: tuple,
    shadow_color: tuple = (0, 0, 0),
    offset: int = 3,
) -> None:
    """Text with a hard displaced shadow (not blurred)."""
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=color)


# ── SECTION 5: TEXT UTILITIES ─────────────────────────────────────────────────

def measure_text(text: str, font) -> tuple:
    """Returns (width, height) of rendered text using getbbox."""
    try:
        bbox = font.getbbox(text)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except AttributeError:
        # Fallback for ImageFont.load_default() which lacks getbbox
        return (len(text) * 6, 11)


def wrap_text(text: str, font, max_width: int) -> list:
    """Word-wraps text to fit within max_width pixels. Returns list of lines."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if measure_text(candidate, font)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def sample_brightness(img: Image.Image, x: int, y: int, w: int, h: int) -> float:
    """Mean luminance 0.0-1.0 of the region (x, y, x+w, y+h)."""
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(img.width, x + w), min(img.height, y + h)
    if x2 <= x1 or y2 <= y1:
        return 0.5
    region = img.crop((x1, y1, x2, y2)).convert("L")
    pixels = list(region.getdata())
    return sum(pixels) / (len(pixels) * 255)


def draw_corpo(
    draw: ImageDraw.ImageDraw,
    canvas: Image.Image,
    lines: list,
    font,
    x: int, y: int,
    max_w: int,
    line_height_factor: float = 1.45,
) -> int:
    """Draws corpo text block. Returns y coordinate below the last line."""
    font_h = measure_text("Ag", font)[1]
    step = int(font_h * line_height_factor)
    current_y = y
    for line in lines:
        for wline in wrap_text(line, font, max_w):
            brightness = sample_brightness(canvas, x, current_y, max_w, step)
            color = BRANCO_QUENTE if brightness < 0.45 else CREME
            for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                draw.text((x + dx, current_y + dy), wline, font=font, fill=PRETO)
            draw.text((x, current_y), wline, font=font, fill=color)
            current_y += step
    return current_y


def fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: str,
             max_size: int, max_width: int):
    """
    Returns the largest FreeTypeFont at or below max_size where text fits
    within max_width pixels. Steps down by 2px until it fits.
    Falls back to ImageFont.load_default() if the path is unusable.
    """
    if not font_path:
        return ImageFont.load_default()
    size = max_size
    while size > 8:
        try:
            font = ImageFont.truetype(font_path, size)
        except OSError:
            return ImageFont.load_default()
        try:
            w = draw.textbbox((0, 0), text, font=font)[2]
        except Exception:
            return font
        if w <= max_width:
            return font
        size -= 2
    try:
        return ImageFont.truetype(font_path, max(8, size))
    except OSError:
        return ImageFont.load_default()


# ── SECTION 6: LAYOUT BLOCKS HELPER ─────────────────────────────────────────

def _draw_color_blocks(
    draw: ImageDraw.ImageDraw,
    copy: dict,
    layout: str,
    W: int,
    MX: int,
    y: int,
    f_nimbus_r,
    f_nimbus_d,
    gap1: int = 20,
    gap2: int = 22,
) -> int:
    """
    Renders the layout-specific color blocks (items [4] and [5]).
    Block heights are computed dynamically from wrapped line counts (24px pad each side).
    Returns updated y after all blocks.
    """

    def _full_red_block(y0: int) -> int:
        """Full-width red torn_block with drips/splatters. Returns y after block."""
        wrapped = wrap_text(copy["bloco_vermelho"], f_nimbus_r, W - 2 * MX)
        row_h = int(measure_text("Ag", f_nimbus_r)[1] * 1.15)
        blk_h = len(wrapped) * row_h + 48
        torn_block(draw, 0, y0, W, blk_h, VERMELHO, seed=3)
        drip(draw, MX,     y0, 65, VERMELHO, w=4)
        drip(draw, W - MX, y0, 50, VERMELHO, w=3)
        splatter(draw, cx=28,     cy=y0 + blk_h // 2, color=VERMELHO + (175,),
                 n=40, seed=4, max_dist=48)
        splatter(draw, cx=W - 28, cy=y0 + blk_h // 2, color=VERMELHO + (175,),
                 n=40, seed=5, max_dist=48)
        ty = y0 + 24
        for wline in wrapped:
            tw = measure_text(wline, f_nimbus_r)[0]
            stamp(draw, wline, f_nimbus_r, (W - tw) // 2, ty,
                  color=BRANCO_QUENTE, shadow_color=(120, 10, 10), offset=3)
            ty += row_h
        return y0 + blk_h + gap1

    def _partial_gold_block(y0: int) -> int:
        """Partial-width gold torn_block. Returns y after block."""
        do_tw, do_th = measure_text(copy["bloco_dourado"], f_nimbus_d)
        blk_h = do_th + 48
        torn_block(draw, MX, y0, do_tw + 52, blk_h, DOURADO, seed=6)
        stamp(draw, copy["bloco_dourado"], f_nimbus_d, MX + 26, y0 + 24,
              color=PRETO, shadow_color=(100, 75, 20), offset=2)
        splatter(draw, cx=MX + do_tw + 52, cy=y0 + blk_h // 2,
                 color=DOURADO + (200,), n=35, seed=7, max_dist=58)
        return y0 + blk_h + gap2

    def _partial_red_block(y0: int) -> int:
        """Partial-width second red torn_block (vermelho_dominante). Returns y after block."""
        do_tw, do_th = measure_text(copy["bloco_dourado"], f_nimbus_d)
        blk_h = do_th + 48
        torn_block(draw, MX, y0, do_tw + 52, blk_h, VERMELHO, seed=6)
        stamp(draw, copy["bloco_dourado"], f_nimbus_d, MX + 26, y0 + 24,
              color=BRANCO_QUENTE, shadow_color=(120, 10, 10), offset=2)
        splatter(draw, cx=MX + do_tw + 52, cy=y0 + blk_h // 2,
                 color=VERMELHO + (175,), n=35, seed=7, max_dist=58)
        return y0 + blk_h + gap2

    if layout == "vermelho_dominante":
        y = _full_red_block(y)
        y = _partial_red_block(y)

    elif layout == "dourado_dominante":
        vm_tw, vm_th = measure_text(copy["bloco_vermelho"], f_nimbus_r)
        stamp(draw, copy["bloco_vermelho"], f_nimbus_r, (W - vm_tw) // 2, y,
              color=VERMELHO, shadow_color=PRETO, offset=3)
        y += vm_th + gap1
        y = _partial_gold_block(y)

    elif layout == "minimalista":
        vm_tw, vm_th = measure_text(copy["bloco_vermelho"], f_nimbus_r)
        stamp(draw, copy["bloco_vermelho"], f_nimbus_r, (W - vm_tw) // 2, y,
              color=VERMELHO, shadow_color=PRETO, offset=3)
        y += vm_th + gap1
        do_tw, do_th = measure_text(copy["bloco_dourado"], f_nimbus_d)
        draw.text((MX, y), copy["bloco_dourado"], font=f_nimbus_d, fill=DOURADO)
        y += do_th + gap2

    else:  # padrao
        y = _full_red_block(y)
        y = _partial_gold_block(y)

    return y


# ── SECTION 7: FEED COMPOSITOR ───────────────────────────────────────────────

def render_feed(campanha: dict, output_dir: Path) -> Path:
    """Renders the 1080x1080 feed creative. Returns the output Path."""
    W, H = 1080, 1080
    MX   = 54
    copy = campanha["copy"]

    canvas = process_background(campanha["imagem"], W, H)
    draw   = ImageDraw.Draw(canvas)

    _nimbus_path = str(_resolve_font_path("nimbus") or "")
    _max_w       = W - 2 * MX

    f_tag      = load_font("mono_bold",      FONT_SIZES["tag"])
    f_nimbus1  = fit_font(draw, copy["linha1"],           _nimbus_path, FONT_SIZES["linha1_feed"],   _max_w)
    f_nimbus_r = fit_font(draw, copy["bloco_vermelho"],   _nimbus_path, FONT_SIZES["bloco_vm_feed"], _max_w)
    f_nimbus_d = fit_font(draw, copy["bloco_dourado"],    _nimbus_path, FONT_SIZES["bloco_do_feed"], _max_w)
    f_corpo    = load_font("poppins_medium", FONT_SIZES["corpo_feed"])
    f_cta      = load_font("mono_bold",      FONT_SIZES["cta_feed"])
    f_wm       = load_font("mono_regular",   FONT_SIZES["watermark"])

    y = MX

    # [1] Black splatters top-right
    splatter(draw, cx=W - 80, cy=80, color=PRETO + (210,),
             n=120, seed=1, max_dist=160)

    # [2] Tag block
    tag_tw, tag_th = measure_text(copy["tag"], f_tag)
    tag_h = tag_th + 20
    torn_block(draw, MX, y, tag_tw + 32, tag_h, PRETO, seed=2)
    draw.text((MX + 16, y + 10), copy["tag"], font=f_tag, fill=DOURADO)
    y += tag_h + 40

    # [3] linha1
    stamp(draw, copy["linha1"], f_nimbus1, MX, y,
          color=BRANCO_QUENTE, shadow_color=PRETO, offset=4)
    y += measure_text(copy["linha1"], f_nimbus1)[1] + 24

    # [4+5] Layout-specific color blocks
    y = _draw_color_blocks(draw, copy, campanha.get("layout", "padrao"),
                           W, MX, y, f_nimbus_r, f_nimbus_d, gap1=20, gap2=22)

    # [6] Divider
    draw.rectangle([(MX, y), (W - MX, y + 3)], fill=DIVISOR)
    y += 20
    # Push corpo to at least 55% of canvas height so content isn't bunched at top
    y = max(y, int(H * 0.55))

    cta_tw, cta_th = measure_text(copy["cta"], f_cta)
    cta_h = cta_th + 28

    # [7] Corpo
    y = draw_corpo(draw, canvas, copy["corpo"], f_corpo,
                   x=MX, y=y, max_w=W - 2 * MX)
    y += 20

    # [8] CTA
    torn_block(draw, MX, y, cta_tw + 52, cta_h, PRETO, seed=8)
    draw.text((MX + 26, y + 14), copy["cta"], font=f_cta, fill=DOURADO)

    # [10] Black bar 8px at absolute bottom
    draw.rectangle([(0, H - 8), (W, H)], fill=PRETO)

    # [9] Watermark — rendered last, anchored to bottom
    wm_text = "@blackline.mkt"
    wm_tw, wm_th = measure_text(wm_text, f_wm)
    draw.text(((W - wm_tw) // 2, H - 32 - wm_th), wm_text, font=f_wm, fill=WATERMARK_COLOR)

    out_path = output_dir / f"{campanha['nome']}_feed_1080x1080.png"
    canvas.convert("RGB").save(str(out_path), "PNG")
    return out_path


# ── SECTION 7: STORY COMPOSITOR ──────────────────────────────────────────────

def render_story(campanha: dict, output_dir: Path) -> Path:
    """Renders the 1080x1920 story creative. Returns the output Path."""
    W, H        = 1080, 1920
    MX          = 60
    SAFE_TOP    = 270
    SAFE_BOTTOM = 1650
    copy        = campanha["copy"]

    canvas = process_background(campanha["imagem"], W, H)
    draw   = ImageDraw.Draw(canvas)

    _nimbus_path = str(_resolve_font_path("nimbus") or "")
    _max_w       = W - 2 * MX

    f_tag      = load_font("mono_bold",      FONT_SIZES["tag"])
    f_nimbus1  = fit_font(draw, copy["linha1"],           _nimbus_path, FONT_SIZES["linha1_story"],   _max_w)
    f_nimbus_r = fit_font(draw, copy["bloco_vermelho"],   _nimbus_path, FONT_SIZES["bloco_vm_story"], _max_w)
    f_nimbus_d = fit_font(draw, copy["bloco_dourado"],    _nimbus_path, FONT_SIZES["bloco_do_story"], _max_w)
    f_corpo    = load_font("poppins_medium", FONT_SIZES["corpo_story"])
    f_cta      = load_font("mono_bold",      FONT_SIZES["cta_story"])
    f_wm       = load_font("mono_regular",   FONT_SIZES["watermark"])

    y = SAFE_TOP

    # [1] Black splatters
    splatter(draw, cx=W - 100, cy=200, color=PRETO + (210,),
             n=120, seed=1, max_dist=160)

    # [2] Tag block
    tag_tw, tag_th = measure_text(copy["tag"], f_tag)
    tag_h = tag_th + 20
    torn_block(draw, MX, y, tag_tw + 32, tag_h, PRETO, seed=2)
    draw.text((MX + 16, y + 10), copy["tag"], font=f_tag, fill=DOURADO)
    y += tag_h + 40

    # [3] linha1
    stamp(draw, copy["linha1"], f_nimbus1, MX, y,
          color=BRANCO_QUENTE, shadow_color=PRETO, offset=4)
    y += measure_text(copy["linha1"], f_nimbus1)[1] + 28

    # [4+5] Layout-specific color blocks
    y = _draw_color_blocks(draw, copy, campanha.get("layout", "padrao"),
                           W, MX, y, f_nimbus_r, f_nimbus_d, gap1=24, gap2=26)

    # [6] Divider
    draw.rectangle([(MX, y), (W - MX, y + 3)], fill=DIVISOR)
    y += 22
    # Push corpo to at least 55% of canvas height so content isn't bunched at top
    y = max(y, int(H * 0.55))

    cta_tw, cta_th = measure_text(copy["cta"], f_cta)
    cta_h = cta_th + 28

    # [7] Corpo
    y = draw_corpo(draw, canvas, copy["corpo"], f_corpo,
                   x=MX, y=y, max_w=W - 2 * MX)
    y += 24

    # [8] CTA
    if y + cta_h > SAFE_BOTTOM:
        print(
            f"AVISO: CTA ultrapassa zona segura ({y + cta_h} > {SAFE_BOTTOM}). "
            f"Reduza o texto.",
            file=sys.stderr,
        )
    torn_block(draw, MX, y, cta_tw + 52, cta_h, PRETO, seed=8)
    draw.text((MX + 26, y + 14), copy["cta"], font=f_cta, fill=DOURADO)

    # [10] Black bar 8px at absolute bottom
    draw.rectangle([(0, H - 8), (W, H)], fill=PRETO)

    # [9] Watermark — rendered last, anchored to bottom
    wm_text = "@blackline.mkt"
    wm_tw, wm_th = measure_text(wm_text, f_wm)
    draw.text(((W - wm_tw) // 2, H - 32 - wm_th), wm_text, font=f_wm, fill=WATERMARK_COLOR)

    out_path = output_dir / f"{campanha['nome']}_story_1080x1920.png"
    canvas.convert("RGB").save(str(out_path), "PNG")
    return out_path


# ── SECTION 8: ENTRYPOINT ────────────────────────────────────────────────────

_REQUIRED_COPY_KEYS = {"tag", "linha1", "bloco_vermelho", "bloco_dourado", "corpo", "cta"}


def main():
    if len(sys.argv) < 2:
        print("Uso: python bl_gerar.py campanha.json", file=sys.stderr)
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Erro: arquivo nao encontrado -- {json_path}", file=sys.stderr)
        sys.exit(1)

    with json_path.open(encoding="utf-8") as f:
        try:
            campanha = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Erro no JSON: {e}", file=sys.stderr)
            sys.exit(1)

    for key in ("nome", "imagem", "formatos", "copy"):
        if key not in campanha:
            print(f"Erro: chave obrigatoria ausente no JSON: '{key}'", file=sys.stderr)
            sys.exit(1)

    if not isinstance(campanha["copy"], dict):
        print("Erro: 'copy' deve ser um objeto JSON.", file=sys.stderr)
        sys.exit(1)

    if not isinstance(campanha["formatos"], list):
        print("Erro: 'formatos' deve ser uma lista JSON.", file=sys.stderr)
        sys.exit(1)

    missing_copy = _REQUIRED_COPY_KEYS - set(campanha["copy"].keys())
    if missing_copy:
        print(f"Erro: chaves ausentes em 'copy': {missing_copy}", file=sys.stderr)
        sys.exit(1)

    if not Path(campanha["imagem"]).exists():
        print(f"Erro: imagem nao encontrada -- {campanha['imagem']}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    _renderers = {"feed": render_feed, "story": render_story}

    for fmt in campanha["formatos"]:
        renderer = _renderers.get(fmt)
        if renderer is None:
            print(f"AVISO: formato desconhecido '{fmt}' ignorado.", file=sys.stderr)
            continue
        out = renderer(campanha, output_dir)
        print(f"Gerado: {out.resolve()}")


if __name__ == "__main__":
    main()
