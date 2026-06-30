"""
Render the FRONT of the cheat sheet — "Which to Use": the selection flow that
maps a clue in the problem statement to the technique to reach for. Source:
flowchart.yaml.

Counterpart to back.py: each builder owns one page and exposes build_*_svg();
build.py orchestrates the two into a single A4-landscape PDF. Shared colours live
in config.py and text measurement in textmetrics.py.
"""
import os, html as H, itertools as _it
import yaml
from config import FAMILY, fam, KEYWORDS
from textmetrics import measure, tw, wrap

HERE = os.path.dirname(os.path.abspath(__file__))

# --- shared canvas geometry (same as the back) -----------------------------
W = 1403
M = 26
NCOL = 4
GUT = 14
COLW = (W - 2*M - (NCOL-1)*GUT) / NCOL
TOP = 86

PILL_H = 21
SEC_PAD = 11
SEC_TITLE_H = 28
KW_LH = 13.5
GAP_ROW = 8
QF = 12.0     # question font
TF = 12.0     # pill text font
KF = 10.5     # keyword font
LINE_Q = 15   # line height for wrapped question text


def esc(s):
    return H.escape(s)


# --- load flowchart.yaml into the row-tuple format the renderer consumes ----
# Row tuples:
#   ('qn', question, [subrows])        nested question; Yes leads into subrows
#   ('q',  question, technique)        Yes -> technique, No falls through
#   ('q2', question, techYes, techNo)  Yes -> techYes, No -> techNo
#   ('end', 'Otherwise', technique)    fall-through default
#   ('note', text)                     plain note line
# The YAML carries `when:` phrases; we copy them into KEYWORDS at load time so
# the renderer shows them under each pill.

def _fam_hint(title):
    t = title.lower()
    if 'graph' in t: return 'graph'
    if 'sorted' in t or 'search' in t: return 'search'
    if 'linked' in t: return 'pointer'
    if 'lookup' in t: return 'heap'
    if 'small' in t: return 'exhaust'
    if 'subarray' in t or 'window' in t: return 'pointer'
    if 'max' in t: return 'dp'
    if 'count' in t: return 'dp'
    return 'other'


def _tech(d):
    name = d['use']
    when = d.get('when', '') or ''
    if when:
        KEYWORDS[name] = when
    return name


def _step(node):
    if 'note' in node:
        return ('note', node['note'])
    if 'otherwise' in node:
        return ('end', 'Otherwise', _tech(node['otherwise']))
    if 'then' in node:
        return ('qn', node['ask'], [_step(s) for s in node['then']])
    q = node['ask']
    if 'if_no' in node:
        return ('q2', q, _tech(node['if_yes']), _tech(node['if_no']))
    return ('q', q, _tech(node['if_yes']))


def build_sections(src=None):
    path = src or os.path.join(HERE, 'flowchart.yaml')
    with open(path, encoding='utf-8') as f:
        doc = yaml.safe_load(f)
    out = []
    for sec in doc:
        rows = [_step(s) for s in sec['steps']]
        out.append((sec['section'], _fam_hint(sec['section']), rows))
    return out


# --- rendering --------------------------------------------------------------
def pill(x, y, text, frag, maxw):
    fill, band, fg = FAMILY[fam(text)]
    fs = TF
    pad = 11
    w = tw(text, fs, True) + pad*2
    if w > maxw:
        fs = max(9.0, TF*(maxw-pad*2)/(w-pad*2)); w = tw(text, fs, True) + pad*2
    frag.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{PILL_H}" rx="{PILL_H/2:.1f}" fill="{fill}" stroke="{band}" stroke-width="0.8"/>')
    frag.append(f'<text x="{x+w/2:.1f}" y="{y+PILL_H/2+4.2:.1f}" font-size="{fs:.1f}" font-weight="600" fill="{fg}" text-anchor="middle">{esc(text)}</text>')
    return w


def kw_under(x, y, text, maxw, frag, emit):
    kw = KEYWORDS.get(text, '')
    if not kw: return 0
    # ` || ` forces a line break between trigger phrases; each segment still wraps on width.
    lines = [ln for seg in kw.split(' || ') for ln in wrap(seg, KF, maxw)][:2]
    for ln in lines:
        if emit:
            frag.append(f'<text x="{x:.1f}" y="{y+8:.1f}" font-size="{KF}" fill="#888780" font-style="italic">{esc(ln)}</text>')
        y += KW_LH
    return len(lines)*KW_LH


frag_box_marker = [0]


