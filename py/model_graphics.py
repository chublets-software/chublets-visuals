"""Drawing kit for the flat Wikibase data model graphics (S10 onwards).

These graphics sit directly under img/ (no block folder), carry no title,
header or footer, and are cropped to their content plus a 10 px border. Their
caption, alt text and sources live in captions.yaml (PRIMER.md A3).

The kit is small on purpose: text with measured width (the vendored Fira Sans
is measured with Pillow, so a box is as wide as its text really is), boxes,
chips, wrapped text and `save()`, which writes img/<name>.svg and .png. All
coordinates are rounded to two decimals, so the SVG text is the same on every
platform (PRIMER.md finding 16: sin/cos differ in the last digit on Linux).

Colours. Two palettes, never mixed in one element:
  * the house palette (`visuals_utils.CATEGORY_COLORS`) for everything that
    says where a property comes from (its Starter Pack status);
  * the semantic scheme (`SEM`) only for elements of the model itself: a class,
    a term, property metadata, an instance, a real object.
"""

from __future__ import annotations

import re
from functools import lru_cache

from PIL import ImageFont

from visuals_utils import (
    CATEGORY_COLORS,
    FONT_BOLD,
    FONT_FAMILY,
    FONT_REGULAR,
    IMG_DIR,
    INK,
    MUTED,
    ROOT,
    ensure_dirs,
    font_face_css,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)
from visuals_utils import esc as xml_esc

FONT_REL = "../fonts"  # from img/<name>.svg back to fonts/
MARGIN = 10
OVERSAMPLE = 2.0

# Semantic scheme (user preference, Mermaid scheme): model elements only.
SEM = {
    "class": "#9a3412",      # Class: dark orange
    "term": "#4c1d95",       # Term: dark purple
    "propmeta": "#fbbf24",   # Property metadata: amber
    "instance": "#e2e8f0",   # Subject / object: pastel grey
    "real": "#166534",       # Real object: dark green
    "owl": "#ffffff",        # OWL: white
}

# House palette for the Starter Pack status of a property.
STATUS_COLORS = {
    "crosswalked": CATEGORY_COLORS[0],        # purple: CodeMeta and Wikidata
    "codemeta-only": CATEGORY_COLORS[2],      # teal
    "wikidata-only": CATEGORY_COLORS[4],      # slate blue
    "chublets-addition": CATEGORY_COLORS[1],  # gold
    "": CATEGORY_COLORS[5],                   # neutral: no status
}


