"""Block 1 (3/4) -- CodeMeta <-> Wikidata crosswalk (S11: redrawn on the model's crosswalk).

The same diagram as the CodeMeta overview, with the equivalent Wikidata property
of every term (Pn) and a dash for the terms that have none.

Reads: py/model_data.py (vendored crosswalk). Produces: img/chublets-codemeta-wikidata-crosswalk.svg / .png

Runnable standalone: `python py/step_codemeta_wikidata_crosswalk.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import codemeta_diagram  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402

NAME = "chublets-codemeta-wikidata-crosswalk"


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, codemeta_diagram.build(M, with_pids=True))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_crosswalked']} of {facts['n_codemeta_terms']} terms have a Wikidata property")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
