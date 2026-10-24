"""Block 1 (2/4) -- Wikidata software-properties overview (S11: redrawn on the model).

The Wikidata properties of the WikiProject Informatics software list, in the groups
of that page. Every property is also a property of the chublets Wikibase; a coloured
square tells whether it has a CodeMeta term (crosswalked) or not (Wikidata only).

Reads: py/model_data.py (vendored list). Produces: img/chublets-wikidata-properties-overview.svg / .png

Runnable standalone: `python py/step_wikidata_properties_overview.py`
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

NAME = "chublets-wikidata-properties-overview"
GROUPS = {"technical": "Technical", "registries": "Registries and identifiers", "versioning": "Versioning",
          "relations": "Relations", "links": "Links", "rights": "Rights", "identity": "Identity", "people": "People"}
BOX_W, ROW_H, HEAD_H, GAP, N_COL = 400, 25, 50, 36, 4
SC = g.STATUS_COLORS


def build(M: model_data.Model) -> g.Canvas:
    rows = model_data.wikiproject_software_list()
    groups: OrderedDict[str, list[dict]] = OrderedDict((k, []) for k in GROUPS)
    for r in rows:
        assert r["group"] in GROUPS, f"unknown group {r['group']!r} on the WikiProject list"
        groups[r["group"]].append(r)
    for v in groups.values():
        v.sort(key=lambda r: r["label_en"].lower())
    # a few entries of the list have no label yet; the Wikibase property with that twin has one
    by_twin = {p.twin: p.label for p in M.props.values() if p.twin}
    for v in groups.values():
        for r in v:
            if "label to be filled" in r["label_en"]:
                r["label_en"] = by_twin[r["pid"]]
        v.sort(key=lambda r: r["label_en"].lower())
    cv = g.Canvas()
    heights = [0.0] * N_COL
    order = sorted(groups, key=lambda k: -len(groups[k]))
    for key in order:
        rs = groups[key]
        c = min(range(N_COL), key=lambda i: heights[i])
        x, y = c * (BOX_W + GAP), heights[c]
        h = HEAD_H + len(rs) * ROW_H + 14
        col = "#475569"
        out = g.rect(x, y, BOX_W, h, fill="#ffffff", stroke=col, sw=2.2, rx=8)
        out += g.text(x + 16, y + 31, GROUPS[key], 17, bold=True, fill=INK)
        out += g.text(x + BOX_W - 16, y + 31, str(len(rs)), 15, bold=True, fill=MUTED, anchor="end")
        out += g.line([(x, y + HEAD_H - 6), (x + BOX_W, y + HEAD_H - 6)], col, sw=1.4)
        yy = y + HEAD_H + 12
        for r in rs:
            status = r["wikibase_status"]
            assert status in ("crosswalked", "wikidata-only"), f"{r['pid']}: unexpected status {status!r}"
            out += g.rect(x + 14, yy - 11, 12, 12, fill=SC[status], rx=3)
            out += g.text(x + 36, yy, r["label_en"], 14.5, fill=INK)
            out += g.text(x + BOX_W - 16, yy, r["pid"], 13.5, fill=MUTED, anchor="end")
            yy += ROW_H
        cv.add(out, x, y, x + BOX_W, y + h)
        heights[c] += h + 30
    # legend
    ly = max(heights) + 10
    n_cw = sum(1 for r in rows if r["wikibase_status"] == "crosswalked")
    out, x = "", 0.0
    for label, col in ((f"also a CodeMeta term (crosswalked): {n_cw}", SC["crosswalked"]),
                       (f"Wikidata only: {len(rows) - n_cw}", SC["wikidata-only"])):
        out += g.rect(x, ly, 14, 14, fill=col, rx=3) + g.text(x + 24, ly + 12, label, 14, fill=INK)
        x += 24 + g.text_w(label, 14) + 40
    out += g.text(x, ly + 12, "Pn = Wikidata property ID", 14, italic=True, fill=MUTED)
    cv.add(out, 0, ly - 2, x + 260, ly + 20)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = {**model_data.caption_facts(M), "n_wikiproject": len(model_data.wikiproject_software_list())}
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_wikiproject']} Wikidata software properties in {len(GROUPS)} groups")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
