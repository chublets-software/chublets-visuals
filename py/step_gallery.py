"""S9c -- HTML overview for GitHub Pages (docs/).

Writes two self-contained pages:

  * `docs/index.html`  every graphic under img/ (SVG and PNG download) with its
    entry from captions.yaml (caption, alt text, sources, licence), grouped by
    folder;
  * `docs/tables.html`  every table of the data model (the same `tables_data`
    objects the LaTeX appendix is built from) as a sortable, filterable HTML
    table, with CSV and `.tex` downloads.

The pages need no network: no CDN, no web font, no tracking. Graphics are copied
to docs/img/ and the downloads to docs/data/, because GitHub Pages serves only
the folder it is pointed at (Settings -> Pages -> Deploy from a branch -> main,
/docs). Everything is deterministic (no clock, sorted order, copied bytes), so a
second run changes nothing.

Produces: docs/index.html, docs/tables.html, docs/.nojekyll, docs/img/**, docs/fonts/*.ttf,
          docs/data/*.csv, docs/data/*.tex
Runnable standalone: `python py/step_gallery.py`
"""

from __future__ import annotations

import csv
import html
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import model_data  # noqa: E402
import tables_data  # noqa: E402
from tables_data import Row, Sub, Table  # noqa: E402
from visuals_utils import IMG_DIR, ROOT  # noqa: E402

DOCS = ROOT / "docs"
TEX_DIR = ROOT / "tex"
DEFAULT_LICENCE = captions.DEFAULT_LICENCE


# --------------------------------------------------------------------------
def _e(text: object) -> str:
    return html.escape(str(text), quote=True)


def _flat(table: Table) -> tuple[list[str], list[tuple[tuple[str, ...], bool]]]:
    """Header and rows; a Sub row becomes a leading 'Topic' column on the rows below it."""
    has_sub = any(isinstance(r, Sub) for r in table.rows)
    header = [c.title for c in table.cols]
    out: list[tuple[tuple[str, ...], bool]] = []
    topic = ""
    for r in table.rows:
        if isinstance(r, Sub):
            topic = r.text.rsplit(" (", 1)[0]
            continue
        out.append(((topic,) + r.cells if has_sub else r.cells, r.total))
    return (["Topic"] + header if has_sub else header), out


def _write_csv(table: Table) -> None:
    header, rows = _flat(table)
    path = DOCS / "data" / f"{table.name}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for cells, _ in rows:
            w.writerow(cells)


def _table_html(table: Table) -> str:
    header, rows = _flat(table)
    offset = len(header) - len(table.cols)
    aligns = ["l"] * offset + [c.align for c in table.cols]
    th = "".join(
        f'<th data-col="{i}" class="{"num" if a == "r" else ""}" role="columnheader" tabindex="0" aria-sort="none">{_e(h)}</th>'
        for i, (h, a) in enumerate(zip(header, aligns))
    )
    body = []
    for cells, total in rows:
        tds = "".join(f'<td class="{"num" if a == "r" else ""}">{_e(c)}</td>' for c, a in zip(cells, aligns))
        body.append(f'<tr class="total">{tds}</tr>' if total else f"<tr>{tds}</tr>")
    tex = f"data/{table.name}.tex"
    return f"""
<section class="tbl" id="{_e(table.name)}" data-title="{_e(table.title)}">
  <h3>{_e(table.title)}</h3>
  <p class="caption">{_e(table.caption)}</p>
  <div class="tools">
    <input type="search" class="filter" placeholder="Filter rows" aria-label="Filter rows of {_e(table.title)}">
    <span class="count" aria-live="polite"></span>
    <span class="dl"><a href="data/{_e(table.name)}.csv" download>CSV</a> <a href="{_e(tex)}" download>LaTeX</a></span>
  </div>
  <div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>
{chr(10).join(body)}
  </tbody></table></div>
  <p class="src">Sources: {_e(", ".join(table.sources) or "vendored model tables")}</p>
</section>"""


