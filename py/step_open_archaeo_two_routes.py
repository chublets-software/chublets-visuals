"""S11 -- how open-archaeo is split into an OpenRefine and a Python slice.

Reads: py/model_data.py. Produces: img/open-archaeo-two-routes.svg / .png

Runnable standalone: `python py/step_open_archaeo_two_routes.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
import oa_graphics as oa  # noqa: E402
import four_steps as fs  # noqa: E402
from visuals_utils import CATEGORY_COLORS, MUTED  # noqa: E402

NAME = "open-archaeo-two-routes"
GREY, TEAL, PURPLE = CATEGORY_COLORS[5], CATEGORY_COLORS[2], CATEGORY_COLORS[0]
N_CSV = 562  # entries of open-archaeo.csv, read from the repository (PRIMER.md S6b)


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    n = f["n_oa_entries"]  # the software subset; the demo imports exactly these
    assert n % 2 == 0, "the split gives two equal halves"
    half = n // 2
    bw, gap = 300, 56
    top = [("open-archaeo.csv", [f"{N_CSV} entries"]), ("transform", [f"{n} software entries"]), ("split", ["stratified, deterministic"])]
    h1, cs = oa.row(cv, 0, 0, top, bw, gap, GREY)
    total = 3 * bw + 2 * gap
    two = [("OpenRefine slice", [f"{half} entries", "out/OpenRefine/"], TEAL), ("Python slice", [f"{half} entries", "out/Python/"], PURPLE)]
    bw2 = 340
    y2 = h1 + 90
    xs = [(total - (2 * bw2 + 80)) / 2 + i * (bw2 + 80) for i in range(2)]
    h2 = 0
    for x, (t, ls, c) in zip(xs, two):
        svg, h = fs._box(x, y2, bw2, t, ls, c, tsize=21)
        cv.add(svg, x, y2, x + bw2, y2 + h)
        h2 = h
        cv.add(fs._arrow(cs[2], h1 + 3, x + bw2 / 2, y2 - 3, MUTED, sw=3), min(cs[2], x + bw2 / 2), h1, max(cs[2], x + bw2 / 2), y2)
    y3 = y2 + h2 + 90
    bw3 = 480
    x3 = (total - bw3) / 2
    svg, h3 = fs._box(x3, y3, bw3, "Shared vocabulary and concordance", ["vocabulary.json (from OpenRefine) and concordance.csv (id, qid)"], GREY, fill=0.84)
    cv.add(svg, x3, y3, x3 + bw3, y3 + h3)
    for x in xs:
        cv.add(fs._arrow(x + bw2 / 2, y2 + h2 + 3, x3 + bw3 / 2, y3 - 3, MUTED, sw=3), min(x + bw2 / 2, x3 + bw3 / 2), y2 + h2, max(x + bw2 / 2, x3 + bw3 / 2), y3)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
