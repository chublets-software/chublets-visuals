"""The chublets Wikibase data model, read from the vendored sources.

One place that knows how the tables of `chublets-wikibase-demo`, the kernel of
`wikibase-static` and the Starter Pack relate, so that no figure re-derives a
count (PRIMER.md A2: every number in a graphic is read at run time, never typed).

Sources (all under data/raw/, unchanged copies; see data/raw/SNAPSHOT.md):

  chublets-wikibase-demo/data/csv/*.csv            the model as the demo keeps it
  chublets-wikibase-demo/background/property-set.csv   what the Starter Pack said
  chublets-wikibase-demo/starter-pack/data/*.csv   the crosswalk ground truth
  wikibase-static/.../kernel/*.csv                 Q1-Q3, P1-P10
  wikibase-federation/usecases/chublets/*          id maps of the push

What the property set is made of (verified by `model-data`):

  kernel   P1-P10 (the numbers 1 to 99 are reserved for it), of which P1, P2, P4,
           P7 are rows of the Starter Pack and P3, P5, P6, P8, P9, P10 are not
  pack     149 further rows of the Starter Pack (P100 ...)
  review   P249-P257, nine properties of the WikiProject page that the pack lacked
           (review of 2026-10-22)

The Starter Pack's own count of 153 is "pack" plus the four kernel rows it lists.
Each pack row keeps its original `pack_status` (crosswalked / codemeta-only /
wikidata-only / chublets-addition); the nine review rows and the six other
kernel properties have none, and say so instead of inheriting one.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from visuals_utils import DATA_RAW

DEMO = DATA_RAW / "chublets-wikibase-demo"
STATIC = DATA_RAW / "wikibase-static"
FEDERATION = DATA_RAW / "wikibase-federation"
PACK = DEMO / "starter-pack" / "data"
STATIC_KERNEL = STATIC / "py" / "wikibase_static" / "data" / "kernel"

PACK_STATUSES = ("crosswalked", "codemeta-only", "wikidata-only", "chublets-addition")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _idnum(entity_id: str) -> int:
    return int(entity_id[1:])


def _split(text: str) -> tuple[str, ...]:
    return tuple(t.strip() for t in text.split(";") if t.strip())


_TAG = re.compile(r"<\s*([A-Za-z][A-Za-z0-9]*)")


def datacite_elements(text: str) -> tuple[str, ...]:
    """DataCite element names in a Starter Pack `datacite_elements` cell.

    The cell holds either a bare element ("creator") or the XML the crosswalk
    shows (`<relatedItem relatedItemType="..." relationType="IsDocumentedBy">`);
    only the element name is kept, the many-to-one qualifier (`relationType`,
    `contributorType`, `dateType`) stays available in `Prop.datacite_raw`."""
    text = text.strip()
    if not text:
        return ()
    names = _TAG.findall(text)
    if names:
        out: list[str] = []
        for n in names:
            if n not in out:
                out.append(n)
        return tuple(out)
    return (text.split()[0],)


_TAG_FULL = re.compile(r"<\s*([A-Za-z][A-Za-z0-9]*)([^>]*)>")
_ATTR = re.compile(r'([A-Za-z][A-Za-z0-9]*)="([^"]*)"')


def datacite_detail(text: str) -> tuple[str, ...]:
    """DataCite element plus the qualifiers that tell its many-to-one uses apart.

    `<relatedItem relatedItemType="JournalArticle" relationType="IsDocumentedBy">`
    becomes `relatedItem [relatedItemType=JournalArticle, relationType=IsDocumentedBy]`.
    Attribute values that are only a placeholder ("....." in the crosswalk) are
    dropped. A bare element ("creator") stays as it is."""
    text = text.strip()
    if not text:
        return ()
    found = _TAG_FULL.findall(text)
    if not found:
        return (text.split()[0],)
    out: list[str] = []
    for name, attrs in found:
        pairs = [f"{k}={v}" for k, v in _ATTR.findall(attrs) if v.strip(".") != ""]
        item = f"{name} [{', '.join(pairs)}]" if pairs else name
        if item not in out:
            out.append(item)
    return tuple(out)


@dataclass(frozen=True)
class Prop:
    id: str
    label: str
    datatype: str
    origin_set: str            # "kernel" | "pack" | "review"
    pack_status: str           # one of PACK_STATUSES, or "" (review rows, extra kernel)
    twin: str                  # Wikidata property (P4), "" if none
    close_match: tuple[str, ...]
    codemeta_terms: tuple[str, ...]
    codemeta_groups: tuple[str, ...]   # CodeMeta type of each term (Thing, CreativeWork, ...)
    schema_org: tuple[str, ...]        # P102
    datacite: tuple[str, ...]          # element names, derived via CodeMeta (not published)
    datacite_raw: str
    datacite_detail: tuple[str, ...]   # element + qualifiers, see datacite_detail()
    wikiproject_group: str     # group of the twin on the WikiProject page ("" if none)
    domain: str                # P9
    range: str                 # P10
    phase: str
    provenance: tuple[str, ...]
    confidence: str

    @property
    def kernel(self) -> bool:
        return self.origin_set == "kernel"


@dataclass(frozen=True)
class Cls:
    id: str
    label: str
    origin: str
    parents: tuple[str, ...]   # P1
    twin: str                  # P4
    crm: str                   # CRM class of the model (own row) or ""


@dataclass
class Model:
    props: dict[str, Prop]
    classes: dict[str, Cls]
    pack_rows: int
    mapping_summary: dict[str, int]
    codemeta_terms: list[dict[str, str]]
    bridge: list[dict[str, str]]
    wikiproject_groups: dict[str, str]
    crm: dict[str, str] = field(default_factory=dict)

    # -- counts ------------------------------------------------------------
    def by_set(self) -> Counter:
        return Counter(p.origin_set for p in self.props.values())

    def pack_status_counts(self) -> Counter:
        """The Starter Pack's own 37 / 46 / 52 / 18 (kernel rows P1, P2, P4, P7 included)."""
        return Counter(p.pack_status for p in self.props.values() if p.pack_status)

    def bridge_counts(self) -> Counter:
        return Counter(r["bridge"] for r in self.bridge)

    def crm_of(self, class_id: str) -> tuple[str, str]:
        """(CRM class, class it is inherited from) for a class of the model."""
        seen: set[str] = set()
        todo = [class_id]
        while todo:
            c = todo.pop(0)
            if c in seen or c not in self.classes:
                continue
            seen.add(c)
            if self.classes[c].crm:
                return self.classes[c].crm, c
            todo.extend(self.classes[c].parents)
        return "", ""


