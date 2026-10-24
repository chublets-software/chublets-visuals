"""S11 -- the architecture of chublets.software: from the sources to the marketplaces.

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
from visuals_utils import CATEGORY_COLORS, FOUR_STEPS  # noqa: E402

NAME = "chublets-software-architecture"
NEUTRAL = CATEGORY_COLORS[5]


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    items = [
        ("Wikidata bridge", ["open-archaeo import pipeline", f"{f['n_oa_entries']} entries"], NEUTRAL),
        ("Data sources", ["Wikidata items, FDOx objects,", "Git repositories via CFF"], FOUR_STEPS[0]["color"]),
        ("Wikibase of chublets", [f"{f['n_props']} properties, {f['n_classes']} classes,", f"{f['n_items']} items"], FOUR_STEPS[2]["color"]),
        ("Export pipeline", ["SPARQL, rdflib,", "CodeMeta, DCAT and DataCite"], FOUR_STEPS[3]["color"]),
        ("Marketplaces and knowledge graph", ["nfdi.software, find.software", "and KGE4RSE"], NEUTRAL),
    ]
    oa.row(cv, 0, 0, items, 270, 50, NEUTRAL)
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
