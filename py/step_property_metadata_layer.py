"""S10 -- the metadata layer of a property.

A property of the chublets Wikibase is itself an entity and carries statements:
its equivalents in Wikidata, CodeMeta and schema.org, its domain and range, and a
formatter URL for identifiers. One example property shows the values; a bar per
row says for how many of the properties the statement exists.

Style: semantic scheme, property-metadata amber for the property and the bars.

Reads: py/model_data.py. Produces: img/property-metadata-layer.svg / .png

Runnable standalone: `python py/step_property_metadata_layer.py`
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

NAME = "property-metadata-layer"
EXAMPLE = "programmed in"   # label of the example property; the step fails if it is not unique
PRP = g.SEM["propmeta"]
DARK = "#b45309"

# (property id, name, what the value is)
ROWS = [
    ("P4", "Wikidata equivalent", "ID of the equivalent Wikidata property"),
    ("P100", "close match Wikidata property", "Wikidata property that is close, not equal"),
    ("P101", "equivalent CodeMeta term", "name of the CodeMeta term"),
    ("P102", "equivalent schema.org term", "name of the schema.org term"),
    ("P9", "domain", "class of the entity that has the property"),
    ("P10", "range", "class of the value"),
    ("P5", "formatter URL", "URL pattern that turns an identifier into a link"),
]
X_LAB, X_EX, X_BAR, BAR_W = 0, 520, 900, 360
ROW_H = 62


def _values(M: model_data.Model, pid: str) -> dict[str, list[str]]:
    D = model_data.DEMO / "data" / "csv"
    ents = {e["id"]: e for e in model_data.read_csv(D / "entities.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "entities.csv")}
    out: dict[str, list[str]] = defaultdict(list)
    for s in model_data.read_csv(D / "statements.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "statements.csv"):
        if s["subject"] == pid:
            v = s["value"]
            out[s["property"]].append(ents[v]["label_en"] if v in ents and ents[v]["kind"] == "class" else v)
    return out


def counts() -> dict[str, int]:
    D = model_data.DEMO / "data" / "csv"
    ents = {e["id"]: e["kind"] for e in model_data.read_csv(D / "entities.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "entities.csv")}
    seen: dict[str, set[str]] = defaultdict(set)
    for s in model_data.read_csv(D / "statements.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "statements.csv"):
        if ents.get(s["subject"]) == "property":
            seen[s["property"]].add(s["subject"])
    return {k: len(v) for k, v in seen.items()}


def build(M: model_data.Model) -> g.Canvas:
    ex = [p for p in M.props.values() if p.label == EXAMPLE]
    assert len(ex) == 1, f"example property {EXAMPLE!r} must be unique, found {len(ex)}"
    ex = ex[0]
    vals = _values(M, ex.id)
    cnt = counts()
    n = len(M.props)
    cv = g.Canvas()
    # the example property
    out = g.rect(0, 0, 640, 76, fill=PRP, stroke=DARK, sw=2, rx=12)
    out += g.text(20, 34, ex.label, 22, bold=True, fill=INK)
    out += g.text(20, 58, f"{ex.id} · property of the chublets Wikibase · data type: {ex.datatype}", 13.5, fill="#78350f")
    cv.add(out, 0, 0, 640, 76)
    cv.add(g.text(670, 34, "A property is itself an entity: it carries the statements below.", 14, italic=True, fill=MUTED)
           + g.text(670, 56, "Example values are those of this property.", 14, italic=True, fill=MUTED), 670, 14, 1260, 62)
    y = 110
    cv.add(g.text(X_LAB, y, "Statement on the property", 13, bold=True, fill=MUTED)
           + g.text(X_EX, y, "Example value", 13, bold=True, fill=MUTED)
           + g.text(X_BAR, y, f"Properties with this statement (of {n})", 13, bold=True, fill=MUTED), 0, y - 14, X_BAR + 420, y + 4)
    y += 16
    for pid, name, what in ROWS:
        v = vals.get(pid)
        out = g.line([(0, y), (X_BAR + BAR_W + 60, y)], tint(MUTED, 0.8), sw=1)
        out += g.text(X_LAB, y + 26, f"{name} ({pid})", 16, bold=True, fill=INK)
        out += g.text(X_LAB, y + 47, what, 13, fill=MUTED)
        if v:
            txt = ", ".join(v)
            if pid == "P4":
                txt = "Wikidata " + txt
            out += g.text(X_EX, y + 36, txt, 15, fill=INK)
        else:
            out += g.text(X_EX, y + 36, "not set for this property", 13.5, italic=True, fill=MUTED)
        k = cnt.get(pid, 0)
        out += g.rect(X_BAR, y + 20, BAR_W, 24, fill=tint(PRP, 0.7), rx=5)
        out += g.rect(X_BAR, y + 20, max(BAR_W * k / n, 4), 24, fill=PRP, stroke=DARK, sw=1, rx=5)
        out += g.text(X_BAR + BAR_W + 12, y + 38, str(k), 16, bold=True, fill=INK)
        cv.add(out, 0, y, X_BAR + BAR_W + 60, y + ROW_H)
        y += ROW_H
    cv.add(g.line([(0, y), (X_BAR + BAR_W + 60, y)], tint(MUTED, 0.8), sw=1), 0, y, X_BAR + BAR_W + 60, y)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    cnt = counts()
    facts.update({f"n_meta_{k.lower()}": v for k, v in cnt.items()})
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append("statements on properties: " + ", ".join(f"{k} {cnt.get(k, 0)}" for k, *_ in ROWS))
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
