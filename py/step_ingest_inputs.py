"""S11 -- step 1, Ingest: the three entry points.

Reads: py/model_data.py, py/four_steps.py. Produces: img/chublets-step-ingest.svg / .png

Runnable standalone: `python py/step_ingest_inputs.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import four_steps  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402

NAME = "chublets-step-ingest"


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    svg, w, h = four_steps.panel(0, f)
    cv.add(svg, 0, 0, w, h)
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
