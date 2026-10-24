"""the four FAIR principles as one collage.

Reads: py/model_data.py, py/fair_panels.py. Produces: img/chublets-four-steps.svg / .png

Runnable standalone: `python py/step_fair_pattern.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import fair_panels  # noqa: E402
import four_steps  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402

NAME = "chublets-fair"


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    hs = fair_panels.heights(f)
    gap, top = 40, max(hs)
    for i in range(4):
        svg, w, h = fair_panels.panel(i, f, top)
        x = i * (four_steps.PW + gap)
        cv.add(f'<g transform="translate({x},0)">' + svg + "</g>", x, 0, x + w, h)
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
