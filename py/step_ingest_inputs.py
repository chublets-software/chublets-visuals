"""S4b (1/4) -- Ingest: the three input sources.

Detail diagram behind the "Ingest" badge from S4. Same composition as
chublets-wikibase-datamodel (S2's converging-sources pattern), now for the
three ways data actually enters the chublets Wikibase rather than for the
two halves of its property set.

Content confirmed 2026-09-10 (Talk-Chat, "Input von Wikidata Items, FDOx
aus der registry, und Git Repos ueber CFF"); not yet grounded in a
data/raw source the way S2 is (PRIMER.md Teil D) -- these are the three
source *kinds*, not counted instances, so there is nothing to parse yet.

Produces:
  img/block-3-four-step-pattern/step-1-ingest-detail.svg / .png (transparent)

Runnable standalone: `python py/step_ingest_inputs.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    BLOCK3_DIR,
    FOUR_STEPS,
    INK,
    MUTED,
    ROOT,
    arrow_marker,
    ensure_dirs,
    esc,
    font_face_css,
    render_svg_to_png,
    step_header,
    tint,
    trim_transparent_border,
)

STEP_IDX = 0
STEP = FOUR_STEPS[STEP_IDX]
ACCENT = STEP["color"]  # teal -- same as the Ingest badge

BOX_W = 380
BOX_H = 180
GAP_X = 60
MARGIN = 60
GAP_HEADER_TO_SOURCES = 40
GAP_SOURCES_TO_RESULT = 90

OVERSAMPLE = 1.8


def _source_box(x: float, y: float, title: str, lines: list[str], color: str) -> str:
    fill = tint(color, 0.9)
    out = f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="10" fill="{fill}" stroke="{color}" stroke-width="3.5"/>'
    out += (
        f'<text x="{x+BOX_W/2}" y="{y+42}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="23" fill="{INK}">{esc(title)}</text>'
    )
    fy = y + 80
    for line in lines:
        out += (
            f'<text x="{x+BOX_W/2}" y="{fy}" text-anchor="middle" font-family="Fira Sans" '
            f'font-weight="400" font-size="16.5" fill="{INK}">{esc(line)}</text>'
        )
        fy += 24
    return out


def _build_svg() -> tuple[str, float, float]:
    header_svg, top_y = step_header(STEP_IDX, STEP, MARGIN, MARGIN)
    top_y += GAP_HEADER_TO_SOURCES
    result_y = top_y + BOX_H + GAP_SOURCES_TO_RESULT

    n = 3
    total_w = n * BOX_W + (n - 1) * GAP_X
    xs = [MARGIN + i * (BOX_W + GAP_X) for i in range(n)]
    center_x = MARGIN + total_w / 2

    result_w = total_w
    result_h = 150
    result_x = MARGIN

    W = MARGIN * 2 + total_w
    H = result_y + result_h + MARGIN

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", MUTED))
    p.append("</defs>")
    p.append(header_svg)

    sources = [
        ("Wikidata items", ["chublets bridge items from the", "open-archaeo \u2192 Wikidata pipeline"]),
        ("FDOx objects", ["CITATION.cff + codemeta.json via", "the FDOx-squirrel registry"]),
        ("Git repos via CFF", ["Direct CITATION.cff harvest,", "no Wikidata/FDOx wrapper yet"]),
    ]
    for x, (title, lines) in zip(xs, sources):
        p.append(_source_box(x, top_y, title, lines, ACCENT))
        p.append(f'<line x1="{x+BOX_W/2}" y1="{top_y+BOX_H}" x2="{center_x:.1f}" y2="{result_y}" '
                  f'stroke="{MUTED}" stroke-width="3.5" marker-end="url(#arrow)"/>')

    fill = tint(ACCENT, 0.88)
    p.append(f'<rect x="{result_x}" y="{result_y}" width="{result_w}" height="{result_h}" '
              f'rx="12" fill="{fill}" stroke="{ACCENT}" stroke-width="4"/>')
    p.append(
        f'<text x="{W/2}" y="{result_y+55}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="27" fill="{INK}">chublets.software Wikibase</text>'
    )
    p.append(
        f'<text x="{W/2}" y="{result_y+95}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="400" font-size="18" fill="{MUTED}">three independent entry points, one target schema</text>'
    )
    p.append(
        f'<text x="{W/2}" y="{result_y+122}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="400" font-size="18" fill="{MUTED}">(see chublets-wikibase-datamodel)</text>'
    )

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK3_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = BLOCK3_DIR / "step-1-ingest-detail.svg"
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
