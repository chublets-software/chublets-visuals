"""S11 -- the four steps of the chublets pipeline as one collage.

Reads: py/model_data.py, py/four_steps.py. Produces: img/chublets-four-steps.svg / .png

Runnable standalone: `python py/step_pattern.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import four_steps  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402

NAME = "chublets-four-steps"


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    hs = four_steps.heights(f)
    gap, top = 70, max(hs)
    for i in range(4):
        svg, w, h = four_steps.panel(i, f, top)
        x = i * (four_steps.PW + gap)
        cv.add(f'<g transform="translate({x},0)">' + svg + "</g>", x, 0, x + w, h)
        if i < 3:
            ax = x + w + 8
            cv.add(four_steps._arrow(ax, 33, ax + gap - 16, 33, "#64748b", sw=4), ax, 20, ax + gap - 16, 46)
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
