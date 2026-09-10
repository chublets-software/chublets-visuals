"""Block 1 (4/4) -- chublets.software federated datamodel.

The concept the other three Block 1 diagrams build up to: the chublets
Wikibase does not invent its own software schema. Its property set is the
union of two sources, read live from this repo's own other two sources so
the three diagrams can never quietly disagree (A3, one source per fact):

  - the Wikidata software properties (WikiProject Informatics/Software/
    Properties), reused as-is via Wikibase federation -- count from
    data/raw/wikidata-software-properties.csv;
  - the CodeMeta properties that data/raw/codemeta-wikidata-crosswalk.xlsx
    records as NOT mapped to any Wikidata property -- these need a new
    chublets-only property, minted once and then reused.

Produces:
  img/chublets-wikibase-datamodel.svg / .png (transparent)

Runnable standalone: `python py/step_wikibase_datamodel.py`
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    DATA_RAW,
    IMG_DIR,
    INK,
    MUTED,
    CHUBLETS_PURPLE,
    CATEGORY_COLORS,
    arrow_marker,
    ensure_dirs,
    esc,
    font_face_css,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)
import crosswalk_data  # noqa: E402

W = 1500
BOX_W = 560
BOX_H = 190
TOP_Y = 70
BOTTOM_Y = 560
GAP_X = 100
MARGIN = 60

SRC_WIKIDATA_COLOR = CATEGORY_COLORS[4]  # slate blue -- "external, reused"
SRC_CODEMETA_COLOR = CATEGORY_COLORS[1]  # gold -- "CodeMeta-derived, new"

OVERSAMPLE = 1.8


def _source_box(x: float, y: float, title: str, lines: list[str], count_label: str, color: str) -> str:
    fill = tint(color, 0.9)
    out = f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="10" fill="{fill}" stroke="{color}" stroke-width="3.5"/>'
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+42}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="25" fill="{INK}">{esc(title)}</text>'
    )
    fy = y + 82
    for line in lines:
        out += (
            f'<text x="{x+BOX_W/2}" y="{fy}" text-anchor="middle" font-family="Fira Sans" '
            f'font-weight="400" font-size="18" fill="{INK}">{esc(line)}</text>'
        )
        fy += 26
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+BOX_H-22}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="22" fill="{color}">{esc(count_label)}</text>'
    )
    return out


def _build_svg(n_wikidata: int, n_codemeta_only: int) -> tuple[str, float, float]:
    left_x = MARGIN
    right_x = MARGIN + BOX_W + GAP_X
    center_x = (left_x + right_x + BOX_W) / 2

    result_w = BOX_W + GAP_X + 0  # same total footprint as the two sources combined
    result_x = left_x
    result_y = BOTTOM_Y
    result_h = 220

    H = result_y + result_h + MARGIN
    Wsvg = right_x + BOX_W + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wsvg}" height="{H}" viewBox="0 0 {Wsvg} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", MUTED))
    p.append("</defs>")

    p.append(_source_box(
        left_x, TOP_Y, "Wikidata software properties",
        ["WikiProject Informatics/", "Software/Properties", "reused via Wikibase federation"],
        f"{n_wikidata}+ properties, 0 new", SRC_WIKIDATA_COLOR,
    ))
    p.append(_source_box(
        right_x, TOP_Y, "CodeMeta-only fields",
        ["CodeMeta terms with no", "matching Wikidata property", "(see chublets-codemeta-wikidata-crosswalk)"],
        f"{n_codemeta_only} new chublets properties", SRC_CODEMETA_COLOR,
    ))

    # two converging connectors into the result box
    p.append(f'<line x1="{left_x+BOX_W/2}" y1="{TOP_Y+BOX_H}" x2="{center_x-10}" y2="{result_y}" '
              f'stroke="{MUTED}" stroke-width="3.5" marker-end="url(#arrow)"/>')
    p.append(f'<line x1="{right_x+BOX_W/2}" y1="{TOP_Y+BOX_H}" x2="{center_x+10}" y2="{result_y}" '
              f'stroke="{MUTED}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    fill = tint(CHUBLETS_PURPLE, 0.88)
    p.append(f'<rect x="{result_x}" y="{result_y}" width="{right_x+BOX_W-result_x}" height="{result_h}" '
              f'rx="12" fill="{fill}" stroke="{CHUBLETS_PURPLE}" stroke-width="4"/>')
    p.append(
        f'<text x="{Wsvg/2}" y="{result_y+50}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="30" fill="{INK}">chublets.software Wikibase datamodel</text>'
    )
    for i, line in enumerate([
        f"{n_wikidata}+ Wikidata properties, reused as-is",
        f"+ {n_codemeta_only} chublets-only properties for the CodeMeta-only fields",
        "= one federated schema, not a schema invented from scratch",
    ]):
        p.append(
            f'<text x="{Wsvg/2}" y="{result_y+95+i*32}" text-anchor="middle" font-family="Fira Sans" '
            f'font-weight="400" font-size="19" fill="{INK}">{esc(line)}</text>'
        )

    p.append("</svg>")
    return "\n".join(p), Wsvg, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs()
    log: list[str] = []

    with open(DATA_RAW / "wikidata-software-properties.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    n_wikidata = sum(1 for r in rows if r["pid"] != "-")
    log.append(f"read {n_wikidata} named Wikidata properties from CSV (plus an unitemised dozen registry IDs)")

    sections = crosswalk_data.load(DATA_RAW / "codemeta-wikidata-crosswalk.xlsx")
    counts = crosswalk_data.counts(sections)
    total_all = sum(t for t, _ in counts.values())
    mapped_all = sum(m for _, m in counts.values())
    n_codemeta_only = total_all - mapped_all
    log.append(f"read crosswalk: {n_codemeta_only} of {total_all} CodeMeta properties are unmapped (CodeMeta-only)")

    svg_text, w, h = _build_svg(n_wikidata, n_codemeta_only)
    svg_path = IMG_DIR / "chublets-wikibase-datamodel.svg"
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
