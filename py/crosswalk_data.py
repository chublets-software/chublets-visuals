"""Parses data/raw/codemeta-wikidata-crosswalk.xlsx into plain Python
structures for the CodeMeta and CodeMeta<->Wikidata diagram steps.

Sheet layout (Crosswalk CodeMeta, header row 4, data from row 5): column A
is the CodeMeta property name, column F is the mapped Wikidata property --
either "wd:P1324" or a free-text correction such as "corrected: P178 -
developer" (Florian's review pass overriding the first-pass mapping; see
PRIMER.md A1 Befund 1, 2026-09-10). A section header row has column A set
to "Properties from X -> Y -> Z" and columns B/C empty; that is the only
reliable marker, since a genuine property row can itself have an empty
range/description in a handful of places.

Kept as a stdlib-plus-openpyxl module, imported lazily by the two steps
that need it, so `main.py --list`/`--dry-run` stay free of the dependency.
"""

from __future__ import annotations

import re
from pathlib import Path

PID_RE = re.compile(r"\bP\d+\b")

# The four CodeMeta types the crosswalk sheet walks through, in the order
# they appear in the xlsx, each with its declared parent in the schema.org
# hierarchy CodeMeta itself documents (Thing -> CreativeWork ->
# {SoftwareSourceCode, SoftwareApplication}).
TYPE_ORDER = [
    "Thing",
    "CreativeWork",
    "SoftwareSourceCode",
    "SoftwareApplication",
]
TYPE_PARENT = {
    "Thing": None,
    "CreativeWork": "Thing",
    "SoftwareSourceCode": "CreativeWork",
    "SoftwareApplication": "CreativeWork",
}


def _section_type(header: str) -> str:
    """'Properties from Thing -> CreativeWork -> SoftwareSourceCode' -> 'SoftwareSourceCode'.
    'Properties from Thing' (no arrow, the base case) -> 'Thing'.
    """
    tail = header.split("->")[-1].strip()
    return tail.removeprefix("Properties from ").strip()


def load(xlsx_path: Path) -> dict[str, list[tuple[str, str | None]]]:
    """Returns {type_name: [(property_name, wikidata_pid_or_None), ...]}."""
    import openpyxl  # lazy

    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["Crosswalk CodeMeta"]

    sections: dict[str, list[tuple[str, str | None]]] = {t: [] for t in TYPE_ORDER}
    current: str | None = None

    for row in range(5, ws.max_row + 1):
        prop = ws.cell(row=row, column=1).value
        rng = ws.cell(row=row, column=2).value
        wd_raw = ws.cell(row=row, column=6).value
        if not prop:
            continue
        if isinstance(prop, str) and rng is None and "properties" in prop.lower():
            # Header-like row. Two kinds appear in the sheet: a genuine new
            # top-level type section ("Properties from Thing -> CreativeWork
            # -> SoftwareApplication", tail = a TYPE_ORDER member), and a
            # sub-divider within the current type ("Properties outside the
            # hierarchy from Thing -> CreativeWork -> WebPage", "Additional
            # properties from Codemeta Thing -> CreativeWork ->
            # Codemeta:Software" -- tails "WebPage" / "Codemeta:Software",
            # neither a CodeMeta type). Only the first changes `current`;
            # the second is a label only, its rows stay in the type it sits
            # under (verified against the xlsx: rows 63/66 sit inside the
            # "Thing" block, geprueft 2026-09-10).
            tail = _section_type(prop)
            if tail in TYPE_ORDER:
                current = tail
            continue
        if current is None:
            continue
        pid = None
        if wd_raw:
            m = PID_RE.search(str(wd_raw))
            if m:
                pid = m.group(0)
        sections[current].append((str(prop), pid))

    return sections


def counts(sections: dict[str, list[tuple[str, str | None]]]) -> dict[str, tuple[int, int]]:
    """Returns {type_name: (total, mapped)}."""
    return {t: (len(rows), sum(1 for _, pid in rows if pid)) for t, rows in sections.items()}
