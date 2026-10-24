"""Shared helpers for the architecture and open-archaeo graphics (S11): rows of boxes joined by arrows."""

from __future__ import annotations

import four_steps as fs
import model_graphics as g
from visuals_utils import INK, MUTED


def box_height(w, title, lines, size=15.5):
    return fs._box(0, 0, w, title, lines, "#000000", size=size)[1]


def row(cv, x, y, items, bw, gap, col, h=None, fills=None, arrows=True, size=15.5):
    """Boxes side by side with equal height. items: (title, lines[, colour]). Returns (height, centres)."""
    h = h or max(box_height(bw, t, ls, size) for t, ls, *_ in items)
    centres = []
    for i, it in enumerate(items):
        t, ls = it[0], it[1]
        c = it[2] if len(it) > 2 else col
        bx = x + i * (bw + gap)
        svg, _ = fs._box(bx, y, bw, t, ls, c, fill=(fills[i] if fills else 0.9), size=size, min_h=h)
        cv.add(svg, bx, y, bx + bw, y + h)
        centres.append(bx + bw / 2)
        if arrows and i < len(items) - 1:
            a = fs._arrow(bx + bw + 3, y + h / 2, bx + bw + gap - 3, y + h / 2, MUTED if len(it) > 2 else c, sw=3.5)
            cv.add(a, bx + bw, y + h / 2 - 8, bx + bw + gap, y + h / 2 + 8)
    return h, centres


def note(cv, x, y, text, width, size=14.5):
    ys = y
    for ln in g.wrap(text, size, width):
        cv.add(g.text(x, ys + size, ln, size, fill=MUTED, italic=True), x, ys, x + width, ys + size + 4)
        ys += size + 6
    return ys - y
