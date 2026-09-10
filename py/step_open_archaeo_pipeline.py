"""S6 -- `python py/wikidata/main.py all`: the automated read-only build.

Rebuilt 2026-09-10 to match the real repo (Flo: "S6 auf den echten Stand
bringen, dass es konsistent ist") -- the previous version described a
six-statement identity block and a GitHub-enrichment step that do not
exist in the current pipeline (PRIMER.md A1 Befund 10). This version
parses ALL_STEPS out of a vendored snapshot of the real
py/wikidata/main.py (open_archaeo_data.py) instead of carrying the step
list as a literal here, so refreshing it when the upstream repo changes
is a file copy, not a rewrite (Flo, 2026-09-10: "damit können wir es auch
weiterfuehren, wenn sich in dem repo was tut").

Distinct from the other open-archaeo diagrams rather than a fourth
near-duplicate of them: S6b(1/3) shows the two-team split, S6b(2/3) the
interactive human session for the Python route (check -> preview ->
reconcile -> push -> push --live). This diagram shows the one thing `all`
actually runs end to end with no human in the loop and nothing written to
Wikidata -- a third, genuinely different view of the same pipeline.

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
    DATA_RAW,
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
import open_archaeo_data  # noqa: E402

ACCENT = CATEGORY_COLORS[5]  # neutral grey -- same as S5's "Wikidata bridge" stage

BOX_W = 260
BOX_H = 130
GAP_X = 40
GAP_Y = 60
MARGIN = 60
TITLE_H = 60
COLS = 4

OVERSAMPLE = 1.8


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


def _build_svg(all_steps: list[tuple[str, bool, str]]) -> tuple[str, float, float]:
    n = len(all_steps)
    rows = [all_steps[i:i + COLS] for i in range(0, n, COLS)]
    total_w = COLS * BOX_W + (COLS - 1) * GAP_X
    W = MARGIN * 2 + total_w
    top_y = MARGIN + TITLE_H
    n_rows = len(rows)
    H = top_y + n_rows * BOX_H + (n_rows - 1) * GAP_Y + MARGIN + 44

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    p.append(font_face_css())
    p.append("<defs>")
    p.append(arrow_marker("arrow", ACCENT))
    p.append("</defs>")

    p.append(
        f'<text x="{MARGIN}" y="{MARGIN+10}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="700" font-size="28" fill="{INK}">python py/wikidata/main.py all</text>'
    )

    fill = tint(ACCENT, 0.92)
    positions = {}
    for r, row in enumerate(rows):
        y = top_y + r * (BOX_H + GAP_Y)
        for c, (name, needs_conn, desc) in enumerate(row):
            x = MARGIN + c * (BOX_W + GAP_X)
            positions[(r, c)] = (x, y)
            tag = "reads Wikidata" if needs_conn else "offline"
            lines = [(name, 700, 20), (tag, 400, 13)] + [(s, 400, 13) for s in _wrap(desc, 27)]
            p.append(label_box(x, y, BOX_W, BOX_H, lines, fill=fill, stroke=ACCENT, text_color=INK))

    # arrows: left-to-right within a row, then last-of-row to first-of-next-row
    flat = [(r, c) for r in range(len(rows)) for c in range(len(rows[r]))]
    for i in range(len(flat) - 1):
        r1, c1 = flat[i]
        r2, c2 = flat[i + 1]
        x1, y1 = positions[(r1, c1)]
        x2, y2 = positions[(r2, c2)]
        if r1 == r2:
            p.append(f'<line x1="{x1+BOX_W}" y1="{y1+BOX_H/2}" x2="{x2-6}" y2="{y2+BOX_H/2}" '
                      f'stroke="{ACCENT}" stroke-width="4" marker-end="url(#arrow)"/>')
        else:
            midy = y1 + BOX_H + GAP_Y / 2
            p.append(f'<path d="M {x1+BOX_W/2},{y1+BOX_H} L {x1+BOX_W/2},{midy} '
                      f'L {x2+BOX_W/2},{midy} L {x2+BOX_W/2},{y2-6}" fill="none" '
                      f'stroke="{ACCENT}" stroke-width="4" marker-end="url(#arrow)"/>')

    footnote_y = top_y + n_rows * BOX_H + (n_rows - 1) * GAP_Y + 34
    p.append(
        f'<text x="{MARGIN}" y="{footnote_y}" text-anchor="start" font-family="Fira Sans" '
        f'font-weight="400" font-size="15" fill="{MUTED}">Deliberately left out of `all`: reconcile '
        f'(slow -- add with --reconcile) and push (writes -- a decision, not automation). See '
        f'open-archaeo-python-route.</text>'
    )

    p.append("</svg>")
    return "\n".join(p), W, H


def run(strict: bool = False) -> list[str]:
    ensure_dirs(SYSTEM_ARCH_DIR)
    log: list[str] = []

    data = open_archaeo_data.load(DATA_RAW / "open-archaeo" / "wikidata-main.py")
    all_steps = data["all_steps"]
    log.append(f"read ALL_STEPS from vendored py/wikidata/main.py: {len(all_steps)} steps")

    svg_text, w, h = _build_svg(all_steps)
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