def draw_section(sec, ox, oy, emit, frag):
    title, band_fam, rows = sec
    bandc = FAMILY[band_fam][1]
    x = ox + SEC_PAD + 7
    cw = COLW - SEC_PAD*2 - 7
    y = oy + SEC_PAD
    if emit:
        for i, ln in enumerate(wrap(title, 13.5, cw-2, True)):
            frag.append(f'<text x="{x:.1f}" y="{y+13+ i*15:.1f}" font-size="13.5" font-weight="700" fill="#2C2C2A">{esc(ln)}</text>')
    th = len(wrap(title, 13.5, cw-2, True))
    y += SEC_TITLE_H + (th-1)*15

    def emit_pill_row(tag, tc, tech, rx, rw, gap=GAP_ROW):
        nonlocal y
        y += 2  # gap between question text and pill
        if emit:
            frag.append(f'<text x="{rx+4:.1f}" y="{y+PILL_H/2+4:.1f}" font-size="9.0" fill="{tc}" font-weight="600">{tag}</text>')
            pill(rx+23, y, tech, frag, rw-23)
        kh = kw_under(rx+23, y+PILL_H+4, tech, rw-23, frag, emit)
        y += PILL_H + 4 + kh + gap

    def rows_draw(rows, depth):
        nonlocal y
        ind = depth*11
        rx = x+ind; rw = cw-ind
        for r in rows:
            k = r[0]
            if k == 'note':
                for ln in wrap(r[1], 10, rw):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+9:.1f}" font-size="10" fill="#888780" font-style="italic">{esc(ln)}</text>')
                    y += 11.5
            elif k == 'qn':
                for ln in wrap(r[1], QF, rw, True):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+10:.1f}" font-size="{QF}" font-weight="600" fill="#534AB7">{esc(ln)}</text>')
                    y += LINE_Q
                y += GAP_ROW  # same lead-in a pill gives the next question, so a grouping header isn't tighter
                rows_draw(r[2], depth+1)
            elif k in ('q', 'end'):
                q, tech = r[1], r[2]
                for ln in wrap(q, QF, rw):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+10:.1f}" font-size="{QF}" fill="#444441">{esc(ln)}</text>')
                    y += LINE_Q
                tag = 'Yes' if k == 'q' else '·'
                tc = '#1D9E75' if k == 'q' else '#888780'
                emit_pill_row(tag, tc, tech, rx, rw)
            elif k == 'q2':
                q = r[1]
                for ln in wrap(q, QF, rw):
                    if emit: frag.append(f'<text x="{rx:.1f}" y="{y+10:.1f}" font-size="{QF}" fill="#444441">{esc(ln)}</text>')
                    y += LINE_Q
                emit_pill_row('Yes', '#1D9E75', r[2], rx, rw, gap=0)  # Yes+No share a question: keep them tight
                emit_pill_row('No', '#D85A30', r[3], rx, rw)

    rows_draw(rows, 0)
    y += SEC_PAD
    total_h = y-oy
    if emit:
        frag.insert(frag_box_marker[0],
          f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{COLW:.1f}" height="{total_h:.1f}" rx="9" fill="#ffffff" stroke="#D3D1C7" stroke-width="0.8"/>'
          f'<rect x="{ox:.1f}" y="{oy:.1f}" width="4.5" height="{total_h:.1f}" rx="2.25" fill="{bandc}"/>')
    return total_h


def _balance(heights, ncol, top, gap):
    """Search every way to assign sections to NCOL columns and pick the one with
    the shortest tallest-column (then smallest spread). Re-balances itself
    whenever flowchart.yaml changes. With ~9 sections × 4 columns the search is
    tiny (4^9). Sections keep reading order within each column."""
    n = len(heights)
    best = None
    for combo in _it.product(range(ncol), repeat=n):
        cols = [[] for _ in range(ncol)]
        for i, c in enumerate(combo):
            cols[c].append(i)
        if any(len(c) == 0 for c in cols):
            continue
        hh = [top + sum(heights[i] for i in c) + gap*len(c) for c in cols]
        key = (max(hh), max(hh) - min(hh))
        if best is None or key < best[0]:
            best = (key, combo)
    return {i: best[1][i] for i in range(n)}


