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

FONT_REGULAR = FONTS_DIR / "FiraSans-Regular.ttf"
FONT_BOLD = FONTS_DIR / "FiraSans-Bold.ttf"
FONT_FAMILY = "Fira Sans"

# Every generated SVG lives directly under img/, so the relative path back
# to fonts/ is always the same. If a step ever writes its SVG somewhere
# else, this constant has to move with it.
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
CATEGORY_COLORS = [
    "#3B1F4A",  # purple   -- house primary
    "#B8862E",  # gold     -- house secondary
    "#0E7A6E",  # teal
    "#A8451F",  # rust
    "#2A5F8A",  # slate blue
    "#5B5568",  # neutral (misc / footnote groups)
]


def ensure_dirs() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)


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
