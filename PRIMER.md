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
7. **Drei der vier S4b-Detailgrafiken hatten keinen Icon-Bezug zum
   zugehörigen S4-Badge** (nur `chublets-model-datamodel` hatte ein Icon,
   `ingest`/`curate`/`export` waren reine Flussdiagramme ohne jeden
   Hinweis, zu welchem Schritt sie gehören) — Flo, 2026-09-10: "ich
   verstehe bei der Bezeichnung nicht welcher step es ist", zusätzlich
   Hinweis, dass `fdox-visuals` sein Schritt-Icon konsequent überall
   mitführt. Behoben durch `step_header()` (S4c).
8. **`_FONT_REL_PREFIX` war für die alte flache `img/`-Struktur berechnet**
   (`../fonts`, ein Verzeichnis hoch). Mit dem Umzug auf
   `img/<block>/*.svg` (S4c) liegen alle SVGs jetzt eine Ebene tiefer —
   der Pfad musste auf `../../fonts` korrigiert werden, sonst findet eine
   direkt geöffnete `.svg`-Datei (Browser/Inkscape) die Schrift nicht mehr
   (die PNG-Rasterung selbst war nie betroffen, die läuft über
   `font_files=`, nicht über das `@font-face`-CSS).
9. **Der open-archaeo-Pipeline-Code selbst liegt nicht in diesem Repo** —
   die sechs Identity-Statements, `enrich.py` mit ETag-Caching, die
   Kategorien-Reconciliation und `push --create`/`--skip-blocked` sind alle
   aus echter, bereits gebauter und getesteter Arbeit (eigener
   Chat-Verlauf), aber `chublets-visuals` hat keinen Zugriff auf das
   `n4o-rse/open-archaeo`-Pipeline-Repo selbst. S6 ist deshalb wie
   `chublets-wikidata-properties-overview` behandelt: eine kuratierte,
   von Hand gepflegte Beschreibung statt eines Live-Parse aus einer
   externen Quelle, die dieses Repo nicht enthält — nicht dasselbe wie
   S4b's "aus dem Talk-Chat, ungeprüft", weil der Pipeline-Code real
   existiert und läuft, nur eben anderswo.
10. **S6 (Befund 9) war veraltet gegenüber dem echten Repo-Stand.** Geprüft
    2026-09-10 durch Klonen von `github.com/n4o-rse/open-archaeo`: die
    Pipeline hat sich seit dem Wissensstand, aus dem S6 gebaut wurde,
    spürbar weiterentwickelt. Drei konkrete Abweichungen: (a) nur **zwei**
    Pflicht-Statements (`P31` + `P6104`), nicht sechs — `P361`/`P195`/`P217`/
    `P2888` aus S6 kommen in `docs/MAPPING.md` so nicht vor; (b) kein
    `enrich.py` mehr, stattdessen ein deterministischer, stratifizierter
    `split`-Schritt, der den 416-Eintrags-Datensatz in zwei nicht
    überlappende 208er-Hälften teilt — eine für OpenRefine
    (`out/OpenRefine/`), eine für Python (`out/Python/`); (c) die
    Python-Seite hat acht CLI-Schritte (`check`/`preview`/`reconcile`/
    `vocab`/`categories`/`subjects`/`push`/`sparql`/`site`, siehe
    `py/wikidata/main.py`), nicht die vier aus S6. S6 selbst wurde zunächst
    nicht angefasst (Flo: "das was wir haben passt") — mit S6c dann doch
    korrigiert, siehe Befund 11.