def load() -> Model:
    demo_entities = read_csv(DEMO / "data" / "csv" / "entities.csv")
    kernel_entities = read_csv(STATIC_KERNEL / "entities.csv")
    demo_statements = read_csv(DEMO / "data" / "csv" / "statements.csv")
    kernel_statements = read_csv(STATIC_KERNEL / "statements.csv")
    pack_set = {r["local_id"]: r for r in read_csv(DEMO / "background" / "property-set.csv")}

    stmts: dict[str, dict[str, list[str]]] = {}
    for s in kernel_statements + demo_statements:
        stmts.setdefault(s["subject"], {}).setdefault(s["property"], []).append(s["value"])

    def vals(entity: str, prop: str) -> tuple[str, ...]:
        return tuple(stmts.get(entity, {}).get(prop, ()))

    # CodeMeta type of every CodeMeta term (all 84 rows, not only the 68 of the workbook)
    cm_rows = read_csv(PACK / "codemeta-terms-to-wikibase.csv")
    cm_group: dict[str, str] = {}
    for r in cm_rows:
        cm_group.setdefault(r["codemeta_term"], r["codemeta_group"])

    wp_group = {r["pid"]: r["group"] for r in read_csv(PACK / "wikidata-properties.csv") if r["group"]}

    entity_rows = {e["id"]: e for e in kernel_entities + demo_entities}
    prop_ids = sorted((i for i, e in entity_rows.items() if e["kind"] == "property"), key=_idnum)

    props: dict[str, Prop] = {}
    for pid in prop_ids:
        e = entity_rows[pid]
        row = pack_set.get(pid, {})
        is_kernel = _idnum(pid) < 100
        origin_set = "kernel" if is_kernel else ("pack" if pid in pack_set else "review")
        twin = (vals(pid, "P4") or ((row.get("wikidata_pid", ""),) if row.get("wikidata_pid") else ("",)))[0]
        terms = _split(row.get("codemeta_terms", ""))
        # P101 on the entity is the model's own record of the term; it agrees with the pack row
        terms = terms or vals(pid, "P101")
        dc_raw = row.get("datacite_elements", "")
        props[pid] = Prop(
            id=pid,
            label=e["label_en"],
            datatype=e["datatype"],
            origin_set=origin_set,
            pack_status=row.get("status", ""),
            twin=twin,
            close_match=vals(pid, "P100"),
            codemeta_terms=terms,
            codemeta_groups=tuple(cm_group.get(t, "") for t in terms),
            schema_org=vals(pid, "P102"),
            datacite=datacite_elements(dc_raw),
            datacite_raw=dc_raw,
            datacite_detail=datacite_detail(dc_raw),
            wikiproject_group=wp_group.get(twin, ""),
            domain=(vals(pid, "P9") or ("",))[0],
            range=(vals(pid, "P10") or ("",))[0],
            phase=row.get("phase", ""),
            provenance=_split(row.get("provenance", "")),
            confidence=row.get("confidence", ""),
        )

    crm_rows = {r["class"]: r["crm_class"] for r in read_csv(DEMO / "data" / "crm.csv")}
    classes: dict[str, Cls] = {}
    for cid in sorted((i for i, e in entity_rows.items() if e["kind"] == "class"), key=_idnum):
        e = entity_rows[cid]
        classes[cid] = Cls(
            id=cid,
            label=e["label_en"],
            origin=e.get("origin", ""),
            parents=vals(cid, "P1"),
            twin=(vals(cid, "P4") or ("",))[0],
            crm=crm_rows.get(cid, ""),
        )

    summary = {
        r["metric"].strip(): int(r["value"])
        for r in read_csv(PACK / "mapping-summary.csv")
        if r["value"].strip().isdigit()
    }
    return Model(
        props=props,
        classes=classes,
        pack_rows=len(pack_set),
        mapping_summary=summary,
        codemeta_terms=cm_rows,
        bridge=read_csv(PACK / "datacite-wikidata-bridge.csv"),
        wikiproject_groups=wp_group,
        crm=crm_rows,
    )
