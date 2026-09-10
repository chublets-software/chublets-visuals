"""S4b (4/4) -- Export & Publish: the export pipeline.

Detail diagram behind the "Export & Publish" badge from S4. Content
carried over from the old F28 workflow panel (SPARQL endpoint -> CONSTRUCT
query -> parse with rdflib -> per-vocabulary mapper -> output file ->
marketplace) -- same caveat as chublets-curate-workflow: conceptual
sequence from the talk chat, not yet checked against real pipeline code
(PRIMER.md Teil D).

Produces:
  img/chublets-export-pipeline.svg / .png (transparent)

Runnable standalone: `python py/step_export_pipeline.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    FOUR_STEPS,
    IMG_DIR,
    INK,
    MUTED,
    arrow_marker,
    ensure_dirs,
    font_face_css,
    label_box,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)

ACCENT = FOUR_STEPS[3]["color"]  # slate blue -- same as the Export & Publish badge

BOX_W = 260
GAP_X = 50
MARGIN = 50

ROW1_Y, ROW1_H = 50, 90
ROW2_Y, ROW2_H = 220, 90
ROW3_Y, ROW3_H = 380, 70
ROW4_Y, ROW4_H = 510, 110

OVERSAMPLE = 1.8

ROW1 = ["SPARQL endpoint", "CONSTRUCT query", "Parse RDF (rdflib)", "Property mapping"]
ROW2 = ["CodeMeta mapper", "DCAT mapper", "DataCite mapper"]
ROW3 = ["codemeta.json", "catalog.ttl", "datacite.xml"]


def _row_xs(n: int, total_w: float) -> list[float]:
    group_w = n * BOX_W + (n - 1) * GAP_X
    start = MARGIN + (total_w - group_w) / 2
    return [start + i * (BOX_W + GAP_X) for i in range(n)]


def _build_svg() -> tuple[str, float, float]:
    total_w = 4 * BOX_W + 3 * GAP_X  # row 1 sets the overall width
    W = MARGIN * 2 + total_w
    H = ROW4_Y + ROW4_H + MARGIN

    xs1 = _row_xs(4, total_w)
    xs2 = _row_xs(3, total_w)
    xs3 = xs2  # each output sits directly under its mapper

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", ACCENT))
    p.append("</defs>")

    fill = tint(ACCENT, 0.9)

    # Row 1: the linear read-and-parse chain
    for i, title in enumerate(ROW1):
        p.append(label_box(xs1[i], ROW1_Y, BOX_W, ROW1_H, [(title, 700, 20)], fill=fill, stroke=ACCENT, text_color=INK))
        if i < 3:
            x2 = xs1[i] + BOX_W
            y = ROW1_Y + ROW1_H / 2
            p.append(f'<line x1="{x2}" y1="{y}" x2="{xs1[i+1]-6}" y2="{y}" '
                      f'stroke="{ACCENT}" stroke-width="4" marker-end="url(#arrow)"/>')

    # branch: Property mapping (last of row 1) fans out to the 3 mappers
    src_x = xs1[3] + BOX_W / 2
    src_y = ROW1_Y + ROW1_H
    for x in xs2:
        p.append(f'<line x1="{src_x}" y1="{src_y}" x2="{x+BOX_W/2}" y2="{ROW2_Y}" '
                  f'stroke="{ACCENT}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    # Row 2: the three vocabulary mappers
    for i, title in enumerate(ROW2):
        p.append(label_box(xs2[i], ROW2_Y, BOX_W, ROW2_H, [(title, 700, 20)], fill=fill, stroke=ACCENT, text_color=INK))

    # Row 2 -> Row 3: one arrow each, straight down
    for x in xs2:
        cx = x + BOX_W / 2
        p.append(f'<line x1="{cx}" y1="{ROW2_Y+ROW2_H}" x2="{cx}" y2="{ROW3_Y}" '
                  f'stroke="{ACCENT}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    # Row 3: the three output files
    outfill = tint(ACCENT, 0.95)
    for i, title in enumerate(ROW3):
        p.append(label_box(xs3[i], ROW3_Y, BOX_W, ROW3_H, [(title, 400, 18)], fill=outfill, stroke=ACCENT, text_color=INK))

    # converge: three outputs -> one marketplace box
    dst_x, dst_y = W / 2, ROW4_Y
    for x in xs3:
        p.append(f'<line x1="{x+BOX_W/2}" y1="{ROW3_Y+ROW3_H}" x2="{dst_x}" y2="{dst_y}" '
                  f'stroke="{ACCENT}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    p.append(label_box(
        (W - total_w) / 2, ROW4_Y, total_w, ROW4_H,
        [("nfdi.software & find.software", 700, 24), ("+ KGE4RSE knowledge graph", 400, 17)],
        fill=tint(ACCENT, 0.85), stroke=ACCENT, text_color=INK,
    ))

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs()
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = IMG_DIR / "chublets-export-pipeline.svg"
    svg_path.write_text(svg_text, encoding="utf-8")
    png_path = svg_path.with_suffix(".png")
    render_svg_to_png(svg_path, png_path, int(w * OVERSAMPLE), int(h * OVERSAMPLE))
    final_w, final_h = trim_transparent_border(png_path, margin_px=10)
    log.append(
        f"wrote {svg_path.relative_to(IMG_DIR.parent)} + .png "
        f"({final_w}x{final_h}, transparent, <=10px border)"
    )
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
