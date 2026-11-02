"""S15 -- community efforts towards visible software in cultural heritage.

Reads: nothing but the shared drawing helpers. Produces: img/chublets-community-efforts.svg / .png

Runnable standalone: `python py/step_efforts.py`
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
NAME = "chublets-community-efforts"
NEUTRAL = CATEGORY_COLORS[5]


def build():
    cv = g.Canvas()
    bw, gap, vgap = 300, 56, 56
    top = [("2019: Little Minions", ["sessions: a name and", "a community, no record"], FOUR_STEPS[0]["color"]),
           ("Hungry Squirrels Ontology", ["a domain model in RDF,", "limited reach"], FOUR_STEPS[1]["color"]),
           ("open-archaeo", ["a community list: coverage,", "flat table"], FOUR_STEPS[2]["color"])]
    h, _ = oa.row(cv, 0, 0, top, bw, gap, NEUTRAL)
    y2 = h + vgap; x3 = 2 * (bw + gap); x2 = bw + gap
    for x, it in ((x3, ("Wikidata", ["global identifiers, queries,", "generic vocabulary"], FOUR_STEPS[3]["color"])),
                  (x2, ("chublets.software", ["combines them: curated,", "domain-specific, linked"], NEUTRAL))):
        svg, _ = fs._box(x, y2, bw, it[0], it[1], it[2], fill=0.9, size=15.5, min_h=h)
        cv.add(svg, x, y2, x + bw, y2 + h)
    a = fs._arrow(x3 + bw / 2, h + 3, x3 + bw / 2, y2 - 3, oa.MUTED, sw=3.5); cv.add(a, x3 + bw / 2 - 8, h, x3 + bw / 2 + 8, y2)
    a = fs._arrow(x3 - 3, y2 + h / 2, x2 + bw + 3, y2 + h / 2, oa.MUTED, sw=3.5); cv.add(a, x2 + bw, y2 + h / 2 - 8, x3, y2 + h / 2 + 8)
    x1 = 0
    svg, _ = fs._box(x1, y2, bw, "find.software (planned)", ["cross-disciplinary discovery", "through Wikidata"], NEUTRAL, fill=0.9, size=15.5, min_h=h)
    cv.add(svg, x1, y2, x1 + bw, y2 + h)
    a = fs._arrow(x2 - 3, y2 + h / 2, x1 + bw + 3, y2 + h / 2, oa.MUTED, sw=3.5); cv.add(a, x1 + bw, y2 + h / 2 - 8, x2, y2 + h / 2 + 8)
    return cv


def run(strict: bool = False) -> list[str]:
    log = [g.save(NAME, build())]
    if NAME in captions.load():
        captions.render(NAME)
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
