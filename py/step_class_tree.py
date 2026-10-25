"""S10 -- class tree of the chublets Wikibase.

The 13 classes of the model with their subclass-of (P1) edges, their Wikidata
equivalent (P4) and their CIDOC CRM class (own or inherited). Layout is a left to
right tree; the one class with two parents (chublet) is drawn with two edges.

Style: semantic scheme, class colour (dark orange) for classes; the origin of a
class is told by its fill -- built-in light, chublets solid,
importer stub dashed. No title, header or footer; the caption is in captions.yaml.

Reads: py/model_data.py (vendored model tables). Produces: img/class-tree.svg / .png

Runnable standalone: `python py/step_class_tree.py`
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "class-tree"
CLS = g.SEM["class"]

MIN_COL_W = [190, 300, 300, 300]  # a column grows when its text needs more room (`_col_widths`)
GAP = 70
NODE_H = 62
PITCH = 78

# Row of every class (layout decision; `_check_layout` fails if the model gains or
# loses a class or changes a parent, so a new class is placed on purpose).
ORDER_Q3_KIDS = ["Q105", "Q100", "Q1", "Q2"]


def _layout(M: model_data.Model) -> dict[str, tuple[int, float]]:
    """class id -> (column, row)."""
    kids: dict[str, list[str]] = {}
    for c in M.classes.values():
        for p in c.parents:
            kids.setdefault(p, []).append(c.id)
    roots = [c.id for c in M.classes.values() if not c.parents]
    assert roots == ["Q3"], f"expected one root class Q3, found {roots}"
    assert sorted(kids["Q3"]) == sorted(ORDER_Q3_KIDS), f"children of Q3 changed: {kids['Q3']}"
    multi = [c.id for c in M.classes.values() if len(c.parents) > 1]
    assert multi == ["Q106"] and M.classes["Q106"].parents == ("Q105", "Q101"), (
        f"the layout expects chublet (Q106) as the only class with two parents (Q105, Q101); found {multi}"
    )
    q100_kids = sorted((k for k in kids["Q100"]), key=lambda i: int(i[1:]))
    assert "Q106" not in q100_kids

    pos: dict[str, tuple[int, float]] = {"Q3": (0, 0.0)}
    row = 0
    pos["Q105"] = (1, float(row))
    row += 1
    first = row
    for k in q100_kids:
        pos[k] = (2, float(row))
        row += 1
    pos["Q100"] = (1, (first + row - 1) / 2)
    pos["Q1"] = (1, float(row))
    row += 1
    pos["Q2"] = (1, float(row))
    pos["Q106"] = (3, pos["Q101"][1])  # beside its second parent
    pos["Q3"] = (0, (pos["Q105"][1] + pos["Q2"][1]) / 2)
    assert set(pos) == set(M.classes), f"classes without a place: {set(M.classes) - set(pos)}"
    # every other class has exactly one parent, one column to its left
    for c in M.classes.values():
        if c.id not in ("Q106",) and c.parents:
            assert pos[c.id][0] == pos[c.parents[0]][0] + 1, f"{c.id} is not one column right of its parent"
    return pos


def _need(M: model_data.Model, cid: str) -> float:
    """Width a class box needs for its label, chip and identifier line."""
    c = M.classes[cid]
    crm, frm = M.crm_of(cid)
    ident = c.id + (f" \u00b7 Wikidata {c.twin}" if c.twin else "")
    need = 12 + g.text_w(ident, 12.5) + 12
    label = 12 + g.text_w(c.label, 16, True) + 10
    if crm:
        chip_label = crm if frm == cid else crm.split(":")[-1] + " inherited"
        label += g.text_w(chip_label, 11.5) + 14 + 9
    return max(need, label + 12)


def _col_widths(M: model_data.Model, pos: dict[str, tuple[int, float]]) -> list[int]:
    """Column widths computed from the measured text (they differ between platforms), never asserted."""
    widths = list(MIN_COL_W)
    for cid, (col, _) in pos.items():
        widths[col] = max(widths[col], math.ceil(_need(M, cid)))
    return widths


def _col_x(col: int, widths: list[int]) -> float:
    return sum(widths[:col]) + GAP * col


def _box(M: model_data.Model, cid: str, x: float, y: float, w: float, cv: g.Canvas) -> None:
    c = M.classes[cid]
    kind = c.origin or "kernel"
    crm, frm = M.crm_of(cid)
    if kind == "starter-pack":
        fill, stroke, dash, ink, sub = CLS, CLS, None, "#ffffff", tint(CLS, 0.78)
    elif kind == "wikidata-stub":
        fill, stroke, dash, ink, sub = "#ffffff", CLS, "6 4", INK, MUTED
    else:
        fill, stroke, dash, ink, sub = tint(CLS, 0.88), CLS, None, INK, MUTED
    out = g.rect(x, y, w, NODE_H, fill=fill, stroke=stroke, sw=2, rx=9, dash=dash)
    out += g.text(x + 12, y + 25, c.label, 16, bold=True, fill=ink)
    ident = c.id + (f" · Wikidata {c.twin}" if c.twin else "")
    out += g.text(x + 12, y + 46, ident, 12.5, fill=sub)
    if crm:
        own = frm == cid
        label = crm if own else "D14 inherited"
        label = label if own else crm.split(":")[-1] + " inherited"
        solid = own
        if kind == "starter-pack":
            chip_fill, chip_stroke, chip_col = ("#ffffff", "none", CLS) if solid else ("none", "#ffffff", "#ffffff")
        else:
            chip_fill, chip_stroke, chip_col = (CLS, "none", "#ffffff") if solid else ("none", CLS, CLS)
        svg, cw = g.chip(x + w - 9, y + 9, label, 11.5, fill=chip_fill, stroke=chip_stroke, color=chip_col,
                         dash=None if solid else "3 2", anchor_right=True)
        out += svg
    cv.add(out, x, y, x + w, y + NODE_H)


def build(M: model_data.Model) -> g.Canvas:
    pos = _layout(M)
    cv = g.Canvas()
    widths = _col_widths(M, pos)
    box: dict[str, tuple[float, float, float]] = {}  # id -> (x, y, w)
    for cid, (col, row) in pos.items():
        box[cid] = (_col_x(col, widths), row * PITCH, widths[col])
    # edges first (under the boxes)
    def mid(cid: str) -> float:
        return box[cid][1] + NODE_H / 2

    def right(cid: str) -> float:
        return box[cid][0] + box[cid][2]

    tri = 13
    for parent in ("Q3", "Q100"):
        kids = [c.id for c in M.classes.values() if c.parents == (parent,)]
        xr = right(parent)
        xbus = xr + 38
        ys = [mid(k) for k in kids]
        out = g.line([(xr + tri, mid(parent)), (xbus, mid(parent))], MUTED)
        out += g.line([(xbus, min(ys + [mid(parent)])), (xbus, max(ys + [mid(parent)]))], MUTED)
        for k in kids:
            out += g.line([(xbus, mid(k)), (box[k][0], mid(k))], MUTED)
        out += g.triangle_left(xr, mid(parent), tri)
        cv.add(out, xr, min(ys), box[kids[0]][0], max(ys))
    # chublet (Q106): two parents
    q106 = box["Q106"]
    xr = right("Q101")
    out = g.line([(xr + tri, mid("Q101")), (q106[0], mid("Q106"))], MUTED) + g.triangle_left(xr, mid("Q101"), tri)
    xr5 = right("Q105")
    xdrop = q106[0] + q106[2] / 2
    out += g.line([(xr5 + tri, mid("Q105")), (xdrop, mid("Q105")), (xdrop, q106[1])], MUTED)
    out += g.triangle_left(xr5, mid("Q105"), tri)
    cv.add(out, xr5, mid("Q105"), xdrop, q106[1])

    for cid, (x, y, w) in box.items():
        _box(M, cid, x, y, w, cv)

    # legend, in the free area right of the chublets classes
    n = model_data.caption_facts(M)
    lx = _col_x(3, widths)
    ly = box["Q106"][1] + PITCH * 2.2
    items = [
        ("built-in class of the data model", n["n_kernel_classes"], tint(CLS, 0.88), CLS, None),
        ("class defined for chublets", n["n_pack_classes"], CLS, CLS, None),
        ("class taken over from Wikidata (stub)", n["n_stub_classes"], "#ffffff", CLS, "6 4"),
    ]
    out = ""
    y = ly
    for label, count, fill, stroke, dash in items:
        out += g.rect(lx, y, 34, 20, fill=fill, stroke=stroke, sw=2, rx=5, dash=dash)
        out += g.text(lx + 46, y + 15, f"{label}: {count}", 13.5, fill=INK)
        y += 30
    out += g.line([(lx + 4, y + 10), (lx + 30, y + 10)], MUTED) + g.triangle_left(lx, y + 10, 10)
    out += g.text(lx + 46, y + 15, "subclass of (P1)", 13.5, fill=INK)
    y += 30
    svg, w1 = g.chip(lx, y, "crmdig:D14", 11.5, fill=CLS, color="#ffffff")
    svg2, _ = g.chip(lx + w1 + 8, y, "D14 inherited", 11.5, stroke=CLS, color=CLS, dash="3 2")
    out += svg + svg2
    out += g.text(lx, y + 38, "CIDOC CRM class (D14 Software), stated or inherited", 13.5, fill=INK)
    out += g.text(lx, y + 64, "Qn = class ID in the chublets Wikibase;", 13.5, fill=INK)
    out += g.text(lx, y + 82, "Wikidata Qn = equivalent class (P4) in Wikidata", 13.5, fill=INK)
    cv.add(out, lx, ly, lx + 370, y + 88)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)  # a caption with an unknown placeholder fails here
    log.append(f"{len(M.classes)} classes: {facts['n_kernel_classes']} kernel, {facts['n_pack_classes']} chublets, {facts['n_stub_classes']} importer stubs")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
