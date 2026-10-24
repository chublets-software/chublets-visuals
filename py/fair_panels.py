"""The four FAIR principles as panels (S11), built from the helpers of four_steps.py.

The collage `chublets-fair` shows all four, the single graphics one principle each. Numbers come from
the model (`model_data.caption_facts`).
"""

from __future__ import annotations

import four_steps as fs
import model_graphics as g
from visuals_utils import FAIR_PRINCIPLES, MUTED, tint


def body_findable(f, col):
    w = fs.PW - 2 * fs.PAD
    items = [
        ("Persistent identifiers", [f"every one of the {f['n_items']} items has a Q-ID", "stated Wikidata items are linked by federation"], 0.92),
        ("Registries", ["indexed by nfdi.software and find.software"], 0.92),
        ("Found by", ["Q-ID, SPARQL query and cross-domain search"], 0.84),
    ]
    out, cy = fs._stack(items, fs.PAD, fs.PAD, w, col)
    return out, cy + fs.PAD


def body_accessible(f, col):
    w = fs.PW - 2 * fs.PAD
    items = [
        ("Wikibase API and SPARQL endpoint", ["open protocols, the same for every client"], 0.92),
        ("No login for reading", ["a login only gates writing"], 0.92),
        ("Static pages as well", ["the same CSV model is published as static pages"], 0.84),
    ]
    out, cy = fs._stack(items, fs.PAD, fs.PAD, w, col)
    return out, cy + fs.PAD


def body_interoperable(f, col):
    w = fs.PW - 2 * fs.PAD
    cx = fs.PW / 2
    s, h = fs._box(fs.PAD, fs.PAD, w, "CodeMeta", [f"{f['n_with_codemeta']} terms mapped to properties of the Wikibase", "the pivot between the vocabularies"], col, 0.84)
    out, cy = s, fs.PAD + h
    names = ["Wikidata", "DCAT", "DataCite", "CFF"]
    bw = (w - 3 * 10) / 4
    top = cy + fs.GAP + 8
    for i, n in enumerate(names):
        x = fs.PAD + i * (bw + 10)
        out += fs._arrow(cx, cy + 2, x + bw / 2, top - 2, col, sw=2.5)
        out += g.rect(x, top, bw, 46, fill=tint(col, 0.92), stroke=col, sw=2.5, rx=10)
        out += g.text(x + bw / 2, top + 29, n, 16, bold=True, anchor="middle")
    out += g.text(cx, top + 46 + 24, "each pair is mapped through CodeMeta, not one by one", 14, fill=MUTED, anchor="middle")
    return out, top + 46 + 24 + fs.PAD


def body_reusable(f, col):
    w = fs.PW - 2 * fs.PAD
    items = [
        ("Licence", ["copyright licence (P107) on every chublet item", "taken over from CITATION.cff"], 0.92),
        ("Provenance", [f"{f['n_with_ref']} of {f['n_statements']} statements carry a reference", f"{f['n_with_qual']} carry a qualifier such as a date"], 0.92),
        ("Attribution", ["properties for copyright holder (P167) and year (P168)"], 0.84),
    ]
    out, cy = fs._stack(items, fs.PAD, fs.PAD, w, col)
    return out, cy + fs.PAD


BODIES = [body_findable, body_accessible, body_interoperable, body_reusable]


def panel(idx, f, height=None):
    step = FAIR_PRINCIPLES[idx]
    body, bh = BODIES[idx](f, step["color"])
    return fs.frame(step, body, bh, height)


def heights(f):
    return [BODIES[i](f, FAIR_PRINCIPLES[i]["color"])[1] + fs.HEAD for i in range(4)]
