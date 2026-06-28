#!/usr/bin/env python3
"""Overlay a flat PROP (e.g. a white maple leaf, a heart, a logo) onto a vectorized
pelican body — the reliable way to add a small high-contrast detail the nano editor
keeps stripping (e.g. a white-on-red maple leaf vanished across 8 regenerations).

Workflow this supports:
  1. Get a clean prop shape. Either hand-make an SVG, OR extract one from a good raster:
       - build a near-white (or near-X) mask, FLOOD-FILL from a seed inside the prop to
         isolate just that connected blob (avoids grabbing the body/neck), crop, upscale,
         vtracer colormode="binary" -> prop.svg  (one path).
  2. python3 overlay_prop.py <body.svg> <prop.svg> <out.svg> <cx> <cy> <w> [fill] [render]
       cx cy w  = prop center + width, in the RENDER-px space you eyeball (default 1400).
       fill     = prop color (default #ffffff). render = your QA render width (default 1400).
  3. rsvg-convert -b "#faf8f3" -w 1400 -h 1400 out.svg -o out.png  -> eyeball, nudge cx/cy/w, repeat.

Note: vector trace tends to drop thin STEMS (broke connectivity). Re-add a stem with a
small rounded <rect> via the STEM env knob, or accept the stemless leaf (still reads fine).
"""
import sys, re, os

body_svg, prop_svg, out_svg = sys.argv[1], sys.argv[2], sys.argv[3]
cx, cy, w = float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
fill   = sys.argv[7] if len(sys.argv) > 7 else "#ffffff"
render = float(sys.argv[8]) if len(sys.argv) > 8 else 1400.0

body = open(body_svg).read()
prop = open(prop_svg).read()

BW = float(re.search(r'width="(\d+(?:\.\d+)?)"', body).group(1))   # body coord-space width
pm = re.search(r'width="(\d+(?:\.\d+)?)"\s+height="(\d+(?:\.\d+)?)"', prop)
PW, PH = float(pm.group(1)), float(pm.group(2))
prop_d = re.search(r'<path[^>]*\bd="([^"]+)"', prop).group(1)

R = BW / render
s = (w * R) / PW
tx = cx * R - s * PW / 2
ty = cy * R - s * PH / 2

# optional stem: STEM="x,y,w,h,rx" in PROP-local coords, e.g. STEM="176,320,20,70,9"
stem = ""
if os.environ.get("STEM"):
    sx, sy, sw, sh, srx = os.environ["STEM"].split(",")
    stem = f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="{srx}" fill="{fill}"/>'

g = f'<g transform="translate({tx:.1f},{ty:.1f}) scale({s:.4f})">{stem}<path d="{prop_d}" fill="{fill}"/></g>'
open(out_svg, "w").write(body.replace("</svg>", g + "</svg>"))
print(f"wrote {out_svg}  prop@({cx},{cy}) w={w} fill={fill} scale={s:.3f}")