# --------------------------------------------------------------------------
# Themes of the overview pages: id -> (title, one-line description). Order = order on the page.
THEMES = {
    "vocabularies": ("Vocabularies and evidence", "CodeMeta, Wikidata properties and the evidence the model rests on."),
    "model": ("Data model", "Classes, properties, statements and how a chublet is stored."),
    "pipeline": ("Four-step pipeline", "Ingest, Model, Curate & Link, Export & Publish."),
    "fair": ("FAIR4RS", "How the model meets Findable, Accessible, Interoperable and Reusable."),
    "open-archaeo": ("open-archaeo workflow", "From the open-archaeo list to Wikidata."),
    "architecture": ("Architecture and talk", "The whole system at a glance, and the closing slide."),
}
GRAPHIC_THEME = {
    "chublets-codemeta-overview": "vocabularies", "chublets-wikidata-properties-overview": "vocabularies",
    "chublets-codemeta-wikidata-crosswalk": "vocabularies", "property-vocabulary-overlap": "vocabularies",
    "codemeta-coverage": "vocabularies", "model-evidence-base": "vocabularies",
    "chublets-wikibase-datamodel": "model", "class-tree": "model", "property-origin": "model", "property-topics": "model",
    "entity-overview": "model", "property-metadata-layer": "model", "chublet-item": "model",
    "statement-provenance": "model", "chublet-identity": "model", "wikibase-bootstrap": "model",
    "static-vs-federation": "model",
    "chublets-software-architecture": "architecture", "chublets-talk-closing": "architecture",
}
TABLE_THEME = {
    "table-codemeta-terms": "vocabularies", "table-wikidata-groups": "vocabularies",
    "table-datacite-evidence": "vocabularies", "table-evidence-sources": "vocabularies",
    "table-property-evidence": "vocabularies",
}


def theme_of_graphic(stem: str) -> str:
    if stem in GRAPHIC_THEME:
        return GRAPHIC_THEME[stem]
    if stem.startswith(("chublets-step-", "chublets-four-step", "step-")):
        return "pipeline"
    if stem.startswith(("chublets-fair", "fair-")):
        return "fair"
    if stem.startswith("open-archaeo-"):
        return "open-archaeo"
    raise RuntimeError(f"graphic '{stem}' has no theme; add it to GRAPHIC_THEME in step_gallery.py")


def _chips(counts: dict[str, int]) -> str:
    out = ['<div class="chips" role="group" aria-label="Filter by theme">']
    out.append(f'<button type="button" class="chip" data-theme="" aria-pressed="true">All <span>{sum(counts.values())}</span></button>')
    for tid, (title, desc) in THEMES.items():
        if counts.get(tid):
            out.append(f'<button type="button" class="chip" data-theme="{tid}" aria-pressed="false" title="{_e(desc)}">{_e(title)} <span>{counts[tid]}</span></button>')
    out.append("</div>")
    return "".join(out)


def _group_head(tid: str) -> str:
    title, desc = THEMES[tid]
    return f'<div class="grphead"><h3 class="grp" id="theme-{tid}">{_e(title)}</h3><p class="caption">{_e(desc)}</p></div>'


def _tables_grouped(tables) -> str:
    by: dict[str, list] = {t: [] for t in THEMES}
    for t in tables:
        by[TABLE_THEME.get(t.name, "model")].append(t)
    out = [_chips({k: len(v) for k, v in by.items()})]
    for tid, ts in by.items():
        if ts:
            out.append(f'<div class="grp" data-theme="{tid}">{_group_head(tid)}' + "".join(_table_html(t) for t in ts) + "</div>")
    return "".join(out)


