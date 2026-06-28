import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_sections import SECTIONS_GEN
from config import FAMILY, fam, KEYWORDS
import html as H

W = 1403
M = 26
NCOL = 4
GUT = 14
COLW = (W - 2*M - (NCOL-1)*GUT) / NCOL
TOP = 86

def esc(s): return H.escape(s)

from PIL import ImageFont

# Resolve a Helvetica/Arial-metric-compatible TTF for text measurement. The SVG
# declares "Arial, Helvetica, sans-serif", so we measure with a metric-compatible
# face to make pills hug their labels identically across platforms. The first
# existing path wins; override with the ALGOSEL_FONT_REGULAR / ALGOSEL_FONT_BOLD
# environment variables to point at any Helvetica/Arial-like TTF.
_FONT_CANDIDATES = {
    'regular': [
        os.environ.get('ALGOSEL_FONT_REGULAR'),
        # Linux — Liberation Sans is metric-compatible with Arial
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf',
        # macOS
        '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/Library/Fonts/Arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        # Windows
        'C:\\Windows\\Fonts\\arial.ttf',
        # Last-resort fallback (metrics differ slightly but keeps the build working)
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ],
    'bold': [
        os.environ.get('ALGOSEL_FONT_BOLD'),
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/Library/Fonts/Arial Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        'C:\\Windows\\Fonts\\arialbd.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ],
}

def _resolve_font(kind):
    for path in _FONT_CANDIDATES[kind]:
        if path and os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"No {kind} Helvetica/Arial-compatible font found. Install Liberation Sans "
        f"(Linux: `liberation-fonts` / `fonts-liberation`) or set the "
        f"ALGOSEL_FONT_{kind.upper()} environment variable to a TTF path.")

_FONT_REG = _resolve_font('regular')
_FONT_BLD = _resolve_font('bold')
_cache = {}
def measure(s, size, bold=False):
    key = (round(size), bold)
    f = _cache.get(key)
    if f is None:
        f = ImageFont.truetype(_FONT_BLD if bold else _FONT_REG, int(round(size)))
        _cache[key] = f
    return f.getbbox(s)[2]

def tw(s,size,bold=False):
    return measure(s, size, bold)

PILL_H = 21
SEC_PAD = 11
SEC_TITLE_H = 28
KW_LH = 13.5
GAP_ROW = 8
QF = 12.0     # question font
TF = 12.0     # pill text font
KF = 10.5     # keyword font
LINE_Q = 15   # line height for wrapped question text

def wrap(s,size,maxw,bold=False):
    words=s.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if tw(t,size,bold)>maxw and cur: lines.append(cur); cur=w
        else: cur=t
    if cur: lines.append(cur)
    return lines

def pill(x,y,text,frag,maxw):
    fill,band,fg = FAMILY[fam(text)]
    fs = TF
    pad = 11
    w = tw(text,fs,True)+pad*2
    if w > maxw:
        fs = max(9.0, TF*(maxw-pad*2)/(w-pad*2)); w = tw(text,fs,True)+pad*2
    frag.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{PILL_H}" rx="{PILL_H/2:.1f}" fill="{fill}" stroke="{band}" stroke-width="0.8"/>')
    frag.append(f'<text x="{x+w/2:.1f}" y="{y+PILL_H/2+4.2:.1f}" font-size="{fs:.1f}" font-weight="600" fill="{fg}" text-anchor="middle">{esc(text)}</text>')
    return w

def kw_under(x,y,text,maxw,frag,emit):
    kw=KEYWORDS.get(text,'')
    if not kw: return 0
    lines=wrap(kw,KF,maxw)[:2]
    for ln in lines:
        if emit:
            frag.append(f'<text x="{x:.1f}" y="{y+8:.1f}" font-size="{KF}" fill="#888780" font-style="italic">{esc(ln)}</text>')
        y+=KW_LH
    return len(lines)*KW_LH

frag_box_marker=[0]

