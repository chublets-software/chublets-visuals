"""Parses data/raw/open-archaeo/wikidata-main.py -- a vendored snapshot of
github.com/n4o-rse/open-archaeo's py/wikidata/main.py -- for the real
ALL_STEPS pipeline that `python py/wikidata/main.py all` runs.

Why a vendored snapshot rather than a live clone at build time: A3 keeps
network access confined to one step nobody runs by default (there isn't
one here yet), and a snapshot is exactly what PRIMER.md Befund 10 needed
-- something S6 can be checked against without re-cloning an external
repo on every build. Refreshing it is one file copy: replace
data/raw/open-archaeo/wikidata-main.py with the current
py/wikidata/main.py from the real repo, dated in a PRIMER.md Befund, and
step_open_archaeo_pipeline.py picks up whatever ALL_STEPS says without
any code change here -- that is the "weiterfuehren, wenn sich im Repo was
tut" Flo asked for (2026-09-10).

Extraction is a bracket-matched slice fed to `ast.literal_eval`, not a
full Python parse: ALL_STEPS is a plain list-of-tuples literal (str, bool,
str), and literal_eval is the standard-library-safe way to turn exactly
that back into data without executing the file it came from.
"""

from __future__ import annotations

import ast
from pathlib import Path


def _extract_literal(source: str, name: str) -> str:
    """Return the `[...]` (or `(...)`) literal assigned to `name = `,
    found by bracket-matching from the first opening bracket after the
    assignment -- robust to the literal spanning multiple lines, which a
    single-line regex would not be.
    """
    marker = f"{name} = "
    start = source.index(marker) + len(marker)
    open_ch = source[start]
    close_ch = {"[": "]", "(": ")"}[open_ch]
    depth = 0
    for i in range(start, len(source)):
        if source[i] == open_ch:
            depth += 1
        elif source[i] == close_ch:
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise ValueError(f"unbalanced brackets while extracting {name!r}")


def load(main_py_path: Path) -> dict:
    """Returns the pieces step_open_archaeo_pipeline.py draws its content
    from: `all_steps` ([(name, needs_connection, description), ...]),
    `steps` (the full STEPS list including the ones ALL_STEPS omits), and
    `reconcile_step` (the (name, needs_connection, description) tuple for
    the step `all` deliberately leaves out, alongside `push`).
    """
    source = main_py_path.read_text(encoding="utf-8")

    steps = ast.literal_eval(_extract_literal(source, "STEPS"))
    all_steps = ast.literal_eval(_extract_literal(source, "ALL_STEPS"))
    reconcile_step = ast.literal_eval(_extract_literal(source, "RECONCILE_STEP"))

    return {"steps": steps, "all_steps": all_steps, "reconcile_step": reconcile_step}
