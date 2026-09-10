# PRIMER — chublets-visuals

Arbeitsplan für `chublets-visuals`: die Grafik-Werkstatt für chublets.software.
Ein `main.py`, das reine Python-Skripte fährt und SVG/PNG für Vorträge (aktuell:
CAA JCM DE-NL/FL, 16.–18.09.2026, Münster, Slot "Code is Data, Too — Nuggets,
Minions and Crows in a FAIR4RS Marketplace for Computational Archaeology"),
Paper-Abbildungen (deRSE26/ECEASST) und READMEs erzeugt — deterministisch, ohne
externe CLI-Tools, damit `pip install -r requirements.txt` reicht. Schwesterrepo
zu `FDOx-squirrel/fdox-visuals` (gleicher Autor, gleiches Hausmuster), eigene
Palette.

**Ort.** `https://github.com/chublets-software/chublets-visuals/blob/main/PRIMER.md`
(Vorschlag, Repo noch nicht angelegt — siehe A4).

**So wird es benutzt.** Wird vollständig zu Beginn jedes Chats hochgeladen.
Danach genügt "wir machen S4". Teil A gilt immer, Teil B ist die Übersicht,
Teil C beschreibt den einzelnen Schritt.

---

# Teil A — Immer gültig

## A1. Ausgangslage

Ausgangspunkt war die bestehende 29-Folien-Präsentation
`JCM2026_Muenster_chublets.software.pdf`: F1–F24 (Framing, Historie,
open-archaeo, RSE-Stack, FDOx, chublets-Konzept) bleiben unverändert bestehen.
Ab F25 wird neu strukturiert und alles als eigenständige, paper-taugliche
Grafik-Bibliothek neu per Python erzeugt statt als Google-Slides-Screenshot
wiederverwendet — die Grafiken werden zufällig auch im Talk benutzt, sind aber
nicht auf ihn beschränkt.

**Befunde (geprüft 2026-09-10):**

1. **Die Crosswalk-xlsx hat Sub-Header-Zeilen, die kein neues CodeMeta-Type-
   Segment einleiten.** Neben den vier echten Abschnittsmarkierungen
   ("Properties from Thing -> CreativeWork -> SoftwareApplication" etc., deren
   letztes Segment einer der vier Typnamen ist) stehen im `Thing`-Abschnitt
   zwei weitere Zeilen mit demselben `Range`-leer-Muster, aber einem Tail, der
   kein CodeMeta-Typ ist ("... -> WebPage", "... -> Codemeta:Software"). Erster
   Parser-Versuch hat diese als Property-Zeilen mitgezählt (sichtbar als
   Fließtext-Zeile mitten in der `Thing`-Box). Fix: nur Header, deren
   `->`-Tail einer von `{Thing, CreativeWork, SoftwareSourceCode,
   SoftwareApplication}` ist, wechselt den aktuellen Abschnitt; jede andere
   Zeile mit leerem `Range` wird als Sub-Divider übersprungen, ohne den
   Abschnitt zu wechseln (`py/crosswalk_data.py`).
2. **CodeMeta-Crosswalk, gezählt aus der xlsx:** 68 Property-Zeilen über die
   vier Typen (`Thing` 20, `CreativeWork` 22, `SoftwareSourceCode` 5,
   `SoftwareApplication` 21), davon 33 mit einer erkennbaren Wikidata-PID in
   Spalte F (Regex `P\d+`, auch aus "corrected: P178 - developer"-Freitext
   extrahiert), 35 ungemappt. `relatedLink` kommt als CodeMeta-Property-Name
   zweimal vor (zwei unterschiedliche Wikidata-Korrekturen, P973 und P11201) —
   das ist echte Quelldatenlage, kein Duplikat-Bug.
3. **Die Wikidata-WikiProject-Properties-Seite liegt nur als PDF vor, keine
   maschinenlesbare Tabelle.** Neu-Scrapen bei jedem Build wäre fragil für
   keinen Gewinn (mehrseitiges PDF, keine stabile Struktur). Stattdessen von
   Hand in `data/raw/wikidata-software-properties.csv` übertragen (47 Zeilen,
   5 Kategorien, davon 46 mit echter PID + 1 Sammelzeile "12 more
   package-registry IDs" für nicht einzeln aufgeführte Registry-Properties)
   und als versionierte Quelle behandelt wie jede andere `data/raw`-Datei.
4. **Hausfarben aus dem chublets-Logo gesampelt** (`chublets_software_logo.png`,
   `PIL.Image.getcolors`): dominantes Lila clustert um `#32173D`/`#341A3F`,
   dominantes Gold um `#D7A141`/`#B8862E`. Gewählt: `CHUBLETS_PURPLE =
   #3B1F4A`, `CHUBLETS_GOLD = #B8862E` — beide leicht Richtung Lesbarkeit auf
   hellem Grund nachjustiert, nicht die reinen Pixelwerte.
5. **Ein Force-Directed-Graph ist als Diagrammtyp verworfen worden.** Die
   ursprüngliche F25-Grafik (codemeta.github.io-Term-Graph) ist ein
   Screenshot eines externen, physik-basierten Layouts — nicht Byte-für-Byte
   reproduzierbar und damit unvereinbar mit der Determinismus-Regel unten.
   Ersetzt durch ein Klassendiagramm (Thing → CreativeWork →
   {SoftwareSourceCode, SoftwareApplication}), das exakt dieselbe
   Eigenschaftsliste zeigt, aber deterministisch layoutet.
6. **Font- und Renderpipeline von `fdox-visuals` 1:1 übernommen**, ohne
   erneute Prüfung der dort bereits dokumentierten Befunde (resvg-py statt
   cairosvg wegen fehlender System-libcairo unter Windows, Fira Sans
   vendored, `trim_transparent_border`, Google-Slides-25-Megapixel-Grenze) —
   siehe `fdox-visuals/PRIMER.md` A1.1–A1.6 für die Herleitung.

## A2. Zielbild

```
data/raw/*.xlsx, *.csv   echte Quelldaten (Crosswalk, Property-Listen)
      |
      v  py/step_*.py    Geometrie + Text, keine Renderlogik
      |
      v  main.py
img/*.svg                 Quelle, versioniert
      |
      v  resvg-py (in-process)
img/*.png                 fertige Grafik fuer Folien/Paper/README, transparenter Hintergrund
```

Eigenschaften, an denen sich das Ergebnis messen lassen muss:

- Zweimal `python main.py` hintereinander → `git status` bleibt leer.
- Jede PNG hat transparenten Hintergrund, exakt ≤10px Rand, und bleibt unter
  Google Slides' 25-Megapixel-Grenze.
- Farbe und Typografie kommen ausschließlich aus `py/visuals_utils.py` — kein
  Hex-Code wiederholt sich hart codiert in einem `step_*.py`.
- Jede Zahl, die in einer Grafik auftaucht (Property-Anzahl, Mapping-Quote),
  ist zur Laufzeit aus `data/raw/` gelesen, nicht von Hand eingetragen — die
  Grafik kann also nie stillschweigend von ihrer eigenen Quelle abweichen.

## A3. Querschnittsregeln

- Rohdaten liegen unverändert unter `data/raw/`, read-only. Was ein Skript
  daraus macht, geht nach `img/`.
- Wiederverwendung heißt Kopieren, nicht Referenzieren — Ausnahme: die
  Fira-Sans-Schriftdateien, 1:1 aus `fdox-visuals/fonts/` übernommen (gleiche
  SIL-OFL-Lizenz, gleicher Zweck).
- **Keine Uhr im Ergebnis.** Kein `datetime.now()` in einem Generator.
- **Zweimal laufen lassen, `git status` muss leer bleiben.**
- Netzwerkzugriff ist in diesem Repo aktuell nirgends nötig (alle Quellen sind
  bereits lokale Dateien unter `data/raw/`) — sollte ein späterer Schritt live
  von einer URL lesen (z. B. eine aktuelle Wikidata-Abfrage), bekommt er einen
  eigenen, nicht im Default-Lauf enthaltenen Schritt.
- Sprache/Plattform: PRIMER.md Deutsch, alles andere (Code, Kommentare,
  README, Commit-Messages) Englisch. Windows ist Referenzplattform, Befehle
  einzeilig für `cmd`.

## A4. Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Renderpipeline | resvg-py + vendored Fira Sans, identisch zu fdox-visuals | 2026-09-10 |
| Hausfarben | `CHUBLETS_PURPLE #3B1F4A`, `CHUBLETS_GOLD #B8862E`, aus dem Logo gesampelt | 2026-09-10 |
| Kategorie-Palette | 6 Farben (purple, gold, teal, rust, slate blue, neutral grau) für gruppierte Diagramme | 2026-09-10 |
| CodeMeta-Übersicht | Klassendiagramm statt Force-Directed-Graph (Determinismus) | 2026-09-10 |
| Wikidata-Property-Quelle | von Hand kuratierte CSV statt Live-PDF-Scraping | 2026-09-10 |
| Namensschema | `chublets-<thema>` je Grafik, `img/chublets-<thema>.svg/.png` | 2026-09-10 |
| Repo-Ziel | `chublets-software/chublets-visuals` | Vorschlag, 2026-09-10 |
| Vier-Schritte-Namen (Block 3) | Ingest → Model → Curate & Link → Export & Publish | Vorschlag, 2026-09-10 |
| FAIR4RS-Mechanismen (Block 2) | Findable: Q-IDs + nfdi.software-Indexierung; Accessible: Wikibase-API/SPARQL; Interoperable: CodeMeta als Pivot; Reusable: Lizenz-/Provenienz-Statements | Vorschlag, 2026-09-10 |

## A5. Was in welchem Chat hochgeladen wird

Zu Beginn jedes Chats: `PRIMER.md` plus ein Bundle aus Quellen und Code (kein
`img/`, kein `.venv/`). Unter Windows:

```cmd
powershell -Command "Compress-Archive -Path PRIMER.md,py,data\raw,fonts,main.py,requirements.txt,CITATION.cff,LICENSE,README.md,.gitignore -DestinationPath chublets-visuals-bundle.zip -Force"
```

Nicht hochladen: `img/*.png`/`img/*.svg` (werden neu gebaut), `__pycache__/`,
`.git/`, `img/pipeline_report.txt`.

---

# Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen: Palette, Font, Namensschema | chublets-visuals | — | erledigt 2026-09-10 |
| S1 | Skeleton: `main.py`, `visuals_utils.py`, Lizenz/Citation/README | chublets-visuals | S0 | erledigt 2026-09-10 |
| S2 | Block 1: CodeMeta / Wikidata / chublets-Datamodel (4 Grafiken) | chublets-visuals | S1 | erledigt 2026-09-10 |
| S3 | Block 2: FAIR4RS-Kette (Banner + 4 Detailgrafiken F/A/I/R) | chublets-visuals | S1 | offen |
| S4 | Block 3: chublets.software Four-Step-Pattern (Banner + 4 Detailgrafiken) | chublets-visuals | S1 | offen |
| S5 | System Architecture (konsolidiertes Klassendiagramm/Workflow/Output) | chublets-visuals | S2, S4 | offen |
| S6 | open-archaeo → Wikidata Pipeline (Standalone-Architekturdiagramm) | chublets-visuals | S1 | offen |

S3, S4 und S6 sind voneinander unabhängig und können in beliebiger Reihenfolge
laufen. S5 braucht die Datenmodell-Zahlen aus S2 und die Schrittnamen aus S4,
sollte also nach beiden kommen.

---

# Teil C — Die Schritte

## S0 — Festlegungen

**Ziel:** Hausfarben, Font und Namensschema stehen fest, bevor der erste
`step_*.py` geschrieben wird.

**Substanz:** siehe A1 Befund 4 und A4. Keine eigene Codeänderung.

**Abnahme:** A4-Zeilen zu Farbe/Font/Namensschema eingetragen.

### Erledigt 2026-09-10

Logo-Sampling durchgeführt, `#3B1F4A`/`#B8862E` festgelegt, Fira-Sans-Dateien
aus `fdox-visuals/fonts/` kopiert (identische Lizenz, `fonts/LICENSE-FiraSans.txt`
mitkopiert).

## S1 — Skeleton

**Ziel:** `python main.py --list` läuft und zeigt die geplanten Schritte;
Lizenz/Citation/README stehen.

**Substanz:** `py/visuals_utils.py` (Konstanten, Render-Helfer, Farbraum-Helfer
`shade()`/`tint()`, generische SVG-Primitive), `main.py` (Orchestrator, aus
`fdox-visuals/main.py` übernommen, `STEPS`-Tabelle angepasst),
`requirements.txt` (resvg-py, pillow, **zusätzlich openpyxl** — liest
`data/raw/*.xlsx`, `fdox-visuals` braucht das nicht), `.gitignore`, `LICENSE`
(MIT), `CITATION.cff`, `README.md`.

**Abnahme:** `python main.py --list` läuft ohne schwere Imports;
`python main.py --dry-run` zeigt den Plan.

### Erledigt 2026-09-10

Wie geplant. `requirements.txt` weicht von `fdox-visuals` um die
`openpyxl`-Zeile ab (Grund im Kommentar dort dokumentiert).

## S2 — Block 1: CodeMeta / Wikidata / chublets-Datamodel

**Ziel:** vier Grafiken, die zusammen zeigen, dass das chublets-Datenmodell
kein neu erfundenes Schema ist, sondern eine Vereinigung aus wiederverwendeten
Wikidata-Properties und neuen, nur für CodeMeta-Felder nötigen Properties.

**Uploads:** `Crosswalk_-_Wikidata_-_Florian_Thiery_1_.xlsx` (→
`data/raw/codemeta-wikidata-crosswalk.xlsx`),
`Wikidata_WikiProject_Informatics_Software_Properties_-_Wikidata.pdf` (von
Hand übertragen nach `data/raw/wikidata-software-properties.csv`),
`chublets_software_logo.png` (Farbsampling für S0).

**Substanz:**

- `py/crosswalk_data.py` — gemeinsamer Parser für die xlsx, von
  `step_codemeta_overview.py` und `step_codemeta_wikidata_crosswalk.py`
  benutzt (eine Quelle, zwei Ansichten; siehe A1 Befund 1 für den Parser-Bug
  unterwegs).
- `py/step_codemeta_overview.py` → `img/chublets-codemeta-overview.svg/.png`
- `py/step_wikidata_properties_overview.py` →
  `img/chublets-wikidata-properties-overview.svg/.png`
- `py/step_codemeta_wikidata_crosswalk.py` →
  `img/chublets-codemeta-wikidata-crosswalk.svg/.png`
- `py/step_wikibase_datamodel.py` → `img/chublets-wikibase-datamodel.svg/.png`
  (liest die Zahlen live aus den beiden anderen Quellen, nicht aus den
  bereits gebauten Grafiken der anderen Schritte — A2's "keine Zahl von Hand"
  gilt auch schrittübergreifend)

**Abnahme:** alle vier `img/chublets-*.png` existieren, transparenter
Hintergrund, ≤10px Rand; zweimal `python main.py --only codemeta --only
wikidata --only crosswalk --only datamodel` (bzw. einzeln) hintereinander →
`git status` leer.

### Erledigt 2026-09-10

68 CodeMeta-Properties / 33 gemappt (Befund 2), 47 Wikidata-Property-Zeilen
über 5 Kategorien (Befund 3). Parser-Bug aus Befund 1 während S2 gefunden und
gefixt, bevor die erste Grafik final gerendert wurde. Determinismus-Check:
siehe unten im Chat-Protokoll dieses Schritts (zweiter Lauf, `git status`
sauber).

---

# Teil D — Offene Punkte

- **Vier-Schritte-Namen (Block 3) sind ein Vorschlag**, nicht bestätigt:
  Ingest → Model → Curate & Link → Export & Publish. Alternative: Begriffe
  aus dem deRSE26-Paper übernehmen ("Modeling & Maintaining", "RDF Export"),
  die dort schon feststehen und nicht doppelt benannt werden sollten.
- **FAIR4RS-Detailgrafiken (Block 2) brauchen je einen eigenen Mechanismus**
  pro Prinzip — in A4 als Vorschlag eingetragen, aber nicht gegen die
  tatsächliche deRSE26-FAIR-Tabelle geprüft. Sobald das Paper zugänglich ist:
  gegenprüfen statt neu erfinden.
- **System Architecture (S5)** konsolidiert die drei Panels der alten F28
  (Klassendiagramm/Workflow/Output) zu einem Diagramm und ergänzt die
  Wikidata-Brücke als expliziten ersten Schritt (siehe Talk-Chat, dort schon
  skizziert) — sobald S4 die Schrittnamen liefert, wird daraus S5.
- **open-archaeo-Pipeline (S6)** ist inhaltlich bereits im Talk-Chat
  skizziert (Transform+Identity → Enrich → Reconcile → Push); für dieses Repo
  fehlt noch die Anbindung an echte Quelldaten (vermutlich das
  `n4o-rse/open-archaeo`-Pipeline-Repo selbst, nicht nur die Beschreibung) —
  zu klären, ob S6 aus echtem Code liest oder aus einer kuratierten
  Zusammenfassung wie S2's Wikidata-CSV.
- **Talk-spezifische Foliengrafiken** (wie `fdox-visuals` sie in S8–S10 hat:
  reale Folien mit Screenshots/Logos komponiert, nicht nur generische Badges)
  sind für chublets-visuals noch nicht geplant — falls der CAA-Talk das
  braucht, wäre das ein weiterer Block.
- **Repo-Anlage:** `chublets-software/chublets-visuals` existiert noch nicht
  auf GitHub (A4-Zeile ist ein Vorschlag) — zu klären, ob unter derselben Org
  wie `open-archaeo`/`chublets.software` selbst oder einer neuen.
