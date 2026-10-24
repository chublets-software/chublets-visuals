"""Block 1 (1/4) -- CodeMeta term overview (S11: redrawn on the model's crosswalk).

The 83 distinct CodeMeta terms of the CodeMeta-Wikidata crosswalk, each in the
CodeMeta type it belongs to, with the subclass hierarchy Thing, CreativeWork,
SoftwareSourceCode and SoftwareApplication.

Reads: py/model_data.py (vendored crosswalk). Produces: img/chublets-codemeta-overview.svg / .png

Runnable standalone: `python py/step_codemeta_overview.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import codemeta_diagram  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402

NAME = "chublets-codemeta-overview"


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    types = codemeta_diagram.terms_by_type(M)
    log = [g.save(NAME, codemeta_diagram.build(M, with_pids=False))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_codemeta_terms']} CodeMeta terms in {len(types)} types")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
