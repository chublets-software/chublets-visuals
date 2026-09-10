"""Talk closing slide -- the eight badges as a ring around the chublets
logo. Same idea as fdox-visuals' step_talk_closing.py (S10): the closing
slide is a small knowledge graph, not a table describing one. Right
half of the ring is the four-step process (Ingest -> Model -> Curate &
Link -> Export & Publish), left half is the four FAIR4RS principles
(Reusable -> Interoperable -> Accessible -> Findable) -- two clear arcs
rather than a claimed cause/effect pairing between them, since unlike
fdox's step/purpose chain there isn't a real one-to-one mapping here.

The logo (img/source/chublets-logo.svg, the crow with the nuggets, Flo's
own upload) is embedded as a nested <svg> inline in the generated markup
-- load_logo_inner_svg() strips it down to a viewBox and inner XML, then
_build_svg() places it as <svg x=".." y=".." width=".." height=".."
viewBox="..">{inner}</svg>, so the nested viewport does the scaling and
one resvg-py render pass draws logo and badges together. First version
composited the logo onto the rendered .png with PIL instead (fdox-visuals'
paste_raster() pattern, still in visuals_utils.py for genuine raster-only
assets); that left the .png right but the .svg source with no logo at all
(Flo, 2026-09-10: "bei meinem output (und im repo nicht)") -- inline
embedding renders identically in both because there is only one render
path now.

Produces:
  img/talk/chublets-talk-closing.svg / .png (transparent, white-background slide)

Runnable standalone: `python py/step_talk_closing.py`
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_utils import (  # noqa: E402
    FAIR_PRINCIPLES,
    FOUR_STEPS,
    INK,
    ROOT,
    SOURCE_DIR,
    TALK_DIR,
    ensure_dirs,
    esc,
    fair4rs_icon,
    font_face_css,
    four_step_icon,
    load_logo_inner_svg,
    render_svg_to_png,
    tint,
    trim_transparent_border,
)

W, H = 1500, 1500
CX, CY = 750, 750
RING_R = 480
BADGE_R = 105
TAG_SIZE = 60
TAG_OFFSET = 14
# Logo footprint, sized to the *diagonal* clearance to the ring, not just
# its half-height -- the crow's feet and the scattered nuggets reach
# close to all four corners of the logo's own bounding box, and the
# nearest badges (Export & Publish at 45 deg, Reusable at 90 deg, Findable
# at 225 deg, Ingest at -90 deg) sit in those corner directions. A first
# version sized only against half-height overlapped the nuggets into
# Curate & Link's badge (Flo, 2026-09-10: "schau dass die nuggets nichts
# beruehren") -- half-diagonal is the number that actually matters here.
LOGO_W = 440
LOGO_H = round(LOGO_W * 2136 / 2016)  # the logo's own aspect ratio (viewBox 2016x2136)

OVERSAMPLE = 2.0

# (angle in degrees, icon_fn, icon_idx, item) -- clockwise from the top.
# Right half: the four-step process, in order. Left half: the FAIR
# principles, reversed, so the ring reads as one loop rather than two
# halves running opposite ways (Findable sits next to Ingest at the top
# seam, which is at least a defensible "found, then ingested" reading --
# not claimed as more than that).
_RING = [
    (-90, four_step_icon, 0, FOUR_STEPS[0]),   # Ingest
    (-45, four_step_icon, 1, FOUR_STEPS[1]),   # Model
    (0,   four_step_icon, 2, FOUR_STEPS[2]),   # Curate & Link
    (45,  four_step_icon, 3, FOUR_STEPS[3]),   # Export & Publish
    (90,  fair4rs_icon,   3, FAIR_PRINCIPLES[3]),  # Reusable
    (135, fair4rs_icon,   2, FAIR_PRINCIPLES[2]),  # Interoperable
    (180, fair4rs_icon,   1, FAIR_PRINCIPLES[1]),  # Accessible
    (225, fair4rs_icon,   0, FAIR_PRINCIPLES[0]),  # Findable
]


def _badge(cx: float, cy: float, icon_fn, icon_idx: int, item: dict) -> str:
    color = item["color"]
    fill = tint(color, 0.88)
    tag_x, tag_y = cx - BADGE_R - TAG_OFFSET, cy - BADGE_R - TAG_OFFSET
    out = f'<circle cx="{cx}" cy="{cy}" r="{BADGE_R}" fill="{fill}" stroke="{color}" stroke-width="5"/>'
    scale = BADGE_R / 150
    out += f'<g transform="translate({cx},{cy}) scale({scale:.4f})">{icon_fn(icon_idx, color)}</g>'
    out += f'<rect x="{tag_x}" y="{tag_y}" width="{TAG_SIZE}" height="{TAG_SIZE}" rx="12" fill="{color}"/>'
    out += (
        f'<text x="{tag_x + TAG_SIZE/2}" y="{tag_y + TAG_SIZE/2 + 18}" text-anchor="middle" '
        f'font-family="Fira Sans" font-weight="700" font-size="46" fill="white">{item["num"]}</text>'
    )
    title = " ".join(item["title"])
    label_y = cy + BADGE_R + 40
    out += (
        f'<text x="{cx}" y="{label_y}" text-anchor="middle" font-family="Fira Sans" '
        f'font-weight="700" font-size="27" fill="{INK}">{esc(title)}</text>'
    )
    return out


def _build_svg(logo_inner: str, logo_view_w: float, logo_view_h: float) -> str:
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    for angle, icon_fn, idx, item in _RING:
        rad = math.radians(angle)
        cx = CX + RING_R * math.cos(rad)
        cy = CY + RING_R * math.sin(rad)
        p.append(_badge(cx, cy, icon_fn, idx, item))

    logo_x, logo_y = CX - LOGO_W / 2, CY - LOGO_H / 2
    p.append(
        f'<svg x="{logo_x}" y="{logo_y}" width="{LOGO_W}" height="{LOGO_H}" '
        f'viewBox="0 0 {logo_view_w:g} {logo_view_h:g}">{logo_inner}</svg>'
    )

    p.append("</svg>")
    return "\n".join(p)


def run(strict: bool = False) -> list[str]:
    ensure_dirs(TALK_DIR)
    log: list[str] = []

    logo_inner, logo_view_w, logo_view_h = load_logo_inner_svg(SOURCE_DIR / "chublets-logo.svg")

    svg_text = _build_svg(logo_inner, logo_view_w, logo_view_h)
    svg_path = TALK_DIR / "chublets-talk-closing.svg"
    svg_path.write_text(svg_text, encoding="utf-8")
    png_path = svg_path.with_suffix(".png")
    render_svg_to_png(svg_path, png_path, int(W * OVERSAMPLE), int(H * OVERSAMPLE))

    final_w, final_h = trim_transparent_border(png_path, margin_px=10)
    log.append(
        f"wrote {svg_path.relative_to(ROOT)} + .png "
        f"({final_w}x{final_h}, transparent, <=10px border, logo embedded inline)"
    )
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
