"""Check the subclass-of (P1) edges of the model against Wikidata (run by hand, needs network).

Not part of `python main.py`: the build runs offline (PRIMER.md A3). Run it once on a machine
with internet access:

    python py/check_class_hierarchy.py

For every edge "class C is a subclass of class P" in the model where both classes have a
Wikidata equivalent (P4), it asks Wikidata whether the equivalent of C is a direct or an
indirect subclass (P279) of the equivalent of P, and lists the direct Wikidata parents of C's
equivalent. The result is written to `data/raw/wikidata-class-hierarchy.csv` (commit it, then
the build can show it) and printed as a table. Only the standard library is used.
"""

from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_data  # noqa: E402

ENDPOINT = "https://query.wikidata.org/sparql"
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "wikidata-class-hierarchy.csv"
UA = "chublets-visuals/1.0 (https://github.com/chublets-software/chublets-visuals; class hierarchy check)"


def sparql(query: str) -> dict:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def ask(query: str) -> bool:
    return bool(sparql(query)["boolean"])


def main() -> int:
    M = model_data.load()
    rows = []
    for c in M.classes.values():
        for parent in c.parents:
            p = M.classes[parent]
            if not (c.twin and p.twin):
                continue  # one side has no Wikidata equivalent: nothing to compare
            direct = ask(f"ASK {{ wd:{c.twin} wdt:P279 wd:{p.twin} }}")
            time.sleep(1)
            indirect = ask(f"ASK {{ wd:{c.twin} wdt:P279+ wd:{p.twin} }}")
            time.sleep(1)
            res = sparql(
                f'SELECT ?p ?pLabel WHERE {{ wd:{c.twin} wdt:P279 ?p . '
                f'SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}'
            )
            parents = "; ".join(sorted(
                b["p"]["value"].rsplit("/", 1)[-1] + " " + b.get("pLabel", {}).get("value", "") for b in res["results"]["bindings"]))
            rel = "direct" if direct else ("indirect" if indirect else "none")
            rows.append({
                "class": c.id, "label": c.label, "wikidata": c.twin,
                "parent_class": p.id, "parent_label": p.label, "parent_wikidata": p.twin,
                "relation_in_wikidata": rel, "direct_parents_in_wikidata": parents,
            })
            print(f"{c.id} {c.label} ({c.twin}) -> {p.id} {p.label} ({p.twin}): {rel}")
            time.sleep(1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
