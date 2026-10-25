"""chublets-visuals: shared constants and render helpers.

Adapted from FDOx-squirrel/fdox-visuals' visuals_utils.py (same author, same
house pattern): identical render pipeline (resvg-py, vendored Fira Sans,
trim-to-content), different palette. No step imports rdflib/Pillow
at module level -- this stays light on purpose so `python main.py --list`
and `--dry-run` are instant.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS_DIR = ROOT / "fonts"
IMG_DIR = ROOT / "img"
DATA_RAW = ROOT / "data" / "raw"

# Block subfolders under img/ (Flo, 2026-09-10: "die 'bloecke' im img
# folder in einzelne subfolder stecken"). Every step writes into exactly
# one of these -- nothing is written directly into IMG_DIR any more.
# Not one of the three numbered "blocks" -- system-level diagrams that sit
# above them (the consolidated architecture, and later the open-archaeo
# pipeline), so they get their own, non-numbered folder.
# Composited, talk-specific slides (real assets like the logo pasted onto
# a generated ring/banner) -- distinct from the generic, reusable badges
# in the block-N folders, same distinction fdox-visuals draws with its
# "talk-*" steps.
TALK_DIR = IMG_DIR / "talk"
# Real, non-regeneratable assets (the logo) that a talk-specific step
# composites onto a generated canvas -- input, not output, but kept under
# img/ so it travels with what uses it (mirrors fdox-visuals' img/source/).
SOURCE_DIR = IMG_DIR / "source"

FONT_REGULAR = FONTS_DIR / "FiraSans-Regular.ttf"
FONT_BOLD = FONTS_DIR / "FiraSans-Bold.ttf"
FONT_FAMILY = "Fira Sans"

# All graphics sit directly in img/, so the relative path back to fonts/ is one level up.
_FONT_REL_PREFIX = "../fonts"

INK = "#1E1425"
MUTED = "#5B5568"
BG = "#FFFFFF"

# The house palette. Sampled from the chublets.software logo (the crow with
# the gold nuggets, chublets_software_logo.png, 2026-09-10): dominant purple
# clusters around #32173D/#341A3F, dominant gold around #D7A141/#B8862E.
# CHUBLETS_PURPLE is the primary -- every graphic that needs "the chublets
# purple" reads it from here rather than repeating the literal, so the
# family stays a single source of truth (mirrors FDO_ACCENT in fdox-visuals).
CHUBLETS_PURPLE = "#3B1F4A"
CHUBLETS_GOLD = "#B8862E"

# Five-way category palette for grouped diagrams (property/class groupings,
# badge chains). Purple and gold are the two house colours; the other three
# are chosen for clear separation at small swatch size, not because they
# carry their own semantics -- unlike a status colour, a category colour
# here just has to stay distinct from its neighbours in the same diagram.
# Every graphic, table and caption of the model graphics is CC BY 4.0, by Florian Thiery
# (decided 2026-10-24; the code is MIT). One place, so no output can forget it.
CREATOR = "Florian Thiery"
LICENCE = "CC BY 4.0"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
ATTRIBUTION = f"{CREATOR}, {LICENCE}"

CATEGORY_COLORS = [
    "#3B1F4A",  # purple   -- house primary
    "#B8862E",  # gold     -- house secondary
    "#0E7A6E",  # teal
    "#A8451F",  # rust
    "#2A5F8A",  # slate blue
    "#5B5568",  # neutral (misc / footnote groups)
]

# chublets.software's own four-step documentation pattern (Block 3),
# analogous to fdox-visuals' FDO Encapsulation -> ... -> Federated KG
# Integration chain. Confirmed 2026-09-10 (PRIMER.md A4, was a proposal
# since S0). Colour assignment: the two house colours sit in the middle as
# the chublets-specific steps (Model, Curate & Link); teal and slate
# bookend them as the steps that face outward, toward data coming in and
# going back out. Every graphic that needs "the chublets step colours"
# reads this list rather than repeating a hex code (A3).
FOUR_STEPS = [
    {
        "id": "ingest",
        "num": "1",
        "title": ["Ingest"],
        "desc": "Wikidata items, FDOx objects & Git repos via CFF",
        "color": CATEGORY_COLORS[2],  # teal
    },
    {
        "id": "model",
        "num": "2",
        "title": ["Model"],
        "desc": "Federated datamodel: Wikidata properties + CodeMeta-only fields",
        "color": CATEGORY_COLORS[0],  # purple
    },
    {
        "id": "curate-link",
        "num": "3",
        "title": ["Curate", "& Link"],
        "desc": "Statements, qualifiers, manual curation & quality control",
        "color": CATEGORY_COLORS[1],  # gold
    },
    {
        "id": "export-publish",
        "num": "4",
        "title": ["Export", "& Publish"],
        "desc": "SPARQL to CodeMeta/DCAT/DataCite, into nfdi.software & find.software",
        "color": CATEGORY_COLORS[4],  # slate blue
    },
]

# The four FAIR4RS principles (Block 2), same badge/banner geometry as
# FOUR_STEPS, different content and icon set (step_fair_pattern.py).
# Mechanisms are a proposal (PRIMER.md A4, 2026-09-10) not yet checked
# against the actual deRSE26 paper's FAIR table (Teil D) -- Flo's own
# earlier framing ("F über nfdi.software, A/I/R via existing standards")
# is the basis. "num" holds the principle's letter rather than a step
# index, reusing the same tag rendering.
FAIR_PRINCIPLES = [
    {
        "id": "findable",
        "num": "F",
        "title": ["Findable"],
        "desc": "Persistent Wikidata Q-IDs, indexed by nfdi.software",
        "color": CATEGORY_COLORS[2],  # teal
    },
    {
        "id": "accessible",
        "num": "A",
        "title": ["Accessible"],
        "desc": "Open Wikibase API & SPARQL endpoint, no login for reads",
        "color": CATEGORY_COLORS[0],  # purple
    },
    {
        "id": "interoperable",
        "num": "I",
        "title": ["Interoperable"],
        "desc": "CodeMeta as the pivot format between vocabularies",
        "color": CATEGORY_COLORS[1],  # gold
    },
    {
        "id": "reusable",
        "num": "R",
        "title": ["Reusable"],
        "desc": "License & provenance statements, carried from CFF",
        "color": CATEGORY_COLORS[4],  # slate blue
    },
]


def ensure_dirs(path: Path = IMG_DIR) -> None:
    path.mkdir(parents=True, exist_ok=True)


def esc(text: str) -> str:
    """Escape the handful of characters that appear in our own copy text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tint(hex_color: str, white_ratio: float) -> str:
    """Mix a colour toward white by `white_ratio` (0 = unchanged, 1 = white)."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    mix = lambda c: int(c * (1 - white_ratio) + 255 * white_ratio)
    return f"#{mix(r):02X}{mix(g):02X}{mix(b):02X}"


def font_face_css(rel_prefix: str | None = None) -> str:
    """@font-face block pointing at the two vendored weights.

    Vendored, not referenced: the repo carries its own copy of Fira Sans
    under fonts/, so a fresh clone renders identically without the font
    being installed on the machine that runs it. `rel_prefix` is the relative
    path from the SVG back to fonts/ (default: two levels up, the old block
    folders; the flat graphics directly under img/ pass "../fonts").
    """
    prefix = _FONT_REL_PREFIX if rel_prefix is None else rel_prefix
    return (
        "<style>"
        f'@font-face {{ font-family: "{FONT_FAMILY}"; '
        f'src: url("{prefix}/FiraSans-Regular.ttf"); font-weight: 400; }} '
        f'@font-face {{ font-family: "{FONT_FAMILY}"; '
        f'src: url("{prefix}/FiraSans-Bold.ttf"); font-weight: 700; }}'
        "</style>"
    )


def render_svg_to_png(svg_path: Path, png_path: Path, width: int, height: int) -> None:
    """Rasterise via resvg (a single self-contained compiled wheel -- no
    system libcairo/rsvg/ImageMagick needed).
    """
    import resvg_py  # lazy: keeps --list/--dry-run free of the import

    png_bytes = resvg_py.svg_to_bytes(
        svg_path=str(svg_path),
        width=width,
        height=height,
        font_files=[str(FONT_REGULAR), str(FONT_BOLD)],
        skip_system_fonts=True,  # always our vendored files, never a same-named system font
    )
    png_path.write_bytes(png_bytes)


def trim_transparent_border(png_path: Path, margin_px: int = 10) -> tuple[int, int]:
    """Crop a PNG to its non-transparent content, then pad back out to an
    exact, small, uniform transparent border. Returns the final (w, h).
    """
    from PIL import Image  # lazy, same reasoning as render_svg_to_png

    im = Image.open(png_path).convert("RGBA")
    bbox = im.split()[-1].getbbox()  # bounding box of the alpha channel
    if bbox is None:
        return im.size  # fully transparent; nothing sensible to crop to
    cropped = im.crop(bbox)
    w, h = cropped.size
    out = Image.new("RGBA", (w + 2 * margin_px, h + 2 * margin_px), (0, 0, 0, 0))
    out.paste(cropped, (margin_px, margin_px))
    out.save(png_path)
    return out.size


def paste_raster(base_png_path: Path, asset_path: Path, x: int, y: int, w: int, h: int,
                  scale: float, circular: bool = False) -> None:
    """Composite a source raster asset onto an already-rendered PNG, at
    design-grid (x, y, w, h) scaled by the same `scale` factor the SVG was
    rasterised at. Call this BEFORE trim_transparent_border -- it needs
    the untrimmed canvas, whose pixel coordinates are known in advance
    from the design grid; trimming first would make (x, y) ambiguous.

    Prefer load_logo_inner_svg() over this for the chublets logo
    specifically: an inline nested <svg> renders identically in both the
    .svg source and the .png (one render pass, resvg-py draws the paths
    directly), where paste_raster only ever touches the already-rasterised
    .png -- the .svg source then has no logo in it at all, confirmed the
    hard way (Flo, 2026-09-10: "bei meinem output (und im repo nicht)").
    Kept for genuine raster-only assets (screenshots) that have no vector
    original to embed.
    """
    from PIL import Image, ImageDraw

    base = Image.open(base_png_path).convert("RGBA")
    px, py, pw, ph = (int(v * scale) for v in (x, y, w, h))
    src = Image.open(asset_path).convert("RGBA").resize((pw, ph), Image.LANCZOS)
    if circular:
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, pw, ph), fill=255)
        base.paste(src, (px, py), mask)
    else:
        base.paste(src, (px, py), src)
    base.save(base_png_path)


def load_logo_inner_svg(svg_path: Path) -> tuple[str, float, float]:
    """Returns (inner_xml, view_w, view_h) for a vendored, hand-authored
    SVG (namely img/source/chublets-logo.svg, Inkscape-exported) so it can
    be embedded as a nested <svg x=".." y=".." width=".." height=".."
    viewBox="0 0 view_w view_h">{inner_xml}</svg> inside a generated
    diagram -- the nested viewport does the scaling, no manual path
    transform needed.

    Strips <sodipodi:namedview>, the one element in an Inkscape export
    that uses a namespace (xmlns:sodipodi) this repo's SVGs never declare
    on their own root <svg> -- harmless editor metadata (last-used zoom
    and pan position), not part of the drawing, so removing it is safe
    rather than declaring a namespace for content nothing reads.
    """
    import re

    source = svg_path.read_text(encoding="utf-8")

    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', source)
    if not m:
        raise ValueError(f"no viewBox found in {svg_path}")
    view_w, view_h = float(m.group(1)), float(m.group(2))

    body_start = source.index(">", source.index("<svg")) + 1
    body_end = source.rindex("</svg>")
    inner = source[body_start:body_end]

    inner = re.sub(r"<sodipodi:namedview.*?/>", "", inner, flags=re.DOTALL)
    # Inkscape also drops per-path editor hints like sodipodi:nodetypes="..."
    # scattered through the drawing (path curve-node hints, irrelevant to
    # rendering) -- same undeclared-namespace problem, strip case by case.
    inner = re.sub(r'\s+(?:sodipodi|inkscape):[\w-]+="[^"]*"', "", inner)

    return inner, view_w, view_h


# --- generic SVG primitives ---------------------------------------------