def f(v: float) -> str:
    """A coordinate with at most two decimals and no trailing zeros."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


@lru_cache(maxsize=None)
def _font(size8: int, bold: bool) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size8)


def text_w(text: str, size: float, bold: bool = False) -> float:
    """Width in px of `text` in Fira Sans at `size` px (measured at 8x)."""
    return _font(int(round(size * 8)), bold).getlength(text) / 8


def wrap(text: str, size: float, max_w: float, bold: bool = False) -> list[str]:
    """Greedy word wrap to `max_w` px, measured with the real font."""
    lines: list[str] = []
    cur = ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and text_w(trial, size, bold) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def text(x: float, y: float, s: str, size: float = 14, bold: bool = False, fill: str = INK,
         anchor: str = "start", italic: bool = False, opacity: float | None = None) -> str:
    extra = ""
    if bold:
        extra += ' font-weight="700"'
    if italic:
        extra += ' font-style="italic"'
    if opacity is not None:
        extra += f' fill-opacity="{f(opacity)}"'
    return (
        f'<text x="{f(x)}" y="{f(y)}" font-family="{FONT_FAMILY}, sans-serif" '
        f'font-size="{f(size)}"{extra} fill="{fill}" text-anchor="{anchor}">{xml_esc(s)}</text>'
    )


def rect(x: float, y: float, w: float, h: float, fill: str = "none", stroke: str = "none",
         sw: float = 1.5, rx: float = 8, dash: str | None = None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    st = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke != "none" else ""
    return (
        f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" '
        f'fill="{fill}"{st}{d}/>'
    )


def line(points: list[tuple[float, float]], stroke: str = MUTED, sw: float = 1.6,
         dash: str | None = None) -> str:
    d = " ".join(("M" if i == 0 else "L") + f"{f(x)},{f(y)}" for i, (x, y) in enumerate(points))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{f(sw)}" '
        f'stroke-linejoin="round" stroke-linecap="round"{da}/>'
    )


def arrowhead(x: float, y: float, dx: float, dy: float, size: float = 11, fill: str = MUTED) -> str:
    """Filled arrowhead with its tip at (x, y), pointing along the unit vector (dx, dy)."""
    nx, ny = -dy, dx
    bx, by = x - dx * size, y - dy * size
    w = size * 0.45
    return (
        f'<path d="M{f(x)},{f(y)} L{f(bx + nx * w)},{f(by + ny * w)} L{f(bx - nx * w)},{f(by - ny * w)} z" '
        f'fill="{fill}"/>'
    )


def triangle_left(x: float, y: float, size: float = 13, fill: str = "#ffffff", stroke: str = MUTED) -> str:
    """Open triangle whose tip is at (x, y), pointing left (towards a parent to the left)."""
    h = size / 2
    return (
        f'<path d="M{f(x)},{f(y)} L{f(x + size)},{f(y - h)} L{f(x + size)},{f(y + h)} z" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
    )


def chip(x: float, y: float, label: str, size: float = 11.5, fill: str = "#ffffff", stroke: str = "none",
         color: str = INK, dash: str | None = None, pad: float = 7, h: float | None = None,
         bold: bool = False, anchor_right: bool = False) -> tuple[str, float]:
    """A small rounded label. Returns (svg, width). With `anchor_right`, x is the right edge."""
    w = text_w(label, size, bold) + 2 * pad
    hh = h or size + 8
    x0 = x - w if anchor_right else x
    svg = rect(x0, y, w, hh, fill=fill, stroke=stroke, sw=1.2, rx=hh / 2, dash=dash)
    svg += text(x0 + w / 2, y + hh / 2 + size * 0.35, label, size, bold=bold, fill=color, anchor="middle")
    return svg, w


class Canvas:
    """Collects SVG parts and the extent they cover, then crops to it plus MARGIN."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.x0 = self.y0 = float("inf")
        self.x1 = self.y1 = float("-inf")

    def add(self, svg: str, x0: float, y0: float, x1: float, y1: float) -> None:
        self.parts.append(svg)
        self.x0, self.y0 = min(self.x0, x0), min(self.y0, y0)
        self.x1, self.y1 = max(self.x1, x1), max(self.y1, y1)

    def svg(self) -> tuple[str, float, float]:
        ox, oy = MARGIN - self.x0, MARGIN - self.y0
        w = self.x1 - self.x0 + 2 * MARGIN
        h = self.y1 - self.y0 + 2 * MARGIN
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(w)}" height="{f(h)}" '
            f'viewBox="0 0 {f(w)} {f(h)}">'
        )
        body = f'<g transform="translate({f(ox)},{f(oy)})">' + "\n".join(self.parts) + "</g>"
        return head + font_face_css(FONT_REL) + body + "</svg>", w, h


# A graphic has to be readable in the paper without the code (PRIMER.md A4): the starting set the
# model was begun from is not named in any graphic.
_FORBIDDEN = re.compile(r"starter[ -]?(pack|kit)|\bthe pack\b", re.IGNORECASE)


def save(name: str, canvas: Canvas) -> str:
    """Write img/<name>.svg and .png (transparent, 10 px border); returns a log line."""
    ensure_dirs(IMG_DIR)
    svg, w, h = canvas.svg()
    hit = _FORBIDDEN.search(svg)
    if hit:
        raise ValueError(f"{name}: the graphic contains {hit.group(0)!r}, which must not appear in a graphic")
    svg_path = IMG_DIR / f"{name}.svg"
    svg_path.write_text(svg + "\n", encoding="utf-8", newline="\n")
    png_path = svg_path.with_suffix(".png")
    render_svg_to_png(svg_path, png_path, int(w * OVERSAMPLE), int(h * OVERSAMPLE))
    fw, fh = trim_transparent_border(png_path, margin_px=10)
    return f"wrote {svg_path.relative_to(ROOT)} + .png ({fw}x{fh}, transparent, <=10px border)"
