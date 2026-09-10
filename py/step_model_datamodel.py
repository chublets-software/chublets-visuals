"""S4b (2/4) -- Model: compact datamodel card.

Detail diagram behind the "Model" badge from S4. Deliberately not a
redraw of chublets-wikibase-datamodel (S2) -- same numbers, read live
from the same two sources so the two diagrams can never quietly disagree
(A3), but laid out as a single compact card next to the Model icon rather
than the two-source-plus-result diagram S2 draws for its own, more
detailed context.

Produces:
  img/chublets-model-datamodel.svg / .png (transparent)

Runnable standalone: `python py/step_model_datamodel.py`
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    DATA_RAW,
    FOUR_STEPS,
    IMG_DIR,
    INK,
    MUTED,
    ensure_dirs,
    esc,
    font_face_css,
    four_step_icon,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)
import crosswalk_data  # noqa: E402

ACCENT = FOUR_STEPS[1]["color"]  # purple -- same as the Model badge

W = 1100
H = 260
ICON_R = 90
MARGIN = 50

OVERSAMPLE = 2.0


def _build_svg(n_wikidata: int, n_codemeta_only: int) -> str:
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())

    icon_cx, icon_cy = MARGIN + ICON_R, H / 2
    fill = tint(ACCENT, 0.88)
    p.append(f'<circle cx="{icon_cx}" cy="{icon_cy}" r="{ICON_R}" fill="{fill}" stroke="{ACCENT}" stroke-width="6"/>')
    p.append(f'<g transform="translate({icon_cx},{icon_cy})">{four_step_icon(1, ACCENT)}</g>')

    text_x = icon_cx + ICON_R + 50
    p.append(
        f'<text x="{text_x}" y="{H/2-38}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="34" fill="{INK}">chublets.software datamodel</text>'
    )
    p.append(
        f'<text x="{text_x}" y="{H/2+8}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="22" fill="{ACCENT}">{n_wikidata}+ Wikidata properties reused</text>'
    )
    p.append(
        f'<text x="{text_x}" y="{H/2+42}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="22" fill="{ACCENT}">{n_codemeta_only} CodeMeta-only properties added</text>'
    )
    p.append(
        f'<text x="{text_x}" y="{H/2+78}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="400" font-size="17" fill="{MUTED}">= one federated schema, via Wikibase federation</text>'
    )

    p.append("</svg>")
    return "\n".join(p)


def run(strict: bool = False) -> list[str]:
    ensure_dirs()
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

    svg_text = _build_svg(n_wikidata, n_codemeta_only)
    svg_path = IMG_DIR / "chublets-model-datamodel.svg"
    svg_path.write_text(svg_text, encoding="utf-8")
    png_path = svg_path.with_suffix(".png")
    render_svg_to_png(svg_path, png_path, int(W * OVERSAMPLE), int(H * OVERSAMPLE))
    final_w, final_h = trim_transparent_border(png_path, margin_px=10)
    log.append(
        f"wrote {svg_path.relative_to(IMG_DIR.parent)} + .png "
        f"({final_w}x{final_h}, transparent, <=10px border)"
    )
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
