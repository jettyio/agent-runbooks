#!/usr/bin/env python3
"""Make a pelican asset transparent — the 2026-06-27 Canada-Day lesson.

PNG: border flood-fill the flat cream background -> alpha 0. Interior whites
     (body/face) SURVIVE because the bird is fully enclosed by the navy outline,
     so the flood (seeded from the image border) can't reach them. A 2px dilation
     eats the cream anti-alias halo so there's no fringe on dark/colored backgrounds.
SVG: delete vtracer's FIRST <path> (the full-canvas cream bg rect) and ensure a
     viewBox so it scales cleanly.

Usage:
    python3 transparentize.py <in.png>  <out.png>
    python3 transparentize.py <in.svg>  <out.svg>
"""
import sys, re

inp, out = sys.argv[1], sys.argv[2]

if inp.lower().endswith(".png"):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    im = Image.open(inp).convert("RGBA")
    rgb = np.asarray(im).astype(np.int16)[:, :, :3]
    h, w, _ = rgb.shape
    bg = np.median(np.array([rgb[2, 2], rgb[2, w-3], rgb[h-3, 2], rgb[h-3, w-3]]), 0)
    dist = np.sqrt(((rgb - bg) ** 2).sum(2))
    lbl, _ = ndimage.label(dist < 60)                       # near-cream pixels
    border = (set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]))
    border.discard(0)
    bgmask = ndimage.binary_dilation(np.isin(lbl, list(border)), iterations=2)
    o = np.asarray(im).copy()
    o[bgmask, 3] = 0
    Image.fromarray(o, "RGBA").save(out)
    print(f"transparent PNG -> {out}  (removed {int(bgmask.sum())} bg px)")
else:
    s = open(inp).read()
    hdr = re.search(r"<svg([^>]*)>", s).group(0)
    if "viewBox" not in hdr:
        wm = re.search(r'width="(\d+)"', hdr); hm = re.search(r'height="(\d+)"', hdr)
        if wm and hm:
            s = s.replace(hdr, hdr[:-1] + f' viewBox="0 0 {wm.group(1)} {hm.group(1)}">', 1)
    first = re.search(r"<path\b.*?/>", s, flags=re.S).group(0)
    assert ("FAF8F3" in first.upper()) or ("3072" in first), \
        "first <path> doesn't look like the full-canvas cream bg — inspect before stripping"
    open(out, "w").write(s.replace(first, "", 1))
    print(f"transparent SVG -> {out}  (stripped full-canvas bg path)")