def build_front_svg(out_path=None, src=None):
    sections = build_sections(src)
    heights = [draw_section(s, 0, 0, False, []) for s in sections]
    assign = _balance(heights, NCOL, TOP, 11)

    colY = [TOP]*NCOL
    place = []
    for i in range(len(sections)):
        c = assign[i]; x = M + c*(COLW+GUT)
        place.append((c, x, colY[c], i)); colY[c] += heights[i] + 11

    pageH = max(colY) + M + 48

    frag = []
    for (c, x, y, i) in place:
        frag_box_marker[0] = len(frag)
        draw_section(sections[i], x, y, True, frag)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{pageH:.0f}" viewBox="0 0 {W} {pageH:.0f}" font-family="Arial, Helvetica, sans-serif">')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{pageH:.0f}" fill="#ffffff"/>')
    svg.append(f'<text x="{M}" y="38" font-size="21" font-weight="700" fill="#2C2C2A">Algorithm Cheat Sheet · Which to Use</text>')
    # subtitle: right-aligned beside the title, sharing its baseline (bottoms colinear)
    _sub = "Find the first matching clue, then take the technique it points to. Italic phrases under each pill are the words to look for in the problem statement. Inspired by AlgoMonster’s flowchart."
    svg.append(f'<text x="{W-M:.0f}" y="38" font-size="11" fill="#5F5E5A" text-anchor="end">{esc(_sub)}</text>')
    # divider below the title/subtitle row, then the constraints strip beneath it
    svg.append(f'<line x1="{M}" y1="52" x2="{W-M}" y2="52" stroke="#D3D1C7" stroke-width="1"/>')
    # constraints → complexity — the first filter: n caps the complexity you can afford
    _sy = 66
    _bk = [('n ≤ 12', 'O(n!)'), ('≤ 20', 'O(2ⁿ)'), ('≤ 500', 'O(n³)'), ('≤ 5000', 'O(n²)'),
           ('≤ 10^6', 'O(n log n)'), ('≤ 10^8', 'O(n)'), ('≥ 10^9', 'O(log n)')]
    _head = ('<tspan font-weight="700" fill="#888780">CONSTRAINTS </tspan>'
             '<tspan dy="-1.2">→</tspan><tspan dy="1.2">'
             '<tspan font-weight="700" fill="#888780"> COMPLEXITY</tspan></tspan>')
    _pairs = '   ·   '.join(
        f'<tspan font-weight="700" fill="#3A3A37">{esc(th)}</tspan> '
        f'<tspan dy="-1.2">→</tspan><tspan dy="1.2"> {esc(cx)}</tspan>'
        for th, cx in _bk)
    svg.append(f'<text x="{M}" y="{_sy}" font-size="10.5" fill="#5F5E5A" xml:space="preserve">{_head}      {_pairs}</text>')
    svg.append(f'<text x="{W-M:.0f}" y="{_sy}" font-size="9.5" fill="#888780" font-style="italic" text-anchor="end">rough budget ~10^8 ops/s · Python ~10^7 · memory ~256 MB</text>')
    svg += frag
    fy = max(colY) + 26
    svg.append(f'<line x1="{M}" y1="{fy-15:.0f}" x2="{W-M}" y2="{fy-15:.0f}" stroke="#D3D1C7" stroke-width="1"/>')
    svg.append(f'<text x="{M}" y="{fy:.0f}" font-size="11" font-weight="700" fill="#888780">FAMILY</text>')
    legend = [('graph', 'graph/traversal'), ('search', 'search'), ('pointer', 'pointers/window'), ('heap', 'heap/sort/interval'), ('dp', 'dynamic prog.'), ('exhaust', 'brute/backtrack'), ('stack', 'stack'), ('other', 'other')]
    lx = M + 62
    for k, lab in legend:
        fill, band, fg = FAMILY[k]
        svg.append(f'<rect x="{lx:.0f}" y="{fy-10:.0f}" width="11" height="11" rx="3" fill="{fill}" stroke="{band}" stroke-width="0.8"/>')
        svg.append(f'<text x="{lx+16:.0f}" y="{fy:.0f}" font-size="11" fill="#5F5E5A">{lab}</text>')
        lx += 17 + tw(lab, 11) + 16
    svg.append(f'<text x="{W-M:.0f}" y="{fy:.0f}" font-size="9.5" fill="#888780" font-style="italic" text-anchor="end">Yes (green) take it · No (orange) alternative · purple = grouping question · · = fall-through default</text>')
    svg.append('</svg>')

    if out_path is None:
        out_path = os.path.join(HERE, 'algorithm-cheat-sheet.svg')
    open(out_path, 'w').write('\n'.join(svg))
    print('front pageH', round(pageH), 'aspect', round(W/pageH, 3), '(A4 land 1.414)', 'cols', [round(c) for c in colY])
    return out_path


if __name__ == '__main__':
    build_front_svg()
