"""S11 -- the OpenRefine route through the open-archaeo Wikidata session.

Reads: py/model_data.py. Produces: img/open-archaeo-openrefine-route.svg / .png

Runnable standalone: `python py/step_open_archaeo_openrefine_route.py`
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

NAME = "open-archaeo-openrefine-route"
COL = CATEGORY_COLORS[2]  # teal: the OpenRefine slice, as in open-archaeo-two-routes
STAGES = [
    ("Setup", ["OpenRefine 3.7 or later, the Wikibase extension, logged in with the editing account"]),
    ("Split and derive", ["multi-valued cells; VCS, archive date, CRAN and PyPI taken from GREL expressions"]),
    ("Reconcile", ["name and repository match against P1324; owns the shared vocabulary (P277, P1547, P921)"]),
    ("Schema and upload", ["edit the Wikidata schema; upload directly or export as QuickStatements"]),
    ("Hand back", ["id,qid CSV goes to the concordance; resolved values go to vocabulary.json"]),
]


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    oa.row(cv, 0, 0, STAGES, 270, 46, COL)
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
