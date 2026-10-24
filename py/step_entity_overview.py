"""S10 -- what the chublets Wikibase contains.

Three kinds of entity -- classes, items, properties -- with their numbers, how the
items split (chublets, other items, items without a class), how the items link to
the classes (instance of, P2) and to the properties (statements), and where the
items come from.

Style: semantic scheme; class colour for classes, instance grey for items,
property-metadata amber for properties. Item origins use the house palette.

Reads: py/model_data.py. Produces: img/entity-overview.svg / .png

Runnable standalone: `python py/step_entity_overview.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import CATEGORY_COLORS, INK, MUTED, tint  # noqa: E402

NAME = "entity-overview"
CLS, PRP, ITM = g.SEM["class"], g.SEM["propmeta"], g.SEM["instance"]

BOX_W, BOX_H = 300, 150
GAP = 190
ITEM_W = 520


def _entity_box(cv, x, y, w, h, fill, stroke, ink, sub, big, title, lines):
    out = g.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2, rx=12)
    out += g.text(x + 20, y + 52, str(big), 40, bold=True, fill=ink)
    out += g.text(x + 20, y + 82, title, 18, bold=True, fill=ink)
    yy = y + 106
    for ln in lines:
        out += g.text(x + 20, yy, ln, 13, fill=sub)
        yy += 17
    cv.add(out, x, y, x + w, y + h)


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    cv = g.Canvas()
    xc, xi = 0, BOX_W + GAP
    xp = xi + ITEM_W + GAP
    y0 = 40
    _entity_box(cv, xc, y0, BOX_W, BOX_H, CLS, CLS, "#ffffff", tint(CLS, 0.78), f["n_classes"], "classes",
                ["Class (Q1), Property (Q2), software,", "chublet …; subclass of (P1)"])
    _entity_box(cv, xp, y0, BOX_W, BOX_H, PRP, "#b45309", INK, "#78350f", f["n_props"], "properties",
                ["P1–P10 built in, the others", "describe chublets and metadata"])
    # items: one big box with two split bars (by class, by origin)
    iy, ih = y0 - 20, 440
    out = g.rect(xi, iy, ITEM_W, ih, fill=tint(ITM, 0.5), stroke="#94a3b8", sw=2, rx=12)
    out += g.text(xi + 20, iy + 52, str(f["n_items"]), 40, bold=True, fill=INK)
    out += g.text(xi + 20, iy + 82, "items", 18, bold=True, fill=INK)
    bw = ITEM_W - 40
    bx = xi + 20

    def split(by, parts, heading):
        o = g.text(bx, by - 8, heading, 14, bold=True, fill=INK)
        x = bx
        for n, _l, col, ink in parts:
            w = bw * n / f["n_items"]
            o += g.rect(x, by, w - 2, 30, fill=col, stroke="#64748b" if col == "#ffffff" else "none", sw=1.2, rx=4)
            if w > 60:
                o += g.text(x + (w - 2) / 2, by + 21, str(n), 15, bold=True, fill=ink, anchor="middle")
            x += w
        yy = by + 52
        for n, label, col, _ink in parts:
            o += g.rect(bx, yy - 13, 22, 16, fill=col, stroke="#64748b" if col == "#ffffff" else "none", sw=1.2, rx=4)
            o += g.text(bx + 32, yy, f"{n} {label}", 13.5, fill=INK)
            yy += 24
        return o

    out += split(iy + 124, [
        (f["n_chublet_items"], "chublets (instance of chublet, Q106)", "#475569", "#ffffff"),
        (f["n_other_items"], "other items: topics, accounts, DOIs, URLs", "#94a3b8", INK),
        (f["n_items_no_class"], "items without a class", "#ffffff", INK),
    ], "By class")
    out += split(iy + 270, [
        (f["n_items_open_archaeo"], "imported from the open-archaeo list of archaeological software", CATEGORY_COLORS[0], "#ffffff"),
        (f["n_items_wikidata"], "taken over from Wikidata", CATEGORY_COLORS[4], "#ffffff"),
        (f["n_items_stub"], "stubs: label-only items standing in for Wikidata entities", CATEGORY_COLORS[3], "#ffffff"),
    ], "By origin")
    out += g.text(xi + 20, iy + ih - 18, f"All entities together carry {f['n_statements']} statements.", 13.5, italic=True, fill=MUTED)
    cv.add(out, xi, iy, xi + ITEM_W, iy + ih)
    # arrows items -> classes (instance of, P2) and items -> properties (statements)
    ym = iy + ih / 2 - 30
    a = g.line([(xi, ym), (xc + BOX_W + 12, ym)], MUTED, sw=2) + g.arrowhead(xc + BOX_W, ym, -1, 0, 12)
    a += g.text((xc + BOX_W + xi) / 2, ym - 12, "instance of (P2)", 14, bold=True, fill=INK, anchor="middle")
    cv.add(a, xc + BOX_W, ym - 30, xi, ym + 6)
    b = g.line([(xi + ITEM_W, ym), (xp - 12, ym)], MUTED, sw=2) + g.arrowhead(xp, ym, 1, 0, 12)
    b += g.text((xi + ITEM_W + xp) / 2, ym - 12, "statements", 14, bold=True, fill=INK, anchor="middle")
    b += g.text((xi + ITEM_W + xp) / 2, ym + 22, f"{f['n_statements_items']} in items", 13, fill=MUTED, anchor="middle")
    cv.add(b, xi + ITEM_W, ym - 30, xp, ym + 30)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_classes']} classes, {facts['n_items']} items ({facts['n_chublet_items']} chublets), {facts['n_props']} properties, {facts['n_statements']} statements")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
