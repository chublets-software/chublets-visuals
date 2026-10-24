"""S10 -- how the model gets into a real Wikibase.

The three phases of the push (core, model, items) with what each writes, the
rules of the push, and what happens when the target Wikibase is not empty
(inventory, adopt list, run). Numbers are read from the model and from the id
map and adopt list of the push.

Style: semantic scheme (class orange for classes, property-metadata amber for
properties, grey for items); phases in neutral boxes.

Reads: py/model_data.py. Produces: img/wikibase-bootstrap.svg / .png

Runnable standalone: `python py/step_wikibase_bootstrap.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "wikibase-bootstrap"
CLS, PRP, ITM = g.SEM["class"], g.SEM["propmeta"], g.SEM["instance"]
GREY = "#64748b"
PW, PH, PG = 400, 250, 70
RULES = ["every property is a local property (no federated properties)",
         "item values may point to Wikidata items (federated values)",
         "stubs of Wikidata items are not created; the value points to Wikidata",
         "dry run is the default; writing needs an explicit switch",
         "a rerun continues where the last run stopped (ids are recorded)"]


def facts() -> dict:
    f = model_data.FEDERATION / "usecases" / "chublets"
    return {"n_adopt": len(model_data.read_csv(f / "adopt-chublets-wikibase.de.csv")),
            "n_idmap": len(model_data.read_csv(f / "idmap-chublets-wikibase.de.csv"))}


def build(M: model_data.Model) -> g.Canvas:
    cf = model_data.caption_facts(M)
    n_items_create = cf["n_items"] - cf["n_items_stub"]
    cv = g.Canvas()
    chip_cls = lambda t, x, y: g.chip(x, y, t, 12.5, fill=CLS, color="#ffffff")
    phases = [
        ("1  core", "ids equal those of the model", [(CLS, f"{cf['n_kernel_classes']} built-in classes (Q1–Q3)"),
                                                      (PRP, f"{cf['n_kernel']} built-in properties (P1–P10)")]),
        ("2  model", "new ids, recorded in the id map", [(CLS, f"{cf['n_pack_classes']} classes defined for chublets"),
                                                         (PRP, f"{cf['n_pack'] + cf['n_review']} properties")]),
        ("3  items", "new ids, in steps (by origin, with a limit)", [(ITM, f"{cf['n_items_open_archaeo']} items from open-archaeo"),
                                                                    (ITM, f"{cf['n_items_wikidata']} items taken over from Wikidata")]),
    ]
    for i, (title, sub, rows) in enumerate(phases):
        x = i * (PW + PG)
        out = g.rect(x, 0, PW, PH, fill="#ffffff", stroke=GREY, sw=2, rx=14)
        out += g.text(x + 22, 44, title, 24, bold=True, fill=INK)
        out += g.text(x + 22, 70, sub, 13.5, fill=MUTED)
        yy = 106
        for col, label in rows:
            stroke = "#b45309" if col == PRP else (GREY if col == ITM else "none")
            out += g.rect(x + 22, yy, 28, 22, fill=col, stroke=stroke, sw=1.4, rx=6)
            out += g.text(x + 62, yy + 17, label, 15, fill=INK)
            yy += 36
        if i == 2:
            out += g.text(x + 22, yy + 12, f"not written: {cf['n_items_stub']} stubs of Wikidata items", 13, italic=True, fill=MUTED)
        cv.add(out, x, 0, x + PW, PH)
        if i < 2:
            cv.add(g.line([(x + PW + 8, PH / 2), (x + PW + PG - 14, PH / 2)], MUTED, sw=2.4)
                   + g.arrowhead(x + PW + PG - 6, PH / 2, 1, 0, 13), x + PW, PH / 2 - 10, x + PW + PG, PH / 2 + 10)
    total_w = 3 * PW + 2 * PG
    # rules
    y = PH + 50
    out = g.text(0, y, "Rules of the push", 15, bold=True, fill=INK)
    yy = y + 28
    for r in RULES:
        out += g.rect(0, yy - 12, 8, 8, fill=GREY, rx=4) + g.text(20, yy, r, 14.5, fill=INK)
        yy += 26
    cv.add(out, 0, y - 18, 640, yy)
    # non-empty target
    x0 = 700
    hf = facts()
    out = g.text(x0, y, "A target that is not empty", 15, bold=True, fill=INK)
    steps = [("inventory", "read-only list of what the target already holds"),
             ("adopt list", f"{hf['n_adopt']} pairs: id in the model → existing id in the target; checked by label and datatype"),
             ("run", "adopted entities are not created again; their statements are added")]
    yy = y + 20
    for i, (t, d) in enumerate(steps):
        out += g.rect(x0, yy, 150, 40, fill=tint(GREY, 0.85), stroke=GREY, sw=1.6, rx=10)
        out += g.text(x0 + 75, yy + 26, t, 15, bold=True, fill=INK, anchor="middle")
        lines = g.wrap(d, 13.5, total_w - x0 - 180)
        for k, ln in enumerate(lines):
            out += g.text(x0 + 170, yy + 18 + 18 * k - 9 * (len(lines) - 1), ln, 13.5, fill=INK)
        if i < 2:
            out += g.line([(x0 + 75, yy + 42), (x0 + 75, yy + 56)], MUTED, sw=2) + g.arrowhead(x0 + 75, yy + 64, 0, 1, 10)
        yy += 70
    out += g.text(x0, yy + 6, f"The id map of the push lists {hf['n_idmap']} entities of the target.", 13.5, italic=True, fill=MUTED)
    cv.add(out, x0, y - 18, total_w, yy + 14)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts_ = {**model_data.caption_facts(M), **facts()}
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts_)
    log.append(f"adopt {facts_['n_adopt']}, id map {facts_['n_idmap']}")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
