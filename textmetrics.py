"""Shared text-measurement helpers for the cheat-sheet builders.

The SVGs declare metric-compatible font stacks; here we resolve a real TTF per
style (regular / bold / mono) so pills and code blocks hug their text identically
across platforms. The first existing path wins; override any of them with the
ALGOSEL_FONT_REGULAR / ALGOSEL_FONT_BOLD / ALGOSEL_FONT_MONO environment
variables to point at any compatible TTF.
"""
import os
from PIL import ImageFont

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
    'mono': [
        os.environ.get('ALGOSEL_FONT_MONO'),
        # Linux
        '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
        '/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf',
        # macOS
        '/System/Library/Fonts/Menlo.ttc',
        '/System/Library/Fonts/Monaco.ttf',
        '/System/Library/Fonts/Supplemental/Courier New.ttf',
        # Windows
        'C:\\Windows\\Fonts\\consola.ttf',
        'C:\\Windows\\Fonts\\cour.ttf',
        # Last-resort fallback
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    ],
}


def _resolve_font(kind):
    for path in _FONT_CANDIDATES[kind]:
        if path and os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"No {kind} font found. Install Liberation fonts (Linux: `fonts-liberation`) "
        f"or set the ALGOSEL_FONT_{kind.upper()} environment variable to a TTF path.")


_PATHS = {k: _resolve_font(k) for k in _FONT_CANDIDATES}
_cache = {}


def _face(kind, size):
    key = (kind, round(size))
    f = _cache.get(key)
    if f is None:
        f = ImageFont.truetype(_PATHS[kind], int(round(size)))
        _cache[key] = f
    return f


def measure(s, size, bold=False):
    return _face('bold' if bold else 'regular', size).getbbox(s)[2]


def tw(s, size, bold=False):
    return measure(s, size, bold)


def mono_w(s, size):
    """Width of a monospace string at the given size."""
    return _face('mono', size).getbbox(s)[2]


def wrap(s, size, maxw, bold=False):
    words = s.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if tw(t, size, bold) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines
