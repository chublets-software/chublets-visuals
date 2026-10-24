"""S10 -- how the CodeMeta terms are covered by the Wikibase.

Every CodeMeta term is one chip, grouped by the CodeMeta type it belongs to.
Purple chips are terms that are crosswalked to a Wikidata property, teal chips are
CodeMeta terms without a Wikidata property (they became Wikibase properties of
their own).

Style: house palette for the two coverage classes (same colours as property-origin).

Reads: py/model_data.py. Produces: img/codemeta-coverage.svg / .png

Runnable standalone: `python py/step_codemeta_coverage.py`
"""

from __future__ import annotations

import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "codemeta-coverage"
SC = g.STATUS_COLORS
X_CHIPS, W = 330, 1300
CHIP_H, GAP_X, GAP_Y = 26, 8, 8


def _terms(M: model_data.Model) -> OrderedDict:
    """group -> [(term, status)], one entry per distinct term, groups by size."""
    seen: dict[str, tuple[str, str]] = {}
    for r in M.codemeta_terms:
        t = r["codemeta_term"]
        if t not in seen or (r["status"] == "crosswalked" and seen[t][1] != "crosswalked"):
            seen[t] = (r["codemeta_group"].replace(" (v2 term)", ""), r["status"])
    groups: dict[str, list[tuple[str, str]]] = {}
    for t, (grp, status) in seen.items():
        groups.setdefault(grp, []).append((t, status))
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    return OrderedDict((k, sorted(groups[k], key=lambda x: (x[1] != "crosswalked", x[0].lower()))) for k in order)


def build(M: model_data.Model) -> g.Canvas:
    groups = _terms(M)
    total = sum(len(v) for v in groups.values())
    assert total == M.mapping_summary["codemeta_terms_total"], "distinct terms differ from the crosswalk summary"
    cv = g.Canvas()
    n_cw = sum(1 for v in groups.values() for _t, s in v if s == "crosswalked")
    n_co = total - n_cw
    # legend
    out = ""
    x = 0
    for label, col in ((f"crosswalked to a Wikidata property: {n_cw}", SC["crosswalked"]),
                       (f"CodeMeta term only: {n_co}", SC["codemeta-only"])):
        out += g.rect(x, 0, 34, 20, fill=col, rx=5) + g.text(x + 46, 15, label, 14, fill=INK)
        x += 46 + g.text_w(label, 14) + 40
    out += g.text(x, 15, "Left: the CodeMeta type a term belongs to.", 13.5, italic=True, fill=MUTED)
    cv.add(out, 0, 0, x + 340, 22)
    y = 46
    for grp, terms in groups.items():
        # lay the chips out first to know the row height
        placed, cx, cy = [], X_CHIPS, 0
        for t, status in terms:
            w = g.text_w(t, 13.5) + 22
            if cx + w > X_CHIPS + W - 330 and cx > X_CHIPS:
                cx, cy = X_CHIPS, cy + CHIP_H + GAP_Y
            placed.append((t, status, cx, cy, w))
            cx += w + GAP_X
        h = cy + CHIP_H
        out = g.text(0, y + 19, grp, 15, bold=True, fill=INK)
        lines = [f"{len(terms)} term" + ("s" if len(terms) > 1 else "")]
        out += g.text(0, y + 39, lines[0], 13, fill=MUTED)
        for t, status, px, py, w in placed:
            col = SC[status]
            out += g.rect(px, y + py, w, CHIP_H, fill=col, rx=13) + g.text(px + 11, y + py + 18, t, 13.5, fill="#ffffff")
        out += g.line([(0, y + max(h, 44) + 8), (X_CHIPS + W - 330, y + max(h, 44) + 8)], tint(MUTED, 0.8), sw=1)
        cv.add(out, 0, y, X_CHIPS + W - 330, y + max(h, 44) + 10)
        y += max(h, 44) + 20
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    facts["n_codemeta_groups"] = len(_terms(M))
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_codemeta_terms']} terms in {facts['n_codemeta_groups']} groups")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
