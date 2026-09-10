"""Block 1 (2/4) -- Wikidata software-properties overview.

Companion piece to chublets-codemeta-overview: same visual language, same
box vocabulary, but Wikidata has no type hierarchy to draw (WikiProject
Informatics/Software/Properties is a flat property list), so this is five
category boxes side by side rather than a class tree. Categories and
membership are an editorial grouping (not sourced from the WikiProject
page itself, which lists properties in publication order); the property
set itself is manually transcribed from
Wikidata_WikiProject_Informatics_Software_Properties-Wikidata.pdf into
data/raw/wikidata-software-properties.csv, geprueft 2026-09-10 -- the PDF
has no machine-readable table export, so re-scraping it on every build
would be fragile for no benefit; the CSV is the versioned source of
record instead (PRIMER.md A3).

Produces:
  img/chublets-wikidata-properties-overview.svg / .png (transparent)

Runnable standalone: `python py/step_wikidata_properties_overview.py`
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
    CATEGORY_COLORS,
    ensure_dirs,
    esc,
    font_face_css,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)

BOX_W = 400
FIELD_H = 26
HEADER_H = 48
PAD_V = 16
H_GAP = 36
MARGIN = 60

OVERSAMPLE = 1.7

CATEGORY_ORDER = [
    "Identity & people",
    "Technical",
    "Relations",
    "Links & registries",
    "Versioning & rights",
]


def _load(csv_path: Path) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {c: [] for c in CATEGORY_ORDER}
    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[row["category"]].append((row["label"], row["pid"]))
    return out


def _box_height(n: int) -> float:
    return HEADER_H + n * FIELD_H + 2 * PAD_V


def _render_box(x: float, y: float, title: str, rows: list[tuple[str, str]], color: str) -> str:
    h = _box_height(len(rows))
    fill = tint(color, 0.9)
    out = f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{h}" rx="6" fill="{fill}" stroke="{color}" stroke-width="3"/>'
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+30}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="21" fill="{INK}">{esc(title)}</text>'
    )
    out += f'<line x1="{x}" y1="{y+HEADER_H}" x2="{x+BOX_W}" y2="{y+HEADER_H}" stroke="{color}" stroke-width="2.5"/>'
    fy = y + HEADER_H + 20
    for label, pid in rows:
        out += (
            f'<text x="{x+14}" y="{fy}" text-anchor="start" font-family="Fira Sans" '
            f'font-weight="400" font-size="15.5" fill="{INK}">+ {esc(label)}</text>'
        )
        if pid and pid != "-":
            out += (
                f'<text x="{x+BOX_W-14}" y="{fy}" text-anchor="end" font-family="Fira Sans" '
                f'font-weight="400" font-size="14" fill="{MUTED}">{esc(pid)}</text>'
            )
        fy += FIELD_H
    return out


def _build_svg(data: dict[str, list[tuple[str, str]]]) -> tuple[str, float, float]:
    n = len(CATEGORY_ORDER)
    W = MARGIN * 2 + n * BOX_W + (n - 1) * H_GAP
    top = MARGIN + 30  # room for the "Wikidata Software Properties" caption above the row
    tallest = max(_box_height(len(data[c])) for c in CATEGORY_ORDER)
    H = top + tallest + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append(
        f'<text x="{MARGIN}" y="{MARGIN}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="24" fill="{INK}">Wikidata: WikiProject Informatics/Software/Properties</text>'
    )
    for i, cat in enumerate(CATEGORY_ORDER):
        x = MARGIN + i * (BOX_W + H_GAP)
        p.append(_render_box(x, top, cat, data[cat], CATEGORY_COLORS[i]))
    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs()
    log: list[str] = []

    data = _load(DATA_RAW / "wikidata-software-properties.csv")
    total = sum(len(v) for v in data.values())
    log.append(f"read {total} Wikidata properties across {len(data)} categories from CSV")

    svg_text, w, h = _build_svg(data)
    svg_path = IMG_DIR / "chublets-wikidata-properties-overview.svg"
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
