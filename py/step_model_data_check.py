"""S8 -- the data layer under the model graphics: verify, do not draw.

Runs first, so a broken or edited snapshot stops the build before any graphic
is drawn. Three kinds of check:

  1. the vendored files are the files in data/raw/vendor-manifest.csv
     (SHA-256, line endings normalised) -- "unchanged copies" is checked, not
     assumed;
  2. the tables agree with each other and with the Starter Pack's own summary
     (153 pack rows = 37 + 46 + 52 + 18; 83 CodeMeta terms = 37 + 46;
     DataCite bridge 24 / 8 / 9 / 27);
  3. the property set is what PRIMER.md A1 says it is (10 kernel + 149 pack +
     9 review = 168), and data/topics.yaml puts every one of them in exactly
     one topic.

Anything that is a fact about the data but not a contradiction -- the demo
README's "63 properties with item values" against what the tables count -- is
logged as a NOTE and decides nothing.

Produces: nothing under img/. Log lines only.

Runnable standalone: `python py/step_model_data_check.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_data  # noqa: E402
import topics  # noqa: E402
import vendor_sources  # noqa: E402


def run(strict: bool = False) -> list[str]:
    log: list[str] = []
    errors: list[str] = []

    problems = vendor_sources.check()
    errors.extend(problems)
    log.append(f"vendored files match the manifest ({len(problems)} problem(s))" if not problems
               else f"{len(problems)} vendored file(s) differ from the manifest")

    m = model_data.load()
    ms = m.mapping_summary

    def expect(what: str, got: object, want: object) -> None:
        if got != want:
            errors.append(f"{what}: {got} (expected {want})")

    # the property set
    sets = m.by_set()
    expect("properties in the model", len(m.props), 168)
    expect("kernel properties (P1-P10)", sets["kernel"], 10)
    expect("Starter Pack rows beyond the kernel", sets["pack"], 149)
    expect("WikiProject review additions (P249-P257)", sets["review"], 9)
    expect("Starter Pack rows", m.pack_rows, ms["wikibase_properties_total"])
    expect("Starter Pack rows = properties with a pack status",
           sum(m.pack_status_counts().values()), m.pack_rows)

    # the Starter Pack's own status counts
    for status in model_data.PACK_STATUSES:
        expect(f"pack status '{status}'", m.pack_status_counts()[status], ms[f"status {status}"])

    # CodeMeta terms
    expect("CodeMeta terms total", ms["codemeta_terms_total"],
           ms["codemeta_terms_crosswalked_to_wikidata"] + ms["codemeta_terms_without_wikidata_property"])
    expect("rows of codemeta-terms-to-wikibase.csv (one term, relatedLink, twice; Person identifier separate)",
           len(m.codemeta_terms), ms["codemeta_terms_total"] + 1)
    expect("pack rows with status crosswalked", m.pack_status_counts()["crosswalked"],
           ms["codemeta_terms_crosswalked_to_wikidata"])
    expect("pack rows with status codemeta-only", m.pack_status_counts()["codemeta-only"],
           ms["codemeta_terms_without_wikidata_property"])

    # DataCite via the CodeMeta hub
    bc = m.bridge_counts()
    expect("bridge 'both'", bc["both"], ms["s9_bridge_both_wikidata_and_datacite"])
    expect("bridge 'wikidata-only'", bc["wikidata-only"], ms["s9_bridge_wikidata_only"])
    expect("bridge 'datacite-only'", bc["datacite-only"], ms["s9_bridge_datacite_only"])
    expect("bridge 'neither'", bc["neither"], ms["s9_bridge_neither"])

    # topics (data/topics.yaml): every property in exactly one topic
    ts = topics.load()
    errors.extend(topics.validate(ts, m))

    # classes
    for cid in ("Q100", "Q101", "Q102", "Q103", "Q104", "Q105", "Q106"):
        if cid not in m.classes:
            errors.append(f"class {cid} missing from the model")
    for cid in ("Q100", "Q101", "Q102", "Q103", "Q104", "Q106"):
        if not m.crm_of(cid)[0]:
            errors.append(f"class {cid} reaches no CRM class (data/crm.csv)")

    log.append(
        f"{len(m.props)} properties: {sets['kernel']} kernel + {sets['pack']} pack + {sets['review']} review; "
        f"Starter Pack {m.pack_rows} = "
        + " + ".join(f"{m.pack_status_counts()[s]} {s}" for s in model_data.PACK_STATUSES)
    )
    log.append(f"{len(ts)} topics cover all {sum(len(t.members) for t in ts)} properties exactly once")
    log.append(f"{len(m.classes)} classes; CodeMeta {ms['codemeta_terms_total']} terms "
               f"({ms['codemeta_terms_crosswalked_to_wikidata']} crosswalked, "
               f"{ms['codemeta_terms_without_wikidata_property']} CodeMeta-only); "
               f"DataCite bridge {bc['both']} both / {bc['wikidata-only']} Wikidata only / "
               f"{bc['datacite-only']} DataCite only / {bc['neither']} neither")

    # notes: facts the tables state that differ from prose elsewhere
    n_dc = sum(1 for p in m.props.values() if p.datacite)
    n_so = sum(1 for p in m.props.values() if p.schema_org)
    n_item = sum(1 for p in m.props.values() if p.datatype == "wikibase-item" and not p.kernel)
    n_range = sum(1 for p in m.props.values() if p.range and not p.kernel)
    log.append(f"NOTE: {n_dc} properties carry a DataCite element, {n_so} a schema.org term (P102)")
    log.append(f"NOTE: {n_item} non-kernel properties have item values; {n_range} non-kernel properties carry a range (P10)")

    if errors:
        for e in errors:
            log.append(f"ERROR: {e}")
        raise RuntimeError(f"{len(errors)} data check(s) failed:\n  " + "\n  ".join(errors))
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