def _graphics(fact: dict[str, object]) -> tuple[str, int, int]:
    """(HTML of the graphics section, number of graphics, number with a caption)."""
    entries = captions.load()
    skip = IMG_DIR / "source"
    svgs = sorted(p for p in IMG_DIR.rglob("*.svg") if skip not in p.parents)
    img_out = DOCS / "img"
    if img_out.exists():
        shutil.rmtree(img_out)
    groups: dict[str, list[Path]] = {t: [] for t in THEMES}
    for p in svgs:
        groups[theme_of_graphic(p.stem)].append(p)
        for ext in (".svg", ".png"):
            src = p.with_suffix(ext)
            if src.is_file():
                dst = img_out / src.relative_to(IMG_DIR)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
    counts = {t: len(ps) for t, ps in groups.items()}
    parts: list[str] = [_chips(counts)]
    with_caption = 0
    for tid, ps in groups.items():
        if not ps:
            continue
        parts.append(f'<div class="grp" data-theme="{tid}">{_group_head(tid)}<div class="grid">')
        for p in ps:
            rel = p.relative_to(IMG_DIR).as_posix()
            stem = p.stem
            entry = captions.render(stem, **fact) if stem in entries else {}
            with_caption += bool(entry)
            alt = entry.get("alt") or stem.replace("-", " ")
            cap = entry.get("caption") or "No caption yet (see captions.yaml)."
            lic = entry.get("licence") or DEFAULT_LICENCE
            srcs = ", ".join(entry.get("sources") or [])
            png = (IMG_DIR / rel).with_suffix(".png").is_file()
            # an SVG shown through <img> cannot load fonts, so the PNG (rendered with Fira Sans) is the thumbnail
            thumb = Path(rel).with_suffix(".png").as_posix() if png else rel
            links = f'<a href="img/{_e(rel)}" download>SVG</a>' + (f' <a href="img/{_e(Path(rel).with_suffix(".png").as_posix())}" download>PNG</a>' if png else "")
            parts.append(
                f'<figure class="card" data-name="{_e(stem)} {_e(cap)}">'
                f'<a class="thumb" href="img/{_e(rel)}"><img loading="lazy" src="img/{_e(thumb)}" alt="{_e(alt)}"></a>'
                f'<figcaption><strong>{_e(stem)}</strong>'
                + (f'<details class="cap"><summary>Caption</summary><p>{_e(cap)}</p></details>' if entry else f'<span class="cap missing">{_e(cap)}</span>')
                + f'<span class="meta">{_e(captions.CREATOR)}, {_e(lic)}{" · " + _e(srcs) if srcs else ""} · {links}</span></figcaption></figure>'
            )
        parts.append("</div></div>")
    return "\n".join(parts), len(svgs), with_caption


CSS = """
:root{--bg:#fff;--fg:#1e293b;--mut:#64748b;--line:#e2e8f0;--card:#f8fafc;--acc:#4c1d95;--hl:#fef3c7}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0f172a;--fg:#e2e8f0;--mut:#94a3b8;--line:#334155;--card:#1e293b;--acc:#c4b5fd;--hl:#422006}}
:root[data-theme=dark]{--bg:#0f172a;--fg:#e2e8f0;--mut:#94a3b8;--line:#334155;--card:#1e293b;--acc:#c4b5fd;--hl:#422006}
section.tbl,h2{scroll-margin-top:64px}*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 "Fira Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--acc)}header,main,footer{max-width:1200px;margin:0 auto;padding:0 16px}
header{padding-top:28px}h1{margin:0 0 4px;font-size:1.7rem}header p{margin:0;color:var(--mut);max-width:70ch}
nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);margin-top:16px;z-index:5}
nav .in{max-width:1200px;margin:0 auto;padding:8px 16px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
nav a[aria-current=page]{font-weight:700;color:var(--fg);text-decoration:none;border-bottom:2px solid var(--acc)}
nav input{flex:1;min-width:180px;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
nav button{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:6px 10px;cursor:pointer}
h2{margin:32px 0 4px;font-size:1.3rem}h3{margin:20px 0 6px;font-size:1.05rem}h3.grp{color:var(--fg);font-weight:600;text-transform:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}
.card{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
.card .thumb{display:flex;align-items:center;justify-content:center;background:#fff;min-height:160px;padding:8px;border-bottom:1px solid var(--line)}
.card img{max-width:100%;height:auto;max-height:260px}
figcaption{padding:10px 12px;display:flex;flex-direction:column;gap:4px;font-size:.9rem}
.cap summary{cursor:pointer;color:var(--acc)}.cap p{margin:6px 0 0}.cap.missing{color:var(--mut);font-style:italic}.meta,.src,.count{color:var(--mut);font-size:.82rem}
.caption{max-width:90ch;font-size:.92rem;margin:0 0 8px}
.tools{display:flex;gap:12px;align-items:center;margin:6px 0;flex-wrap:wrap}.tools .filter{padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);min-width:200px}
.scroll{overflow:auto;border:1px solid var(--line);border-radius:6px;max-height:70vh}
table{border-collapse:collapse;width:100%;font-size:.86rem}th,td{padding:4px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--card);cursor:pointer;white-space:nowrap;user-select:none}th[aria-sort=ascending]::after{content:" \\25B2";font-size:.7em}th[aria-sort=descending]::after{content:" \\25BC";font-size:.7em}
.num{text-align:right;font-variant-numeric:tabular-nums}tr.total td{font-weight:700;background:var(--card)}tr:hover td{background:var(--hl)}tr[hidden]{display:none}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.chip{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:5px 12px;cursor:pointer;font:inherit;font-size:.9rem}
.chip span{color:var(--mut);margin-left:4px}.chip[aria-pressed=true]{background:var(--acc);color:var(--bg);border-color:var(--acc)}.chip[aria-pressed=true] span{color:inherit}
.grphead{margin-top:24px}.grphead h3{margin-bottom:0}.grphead .caption{margin:0 0 8px;color:var(--mut)}
footer{padding:32px 16px 48px;color:var(--mut);font-size:.85rem}
"""

