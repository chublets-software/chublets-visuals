"""S11, S15 -- the architecture of chublets.software: sources, tables, data model, outputs.

Reads: py/model_data.py. Produces: img/chublets-software-architecture.svg / .png

Runnable standalone: `python py/step_architecture.py`
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
from visuals_utils import CATEGORY_COLORS, FOUR_STEPS  # noqa: E402

NAME = "chublets-software-architecture"
NEUTRAL = CATEGORY_COLORS[5]


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    bw, gap, vgap = 300, 56, 56
    top = [
        ("Sources", [f"open-archaeo ({f['n_oa_entries']} entries),", "selected Wikidata items"], FOUR_STEPS[0]["color"]),
        ("Tables", ["import, mapping, merge", "and human curation"], FOUR_STEPS[1]["color"]),
        ("Data model", [f"{f['n_props']} properties, {f['n_classes']} classes,", f"{f['n_items_merged']} items, Wikidata links"], FOUR_STEPS[2]["color"]),
    ]
    h, _ = oa.row(cv, 0, 0, top, bw, gap, NEUTRAL)
    y2 = h + vgap
    x3 = 2 * (bw + gap)
    x2 = bw + gap
    x1 = 0
    for x, it in ((x1, ("Wikidata (reference)", ["identity and shared", "vocabulary, linked"], NEUTRAL)),
                  (x2, ("Discovery (planned)", ["through Wikidata", "to find.software"], NEUTRAL)),
                  (x3, ("Outputs", ["Wikibase prototype, static", "site, RDF and SPARQL"], FOUR_STEPS[3]["color"]))):
        svg, _ = fs._box(x, y2, bw, it[0], it[1], it[2], fill=0.9, size=15.5, min_h=h)
        cv.add(svg, x, y2, x + bw, y2 + h)
    a1 = fs._arrow(x3 + bw / 2, h + 3, x3 + bw / 2, y2 - 3, oa.MUTED, sw=3.5)
    cv.add(a1, x3 + bw / 2 - 8, h, x3 + bw / 2 + 8, y2)
    a2 = fs._arrow(x3 - 3, y2 + h / 2, x2 + bw + 3, y2 + h / 2, oa.MUTED, sw=3.5)
    cv.add(a2, x2 + bw, y2 + h / 2 - 8, x3, y2 + h / 2 + 8)
    a3 = fs._arrow(x1 + bw / 2, y2 - 3, x1 + bw / 2, h + 3, oa.MUTED, sw=3.5)
    cv.add(a3, x1 + bw / 2 - 8, h, x1 + bw / 2 + 8, y2)
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
