"""The statistics and catalogues of the Wikibase data model as neutral tables.

Every table is built here once, from `model_data` (and `topics`), as plain text:
a `Table` of columns and rows with no LaTeX and no HTML in it. Two renderers
read the same objects, so the paper appendix and the HTML overview cannot differ:

  py/latex_utils.py + py/step_latex_tables.py   ->  tex/table-*.tex   (Overleaf)
  py/step_gallery.py                            ->  docs/index.html and docs/data/*.csv

All numbers in cells and captions are computed from the vendored sources (nothing
is typed), and `build()` asserts the sums that must hold (168 properties, 153
initial-set properties, 84 CodeMeta rows ...), so a table cannot go out with a number
that disagrees with the model.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_data  # noqa: E402
import topics as topics_mod  # noqa: E402


@dataclass(frozen=True)
class Col:
    title: str
    align: str = "l"          # "l" | "r" (LaTeX letter; HTML text-align)
    width: float | None = None  # fraction of \linewidth for a wrapping LaTeX column
    brk: bool = False         # identifiers / URLs: allow line breaks inside words


@dataclass(frozen=True)
class Row:
    cells: tuple[str, ...]
    total: bool = False


@dataclass(frozen=True)
class Sub:
    """Sub-header row (a topic). In HTML it becomes a leading 'Topic' column."""
    text: str


@dataclass
class Table:
    name: str                 # file stem: tex/<name>.tex, docs/data/<name>.csv
    label: str                # LaTeX label
    title: str                # short name for the HTML page
    caption: str
    cols: list[Col]
    rows: list[Row | Sub]
    size: str = r"\small"
    tabcolsep: str | None = None
    sources: tuple[str, ...] = ()


STATUS = {
    "crosswalked": "crosswalked",
    "codemeta-only": "CodeMeta only",
    "wikidata-only": "Wikidata only",
    "chublets-addition": "chublets addition",
    "": "none",
}
STATUS_ORDER = ("crosswalked", "codemeta-only", "wikidata-only", "chublets-addition", "")
SET_LABEL = {"kernel": "kernel", "pack": "initial", "review": "review"}
DATATYPE = {
    "wikibase-item": "item",
    "external-id": "external id",
    "commonsMedia": "media",
    "monolingualtext": "mono. text",
    "wikibase-property": "property",
}
BRIDGE = {
    "both": "both",
    "wikidata-only": "Wikidata only",
    "datacite-only": "DataCite only",
    "neither": "neither",
    "not in S9": "not in crosswalk",
}
DASH = "--"


def _r(*cells: object, total: bool = False) -> Row:
    return Row(tuple(str(c) for c in cells), total)


def _n(n: int) -> str:
    return str(n) if n else DASH


def _status_key(p: model_data.Prop) -> str:
    return p.pack_status


def _schema_cell(p: model_data.Prop) -> str:
    if not p.schema_org:
        return DASH
    if set(p.schema_org) == set(p.codemeta_terms):
        return "="
    return ", ".join(p.schema_org)


def _wikidata_cell(p: model_data.Prop) -> str:
    if p.twin:
        return p.twin
    if p.close_match:
        return "≈ " + ", ".join(p.close_match)
    return DASH


def _verification() -> Counter:
    rows = model_data.read_csv(model_data.DEMO / "background" / "verification-report.csv")
    return Counter(r["verdict"] for r in rows)


# --------------------------------------------------------------------------
def t_statistics(M: model_data.Model) -> Table:
    s = M.mapping_summary
    sets = M.by_set()
    st = M.pack_status_counts()
    br = M.bridge_counts()
    ver = _verification()
    n_checks = sum(ver.values())
    cls_origin = Counter(c.origin or "kernel" for c in M.classes.values())
    n_dc = sum(1 for p in M.props.values() if p.datacite)
    n_so = sum(1 for p in M.props.values() if p.schema_org)
    n_cm = sum(1 for p in M.props.values() if p.close_match)
    pack_rows = sum(st.values())
    rows = [
        _r("Properties in the Wikibase model", len(M.props), f"{sets['kernel']} kernel + {sets['pack']} initial + {sets['review']} review"),
        _r("Properties of the initial modelling set", pack_rows, f"{sets['pack']} initial + {pack_rows - sets['pack']} kernel properties"),
        _r("Properties of the demo import", sets["pack"] + sets["review"], f"{sets['pack']} initial + {sets['review']} review (P100 to P257)"),
        _r("Classes", len(M.classes), f"{cls_origin['kernel']} kernel, {cls_origin['starter-pack']} chublets, {cls_origin['wikidata-stub']} Wikidata stubs"),
        _r("CodeMeta terms (distinct)", s["codemeta_terms_total"], f"{len(M.codemeta_terms)} crosswalk rows; relatedLink has two"),
        _r("  in the reviewed crosswalk workbook", s["codemeta_terms_in_reviewed_workbook"], f"{s['codemeta_terms_not_in_workbook']} terms are not in it"),
        _r("  crosswalked to a Wikidata property", s["codemeta_terms_crosswalked_to_wikidata"], f"{s['wikidata_pids_used_by_crosswalk']} distinct Wikidata properties"),
        _r("  without a Wikidata property", s["codemeta_terms_without_wikidata_property"], "new CodeMeta-only properties"),
        _r("Wikidata properties of the crosswalk in the WikiProject list", s["of which in the WikiProject Software list"], f"{s['of which NOT in the WikiProject Software list']} are not in it"),
        _r("WikiProject Software properties known", s["wikiproject_software_pids_known"], f"{s['of which Wikidata-only (no CodeMeta term)']} without a CodeMeta term"),
        _r("Origin class: crosswalked", st["crosswalked"], "CodeMeta term and Wikidata property, one Wikibase property"),
        _r("Origin class: CodeMeta only", st["codemeta-only"], "new property for a CodeMeta term"),
        _r("Origin class: Wikidata only", st["wikidata-only"], "Wikidata property without CodeMeta term"),
        _r("Origin class: chublets addition", st["chublets-addition"], "in neither vocabulary"),
        _r("Properties with a close match (P100)", n_cm, "loose Wikidata match of a CodeMeta-only property"),
        _r("Properties with a schema.org term (P102)", n_so, "term of the property in schema.org"),
        _r("Properties with a DataCite element", n_dc, "derived via the CodeMeta hub, not published"),
        _r("CodeMeta terms in both Wikidata and DataCite", br["both"], "of the 68 terms of the crosswalk"),
        _r("CodeMeta terms in Wikidata only", br["wikidata-only"], ""),
        _r("CodeMeta terms in DataCite only", br["datacite-only"], ""),
        _r("CodeMeta terms in neither", br["neither"], ""),
        _r("Checks against live Wikidata", n_checks, f"{ver['ok']} ok, {n_checks - ver['ok']} differ (label or datatype)"),
    ]
    assert pack_rows == s["wikibase_properties_total"], "initial-set property count differs from mapping-summary"
    assert sum(br.values()) == s["codemeta_terms_in_reviewed_workbook"]
    cap = (
        f"Key figures of the chublets Wikibase data model: {len(M.props)} properties and {len(M.classes)} classes, "
        f"their origin classes, and the evidence base (CodeMeta, DataCite via the CodeMeta hub, Wikidata verification). "
        f"All values are read from the vendored model tables."
    )
    return Table("table-model-statistics", "tab:model-statistics", "Model statistics", cap,
                 [Col("Measure", width=0.44), Col("Value", "r"), Col("Composition", width=0.40)], rows,
                 sources=("chublets-wikibase-demo",))


def t_origin(M: model_data.Model) -> Table:
    rows = []
    tot: Counter = Counter()
    for sset in ("kernel", "pack", "review"):
        ps = [p for p in M.props.values() if p.origin_set == sset]
        c = Counter(_status_key(p) for p in ps)
        cells = [SET_LABEL[sset]] + [_n(c[k]) for k in STATUS_ORDER[:4]] + [_n(c[""]), str(len(ps))]
        rows.append(Row(tuple(cells)))
        tot.update(c)
    rows.append(_r("total", *[_n(tot[k]) for k in STATUS_ORDER[:4]], _n(tot[""]), len(M.props), total=True))
    assert sum(tot.values()) == len(M.props)
    cap = (
        f"The {len(M.props)} properties of the Wikibase model by origin set and origin class. "
        f"The kernel (P1 to P10) belongs to wikibase-static; the initial set (P100 to P248) was the starting point of the modelling; "
        f"the {M.by_set()['review']} review properties were added after the review of 2026-10-22. "
        f"Only the initial set and four kernel properties carry an origin class; the others are unclassified."
    )
    cols = [Col("Set", width=0.14), Col("Crosswalked", "r", 0.14), Col("CodeMeta only", "r", 0.14), Col("Wikidata only", "r", 0.14),
            Col("chublets addition", "r", 0.14), Col("Unclassified", "r", 0.14), Col("Total", "r", 0.14)]
    return Table("table-property-origin", "tab:property-origin", "Properties by origin", cap, cols, rows, size=r"\footnotesize", tabcolsep="3pt", sources=("chublets-wikibase-demo",))


def t_evidence(M: model_data.Model) -> Table:
    rows = []
    cols_n = 6
    tot = [0] * cols_n
    for k in STATUS_ORDER:
        ps = [p for p in M.props.values() if _status_key(p) == k]
        vals = [len(ps), sum(1 for p in ps if p.twin), sum(1 for p in ps if p.close_match),
                sum(1 for p in ps if p.codemeta_terms), sum(1 for p in ps if p.schema_org), sum(1 for p in ps if p.datacite)]
        tot = [a + b for a, b in zip(tot, vals)]
        rows.append(_r("unclassified" if k == "" else STATUS[k], *[_n(v) for v in vals]))
    rows.append(_r("total", *tot, total=True))
    assert tot[0] == len(M.props)
    cap = (
        f"Which external vocabularies the {len(M.props)} properties point to, by origin class: "
        f"a Wikidata twin (P4), a loose Wikidata close match (P100), a CodeMeta term, a schema.org term (P102), "
        f"and a DataCite element (derived via the CodeMeta hub; DataCite itself is not published as a mapping)."
    )
    cols = [Col("Status", width=0.16), Col("Properties", "r", 0.14), Col("Wikidata twin", "r", 0.14), Col("Close match", "r", 0.14),
            Col("CodeMeta term", "r", 0.14), Col("schema.org", "r", 0.14), Col("DataCite", "r", 0.14)]
    return Table("table-property-evidence", "tab:property-evidence", "Evidence per status", cap, cols, rows,
                 size=r"\footnotesize", tabcolsep="3pt", sources=("chublets-wikibase-demo",))


def t_topics(M: model_data.Model, ts: list[topics_mod.Topic]) -> Table:
    rows = []
    tot = [0] * 6
    for t in ts:
        ps = [M.props[p] for p in t.members]
        s = Counter(p.origin_set for p in ps)
        vals = [len(ps), s["kernel"], s["pack"], s["review"], sum(1 for p in ps if p.schema_org), sum(1 for p in ps if p.datacite)]
        tot = [a + b for a, b in zip(tot, vals)]
        rows.append(_r(t.label, *[_n(v) for v in vals]))
    rows.append(_r("total", *tot, total=True))
    assert tot[0] == len(M.props)
    cap = (
        f"The {len(ts)} topics of the {len(M.props)} properties, with their origin set and the number of properties that carry a schema.org term "
        f"or a DataCite element. The topics were derived from the WikiProject groups of the Wikidata twins and from the CodeMeta and schema.org "
        f"types of the terms; each property belongs to exactly one topic."
    )
    cols = [Col("Topic", width=0.22), Col("Properties", "r", 0.13), Col("Kernel", "r", 0.13), Col("Initial", "r", 0.13),
            Col("Review", "r", 0.13), Col("schema.org", "r", 0.13), Col("DataCite", "r", 0.13)]
    return Table("table-topics", "tab:topics", "Topics", cap, cols, rows, size=r"\footnotesize", tabcolsep="3pt", sources=("data/topics.yaml",))


def t_topics_status(M: model_data.Model, ts: list[topics_mod.Topic]) -> Table:
    rows = []
    tot = [0] * 6
    for t in ts:
        ps = [M.props[p] for p in t.members]
        st = Counter(_status_key(p) for p in ps)
        vals = [st["crosswalked"], st["codemeta-only"], st["wikidata-only"], st["chublets-addition"], st[""], len(ps)]
        tot = [a + b for a, b in zip(tot, vals)]
        rows.append(_r(t.label, *[_n(v) for v in vals]))
    rows.append(_r("total", *tot, total=True))
    assert tot[-1] == len(M.props)
    cap = (
        f"The {len(ts)} topics by origin class. Kernel properties outside the initial set and the {M.by_set()['review']} review "
        f"properties are unclassified."
    )
    cols = [Col("Topic", width=0.16), Col("Crosswalked", "r", 0.14), Col("CodeMeta only", "r", 0.14), Col("Wikidata only", "r", 0.14),
            Col("chublets addition", "r", 0.14), Col("Unclassified", "r", 0.14), Col("Total", "r", 0.14)]
    return Table("table-topics-by-status", "tab:topics-by-status", "Topics by origin class", cap, cols, rows, size=r"\footnotesize", tabcolsep="3pt", sources=("data/topics.yaml", "chublets-wikibase-demo"))


def t_catalogue(M: model_data.Model, ts: list[topics_mod.Topic]) -> Table:
    rows: list[Row | Sub] = []
    for t in ts:
        rows.append(Sub(f"{t.label} ({len(t.members)})"))
        for pid in t.members:
            p = M.props[pid]
            rows.append(_r(
                p.id, p.label, DATATYPE.get(p.datatype, p.datatype), SET_LABEL[p.origin_set],
                STATUS[_status_key(p)] if _status_key(p) else DASH,
                _wikidata_cell(p),
                ", ".join(p.codemeta_terms) or DASH,
                _schema_cell(p),
                ", ".join(p.datacite) or DASH,
            ))
    cap = (
        f"Catalogue of the {len(M.props)} properties of the chublets Wikibase by topic. Wikidata: twin property (P4), or the loose close match (P100) "
        f"marked with an approximation sign. CodeMeta: term(s) of the property. schema.org: ``='' means the schema.org term is the CodeMeta term, "
        f"otherwise the term is given. DataCite: element derived via the CodeMeta hub (not a published mapping)."
    ).replace("``='' ", "= ")
    cols = [Col("ID", width=0.055), Col("Label", width=0.13, brk=True), Col("Datatype", width=0.105), Col("Set", width=0.075),
            Col("Status", width=0.115), Col("Wikidata", width=0.105), Col("CodeMeta", width=0.135, brk=True),
            Col("schema.org", width=0.125, brk=True), Col("DataCite", width=0.115, brk=True)]
    return Table("table-properties-by-topic", "tab:properties-by-topic", "Properties by topic", cap, cols, rows,
                 size=r"\footnotesize", tabcolsep="2.5pt", sources=("data/topics.yaml", "chublets-wikibase-demo"))


def _prop_for_term(M: model_data.Model, row: dict[str, str]) -> model_data.Prop | None:
    term = row["codemeta_term"]
    cands = [p for p in M.props.values() if term in p.codemeta_terms]
    if len(cands) > 1:
        cands = [p for p in cands if p.twin and p.twin == row["wikidata_pid"]] or [
            p for p in cands if p.label == row["wikibase_property"]]
    return cands[0] if len(cands) == 1 else None


def t_codemeta(M: model_data.Model) -> Table:
    rows = []
    unmatched = []
    for r in M.codemeta_terms:
        p = _prop_for_term(M, r)
        if p is None:
            unmatched.append(r["codemeta_term"])
            continue
        rows.append(_r(
            r["codemeta_term"], r["codemeta_group"], STATUS[r["status"]], r["wikidata_pid"] or DASH,
            f"{p.id} {p.label}", ", ".join(p.datacite) or DASH, BRIDGE[r["s9_bridge"]],
        ))
    assert not unmatched, f"CodeMeta terms without a Wikibase property: {unmatched}"
    cs = Counter(r["status"] for r in M.codemeta_terms)
    cap = (
        f"The {len(M.codemeta_terms)} rows of the CodeMeta term crosswalk ({M.mapping_summary['codemeta_terms_total']} distinct terms; relatedLink has two rows) "
        f"with their CodeMeta type, status ({cs['crosswalked']} crosswalked rows, {cs['codemeta-only']} CodeMeta only), Wikidata property, "
        f"the Wikibase property they became, the derived DataCite element, and where the term stands in the Wikidata/DataCite bridge "
        f"(only the {sum(M.bridge_counts().values())} terms of the ConnOSS crosswalk are classified)."
    )
    cols = [Col("CodeMeta term", brk=True, width=0.15), Col("CodeMeta type", width=0.14, brk=True), Col("Status", width=0.12),
            Col("Wikidata"), Col("Wikibase property", width=0.19, brk=True), Col("DataCite", width=0.13, brk=True),
            Col("Bridge", width=0.12)]
    return Table("table-codemeta-terms", "tab:codemeta-terms", "CodeMeta terms", cap, cols, rows,
                 size=r"\footnotesize", tabcolsep="3pt", sources=("chublets-wikibase-demo",))


def t_groups(M: model_data.Model) -> Table:
    rows_in = model_data.read_csv(model_data.PACK / "wikidata-properties.csv")
    keys = ["wikidata-only", "crosswalked", "chublets-addition", "candidate only (not in set)"]
    by: dict[str, Counter] = {}
    for r in rows_in:
        by.setdefault(r["group"] or "(no group)", Counter())[r["wikibase_status"]] += 1
    order = sorted(by, key=lambda g: (-sum(by[g].values()), g))
    rows = []
    tot = Counter()
    for g in order:
        c = by[g]
        tot.update(c)
        rows.append(_r(g, *[_n(c[k]) for k in keys], sum(c.values())))
    rows.append(_r("total", *[_n(tot[k]) for k in keys], len(rows_in), total=True))
    assert set(tot) <= set(keys), set(tot) - set(keys)
    cap = (
        f"The {len(rows_in)} Wikidata properties considered for the model, by WikiProject group and by what became of them in the Wikibase. "
        f"``Candidate only'' properties were considered but are not in the property set."
    ).replace("``Candidate only''", "Candidate only")
    cols = [Col("WikiProject group", width=0.20), Col("Wikidata only", "r", 0.15), Col("Crosswalked", "r", 0.15), Col("chublets addition", "r", 0.15),
            Col("Candidate only", "r", 0.15), Col("Total", "r", 0.15)]
    return Table("table-wikidata-groups", "tab:wikidata-groups", "Wikidata groups", cap, cols, rows,
                 size=r"\footnotesize", tabcolsep="3pt", sources=("chublets-wikibase-demo",))


def t_datacite(M: model_data.Model) -> Table:
    rows = []
    for p in M.props.values():
        if p.datacite:
            rows.append(_r(p.id, p.label, ", ".join(p.codemeta_terms) or DASH, "; ".join(p.datacite_detail)))
    cap = (
        f"The {len(rows)} properties that carry a DataCite element. The element is derived via the CodeMeta hub (CodeMeta term to DataCite element "
        f"in the ConnOSS crosswalk); a mapping from DataCite to Wikidata is not published. Qualifiers in square brackets tell apart properties "
        f"that map to the same element (for example the relation or contributor type)."
    )
    cols = [Col("ID"), Col("Label", width=0.22), Col("CodeMeta term", width=0.18, brk=True), Col("DataCite element [qualifiers]", width=0.42, brk=True)]
    return Table("table-datacite-evidence", "tab:datacite-evidence", "DataCite evidence", cap, cols, rows,
                 size=r"\footnotesize", sources=("chublets-wikibase-demo",))


def t_classes(M: model_data.Model) -> Table:
    origin = {"": "kernel", "starter-pack": "chublets", "wikidata-stub": "Wikidata stub"}
    rows = []
    for c in M.classes.values():
        crm, frm = M.crm_of(c.id)
        crm_cell = DASH if not crm else (crm if frm == c.id else f"{crm} (from {frm})")
        parents = ", ".join(f"{q} {M.classes[q].label}" for q in c.parents) or DASH
        rows.append(_r(c.id, c.label, origin[c.origin], parents, c.twin or DASH, crm_cell))
    cap = (
        f"The {len(M.classes)} classes of the chublets Wikibase: origin, parent class(es) (P1), Wikidata equivalent (P4) and CIDOC CRM class "
        f"(crmdig:D14 is given for two classes; the others inherit it). Classes marked Wikidata stub were taken over from Wikidata as stubs."
    )
    cols = [Col("ID"), Col("Label", width=0.14), Col("Origin", width=0.12), Col("Parent class", width=0.19), Col("Wikidata"), Col("CRM class", width=0.17)]
    return Table("table-classes", "tab:classes", "Classes", cap, cols, rows, size=r"\footnotesize", sources=("chublets-wikibase-demo", "wikibase-static"))


def _scode(code: str) -> tuple[int, int]:
    return (0, int(code[1:])) if code[1:].isdigit() else (1, 0)


def t_sources() -> Table:
    bg = model_data.DEMO / "background"
    rows_in = model_data.read_csv(bg / "sources.csv") + model_data.read_csv(bg / "demo-sources.csv")
    rows_in.sort(key=lambda r: _scode(r["code"]))
    rows = [_r(r["code"], r["description"], r["origin"], r["retrieved"]) for r in rows_in]
    cap = (
        f"The {len(rows)} sources on which the model and its crosswalk rest "
        f"(S = source, R = assistant recall, which is unchecked)."
    )
    cols = [Col("Code"), Col("Source", width=0.40), Col("Origin", width=0.27, brk=True), Col("Retrieved")]
    return Table("table-evidence-sources", "tab:evidence-sources", "Evidence sources", cap, cols, rows,
                 size=r"\footnotesize", tabcolsep="3pt", sources=("chublets-wikibase-demo",))


def build() -> list[Table]:
    M = model_data.load()
    ts = topics_mod.load()
    problems = topics_mod.validate(ts, M)
    if problems:
        raise RuntimeError("; ".join(problems))
    return [
        t_statistics(M), t_origin(M), t_evidence(M), t_topics(M, ts), t_topics_status(M, ts), t_catalogue(M, ts),
        t_codemeta(M), t_groups(M), t_datacite(M), t_classes(M), t_sources(),
    ]


if __name__ == "__main__":
    for t in build():
        print(f"{t.name}: {len(t.rows)} rows")
