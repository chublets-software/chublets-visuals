r"""S9b -- LaTeX tables for the paper appendix (tex/).

One `longtable` per table of `tables_data` (statistics, origin, topics, the
property catalogue, CodeMeta terms, ...), plus `tex/appendix-tables.tex`, which
`\input`s them all. Copy the folder `tex/` into the Overleaf project and add

    \usepackage{longtable}
    \usepackage{array}
    \input{tex/appendix-tables}

to the document. Output is ASCII only and has no timestamp, so a second run
writes the same bytes. Sizes can be overridden for all tables at once with
`\renewcommand{\chubletstablesize}{\scriptsize}` in the preamble.

Produces: tex/table-*.tex, tex/appendix-tables.tex
Runnable standalone: `python py/step_latex_tables.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latex_utils  # noqa: E402
import tables_data  # noqa: E402
from visuals_utils import ROOT  # noqa: E402

TEX_DIR = ROOT / "tex"


def run(strict: bool = False) -> list[str]:
    tables = tables_data.build()
    log: list[str] = []
    for t in tables:
        latex_utils.write(TEX_DIR / f"{t.name}.tex", latex_utils.longtable(t, size=t.size, tabcolsep=t.tabcolsep))
        log.append(f"tex/{t.name}.tex ({len(t.rows)} rows)")
    master = [
        latex_utils.HEADER.format(name="appendix-tables"),
        "% Needs \\usepackage{longtable} and \\usepackage{array} in the preamble.",
        "",
    ]
    for t in tables:
        master.append(f"\\input{{tex/{t.name}}}")
        master.append("")
    latex_utils.write(TEX_DIR / "appendix-tables.tex", "\n".join(master))
    log.append("tex/appendix-tables.tex")
    return log


if __name__ == "__main__":
    for line in run():
        print(line)
