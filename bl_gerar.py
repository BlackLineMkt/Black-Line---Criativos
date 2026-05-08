"""
Black Line Agency -- Gerador de Criativos INK RIOT
Uso: python bl_gerar.py campanha.json
"""
import sys
import os
import json
import math
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError:
    print("Pillow nao encontrado. Instale com:  pip install Pillow", file=sys.stderr)
    sys.exit(1)

# -- SECTION 1: CONSTANTS ----------------------------------------------------

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
    "tag":            17,
    "linha1_feed":   112,   "linha1_story":   96,
    "bloco_vm_feed": 118,   "bloco_vm_story": 100,
    "bloco_do_feed": 108,   "bloco_do_story":  90,
    "corpo_feed":     26,   "corpo_story":     30,
    "cta_feed":       28,   "cta_story":       32,
    "watermark":      20,
}

# -- SECTION 2: FONT LOADER --------------------------------------------------
# (implemented in Task 2)

# -- SECTION 3: BACKGROUND PROCESSING ----------------------------------------
# (implemented in Task 3)

# -- SECTION 4: GRAPHIC PRIMITIVES -------------------------------------------
# (implemented in Tasks 4-5)

# -- SECTION 5: TEXT UTILITIES -----------------------------------------------
# (implemented in Task 6)

# -- SECTION 6: FEED COMPOSITOR ----------------------------------------------
# (implemented in Task 7)

# -- SECTION 7: STORY COMPOSITOR ---------------------------------------------
# (implemented in Task 8)

# -- SECTION 8: ENTRYPOINT ---------------------------------------------------


def main():
    if len(sys.argv) < 2:
        print("Uso: python bl_gerar.py campanha.json", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
