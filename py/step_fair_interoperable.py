"""Block 2 (4/5) -- Interoperable.

Detail diagram behind the "Interoperable" badge: CodeMeta as the hub that
chublets.software reads/writes against, with the four vocabularies it
bridges as spokes. Unlike the other three FAIR detail cards this one gets
an actual hub-and-spoke diagram, not just a text card -- "interoperable"
specifically means "connects several vocabularies", so showing the
connections communicates more than a sentence about them would.

Produces:
  img/block-2-fair4rs-chain/fair-interoperable-detail.svg / .png (transparent)

Runnable standalone: `python py/step_fair_interoperable.py`
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
    arrow_marker,
    ensure_dirs,
    fair4rs_icon,
    font_face_css,
    label_box,
    render_svg_to_png,
    step_header,
    tint,
    trim_transparent_border,
)

IDX = 2
PRINCIPLE = FAIR_PRINCIPLES[IDX]
ACCENT = PRINCIPLE["color"]

HUB_W, HUB_H = 260, 90
SPOKE_W, SPOKE_H = 220, 80
GAP_X = 40
MARGIN = 50
GAP_HEADER_TO_HUB = 50
GAP_HUB_TO_SPOKES = 90

OVERSAMPLE = 1.8

SPOKES = ["Wikidata", "DCAT", "DataCite", "CFF"]


def _build_svg() -> tuple[str, float, float]:
    header_svg, top_y = step_header(IDX, PRINCIPLE, MARGIN, MARGIN, icon_fn=fair4rs_icon, prefix="")
    hub_y = top_y + GAP_HEADER_TO_HUB
    spoke_y = hub_y + HUB_H + GAP_HUB_TO_SPOKES

    n = len(SPOKES)
    spokes_w = n * SPOKE_W + (n - 1) * GAP_X
    W = MARGIN * 2 + max(spokes_w, HUB_W)
    H = spoke_y + SPOKE_H + MARGIN

    hub_x = MARGIN + (W - MARGIN * 2 - HUB_W) / 2
    spokes_x0 = MARGIN + (W - MARGIN * 2 - spokes_w) / 2
    xs = [spokes_x0 + i * (SPOKE_W + GAP_X) for i in range(n)]

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", ACCENT))
    p.append("</defs>")
    p.append(header_svg)

    hub_cx = hub_x + HUB_W / 2
    hub_bottom = hub_y + HUB_H
    for x in xs:
        cx = x + SPOKE_W / 2
        p.append(f'<line x1="{hub_cx}" y1="{hub_bottom}" x2="{cx}" y2="{spoke_y}" '
                  f'stroke="{ACCENT}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    p.append(label_box(hub_x, hub_y, HUB_W, HUB_H, [("CodeMeta", 700, 24)],
                        fill=tint(ACCENT, 0.85), stroke=ACCENT, text_color=INK))

    spoke_fill = tint(ACCENT, 0.92)
    for x, name in zip(xs, SPOKES):
        p.append(label_box(x, spoke_y, SPOKE_W, SPOKE_H, [(name, 700, 20)],
                            fill=spoke_fill, stroke=ACCENT, text_color=INK))

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK2_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = BLOCK2_DIR / "fair-interoperable-detail.svg"
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
