"""
Render the BACK of the cheat sheet — "How They Work": one compact pattern card
per algorithm, each with a coloured header + complexity badge, a one-line idea,
and a minimal code template. Source: algorithms.yaml.

Mirrors the front's visual language (white rounded boxes, coloured left band,
the FAMILY palette) and its automatic 4-column balancing. Produces an SVG that
build.py renders into the second PDF page.
"""
import os, html as H, itertools as _it
import yaml
from config import FAMILY
from textmetrics import tw, wrap, mono_w

HERE = os.path.dirname(os.path.abspath(__file__))

# --- shared canvas geometry (same as the front) ---------------------------
W = 1403
M = 26
NCOL = 4
GUT = 14
COLW = (W - 2*M - (NCOL-1)*GUT) / NCOL
TOP = 86

# --- card metrics ----------------------------------------------------------
PAD = 11          # inner padding of a card
BAND = 4.5        # coloured left band width
NAME_F = 13.5     # header font
BADGE_F = 9.5     # complexity badge font
IDEA_F = 10.0     # idea line font
IDEA_LH = 13.0
CODE_F = 9.0      # code font
CODE_LH = 12.6
CODE_PAD = 7      # padding inside the code strip


def esc(s):
    return H.escape(s)


def _load(src=None):
    path = src or os.path.join(HERE, 'algorithms.yaml')
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def _split_comment(line):
    """Split a code line into (code, comment) on the first '#'. The templates
    never put '#' inside a string, so a plain split is safe."""
    i = line.find('#')
    if i < 0:
        return line, ''
    return line[:i], line[i:]