JS = """
(function(){
 var root=document.documentElement;try{var t=localStorage.getItem('theme');if(t)root.setAttribute('data-theme',t)}catch(e){}
 document.getElementById('theme').addEventListener('click',function(){
  var dark=root.getAttribute('data-theme')?root.getAttribute('data-theme')==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
  var n=dark?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){}});
 function norm(s){return s.toLowerCase()}
 var q=document.getElementById('q');
 var theme='';
 function applyAll(){var v=norm(q.value);
  document.querySelectorAll('.card').forEach(function(c){c.hidden=v&&norm(c.dataset.name).indexOf(v)<0});
  document.querySelectorAll('section.tbl').forEach(function(s){filterTable(s,v+' '+norm(s.querySelector('.filter').value))});
  document.querySelectorAll('div.grp').forEach(function(d){
   var off=theme&&d.dataset.theme!==theme,any=d.querySelector('.card:not([hidden])')||d.querySelector('section.tbl');
   d.hidden=off||!any})}
 document.querySelectorAll('.chip').forEach(function(b){b.addEventListener('click',function(){
  theme=b.dataset.theme;document.querySelectorAll('.chip').forEach(function(o){o.setAttribute('aria-pressed',o===b?'true':'false')});applyAll()})});
 function filterTable(s,extra){var terms=extra.split(/\\s+/).filter(Boolean),n=0,tot=0;
  s.querySelectorAll('tbody tr').forEach(function(r){var txt=norm(r.textContent),ok=terms.every(function(t){return txt.indexOf(t)>=0});r.hidden=!ok;tot++;if(ok)n++});
  s.querySelector('.count').textContent=n+' of '+tot+' rows'}
 q.addEventListener('input',applyAll);
 document.querySelectorAll('section.tbl').forEach(function(s){
  var f=s.querySelector('.filter');f.addEventListener('input',applyAll);
  var tb=s.querySelector('tbody');
  s.querySelectorAll('th').forEach(function(th){function go(){
    var i=+th.dataset.col,asc=th.getAttribute('aria-sort')!=='ascending';
    s.querySelectorAll('th').forEach(function(o){o.setAttribute('aria-sort','none')});th.setAttribute('aria-sort',asc?'ascending':'descending');
    var rows=[].slice.call(tb.rows),tot=rows.filter(function(r){return r.classList.contains('total')}),data=rows.filter(function(r){return!r.classList.contains('total')});
    function val(r){var x=r.cells[i].textContent.trim();var n=parseFloat(x);return x===''||x==='--'?null:(isNaN(n)||!/^[-0-9.]+$/.test(x)?x.toLowerCase():n)}
    data.sort(function(a,b){var x=val(a),y=val(b);if(x===y)return 0;if(x===null)return 1;if(y===null)return -1;
      var d=(typeof x==='number'&&typeof y==='number')?x-y:String(x).localeCompare(String(y),undefined,{numeric:true});return asc?d:-d});
    data.concat(tot).forEach(function(r){tb.appendChild(r)})}
   th.addEventListener('click',go);th.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}})});
 });
 applyAll();
})();
"""


