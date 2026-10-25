"""Vendor the model sources of the Wikibase repositories into data/raw/.

Not a graphics step and not part of `python main.py`: it is the documented way
to refresh the snapshot, run by hand when one of the three source repositories
has moved on (PRIMER.md A3: external sources are vendored as unchanged file
copies, never re-typed as literals).

    python py/vendor_sources.py \\
        --demo ../chublets-wikibase-demo \\
        --static ../wikibase-static \\
        --federation ../wikibase-federation \\
        --open-archaeo ../open-archaeo \\
        --retrieved 2026-10-25

Writes, below data/raw/:
    chublets-wikibase-demo/...   the model tables, the Starter Pack tables and
                                 the review tables (paths as in the repository)
    wikibase-static/...          the kernel tables of the package
    wikibase-federation/...      the chublets use case (README, id maps)
    vendor-manifest.csv          repo, path, bytes, sha256 of every file
    SNAPSHOT.md                  repository, commit, retrieval date

`python py/vendor_sources.py --check` re-hashes every vendored file against the
manifest (the build runs the same check, strict, in the `model-data` step), so
"never edited" is something the repository can prove.

No clock is read: the retrieval date is an argument, so a refresh with the same
sources and the same date is byte-identical.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "vendor-manifest.csv"
SNAPSHOT = RAW / "SNAPSHOT.md"

# repo key -> (GitHub URL, vendored folder name, files relative to the checkout)
SOURCES: dict[str, tuple[str, str, list[str]]] = {
    "demo": (
        "https://github.com/n4o-rse/chublets-wikibase-demo",
        "chublets-wikibase-demo",
        [
            # the model as the demo maintains it
            "data/csv/entities.csv",
            "data/csv/statements.csv",
            "data/csv/qualifiers.csv",
            "data/csv/references.csv",
            "data/csv/idmap.csv",
            "data/csv/merges.csv",
            "data/csv/seeds-wikidata.csv",
            "data/csv/mapping/open-archaeo.csv",
            "data/csv/mapping/open-archaeo-vocabulary.csv",
            "data/crm.csv",
            # what the Starter Pack said, and what the demo's review decided
            "background/property-set.csv",
            "background/classes.csv",
            "background/sources.csv",
            "background/demo-sources.csv",
            "background/verification-report.csv",
            "background/lookup-missing.csv",
            "background/decisions/domain-range.csv",
            "background/decisions/schema-org-term.csv",
            "background/starter-pack-open-points.md",
            # the Starter Pack (crosswalk ground truth)
            "starter-pack/data/codemeta-terms-to-wikibase.csv",
            "starter-pack/data/codemeta-wikidata-crosswalk.csv",
            "starter-pack/data/datacite-wikidata-bridge.csv",
            "starter-pack/data/mapping-summary.csv",
            "starter-pack/data/wikibase-bootstrap-order.csv",
            "starter-pack/data/wikibase-property-set.csv",
            "starter-pack/data/wikidata-entities.csv",
            "starter-pack/data/wikidata-properties.csv",
            "starter-pack/data/sources.csv",
            "starter-pack/data/identity-block-variants.csv",
            "starter-pack/data/open-archaeo-columns.csv",
        ],
    ),
    "open-archaeo": (
        "https://github.com/n4o-rse/open-archaeo",
        "open-archaeo",
        [
            "open-archaeo.csv",
            "py/wikidata/main.py",
        ],
    ),
    "static": (
        "https://github.com/n4o-rse/wikibase-static",
        "wikibase-static",
        [
            "py/wikibase_static/data/kernel/entities.csv",
            "py/wikibase_static/data/kernel/statements.csv",
            "py/wikibase_static/data/dcat-crm.csv",
            "pyproject.toml",
        ],
    ),
    "federation": (
        "https://github.com/n4o-rse/wikibase-federation",
        "wikibase-federation",
        [
            "usecases/chublets/README.md",
            "usecases/chublets/adopt-chublets-wikibase.de.csv",
            "usecases/chublets/idmap-chublets-wikibase.de.csv",
            "CHANGELOG.md",
        ],
    ),
}


def sha256(path: Path) -> str:
    """SHA-256 of the file with CRLF read as LF.

    The reference platform is Windows, where git's autocrlf may rewrite line
    endings on checkout; hashing the normalised bytes keeps `--check` from
    reporting an edit that is only a line-ending conversion. (The vendored
    tables themselves contain no bare CR.)"""
    h = hashlib.sha256()
    h.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def _commit(checkout: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def vendor(checkouts: dict[str, Path], retrieved: str) -> list[str]:
    log: list[str] = []
    rows: list[tuple[str, str, int, str]] = []
    snap: list[str] = []
    for key, (url, folder, files) in SOURCES.items():
        src_root = checkouts[key]
        commit = _commit(src_root)
        snap.append(f"| `{folder}` | <{url}> | `{commit}` | {retrieved} | {len(files)} |")
        for rel in sorted(files):
            src = src_root / rel
            if not src.is_file():
                raise FileNotFoundError(f"{key}: {rel} not found in {src_root}")
            dst = RAW / folder / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)  # bytes unchanged, line endings included
            rows.append((folder, rel, dst.stat().st_size, sha256(dst)))
        log.append(f"vendored {len(files)} files from {folder} @ {commit}")

    with MANIFEST.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["repo", "path", "bytes", "sha256"])
        for r in sorted(rows):
            w.writerow(r)

    SNAPSHOT.write_text(
        "# Snapshot of the vendored model sources\n\n"
        "Unchanged copies, refreshed with `python py/vendor_sources.py`; "
        "`vendor-manifest.csv` holds a SHA-256 for every file and the build "
        "checks it.\n\n"
        "| Folder | Repository | Commit | Retrieved | Files |\n|---|---|---|---|---|\n"
        + "\n".join(snap)
        + "\n\nLicences stay with the source repositories; the Starter Pack tables "
        "carry the CC BY 4.0 of the ConnOSS crosswalk they derive from "
        "(<https://doi.org/10.5281/zenodo.21935688>).\n",
        encoding="utf-8",
    )
    log.append(f"wrote {MANIFEST.relative_to(ROOT)} ({len(rows)} files) and {SNAPSHOT.relative_to(ROOT)}")
    return log


def check() -> list[str]:
    """Return one problem per file whose hash or presence differs from the manifest."""
    problems: list[str] = []
    if not MANIFEST.is_file():
        return [f"{MANIFEST.relative_to(ROOT)} is missing -- run py/vendor_sources.py"]
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            p = RAW / r["repo"] / r["path"]
            if not p.is_file():
                problems.append(f"missing vendored file {p.relative_to(ROOT)}")
            elif sha256(p) != r["sha256"]:
                problems.append(f"{p.relative_to(ROOT)} differs from the manifest (edited?)")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", type=Path, help="checkout of n4o-rse/chublets-wikibase-demo")
    ap.add_argument("--static", type=Path, help="checkout of n4o-rse/wikibase-static")
    ap.add_argument("--federation", type=Path, help="checkout of n4o-rse/wikibase-federation")
    ap.add_argument("--open-archaeo", type=Path, dest="oa", help="checkout of n4o-rse/open-archaeo")
    ap.add_argument("--retrieved", help="retrieval date, YYYY-MM-DD (no clock is read)")
    ap.add_argument("--check", action="store_true", help="verify the vendored files against the manifest")
    args = ap.parse_args()

    if args.check:
        problems = check()
        for p in problems:
            print(p)
        print("vendored files match the manifest" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0

    if not (args.demo and args.static and args.federation and args.oa and args.retrieved):
        ap.error("--demo, --static, --federation, --open-archaeo and --retrieved are all required (or use --check)")
    for line in vendor({"demo": args.demo, "static": args.static, "federation": args.federation, "open-archaeo": args.oa}, args.retrieved):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
