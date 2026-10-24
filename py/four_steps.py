"""The four steps of the chublets pipeline as panels (S11).

One builder per step returns the body of a panel; `panel()` wraps it with a coloured header. The
collage (`chublets-four-steps`) puts the four panels side by side, the single-step graphics show one
panel. Numbers come from the model (`model_data.caption_facts`).
"""

from __future__ import annotations

import math

import model_graphics as g
from visuals_utils import FOUR_STEPS, INK, MUTED, tint

PW = 500          # panel width
PAD = 22          # inner padding
HEAD = 66         # header height
GAP = 26          # gap between boxes in a panel


def _box(x, y, w, title, lines, col, fill=0.9, size=15.5, tsize=18, bold_lines=False):
    """A box whose height follows its wrapped text; returns (svg, height)."""
    wrapped = []
    for ln in lines:
        wrapped += g.wrap(ln, size, w - 24, bold=bold_lines)
    h = 14 + tsize + 8 + len(wrapped) * (size + 6) + 10 if wrapped else 14 + tsize + 14
    out = g.rect(x, y, w, h, fill=tint(col, fill), stroke=col, sw=2.5, rx=10)
    out += g.text(x + w / 2, y + 14 + tsize * 0.85, title, tsize, bold=True, fill=INK, anchor="middle")
    yy = y + 14 + tsize + 8 + size
    for ln in wrapped:
        out += g.text(x + w / 2, yy, ln, size, fill=INK, anchor="middle", bold=bold_lines)
        yy += size + 6
    return out, h


def _arrow(x0, y0, x1, y1, col, sw=3):
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    return g.line([(x0, y0), (x1 - ux * 9, y1 - uy * 9)], col, sw=sw) + g.arrowhead(x1, y1, ux, uy, 13, col)


def _stack(items, x, y, w, col, arrows=True):
    """Boxes below each other joined by arrows; items are (title, lines, fill)."""
    out, cy = "", y
    for i, (title, lines, fill) in enumerate(items):
        s, h = _box(x, cy, w, title, lines, col, fill)
        out += s
        if arrows and i < len(items) - 1:
            out += _arrow(x + w / 2, cy + h + 2, x + w / 2, cy + h + GAP - 2, col)
        cy += h + GAP
    return out, cy - GAP


def body_ingest(f, col):
    w = PW - 2 * PAD
    src = [("Wikidata items", ["bridge items found by the open-archaeo to Wikidata pipeline"]),
           ("FDOx objects", ["CITATION.cff and codemeta.json via the FDOx registry"]),
           ("Git repositories", ["CITATION.cff harvested directly, no wrapper yet"])]
    out, cy = "", PAD
    cx = PW / 2
    for t, ls in src:
        s, h = _box(PAD, cy, w, t, ls, col)
        out += s
        cy += h + 14
    cy += 18
    out += _arrow(cx, cy - 34, cx, cy, col)
    s, h = _box(PAD, cy + 6, w, "Wikibase of chublets",
                [f"{f['n_items']} items, {f['n_statements']} statements", "three entry points, one schema"],
                col, 0.84)
    return out + s, cy + 6 + h + PAD


def body_model(f, col):
    w = PW - 2 * PAD
    items = [
        ("Wikidata properties", [f"{f['n_twin']} properties with a Wikidata equivalent (P4)"], 0.92),
        ("CodeMeta terms", [f"{f['n_with_codemeta']} terms, {f['n_crosswalked']} of them with a Wikidata property"], 0.92),
        (f"{f['n_props']} properties, {f['n_classes']} classes",
         ["every property states its equivalents in Wikidata, CodeMeta and schema.org",
          "linked to Wikidata by federation"], 0.84),
    ]
    out, cy = _stack(items, PAD, PAD, w, col)
    return out, cy + PAD


def body_curate(f, col):
    w = PW - 2 * PAD
    items = [
        ("Create items", [f"{f['n_items']} items with Q-IDs"], 0.92),
        ("Add statements", [f"{f['n_statements']} statements with qualifiers and references"], 0.92),
        ("Manual curation", [f"{f['n_merges']} merges of duplicates; ambiguous cases reviewed by a person"], 0.92),
        ("Quality control", ["constraint checks before publishing"], 0.92),
    ]
    out, cy = _stack(items, PAD, PAD, w, col)
    return out, cy + PAD


def body_export(f, col):
    w = PW - 2 * PAD
    cx = PW / 2
    out, cy = "", PAD
    s, h = _box(PAD, cy, w, "Read", ["SPARQL endpoint, CONSTRUCT query,", "RDF parsed with rdflib"], col)
    out += s
    cy += h
    out += _arrow(cx, cy + 2, cx, cy + GAP - 2, col)
    cy += GAP
    s, h = _box(PAD, cy, w, "Property mapping", [], col)
    out += s
    cy += h
    rows = [("CodeMeta mapper", "codemeta.json"), ("DCAT mapper", "catalog.ttl"), ("DataCite mapper", "datacite.xml")]
    bw = (w - 2 * 12) / 3
    cy += GAP
    ry = cy
    rh = 0
    for i, (m, fl) in enumerate(rows):
        x = PAD + i * (bw + 12)
        out += _arrow(cx, cy - GAP + 2, x + bw / 2, ry - 2, col, sw=2.5)
        mh = 14 + 18 + 8 + 2 * 20 + 10
        lines = g.wrap(m, 15, bw - 16, bold=True)
        out += g.rect(x, ry, bw, mh, fill=tint(col, 0.92), stroke=col, sw=2.5, rx=10)
        yy = ry + 26
        for ln in lines:
            out += g.text(x + bw / 2, yy, ln, 15, bold=True, fill=INK, anchor="middle")
            yy += 20
        out += g.text(x + bw / 2, ry + mh - 14, fl, 14.5, fill=MUTED, anchor="middle")
        rh = max(rh, mh)
    cy = ry + rh
    for i in range(3):
        x = PAD + i * (bw + 12) + bw / 2
        out += _arrow(x, cy + 2, cx, cy + GAP + 18, col, sw=2.5)
    s, h = _box(PAD, cy + GAP + 20, w, "Software marketplaces",
                ["nfdi.software and find.software", "and the KGE4RSE knowledge graph"], col, 0.84)
    return out + s, cy + GAP + 20 + h + PAD


BODIES = [body_ingest, body_model, body_curate, body_export]


def panel(idx, f, height=None):
    """(svg, width, height) of the panel of step idx (0..3)."""
    step = FOUR_STEPS[idx]
    col = step["color"]
    body, bh = BODIES[idx](f, col)
    total = max(bh + HEAD, height or 0)
    out = g.rect(0, 0, PW, total, fill=tint(col, 0.96), stroke=col, sw=3, rx=14)
    out += f'<path d="M0,{HEAD} L0,14 Q0,0 14,0 L{PW - 14},0 Q{PW},0 {PW},14 L{PW},{HEAD} z" fill="{col}"/>'
    out += g.rect(18, 15, 36, 36, fill="#ffffff", rx=9)
    out += g.text(36, 41, step["num"], 24, bold=True, fill=col, anchor="middle")
    out += g.text(70, 42, " ".join(step["title"]), 25, bold=True, fill="#ffffff")
    out += f'<g transform="translate(0,{HEAD})">{body}</g>'
    return out, PW, total


def heights(f):
    return [BODIES[i](f, FOUR_STEPS[i]["color"])[1] + HEAD for i in range(4)]
