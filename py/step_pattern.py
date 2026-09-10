"""S4 -- chublets.software four-step documentation pattern.

Analogous to fdox-visuals' step_pattern.py (same badge/banner geometry,
same render pipeline), own icon set and colours: Ingest -> Model ->
Curate & Link -> Export & Publish (confirmed 2026-09-10, PRIMER.md A4).

Produces:
  img/chublets-four-step-pattern.svg / .png   content-only banner, transparent
  img/chublets-step-<n>-<slug>.svg / .png     one badge per step, transparent

Runnable standalone: `python py/step_pattern.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    FOUR_STEPS,
    BLOCK3_DIR,
    ROOT,
    INK,
    MUTED,
    ensure_dirs,
    esc,
    font_face_css,
    four_step_icon,
    render_svg_to_png,
    tint,
    trim_transparent_border,
    wrap_text,
)

BADGE_R = 150
TAG_SIZE = 132
TAG_OFFSET = 26

W = 3840
MARGIN_X = 260
COL_W = (W - 2 * MARGIN_X) / 4
CENTERS = [MARGIN_X + COL_W * (i + 0.5) for i in range(4)]

TOP_MARGIN = 130
BADGE_CY = TOP_MARGIN + BADGE_R + TAG_OFFSET
TITLE_Y0 = BADGE_CY + BADGE_R + 150
DESC_Y0 = TITLE_Y0 + 80 * 2 + 46
BOTTOM_MARGIN = 130

# See fdox-visuals/py/step_pattern.py's OVERSAMPLE comment: kept modest so
# the trimmed content's *content* area stays well under Google Slides'
# 25-megapixel insert limit.
OVERSAMPLE = 1.5
ICON_SCALE = 4


def _badge_markup(cx: float, cy: float, step_idx: int, step: dict) -> str:
    color = step["color"]
    tint_fill = tint(color, 0.88)
    tag_x = cx - BADGE_R - TAG_OFFSET
    tag_y = cy - BADGE_R - TAG_OFFSET
    out = f'<circle cx="{cx}" cy="{cy}" r="{BADGE_R}" fill="{tint_fill}" stroke="{color}" stroke-width="7"/>'
    out += f'<g transform="translate({cx},{cy})">{four_step_icon(step_idx, color)}</g>'
    out += f'<rect x="{tag_x}" y="{tag_y}" width="{TAG_SIZE}" height="{TAG_SIZE}" rx="26" fill="{color}"/>'
    out += (
        f'<text x="{tag_x + TAG_SIZE/2}" y="{tag_y + TAG_SIZE/2 + 40}" text-anchor="middle" '
        f'font-family="Fira Sans" font-weight="700" font-size="104" fill="white">{step["num"]}</text>'
    )
    return out


def _title_tspans(cx: float, y0: float, lines: list[str]) -> str:
    return "".join(
        f'<text x="{cx}" y="{y0 + i*80}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="60" fill="{INK}">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )


def _build_content_svg(desc_lines_per_step: list[list[str]]) -> tuple[str, int]:
    max_desc_lines = max(len(x) for x in desc_lines_per_step)
    content_bottom = DESC_Y0 + (max_desc_lines - 1) * 54 + 34
    h = int(content_bottom + BOTTOM_MARGIN)

    x_first, x_last = CENTERS[0] + BADGE_R + 10, CENTERS[-1] - BADGE_R - 10
    grad_stops = "".join(
        f'<stop offset="{i/3*100:.0f}%" stop-color="{s["color"]}"/>' for i, s in enumerate(FOUR_STEPS)
    )

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(
        f'<linearGradient id="flow" gradientUnits="userSpaceOnUse" '
        f'x1="{x_first}" y1="{BADGE_CY}" x2="{x_last}" y2="{BADGE_CY}">{grad_stops}</linearGradient>'
    )
    p.append("</defs>")
    p.append(
        f'<line x1="{x_first}" y1="{BADGE_CY}" x2="{x_last}" y2="{BADGE_CY}" '
        f'stroke="url(#flow)" stroke-width="10" stroke-linecap="round"/>'
    )
    for i in range(3):
        mx = (CENTERS[i] + CENTERS[i + 1]) / 2
        p.append(
            f'<path d="M {mx-26},{BADGE_CY-22} L {mx+26},{BADGE_CY} L {mx-26},{BADGE_CY+22}" '
            f'fill="none" stroke="white" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>'
        )
    for i, (cx, step) in enumerate(zip(CENTERS, FOUR_STEPS)):
        p.append(_badge_markup(cx, BADGE_CY, i, step))
        p.append(_title_tspans(cx, TITLE_Y0, step["title"]))
        for j, line in enumerate(desc_lines_per_step[i]):
            p.append(
                f'<text x="{cx}" y="{DESC_Y0 + j*54}" text-anchor="middle" font-family="Fira Sans" '
                f'font-weight="400" font-size="38" fill="{MUTED}">{esc(line)}</text>'
            )
    p.append("</svg>")
    return "\n".join(p), h


def _build_icon_svg(step_idx: int, step: dict) -> tuple[str, int]:
    pad = 15
    left = -(BADGE_R + TAG_OFFSET) - pad
    top = -(BADGE_R + TAG_OFFSET) - pad
    right = BADGE_R + pad
    bottom = BADGE_R + pad
    vb_w, vb_h = right - left, bottom - top
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w}" height="{vb_h}" '
        f'viewBox="{left} {top} {vb_w} {vb_h}">'
    ]
    p.append(font_face_css())
    p.append(_badge_markup(0, 0, step_idx, step))
    p.append("</svg>")
    return "\n".join(p), vb_w


def run(strict: bool = False) -> list[str]:
    ensure_dirs(BLOCK3_DIR)
    log: list[str] = []
    warnings: list[str] = []

    desc_lines_per_step = [wrap_text(s["desc"], max_chars=30) for s in FOUR_STEPS]
    for s, lines in zip(FOUR_STEPS, desc_lines_per_step):
        if len(lines) > 3:
            warnings.append(f'description for "{s["id"]}" wraps to {len(lines)} lines (design assumes <=3)')

    svg_text, h = _build_content_svg(desc_lines_per_step)
    svg_path = BLOCK3_DIR / "chublets-four-step-pattern.svg"
    svg_path.write_text(svg_text, encoding="utf-8")
    png_path = svg_path.with_suffix(".png")
    render_svg_to_png(svg_path, png_path, int(W * OVERSAMPLE), int(h * OVERSAMPLE))
    final_w, final_h = trim_transparent_border(png_path, margin_px=10)
    log.append(
        f"wrote {svg_path.relative_to(ROOT)} + .png "
        f"({final_w}x{final_h}, transparent, <=10px border)"
    )

    for i, step in enumerate(FOUR_STEPS):
        svg_text, vb = _build_icon_svg(i, step)
        svg_path = BLOCK3_DIR / f"step-{step['num']}-{step['id']}-badge.svg"
        svg_path.write_text(svg_text, encoding="utf-8")
        png_path = svg_path.with_suffix(".png")
        render_svg_to_png(svg_path, png_path, int(vb * ICON_SCALE), int(vb * ICON_SCALE))
        final_w, final_h = trim_transparent_border(png_path, margin_px=10)
        log.append(
            f"wrote {svg_path.relative_to(ROOT)} + .png "
            f"({final_w}x{final_h}, transparent, <=10px border)"
        )

    if warnings:
        for w in warnings:
            log.append(f"WARNING: {w}")
        if strict:
            raise RuntimeError(f"{len(warnings)} warning(s) in step 'pattern' (--strict)")

    return log


if __name__ == "__main__":
    for line in run():
        print(line)
