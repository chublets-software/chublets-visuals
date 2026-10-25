"""Captions for the graphics, kept outside the graphics.

A graphic carries no title, header, footer or citation (PRIMER.md A3, since
S8): it has to stand on its own wherever it is placed. What a paper or a slide
needs next to it -- caption, alt text, sources, licence -- lives in
`captions.yaml` at the repository root, one entry per graphic, keyed by the
file stem (`class-tree` for `img/class-tree.svg`).

    class-tree:
      caption: >-
        Class tree of the chublets Wikibase: {n_classes} classes ...
      alt: Tree of seven classes below the root class Instance ...
      sources: [chublets-wikibase-demo, wikibase-static]
      licence: ~            # optional; empty means DEFAULT_LICENCE (CC BY 4.0)

`caption` and `alt` are English (British); `{placeholders}` are filled from the
facts a step passes to `render()`, so a number in a caption is the number the
graphic shows. `sources` and `licence` are optional. Nothing here is drawn into
an image.

`check()` compares the entries with the SVGs on disk. While graphics are still
being migrated a missing entry is reported, not an error; flip REQUIRE_ALL once
every graphic has one.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from visuals_utils import IMG_DIR, ROOT

CAPTIONS_FILE = ROOT / "captions.yaml"

# Becomes True when the last graphic has its entry (end of the S11 migration):
# from then on a graphic without a caption is an error in --strict.
REQUIRE_ALL = True

# Graphics, tables and captions are CC BY 4.0, the code is MIT (decided 2026-10-24,
# see LICENSE-GRAPHICS.md). An entry may name another licence; without one this applies.
import visuals_utils  # noqa: E402

DEFAULT_LICENCE = visuals_utils.LICENCE
CREATOR = visuals_utils.CREATOR

REQUIRED_KEYS = ("caption", "alt")
KNOWN_KEYS = {"caption", "alt", "sources", "licence", "title"}


def load() -> dict[str, dict]:
    if not CAPTIONS_FILE.is_file():
        return {}
    data = yaml.safe_load(CAPTIONS_FILE.read_text(encoding="utf-8"))
    return data or {}


def render(fig_id: str, **facts: object) -> dict:
    """The entry for `fig_id` with `{placeholders}` in caption and alt filled in.

    A placeholder without a fact raises KeyError, so a caption can never go out
    with a literal "{n_props}" in it."""
    entries = load()
    if fig_id not in entries:
        raise KeyError(f"captions.yaml has no entry for '{fig_id}'")
    entry = dict(entries[fig_id])
    for key in ("caption", "alt"):
        if key in entry:
            entry[key] = str(entry[key]).format(**facts)
    return entry


def figure_ids() -> list[str]:
    """File stems of every SVG graphic under img/ (the vendored logo is no graphic)."""
    skip = IMG_DIR / "source"
    return sorted(
        {p.stem for p in IMG_DIR.rglob("*.svg") if skip not in p.parents}
    )


def check() -> tuple[list[str], list[str]]:
    """(errors, notes). Errors always fail; notes fail only once REQUIRE_ALL is set."""
    entries = load()
    ids = set(figure_ids())
    errors: list[str] = []
    notes: list[str] = []
    for fig_id, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            errors.append(f"captions.yaml: '{fig_id}' is not a mapping")
            continue
        for key in REQUIRED_KEYS:
            if not str(entry.get(key, "")).strip():
                errors.append(f"captions.yaml: '{fig_id}' has no {key}")
        for key in entry:
            if key not in KNOWN_KEYS:
                errors.append(f"captions.yaml: '{fig_id}' has unknown key '{key}'")
        if fig_id not in ids:
            errors.append(f"captions.yaml: '{fig_id}' matches no graphic under img/")
    missing = sorted(ids - set(entries))
    if missing:
        notes.append(f"{len(missing)} of {len(ids)} graphics have no caption yet")
        if REQUIRE_ALL:
            errors.extend(f"graphic '{m}' has no entry in captions.yaml" for m in missing)
    return errors, notes
