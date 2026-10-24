"""S8 -- captions.yaml against the graphics on disk.

Runs last, after every graphic is drawn. Errors (a malformed entry, a caption
for a graphic that does not exist) always fail the step. A graphic without a
caption is a note while the migration is under way and an error once
`captions.REQUIRE_ALL` is switched on.

Produces: nothing. Log lines only.

Runnable standalone: `python py/step_captions_check.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402


def run(strict: bool = False) -> list[str]:
    errors, notes = captions.check()
    entries = captions.load()
    log = [f"captions.yaml: {len(entries)} entries for {len(captions.figure_ids())} graphics"]
    log.extend(f"NOTE: {n}" for n in notes)
    if errors:
        log.extend(f"ERROR: {e}" for e in errors)
        raise RuntimeError(f"{len(errors)} caption problem(s):\n  " + "\n  ".join(errors))
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
