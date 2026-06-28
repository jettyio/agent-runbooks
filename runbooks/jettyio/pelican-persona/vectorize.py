#!/usr/bin/env python3
"""Snap a flat cartoon PNG to the exact Jetty brand palette, then vector-trace to SVG.

Usage:
    python3 vectorize.py <src.png> <flat.png> <out.svg> [accent] [smooth]
    accent ∈ {lavender, amber, sage, greyhoodie, canada}   (default lavender)
    smooth ∈ {1,0}  (default 1)  -- 1 = the clean-outline pipeline (recommended)

SMOOTH=1 (default) is the lesson from the 2026-06-27 alternates: tracing the raster at
low upscale follows every edge wobble and gives a JAGGED / frayed navy outline. Fix =
upscale 3x + a contour Gaussian blur BEFORE the palette-snap, so vtracer follows clean
curves. path_precision drops to 4 to keep the file ~150-200KB (precision 8 balloons it
to 400-600KB with no visible gain).

Adding a NEW accent: don't guess the colors. Sample the real render:
    from PIL import Image; from collections import Counter
    im=Image.open("cand.png").convert("RGB")
    q=im.quantize(colors=24).convert("RGB"); print(Counter(q.getdata()).most_common(24))
  then drop the cluster centers into ACCENTS below (garment highlight/mid/shadow [+ trim]).
"""
import sys
from PIL import Image, ImageFilter
import vtracer

src    = sys.argv[1]
flat   = sys.argv[2]
svg    = sys.argv[3]
accent = sys.argv[4] if len(sys.argv) > 4 else "lavender"
smooth = (sys.argv[5] != "0") if len(sys.argv) > 5 else True

# Jetty brand palette (RGB). Shared base + per-accent (sampled from real renders).
BASE = [
    (250,248,243),  # cream bg
    (255,255,255),  # white body
    (10,18,48),     # navy outline #0A1230
    (255,170,0),    # orange pouch/feet #FFAA00
    (216,143,14),   # dark orange (crease/shadow) #D88F0E
    (250,194,82),   # gold foot highlight #FAC252
]
ACCENTS = {
    "lavender":   [(124,95,217),(98,75,180),(206,196,240)],        # #7C5FD9 + dark + light
    "amber":      [(240,169,31),(216,143,14),(251,233,195)],       # #F0A91F + dark + light
    "sage":       [(132,169,127),(92,122,90),(205,222,202)],       # #84A97F render-sampled (2026-06-27) + dark + light
    # grey hoodie (highlight/mid/shadow/deep) + lavender drawstrings (core + light)
    "greyhoodie": [(202,202,204),(180,180,182),(120,120,132),(96,96,108),(124,95,217),(184,156,228)],
    # Canada red hoodie (mid/shadow/highlight). White maple leaf uses BASE white.
    # Tuned 2026-06-27 from the real render: brighter #E33028 (was #D23228, too muted).
    "canada":     [(227,48,40),(150,33,38),(240,96,84)],           # #E33028 bright + dark + light
    # Operator-formal yellow blazer (mid/shadow/highlight). Lighter+more yellow than amber
    # so it separates from the #FFAA00 beak in the snap. Bow/bowtie navy = BASE ink.
    "operatoryellow": [(238,197,55),(205,158,28),(250,222,110)],   # #EEC537 + dark + light
}
palette = BASE + ACCENTS.get(accent, ACCENTS["lavender"])

pal_img = Image.new("P", (1,1))
flat_pal = []
for c in palette: flat_pal += list(c)
flat_pal += [0,0,0]*(256-len(palette))
pal_img.putpalette(flat_pal)

im = Image.open(src).convert("RGB")
w,h = im.size
if smooth:
    im = im.resize((w*3, h*3), Image.LANCZOS)             # big upscale -> smoother curves
    im = im.filter(ImageFilter.GaussianBlur(radius=2.5))  # even out ragged edge noise
    snapped = im.quantize(palette=pal_img, dither=Image.Dither.NONE).convert("RGB")
    snapped = snapped.filter(ImageFilter.ModeFilter(size=3))   # drop isolated snap specks
    pp = 4
else:
    im = im.resize((int(w*1.5), int(h*1.5)), Image.LANCZOS)
    snapped = im.quantize(palette=pal_img, dither=Image.Dither.NONE).convert("RGB")
    pp = 6
snapped.save(flat)

vtracer.convert_image_to_svg_py(
    flat, svg,
    colormode="color", hierarchical="stacked", mode="spline",
    filter_speckle=48 if smooth else 16, color_precision=8, layer_difference=24,
    corner_threshold=80 if smooth else 60, length_threshold=4.0,
    splice_threshold=60 if smooth else 45, path_precision=pp,
)
print("wrote", flat, svg, "accent=", accent, "smooth=", smooth)
