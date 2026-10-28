"""Render stills + a looping GIF of promap's scripted animations into docs/images/."""
import os, sys
import numpy as np, moderngl
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from promap.media import generative as g
from promap.render.gen import GenRenderer

OUT = os.path.join(HERE, "images")
ctx = moderngl.create_standalone_context(require=330)
r = GenRenderer(ctx); r.readback = True

def frame(name, t, size, extra=None):
    eff = g.EFFECTS[name]
    p = dict(extra or {})
    if eff.param("text"): p.setdefault("text", "BOO")
    params = eff.normalize(p)
    assert r.texture_for(name, g.GenFrame(name, params, t, size)) is not None, r.errors.get(name)
    return Image.fromarray(r.readbacks[name].copy())

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
except Exception:
    font = ImageFont.load_default()

# --- contact sheet of every effect ---
T = {"kinetic_typography": 0.6, "raymarched_fractals": 5.0, "glitch_effect": 1.1}
names = [n for n in g.EFFECTS if n != "alignment_grid"] + ["alignment_grid"]
cell, label_h, cols = 220, 24, 7
rows = (len(names) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (14, 14, 18))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    im = frame(n, T.get(n, 2.3), (cell, cell))
    x, y = (i % cols) * cell, (i // cols) * (cell + label_h)
    sheet.paste(im, (x, y))
    d.text((x + 8, y + cell + 4), g.EFFECTS[n].title, fill=(220, 220, 230), font=font)
sheet.save(f"{OUT}/animations.png", optimize=True)
print("sheet", sheet.size)

# --- looping GIF, six effects in a grid ---
pick = ["neon_glow", "metaballs", "raymarched_fractals", "flow_fields", "liquid_morph", "vaporwave_grid"]
gc, gcols, fps, secs = 200, 3, 15, 3.0
nfr = int(fps * secs)
frames = []
for k in range(nfr):
    t = k / fps
    grid = Image.new("RGB", (gcols * gc, 2 * gc))
    for i, n in enumerate(pick):
        grid.paste(frame(n, t, (gc, gc)), ((i % gcols) * gc, (i // gcols) * gc))
    frames.append(grid.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG))
frames[0].save(f"{OUT}/animations.gif", save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True)
print("gif frames", nfr)
r.release(); ctx.release()
