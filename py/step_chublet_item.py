"""S10 -- one chublet as an item of the Wikibase.

A real item of the demo (SPARQLing Unicorn QGIS Plugin) drawn like an item page:
its statements by property, class values as class chips, item values as item chips,
literals as plain text, qualifiers below the value, and a count of the references
behind each statement. A few statements are shown; the count of the rest is told.

Style: semantic scheme (class orange for classes, instance grey for items).

Reads: py/model_data.py (vendored demo CSV). Produces: img/chublet-item.svg / .png

Runnable standalone: `python py/step_chublet_item.py`
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "chublet-item"
ITEM = "Q360"
CLS, ITM = g.SEM["class"], g.SEM["instance"]
# properties shown, in this order (labels in the model)
SHOWN = ["instance of", "Wikidata equivalent", "developer", "programmed in", "source code repository URL",
         "software version identifier", "DOI", "official website"]
W = 1060
X_PROP, X_VAL = 20, 330


def _load():
    D = model_data.DEMO / "data" / "csv"
    ents = {e["id"]: e for e in model_data.read_csv(D / "entities.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "entities.csv")}
    stm = [s for s in model_data.read_csv(D / "statements.csv") if s["subject"] == ITEM]
    q = defaultdict(list)
    for x in model_data.read_csv(D / "qualifiers.csv"):
        q[x["sid"]].append(x)
    r = defaultdict(set)
    for x in model_data.read_csv(D / "references.csv"):
        r[x["sid"]].add(x["group"])
    return ents, stm, q, r


def build(M: model_data.Model) -> tuple[g.Canvas, dict[str, int]]:
    ents, stm, qual, refs = _load()
    lab = lambda i: ents[i]["label_en"] if i in ents else i
    by = defaultdict(list)
    for s in stm:
        by[lab(s["property"])].append(s)
    for name in SHOWN:
        assert name in by, f"{ITEM} has no statement {name!r}"
    cv = g.Canvas()
    title = ents[ITEM]["label_en"]
    out = g.rect(0, 0, W, 78, fill=tint(ITM, 0.3), stroke="#94a3b8", sw=2, rx=12)
    out += g.text(20, 38, title, 24, bold=True, fill=INK)
    out += g.text(20, 63, f"{ITEM} · item of the chublets Wikibase · {len(stm)} statements", 14, fill=MUTED)
    cv.add(out, 0, 0, W, 78)
    y = 102
    shown_n = 0
    for name in SHOWN:
        ss = by[name]
        rank_pref = [s for s in ss if s["rank"] == "preferred"]
        pick = rank_pref if (name == "software version identifier" and rank_pref) else ss
        out = g.text(X_PROP, y + 22, name, 16, bold=True, fill=INK)
        yy = y
        for s in pick:
            v = s["value"]
            kind = ents[v]["kind"] if v in ents else "literal"
            x = X_VAL
            if kind in ("class", "item"):
                text = lab(v)
                fill, stroke, ink = (CLS, "none", "#ffffff") if kind == "class" else (ITM, "#64748b", INK)
                w = g.text_w(text, 14) + 22
                out += g.rect(x, yy + 4, w, 26, fill=fill, stroke=stroke, sw=1, rx=13)
                out += g.text(x + 11, yy + 22, text, 14, fill=ink)
                x += w + 12
            else:
                out += g.text(x, yy + 22, v, 14.5, fill=INK)
                x += g.text_w(v, 14.5) + 12
            if s["rank"] == "preferred":
                out += g.text(x, yy + 22, "preferred rank", 12, italic=True, fill=MUTED)
            n_ref = len(refs.get(s["sid"], ()))
            if n_ref:
                lab_r = f"{n_ref} reference" + ("s" if n_ref > 1 else "")
                svg, cw = g.chip(W - 20, yy + 7, lab_r, 11.5, fill="none", stroke="#64748b", color=MUTED, anchor_right=True)
                out += svg
            shown_n += 1
            qs = qual.get(s["sid"], [])
            if qs:
                qt = "  ·  ".join(f"{lab(x_['property'])}: {lab(x_['value'])}" for x_ in qs)
                out += g.line([(X_VAL + 8, yy + 34), (X_VAL + 8, yy + 52)], "#94a3b8", sw=1.4)
                out += g.text(X_VAL + 18, yy + 48, qt, 12.5, fill=MUTED)
                yy += 24
            yy += 36
        if name == "software version identifier":
            more = len(ss) - len(pick)
            out += g.text(X_VAL, yy + 14, f"and {more} earlier versions, each with its own date and references", 12.5, italic=True, fill=MUTED)
            yy += 26
        out += g.line([(0, yy + 6), (W, yy + 6)], tint(MUTED, 0.8), sw=1)
        cv.add(out, 0, y, W, yy + 8)
        y = yy + 10
    rest = len(stm) - sum(len(by[n]) if n != "software version identifier" else len(by[n]) for n in SHOWN)
    cv.add(g.text(X_PROP, y + 22, f"and {len(by) - len(SHOWN)} more kind of statement: title", 13, italic=True, fill=MUTED), X_PROP, y + 6, W, y + 30)
    y += 54
    # legend
    out = ""
    x = 0
    for label, fill, stroke, ink in (("class", CLS, "none", "#ffffff"), ("item", ITM, "#64748b", INK)):
        w = g.text_w(label, 13) + 22
        out += g.rect(x, y, w, 24, fill=fill, stroke=stroke, sw=1, rx=12) + g.text(x + 11, y + 17, label, 13, fill=ink)
        x += w + 8
    out += g.text(x + 8, y + 17, "= value is a class or an item;  plain text = literal value;  grey line = qualifier of the statement above", 13, fill=INK)
    cv.add(out, 0, y, W, y + 26)
    facts = {"n_item_statements": len(stm), "n_item_versions": len(by["software version identifier"]),
             "item_label": title, "item_id": ITEM}
    return cv, facts


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    cv, extra = build(M)
    facts = {**model_data.caption_facts(M), **extra}
    log = [g.save(NAME, cv)]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{extra['item_id']} {extra['item_label']}: {extra['n_item_statements']} statements")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
