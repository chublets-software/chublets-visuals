"""chublets-visuals: shared constants and render helpers.

Adapted from FDOx-squirrel/fdox-visuals' visuals_utils.py (same author, same
house pattern): identical render pipeline (resvg-py, vendored Fira Sans,
trim-to-content), different palette. No step imports rdflib/openpyxl/Pillow
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
BLOCK1_DIR = IMG_DIR / "block-1-codemeta-wikidata-datamodel"
BLOCK2_DIR = IMG_DIR / "block-2-fair4rs-chain"
BLOCK3_DIR = IMG_DIR / "block-3-four-step-pattern"
# Not one of the three numbered "blocks" -- system-level diagrams that sit
# above them (the consolidated architecture, and later the open-archaeo
# pipeline), so they get their own, non-numbered folder.
SYSTEM_ARCH_DIR = IMG_DIR / "system-architecture"
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

# Every generated SVG now lives one level under img/ (img/<block>/*.svg),
# so the relative path back to fonts/ is two levels up, not one. Changed
# 2026-09-10 together with the block-subfolder move -- see the comment on
# BLOCK1_DIR/BLOCK3_DIR above. If a step ever writes its SVG at a
# different depth, this constant has to move with it.
_FONT_REL_PREFIX = "../../fonts"

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


def wrap_text(text: str, max_chars: int = 26) -> list[str]:
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def shade(hex_color: str, factor: float) -> str:
    """Darken (factor<1) or lighten-toward-white (factor>1, capped) a hex colour."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r, g, b = (min(255, max(0, int(c * factor))) for c in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def tint(hex_color: str, white_ratio: float) -> str:
    """Mix a colour toward white by `white_ratio` (0 = unchanged, 1 = white)."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    mix = lambda c: int(c * (1 - white_ratio) + 255 * white_ratio)
    return f"#{mix(r):02X}{mix(g):02X}{mix(b):02X}"


def font_face_css() -> str:
    """@font-face block pointing at the two vendored weights.

    Vendored, not referenced: the repo carries its own copy of Fira Sans
    under fonts/, so a fresh clone renders identically without the font
    being installed on the machine that runs it.
    """
    return (
        "<style>"
        f'@font-face {{ font-family: "{FONT_FAMILY}"; '
        f'src: url("{_FONT_REL_PREFIX}/FiraSans-Regular.ttf"); font-weight: 400; }} '
        f'@font-face {{ font-family: "{FONT_FAMILY}"; '
        f'src: url("{_FONT_REL_PREFIX}/FiraSans-Bold.ttf"); font-weight: 700; }}'
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


def flatten_to_jpg(png_path: Path, jpg_path: Path, quality: int = 95) -> None:
    """Flatten a (possibly transparent) PNG onto white and save as JPEG."""
    from PIL import Image  # lazy, same reasoning as above

    with Image.open(png_path) as im:
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3])
        bg.save(jpg_path, "JPEG", quality=quality, subsampling=0)


def paste_raster(base_png_path: Path, asset_path: Path, x: int, y: int, w: int, h: int,
                  scale: float, circular: bool = False) -> None:
    """Composite a source raster asset (e.g. the chublets logo, under
    img/source/) onto an already-rendered PNG, at design-grid (x, y, w, h)
    scaled by the same `scale` factor the SVG was rasterised at. Call this
    BEFORE trim_transparent_border -- it needs the untrimmed canvas, whose
    pixel coordinates are known in advance from the design grid; trimming
    first would make (x, y) ambiguous.
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


# --- generic SVG primitives ---------------------------------------------


def arrow_marker(marker_id: str = "arrow", color: str = MUTED) -> str:
    return (
        f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
    )


def arrow_line(x1: float, y1: float, x2: float, y2: float, color: str = MUTED,
               width: float = 4, marker_id: str = "arrow") -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{width}" marker-end="url(#{marker_id})"/>'
    )


def elbow_path(points: list[tuple[float, float]], color: str = MUTED,
               width: float = 4, marker_id: str = "arrow") -> str:
    """A multi-segment orthogonal/angled connector ending in an arrowhead."""
    pts = " ".join(f"{x},{y}" for x, y in points)
    return (
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linejoin="round" marker-end="url(#{marker_id})"/>'
    )


def open_triangle(x1: float, y1: float, x2: float, y2: float, color: str = "white",
                   width: float = 12) -> str:
    """An open (unfilled) chevron arrowhead pointing from (x1,y1) toward
    (x2,y2), used for inheritance-style connectors (UML "is-a").
    """
    import math

    ang = math.atan2(y2 - y1, x2 - x1)
    size = 26
    spread = 0.5
    ax1 = x2 - size * math.cos(ang - spread)
    ay1 = y2 - size * math.sin(ang - spread)
    ax2 = x2 - size * math.cos(ang + spread)
    ay2 = y2 - size * math.sin(ang + spread)
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3"/>'
        f'<polyline points="{ax1:.1f},{ay1:.1f} {x2},{y2} {ax2:.1f},{ay2:.1f}" '
        f'fill="white" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>'
    )


def label_box(x: float, y: float, w: float, h: float, lines: list[tuple[str, int, float]],
              fill: str = "white", stroke: str = INK, text_color: str = INK, radius: float = 10) -> str:
    """A rounded rectangle centred on (x + w/2, y + h/2) holding one or more
    text lines, each given as (text, font-weight, font-size), vertically
    centred as a block. Used by flow-style diagrams (S4b curate/export).
    """
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    n = len(lines)
    line_h = 30
    start_y = y + h / 2 - (n - 1) * line_h / 2 + 8
    for i, (text, weight, size) in enumerate(lines):
        out += (
            f'<text x="{x + w/2}" y="{start_y + i*line_h}" text-anchor="middle" font-family="{FONT_FAMILY}" '
            f'font-weight="{weight}" font-size="{size}" fill="{text_color}">{esc(text)}</text>'
        )
    return out


