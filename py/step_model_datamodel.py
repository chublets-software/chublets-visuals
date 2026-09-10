"""S4b (2/4) -- Model: compact datamodel card.

Detail diagram behind the "Model" badge from S4. Same header treatment as
the other three S4b diagrams (small badge + "Step N -- Title", Flo,
2026-09-10: consistent step marker on every detail diagram) followed by
one content card -- not a redraw of chublets-wikibase-datamodel (S2), but
the same numbers, read live from the same two sources so the two diagrams
can never quietly disagree (A3).

Produces:
  img/block-3-four-step-pattern/step-2-model-detail.svg / .png (transparent)

Runnable standalone: `python py/step_model_datamodel.py`
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    BLOCK3_DIR,
    DATA_RAW,
    FOUR_STEPS,
    INK,
    MUTED,
    ROOT,
    ensure_dirs,
    esc,
    font_face_css,
    label_box,
    render_svg_to_png,
    step_header,
    tint,
    trim_transparent_border,
)
import crosswalk_data  # noqa: E402

STEP_IDX = 1
STEP = FOUR_STEPS[STEP_IDX]
ACCENT = STEP["color"]  # purple -- same as the Model badge

CARD_W = 900
CARD_H = 190
MARGIN = 50
GAP_HEADER_TO_CARD = 40

OVERSAMPLE = 1.9


def _build_svg(n_wikidata: int, n_codemeta_only: int) -> tuple[str, float, float]:
    header_svg, top_y = step_header(STEP_IDX, STEP, MARGIN, MARGIN)
    top_y += GAP_HEADER_TO_CARD

    W = MARGIN * 2 + CARD_W
    H = top_y + CARD_H + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append(header_svg)

    p.append(label_box(
        MARGIN, top_y, CARD_W, CARD_H,
        [
            (f"{n_wikidata}+ Wikidata properties reused", 700, 24),
            (f"{n_codemeta_only} CodeMeta-only properties added", 700, 24),
            ("= one federated schema, via Wikibase federation", 400, 18),
        ],
        fill=tint(ACCENT, 0.9), stroke=ACCENT, text_color=INK,
    ))

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK3_DIR)
    log: list[str] = []

    with open(DATA_RAW / "wikidata-software-properties.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    n_wikidata = sum(1 for r in rows if r["pid"] != "-")

    sections = crosswalk_data.load(DATA_RAW / "codemeta-wikidata-crosswalk.xlsx")
    counts = crosswalk_data.counts(sections)
    total_all = sum(t for t, _ in counts.values())
    mapped_all = sum(m for _, m in counts.values())
    n_codemeta_only = total_all - mapped_all
    log.append(f"read {n_wikidata} Wikidata properties, {n_codemeta_only} CodeMeta-only fields (same sources as S2)")

    svg_text, w, h = _build_svg(n_wikidata, n_codemeta_only)
    svg_path = BLOCK3_DIR / "step-2-model-detail.svg"
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
