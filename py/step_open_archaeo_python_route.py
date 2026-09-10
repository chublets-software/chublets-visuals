"""S6b (2/3) -- the Python route, in session order.

Grounded in py/wikidata/main.py's actual STEPS/ALL_STEPS lists and the
practical session documented in out/Python/README.md ("The session"),
not the original S6 diagram's memory-based "GitHub enrichment" framing
(PRIMER.md A1 Befund 10). `check` is genuinely the default step -- running
the CLI with no arguments runs it -- and `push --live` is the only step
that writes to Wikidata at all; everything else, including the plain
`push` (a dry run), is read-only.

Produces:
  img/system-architecture/open-archaeo-python-route.svg / .png (transparent)

Runnable standalone: `python py/step_open_archaeo_python_route.py`
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

ACCENT = CATEGORY_COLORS[0]  # purple -- matches "Python slice" in the two-routes diagram

BOX_W = 250
BOX_H = 160
GAP_X = 50
MARGIN = 60
TITLE_H = 60

OVERSAMPLE = 1.8

STAGES = [
    ("check", "default step", "Verifies Q-ids, datatypes, no duplicate claims -- writes nothing"),
    ("preview", "docs/preview.html", "Every item's statements, blocked / deferred / note"),
    ("reconcile", "read-only, slow", "What Wikidata already has -- by repository URL, DOI, CRAN, PyPI"),
    ("push", "dry run by default", "Text report of what would be written"),
    ("push --live", "the only write", "Only rows reconcile matched to a Q-id -- never creates items"),
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
    H = top_y + BOX_H + MARGIN + 44

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", ACCENT))
    p.append("</defs>")

    p.append(
        f'<text x="{MARGIN}" y="{MARGIN+10}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="28" fill="{INK}">The Python route (py/wikidata/main.py)</text>'
    )

    fill = tint(ACCENT, 0.92)
    for i, (title, tag, desc) in enumerate(STAGES):
        x = MARGIN + i * (BOX_W + GAP_X)
        lines = [(title, 700, 20), (tag, 400, 13.5)] + [(s, 400, 13) for s in _wrap(desc, 27)]
        p.append(label_box(x, top_y, BOX_W, BOX_H, lines, fill=fill, stroke=ACCENT, text_color=INK))
        if i < n - 1:
            x2 = x + BOX_W
            y = top_y + BOX_H / 2
            p.append(f'<line x1="{x2}" y1="{y}" x2="{x2+GAP_X-6}" y2="{y}" '
                      f'stroke="{ACCENT}" stroke-width="4" marker-end="url(#arrow)"/>')

    p.append(
        f'<text x="{MARGIN}" y="{top_y+BOX_H+34}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="400" font-size="15" fill="{MUTED}">Also available: vocab, categories, subjects -- '
        f'worksheet builders that feed the shared vocabulary, not part of this session.</text>'
    )

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(SYSTEM_ARCH_DIR)
    log: list[str] = []

    svg_text, w, h = _build_svg()
    svg_path = SYSTEM_ARCH_DIR / "open-archaeo-python-route.svg"
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
