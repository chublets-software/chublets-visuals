"""S10 -- how a chublet gets its identity.

One real chublet (pastclim) imported from an entry of the open-archaeo list. Its
identity block ties it to three shared items (the WikiProject, the platform and
the collection); the same three items are used by every chublet. Below: the
merges that unite two records of the same thing.

Style: semantic scheme (class orange, items grey).

Reads: py/model_data.py (vendored demo CSV). Produces: img/chublet-identity.svg / .png

Runnable standalone: `python py/step_chublet_identity.py`
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import INK, MUTED, tint  # noqa: E402

NAME = "chublet-identity"
ITEM = "Q424"
CLS, ITM = g.SEM["class"], g.SEM["instance"]
GREY = "#64748b"
# identity statements shown: (property label, which shared item id it points to)
IDENT = ("part of", "collection", "maintained by WikiProject")
EDGES = [("maintained by WikiProject", "Q108"), ("part of", "Q109"), ("part of", "Q110"), ("collection", "Q110")]


def _data():
    D = model_data.DEMO / "data" / "csv"
    ents = {e["id"]: e for e in model_data.read_csv(D / "entities.csv") + model_data.read_csv(model_data.STATIC_KERNEL / "entities.csv")}
    stm = model_data.read_csv(D / "statements.csv")
    idmap = model_data.read_csv(D / "idmap.csv")
    merges = model_data.read_csv(D / "merges.csv")
    return ents, stm, idmap, merges


def facts() -> dict:
    ents, stm, idmap, merges = _data()
    users = {i: len({s["subject"] for s in stm if s["value"] == i and ents[s["property"]]["label_en"] in IDENT})
             for i in ("Q108", "Q109", "Q110")}
    return {"n_merges": len(merges), "n_identity_users": max(users.values()), "n_open_archaeo_keys": sum(1 for r in idmap if r["source"] == "open-archaeo")}


def build(M: model_data.Model) -> g.Canvas:
    ents, stm, idmap, merges = _data()
    lab = lambda i: ents[i]["label_en"] if i in ents else i
    f = facts()
    key = [r["key"] for r in idmap if r["id"] == ITEM and r["source"] == "open-archaeo"]
    assert len(key) == 1, f"{ITEM} must have exactly one open-archaeo key"
    mine = [s for s in stm if s["subject"] == ITEM]
    cv = g.Canvas()
    # left: source entry
    out = g.rect(0, 70, 250, 110, fill="#ffffff", stroke=GREY, sw=2, rx=12, dash="6 4")
    out += g.text(18, 100, "Entry in the source list", 14, bold=True, fill=INK)
    out += g.text(18, 124, "open-archaeo", 13.5, fill=INK)
    out += g.text(18, 146, key[0], 13.5, fill=MUTED)
    out += g.text(18, 168, "the key stays in the id map", 12.5, italic=True, fill=MUTED)
    cv.add(out, 0, 70, 250, 180)
    # centre: the item
    X0, W0 = 340, 470
    out = g.rect(X0, 0, W0, 330, fill=tint(ITM, 0.4), stroke="#94a3b8", sw=2, rx=12)
    out += g.text(X0 + 20, 36, lab(ITEM), 22, bold=True, fill=INK)
    out += g.text(X0 + 20, 58, f"{ITEM} · chublet imported from the entry", 13.5, fill=MUTED)
    out += g.text(X0 + 20, 92, "instance of", 14, bold=True, fill=INK)
    x = X0 + 150
    for v in [s["value"] for s in mine if s["property"] == "P2"]:
        w = g.text_w(lab(v), 13.5) + 22
        out += g.rect(x, 76, w, 26, fill=CLS, rx=13) + g.text(x + 11, 94, lab(v), 13.5, fill="#ffffff")
        x += w + 8
    ys = {}
    yy = 140
    for prop, target in EDGES:
        out += g.text(X0 + 20, yy + 5, prop, 14, bold=True, fill=INK)
        out += g.text(X0 + 250, yy + 5, lab(target), 14, fill=INK)
        ys[(prop, target)] = yy
        yy += 38
    out += g.text(X0 + 20, yy + 5, "inventory number", 14, bold=True, fill=INK)
    inv = [s for s in mine if lab(s["property"]) == "inventory number"]
    out += g.text(X0 + 250, yy + 5, inv[0]["value"] if inv else "", 14, fill=INK)
    out += g.text(X0 + 20, yy + 30, "plus developers, repository, language, …", 13, italic=True, fill=MUTED)
    cv.add(out, X0, 0, X0 + W0, 330)
    cv.add(g.line([(250, 125), (X0 - 14, 125)], MUTED, sw=2) + g.arrowhead(X0, 125, 1, 0, 12)
           + g.text(295, 112, "imported as", 13, bold=True, fill=INK, anchor="middle"), 250, 100, X0, 140)
    # right: shared items
    XR = 1010
    nodes = {"Q108": 40, "Q109": 150, "Q110": 260}
    for qid, ny in nodes.items():
        o = g.rect(XR, ny, 330, 64, fill=ITM, stroke=GREY, sw=1.6, rx=32)
        o += g.text(XR + 24, ny + 28, lab(qid), 15, bold=True, fill=INK)
        users = len({s_["subject"] for s_ in stm if s_["value"] == qid and lab(s_["property"]) in IDENT})
        o += g.text(XR + 24, ny + 49, f"{qid} \u00b7 used by {users} chublets", 12.5, fill=MUTED)
        cv.add(o, XR, ny, XR + 330, ny + 64)
    for (prop, target), ey in ys.items():
        ny = nodes[target] + 32
        cv.add(g.line([(X0 + W0, ey), (X0 + W0 + 60, ey), (XR - 60, ny), (XR, ny)], MUTED, sw=1.6), X0 + W0, min(ey, ny), XR, max(ey, ny))
    cv.add(g.text(XR, 20, "Shared by every chublet", 13.5, bold=True, fill=MUTED), XR, 6, XR + 330, 26)
    # bottom: merges
    y = 380
    out = g.text(0, y, f"One thing, two records: {f['n_merges']} merges", 15, bold=True, fill=INK)
    out += g.text(0, y + 22, "An entry of the source list and a Wikidata item that describe the same thing become one item.", 13.5, fill=MUTED)
    yy = y + 56
    for r in merges:
        w1 = g.text_w(r["from"], 13) + 18
        out += g.rect(0, yy - 16, w1, 22, fill="#ffffff", stroke=GREY, sw=1.2, rx=11, dash="4 3") + g.text(9, yy, r["from"], 13, fill=MUTED)
        out += g.text(w1 + 8, yy, "→", 14, fill=MUTED)
        w2 = g.text_w(r["to"], 13) + 18
        out += g.rect(w1 + 30, yy - 16, w2, 22, fill=ITM, stroke=GREY, sw=1.2, rx=11) + g.text(w1 + 39, yy, r["to"], 13, fill=INK)
        out += g.text(w1 + w2 + 48, yy, r["note"], 13.5, fill=INK)
        yy += 28
    cv.add(out, 0, y - 18, 1340, yy)
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts_ = {**model_data.caption_facts(M), **facts()}
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts_)
    log.append(f"{facts_['n_merges']} merges, {facts_['n_open_archaeo_keys']} open-archaeo keys")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
