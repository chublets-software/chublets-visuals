"""The topics of the Wikibase properties (data/topics.yaml).

    python py/topics.py            print the review table (Markdown) to stdout

`load()` returns the topics in plate order; `topic_of()` the topic of a property.
`validate()` is what the `model-data` step runs: every property of the model is
in exactly one topic, no topic lists an unknown property, no topic is empty.

The review table cross-tabs the topics against what they were derived from --
origin set and Starter Pack status, the WikiProject group of the Wikidata twin,
and the CodeMeta type of the property's term -- so a reader can see where the
topics agree with those groupings and where they deliberately do not. All counts
are computed from the model, none is typed.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_data  # noqa: E402
from visuals_utils import ROOT  # noqa: E402

TOPICS_FILE = ROOT / "data" / "topics.yaml"


@dataclass(frozen=True)
class Topic:
    id: str
    label: str
    description: str
    basis: str
    members: tuple[str, ...]


def load() -> list[Topic]:
    raw = yaml.safe_load(TOPICS_FILE.read_text(encoding="utf-8"))["topics"]
    return [
        Topic(
            id=t["id"],
            label=t["label"],
            description=t["description"],
            basis=t.get("basis", ""),
            members=tuple(sorted(t["members"], key=lambda p: int(p[1:]))),
        )
        for t in raw
    ]


def topic_of(topics: list[Topic]) -> dict[str, str]:
    return {p: t.id for t in topics for p in t.members}


def validate(topics: list[Topic], model: model_data.Model) -> list[str]:
    errors: list[str] = []
    seen = Counter(p for t in topics for p in t.members)
    errors += [f"topics.yaml: {p} is listed {n} times" for p, n in sorted(seen.items()) if n > 1]
    errors += [f"topics.yaml: {p} is not a property of the model" for p in sorted(seen) if p not in model.props]
    errors += [f"topics.yaml: {p} ({model.props[p].label}) is in no topic" for p in model.props if p not in seen]
    errors += [f"topics.yaml: topic '{t.id}' is empty" for t in topics if not t.members]
    ids = [t.id for t in topics]
    errors += [f"topics.yaml: topic id '{i}' is used twice" for i, n in Counter(ids).items() if n > 1]
    return errors


def review(topics: list[Topic], model: model_data.Model) -> str:
    where = topic_of(topics)
    out: list[str] = []
    out.append("# Topics of the chublets Wikibase properties -- review table\n")
    out.append(f"{len(model.props)} properties in {len(topics)} topics. Counts are computed from the vendored model.\n")

    out.append("## Topics, origin and size\n")
    out.append("| Topic | n | kernel | pack | review | crosswalked | CodeMeta only | Wikidata only | chublets addition |")
    out.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|")
    for t in topics:
        ps = [model.props[p] for p in t.members]
        s = Counter(p.origin_set for p in ps)
        st = Counter(p.pack_status for p in ps)
        out.append(
            f"| {t.label} | {len(ps)} | {s['kernel'] or ''} | {s['pack'] or ''} | {s['review'] or ''} "
            f"| {st['crosswalked'] or ''} | {st['codemeta-only'] or ''} | {st['wikidata-only'] or ''} | {st['chublets-addition'] or ''} |"
        )
    out.append("")

    out.append("## Members\n")
    for t in topics:
        out.append(f"**{t.label}** ({len(t.members)}) -- {t.description}\n")
        out.append(", ".join(f"{p} {model.props[p].label}" for p in t.members) + "\n")

    groups = sorted({p.wikiproject_group for p in model.props.values() if p.wikiproject_group})
    out.append("## Against the WikiProject groups (group of the Wikidata twin)\n")
    out.append("| Topic | " + " | ".join(groups) + " | no group |")
    out.append("|---|" + "--:|" * (len(groups) + 1))
    for t in topics:
        c = Counter(model.props[p].wikiproject_group for p in t.members)
        out.append(f"| {t.label} | " + " | ".join(str(c[g] or "") for g in groups) + f" | {c[''] or ''} |")
    out.append("")

    types = sorted({g for p in model.props.values() for g in p.codemeta_groups if g})
    out.append("## Against the CodeMeta type of the property's term\n")
    out.append("| Topic | " + " | ".join(types) + " | no term |")
    out.append("|---|" + "--:|" * (len(types) + 1))
    for t in topics:
        c: Counter = Counter()
        for p in t.members:
            gs = {g for g in model.props[p].codemeta_groups if g}
            for g in gs:
                c[g] += 1
            if not gs:
                c[""] += 1
        out.append(f"| {t.label} | " + " | ".join(str(c[g] or "") for g in types) + f" | {c[''] or ''} |")
    out.append("")

    out.append("## What the topics carry from schema.org and DataCite\n")
    out.append("| Topic | with schema.org term (P102) | with DataCite element |")
    out.append("|---|--:|--:|")
    for t in topics:
        ps = [model.props[p] for p in t.members]
        out.append(f"| {t.label} | {sum(1 for p in ps if p.schema_org) or ''} | {sum(1 for p in ps if p.datacite) or ''} |")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    m = model_data.load()
    ts = load()
    problems = validate(ts, m)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        raise SystemExit(1)
    print(review(ts, m))
