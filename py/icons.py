"""Badge icons (S11): the clean redraws of the lock, the link, the cycle and the export arrow.

Same coordinate system as `visuals_utils.four_step_icon` / `fair4rs_icon` (centred on 0, designed for a
badge of radius 150). Icons that were fine (search, fork, triangle, check) are taken over unchanged; the
others are drawn here with round caps and filled arrow heads. All coordinates are rounded to two decimals.
"""

from __future__ import annotations

import math

import model_graphics as g
import visuals_utils as v

SW = 9


def _arrowhead(x, y, dx, dy, size, col):
    return g.arrowhead(x, y, dx, dy, size, col)


def lock_open(col):
    body = g.rect(-44, -2, 88, 62, fill=col, rx=12)
    shackle = (f'<path d="M-26,-4 L-26,-28 A26,26 0 0 1 26,-28 L26,-18" fill="none" stroke="{col}" '
               f'stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/>')
    hole = g.rect(-5, 20, 10, 24, fill="#ffffff", rx=5) + f'<circle cx="0" cy="22" r="9" fill="#ffffff"/>'
    return body + shackle + hole


def link(col):
    caps = ""
    for cx in (-26, 26):
        caps += g.rect(cx - 38, -19, 76, 38, fill="none", stroke=col, sw=SW, rx=19)
    return f'<g transform="rotate(-45)">{caps}</g>'


def cycle(col):
    r = 44
    out = ""
    for a0, a1 in ((-165, -25), (15, 155)):
        x0, y0 = r * math.cos(math.radians(a0)), r * math.sin(math.radians(a0))
        x1, y1 = r * math.cos(math.radians(a1)), r * math.sin(math.radians(a1))
        out += (f'<path d="M{g.f(x0)},{g.f(y0)} A{r},{r} 0 0 1 {g.f(x1)},{g.f(y1)}" fill="none" stroke="{col}" '
                f'stroke-width="{SW}" stroke-linecap="round"/>')
        tx, ty = -math.sin(math.radians(a1)), math.cos(math.radians(a1))
        out += _arrowhead(x1 + tx * 22, y1 + ty * 22, tx, ty, 34, col)
    return out


def export(col):
    out = (f'<path d="M-6,-48 L-48,-48 L-48,48 L-6,48" fill="none" stroke="{col}" stroke-width="{SW}" '
           f'stroke-linecap="round" stroke-linejoin="round"/>')
    out += f'<path d="M-22,0 L30,0" stroke="{col}" stroke-width="{SW}" stroke-linecap="round"/>'
    out += _arrowhead(62, 0, 1, 0, 38, col)
    return out


_NEW = {("fair", 1): lock_open, ("fair", 2): link, ("fair", 3): cycle, ("step", 3): export}


def step_icon(idx, col):
    fn = _NEW.get(("step", idx))
    return fn(col) if fn else v.four_step_icon(idx, col)


def fair_icon(idx, col):
    fn = _NEW.get(("fair", idx))
    return fn(col) if fn else v.fair4rs_icon(idx, col)
