"""S10 -- the topics of the properties of the chublets Wikibase.

One row per topic (data/topics.yaml, approved 2026-10-24): its name and what it
covers, a bar with one segment per property coloured by origin in the CodeMeta-
Wikidata crosswalk, the number of properties, and a few example properties.

Style: house palette for the origin colours (same as property-origin). Rows are
ordered by size, ties by name; the examples are the first properties of the topic
by identifier, so the graphic is the same on every run.

Reads: py/model_data.py, py/topics.py. Produces: img/property-topics.svg / .png

Runnable standalone: `python py/step_property_topics.py`
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
import topics as topics_mod  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "property-topics"

ORIGINS = [
    ("crosswalked", "crosswalked (CodeMeta and Wikidata)"),
    ("codemeta-only", "CodeMeta only"),
    ("wikidata-only", "Wikidata only"),
    ("chublets-addition", "chublets addition"),
    ("", "unclassified (built-in, later added)"),
]

UNIT = 15          # px per property in a bar
BAR_H = 22
TOPIC_W = 300
DESC_W = 300
EXAMPLES = 4
ROW_PAD = 12


def build(M: model_data.Model, ts: list[topics_mod.Topic]) -> g.Canvas:
    cv = g.Canvas()
    rows = sorted(ts, key=lambda t: (-len(t.members), t.label))
    x_bar = 10 + TOPIC_W + 14
    max_n = max(len(t.members) for t in rows)
    x_ex = x_bar + max_n * UNIT + 52

    # legend
    x = 10
    for key, label in ORIGINS:
        n = sum(1 for p in M.props.values() if p.pack_status == key)
        txt = f"{label}: {n}"
        out = g.rect(x, 4, 16, 16, fill=g.STATUS_COLORS[key], rx=4)
        out += g.text(x + 24, 17, txt, 13.5, fill=INK)
        w = 24 + g.text_w(txt, 13.5) + 26
        cv.add(out, x, 4, x + w, 20)
        x += w
    out = g.text(x_bar, 52, "one square per property", 12.5, italic=True, fill=MUTED)
    out += g.text(x_ex, 52, "examples", 12.5, italic=True, fill=MUTED)
    cv.add(out, x_bar, 40, x_ex + 80, 54)

    y = 66
    for t in rows:
        props = [M.props[p] for p in t.members]
        name_lines = g.wrap(t.label, 15, TOPIC_W, bold=True)
        desc_lines = g.wrap(t.description, 12.5, TOPIC_W)
        left_h = len(name_lines) * 18 + len(desc_lines) * 16
        ex = ", ".join(p.label for p in props[:EXAMPLES]) + (", …" if len(props) > EXAMPLES else "")
        ex_lines = g.wrap(ex, 12.5, 430)
        row_h = max(left_h, len(ex_lines) * 16, BAR_H) + ROW_PAD
        out = ""
        ty = y + 14
        for ln in name_lines:
            out += g.text(10, ty, ln, 15, bold=True, fill=INK)
            ty += 18
        for ln in desc_lines:
            out += g.text(10, ty - 2, ln, 12.5, fill=MUTED)
            ty += 16
        # bar: one square per property, grouped by origin
        order = {k: i for i, (k, _l) in enumerate(ORIGINS)}
        bx = x_bar
        by = y + 4
        for p in sorted(props, key=lambda q: (order[q.pack_status], int(q.id[1:]))):
            out += g.rect(bx, by, UNIT - 2, BAR_H, fill=g.STATUS_COLORS[p.pack_status], rx=3)
            bx += UNIT
        out += g.text(bx + 6, by + BAR_H / 2 + 5, str(len(props)), 15, bold=True, fill=INK)
        ey = y + 17
        for ln in ex_lines:
            out += g.text(x_ex, ey, ln, 12.5, fill=INK)
            ey += 16
        cv.add(out, 10, y, x_ex + 430, y + row_h)
        y += row_h
        if t is not rows[-1]:
            cv.add(g.line([(10, y - ROW_PAD / 2), (x_ex + 430, y - ROW_PAD / 2)], stroke=tint(MUTED, 0.8), sw=1),
                   10, y - ROW_PAD / 2, x_ex + 430, y - ROW_PAD / 2)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    ts = topics_mod.load()
    problems = topics_mod.validate(ts, M)
    if problems:
        raise RuntimeError("; ".join(problems))
    facts = model_data.caption_facts(M, len(ts))
    log = [g.save(NAME, build(M, ts))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    sizes = Counter(len(t.members) for t in ts)
    log.append(f"{len(ts)} topics, {facts['n_props']} properties; largest topic {max(sizes)} properties")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
