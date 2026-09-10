"""S6 -- the open-archaeo -> Wikidata import pipeline.

The detail behind chublets-software-architecture's (S5) "Wikidata bridge"
stage, which is deliberately neutral-grey there and says "see S6" --
this is that S6. Unlike Block 2's FAIR mechanisms or S4b's Curate/Export
content, this pipeline is not a talk-chat sketch: every stage names a real,
already-built and exercised part of the open-archaeo -> Wikidata Python
pipeline (own conversation history, not this repo -- see PRIMER.md A1
Befund 9). It is written here as a curated description rather than parsed
from the pipeline's own source, because that source is not part of this
repository (Teil D, was an open question in S6's placeholder entry;
resolved by treating it the same way as chublets-wikidata-properties-
overview treats the WikiProject page: a maintained CSV of record, not a
live parse of an external repo this one doesn't contain).

Produces:
  img/system-architecture/open-archaeo-wikidata-pipeline.svg / .png (transparent)

Runnable standalone: `python py/step_open_archaeo_pipeline.py`
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

ACCENT = CATEGORY_COLORS[5]  # neutral grey -- same as S5's "Wikidata bridge" stage

BOX_W = 280
BOX_H = 150
GAP_X = 60
MARGIN = 60
TITLE_H = 60

OVERSAMPLE = 1.8

STAGES = [
    ("open-archaeo CSV", "Community register on GitHub"),
    ("Transform + identity", "Slug logic, six statements (P31/P6104/P361/P195+q/P217/P2888)"),
    ("GitHub enrichment", "Licence, dates, topics, language -- ETag-cached"),
    ("Category reconciliation", "suggest / verify / apply"),
    ("Push to Wikidata", "create or skip-blocked items"),
]


def _wrap(text: str, max_chars: int) -> list[str]:
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _build_svg() -> tuple[str, float, float]:
    n = len(STAGES)
    total_w = n * BOX_W + (n - 1) * GAP_X
    W = MARGIN * 2 + total_w
    top_y = MARGIN + TITLE_H
    H = top_y + BOX_H + MARGIN + 40

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", ACCENT))
    p.append("</defs>")

    p.append(
        f'<text x="{MARGIN}" y="{MARGIN+10}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="28" fill="{INK}">open-archaeo \u2192 Wikidata pipeline</text>'
    )

    fill = tint(ACCENT, 0.92)
    for i, (title, sub) in enumerate(STAGES):
        x = MARGIN + i * (BOX_W + GAP_X)
        lines = [(title, 700, 19)]
        sub_lines = _wrap(sub, 30)
        lines += [(s, 400, 14) for s in sub_lines]
        p.append(label_box(x, top_y, BOX_W, BOX_H, lines, fill=fill, stroke=ACCENT, text_color=INK))
        if i < n - 1:
            x2 = x + BOX_W
            y = top_y + BOX_H / 2
            p.append(f'<line x1="{x2}" y1="{y}" x2="{x2+GAP_X-6}" y2="{y}" '
                      f'stroke="{ACCENT}" stroke-width="4" marker-end="url(#arrow)"/>')

    p.append(
        f'<text x="{MARGIN}" y="{top_y+BOX_H+34}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="400" font-size="15" fill="{MUTED}">Output: Wikidata items carrying the identity block '
        f'-- the "Wikidata items" input to chublets-ingest-inputs.</text>'
    )

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(SYSTEM_ARCH_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = SYSTEM_ARCH_DIR / "open-archaeo-wikidata-pipeline.svg"
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
