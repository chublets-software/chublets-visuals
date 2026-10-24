#!/usr/bin/env python3
"""chublets-visuals orchestrator -- the only entry point.

    python main.py                     all steps, in order
    python main.py --list              print steps and exit
    python main.py --only codemeta     one step
    python main.py --from crosswalk    this step and everything after
    python main.py --skip datamodel    everything but this
    python main.py --dry-run           print the plan, run nothing
    python main.py --strict            warnings become errors (this is what CI runs)

Step modules are imported lazily so `--list` and `--dry-run` stay instant
and free of resvg-py/Pillow/openpyxl.

Every planned step (Block 1, Block 2, S4, S4b, S4c, S5, S6, S6b, S6c, S7,
S7b) is built; S8 onwards (the graphics of the Wikibase data model) is under
way, see PRIMER.md. New work gets a fresh id; existing ids never change, since
PATCH-README.md and PRIMER.md refer to them by id. `model-data` runs first and
`captions` checks the finished graphics; `tables` writes tex/ (paper appendix) and
`gallery` last writes docs/ (the GitHub Pages overview), because it shows everything
the steps before it produced.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "py"))

# (id, description, module name under py/)
STEPS = [
    ("model-data", "S8: verify the vendored model sources and the numbers drawn from them", "step_model_data_check"),
    ("codemeta", "Block 1 (1/4): CodeMeta term overview (class tree)", "step_codemeta_overview"),
    ("wikidata", "Block 1 (2/4): Wikidata software-properties overview", "step_wikidata_properties_overview"),
    ("crosswalk", "Block 1 (3/4): CodeMeta <-> Wikidata crosswalk", "step_codemeta_wikidata_crosswalk"),
    ("datamodel", "Block 1 (4/4): chublets.software federated datamodel", "step_wikibase_datamodel"),
    ("pattern", "S4: chublets.software four-step pattern banner + 4 icon badges", "step_pattern"),
    ("ingest", "S4b (1/4): Ingest detail -- three input sources", "step_ingest_inputs"),
    ("model", "S4b (2/4): Model detail -- compact datamodel card", "step_model_datamodel"),
    ("curate", "S4b (3/4): Curate & Link detail -- curation workflow", "step_curate_workflow"),
    ("export", "S4b (4/4): Export & Publish detail -- export pipeline", "step_export_pipeline"),
    ("architecture", "S5: chublets.software system architecture (5 stages)", "step_architecture"),
    ("fair-pattern", "Block 2 (1/5): FAIR4RS chain banner + 4 badges", "step_fair_pattern"),
    ("fair-findable", "Block 2 (2/5): Findable detail", "step_fair_findable"),
    ("fair-accessible", "Block 2 (3/5): Accessible detail", "step_fair_accessible"),
    ("fair-interoperable", "Block 2 (4/5): Interoperable detail (CodeMeta hub)", "step_fair_interoperable"),
    ("fair-reusable", "Block 2 (5/5): Reusable detail", "step_fair_reusable"),
    ("open-archaeo", "S6: open-archaeo to Wikidata import pipeline", "step_open_archaeo_pipeline"),
    ("oa-two-routes", "S6b (1/3): open-archaeo two routes overview", "step_open_archaeo_two_routes"),
    ("oa-python-route", "S6b (2/3): the Python route session", "step_open_archaeo_python_route"),
    ("oa-openrefine-route", "S6b (3/3): the OpenRefine route", "step_open_archaeo_openrefine_route"),
    ("talk-closing", "Talk closing slide: 8 badges as a ring around the logo", "step_talk_closing"),
    ("class-tree", "S10: class tree of the chublets Wikibase (13 classes)", "step_class_tree"),
    ("property-origin", "S10: origin of the 168 properties by Starter Pack status", "step_property_origin"),
    ("tables", "S9b: LaTeX tables for the paper appendix (tex/)", "step_latex_tables"),
    ("captions", "S8: captions.yaml against the graphics on disk", "step_captions_check"),
    ("gallery", "S9c: HTML overview of graphics and tables for GitHub Pages (docs/)", "step_gallery"),
]


def _select(args: argparse.Namespace) -> list[tuple[str, str, str]]:
    ids = [s[0] for s in STEPS]
    if args.only:
        if args.only not in ids:
            sys.exit(f"unknown step '{args.only}' -- choices: {', '.join(ids)}")
        return [s for s in STEPS if s[0] == args.only]
    if args.frm:
        if args.frm not in ids:
            sys.exit(f"unknown step '{args.frm}' -- choices: {', '.join(ids)}")
        i = ids.index(args.frm)
        return STEPS[i:]
    if args.skip:
        if args.skip not in ids:
            sys.exit(f"unknown step '{args.skip}' -- choices: {', '.join(ids)}")
        return [s for s in STEPS if s[0] != args.skip]
    return list(STEPS)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the chublets-visuals graphics.")
    ap.add_argument("--list", action="store_true", help="print steps and exit")
    ap.add_argument("--only", metavar="ID", help="run exactly one step")
    ap.add_argument("--from", dest="frm", metavar="ID", help="run this step and everything after")
    ap.add_argument("--skip", metavar="ID", help="run everything but this step")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    ap.add_argument("--strict", action="store_true", help="warnings become errors")
    args = ap.parse_args()

    if args.list:
        for sid, desc, _ in STEPS:
            print(f"{sid:10s} {desc}")
        return 0

    selected = _select(args)

    if args.dry_run:
        print("plan:")
        for sid, desc, _ in selected:
            print(f"  {sid:10s} {desc}")
        return 0

    timings: list[tuple[str, float]] = []
    report_lines: list[str] = []
    had_error = False

    for sid, desc, modname in selected:
        print(f"== {sid} -- {desc} ==")
        t0 = time.time()
        try:
            mod = importlib.import_module(modname)
            for line in mod.run(strict=args.strict):
                print(f"  {line}")
                report_lines.append(f"[{sid}] {line}")
        except Exception as exc:  # noqa: BLE001 -- surfaced to the user, not swallowed
            had_error = True
            print(f"  ERROR: {exc}")
            report_lines.append(f"[{sid}] ERROR: {exc}")
            if args.strict:
                break
        timings.append((sid, time.time() - t0))

    total = sum(t for _, t in timings)
    print("\ntiming:")
    for sid, t in timings:
        share = (t / total * 100) if total else 0
        print(f"  {sid:10s} {t:6.2f}s  ({share:4.1f}%)")
    print(f"  {'total':10s} {total:6.2f}s")

    report_path = ROOT / "img" / "pipeline_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
