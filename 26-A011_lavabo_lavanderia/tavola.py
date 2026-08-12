#!/usr/bin/env python3
"""Renderizza il DXF in PNG (tavola completa o ritaglio) per lettura visiva."""
import sys

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.properties import LayoutProperties
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], sys.argv[2]
no_hatch = "--no-hatch" in sys.argv
window = None
for a in sys.argv:
    if a.startswith("--win="):  # --win=x0,y0,x1,y1
        window = [float(v) for v in a[6:].split(",")]

doc = ezdxf.readfile(src)
msp = doc.modelspace()

rotti = [e for e in msp if e.dxftype() == "INSERT" and e.dxf.name not in doc.blocks]
for e in rotti:
    msp.delete_entity(e)

if no_hatch:
    for e in list(msp.query("HATCH")):
        msp.delete_entity(e)

fig = plt.figure(figsize=(22, 16), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ctx = RenderContext(doc)
backend = MatplotlibBackend(ax)
props = LayoutProperties.modelspace()
props.set_colors("#FFFFFF")  # fondo bianco, i colori neri/bianchi si adattano da soli
Frontend(ctx, backend).draw_layout(msp, finalize=True, layout_properties=props)
if window:
    ax.set_xlim(window[0], window[2])
    ax.set_ylim(window[1], window[3])
fig.savefig(out)
print("scritto", out)
