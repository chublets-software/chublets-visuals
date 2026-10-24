"""S11 -- the steps of the open-archaeo Wikidata pipeline (`all`).

Reads: py/open_archaeo_data.py, data/raw/open-archaeo/wikidata-main.py. Produces: img/open-archaeo-wikidata-pipeline.svg / .png

Runnable standalone: `python py/step_open_archaeo_pipeline.py`
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
import open_archaeo_data  # noqa: E402
from visuals_utils import CATEGORY_COLORS, DATA_RAW, MUTED  # noqa: E402

NAME = "open-archaeo-wikidata-pipeline"
COL = CATEGORY_COLORS[5]
COLS = 4
NOTE = "Left out of the run of all steps on purpose: reconcile is slow (added with --reconcile) and push writes to Wikidata, which is a decision and not automation."


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    steps = open_archaeo_data.load(DATA_RAW / "open-archaeo" / "wikidata-main.py")["all_steps"]
    bw, gap, vgap = 290, 50, 56
    items = [(name, ["reads Wikidata" if needs else "offline", desc]) for name, needs, desc in steps]
    h = max(oa.box_height(bw, t, ls) for t, ls in items)
    rows = [items[i:i + COLS] for i in range(0, len(items), COLS)]
    pos = []
    for r, chunk in enumerate(rows):
        y = r * (h + vgap)
        oa.row(cv, 0, y, chunk, bw, gap, COL, h=h, arrows=False)
        for c in range(len(chunk)):
            pos.append((c * (bw + gap), y))
    for (x1, y1), (x2, y2) in zip(pos, pos[1:]):
        if y1 == y2:
            cv.add(fs._arrow(x1 + bw + 3, y1 + h / 2, x2 - 3, y2 + h / 2, COL, sw=3.5), x1 + bw, y1 + h / 2 - 8, x2, y1 + h / 2 + 8)
        else:
            my = y1 + h + vgap / 2
            pts = [(x1 + bw / 2, y1 + h + 2), (x1 + bw / 2, my), (x2 + bw / 2, my), (x2 + bw / 2, y2 - 12)]
            cv.add(g.line(pts, COL, sw=3.5) + g.arrowhead(x2 + bw / 2, y2 - 3, 0, 1, 13, COL), min(x1, x2), y1 + h, max(x1, x2) + bw, y2)
    total = COLS * bw + (COLS - 1) * gap
    oa.note(cv, 0, len(rows) * (h + vgap) - vgap + 22, NOTE, total)
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
