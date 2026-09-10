"""S6b (1/3) -- the two routes into Wikidata.

Grounded directly in github.com/n4o-rse/open-archaeo (py/main.py,
py/split.py, out/OpenRefine/README.md, out/Python/README.md), not from
memory the way the original S6 diagram was -- see PRIMER.md A1 Befund 10
for the discrepancies that surfaced (the real repo has evolved past what
S6 described: two obligatory statements, not six, and an explicit
two-team split rather than a single linear pipeline).

open-archaeo.csv (562) -> transform (416 software subset) -> split
(stratified, deterministic) -> two non-overlapping 208-entry slices, one
per tool, that hand back into a shared vocabulary and concordance.

Produces:
  img/system-architecture/open-archaeo-two-routes.svg / .png (transparent)

Runnable standalone: `python py/step_open_archaeo_two_routes.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    CATEGORY_COLORS,
    INK,
    MUTED,
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

GREY = CATEGORY_COLORS[5]
TEAL = CATEGORY_COLORS[2]     # OpenRefine slice
PURPLE = CATEGORY_COLORS[0]   # Python slice

MARGIN = 60
OVERSAMPLE = 1.8

ROW1_W, ROW1_H = 260, 110
ROW2_W, ROW2_H = 340, 130
ROW3_W, ROW3_H = 460, 110
GAP_X1 = 50
GAP_X2 = 70
V_GAP = 80


def _build_svg() -> tuple[str, float, float]:
    row1 = [
        ("open-archaeo.csv", "562 entries", GREY),
        ("transform", "416-entry software subset", GREY),
        ("split", "stratified, deterministic", GREY),
    ]
    total_w1 = 3 * ROW1_W + 2 * GAP_X1
    total_w2 = 2 * ROW2_W + GAP_X2
    W = MARGIN * 2 + max(total_w1, total_w2, ROW3_W)

    row1_y = MARGIN
    row2_y = row1_y + ROW1_H + V_GAP
    row3_y = row2_y + ROW2_H + V_GAP
    H = row3_y + ROW3_H + MARGIN

    xs1 = [MARGIN + (W - MARGIN * 2 - total_w1) / 2 + i * (ROW1_W + GAP_X1) for i in range(3)]
    xs2 = [MARGIN + (W - MARGIN * 2 - total_w2) / 2 + i * (ROW2_W + GAP_X2) for i in range(2)]
    x3 = MARGIN + (W - MARGIN * 2 - ROW3_W) / 2

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", MUTED))
    p.append("</defs>")

    for i, (x, (title, sub, color)) in enumerate(zip(xs1, row1)):
        p.append(label_box(x, row1_y, ROW1_W, ROW1_H, [(title, 700, 20), (sub, 400, 14)],
                            fill=tint(color, 0.92), stroke=color, text_color=INK))
        if i < 2:
            x2 = x + ROW1_W
            y = row1_y + ROW1_H / 2
            p.append(f'<line x1="{x2}" y1="{y}" x2="{xs1[i+1]-6}" y2="{y}" '
                      f'stroke="{MUTED}" stroke-width="4" marker-end="url(#arrow)"/>')

    split_cx = xs1[2] + ROW1_W / 2
    split_bottom = row1_y + ROW1_H
    row2 = [
        ("OpenRefine slice", "208 entries \u2192 out/OpenRefine/", TEAL),
        ("Python slice", "208 entries \u2192 out/Python/", PURPLE),
    ]
    for x, (title, sub, color) in zip(xs2, row2):
        cx = x + ROW2_W / 2
        p.append(f'<line x1="{split_cx}" y1="{split_bottom}" x2="{cx}" y2="{row2_y}" '
                  f'stroke="{MUTED}" stroke-width="3.5" marker-end="url(#arrow)"/>')
        p.append(label_box(x, row2_y, ROW2_W, ROW2_H, [(title, 700, 22), (sub, 400, 15)],
                            fill=tint(color, 0.9), stroke=color, text_color=INK))

    for x in xs2:
        cx = x + ROW2_W / 2
        p.append(f'<line x1="{cx}" y1="{row2_y+ROW2_H}" x2="{x3+ROW3_W/2}" y2="{row3_y}" '
                  f'stroke="{MUTED}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    p.append(label_box(
        x3, row3_y, ROW3_W, ROW3_H,
        [("Shared vocabulary + concordance", 700, 21),
         ("vocabulary.json (from OpenRefine) + concordance.csv (id, qid)", 400, 14)],
        fill=tint(GREY, 0.88), stroke=GREY, text_color=INK,
    ))

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(SYSTEM_ARCH_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = SYSTEM_ARCH_DIR / "open-archaeo-two-routes.svg"
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