def four_step_icon(step_idx: int, color: str) -> str:
    """The four chublets.software step glyphs (Ingest/Model/Curate &
    Link/Export & Publish), centred on (0, 0) in a local -90..90-ish
    coordinate space. Shared by step_pattern.py (badges) and any S4b
    detail diagram that wants the same glyph next to its own content, so
    the icon is drawn once, not redrawn slightly differently per file (A3).
    """
    sw = 6
    if step_idx == 0:  # Ingest -- three sources converging into one point
        pts = [(-56, -50), (0, -64), (56, -50)]
        lines = "".join(
            f'<line x1="{x}" y1="{y}" x2="0" y2="22" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>' for x, y in pts
        )
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="14" fill="white" stroke="{color}" stroke-width="{sw}"/>' for x, y in pts)
        return lines + dots + f'<circle cx="0" cy="22" r="26" fill="{color}"/>'
    if step_idx == 1:  # Model -- a small three-node property graph
        pts = [(0, -58), (54, 38), (-54, 38)]
        edges = [(0, 1), (1, 2), (2, 0)]
        lines = "".join(
            f'<line x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>' for a, b in edges
        )
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="17" fill="{color}"/>' for x, y in pts)
        return lines + dots
    if step_idx == 2:  # Curate & Link -- a checkmark
        return (
            f'<polyline points="-40,2 -10,34 48,-40" fill="none" stroke="{color}" '
            f'stroke-width="{sw+4}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    # Export & Publish -- an arrow leaving an open container
    bracket = (
        f'<polyline points="6,-52 -34,-52 -34,52 6,52" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    arrow = (
        f'<line x1="-14" y1="0" x2="52" y2="0" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
        f'<polyline points="30,-20 56,0 30,20" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return bracket + arrow


def fair4rs_icon(idx: int, color: str) -> str:
    """The four FAIR4RS principle glyphs (Findable/Accessible/
    Interoperable/Reusable), same local -60..60-ish coordinate space and
    stroke weight as four_step_icon() so the two badge chains read as one
    family despite being separate diagrams (fdox-visuals keeps its
    four-step and four-purpose icon sets in separate files too; this
    mirrors that rather than forcing one shared icon function to serve
    two different meanings).
    """
    sw = 6
    if idx == 0:  # Findable -- a magnifying glass
        return (
            f'<circle cx="-8" cy="-8" r="32" fill="none" stroke="{color}" stroke-width="{sw}"/>'
            f'<line x1="15" y1="15" x2="46" y2="46" stroke="{color}" stroke-width="{sw+2}" stroke-linecap="round"/>'
        )
    if idx == 1:  # Accessible -- an open padlock
        body = f'<rect x="-30" y="2" width="60" height="46" rx="8" fill="{color}"/>'
        shackle = (
            f'<path d="M -14,2 V -16 A 14 14 0 0 1 14,-30 A 14 14 0 0 1 28,-16 V -8" '
            f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
        )
        return shackle + body
    if idx == 2:  # Interoperable -- two linked rings
        return (
            f'<circle cx="-18" cy="0" r="30" fill="none" stroke="{color}" stroke-width="{sw}"/>'
            f'<circle cx="18" cy="0" r="30" fill="none" stroke="{color}" stroke-width="{sw}"/>'
        )
    # Reusable -- a circular reuse arrow (two opposing arcs)
    arc1 = (
        f'<path d="M -32,-6 A 34 34 0 0 1 14,-33" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round"/>'
        f'<polyline points="0,-38 16,-33 8,-18" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    arc2 = (
        f'<path d="M 32,6 A 34 34 0 0 1 -14,33" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round"/>'
        f'<polyline points="0,38 -16,33 -8,18" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return arc1 + arc2


def step_header(step_idx: int, step: dict, x: float, y: float, r: float = 45,
                 icon_fn=None, prefix: str = "Step ") -> tuple[str, float]:
    """A small version of an S4/Block-2 badge (icon only, no number tag --
    the text next to it already says which step) plus a "Step N -- Title"
    or "F -- Title" label, used as a consistent header on every detail
    diagram (Flo, 2026-09-10: "ich verstehe bei der Bezeichnung nicht
    welcher step es ist" / fdox-visuals keeps its step badge visible
    everywhere). Reuses the badge's own icon function at a smaller scale
    rather than drawing a second icon set (A3).

    `icon_fn` defaults to four_step_icon (Block 3); pass fair4rs_icon for
    Block 2 diagrams. `prefix` goes in front of `step["num"]` in the
    label -- "Step " for Block 3 (numeric), "" for Block 2 (the FAIR
    letters read fine on their own, "Step F" would not).

    Returns (svg_markup, y) where y is the top of the first content row
    below the header, so a step file can do
    `header_svg, content_y = step_header(...)` and lay out from there.
    """
    if icon_fn is None:
        icon_fn = four_step_icon
    color = step["color"]
    scale = r / 150
    fill = tint(color, 0.88)
    cx, cy = x + r, y + r
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="4"/>'
    out += f'<g transform="translate({cx},{cy}) scale({scale:.4f})">{icon_fn(step_idx, color)}</g>'
    title = " ".join(step["title"])
    out += (
        f'<text x="{x + 2*r + 22}" y="{cy+9}" text-anchor="start" font-family="{FONT_FAMILY}" '
        f'font-weight="700" font-size="26" fill="{INK}">{prefix}{step["num"]} \u2014 {esc(title)}</text>'
    )
    return out, y + 2 * r + 34
