import math
import os
from PIL import Image, ImageDraw
from hex_painter import HexPainter

HEX_SIZE = 74
PADDING = 80

WIDTH = int(math.sqrt(3) * HEX_SIZE)
HEIGHT = int(2 * HEX_SIZE)
IMG_W, IMG_H = WIDTH + PADDING, HEIGHT + PADDING

# Simple green variations for forest base tiles
COLORS = [
    (34, 100, 34, 255),
    (36, 110, 36, 255),
    (30, 95, 30, 255),
    (40, 120, 40, 255),
    (28, 90, 28, 255),
    (38, 105, 38, 255),
]

OUTPUT_DIR = os.path.join("assets", "hex_tiles")
os.makedirs(OUTPUT_DIR, exist_ok=True)

for i, color in enumerate(COLORS, start=1):
    img = Image.new("RGBA", (IMG_W, IMG_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = IMG_W / 2, IMG_H / 2
    HexPainter.draw_hex_base(draw, cx, cy, HEX_SIZE, color)
    out_path = os.path.join(OUTPUT_DIR, f"forest_base_{i}.png")
    img.save(out_path)
    print(f"Saved {out_path}")
