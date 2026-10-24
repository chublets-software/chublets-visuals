"""S11 -- the Python route through the open-archaeo Wikidata session.

Reads: py/model_data.py. Produces: img/open-archaeo-python-route.svg / .png

Runnable standalone: `python py/step_open_archaeo_python_route.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
import oa_graphics as oa  # noqa: E402
from visuals_utils import CATEGORY_COLORS  # noqa: E402

NAME = "open-archaeo-python-route"
COL = CATEGORY_COLORS[0]  # purple: the Python slice, as in open-archaeo-two-routes
STAGES = [
    ("check", ["default step", "verifies Q-IDs, datatypes and duplicate claims; writes nothing"]),
    ("preview", ["docs/preview.html", "every item's statements, blocked, deferred or noted"]),
    ("reconcile", ["read-only, slow", "what Wikidata already has, by repository URL, DOI, CRAN, PyPI"]),
    ("push", ["dry run by default", "a text report of what would be written"]),
    ("push --live", ["the only step that writes", "only rows that reconcile matched to a Q-ID; never creates items"]),
]
NOTE = "Also available: vocab, categories and subjects. They build the worksheets of the shared vocabulary and are not part of this session."


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    h, _ = oa.row(cv, 0, 0, STAGES, 270, 46, COL)
    total = 5 * 270 + 4 * 46
    oa.note(cv, 0, h + 22, NOTE, total)
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