def _page(*, title: str, active: str, intro: str, body: str, search: str) -> str:
    def nav(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(title)}</title>
<meta name="description" content="Graphics and tables of the chublets Wikibase data model: classes, properties and their origin in Wikidata, CodeMeta, DataCite and chublets additions.">
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>chublets visuals</h1>
  <p>{intro}</p>
</header>
<nav><div class="in">{nav("index.html", "Graphics", "graphics")}{nav("tables.html", "Tables", "tables")}
<input id="q" type="search" placeholder="{_e(search)}" aria-label="{_e(search)}">
<button id="theme" type="button" aria-label="Toggle light and dark">Light / dark</button></div></nav>
<main>
{body}
</main>
<footer>Graphics and tables: {captions.CREATOR}, {DEFAULT_LICENCE}. Code: MIT. Built by <code>python main.py</code> from the snapshot recorded in <code>data/raw/SNAPSHOT.md</code>.</footer>
<script>{JS}</script>
</body>
</html>
"""


def run(strict: bool = False) -> list[str]:
    M = model_data.load()
    import topics as topics_mod

    fact = model_data.caption_facts(M, len(topics_mod.load()))
    tables = tables_data.build()

    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    graphics_html, n_gfx, n_cap = _graphics(fact)

    # the SVGs refer to ../fonts/ (or ../../fonts/) next to them, so the fonts go to docs/fonts/
    fonts_out = DOCS / "fonts"
    if fonts_out.exists():
        shutil.rmtree(fonts_out)
    fonts_out.mkdir(parents=True)
    for ttf in sorted((ROOT / "fonts").glob("*.ttf")):
        shutil.copyfile(ttf, fonts_out / ttf.name)

    data_out = DOCS / "data"
    if data_out.exists():
        shutil.rmtree(data_out)
    for t in tables:
        _write_csv(t)
        src = TEX_DIR / f"{t.name}.tex"
        if not src.is_file():
            raise RuntimeError(f"{src} is missing; run the 'tables' step first")
        shutil.copyfile(src, data_out / f"{t.name}.tex")

    intro = (
        f"Graphics and tables of the chublets Wikibase data model: {fact['n_classes']} classes and {fact['n_props']} properties, "
        f"grouped into {fact['n_topics']} topics, with their origin in Wikidata, CodeMeta, DataCite (as supporting evidence) "
        f"and chublets additions. Every number is read from the vendored model tables."
    )
    gfx_body = (
        f'<h2 id="graphics">Graphics <small class="count">{n_gfx} graphics, {n_cap} with a caption</small></h2>\n'
        f"{graphics_html}"
    )
    toc = " &middot; ".join(f'<a href="#{_e(t.name)}">{_e(t.title)}</a>' for t in tables)
    tbl_body = (
        f'<h2 id="tables">Tables <small class="count">{len(tables)} tables</small></h2>\n'
        f'<p class="caption">The same tables are in the LaTeX appendix (<code>tex/</code>). Click a column header to sort; '
        f"the search above filters all tables at once. {toc}</p>\n"
        + _tables_grouped(tables)
    )
    (DOCS / "index.html").write_text(
        _page(title="chublets visuals", active="graphics", intro=intro, body=gfx_body, search="Search graphics"),
        encoding="utf-8", newline="\n")
    (DOCS / "tables.html").write_text(
        _page(title="chublets visuals: tables", active="tables", intro=intro, body=tbl_body, search="Search all tables"),
        encoding="utf-8", newline="\n")
    return [
        f"docs/index.html: {n_gfx} graphics ({n_cap} with a caption)",
        f"docs/tables.html: {len(tables)} tables; docs/data: {len(tables)} CSV and {len(tables)} LaTeX downloads",
    ]


if __name__ == "__main__":
    for line in run():
        print(line)
