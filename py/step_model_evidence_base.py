"""S10 -- what the model rests on.

Left: the sources the modelling used, each with what was taken from it and how
reliable it is; right: the parts of the Wikibase they feed. All counts are read
from the vendored tables (crosswalk summary, verification report, decision
tables, id map).

Style: house palette for the source kinds; the model parts use the semantic
scheme (class orange, property-metadata amber, item grey).

Reads: py/model_data.py. Produces: img/model-evidence-base.svg / .png

Runnable standalone: `python py/step_model_evidence_base.py`
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import model_graphics as g  # noqa: E402
from visuals_utils import CATEGORY_COLORS, INK, MUTED, tint  # noqa: E402

NAME = "model-evidence-base"
CLS, PRP, ITM = g.SEM["class"], g.SEM["propmeta"], g.SEM["instance"]
GREY = "#64748b"
SRC_W, ROW_H, GAP_Y = 760, 92, 14
X_MODEL, MODEL_W = 1010, 330


def facts(M: model_data.Model) -> dict:
    bg = model_data.DEMO / "background"
    ver = Counter(r["verdict"] for r in model_data.read_csv(bg / "verification-report.csv"))
    ids = Counter(r["source"] for r in model_data.read_csv(model_data.DEMO / "data" / "csv" / "idmap.csv"))
    s = M.mapping_summary
    return {
        "n_checks": sum(ver.values()), "n_checks_ok": ver["ok"], "n_checks_diff": ver["DIFF"],
        "n_wd_checked": len({r["id"] for r in model_data.read_csv(bg / "verification-report.csv")}),
        "n_domain_range": len(model_data.read_csv(bg / "decisions" / "domain-range.csv")),
        "n_schema_decisions": len(model_data.read_csv(bg / "decisions" / "schema-org-term.csv")),
        "n_workbook_terms": s["codemeta_terms_in_reviewed_workbook"],
        "n_terms_outside_workbook": s["codemeta_terms_not_in_workbook"],
        "n_wikiproject_pids": s["wikiproject_software_pids_known"],
        "n_oa_entries": sum(1 for r in model_data.read_csv(model_data.DEMO / "data" / "csv" / "idmap.csv") if r["key"].startswith("entry:")),
    }


def build(M: model_data.Model) -> g.Canvas:
    cf = model_data.caption_facts(M)
    f = facts(M)
    PUR, GLD, TEAL, SLATE = CATEGORY_COLORS[0], CATEGORY_COLORS[1], CATEGORY_COLORS[2], CATEGORY_COLORS[4]
    # (title, what was taken, reliability, colour, model parts fed: p=properties c=classes i=items)
    rows = [
        ("CodeMeta–Wikidata crosswalk", f"{f['n_workbook_terms']} CodeMeta terms reviewed against Wikidata and further schemas",
         "published, read in full", PUR, "p"),
        ("CodeMeta terms page", f"{f['n_terms_outside_workbook']} further terms that have no row in the crosswalk",
         "published, read in full", PUR, "p"),
        ("Wikidata WikiProject Informatics, software properties", f"{f['n_wikiproject_pids']} Wikidata properties for software (the registry identifiers are not all listed); after review {cf['n_review']} properties were added to the model",
         "transcribed by hand", TEAL, "p"),
        ("Live Wikidata check", f"label and datatype of {f['n_wd_checked']} Wikidata entities: {f['n_checks']} checks, {f['n_checks_diff']} differences",
         "checked against Wikidata", SLATE, "pc"),
        ("Decision tables", f"domain and range of {f['n_domain_range']} properties, schema.org term of {f['n_schema_decisions']} properties",
         "decided by hand", GLD, "p"),
        ("open-archaeo list", f"{f['n_oa_entries']} software entries, with their people, tags and works, mapped to items and statements",
         "published, mapped by rule", PUR, "i"),
    ]
    cv = g.Canvas()
    y = 36
    cv.add(g.text(0, 14, "Sources of the modelling", 15, bold=True, fill=INK) + g.text(X_MODEL, 14, "What they feed", 15, bold=True, fill=INK),
           0, 0, X_MODEL + MODEL_W, 20)
    # model boxes
    parts = {"p": (PRP, "#b45309", INK, f"{cf['n_props']} properties", 60), "c": (CLS, CLS, "#ffffff", f"{cf['n_classes']} classes", 60),
             "i": (ITM, GREY, INK, f"{cf['n_items']} items", 60)}
    total_h = len(rows) * (ROW_H + GAP_Y) - GAP_Y
    ys = {"p": y + 40, "c": y + total_h / 2 - 30, "i": y + total_h - 100}
    ys["p"], ys["c"], ys["i"] = y + 20, y + total_h / 2 - 50, y + total_h - 120
    for k, (fill, stroke, ink, label, h) in parts.items():
        out = g.rect(X_MODEL, ys[k], MODEL_W, 100, fill=fill, stroke=stroke, sw=2, rx=12)
        out += g.text(X_MODEL + 22, ys[k] + 46, label, 24, bold=True, fill=ink)
        out += g.text(X_MODEL + 22, ys[k] + 72, {"p": "with their metadata", "c": "built in and defined", "i": "with statements"}[k], 13.5, fill=ink)
        cv.add(out, X_MODEL, ys[k], X_MODEL + MODEL_W, ys[k] + 100)
    yy = y
    used = Counter()
    for title, what, rel, col, feeds in rows:
        out = g.rect(0, yy, SRC_W, ROW_H, fill=tint(col, 0.94), stroke=col, sw=2, rx=12)
        out += g.rect(0, yy, 10, ROW_H, fill=col, rx=5)
        out += g.text(28, yy + 32, title, 16, bold=True, fill=INK)
        lines = g.wrap(what, 14, SRC_W - 60)
        for j, ln in enumerate(lines):
            out += g.text(28, yy + 56 + 19 * j, ln, 14, fill=INK)
        svg, cw = g.chip(SRC_W - 14, yy + 12, rel, 12, fill="none", stroke=col, color=col, anchor_right=True)
        out += svg
        cv.add(out, 0, yy, SRC_W, yy + ROW_H)
        for k in feeds:
            ty = ys[k] + 20 + 14 * used[k]
            used[k] += 1
            sy = yy + ROW_H / 2
            cv.add(g.line([(SRC_W + 4, sy), (SRC_W + 90, sy), (X_MODEL - 90, ty), (X_MODEL - 14, ty)], col, sw=1.8)
                   + g.arrowhead(X_MODEL - 2, ty, 1, 0, 10, fill=col), SRC_W, min(sy, ty), X_MODEL, max(sy, ty))
        yy += ROW_H + GAP_Y
    return cv


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    facts_ = {**model_data.caption_facts(M), **facts(M)}
    log = [g.save(NAME, build(M))]
    if NAME in captions.load():
        captions.render(NAME, **facts_)
    log.append(f"{facts_['n_checks']} checks, {facts_['n_checks_diff']} differences; {facts_['n_oa_entries']} open-archaeo keys")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
