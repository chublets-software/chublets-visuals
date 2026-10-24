"""S10 -- how the property vocabularies overlap.

One bar of all properties, ordered so that the properties with an equivalent
Wikidata property (P4) form one continuous stretch and the properties with a
CodeMeta term form another; the two stretches overlap in the crosswalked
properties. Brackets above and below the bar give the size of each vocabulary.

Style: house palette for the origin colours (as in property-origin); no model
elements are drawn, so the semantic scheme is not used.

Reads: py/model_data.py. Produces: img/property-vocabulary-overlap.svg / .png

Runnable standalone: `python py/step_property_vocabulary_overlap.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "property-vocabulary-overlap"
W = 1000.0
BAR_Y, BAR_H = 70, 58
SC = g.STATUS_COLORS


def _segments(M: model_data.Model):
    """(key, legend text, colour, outline dash, properties) in bar order."""
    P = list(M.props.values())

    def sel(status, twin, cm):
        return [p for p in P if p.pack_status == status and bool(p.twin) == twin and bool(p.codemeta_terms) == cm]

    segs = [
        ("wd", "Wikidata property only", SC["wikidata-only"], None, sel("wikidata-only", True, False)),
        ("add", "chublets addition that has a Wikidata property", SC["chublets-addition"], None, sel("chublets-addition", True, False)),
        ("unc", "built-in or later added, with a Wikidata property", SC[""], None, sel("", True, False)),
        ("both", "in both vocabularies (crosswalked)", SC["crosswalked"], None, sel("crosswalked", True, True)),
        ("cm", "CodeMeta term only", SC["codemeta-only"], None, sel("codemeta-only", False, True)),
        ("none", "in neither vocabulary (chublets additions and built-in properties)", "#ffffff", "5 3",
         [p for p in P if not p.twin and not p.codemeta_terms]),
    ]
    assert sum(len(s[4]) for s in segs) == len(P), "the six groups must partition the properties"
    return segs


def _bracket(cv, x1, x2, y, up, label, col):
    d = -1 if up else 1
    out = g.line([(x1, y - d * 9), (x1, y), (x2, y), (x2, y - d * 9)], col, sw=2)
    ty = y + d * 24 - (0 if up else -2) if not up else y - 12
    out += g.text((x1 + x2) / 2, ty if up else y + 26, label, 15, bold=True, fill=col, anchor="middle")
    cv.add(out, x1, y - 30 if up else y - 9, x2, y + (9 if up else 34))


def build(M: model_data.Model) -> g.Canvas:
    segs = _segments(M)
    total = len(M.props)
    unit = W / total
    cv = g.Canvas()
    x = 0.0
    edges = []
    for key, text_, col, dash, ps in segs:
        w = len(ps) * unit
        edges.append((key, x, x + w))
        out = g.rect(x, BAR_Y, w - 3, BAR_H, fill=col, stroke=MUTED if dash else "none", sw=1.6, rx=6, dash=dash)
        out += g.text(x + (w - 3) / 2, BAR_Y + BAR_H / 2 + 8, str(len(ps)), 22, bold=True,
                      fill=INK if dash else "#ffffff", anchor="middle")
        cv.add(out, x, BAR_Y, x + w, BAR_Y + BAR_H)
        x += w
    e = {k: (a, b) for k, a, b in edges}
    n_wd = sum(len(s[4]) for s in segs[:4])
    n_cm = sum(len(s[4]) for s in segs[3:5])
    n_both = len(segs[3][4])
    assert n_wd == sum(1 for p in M.props.values() if p.twin) and n_cm == sum(1 for p in M.props.values() if p.codemeta_terms)
    _bracket(cv, e["wd"][0], e["both"][1] - 3, BAR_Y - 14, True,
             f"equivalent Wikidata property (P4): {n_wd}", SC["wikidata-only"])
    _bracket(cv, e["both"][0], e["cm"][1] - 3, BAR_Y + BAR_H + 14, False,
             f"equivalent CodeMeta term: {n_cm}", SC["codemeta-only"])
    mid = (e["both"][0] + e["both"][1]) / 2
    cv.add(g.text(mid, BAR_Y + BAR_H + 66, f"{n_both} in both", 14, bold=True, fill=SC["crosswalked"], anchor="middle"),
           mid - 50, BAR_Y + BAR_H + 50, mid + 50, BAR_Y + BAR_H + 72)
    # legend
    y = BAR_Y + BAR_H + 100
    col_w = W / 2
    for i, (key, text_, col, dash, ps) in enumerate(segs):
        cx = (i % 2) * col_w
        cy = y + (i // 2) * 34
        out = g.rect(cx, cy, 34, 20, fill=col, stroke=MUTED if dash else "none", sw=1.6, rx=5, dash=dash)
        lines = g.wrap(f"{text_}: {len(ps)}", 14, col_w - 60)
        assert len(lines) == 1, f"legend entry too long: {text_}"
        out += g.text(cx + 46, cy + 15, lines[0], 14, fill=INK)
        cv.add(out, cx, cy, cx + col_w - 10, cy + 22)
    union = n_wd + n_cm - n_both
    cv.add(g.text(0, y + 3 * 34 + 20, f"Together the two vocabularies cover {union} of the {total} properties.",
                  14, italic=True, fill=MUTED), 0, y + 3 * 34, W, y + 3 * 34 + 26)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts = model_data.caption_facts(M)
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts)
    log.append(f"{facts['n_twin']} with a Wikidata twin, {facts['n_with_codemeta']} with a CodeMeta term, {facts['n_crosswalked']} in both")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
