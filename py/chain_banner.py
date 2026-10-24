"""The chain banner (S11): four badges on a gradient line with title and one line of text each.

Used for the four steps (`chublets-four-step-pattern`) and the four FAIR principles
(`chublets-fair4rs-chain`). The badge icons are the ones of `visuals_utils`.
"""

from __future__ import annotations

import re

import icons
import model_graphics as g
from visuals_utils import INK, MUTED, tint

BR = 74        # badge radius
TAG = 40       # number tag size
TAGO = 13      # tag offset
COL_W = 360
TEXT_W = COL_W - 40
ICON_K = 1.3   # the icons fill the badge (they were small in the circle)
# Offsets (icon units) that centre each icon in its circle; measured from the rendered icons.
CENTRE = {"step_icon": [(0, 16.5), (0, 10), (-4, 3), (0, 0)],
          "fair_icon": [(-3.5, -3.5), (0, 0), (0, 0), (0, 0)]}


def _icon(icon_fn, idx, col, cx=0.0, cy=0.0, r=BR):
    k = r / 150 * ICON_K
    dx, dy = CENTRE[icon_fn.__name__][idx]
    return f'<g transform="translate({g.f(cx + dx * k)},{g.f(cy + dy * k)}) scale({k:.4f})">{icon_fn(idx, col)}</g>'


def _round(svg: str) -> str:
    return re.sub(r"-?\d+\.\d{3,}", lambda m: g.f(float(m.group(0))), svg)


def build(items, icon_fn, descs, uid):
    """items: dicts with num, title, color (visuals_utils.FOUR_STEPS / FAIR_PRINCIPLES); descs: one text each."""
    cv = g.Canvas()
    n = len(items)
    cy = TAG + TAGO
    centres = [COL_W * (i + 0.5) for i in range(n)]
    x0, x1 = centres[0] + BR + 6, centres[-1] - BR - 6
    stops = "".join(f'<stop offset="{i / (n - 1) * 100:.0f}%" stop-color="{it["color"]}"/>' for i, it in enumerate(items))
    out = (f'<defs><linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="{g.f(x0)}" y1="{g.f(cy)}" '
           f'x2="{g.f(x1)}" y2="{g.f(cy)}">{stops}</linearGradient></defs>')
    out += f'<path d="M{g.f(x0)},{g.f(cy)} L{g.f(x1)},{g.f(cy)}" stroke="url(#{uid})" stroke-width="6" stroke-linecap="round" fill="none"/>'
    for i in range(n - 1):
        mx = (centres[i] + centres[i + 1]) / 2
        out += (f'<path d="M{g.f(mx - 13)},{g.f(cy - 11)} L{g.f(mx + 13)},{g.f(cy)} L{g.f(mx - 13)},{g.f(cy + 11)}" '
                f'fill="none" stroke="#ffffff" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
    bottom = cy
    for i, (it, d, cx) in enumerate(zip(items, descs, centres)):
        col = it["color"]
        out += f'<circle cx="{g.f(cx)}" cy="{g.f(cy)}" r="{BR}" fill="{tint(col, 0.88)}" stroke="{col}" stroke-width="4"/>'
        out += _icon(icon_fn, i, col, cx, cy)
        tx, ty = cx - BR - TAGO, cy - BR - TAGO
        out += g.rect(tx, ty, TAG, TAG, fill=col, rx=9)
        out += g.text(tx + TAG / 2, ty + TAG / 2 + 10, it["num"], 30, bold=True, fill="#ffffff", anchor="middle")
        ty0 = cy + BR + 44
        out += g.text(cx, ty0, " ".join(it["title"]), 27, bold=True, fill=INK, anchor="middle")
        yy = ty0 + 30
        for ln in g.wrap(d, 17, TEXT_W):
            out += g.text(cx, yy, ln, 17, fill=MUTED, anchor="middle")
            yy += 24
        bottom = max(bottom, yy)
    cv.add(_round(out), 0, cy - BR - TAGO - 3, n * COL_W, bottom)
    return cv


def badge(item, icon_fn, idx):
    """One badge alone (icon, number tag), for slide corners and navigation."""
    cv = g.Canvas()
    col = item["color"]
    out = f'<circle cx="0" cy="0" r="{BR}" fill="{tint(col, 0.88)}" stroke="{col}" stroke-width="4"/>'
    out += _icon(icon_fn, idx, col)
    tx, ty = -BR - TAGO, -BR - TAGO
    out += g.rect(tx, ty, TAG, TAG, fill=col, rx=9)
    out += g.text(tx + TAG / 2, ty + TAG / 2 + 10, item["num"], 30, bold=True, fill="#ffffff", anchor="middle")
    cv.add(_round(out), tx - 2, ty - 2, BR + 2, BR + 2)
    return cv