def draw_section(sec, ox, oy, emit, frag):
    title, band_fam, rows = sec
    bandc = FAMILY[band_fam][1]
    x = ox + SEC_PAD + 7
    cw = COLW - SEC_PAD*2 - 7
    y = oy + SEC_PAD
    if emit:
        for i,ln in enumerate(wrap(title, 13.5, cw-2, True)):
            frag.append(f'<text x="{x:.1f}" y="{y+13+ i*15:.1f}" font-size="13.5" font-weight="700" fill="#2C2C2A">{esc(ln)}</text>')
    th = len(wrap(title,13.5,cw-2,True))
    y += SEC_TITLE_H + (th-1)*15

    def emit_pill_row(tag, tc, tech, rx, rw):
        nonlocal y
        y += 2  # gap between question text and pill
        if emit:
            frag.append(f'<text x="{rx+4:.1f}" y="{y+PILL_H/2+4:.1f}" font-size="9.0" fill="{tc}" font-weight="600">{tag}</text>')
            pill(rx+23, y, tech, frag, rw-23)
        kh = kw_under(rx+23, y+PILL_H+4, tech, rw-23, frag, emit)
        y += PILL_H + 4 + kh + GAP_ROW

    def rows_draw(rows, depth):
        nonlocal y
        ind=depth*11
        rx=x+ind; rw=cw-ind
        for r in rows:
            k=r[0]
            if k=='note':
                for ln in wrap(r[1],10,rw):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+9:.1f}" font-size="10" fill="#888780" font-style="italic">{esc(ln)}</text>')
                    y+=11.5
            elif k=='qn':
                for ln in wrap(r[1],QF,rw,True):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+10:.1f}" font-size="{QF}" font-weight="600" fill="#534AB7">{esc(ln)}</text>')
                    y+=LINE_Q
                y+=1
                rows_draw(r[2], depth+1)
                y+=2
            elif k in ('q','end'):
                q,tech=r[1],r[2]
                for ln in wrap(q,QF,rw):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+10:.1f}" font-size="{QF}" fill="#444441">{esc(ln)}</text>')
                    y+=LINE_Q
                tag='Yes' if k=='q' else '·'
                tc='#1D9E75' if k=='q' else '#888780'
                emit_pill_row(tag, tc, tech, rx, rw)
            elif k=='q2':
                q=r[1]
                for ln in wrap(q,QF,rw):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+10:.1f}" font-size="{QF}" fill="#444441">{esc(ln)}</text>')
                    y+=LINE_Q
                emit_pill_row('Yes','#1D9E75',r[2],rx,rw)
                emit_pill_row('No','#D85A30',r[3],rx,rw)

    rows_draw(rows,0)
    y += SEC_PAD
    total_h=y-oy
    if emit:
        frag.insert(frag_box_marker[0],
          f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{COLW:.1f}" height="{total_h:.1f}" rx="9" fill="#ffffff" stroke="#D3D1C7" stroke-width="0.8"/>'
          f'<rect x="{ox:.1f}" y="{oy:.1f}" width="4.5" height="{total_h:.1f}" rx="2.25" fill="{bandc}"/>')
    return total_h

heights=[draw_section(s,0,0,False,[]) for s in SECTIONS_GEN]

# Automatic balanced column assignment: search all ways to assign sections to
# NCOL columns and pick the one with the shortest tallest-column (then smallest
# spread). This re-balances itself whenever you edit flowchart.yaml. With ~9
# sections and 4 columns the search is tiny (4^9). Sections keep reading order
# within each column.
import itertools as _it
def _balance(heights, ncol, top, gap):
    n = len(heights)
    best = None
    for combo in _it.product(range(ncol), repeat=n):
        cols = [[] for _ in range(ncol)]
        for i, c in enumerate(combo):
            cols[c].append(i)
        if any(len(c) == 0 for c in cols):
            continue
        H = [top + sum(heights[i] for i in c) + gap*len(c) for c in cols]
        key = (max(H), max(H) - min(H))
        if best is None or key < best[0]:
            best = (key, combo)
    return {i: best[1][i] for i in range(n)}

assign = _balance(heights, NCOL, TOP, 11)

colY=[TOP]*NCOL; place=[]
for i in range(len(SECTIONS_GEN)):
    c=assign[i]; x=M+c*(COLW+GUT); place.append((c,x,colY[c],i)); colY[c]+=heights[i]+11

pageH=max(colY)+M+48

