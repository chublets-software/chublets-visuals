"""S4b (3/4) -- Curate & Link: the curation workflow.

Detail diagram behind the "Curate & Link" badge from S4. Content carried
over from the old F28 workflow panel (Create -> Statements & Qualifiers
-> Manual Curation -> Quality Control) -- not yet checked against actual
pipeline code the way S2's crosswalk numbers are (PRIMER.md Teil D); this
is the conceptual sequence agreed in the talk chat, not a count of
anything.

Produces:
  img/block-3-four-step-pattern/step-3-curate-link-detail.svg / .png (transparent)

Runnable standalone: `python py/step_curate_workflow.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    BLOCK3_DIR,
    FOUR_STEPS,
    INK,
    ROOT,
    arrow_marker,
    ensure_dirs,
    font_face_css,
    label_box,
    render_svg_to_png,
    step_header,
    tint,
    trim_transparent_border,
)

STEP_IDX = 2
STEP = FOUR_STEPS[STEP_IDX]
ACCENT = STEP["color"]  # gold -- same as the Curate & Link badge

BOX_W = 260
BOX_H = 150
GAP_X = 70
MARGIN = 50
GAP_HEADER_TO_STAGES = 40

OVERSAMPLE = 1.8

STAGES = [
    ("Create items", "New Wikibase items / Q-IDs"),
    ("Add statements", "Values + qualifiers per property"),
    ("Manual curation", "Human review of ambiguous cases"),
    ("Quality control", "Constraint checks before publish"),
]


def _build_svg() -> tuple[str, float, float]:
    header_svg, top_y = step_header(STEP_IDX, STEP, MARGIN, MARGIN)
    top_y += GAP_HEADER_TO_STAGES

    n = len(STAGES)
    total_w = n * BOX_W + (n - 1) * GAP_X
    W = MARGIN * 2 + total_w
    H = top_y + BOX_H + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", ACCENT))
    p.append("</defs>")
    p.append(header_svg)

    fill = tint(ACCENT, 0.9)
    for i, (title, sub) in enumerate(STAGES):
        x = MARGIN + i * (BOX_W + GAP_X)
        p.append(label_box(
            x, top_y, BOX_W, BOX_H,
            [(title, 700, 21), (sub, 400, 15.5)],
            fill=fill, stroke=ACCENT, text_color=INK,
        ))
        if i < n - 1:
            x2 = x + BOX_W
            y = top_y + BOX_H / 2
            p.append(f'<line x1="{x2}" y1="{y}" x2="{x2+GAP_X-6}" y2="{y}" '
                      f'stroke="{ACCENT}" stroke-width="4" marker-end="url(#arrow)"/>')

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK3_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = BLOCK3_DIR / "step-3-curate-link-detail.svg"
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
