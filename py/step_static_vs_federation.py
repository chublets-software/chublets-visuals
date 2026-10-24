"""S10 -- two ways to use the same CSV model: static pages and a real Wikibase.

The model lives as CSV tables. wikibase-static renders it as read-only HTML pages;
wikibase-federation writes it into a real Wikibase. The graphic shows the shared
source, the two routes and what comes out of each.

Style: neutral boxes; the model box carries the numbers of the model.

Reads: py/model_data.py. Produces: img/static-vs-federation.svg / .png

Runnable standalone: `python py/step_static_vs_federation.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import CATEGORY_COLORS, INK, MUTED, tint  # noqa: E402

NAME = "static-vs-federation"
GREY = "#64748b"
PURPLE, TEAL = CATEGORY_COLORS[0], CATEGORY_COLORS[2]
W = 430
GAP = 120

ROUTES = [
    ("Static", "wikibase-static", TEAL, "read-only HTML pages",
     [("What it does", "reads the CSV tables and renders the model as web pages"),
      ("Needs", "no server, no account and no write access to any Wikibase"),
      ("Wikidata items", "shown as they are in the model, including stubs"),
      ("Result", "pages that run on GitHub Pages")]),
    ("Federation", "wikibase-federation", PURPLE, "writes into a real Wikibase",
     [("What it does", "pushes the model into a Wikibase in three phases"),
      ("Needs", "an account of the target Wikibase; a dry run is the default"),
      ("Wikidata items", "become federated values; stubs are not created"),
      ("Result", "a live Wikibase; the new ids are recorded in an id map")]),
]


def build(M: model_data.Model) -> g.Canvas:
    f = model_data.caption_facts(M)
    n_ent = f["n_classes"] + f["n_props"] + f["n_items"]
    cv = g.Canvas()

    def needed(rows) -> float:
        """Height of a route box for its text; measured, so it holds on every platform."""
        h = 102.0
        for _k, v in rows:
            h += 20 + 19 * len(g.wrap(v, 14.5, W - 48)) + 20
        return h - 20 + 24

    H = max(needed(r[4]) for r in ROUTES)
    # source box, centred over the two routes
    total = 2 * W + GAP
    sw = 520
    sx = (total - sw) / 2
    out = g.rect(sx, 0, sw, 104, fill="#ffffff", stroke=GREY, sw=2, rx=14)
    out += g.text(sx + sw / 2, 36, "The model as CSV tables", 20, bold=True, fill=INK, anchor="middle")
    out += g.text(sx + sw / 2, 62, f"{n_ent} entities: {f['n_classes']} classes, {f['n_props']} properties, {f['n_items']} items", 14.5, fill=INK, anchor="middle")
    out += g.text(sx + sw / 2, 84, f"{f['n_statements']} statements · repository chublets-wikibase-demo", 13.5, fill=MUTED, anchor="middle")
    cv.add(out, sx, 0, sx + sw, 104)
    for i, (title, repo, col, sub, rows) in enumerate(ROUTES):
        x = i * (W + GAP)
        y = 190
        cx = sx + sw / 2
        tx = x + W / 2
        cv.add(g.line([(cx if i == 0 else cx, 106), (cx, 140), (tx, 140), (tx, y - 14)], MUTED, sw=2.2)
               + g.arrowhead(tx, y - 2, 0, 1, 12), min(cx, tx), 106, max(cx, tx), y)
        out = g.rect(x, y, W, H, fill=tint(col, 0.94), stroke=col, sw=2.4, rx=14)
        out += g.text(x + 24, y + 42, title, 26, bold=True, fill=col)
        out += g.text(x + 24, y + 66, f"{repo} · {sub}", 13.5, fill=MUTED)
        yy = y + 102
        for k, v in rows:
            out += g.text(x + 24, yy, k, 12.5, bold=True, fill=MUTED)
            lines = g.wrap(v, 14.5, W - 48)
            for j, ln in enumerate(lines):
                out += g.text(x + 24, yy + 20 + 19 * j, ln, 14.5, fill=INK)
            yy += 20 + 19 * len(lines) + 20
        cv.add(out, x, y, x + W, y + H)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_classes'] + facts['n_props'] + facts['n_items']} entities, {facts['n_statements']} statements")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
