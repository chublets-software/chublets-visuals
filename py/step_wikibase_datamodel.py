"""Block 1 (4/4) -- chublets.software Wikibase data model (S11: redrawn on the model).

Where the 168 properties come from: Wikidata properties and CodeMeta terms, joined
by the crosswalk, plus what chublets added. All numbers come from the model.

Reads: py/model_data.py. Produces: img/chublets-wikibase-datamodel.svg / .png

Runnable standalone: `python py/step_wikibase_datamodel.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "chublets-wikibase-datamodel"
SC = g.STATUS_COLORS
BOX_W, GAP, TOP_H = 640, 100, 190


def _source(cv, x, title, lines, big, col):
    out = g.rect(x, 0, BOX_W, TOP_H, fill=tint(col, 0.92), stroke=col, sw=3, rx=12)
    out += g.text(x + BOX_W / 2, 40, title, 23, bold=True, fill=INK, anchor="middle")
    yy = 74
    for ln in lines:
        out += g.text(x + BOX_W / 2, yy, ln, 16, fill=INK, anchor="middle")
        yy += 24
    out += g.text(x + BOX_W / 2, TOP_H - 22, big, 21, bold=True, fill=col, anchor="middle")
    cv.add(out, x, 0, x + BOX_W, TOP_H)


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    total_w = 2 * BOX_W + GAP
    _source(cv, 0, "Wikidata properties",
            ["software properties of the WikiProject", "and further properties used for software"],
            f"{f['n_twin']} properties with an equivalent in Wikidata (P4)", SC["wikidata-only"])
    _source(cv, BOX_W + GAP, "CodeMeta terms",
            ["the CodeMeta vocabulary for software metadata", "mapped to Wikidata in the crosswalk"],
            f"{f['n_with_codemeta']} terms, {f['n_crosswalked']} with a Wikidata property", SC["codemeta-only"])
    ry, rh = TOP_H + 110, 290
    cx = total_w / 2
    import math
    for sx, ex in ((BOX_W / 2, BOX_W / 2 + 150), (BOX_W + GAP + BOX_W / 2, BOX_W + GAP + BOX_W / 2 - 150)):
        sy, ey = TOP_H + 6, ry - 4
        d = math.hypot(ex - sx, ey - sy)
        ux, uy = (ex - sx) / d, (ey - sy) / d
        cv.add(g.line([(sx, sy), (ex - ux * 14, ey - uy * 14)], MUTED, sw=3) + g.arrowhead(ex, ey, ux, uy, 18),
               min(sx, ex), sy, max(sx, ex), ey)
    col = SC["crosswalked"]
    out = g.rect(0, ry, total_w, rh, fill=tint(col, 0.9), stroke=col, sw=3.5, rx=14)
    out += g.text(cx, ry + 46, f"Wikibase of chublets: {f['n_props']} properties", 26, bold=True, fill=INK, anchor="middle")
    out += g.text(cx, ry + 76, "all of them local properties; each states its equivalents (Wikidata P4, CodeMeta P101, schema.org P102)", 15.5, fill=INK, anchor="middle")
    parts = [(f["n_crosswalked"], "crosswalked", SC["crosswalked"]), (f["n_codemeta_only"], "CodeMeta only", SC["codemeta-only"]),
             (f["n_wikidata_only"], "Wikidata only", SC["wikidata-only"]), (f["n_chublets_addition"], "chublets addition", SC["chublets-addition"]),
             (f["n_no_status"], "built-in and later added", SC[""])]
    assert sum(n for n, *_ in parts) == f["n_props"], "the five origins must add up to all properties"
    bw = total_w - 80
    x = 40
    for n, label, c in parts:
        w = bw * n / f["n_props"]
        out += g.rect(x, ry + 110, w - 3, 44, fill=c, rx=6) + g.text(x + (w - 3) / 2, ry + 140, str(n), 20, bold=True, fill="#ffffff", anchor="middle")
        lines = g.wrap(label, 14, max(w - 8, 70))
        for k, ln in enumerate(lines):
            out += g.text(x + (w - 3) / 2, ry + 180 + 18 * k, ln, 14, fill=INK, anchor="middle")
        x += w
    out += g.text(cx, ry + rh - 26, "The model is not invented from scratch: it starts from the crosswalk between the two vocabularies.", 14.5, italic=True, fill=MUTED, anchor="middle")
    cv.add(out, 0, ry, total_w, ry + rh)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_props']} properties from {facts['n_twin']} Wikidata equivalents and {facts['n_with_codemeta']} CodeMeta terms")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
