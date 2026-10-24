"""S10 -- where the properties of the chublets Wikibase come from.

One bar for all properties, split by origin in the CodeMeta-Wikidata crosswalk (crosswalked, CodeMeta
only, Wikidata only, chublets addition, none), and below each segment how many of
its properties carry a Wikidata twin (P4), a loose Wikidata close match (P100), a
CodeMeta term, a schema.org term (P102) and a DataCite element. DataCite is drawn
dashed: it is derived via the CodeMeta hub, not a published mapping (PRIMER.md A4).

Style: the house palette for the status colours (visuals_utils.CATEGORY_COLORS);
the semantic scheme is not used, because nothing here is a model element.

Reads: py/model_data.py. Produces: img/property-origin.svg / .png

Runnable standalone: `python py/step_property_origin.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "property-origin"

# status key -> (label, where it comes from)
SEGMENTS = [
    ("crosswalked", "crosswalked", "CodeMeta term mapped to a Wikidata property in the crosswalk"),
    ("codemeta-only", "CodeMeta only", "CodeMeta term without a Wikidata property"),
    ("wikidata-only", "Wikidata only", "Wikidata property without a CodeMeta term"),
    ("chublets-addition", "chublets addition", "defined by chublets, in neither vocabulary"),
    ("", "unclassified", "built-in properties and later additions"),
]

# evidence rows: (label, predicate, derived)
ROWS = [
    ("equivalent Wikidata property (P4)", lambda p: bool(p.twin), False),
    ("close match in Wikidata (P100)", lambda p: bool(p.close_match), False),
    ("equivalent CodeMeta term", lambda p: bool(p.codemeta_terms), False),
    ("equivalent schema.org term (P102)", lambda p: bool(p.schema_org), False),
    ("DataCite element (derived via CodeMeta)", lambda p: bool(p.datacite), True),
]

LABEL_W = 300
BAR_W = 860
BAR_H = 56
GAP = 4
CELL_H = 26
CELL_GAP = 7
TOTAL_W = 70


def build(M: model_data.Model) -> g.Canvas:
    props = list(M.props.values())
    total = len(props)
    cv = g.Canvas()
    x0 = LABEL_W

    # segment geometry
    segs = []
    x = x0
    for key, label, origin in SEGMENTS:
        ps = [p for p in props if p.pack_status == key]
        w = BAR_W * len(ps) / total
        segs.append((key, label, origin, ps, x, w))
        x += w

    # caption lines above the bar
    top_lines = []
    label_sizes: list[float] = []
    for key, label, origin, ps, sx, sw in segs:
        lines = g.wrap(label, 15, sw - 8, bold=True)
        top_lines.append((lines, g.wrap(origin, 12, sw - 8)))
        # a single word wider than its segment is set smaller instead of overflowing
        widest = max(g.text_w(w_, 15, True) for w_ in label.split(" "))
        label_sizes.append(min(15.0, 15.0 * (sw - 6) / widest))
    max_h = max(len(a) * 18 + len(b) * 15 for a, b in top_lines)
    bar_y = 10 + max_h + 10

    for (key, label, origin, ps, sx, sw), (la, lb), lsize in zip(segs, top_lines, label_sizes):
        col = g.STATUS_COLORS[key]
        out = ""
        y = 10 + 14
        for ln in la:
            out += g.text(sx + 3, y, ln, lsize, bold=True, fill=col)
            y += 18
        for ln in lb:
            out += g.text(sx + 3, y - 2, ln, 12, fill=MUTED)
            y += 15
        out += g.rect(sx, bar_y, sw - GAP, BAR_H, fill=col, rx=7)
        out += g.text(sx + (sw - GAP) / 2, bar_y + BAR_H / 2 + 8, str(len(ps)), 24, bold=True, fill="#ffffff", anchor="middle")
        cv.add(out, sx, 10, sx + sw, bar_y + BAR_H)

    out = g.text(x0 + BAR_W + 16, bar_y + BAR_H / 2 + 5, f"{total} properties", 14, bold=True, fill=INK)
    out += g.text(10, bar_y + BAR_H / 2 + 5, "Origin of the property", 14, bold=True, fill=INK)
    cv.add(out, 10, bar_y, x0 + BAR_W + 16 + 150, bar_y + BAR_H)

    # evidence rows
    y = bar_y + BAR_H + 36
    out = g.text(10, y - 6, "Number of properties that have an equivalent in \u2026", 12.5, italic=True, fill=MUTED)
    out += g.text(x0 + BAR_W + 16, y - 6, "all groups", 12, fill=MUTED)
    cv.add(out, 10, y - 20, x0 + BAR_W + 16 + 90, y)
    for label, pred, derived in ROWS:
        out = g.text(10, y + CELL_H / 2 + 5, label, 14, fill=INK, italic=derived)
        for key, _l, _o, ps, sx, sw in segs:
            col = g.STATUS_COLORS[key]
            n = sum(1 for p in ps if pred(p))
            cw = sw - GAP
            track_stroke = col if derived else "none"
            out += g.rect(sx, y, cw, CELL_H, fill=tint(col, 0.9), stroke=track_stroke, sw=1.2, rx=5,
                          dash="4 3" if derived else None)
            if n:
                fw = max(cw * n / len(ps), 6)
                out += g.rect(sx, y, fw, CELL_H, fill=tint(col, 0.55) if derived else col, rx=5)
            txt = str(n) if n else "–"
            # number on the filled part if it fits, otherwise on the track
            on_fill = n and (cw * n / len(ps)) > g.text_w(txt, 14, True) + 16
            if on_fill:
                tx, anchor = sx + cw * n / len(ps) - 8, "end"
                colr = "#ffffff" if not derived else INK
            else:
                tx, anchor, colr = sx + cw - 8, "end", INK
            out += g.text(tx, y + CELL_H / 2 + 5, txt, 14, bold=True, fill=colr, anchor=anchor)
        n_all = sum(1 for p in props if pred(p))
        out += g.text(x0 + BAR_W + 16, y + CELL_H / 2 + 5, str(n_all), 14, bold=True, fill=INK)
        cv.add(out, 10, y, x0 + BAR_W + 16 + TOTAL_W, y + CELL_H)
        y += CELL_H + CELL_GAP
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(
        f"{facts['n_props']} properties: {facts['n_crosswalked']} crosswalked, {facts['n_codemeta_only']} CodeMeta only, "
        f"{facts['n_wikidata_only']} Wikidata only, {facts['n_chublets_addition']} chublets addition, {facts['n_no_status']} no status"
    )
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
