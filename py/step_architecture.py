"""S5 -- chublets.software system architecture.

Consolidates the old F28 three-panel workflow (Wikibase class diagram /
workflow / output) into one diagram, and makes the Wikidata bridge an
explicit first stage rather than folding it silently into "data sources"
the way F28 did (Talk-Chat: F28 already listed "Wikidata IDs" as one input
alongside the open-archaeo CSV, but never showed that they are two
different systems -- the public Wikidata chublets bridge, active today,
versus the not-yet-built chublets Wikibase).

Five stages, each coloured to match its Block 3 badge where one applies
(Data sources = Ingest = teal, chublets Wikibase = Model = purple, Export
pipeline = Export & Publish = slate blue); the two boundary stages
(Wikidata bridge, Marketplaces & KG) are neutral grey, matching the
"boundary vs. chublets-specific" colour convention chublets-wikibase-
datamodel and chublets-four-step-pattern already use.

The datamodel numbers in stage 3 are read live from the same two sources
as chublets-wikibase-datamodel (S2) and chublets-model-datamodel (S4b) --
three diagrams, one set of numbers (A3).

Produces:
  img/system-architecture/chublets-software-architecture.svg / .png (transparent)

Runnable standalone: `python py/step_architecture.py`
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    CATEGORY_COLORS,
    DATA_RAW,
    FOUR_STEPS,
    INK,
    ROOT,
    SYSTEM_ARCH_DIR,
    arrow_marker,
    ensure_dirs,
    font_face_css,
    label_box,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)
import crosswalk_data  # noqa: E402

NEUTRAL = CATEGORY_COLORS[5]
TEAL = FOUR_STEPS[0]["color"]     # Ingest / data sources
PURPLE = FOUR_STEPS[1]["color"]   # Model / chublets Wikibase
SLATE = FOUR_STEPS[3]["color"]    # Export & Publish

BOX_W = 300
BOX_H = 190
GAP_X = 50
TOP_Y = 60
MARGIN = 60

OVERSAMPLE = 1.7


def _build_svg(n_wikidata: int, n_codemeta_only: int) -> tuple[str, float, float]:
    stages = [
        ([("Wikidata bridge", 700, 21), ("open-archaeo import pipeline", 400, 15), ("active -- see S6", 400, 15)], NEUTRAL),
        ([("Data sources", 700, 21), ("Wikidata items, FDOx objects,", 400, 15), ("Git repos via CFF", 400, 15)], TEAL),
        ([("chublets.software Wikibase", 700, 19), (f"{n_wikidata}+ Wikidata + {n_codemeta_only} CodeMeta-only", 400, 15), ("modelled, curated, linked", 400, 15)], PURPLE),
        ([("Export pipeline", 700, 21), ("SPARQL \u2192 rdflib \u2192", 400, 15), ("CodeMeta / DCAT / DataCite", 400, 15)], SLATE),
        ([("Marketplaces & KG", 700, 21), ("nfdi.software, find.software,", 400, 15), ("+ KGE4RSE", 400, 15)], NEUTRAL),
    ]
    n = len(stages)
    total_w = n * BOX_W + (n - 1) * GAP_X
    W = MARGIN * 2 + total_w
    H = TOP_Y + BOX_H + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", INK))
    p.append("</defs>")

    for i, (lines, color) in enumerate(stages):
        x = MARGIN + i * (BOX_W + GAP_X)
        fill = tint(color, 0.9)
        p.append(label_box(x, TOP_Y, BOX_W, BOX_H, lines, fill=fill, stroke=color, text_color=INK))
        if i < n - 1:
            x2 = x + BOX_W
            y = TOP_Y + BOX_H / 2
            p.append(f'<line x1="{x2}" y1="{y}" x2="{x2+GAP_X-6}" y2="{y}" '
                      f'stroke="{INK}" stroke-width="4" marker-end="url(#arrow)"/>')

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(SYSTEM_ARCH_DIR)
    log: list[str] = []

    with open(DATA_RAW / "wikidata-software-properties.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    n_wikidata = sum(1 for r in rows if r["pid"] != "-")

    sections = crosswalk_data.load(DATA_RAW / "codemeta-wikidata-crosswalk.xlsx")
    counts = crosswalk_data.counts(sections)
    total_all = sum(t for t, _ in counts.values())
    mapped_all = sum(m for _, m in counts.values())
    n_codemeta_only = total_all - mapped_all
    log.append(f"read {n_wikidata} Wikidata properties, {n_codemeta_only} CodeMeta-only fields (same sources as S2/S4b)")

    svg_text, w, h = _build_svg(n_wikidata, n_codemeta_only)
    svg_path = SYSTEM_ARCH_DIR / "chublets-software-architecture.svg"
    svg_path.write_text(svg_text, encoding="utf-8")
    png_path = svg_path.with_suffix(".png")
    render_svg_to_png(svg_path, png_path, int(w * OVERSAMPLE), int(h * OVERSAMPLE))
    final_w, final_h = trim_transparent_border(png_path, margin_px=10)
    log.append(
        f"wrote {svg_path.relative_to(ROOT)} + .png "
        f"({final_w}x{final_h}, transparent, <=10px border)"
    )
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
