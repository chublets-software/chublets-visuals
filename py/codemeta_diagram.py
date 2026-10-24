"""Shared drawing of the CodeMeta term diagrams (S11).

Two graphics use it: the overview of the CodeMeta terms by type and the same
diagram with the Wikidata property of every term. The terms are the distinct
terms of the CodeMeta-Wikidata crosswalk as the model has them (83 terms), each
placed in the CodeMeta type it belongs to.

Layout: left to right. Thing, CreativeWork, then SoftwareSourceCode and
SoftwareApplication (subclass of, open triangle). Further CodeMeta terms that
are not part of that hierarchy stand in a fourth column.
"""

from __future__ import annotations

import model_data
import model_graphics as g
from visuals_utils import CATEGORY_COLORS, INK, MUTED, tint

BOX_W, ROW_H, HEAD_H, GAP = 330, 25, 62, 80
COLORS = {
    "Thing": CATEGORY_COLORS[5],
    "CreativeWork": CATEGORY_COLORS[0],
    "SoftwareSourceCode": CATEGORY_COLORS[2],
    "SoftwareApplication": CATEGORY_COLORS[1],
    "CodeMeta additional": CATEGORY_COLORS[3],
    "Person": CATEGORY_COLORS[4],
    "Role": CATEGORY_COLORS[4],
    "Review": CATEGORY_COLORS[4],
}
# types of the hierarchy, left to right; the others stand apart
HIERARCHY = {"CreativeWork": "Thing", "SoftwareSourceCode": "CreativeWork", "SoftwareApplication": "CreativeWork"}
APART = ["CodeMeta additional", "Person", "Role", "Review"]


def _display_group(raw: str) -> tuple[str, bool]:
    """(type shown, also a SoftwareApplication term) for the group name of the crosswalk."""
    also = raw.startswith("SoftwareSourceCode/SoftwareApplication")
    base = raw.replace(" (v2 term)", "").replace(" (outside hierarchy)", "").replace(" (v3)", "")
    if base.startswith("SoftwareSourceCode/"):
        base = "SoftwareSourceCode"
    if base.startswith("CodeMeta"):
        base = "CodeMeta additional"
    return base, also


def terms_by_type(M: model_data.Model) -> dict[str, list[dict]]:
    seen: dict[str, dict] = {}
    for r in M.codemeta_terms:
        t = r["codemeta_term"]
        grp, also = _display_group(r["codemeta_group"])
        e = seen.setdefault(t, {"term": t, "group": grp, "also": also, "pids": [], "status": r["status"]})
        if r["wikidata_pid"] and r["wikidata_pid"] not in e["pids"]:
            e["pids"].append(r["wikidata_pid"])
        if r["status"] == "crosswalked":
            e["status"] = "crosswalked"
    out: dict[str, list[dict]] = {}
    for e in seen.values():
        out.setdefault(e["group"], []).append(e)
    for v in out.values():
        v.sort(key=lambda e: e["term"].lower())
    assert sum(len(v) for v in out.values()) == M.mapping_summary["codemeta_terms_total"], "terms of the diagram differ from the crosswalk summary"
    return out


def _box_h(n: int) -> float:
    return HEAD_H + n * ROW_H + 14


def _box(cv: g.Canvas, x: float, y: float, name: str, rows: list[dict], with_pids: bool) -> None:
    col = COLORS[name]
    h = _box_h(len(rows))
    out = g.rect(x, y, BOX_W, h, fill=tint(col, 0.93), stroke=col, sw=2.4, rx=8)
    out += g.text(x + BOX_W / 2, y + 30, name, 18, bold=True, fill=INK, anchor="middle")
    n_map = sum(1 for r in rows if r["status"] == "crosswalked")
    sub = f"{len(rows)} terms" + (f", {n_map} with a Wikidata property" if with_pids else "")
    out += g.text(x + BOX_W / 2, y + 50, sub, 12.5, fill=MUTED, anchor="middle")
    out += g.line([(x, y + HEAD_H - 4), (x + BOX_W, y + HEAD_H - 4)], col, sw=1.6)
    yy = y + HEAD_H + 16
    for r in rows:
        mapped = r["status"] == "crosswalked"
        label = r["term"] + (" *" if r["also"] else "")
        out += g.text(x + 14, yy, label, 14.5, bold=bool(with_pids and mapped), fill=INK if (mapped or not with_pids) else MUTED)
        if with_pids:
            out += g.text(x + BOX_W - 14, yy, ", ".join(r["pids"]) if r["pids"] else "–", 13.5, fill=col if r["pids"] else MUTED, anchor="end")
        yy += ROW_H
    cv.add(out, x, y, x + BOX_W, y + h)


def build(M: model_data.Model, with_pids: bool) -> g.Canvas:
    types = terms_by_type(M)
    assert set(types) == set(COLORS), f"types of the crosswalk changed: {sorted(set(types) ^ set(COLORS))}"
    cv = g.Canvas()
    col_x = [c * (BOX_W + GAP) for c in range(4)]
    pos: dict[str, tuple[float, float]] = {}
    pos["Thing"] = (col_x[0], 0)
    pos["CreativeWork"] = (col_x[1], 0)
    pos["SoftwareSourceCode"] = (col_x[2], 0)
    pos["SoftwareApplication"] = (col_x[2], _box_h(len(types["SoftwareSourceCode"])) + 30)
    y = 0.0
    for name in APART:
        pos[name] = (col_x[3], y)
        y += _box_h(len(types[name])) + 30
    # subclass edges first
    for child, parent in HIERARCHY.items():
        cx, cy = pos[child]
        px, py = pos[parent]
        y_child = cy + 31
        y_par = py + 31
        xr = px + BOX_W
        xm = xr + GAP / 2
        cv.add(g.line([(xr + 13, y_par), (xm, y_par), (xm, y_child), (cx, y_child)], MUTED, sw=1.8)
               + g.triangle_left(xr, y_par, 13), xr, min(y_par, y_child), cx, max(y_par, y_child))
    for name, (x, yy) in pos.items():
        _box(cv, x, yy, name, types[name], with_pids)
    # legend under Thing
    lx, ly = col_x[0], _box_h(len(types["Thing"])) + 40
    out = g.line([(lx + 4, ly + 10), (lx + 30, ly + 10)], MUTED, sw=1.8) + g.triangle_left(lx, ly + 10, 10)
    out += g.text(lx + 46, ly + 15, "subclass of", 13.5, fill=INK)
    lines = ["* also a term of SoftwareApplication", "Types on the right: other CodeMeta terms"]
    if with_pids:
        lines = ["Pn = equivalent Wikidata property", "– = CodeMeta term without a Wikidata property"] + lines
    yy = ly + 44
    for ln in lines:
        out += g.text(lx, yy, ln, 13.5, fill=INK)
        yy += 22
    cv.add(out, lx, ly, lx + BOX_W + 40, yy)
    return cv
