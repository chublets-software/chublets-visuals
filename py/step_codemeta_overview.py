"""Block 1 (1/4) -- CodeMeta term overview.

Replaces the codemeta.github.io force-directed term graph (the original
F25 slide, a screenshot of an external tool's output) with a class-
inheritance diagram in the chublets house style, built from the same
source the crosswalk step reads: data/raw/codemeta-wikidata-crosswalk.xlsx
(column A per CodeMeta type). A force-directed layout is not
reproducible byte-for-byte across runs (solver-dependent node
positions), which conflicts with this repo's determinism rule; a class
diagram is, and it is also the more legible print/paper figure.

Hierarchy is Thing -> CreativeWork -> {SoftwareSourceCode,
SoftwareApplication}, the schema.org chain CodeMeta itself documents.
Property lists are exhaustive per type (not a curated subset), so the
box sizes directly show the real distribution: SoftwareSourceCode is a
short, specific box; SoftwareApplication and CreativeWork are long,
general ones.

Produces:
  img/chublets-codemeta-overview.svg / .png (transparent)

Runnable standalone: `python py/step_codemeta_overview.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    DATA_RAW,
    IMG_DIR,
    INK,
    MUTED,
    CATEGORY_COLORS,
    ensure_dirs,
    esc,
    font_face_css,
    open_triangle,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)
import crosswalk_data  # noqa: E402

BOX_W = 560
FIELD_H = 27
HEADER_H = 50
PAD_V = 16
V_GAP = 130       # vertical gap between a parent box's bottom and its children's top
H_GAP = 90        # horizontal gap between the two leaf boxes
MARGIN = 60

OVERSAMPLE = 1.7

# type -> (colour, header label shown in the box)
TYPE_COLOR = {
    "Thing": CATEGORY_COLORS[5],               # neutral -- the schema.org root
    "CreativeWork": CATEGORY_COLORS[0],         # purple -- house primary
    "SoftwareSourceCode": CATEGORY_COLORS[2],   # teal
    "SoftwareApplication": CATEGORY_COLORS[1],  # gold
}


def _box_height(n_fields: int) -> float:
    return HEADER_H + n_fields * FIELD_H + 2 * PAD_V


def _render_box(x: float, y: float, title: str, fields: list[str], color: str) -> str:
    h = _box_height(len(fields))
    fill = tint(color, 0.9)
    out = f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{h}" rx="6" fill="{fill}" stroke="{color}" stroke-width="3"/>'
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+32}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="26" fill="{INK}">{esc(title)}</text>'
    )
    out += f'<line x1="{x}" y1="{y+HEADER_H}" x2="{x+BOX_W}" y2="{y+HEADER_H}" stroke="{color}" stroke-width="2.5"/>'
    fy = y + HEADER_H + 21
    for name in fields:
        out += (
            f'<text x="{x+16}" y="{fy}" text-anchor="start" font-family="Fira Sans" '
            f'font-weight="400" font-size="17" fill="{INK}">+ {esc(name)}</text>'
        )
        fy += FIELD_H
    return out


def _build_svg(sections: dict[str, list[tuple[str, str | None]]]) -> tuple[str, float, float]:
    fields = {t: [name for name, _ in rows] for t, rows in sections.items()}
    heights = {t: _box_height(len(fields[t])) for t in fields}

    thing_x = MARGIN + (2 * BOX_W + H_GAP) / 2 - BOX_W / 2
    thing_y = MARGIN

    cw_x = thing_x
    cw_y = thing_y + heights["Thing"] + V_GAP

    leaves_y = cw_y + heights["CreativeWork"] + V_GAP
    src_x = MARGIN
    app_x = MARGIN + BOX_W + H_GAP

    W = MARGIN * 2 + 2 * BOX_W + H_GAP
    H = leaves_y + max(heights["SoftwareSourceCode"], heights["SoftwareApplication"]) + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())

    # inheritance connectors, drawn before the boxes they touch
    p.append(open_triangle(cw_x + BOX_W / 2, cw_y, thing_x + BOX_W / 2, thing_y + heights["Thing"], color=MUTED))
    p.append(open_triangle(src_x + BOX_W / 2, leaves_y, cw_x + BOX_W * 0.3, cw_y + heights["CreativeWork"], color=MUTED))
    p.append(open_triangle(app_x + BOX_W / 2, leaves_y, cw_x + BOX_W * 0.7, cw_y + heights["CreativeWork"], color=MUTED))

    p.append(_render_box(thing_x, thing_y, "Thing", fields["Thing"], TYPE_COLOR["Thing"]))
    p.append(_render_box(cw_x, cw_y, "CreativeWork", fields["CreativeWork"], TYPE_COLOR["CreativeWork"]))
    p.append(_render_box(src_x, leaves_y, "SoftwareSourceCode", fields["SoftwareSourceCode"], TYPE_COLOR["SoftwareSourceCode"]))
    p.append(_render_box(app_x, leaves_y, "SoftwareApplication", fields["SoftwareApplication"], TYPE_COLOR["SoftwareApplication"]))

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs()
    log: list[str] = []

    sections = crosswalk_data.load(DATA_RAW / "codemeta-wikidata-crosswalk.xlsx")
    total = sum(len(rows) for rows in sections.values())
    log.append(f"read {total} CodeMeta properties across {len(sections)} types from crosswalk xlsx")

    svg_text, w, h = _build_svg(sections)
    svg_path = IMG_DIR / "chublets-codemeta-overview.svg"
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
