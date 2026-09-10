"""Block 2 (5/5) -- Reusable.

Detail diagram behind the "Reusable" badge. Mechanism per PRIMER.md A4
(proposal, not yet checked against the deRSE26 paper's FAIR table).

Produces:
  img/block-2-fair4rs-chain/fair-reusable-detail.svg / .png (transparent)

Runnable standalone: `python py/step_fair_reusable.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    BLOCK2_DIR,
    FAIR_PRINCIPLES,
    INK,
    ROOT,
    ensure_dirs,
    fair4rs_icon,
    font_face_css,
    label_box,
    render_svg_to_png,
    step_header,
    tint,
    trim_transparent_border,
)

IDX = 3
PRINCIPLE = FAIR_PRINCIPLES[IDX]
ACCENT = PRINCIPLE["color"]

CARD_W = 900
CARD_H = 190
MARGIN = 50
GAP_HEADER_TO_CARD = 40

OVERSAMPLE = 1.9


def _build_svg() -> tuple[str, float, float]:
    header_svg, top_y = step_header(IDX, PRINCIPLE, MARGIN, MARGIN, icon_fn=fair4rs_icon, prefix="")
    top_y += GAP_HEADER_TO_CARD

    W = MARGIN * 2 + CARD_W
    H = top_y + CARD_H + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append(header_svg)

    p.append(label_box(
        MARGIN, top_y, CARD_W, CARD_H,
        [
            ("License & provenance statements", 700, 24),
            ("Carried forward from CFF, dated qualifiers", 700, 24),
            ("= copyright license (P275) + attribution on every chublet item", 400, 17),
        ],
        fill=tint(ACCENT, 0.9), stroke=ACCENT, text_color=INK,
    ))

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK2_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = BLOCK2_DIR / "fair-reusable-detail.svg"
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
