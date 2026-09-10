"""Block 1 (3/4) -- CodeMeta <-> Wikidata crosswalk.

Same class tree as chublets-codemeta-overview (Thing -> CreativeWork ->
{SoftwareSourceCode, SoftwareApplication}), but every field now carries its
crosswalk status: the mapped Wikidata property id in the accent colour on
the right of a normal-weight row, or a muted em-dash and greyed-out text
when data/raw/codemeta-wikidata-crosswalk.xlsx records no mapping. Reads
the same source as the overview step, via the shared crosswalk_data
parser -- one parse, two views (A3: one source, not two hand-kept lists).

Befund (2026-09-10, from the xlsx as parsed): 68 CodeMeta properties
across the four types, 33 mapped to a Wikidata property, 35 not. The
unmapped 35 are exactly the "CodeMeta-only fields" chublets-wikibase-
datamodel (Block 1, step 4/4) shows as needing new chublets Wikibase
properties rather than reused Wikidata ones.

Produces:
  img/chublets-codemeta-wikidata-crosswalk.svg / .png (transparent)

Runnable standalone: `python py/step_codemeta_wikidata_crosswalk.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    DATA_RAW,
    BLOCK1_DIR,
    ROOT,
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

BOX_W = 620
FIELD_H = 27
HEADER_H = 50
PAD_V = 16
V_GAP = 130
H_GAP = 90
MARGIN = 60
FOOTNOTE_H = 50

OVERSAMPLE = 1.7

TYPE_COLOR = {
    "Thing": CATEGORY_COLORS[5],
    "CreativeWork": CATEGORY_COLORS[0],
    "SoftwareSourceCode": CATEGORY_COLORS[2],
    "SoftwareApplication": CATEGORY_COLORS[1],
}


def _box_height(n_fields: int) -> float:
    return HEADER_H + n_fields * FIELD_H + 2 * PAD_V


def _render_box(x: float, y: float, title: str, rows: list[tuple[str, str | None]],
                 total: int, mapped: int, color: str) -> str:
    h = _box_height(len(rows))
    fill = tint(color, 0.9)
    out = f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{h}" rx="6" fill="{fill}" stroke="{color}" stroke-width="3"/>'
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+32}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="24" fill="{INK}">{esc(title)}</text>'
    )
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+HEADER_H-6}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="400" font-size="14" fill="{MUTED}">{mapped} of {total} mapped to Wikidata</text>'
    )
    out += f'<line x1="{x}" y1="{y+HEADER_H}" x2="{x+BOX_W}" y2="{y+HEADER_H}" stroke="{color}" stroke-width="2.5"/>'
    fy = y + HEADER_H + 21
    for name, pid in rows:
        text_color = INK if pid else MUTED
        out += (
            f'<text x="{x+16}" y="{fy}" text-anchor="start" font-family="Fira Sans" '
            f'font-weight="400" font-size="16.5" fill="{text_color}">+ {esc(name)}</text>'
        )
        right = pid if pid else "\u2013"
        right_color = color if pid else MUTED
        out += (
            f'<text x="{x+BOX_W-16}" y="{fy}" text-anchor="end" font-family="Fira Sans" '
            f'font-weight="{"700" if pid else "400"}" font-size="15" fill="{right_color}">{esc(right)}</text>'
        )
        fy += FIELD_H
    return out


def _build_svg(sections: dict[str, list[tuple[str, str | None]]]) -> tuple[str, float, float]:
    fields = sections
    counts = crosswalk_data.counts(sections)
    heights = {t: _box_height(len(fields[t])) for t in fields}

    thing_x = MARGIN + (2 * BOX_W + H_GAP) / 2 - BOX_W / 2
    thing_y = MARGIN

    cw_x = thing_x
    cw_y = thing_y + heights["Thing"] + V_GAP

    leaves_y = cw_y + heights["CreativeWork"] + V_GAP
    src_x = MARGIN
    app_x = MARGIN + BOX_W + H_GAP

    W = MARGIN * 2 + 2 * BOX_W + H_GAP
    content_h = leaves_y + max(heights["SoftwareSourceCode"], heights["SoftwareApplication"])
    H = content_h + FOOTNOTE_H + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())

    p.append(open_triangle(cw_x + BOX_W / 2, cw_y, thing_x + BOX_W / 2, thing_y + heights["Thing"], color=MUTED))
    p.append(open_triangle(src_x + BOX_W / 2, leaves_y, cw_x + BOX_W * 0.3, cw_y + heights["CreativeWork"], color=MUTED))
    p.append(open_triangle(app_x + BOX_W / 2, leaves_y, cw_x + BOX_W * 0.7, cw_y + heights["CreativeWork"], color=MUTED))

    for t, x, y in [
        ("Thing", thing_x, thing_y),
        ("CreativeWork", cw_x, cw_y),
        ("SoftwareSourceCode", src_x, leaves_y),
        ("SoftwareApplication", app_x, leaves_y),
    ]:
        total, mapped = counts[t]
        p.append(_render_box(x, y, t, fields[t], total, mapped, TYPE_COLOR[t]))

    total_all = sum(t for t, _ in counts.values())
    mapped_all = sum(m for _, m in counts.values())
    p.append(
        f'<text x="{MARGIN}" y="{content_h+38}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="400" font-size="17" fill="{MUTED}">'
        f'{mapped_all} of {total_all} CodeMeta properties map onto an existing Wikidata property; '
        f'the {total_all-mapped_all} that do not are the CodeMeta-only fields chublets-wikibase-datamodel adds.</text>'
    )

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK1_DIR)
    log: list[str] = []

    sections = crosswalk_data.load(DATA_RAW / "codemeta-wikidata-crosswalk.xlsx")
    counts = crosswalk_data.counts(sections)
    total_all = sum(t for t, _ in counts.values())
    mapped_all = sum(m for _, m in counts.values())
    log.append(f"read crosswalk: {mapped_all} of {total_all} CodeMeta properties mapped to Wikidata")

    svg_text, w, h = _build_svg(sections)
    svg_path = BLOCK1_DIR / "chublets-codemeta-wikidata-crosswalk.svg"
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