11. **S6 neu gebaut, diesmal aus einer vendorten Quelldatei statt aus
    Literalen im Skript** (S6c, 2026-09-10). `data/raw/open-archaeo/
    wikidata-main.py` ist eine unveränderte Kopie von
    `py/wikidata/main.py` aus dem geklonten Repo; `py/open_archaeo_data.py`
    liest `ALL_STEPS`/`STEPS`/`RECONCILE_STEP` daraus per
    `ast.literal_eval` (Klammern-Matching, kein Regex über mehrzeilige
    Literale). Damit S6 nicht zur vierten Wiederholung von S6b(1–3) wird,
    zeigt es etwas inhaltlich anderes: nicht den Zwei-Team-Split (S6b 1/3)
    und nicht die interaktive Session mit `reconcile`/`push` (S6b 2/3),
    sondern genau das, was `python py/wikidata/main.py all` automatisiert
    durchläuft — acht rein lesende Schritte, `reconcile` und `push` bewusst
    ausgeschlossen (Kommentar im Quellcode: "writing to Wikidata is a
    decision and a step named 'all' is a bad place to keep one"). Aktualisieren
    heißt ab jetzt: `wikidata-main.py` durch eine frische Kopie ersetzen,
    mit Datum in einem neuen A1-Befund — kein Code in
    `step_open_archaeo_pipeline.py` muss sich dafür ändern.

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
- **Jede Grafik liegt unter einem Block-Unterordner** (`img/block-1-.../`,
  `img/block-3-.../`), nie direkt unter `img/` — seit 2026-09-10 (vorher lag
  alles flach in `img/`). Neue Blöcke bekommen ihren eigenen Unterordner.
- **Namensschema in `block-3-four-step-pattern/`:** `step-<n>-<slug>-badge`
  (das reine Icon, transparent, für Folienecken) und `step-<n>-<slug>-
  detail` (die Grafik, die den Schritt tatsächlich erklärt). Jede
  `-detail`-Grafik trägt denselben Icon-Badge plus "Step N — Titel" als
  Kopfzeile wie die zugehörige `-badge`-Datei — seit 2026-09-10 Pflicht
  (Befund unten), damit nie unklar ist, zu welchem Schritt eine Grafik
  gehört.
- **System-Diagramme, die über den drei nummerierten Blöcken stehen**
  (die konsolidierte Architektur, künftig die open-archaeo-Pipeline)
  bekommen einen eigenen, unnummerierten Unterordner
  (`img/system-architecture/`), keinen `block-N`-Ordner.
- **Namensschema in `block-2-fair4rs-chain/`:** analog zu Block 3,
  `fair-<slug>-badge` / `fair-<slug>-detail` statt `step-<n>-...`, weil die
  vier FAIR4RS-Prinzipien keine Sequenz sind, sondern gleichrangig
  nebeneinanderstehen — die Buchstaben F/A/I/R ersetzen die Nummer 1–4 im
  Badge-Tag (`step_header()` bekommt dafür einen `prefix=""`-Parameter statt
  des festen "Step "-Präfixes).
- **Externe Quell-Repos, aus denen ein Diagramm gebaut wird, werden als
  unveränderte Datei-Kopie unter `data/raw/<repo-name>/` vendort**, nicht
  als Literal im `step_*.py` nachgebaut — Beispiel `data/raw/open-archaeo/
  wikidata-main.py`, gelesen von `py/open_archaeo_data.py`. Aktualisieren
  bei einer neuen Repo-Version heißt: Datei ersetzen, neuen A1-Befund mit
  Datum, kein Codeänderung im Step nötig.
- **Echte, nicht regenerierbare Assets** (das Logo) liegen unter
  `img/source/`, nicht unter `data/raw/` — sie sind kein Rohdaten-Input für
  einen Parser, sondern werden per `paste_raster()` direkt auf eine schon
  gerenderte PNG-Leinwand kopiert (vor `trim_transparent_border`, solange
  die Canvas-Pixelkoordinaten noch exakt dem Design-Raster entsprechen).
  Talk-spezifische, komponierte Folien (die dieses Muster benutzen) liegen
  in einem eigenen `img/talk/`-Ordner, getrennt von den generischen,
  wiederverwendbaren Badges in den `block-N`-Ordnern.
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
| Repo-Ziel | `chublets-software/chublets-visuals` | 2026-09-10 (angelegt, S1+S2 committet) |
| Vier-Schritte-Namen (Block 3) | Ingest → Model → Curate & Link → Export & Publish | bestätigt 2026-09-10 (S4) |
| FAIR4RS-Mechanismen (Block 2) | Findable: Q-IDs + nfdi.software-Indexierung; Accessible: Wikibase-API/SPARQL; Interoperable: CodeMeta als Pivot; Reusable: Lizenz-/Provenienz-Statements | übernommen für S3, 2026-09-10 (bleibt Referenz — Paper zieht bei Bedarf nach, nicht umgekehrt, bestätigt 2026-09-10) |
| Curate & Link / Export & Publish | F28-Konzept-Stand bleibt, keine Prüfung gegen echten Code vor Existenz einer chublets-Wikibase | bestätigt 2026-09-10 |

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
| S3 | Block 2: FAIR4RS-Kette (Banner + 4 Detailgrafiken F/A/I/R) | chublets-visuals | S1 | erledigt 2026-09-10 |
| S4 | chublets.software Four-Step-Pattern: Banner + 4 Icon-Badges | chublets-visuals | S1 | erledigt 2026-09-10 |
| S4b | Four-Step-Pattern: 4 Detailgrafiken (Ingest/Model/Curate & Link/Export & Publish) | chublets-visuals | S4 | erledigt 2026-09-10 |
| S4c | Ordnerstruktur (Block-Unterordner) + konsistente Step-Icons auf allen S4b-Grafiken | chublets-visuals | S4b | erledigt 2026-09-10 |
| S5 | System Architecture (konsolidiertes Klassendiagramm/Workflow/Output) | chublets-visuals | S2, S4b | erledigt 2026-09-10 |
| S6 | open-archaeo → Wikidata Pipeline (Standalone-Architekturdiagramm) | chublets-visuals | S1 | erledigt 2026-09-10 |
| S6b | open-archaeo: die zwei echten Routen (Übersicht, Python-Route, OpenRefine-Route), aus dem echten Repo gebaut | chublets-visuals | S6 | erledigt 2026-09-10 |
| S6c | S6 auf den echten Repo-Stand gebracht, aus einer vendorten Quelldatei statt Literalen | chublets-visuals | S6b | erledigt 2026-09-10 |
| S7 | Talk-Closing-Folie: 8 Badges als Ring um das chublets-Logo | chublets-visuals | S3, S4b | erledigt 2026-09-10 |

Alle Schritte aus dem ursprünglichen Plan sind jetzt erledigt.

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

## S4 — chublets.software Four-Step-Pattern: Banner + Icon-Badges

**Ziel:** das eigene Vier-Schritte-Muster von chublets.software als
Banner-Grafik (alle vier Schritte in einer Reihe) und als vier einzelne,
transparente Icon-Badges — analog zu `fdox-four-step-pattern` in
`fdox-visuals`, gleiche Geometrie/Renderpfad, eigene Icons und Farben.

**Uploads:** keine neuen (nutzt nur `py/visuals_utils.py` aus S1).

**Substanz:**

- `FOUR_STEPS` in `py/visuals_utils.py` — die vier Schritte als einzige
  Quelle (Titel, Beschreibung, Farbe), damit S4b und S5 dieselbe Definition
  lesen statt sie zu wiederholen (A3). Die Namen (**Ingest → Model → Curate
  & Link → Export & Publish**) waren seit S0 ein Vorschlag (A4) und werden
  mit diesem Schritt bestätigt.
- `py/step_pattern.py` — vier neue, eigens gezeichnete Icons (kein
  Icon-Font, reine SVG-Primitive wie der Rest des Repos): Ingest = drei
  Quellpunkte, die in einen Punkt zusammenlaufen; Model = ein Dreiecksgraph
  (drei Knoten, drei Kanten); Curate & Link = ein Häkchen; Export & Publish
  = ein Pfeil, der einen offenen Container verlässt. Farbreihenfolge bewusst
  nicht linear durch die Kategorie-Palette, sondern mit den beiden
  Hausfarben (Lila, Gold) in der Mitte für die chublets-spezifischen
  Schritte (Model, Curate & Link) und Teal/Blaugrau außen für die Schritte,
  die nach außen zeigen (Ingest kommt rein, Export & Publish geht raus).

**Abnahme:** `img/chublets-four-step-pattern.png` + vier
`img/chublets-step-<n>-<slug>.png` existieren, transparenter Hintergrund,
≤10px Rand; zweimal `python main.py --only pattern` hintereinander →
identische Prüfsummen.

### Erledigt 2026-09-10

Vier-Schritte-Namen aus dem Vorschlag in A4 bestätigt (keine Einwände im
Talk-Chat). Banner + 4 Badges gerendert, visuell geprüft (Icons lesbar auch
im kleinen Badge-Format), Determinismus-Check bestanden (zweiter Lauf,
identische SHA-256).

## S4b — Four-Step-Pattern: die vier Detailgrafiken

**Ziel:** zu jedem der vier Schritte aus S4 eine eigene Grafik, die den
Schritt tatsächlich erklärt statt nur zu betiteln.

**Uploads:** keine neuen.

**Substanz:**

- `four_step_icon()` aus `_node_icon` in `py/step_pattern.py` nach
  `py/visuals_utils.py` verschoben (A3: eine Quelle) — wird jetzt sowohl
  von S4 (Badges) als auch von S4b (`chublets-model-datamodel`) benutzt.
  `label_box()` (zentrierte Box mit 1–2 Textzeilen) ebenfalls aus
  `fdox-visuals` übernommen für die S4b-Flussdiagramme.
- `py/step_ingest_inputs.py` → `chublets-ingest-inputs`: dieselbe
  Drei-Quellen-Konvergenz wie `chublets-wikibase-datamodel` (S2), jetzt für
  die drei Eingangswege statt für die zwei Property-Hälften.
- `py/step_model_datamodel.py` → `chublets-model-datamodel`: kompakte Karte
  (Icon + Zahlen), liest dieselben zwei Quellen wie S2 live neu ein —
  bewusst keine dritte, eigene Zählung.
- `py/step_curate_workflow.py` → `chublets-curate-workflow`: vierstufige
  Kette Create → Statements → Curation → QC.
- `py/step_export_pipeline.py` → `chublets-export-pipeline`: SPARQL-Kette
  plus 1-zu-3-Verzweigung (drei Mapper) plus 3-zu-1-Konvergenz (ein
  Marketplace-Ziel) — komplexeste Grafik des Repos bisher.

**Abnahme:** alle vier `img/chublets-{ingest-inputs,model-datamodel,
curate-workflow,export-pipeline}.png` existieren, transparenter
Hintergrund, ≤10px Rand; zweimal `python main.py --from ingest`
hintereinander → identische Prüfsummen; `python main.py` (alle 9 Schritte)
läuft weiterhin fehlerfrei durch.

### Erledigt 2026-09-10

Wie geplant, alle vier Grafiken visuell geprüft. Inhalt für Curate & Link
und Export & Publish stammt weiterhin nur aus dem alten F28-Workflow
(Talk-Chat), nicht aus echtem Code — siehe Teil D, dieser Punkt bleibt
offen. Determinismus-Check bestanden (zweiter Lauf, identische SHA-256 über
alle 9 Schritte / 22 Dateien).

## S4c — Ordnerstruktur + konsistente Step-Icons

**Ziel:** zwei Korrekturen aus dem Talk-Chat: (1) jede der vier S4b-
Detailgrafiken trägt sichtbar dasselbe Icon wie ihr S4-Badge, nicht nur
`chublets-model-datamodel`; (2) `img/` ist nach Block gegliedert statt
flach.

**Uploads:** keine neuen.

**Substanz:**

- `visuals_utils.py`: `BLOCK1_DIR`, `BLOCK3_DIR` ergänzt; `ensure_dirs()`
  nimmt jetzt einen Pfad; `_FONT_REL_PREFIX` von `../fonts` auf
  `../../fonts` korrigiert (Befund 8); neue Funktion `step_header()`
  (kleines Badge ohne Nummern-Tag + "Step N — Titel", nutzt
  `four_step_icon()` skaliert).
- Alle acht Block-1/Block-3-Steps auf `BLOCK1_DIR`/`BLOCK3_DIR` und
  `svg_path.relative_to(ROOT)` (statt `IMG_DIR.parent`) umgestellt.
- `step_pattern.py`: Badges heißen jetzt `step-<n>-<slug>-badge.svg`
  (vorher `chublets-step-<n>-<slug>.svg`).
- Alle vier S4b-Steps: `step_header()` als erste Zeile jeder Grafik,
  bestehender Inhalt entsprechend nach unten verschoben. Neue Dateinamen
  `step-<n>-<slug>-detail.svg` (vorher `chublets-<thema>.svg`).
  `step_model_datamodel.py` dabei umgebaut: das große freistehende Icon
  ist durch denselben kompakten Header wie bei den anderen drei ersetzt,
  die beiden Zahlen stehen jetzt in einer eigenen Content-Karte darunter.

**Abnahme:** `python main.py` (alle 9 Schritte) läuft durch und schreibt
ausschließlich unter `img/block-1-.../` bzw. `img/block-3-.../`, nichts
mehr direkt unter `img/`; jede `-detail`-Datei zeigt sichtbar denselben
Icon-Kreis wie ihre `-badge`-Datei; zweimal laufen lassen → identische
Prüfsummen.

### Erledigt 2026-09-10

Wie geplant. Alter, flacher Dateibestand (13 Dateipaare direkt unter
`img/`) wurde beim Patch explizit als zu löschen markiert (ZIPs können
kein Umbenennen/Löschen transportieren, siehe PATCH-README dieses
Schritts). Determinismus-Check über alle 9 Schritte bestanden.

## S5 — System Architecture

**Ziel:** ein einziges, konsolidiertes Diagramm, das die drei alten
F28-Panels (Wikibase-Klassendiagramm, Workflow, Output) ersetzt und dabei
die Wikidata-Brücke als eigene, explizite erste Stufe zeigt statt sie
stillschweigend unter "Data Sources" zu verstecken (F28 hatte "Wikidata
IDs" bereits als Input gelistet, aber nie gezeigt, dass das ein separates,
bereits aktives System ist).

**Uploads:** keine neuen.

**Substanz:**

- `py/step_architecture.py` → `chublets-software-architecture` in einem
  neuen, unnummerierten Ordner `img/system-architecture/` (`SYSTEM_ARCH_DIR`
  in `visuals_utils.py`) — steht bewusst nicht unter `block-*`, weil es kein
  eigener Block ist, sondern ein System-Überblick über mehrere Blöcke
  hinweg.
- Fünf Stufen in einer Reihe: **Wikidata bridge** (neutral) → **Data
  sources** (Teal, = Ingest-Farbe) → **chublets.software Wikibase** (Lila,
  = Model-Farbe) → **Export pipeline** (Blaugrau, = Export & Publish-Farbe)
  → **Marketplaces & KG** (neutral). Die drei mittleren Farben sind absichtlich
  identisch zu den Block-3-Badges, damit die Systemgrafik sich sichtbar auf
  die Detailgrafiken bezieht, ohne sie zu wiederholen.
- Zahlen in Stufe 3 kommen live aus denselben zwei Quellen wie S2 und
  `chublets-model-datamodel` (S4b) — drei Grafiken, eine Zahl (A3).

**Abnahme:** `img/system-architecture/chublets-software-architecture.png`
existiert, transparenter Hintergrund, ≤10px Rand; zweimal `python main.py
--only architecture` hintereinander → identische Prüfsummen; `python
main.py` (alle 10 Schritte) läuft weiterhin fehlerfrei durch.

### Erledigt 2026-09-10

Wie geplant, visuell geprüft. Determinismus-Check über alle 10 Schritte
bestanden (23 Dateien + `pipeline_report.txt`).

## S3 — Block 2: FAIR4RS-Kette

**Ziel:** dieselbe Banner-plus-Badges-plus-Detailgrafiken-Struktur wie
Block 3 (S4/S4b), jetzt für die vier FAIR4RS-Prinzipien statt für einen
Prozess. `S3` war seit S0 als ID reserviert, aber erst jetzt gebaut — Block
3 kam zuerst, weil die Talk-Reihenfolge das so vorgab.

**Uploads:** keine neuen.

**Substanz:**

- `FAIR_PRINCIPLES` in `visuals_utils.py` — vier Einträge, `num` trägt den
  Buchstaben (`F`/`A`/`I`/`R`) statt einer Zahl; Mechanismen aus A4
  übernommen (Vorschlag, nicht gegen das deRSE26-Paper geprüft, s. Teil D).
- `fair4rs_icon()` — vier neue Icons (Lupe, offenes Schloss, zwei
  verschlungene Ringe, Kreispfeil), gleicher Stil/Strichstärke wie
  `four_step_icon()`, aber eigene Funktion statt Wiederverwendung — Block 3
  und Block 2 bedeuten unterschiedliche Dinge, ein gemeinsames Icon-Set
  hätte das verwischt (dieselbe Trennung wie in `fdox-visuals` zwischen
  `step_pattern.py` und `step_purpose.py`).
- `step_header()` um `icon_fn`- und `prefix`-Parameter erweitert (Block 3
  ruft weiterhin mit den Defaults `four_step_icon`/`"Step "`, Block 2 mit
  `fair4rs_icon`/`""`) — Rückwärtskompatibilität geprüft: alle vier
  S4b-Grafiken byte-identisch vor/nach der Signaturänderung.
- `py/step_fair_pattern.py` → Banner `chublets-fair4rs-chain` + 4 Badges
  `fair-<slug>-badge`.
- `py/step_fair_findable.py`, `step_fair_accessible.py`,
  `step_fair_reusable.py` → einfache Karten (Icon-Header + Textkarte, wie
  `chublets-model-datamodel`).
- `py/step_fair_interoperable.py` → statt einer Textkarte ein
  Hub-Diagramm: CodeMeta in der Mitte, vier Speichen zu Wikidata/DCAT/
  DataCite/CFF — "interoperabel" heißt konkret "verbindet mehrere
  Vokabulare", das zeigt eine Grafik besser als ein Satz.
- Alle fünf Grafiken landen in einem neuen Ordner `img/block-2-fair4rs-chain/`
  (`BLOCK2_DIR`).

**Abnahme:** `img/block-2-fair4rs-chain/` enthält Banner + 4 Badges + 4
Detailgrafiken (10 Dateien × 2 Formate); jede `-detail`-Grafik trägt
denselben Icon-Kreis wie ihre `-badge`-Datei; zweimal `python main.py`
(alle 15 Schritte) → identische Prüfsummen.

### Erledigt 2026-09-10

Wie geplant. Determinismus-Check über alle 15 Schritte bestanden.

## S6 — open-archaeo → Wikidata Pipeline

**Ziel:** das Detail hinter S5's "Wikidata bridge"-Stufe — die fünf realen
Schritte, die aus der open-archaeo-CSV Wikidata-Items mit Identity-Block
machen.

**Uploads:** keine neuen (Inhalt aus eigenem Wissen über die bereits
gebaute Pipeline, nicht aus einer Datei in diesem Repo — Befund 9).

**Substanz:**

- `py/step_open_archaeo_pipeline.py` → `open-archaeo-wikidata-pipeline` in
  `img/system-architecture/`, neben `chublets-software-architecture` (S5),
  nicht in einem `block-N`-Ordner (A3).
- Fünf Stufen in neutralem Grau (`CATEGORY_COLORS[5]`) — dieselbe Farbe wie
  S5's "Wikidata bridge"-Box, damit der Bezug sichtbar ist, ohne die Stufen
  farblich mit einem der drei nummerierten Blöcke zu verwechseln:
  **open-archaeo CSV** → **Transform + identity** (Slug-Logik, die sechs
  Statements P31/P6104/P361/P195+Qualifier/P217/P2888) → **GitHub
  enrichment** (ETag-gecacht) → **Category reconciliation**
  (suggest/verify/apply) → **Push to Wikidata** (create/skip-blocked).
- Fußzeile verweist explizit auf `chublets-ingest-inputs` (Block 3), da der
  Output dieser Pipeline exakt deren "Wikidata items"-Input ist — schließt
  den Kreis zwischen S6, S5 und Block 3.

**Abnahme:** `img/system-architecture/open-archaeo-wikidata-pipeline.png`
existiert, transparenter Hintergrund, ≤10px Rand; zweimal `python main.py
--only open-archaeo` hintereinander → identische Prüfsummen; `python
main.py` (alle 16 Schritte) läuft fehlerfrei durch.

### Erledigt 2026-09-10

Wie geplant, visuell geprüft. Determinismus-Check über alle 16 Schritte
bestanden. Damit sind alle in Teil B geplanten Schritte abgeschlossen —
siehe Teil D für das, was als Nächstes anliegt.

## S6b — open-archaeo: die zwei echten Routen

**Ziel:** drei weitere Grafiken, diesmal direkt aus
`github.com/n4o-rse/open-archaeo` geklont und gelesen (`py/`, `docs/`,
`out/OpenRefine/README.md`, `out/Python/README.md`) statt aus Erinnerung —
Flo: "es soll hier speziell um das verfahren gehen wie man daten von open
archaeo reinbringt (da gibt es ja den py wikibase api weg und open refine
etc.)".

**Uploads:** keine neuen (Repo direkt geklont, `codeload.github.com`/
`github.com` sind im Sandkasten-Netzwerk erlaubt).

**Substanz:**

- `py/step_open_archaeo_two_routes.py` → `open-archaeo-two-routes`: die
  Aufteilung selbst — `open-archaeo.csv` (562) → `transform` (416er
  Software-Subset) → `split` (stratifiziert, deterministisch) → zwei
  nicht überlappende 208er-Hälften (`out/OpenRefine/`, `out/Python/`) →
  gemeinsame Vokabular- und Concordance-Dateien. Farben (Teal/Lila)
  bewusst an die beiden Routen-Grafiken darunter gekoppelt.
- `py/step_open_archaeo_python_route.py` → `open-archaeo-python-route`:
  die tatsächliche Sitzung aus `out/Python/README.md` — `check`
  (Default-Schritt, schreibt nichts) → `preview` (`docs/preview.html`) →
  `reconcile` (read-only, langsam) → `push` (Dry-Run per Default) →
  `push --live` (der einzige Schritt, der wirklich schreibt, und nur für
  bereits reconciliierte Zeilen — legt nie neue Items an).
- `py/step_open_archaeo_openrefine_route.py` →
  `open-archaeo-openrefine-route`: aus `out/OpenRefine/README.md` —
  Setup → Split & Derive (GREL-Ausdrücke für VCS/Archivdatum/CRAN-PyPI) →
  Reconcile (Name+Repository-Match, hält das gemeinsame Vokabular für
  *beide* Routen) → Schema & Upload → Hand back (id,qid-CSV).
- Alle drei in `img/system-architecture/`, neben `chublets-software-
  architecture` und `open-archaeo-wikidata-pipeline` (S6) — kein eigener
  Ordner, weil sie inhaltlich zu S6 gehören, nicht zu einem der drei
  nummerierten Blöcke.

**Abnahme:** drei neue PNG/SVG-Paare in `img/system-architecture/`;
zweimal `python main.py` (alle 19 Schritte) → identische Prüfsummen.

### Erledigt 2026-09-10

Wie geplant, visuell geprüft, direkt gegen den geklonten Repo-Inhalt
verifiziert (Zahlen 562/416/208/208 und die acht CLI-Schritte stammen
wörtlich aus dem Code, nicht aus Erinnerung). Dabei wurde entdeckt, dass
S6 selbst veraltet ist (Befund 10) — bewusst nicht angefasst, siehe
Teil D.

## S6c — S6 auf den echten Stand gebracht

**Ziel:** S6 (`open-archaeo-wikidata-pipeline`) korrigieren, ohne eine
vierte Wiederholung von S6b zu werden, und so, dass ein künftiges Update
des Quell-Repos keine Codeänderung hier braucht (Flo: "dann können wir es
auch weiterführen, wenn sich in dem repo was tut").

**Uploads:** keine neuen (Repo bereits für S6b geklont).

**Substanz:**

- `data/raw/open-archaeo/wikidata-main.py` — unveränderte Kopie von
  `py/wikidata/main.py` aus dem geklonten Repo (neue Konvention, A3).
- `py/open_archaeo_data.py` — liest `ALL_STEPS`, `STEPS` und
  `RECONCILE_STEP` per klammern-gematchter Extraktion +
  `ast.literal_eval`, kein Nachbau der Listen als Literal.
- `py/step_open_archaeo_pipeline.py` komplett neu: zeigt jetzt, was
  `python py/wikidata/main.py all` tatsächlich automatisiert durchläuft —
  acht rein lesende Schritte (`transform → vocab → categories → subjects
  → check → preview → sparql → site`), zwei Zeilen à vier Boxen mit
  Zeilenumbruch-Pfeil. Bewusst **nicht** dasselbe wie S6b(1/3) (der
  Zwei-Team-Split) oder S6b(2/3) (die interaktive Session mit
  `reconcile`/`push`) — dritte, eigenständige Sicht auf dieselbe Pipeline.
  Fußzeile erklärt, warum `reconcile` und `push` fehlen (Kommentar aus dem
  Quellcode übernommen) und verweist auf `open-archaeo-python-route` für
  die interaktive Session.
- Dateiname/Output-Pfad unverändert
  (`img/system-architecture/open-archaeo-wikidata-pipeline.svg/.png`) —
  S5's Verweis "see S6" bleibt gültig, keine Folgeänderung dort nötig.

**Abnahme:** `open-archaeo-wikidata-pipeline.png` zeigt die acht echten
`ALL_STEPS`-Namen; zweimal `python main.py --only open-archaeo`
hintereinander → identische Prüfsummen; `python main.py` (alle 19
Schritte) läuft weiterhin fehlerfrei durch.

### Erledigt 2026-09-10

Wie geplant, visuell geprüft. Der Teil-D-Punkt "S6 widerspricht S6b" ist
damit erledigt und aus Teil D entfernt. Determinismus-Check über alle 19
Schritte bestanden.

## S7 — Talk-Closing-Folie

**Ziel:** eine Abschlussfolie für den CAA-Talk, analog zu
`fdox-visuals`' S10 — die acht Badges (vier Four-Step-Pattern + vier
FAIR4RS) als Ring, diesmal um das echte chublets-Logo statt um eine
generische Sphäre. Flo, 2026-09-10: "wenn du talk spezifische grafiken
(max. 1-2) vor allem für den Abschluss findest wäre das super."

**Uploads:** `chublets_software_logo.png` (bereits zu Beginn des
Talk-Chats hochgeladen, jetzt als `img/source/chublets-logo.png`
vendort).

**Substanz:**

- `paste_raster()` aus `fdox-visuals/py/visuals_utils.py` übernommen —
  komponiert ein echtes Raster-Asset auf eine bereits gerenderte PNG,
  *vor* `trim_transparent_border`, solange die Pixelkoordinaten noch exakt
  dem Design-Raster entsprechen.
- `img/source/` (vendorte Assets, hier das Logo) und `img/talk/`
  (komponierte Folien) als zwei neue, eigene Ordner (A3).
- `py/step_talk_closing.py`: acht Badges auf einem Ring (Radius 480) um
  das Logo (560×~593, Seitenverhältnis des Originals erhalten). Rechte
  Hälfte (−90° bis 45°) die vier Four-Step-Badges in Reihenfolge, linke
  Hälfte (90° bis 225°) die vier FAIR4RS-Badges in *umgekehrter*
  Reihenfolge (Reusable → Interoperable → Accessible → Findable) — damit
  der Ring als eine durchgehende Schleife liest statt als zwei
  gegenläufige Halbkreise. Keine Kausalitätsbehauptung zwischen
  benachbarten Badges (anders als bei fdox, wo Step→Purpose echt
  Ursache→Wirkung ist) — nur eine bewusste, kommentierte Lesart am
  Nahtpunkt Findable/Ingest.

**Abnahme:** `img/talk/chublets-talk-closing.png` existiert, Logo mittig
und unverdeckt von den acht Badges, transparenter Hintergrund, ≤10px Rand;
zweimal `python main.py --only talk-closing` hintereinander → identische
Prüfsummen.

### Erledigt 2026-09-10

Wie geplant, visuell geprüft (Logo lesbar, alle acht Badges klar
zugeordnet, keine Überlappung). Determinismus-Check bestanden. Nur eine
Variante gebaut (fdox hat zwei) — zweite Variante mit echten externen
Hubs (nfdi.software/find.software/Wikidata) ist Teil D, nicht angefragt.

---

# Teil D — Offene Punkte

- **Curate & Link / Export & Publish bleiben auf F28-Konzept-Stand** —
  entschieden 2026-09-10 (Flo: "so lassen, da bis auf open-archaeo noch
  nichts implementiert ist"). Keine weitere Prüfung ansteht, bis es echten
  chublets-Wikibase-Code gibt.
- **FAIR4RS-Mechanismen bleiben der A4-Vorschlag** — entschieden
  2026-09-10 (Flo: "lass das so, an das paper müssen wir eh noch ran zur
  überarbeitung, im zweifel gleichen wir das paper dann an"). Die Grafiken
  sind also die Referenz, das Paper zieht bei Bedarf nach.
- **S6b liest weiterhin nicht aus einer Datei** — bewusst niedrige
  Priorität, 2026-09-10 bestätigt. Bei Gelegenheit könnten
  `open-archaeo-two-routes` und die beiden Routen-Grafiken denselben
  Vendoring-Ansatz wie S6c übernehmen (aus `py/main.py`, `py/split.py` und
  den beiden Slice-READMEs).
- **Talk-Closing-Grafik (S7) hat noch keine zweite Variante** —
  fdox-visuals hat für seine Abschlussfolie zwei Varianten (A: nur
  Ring+Sphäre, B: Ring plus echte externe Hubs wie Wikidata/OpenStreetMap/
  NFDI4Objects angebunden). Für chublets wäre eine Variante B mit
  nfdi.software/find.software/Wikidata als angebundenen Knoten denkbar,
  aber nur auf Zuruf — S7 Variante A allein deckt "1-2 Grafiken für den
  Abschluss" schon ab.
- **Repo-Anlage:** `chublets-software/chublets-visuals` existiert jetzt auf
  GitHub und S1+S2 sind committet (bestätigt 2026-09-10) — Rest dieses Punkts
  erledigt.
