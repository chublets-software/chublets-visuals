"""S18 -- from a repository to four outputs with CoMET-RS and the export of the fork.

The right column quotes real lines from examples/unicorn in
chublets-software/comet-metadata-extraction, tag v0.4.3-chublets.2.

Reads: img/source/chublets-logo.svg, wikidata-logo.svg, connoss-logo.png.
Produces: img/chublets-repository-export.svg / .png

Runnable standalone: `python py/step_repository_export.py`
"""

from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import four_steps as fs  # noqa: E402
import model_graphics as g  # noqa: E402
import oa_graphics as oa  # noqa: E402
from visuals_utils import CATEGORY_COLORS, FOUR_STEPS, load_logo_inner_svg, tint  # noqa: E402

NAME = "chublets-repository-export"
NEUTRAL = CATEGORY_COLORS[5]
SOURCE = Path(__file__).resolve().parent.parent / "img" / "source"
INGEST, EXPORT = FOUR_STEPS[0]["color"], FOUR_STEPS[3]["color"]


def _nested(inner: str, view_w: float, view_h: float, x: float, y: float, w: float) -> str:
    h = w * view_h / view_w
    return f'<svg x="{g.f(x)}" y="{g.f(y)}" width="{g.f(w)}" height="{g.f(h)}" viewBox="0 0 {view_w} {view_h}">{inner}</svg>'


def _chublets(x: float, y: float, w: float) -> str:
    inner, view_w, view_h = load_logo_inner_svg(SOURCE / "chublets-logo.svg")
    return _nested(inner, view_w, view_h, x, y, w)


def _wikidata(x: float, y: float, w: float) -> str:
    text = (SOURCE / "wikidata-logo.svg").read_text(encoding="utf-8")
    inner = "".join(re.findall(r"<path[^>]*/>", text))
    return _nested(inner, 1052.36, 744.09, x, y, w)


def _connoss(x: float, y: float, w: float) -> str:
    data = base64.b64encode((SOURCE / "connoss-logo.png").read_bytes()).decode("ascii")
    h = w * 391 / 421
    return f'<image x="{g.f(x)}" y="{g.f(y)}" width="{g.f(w)}" height="{g.f(h)}" href="data:image/png;base64,{data}"/>'


def _badge(x: float, y: float, label: str, size: float) -> str:
    return g.text(x, y, label, size, bold=True, fill=oa.MUTED, anchor="middle")


def _result(x, y, w, h, title, status, lines, col, logo) -> str:
    out = g.rect(x, y, w, h, fill=tint(col, 0.9), stroke=col, sw=2.5, rx=10)
    out += logo
    tx = x + 100
    out += g.text(tx, y + 23, title, 17, bold=True, fill=fs.INK)
    out += g.text(x + w - 12, y + 23, status, 13.5, fill=fs.INK, anchor="end")
    out += g.rect(tx, y + 33, w - 112, h - 41, fill="#ffffff", rx=6)
    for i, line in enumerate(lines):
        out += g.text(tx + 9, y + 50 + i * 18, line, 13.5, fill=fs.INK)
    return out


def build() -> g.Canvas:
    cv = g.Canvas()
    card_h, card_gap = 124, 10
    total = 4 * card_h + 3 * card_gap
    h = 118
    top = (total - h) / 2
    mid = total / 2

    w1, w2, gap = 170, 214, 40
    x2 = w1 + gap
    svg, _ = fs._box(0, top, w1, "Repository", ["SPARQLing Unicorn", "on GitHub"], NEUTRAL, min_h=h)
    cv.add(svg, 0, top, w1, top + h)
    svg, _ = fs._box(x2, top, w2, "CoMET-RS", ["metadata with source", "and confidence"], INGEST, min_h=h)
    cv.add(svg, x2, top, x2 + w2, top + h)
    cv.add(fs._arrow(w1 + 3, mid, x2 - 3, mid, oa.MUTED, sw=3.5), w1, mid - 8, x2, mid + 8)

    xc = x2 + w2 + 66
    wc = 530
    bus = x2 + w2 + 30
    cards = (
        ("ConnOSS metadata", "CoMET-RS",
         ['"@type": "Software",', '"name": "sparqlunicornGoesGIS",', '"softwareVersion": "0.17.2",',
          '"license": {"name": "GNU General Public License v2.0"'],
         INGEST, lambda y: _connoss(xc + 14, y + 26, 72)),
        ("CodeMeta", "CoMET-RS",
         ['"@type": "SoftwareSourceCode",', '"name": "sparqlunicornGoesGIS",', '"version": "0.17.2",',
          '"license": {"name": "GNU General Public License v2.0"'],
         INGEST, lambda y: _badge(xc + 50, y + 68, "CodeMeta", 15)),
        ("QuickStatements (Wikidata)", "export",
         ['Q74005133  P1324  ".../sparqlunicornGoesGIS"', "Q74005133  P275  Q10513450", 'Q74005133  P348  "0.17.4"'],
         EXPORT, lambda y: _wikidata(xc + 12, y + 32, 78)),
        ("Turtle (chublets)", "export",
         ["chb:Q360  a wikibase:Item ;", "  chbt:P107  chb:Q934 ;", '  chbt:P148  "0.17.4" ;'],
         EXPORT, lambda y: _chublets(xc + 16, y + 22, 70)),
    )
    for i, (title, status, lines, col, logo) in enumerate(cards):
        y = i * (card_h + card_gap)
        cv.add(_result(xc, y, wc, card_h, title, status, lines, col, logo(y)), xc, y, xc + wc, y + card_h)
        cy = y + card_h / 2
        path = g.line([(x2 + w2 + 3, mid), (bus, mid), (bus, cy), (xc - 12, cy)], oa.MUTED, sw=3.5)
        cv.add(path + g.arrowhead(xc - 3, cy, 1, 0, 13, oa.MUTED), x2 + w2, min(mid, cy) - 8, xc, max(mid, cy) + 8)
    return cv


def run(strict: bool = False) -> list[str]:
    log = [g.save(NAME, build())]
    if NAME in captions.load():
        captions.render(NAME)
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