frag=[]
for (c,x,y,i) in place:
    frag_box_marker[0]=len(frag)
    draw_section(SECTIONS_GEN[i],x,y,True,frag)

svg=[]
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{pageH:.0f}" viewBox="0 0 {W} {pageH:.0f}" font-family="Arial, Helvetica, sans-serif">')
svg.append(f'<rect x="0" y="0" width="{W}" height="{pageH:.0f}" fill="#ffffff"/>')
svg.append(f'<text x="{M}" y="38" font-size="21" font-weight="700" fill="#2C2C2A">Algorithm Selection Cheat Sheet</text>')
svg.append(f'<text x="{M}" y="58" font-size="11" fill="#5F5E5A">Find the first matching clue, then take the technique it points to. Italic phrases under each pill are the words to look for in the problem statement. Inspired by AlgoMonster\u2019s flowchart.</text>')
svg.append(f'<line x1="{M}" y1="70" x2="{W-M}" y2="70" stroke="#D3D1C7" stroke-width="1"/>')
svg+=frag
fy=max(colY)+26
svg.append(f'<line x1="{M}" y1="{fy-15:.0f}" x2="{W-M}" y2="{fy-15:.0f}" stroke="#D3D1C7" stroke-width="1"/>')
svg.append(f'<text x="{M}" y="{fy:.0f}" font-size="11" font-weight="700" fill="#888780">FAMILY</text>')
legend=[('graph','graph/traversal'),('search','search'),('pointer','pointers/window'),('heap','heap/sort/interval'),('dp','dynamic prog.'),('exhaust','brute/backtrack'),('stack','stack'),('other','other')]
lx=M+62
for k,lab in legend:
    fill,band,fg=FAMILY[k]
    svg.append(f'<rect x="{lx:.0f}" y="{fy-10:.0f}" width="11" height="11" rx="3" fill="{fill}" stroke="{band}" stroke-width="0.8"/>')
    svg.append(f'<text x="{lx+16:.0f}" y="{fy:.0f}" font-size="11" fill="#5F5E5A">{lab}</text>')
    lx+=17+tw(lab,11)+16
svg.append(f'<text x="{W-M:.0f}" y="{fy:.0f}" font-size="9.5" fill="#888780" font-style="italic" text-anchor="end">Yes (green) take it · No (orange) alternative · purple = grouping question · · = fall-through default</text>')
svg.append('</svg>')

open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'algorithm-cheat-sheet.svg'),'w').write('\n'.join(svg))
print('pageH',round(pageH),'aspect',round(W/pageH,3),'(A4 land 1.414)','cols',[round(c) for c in colY])

# ---- render SVG -> exact A4 landscape PDF ----
# cairosvg embeds a Helvetica-metric font (subsetted) and renders the SVG to
# vector PDF. It needs the native cairo library, which is NOT a pip package:
#   macOS:  brew install cairo
#   Ubuntu: sudo apt install libcairo2
import cairosvg
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from reportlab.lib.pagesizes import A4, landscape

_HERE = os.path.dirname(os.path.abspath(__file__))
_svg = os.path.join(_HERE, 'algorithm-cheat-sheet.svg')
_tmp = os.path.join(_HERE, '_content.pdf')
_out = os.path.join(_HERE, 'algorithm-cheat-sheet.pdf')

cairosvg.svg2pdf(url=_svg, write_to=_tmp)
pw, ph = landscape(A4)
src = PdfReader(_tmp).pages[0]
sw, sh = float(src.mediabox.width), float(src.mediabox.height)
m = 6
scale = min((pw - 2*m)/sw, (ph - 2*m)/sh)
tx, ty = (pw - sw*scale)/2, (ph - sh*scale)/2
w = PdfWriter()
pg = PageObject.create_blank_page(width=pw, height=ph)
pg.merge_transformed_page(src, Transformation().scale(scale).translate(tx, ty))
w.add_page(pg)
with open(_out, 'wb') as f:
    w.write(f)
os.remove(_tmp)
print('Wrote', os.path.basename(_out))

# raster preview for the README (clickable thumbnail that links to the PDF)
_png = os.path.join(_HERE, 'preview.png')
cairosvg.svg2png(url=_svg, write_to=_png, output_width=1600, background_color='white')
print('Wrote', os.path.basename(_png))