def draw_card(card, ox, oy, emit, frag):
    famc = card.get('family', 'other')
    fill, band, fg = FAMILY.get(famc, FAMILY['other'])
    inner_x = ox + PAD + BAND + 2
    cw = COLW - (PAD + BAND + 2) - PAD          # usable text width
    y = oy + PAD

    # header: name (left, may wrap) + complexity badge (right)
    badge = card.get('big_o', '')
    badge_w = tw(badge, BADGE_F, True) + 14 if badge else 0
    name_w = cw - (badge_w + 8 if badge else 0)
    name_lines = wrap(card['name'], NAME_F, name_w, True)
    if emit:
        for i, ln in enumerate(name_lines):
            frag.append(f'<text x="{inner_x:.1f}" y="{y+12+i*15:.1f}" '
                        f'font-size="{NAME_F}" font-weight="700" fill="#2C2C2A">{esc(ln)}</text>')
        if badge:
            bx = ox + COLW - PAD - badge_w
            frag.append(f'<rect x="{bx:.1f}" y="{y:.1f}" width="{badge_w:.1f}" height="16" '
                        f'rx="8" fill="{fill}" stroke="{band}" stroke-width="0.8"/>')
            frag.append(f'<text x="{bx+badge_w/2:.1f}" y="{y+11.5:.1f}" font-size="{BADGE_F}" '
                        f'font-weight="700" fill="{fg}" text-anchor="middle">{esc(badge)}</text>')
    y += 16 + (len(name_lines) - 1) * 15 + 6

    # idea line(s)
    for ln in wrap(card['idea'], IDEA_F, cw):
        if emit:
            frag.append(f'<text x="{inner_x:.1f}" y="{y+8:.1f}" font-size="{IDEA_F}" '
                        f'fill="#7A7972">{esc(ln)}</text>')
        y += IDEA_LH

    # optional concrete example, under the idea (italic)
    ex = card.get('example')
    if ex:
        y += 2
        for ln in wrap('Example: ' + ex, IDEA_F, cw):
            if emit:
                frag.append(f'<text x="{inner_x:.1f}" y="{y+8:.1f}" font-size="{IDEA_F}" '
                            f'fill="#6E6D67" font-style="italic">{esc(ln)}</text>')
            y += IDEA_LH
    y += 5

    # code strip
    lines = card['code'].rstrip('\n').split('\n')
    cf = CODE_F
    longest = max((mono_w(ln, cf) for ln in lines), default=0)
    text_w = cw + PAD - 2*CODE_PAD            # the strip spans nearly the full card
    if longest > text_w:                       # shrink to fit, just in case
        cf = max(7.5, CODE_F * text_w / longest)
    strip_x = inner_x - 4
    strip_w = ox + COLW - PAD - strip_x
    strip_h = len(lines) * CODE_LH + 2*CODE_PAD
    if emit:
        frag.append(f'<rect x="{strip_x:.1f}" y="{y:.1f}" width="{strip_w:.1f}" height="{strip_h:.1f}" '
                    f'rx="5" fill="{fill}" fill-opacity="0.55" stroke="{band}" stroke-width="0.6" stroke-opacity="0.5"/>')
        ty = y + CODE_PAD + cf
        for ln in lines:
            code, comment = _split_comment(ln)
            tx = strip_x + CODE_PAD
            frag.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{cf:.1f}" '
                        f'font-family="Menlo, Consolas, &quot;DejaVu Sans Mono&quot;, &quot;Liberation Mono&quot;, monospace" '
                        f'fill="#2C2C2A" xml:space="preserve">{esc(code)}</text>')
            if comment:
                frag.append(f'<text x="{tx+mono_w(code, cf):.1f}" y="{ty:.1f}" font-size="{cf:.1f}" '
                            f'font-family="Menlo, Consolas, &quot;DejaVu Sans Mono&quot;, &quot;Liberation Mono&quot;, monospace" '
                            f'fill="{fg}" fill-opacity="0.7" font-style="italic" xml:space="preserve">{esc(comment)}</text>')
            ty += CODE_LH
    y += strip_h + PAD

    total_h = y - oy
    if emit:
        frag.insert(frag_box_marker[0],
          f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{COLW:.1f}" height="{total_h:.1f}" rx="9" '
          f'fill="#ffffff" stroke="#D3D1C7" stroke-width="0.8"/>'
          f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{BAND}" height="{total_h:.1f}" rx="{BAND/2:.2f}" fill="{band}"/>')
    return total_h


frag_box_marker = [0]


def _balance(heights, ncol, top, gap):
    """Split the cards into NCOL *contiguous* segments (preserving YAML order
    left-to-right, top-to-bottom) and pick the split with the shortest tallest
    column, then smallest spread. With ~15 cards this enumerates only the
    C(n-1, ncol-1) cut positions — fast, unlike the front's full assignment."""
    n = len(heights)
    best = None
    for cuts in _it.combinations(range(1, n), ncol - 1):
        bounds = (0,) + cuts + (n,)
        segs = [list(range(bounds[k], bounds[k+1])) for k in range(ncol)]
        if any(len(s) == 0 for s in segs):
            continue
        hh = [top + sum(heights[i] for i in s) + gap*len(s) for s in segs]
        key = (max(hh), max(hh) - min(hh))
        if best is None or key < best[0]:
            best = (key, segs)
    return {i: c for c, seg in enumerate(best[1]) for i in seg}


def build_back_svg(out_path=None, src=None, cards=None):
    if cards is None:
        cards = _load(src)
    heights = [draw_card(c, 0, 0, False, []) for c in cards]
    assign = _balance(heights, NCOL, TOP, 11)

    colY = [TOP]*NCOL
    place = []
    for i in range(len(cards)):
        c = assign[i]
        x = M + c*(COLW + GUT)
        place.append((c, x, colY[c], i))
        colY[c] += heights[i] + 11

    pageH = max(colY) + M + 48

    frag = []
    for (c, x, y, i) in place:
        frag_box_marker[0] = len(frag)
        draw_card(cards[i], x, y, True, frag)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{pageH:.0f}" '
           f'viewBox="0 0 {W} {pageH:.0f}" font-family="Arial, Helvetica, sans-serif">']
    svg.append(f'<rect x="0" y="0" width="{W}" height="{pageH:.0f}" fill="#ffffff"/>')
    svg.append(f'<text x="{M}" y="38" font-size="21" font-weight="700" fill="#2C2C2A">Algorithm Cheat Sheet · How They Work</text>')
    svg.append(f'<text x="{M}" y="58" font-size="11" fill="#5F5E5A">The mechanism behind each technique on the front — minimal Python-ish templates, not full implementations. Badge = typical time complexity.</text>')
    svg.append(f'<line x1="{M}" y1="70" x2="{W-M}" y2="70" stroke="#D3D1C7" stroke-width="1"/>')
    svg += frag

    fy = max(colY) + 26
    svg.append(f'<line x1="{M}" y1="{fy-15:.0f}" x2="{W-M}" y2="{fy-15:.0f}" stroke="#D3D1C7" stroke-width="1"/>')
    svg.append(f'<text x="{M}" y="{fy:.0f}" font-size="11" font-weight="700" fill="#888780">FAMILY</text>')
    legend = [('graph', 'graph/traversal'), ('search', 'search'), ('pointer', 'pointers/window'),
              ('heap', 'heap/sort/interval'), ('dp', 'dynamic prog.'), ('exhaust', 'brute/backtrack'),
              ('stack', 'stack'), ('other', 'other')]
    lx = M + 62
    for k, lab in legend:
        fill, band, fg = FAMILY[k]
        svg.append(f'<rect x="{lx:.0f}" y="{fy-10:.0f}" width="11" height="11" rx="3" fill="{fill}" stroke="{band}" stroke-width="0.8"/>')
        svg.append(f'<text x="{lx+16:.0f}" y="{fy:.0f}" font-size="11" fill="#5F5E5A">{lab}</text>')
        lx += 17 + tw(lab, 11) + 16
    svg.append(f'<text x="{W-M:.0f}" y="{fy:.0f}" font-size="9.5" fill="#888780" font-style="italic" text-anchor="end">Pseudocode — 0-indexed, adapt to your language · grey = comment</text>')
    svg.append('</svg>')

    if out_path is None:
        out_path = os.path.join(HERE, 'algorithm-cheat-sheet-back.svg')
    open(out_path, 'w').write('\n'.join(svg))
    print('back  pageH', round(pageH), 'cols', [round(c) for c in colY])
    return out_path


if __name__ == '__main__':
    build_back_svg()
