"""S10 -- how a statement carries its provenance.

Left: the anatomy of one real statement (a version of SPARQLing Unicorn QGIS
Plugin) with its qualifiers and its two reference groups. Right: how often the
Wikibase uses these parts -- statements by origin, statements with references and
qualifiers, the most used qualifier properties.

Style: semantic scheme for the anatomy (item grey, property-metadata amber for
qualifier and reference fields); house palette for the origin bars.

Reads: py/model_data.py. Produces: img/statement-provenance.svg / .png

Runnable standalone: `python py/step_statement_provenance.py`
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import CATEGORY_COLORS, INK, MUTED, tint  # noqa: E402

NAME = "statement-provenance"
ITEM, PROP, VALUE = "Q360", "software version identifier", "0.17.4"
ITM, PRP = g.SEM["instance"], g.SEM["propmeta"]
DARK = "#b45309"
ORIGINS = [("open-archaeo", "imported from the open-archaeo list", CATEGORY_COLORS[0]),
           ("wikidata", "taken over from Wikidata", CATEGORY_COLORS[4]),
           ("wikidata-stub", "about Wikidata stubs", CATEGORY_COLORS[3]),
           ("starter-pack", "defined for chublets", CATEGORY_COLORS[1]),
           ("", "no origin recorded", CATEGORY_COLORS[5])]
X_R, BAR_W = 720, 380


def _data():
    D = model_data.DEMO / "data" / "csv"
    ents = {e["id"]: e for e in model_data.read_csv(D / "entities.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "entities.csv")}
    stm = model_data.read_csv(D / "statements.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "statements.csv")
    qual = defaultdict(list)
    for x in model_data.read_csv(D / "qualifiers.csv"):
        qual[x["sid"]].append(x)
    refs = defaultdict(lambda: defaultdict(list))
    for x in model_data.read_csv(D / "references.csv"):
        refs[x["sid"]][x["group"]].append(x)
    return ents, stm, qual, refs


def _facts(ents, stm, qual, refs) -> dict:
    origin = Counter(s["origin"] for s in stm)
    qprops = Counter(ents[x["property"]]["label_en"] for xs in qual.values() for x in xs)
    return {"n_statements": len(stm), "n_with_ref": sum(1 for s in stm if s["sid"] in refs),
            "n_with_qual": sum(1 for s in stm if s["sid"] in qual), "origin": origin, "qprops": qprops.most_common(5)}


def _box(cv, x, y, w, h, fill, stroke, head, lines, ink=INK):
    out = g.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2, rx=10)
    out += g.text(x + 16, y + 26, head, 14, bold=True, fill=ink)
    yy = y + 48
    for ln in lines:
        out += g.text(x + 16, yy, ln, 13.5, fill=ink)
        yy += 21
    cv.add(out, x, y, x + w, y + h)


def build(M: model_data.Model) -> g.Canvas:
    ents, stm, qual, refs = _data()
    lab = lambda i: ents[i]["label_en"] if i in ents else i
    st = [s for s in stm if s["subject"] == ITEM and lab(s["property"]) == PROP and s["value"] == VALUE]
    assert len(st) == 1, "the example statement must be unique"
    s = st[0]
    f = _facts(ents, stm, qual, refs)
    cv = g.Canvas()
    W = 610
    cv.add(g.text(0, 14, "Anatomy of one statement", 15, bold=True, fill=INK), 0, 0, 260, 20)
    _box(cv, 0, 30, W, 88, tint(ITM, 0.4), "#64748b", "Statement",
         [f"{lab(ITEM)} ({ITEM})", f"{PROP}: {VALUE}  ·  rank: {s['rank'] or 'normal'}  ·  origin: {s['origin'] or 'none'}"])
    qs = qual[s["sid"]]
    qy = 150
    _box(cv, 40, qy, W - 40, 40 + 21 * len(qs), tint(PRP, 0.6), DARK, "Qualifiers (details of this statement)",
         [f"{lab(x['property'])}: {lab(x['value'])}" for x in qs])
    cv.add(g.line([(20, 118), (20, qy + 30), (40, qy + 30)], MUTED, sw=1.8), 0, 118, 40, qy + 30)
    ry = qy + 40 + 21 * len(qs) + 32
    gy = ry
    for grp in sorted(refs[s["sid"]]):
        rows = refs[s["sid"]][grp]
        lines = [f"{lab(x['property'])}: " + (lab(x["value"]) if x["value"] in ents else (x["value"][:46] + ("…" if len(x["value"]) > 46 else ""))) for x in rows]
        h = 40 + 21 * len(lines)
        _box(cv, 40, gy, W - 40, h, "#ffffff", DARK, f"Reference {grp} (where the statement comes from)", lines)
        cv.add(g.line([(20, 118), (20, gy + 30), (40, gy + 30)], MUTED, sw=1.8), 0, 118, 40, gy + 30)
        gy += h + 22
    # right: usage
    n = f["n_statements"]
    y = 30
    out = g.text(X_R, 14, f"Use in the Wikibase ({n} statements)", 15, bold=True, fill=INK)
    cv.add(out, X_R, 0, X_R + 420, 20)

    def bars(y, heading, rows):
        o = g.text(X_R, y, heading, 13.5, bold=True, fill=MUTED)
        y += 14
        for label, k, col in rows:
            o += g.text(X_R, y + 17, label, 13.5, fill=INK)
            o += g.rect(X_R + 270, y, BAR_W, 22, fill=tint(col, 0.88), rx=4)
            o += g.rect(X_R + 270, y, max(BAR_W * k / n, 3), 22, fill=col, rx=4)
            o += g.text(X_R + 270 + BAR_W + 10, y + 17, str(k), 13.5, bold=True, fill=INK)
            y += 30
        cv.add(o, X_R, y - 30 * len(rows) - 14, X_R + 270 + BAR_W + 60, y)
        return y + 18

    y = bars(y + 20, "Statements by origin", [(t, f["origin"][k], c) for k, t, c in ORIGINS])
    y = bars(y, "Statements with …", [("at least one reference", f["n_with_ref"], CATEGORY_COLORS[2]),
                                        ("at least one qualifier", f["n_with_qual"], CATEGORY_COLORS[2])])
    y = bars(y, "Most used qualifiers (statements per qualifier)", [(f"{a}", k, CATEGORY_COLORS[4]) for a, k in f["qprops"]])
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    ents, stm, qual, refs = _data()
    f = _facts(ents, stm, qual, refs)
    facts = {**model_data.caption_facts(M), "n_with_ref": f["n_with_ref"], "n_with_qual": f["n_with_qual"],
             "n_origin_oa": f["origin"]["open-archaeo"], "n_origin_wd": f["origin"]["wikidata"]}
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{f['n_statements']} statements, {f['n_with_ref']} with a reference, {f['n_with_qual']} with a qualifier")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
