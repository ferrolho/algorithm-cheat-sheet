"""
Orchestrator: render the front (front.py) and back (back.py) pages and assemble
them into a single two-page, exact-A4-landscape PDF, plus a raster preview of
each side for the README.

  Front (page 1) — "Which to Use", the selection flow      (source: flowchart.yaml)
  Back  (page 2) — "How They Work", the templates          (source: algorithms.yaml)

cairosvg embeds a Helvetica-metric font (subsetted) and renders each SVG to a
vector PDF. It needs the native cairo library, which is NOT a pip package:
  macOS:  brew install cairo
  Ubuntu: sudo apt install libcairo2
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cairosvg
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from reportlab.lib.pagesizes import A4, landscape

from front import build_front_svg
from back import build_back_svg

_HERE = os.path.dirname(os.path.abspath(__file__))
_out = os.path.join(_HERE, 'algorithm-cheat-sheet.pdf')

_svg_front = build_front_svg()   # page 1 — selection flow
_svg_back = build_back_svg()     # page 2 — how they work

pw, ph = landscape(A4)
m = 6


def _fit_page(svg_path):
    """Render an SVG to a vector PDF page and centre-fit it onto A4 landscape."""
    tmp = svg_path[:-4] + '.tmp.pdf'
    cairosvg.svg2pdf(url=svg_path, write_to=tmp)
    src = PdfReader(tmp).pages[0]
    sw, sh = float(src.mediabox.width), float(src.mediabox.height)
    scale = min((pw - 2*m)/sw, (ph - 2*m)/sh)
    tx, ty = (pw - sw*scale)/2, (ph - sh*scale)/2
    pg = PageObject.create_blank_page(width=pw, height=ph)
    pg.merge_transformed_page(src, Transformation().scale(scale).translate(tx, ty))
    os.remove(tmp)
    return pg


w = PdfWriter()
w.add_page(_fit_page(_svg_front))
w.add_page(_fit_page(_svg_back))
with open(_out, 'wb') as f:
    w.write(f)
print('Wrote', os.path.basename(_out), '(2 pages)')

# raster previews for the README (clickable thumbnails that link to the PDF)
for svg_path, png_name in [(_svg_front, 'preview-front.png'), (_svg_back, 'preview-back.png')]:
    png = os.path.join(_HERE, png_name)
    cairosvg.svg2png(url=svg_path, write_to=png, output_width=1600, background_color='white')
    print('Wrote', png_name)
