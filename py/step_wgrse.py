"""S15 -- the pillars and cross-cutting topics of the WG RSE, the marketplace highlighted.

Reads: nothing but the shared drawing helpers. Produces: img/wgrse-pillars.svg / .png

Runnable standalone: `python py/step_wgrse.py`
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import four_steps as fs  # noqa: E402
import model_graphics as g  # noqa: E402
import oa_graphics as oa  # noqa: E402
from visuals_utils import CATEGORY_COLORS, FOUR_STEPS  # noqa: E402
NAME = "wgrse-pillars"
NEUTRAL = CATEGORY_COLORS[5]


def build():
    cv = g.Canvas()
    SHAFT = "#5b6472"
    bw, gap = 300, 28
    W = 3 * bw + 2 * gap + 2 * 30
    x0 = 30
    svg, th = fs._box(W / 2 - 330, 0, 660, "Research Software Engineering in the", ["Research Data Infrastructure (RDI)"], NEUTRAL, fill=0.97, size=15.5)
    cv.add(svg, W / 2 - 330, 0, W / 2 + 330, th)
    y0 = th + 16
    pillars = ["as Research Data", "as FAIRification Service", "as NFDI Basic Service"]
    ph = max(oa.box_height(bw, "Research Software", [p]) for p in pillars)
    bars = []
    y = y0 + ph + 16
    for t in ("Research Software Metadata", "Research Software (Quality) Criteria", "Research Software Infrastructure / Archiving"):
        bh = oa.box_height(W, t, [])
        bars.append((y, bh, t)); y += bh + 16
    pad, head = 14, 44
    lv = [("Generic Level", ["reach across all disciplines:", "Wikidata, find.software"], FOUR_STEPS[0]["color"]),
          ("NFDI Level", ["shared standards, crosswalks,", "links between consortia"], FOUR_STEPS[1]["color"]),
          ("Domain Level", ["task vocabulary and curation:", "chublets.software"], FOUR_STEPS[2]["color"])]
    ibw = (W - 2 * pad - 2 * 16) / 3
    ih = max(oa.box_height(ibw, t, ls) for t, ls, _ in lv)
    H = head + ih + pad
    ym = y; y += H + 16
    bh = oa.box_height(W, "RSE Training + Guidelines", [])
    yt = y; y += bh + 16
    # pillar shafts run behind all bars and stay visible in the gaps
    for i in range(3):
        x = x0 + i * (bw + gap)
        cv.add(g.rect(x, y0 + ph - 6, bw, y - (y0 + ph - 6), fill=SHAFT), x, y0, x + bw, y)
        svg, _ = fs._box(x, y0, bw, "Research Software", [pillars[i]], NEUTRAL, fill=0.9, size=15.5, min_h=ph)
        cv.add(svg, x, y0, x + bw, y0 + ph)
    for by, bh2, t in bars:
        svg, _ = fs._box(0, by, W, t, [], NEUTRAL, fill=0.95, size=15.5, min_h=bh2)
        cv.add(svg, 0, by, W, by + bh2)
    c = FOUR_STEPS[3]["color"]
    cv.add(g.rect(0, ym, W, H, fill="#d9e4ee", stroke=c), 0, ym, W, ym + H)
    t = "Research Software Marketplace"
    cv.add(g.text(W / 2 - g.text_w(t, 17, True) / 2, ym + 30, t, 17, bold=True), 0, ym, W, ym + 40)
    oa.row(cv, pad, ym + head, lv, ibw, 16, NEUTRAL, h=ih, arrows=False)
    svg, _ = fs._box(0, yt, W, "RSE Training + Guidelines", [], NEUTRAL, fill=0.95, size=15.5, min_h=bh)
    cv.add(svg, 0, yt, W, yt + bh)
    svg, _ = fs._box(0, y, W, "RSE Community", [], FOUR_STEPS[0]["color"], fill=0.85, size=15.5)
    cv.add(svg, 0, y, W, y + 50)
    return cv


def run(strict: bool = False) -> list[str]:
    log = [g.save(NAME, build())]
    if NAME in captions.load():
        captions.render(NAME)
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
