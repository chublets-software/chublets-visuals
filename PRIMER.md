# PRIMER — chublets-visuals

Arbeitsplan und Beschlusslage für `chublets-visuals`: die Grafik-Werkstatt für
chublets.software. Ein `main.py` baut aus vendorten Modelldaten (Starter-Pack-
Crosswalk, `chublets-wikibase-demo`, `wikibase-static`, `wikibase-federation`)
und einer vendorten `open-archaeo`-Quelle deterministisch alle Grafiken (SVG und
PNG), die Tabellen für den Paper-Appendix (LaTeX) und eine HTML-Übersicht für
GitHub Pages — nur mit Python, ohne externe Kommandozeilenwerkzeuge.

Die Grafiken dienen dem Paper (deRSE26/ECEASST), Vorträgen (aktuell CAA JCM
DE-NL/FL, 16.–18.09.2026, Münster, „Code is Data, Too — Nuggets, Minions and
Crows in a FAIR4RS Marketplace for Computational Archaeology“) und READMEs.
Schwesterrepo von `FDOx-squirrel/fdox-visuals` (gleicher Autor, gleiches
Hausmuster, eigene Palette).

**Ort.** <https://github.com/chublets-software/chublets-visuals> ·
Übersicht: <https://chublets-software.github.io/chublets-visuals/>

**So wird es benutzt.** Dieses Dokument wird zu Beginn jedes Arbeitschats
hochgeladen; danach genügt „wir machen S13“. Teil A gilt immer, Teil B ist die
Übersicht, Teil C beschreibt die Schritte, Teil D sammelt offene Punkte.
Es ist ein internes Arbeitsdokument (deutsch); Code, README und alles, was das
Repository nach außen zeigt, ist britisches Englisch.

**Stand 2026-10-25.** Alle Schritte S0 bis S12 sind erledigt. Es gibt 43
Grafiken mit Caption, elf Tabellen und zwei Übersichtsseiten.

---

# Teil A — Immer gültig

## A1. Ausgangslage

**Quellen (alle vendort, nie von Hand abgetippt).**

| Quelle | Wo | Stand |
|---|---|---|
| `n4o-rse/chublets-wikibase-demo` (Modell, Starter-Pack-Tabellen, Review) | `data/raw/chublets-wikibase-demo/` | `a460d94` |
| `n4o-rse/wikibase-static` (Kernel-Tabellen) | `data/raw/wikibase-static/` | `7cd3047` |
| `n4o-rse/wikibase-federation` (Use Case `chublets`) | `data/raw/wikibase-federation/` | `12abb40` |
| `n4o-rse/open-archaeo`, `py/wikidata/main.py` | `data/raw/open-archaeo/wikidata-main.py` | Kopie vom 2026-09-10 |
| Logo (Vektororiginal) | `img/source/chublets-logo.svg` | — |

Prüfsummen aller vendorten Dateien: `data/raw/vendor-manifest.csv`; Commits und
Zeitpunkt: `data/raw/SNAPSHOT.md`. Aktualisieren heißt
`python py/vendor_sources.py ...`, nicht von Hand kopieren. Am 2026-10-25 standen
die drei Modell-Repos live auf denselben Commits wie der Snapshot.

**Die Zahlen des Modells** (`py/model_data.py`, im Schritt `model-data` gegen
`mapping-summary.csv` geprüft): 168 Properties, 13 Klassen, 826 Items, 6873
Aussagen, 83 CodeMeta-Terme (37 mit Wikidata-Property, 46 nur CodeMeta), 63
bekannte Software-Properties der WikiProject-Liste (17 davon im Crosswalk, 46 nur
Wikidata), 416 open-archaeo-Einträge im Modell.

**Befunde.** Die Nummern bleiben, weil Teil C und Commits auf sie verweisen;
überholte Befunde sind kurz gehalten und als solche markiert.

1. **Crosswalk-Parser (überholt).** Die erste Fassung las die Crosswalk-xlsx und
   zählte Zwischenüberschriften als Property-Zeilen. Der Parser (`crosswalk_data.py`)
   und die xlsx sind seit S12 entfernt; die Crosswalk-Zahlen kommen aus den
   vendorten Tabellen (Befund 14).
2. **Zählung des Crosswalks (überholt).** 68 Zeilen, 33 gemappt, 35 ungemappt
   galt für die Workbook-Fassung. Heute: 83 Terme, 37 gemappt, 46 nur CodeMeta
   (Befund 14); `relatedLink` hat weiterhin zwei Zeilen (P973, P11201) und zählt
   als ein Term.
3. **WikiProject-Properties (überholt).** Die Seite liegt nur als PDF vor; die
   früher von Hand übertragene CSV (47 Zeilen) ist ersetzt durch die Liste im
   vendorten Starter-Pack (63 bekannte Properties, plus Registry-IDs, die nicht
   alle einzeln gelistet sind).
4. **Hausfarben aus dem Logo gesampelt** (`PIL.Image.getcolors`): Lila um
   `#32173D`, Gold um `#D7A141`/`#B8862E`; gewählt `CHUBLETS_PURPLE #3B1F4A` und
   `CHUBLETS_GOLD #B8862E`, leicht Richtung Lesbarkeit nachjustiert.
5. **Force-Directed-Graph verworfen.** Ein physikbasiertes Layout ist nicht
   byte-genau reproduzierbar; ersetzt durch ein deterministisches Diagramm mit
   einem Kasten je CodeMeta-Typ.
6. **Font- und Renderpipeline von `fdox-visuals` übernommen** (resvg-py statt
   cairosvg wegen fehlender libcairo unter Windows, Fira Sans vendort,
   `trim_transparent_border`, 25-Megapixel-Grenze von Google Slides); Herleitung
   in `fdox-visuals/PRIMER.md` A1.1–A1.6.
7. **Schritt-Header in Detailgrafiken (überholt).** 2026-09-10 eingeführt, damit
   man sieht, zu welchem Schritt eine Grafik gehört; seit S11 tragen Grafiken
   keinen Header mehr, die Zuordnung leisten Kette, Collage und Caption.
8. **Schriftpfad in SVGs.** Das `@font-face` braucht den relativen Pfad zu
   `fonts/`; seit S11 liegen alle SVGs direkt in `img/`, der Pfad ist `../fonts`.
   Die PNG-Rasterung ist davon nie betroffen (sie nutzt `font_files=`).
9. **Der open-archaeo-Pipeline-Code liegt nicht in diesem Repo.** Die Grafiken zu
   open-archaeo beschreiben ihn, sie führen ihn nicht aus.
10. **Erste Fassung von S6 war veraltet** (geprüft 2026-09-10 am echten Repo):
    nur zwei Pflicht-Statements (P31, P6104), ein stratifizierter `split` teilt
    416 Einträge in zwei Hälften zu je 208 (OpenRefine/Python), acht CLI-Schritte.
11. **S6 liest seitdem die vendorte `wikidata-main.py`** (`py/open_archaeo_data.py`,
    `ast.literal_eval` auf `ALL_STEPS`/`STEPS`/`RECONCILE_STEP`). Aktualisieren
    heißt Datei ersetzen, mit Datum in einem neuen Befund; im Step ändert sich nichts.
    Die Konstante 562 (Einträge der `open-archaeo.csv`) steht nicht in den
    vendorten Dateien; sie wurde 2026-09-10 aus dem Repo gelesen.
12. **Das Logo-SVG braucht Namespace-Bereinigung**, nicht nur Extraktion: jedes
    `sodipodi:*`- und `inkscape:*`-Attribut wird aus dem eingebetteten Markup
    entfernt, sonst meldet resvg-py „unknown namespace prefix“.
13. **Logo-Größe im Talk-Closing** wird gegen die halbe Bilddiagonale gerechnet,
    nicht gegen die halbe Höhe (die Ecken zeigen auf die diagonal stehenden
    Badges); `LOGO_W = 440`.
14. **Grundlage seit 2026-10-24:** Starter-Pack v1.1 (Crosswalk: 83 CodeMeta-Terme
    = 37 gemappt + 46 nur CodeMeta), `chublets-wikibase-demo` (`data/csv/`), Kernel
    von `wikibase-static`, Push-Use-Case `chublets` aus `wikibase-federation`; vendort
    mit SHA-256-Manifest.
15. **Das Property-Set hat 168 Properties**, nicht 153 und nicht 158: 10 Kernel
    (P1–P10; P1, P2, P4, P7 stehen auch im Pack) + 149 weitere Zeilen des Packs
    (P100–P248) + 9 Review-Zeilen vom 2026-10-22 (P249–P257). Die 153 des Packs
    sind „149 + vier Kernel-Zeilen“ und behalten ihren `pack_status` (37 / 46 / 52 /
    18); Review-Zeilen und die übrigen sechs Kernel-Properties haben keinen
    Pack-Status und bekommen keinen erfundenen (`origin_set` in `model_data.py`).
16. **Plattformunterschiede.** (a) `sin`/`cos` unterscheiden sich in der letzten
    Dezimalstelle: neue Steps runden Koordinaten auf zwei Stellen; der Bestand
    wurde in S11/S12 angeglichen (Talk-Closing rundet seit 2026-10-25). (b) Die
    gemessene Textbreite (Pillow/FreeType) ist auf Windows größer als auf Linux;
    ein Neubau auf einem anderen Rechner kann SVGs im Bruchteil eines Pixels
    ändern. Regel (seit Patch 7): Boxen, Spalten und Legenden werden aus der
    gemessenen Breite berechnet, nie gegen eine feste Größe geprüft; `assert` nur
    für Modellannahmen (Anzahl, Eindeutigkeit). Die letzten zwei Pixel-Asserts
    (`class-tree`, `property-vocabulary-overlap`) sind in S12 entfernt.
17. **Die Themenfelder der Properties sind eigene Themenfelder** (`data/topics.yaml`,
    14 Themen, jede Property in genau einem): Die elf Gruppen der WikiProject-Seite
    sind uneinheitlich, und 67 von 168 Properties haben dort keinen Zwilling.
18. **Evidenzbasis geprüft (S12, 2026-10-25).** 68 Terme des Crosswalks + 15 nur
    auf der CodeMeta-Terms-Seite = 83; die 63 WikiProject-Properties sind „bekannt“,
    die Registry-IDs sind nicht alle einzeln gelistet (Grafik sagt das); die
    Prüfung gegen Wikidata hat 246 Checks an 137 Entitäten, 14 Abweichungen.

## A2. Zielbild

```
data/raw/<repo>/…          vendorte Quellen, unverändert (Manifest mit SHA-256)
      │
      ▼  py/model_data.py   die eine Stelle, die sie liest (168 Props, 13 Klassen, 826 Items, …)
      │
      ▼  py/step_*.py       Geometrie + Text, Zahlen nur aus model_data / caption_facts
      │
      ▼  py/model_graphics.py   Text mit gemessener Breite, Boxen, Chips, Zuschnitt, save()
img/<name>.svg + .png       flach, ohne Header/Footer, transparent, Rand 10 px, CC BY 4.0 in den Metadaten
captions.yaml               Caption, Alt-Text, Quellen, Lizenz je Grafik
tex/*.tex                   elf Tabellen für den Appendix (longtable)
docs/                       index.html (Grafiken), tables.html (Tabellen), GitHub Pages
```

Eigenschaften, an denen sich das Ergebnis messen lassen muss:

- Zweimal `python main.py` hintereinander → `git status` bleibt leer (auf demselben Rechner).
- Jede Grafik hat transparenten Hintergrund, ≤ 10 px Rand, bleibt unter Google Slides’ 25-Megapixel-Grenze und hat einen Eintrag in `captions.yaml` (`REQUIRE_ALL`).
- Jede Zahl in einer Grafik oder Caption kommt zur Laufzeit aus den vendorten Daten.
- Farbe und Schrift kommen aus `py/visuals_utils.py` und `py/model_graphics.py`.
- Jede Grafik ist im Paper ohne Kenntnis des Codes lesbar (Legende erklärt Farben, Formen, Chips, IDs).

## A3. Querschnittsregeln

- **Rohdaten** liegen unverändert unter `data/raw/<repo>/`; ein Step liest nie selbst
  eine CSV, sondern geht über `py/model_data.py`. Externe Quellen werden vendort
  (`py/vendor_sources.py`), nicht als Literal nachgebaut.
- **Ausgabe flach:** `img/<name>.svg` und `.png`, kein `block-N`-Ordner, kein Header,
  Footer, Titel, Step-Badge im Bild und keine Quellenzeile. Nur `img/source/` (das
  Logo, ein nicht regenerierbares Asset) ist ein Unterordner.
- **Captions** stehen in `captions.yaml` (Schlüssel = Dateiname ohne Endung;
  Regeln in `py/captions.py`), Zahlen als `{platzhalter}` aus
  `model_data.caption_facts()`. Seit S12 ist eine fehlende Caption ein Fehler
  (`REQUIRE_ALL`).
- **Texte** in Grafiken: britisches Englisch, auf den Inhalt zugeschnitten.
  Modell-Bezeichner (P4, P100, Q-IDs, `crmdig:D14`) bleiben; Code-Begriffe
  (kernel, pack, importer stub) und „Starter Pack/Kit“ kommen in keiner Grafik,
  Caption oder Tabelle vor (`model_graphics.save` und `tables_data._check_wording`
  brechen sonst ab).
- **Farben:** Hauspalette für die Herkunft einer Property (crosswalked, CodeMeta
  only, Wikidata only, chublets addition, unclassified); Semantik-Schema (Klasse
  `#9a3412`, Term `#4c1d95`, Property-Metadaten `#fbbf24`, Instanz `#e2e8f0`,
  reales Objekt `#166534`, OWL weiß) nur für Modellelemente; beide nie im selben Element.
- **DataCite** nur als Zusatzevidenz (Kästchen, „über CodeMeta abgeleitet, nicht publiziert“).
- **Layout aus gemessenem Text:** Boxhöhen, Spaltenbreiten und Legenden folgen der
  gemessenen Textbreite; kein `assert` auf Pixelmaße (Befund 16).
- **Koordinaten** auf zwei Dezimalstellen gerundet, damit SVGs auf jeder Plattform
  dieselben Bytes haben.
- **Icons** (Schritte und FAIR) kommen aus `py/icons.py` (Redraws) und
  `py/visuals_utils.py` (Lupe, Verzweigung, Dreieck, Haken); Zentrierung in
  `py/chain_banner.py`.
- **Lizenz:** Grafiken, Tabellen, Captions und Übersichtsseiten immer CC BY 4.0
  von Florian Thiery, Code MIT (`LICENSE-GRAPHICS.md`; Konstanten `CREATOR`,
  `LICENCE` in `visuals_utils.py`).
- **Keine Uhr im Ergebnis**; **zweimal laufen lassen, `git status` bleibt leer.**
- **Netzwerk** ist nirgends nötig; ein Schritt, der live liest, bekäme einen eigenen
  Verb außerhalb des Default-Laufs.
- **Sprache/Plattform:** PRIMER deutsch, alles andere englisch; Windows ist
  Referenzplattform, Befehle einzeilig für `cmd`.
- **Auslieferung** als Patch-ZIP mit `PATCH-README.md` (Contents, Applying, What to run,
  How to verify, Verified here, Commit mit `git add`/`git commit -m … -m …`/`git push`);
  nur Quellen, Grafiken werden neu gebaut; Flo spielt ein und pusht selbst.

## A4. Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Renderpipeline | resvg-py + vendorte Fira Sans, wie `fdox-visuals` | 2026-09-10 |
| Hausfarben | `CHUBLETS_PURPLE #3B1F4A`, `CHUBLETS_GOLD #B8862E`, aus dem Logo gesampelt; sechs Kategoriefarben (Lila, Gold, Türkis, Rost, Schieferblau, Grau) | 2026-09-10 |
| CodeMeta-Übersicht | Diagramm mit einem Kasten je CodeMeta-Typ statt Force-Directed-Graph (Determinismus) | 2026-09-10 |
| Namen der vier Schritte | Ingest → Model → Curate & Link → Export & Publish | 2026-09-10 |
| FAIR-Mechanismen | Findable: Q-IDs + Indexierung durch nfdi.software und find.software; Accessible: Wikibase-API/SPARQL ohne Login zum Lesen; Interoperable: CodeMeta als Pivot; Reusable: Lizenz-/Provenienz-Statements. Die Grafiken sind die Referenz, das Paper zieht bei Bedarf nach | 2026-09-10 |
| Curate & Link, Export & Publish | bleiben auf Konzeptstand, solange es keinen echten chublets-Wikibase-Code gibt | 2026-09-10 |
| Repo | `chublets-software/chublets-visuals` | 2026-09-10 |
| Ground Truth der Modell-Grafiken | Starter-Pack v1.1 + `chublets-wikibase-demo` + `wikibase-static` (Kernel) + `wikibase-federation` (Push), vendort mit SHA-256-Manifest | 2026-10-24 |
| Form der Grafiken | flach unter `img/`, kein Block, kein Header/Footer; Captions in `captions.yaml` (nur EN, britisch) | 2026-10-24 |
| Herkunftsklassen | crosswalked, CodeMeta only, Wikidata only, chublets addition, unclassified; Mengen: kernel, initial, review; „Starter Pack“ nirgends in Grafik/Caption/Tabelle, interne Feldnamen und vendorte Pfade bleiben | 2026-10-24 |
| Grafiken stehen allein | Legende in jeder Grafik; Modell-Bezeichner bleiben, Code-Begriffe nicht | 2026-10-24 |
| Themenfelder | eigene Themen (`data/topics.yaml`, 14), von Flo freigegeben | 2026-10-24 |
| Lizenz | CC BY 4.0 von Florian Thiery für Grafiken, Tabellen, Captions, Seiten; Code MIT | 2026-10-24 |
| Tabellen und Seiten | LaTeX-`longtable` unter `tex/`; `docs/index.html` und `docs/tables.html`, GitHub Pages aus `main` / `/docs` (läuft) | 2026-10-24 |
| Bestandsgrafiken | alle bleiben, flach und ohne Header; Step-IDs ändern sich nicht; Ketten (`chublets-four-step-pattern`, `chublets-fair4rs-chain`) und Einzel-Badges bleiben erhalten, dazu je eine Collage (`chublets-four-steps`, `chublets-fair`) und Einzelbilder | 2026-10-25 |
| Icons | Schloss, Verknüpfungsglied (Interoperable), Kreislauf und Export-Pfeil in `py/icons.py` neu gezeichnet, alle Icons zentriert | 2026-10-25 |
| Layout | Maße aus gemessenem Text, keine Pixel-Asserts | 2026-10-24 |
| Captions Pflicht | `REQUIRE_ALL = True`: eine Grafik ohne Eintrag ist ein Fehler | 2026-10-25 |
| Altlasten | `crosswalk_data.py`, die Crosswalk-xlsx, die 47-Zeilen-CSV und ungenutzte Helfer in `visuals_utils.py` entfernt | 2026-10-25 |
| Auslieferung | Patch-ZIP mit voller `PATCH-README.md` und Commit-Block, immer; Flo pusht selbst | 2026-10-24 |

## A5. Was in welchem Chat hochgeladen wird

Zu Beginn jedes Chats: `PRIMER.md` plus ein Bundle aus Quellen und Code (kein
`img/`, kein `.venv/`). Unter Windows:

```cmd
powershell -Command "Compress-Archive -Path PRIMER.md,captions.yaml,py,data,fonts,main.py,requirements.txt,CITATION.cff,LICENSE,LICENSE-GRAPHICS.md,README.md,.gitignore -DestinationPath chublets-visuals-bundle.zip -Force"
```

Nicht hochladen: `img/*.png`/`img/*.svg`, `docs/`, `tex/` (werden neu gebaut),
`__pycache__/`, `.git/`, `img/pipeline_report.txt`. Nach jedem Push klont Claude das
Repo frisch (`git fetch` und Fast-Forward), das ersetzt den Upload der Grafiken.

---

# Teil B — Schrittübersicht

| ID | Schritt | Hängt ab von | Status |
|---|---|---|---|
| S0 | Festlegungen: Palette, Font, Namensschema | — | erledigt 2026-09-10 |
| S1 | Skeleton: `main.py`, `visuals_utils.py`, Lizenz, Citation, README | S0 | erledigt 2026-09-10 |
| S2 | Block 1: CodeMeta / Wikidata / chublets-Datenmodell (vier Grafiken) | S1 | erledigt 2026-09-10, neu gezeichnet in S11 |
| S3 | FAIR4RS-Kette (Kette, vier Badges, Collage, vier Einzelbilder) | S1 | erledigt 2026-09-10, neu gezeichnet in S11 |
| S4 | Vier-Schritte-Muster (Kette, vier Badges) | S1 | erledigt 2026-09-10, neu gezeichnet in S11 |
| S4b | Vier Detailgrafiken der Schritte | S4 | erledigt 2026-09-10, ersetzt durch Collage und Einzelbilder in S11 |
| S4c | Block-Ordner und Schritt-Header | S4b | erledigt 2026-09-10, überholt durch S11 (flach, ohne Header) |
| S5 | Systemarchitektur (fünf Stufen) | S2, S4b | erledigt 2026-09-10, neu gezeichnet in S11 |
| S6 | open-archaeo → Wikidata-Pipeline | S1 | erledigt 2026-09-10 |
| S6b | open-archaeo: zwei Routen, Python-Route, OpenRefine-Route | S6 | erledigt 2026-09-10 |
| S6c | S6 aus vendorter Quelldatei auf den echten Stand gebracht | S6b | erledigt 2026-09-10 |
| S7 | Talk-Closing: acht Badges als Ring um das Logo | S3, S4b | erledigt 2026-09-10 |
| S7b | Logo als eingebettetes SVG, Nuggets-Kollision behoben | S7 | erledigt 2026-09-10 |
| S8 | Datenschicht: Quellen vendort, `model_data.py`, `captions.yaml`, Prüfschritte | S1 | erledigt 2026-10-24 |
| S9 | Themen-Taxonomie der 168 Properties | S8 | erledigt 2026-10-24 |
| S9b | LaTeX-Tabellen für den Appendix | S9 | erledigt 2026-10-24 |
| S9c | HTML-Übersicht für GitHub Pages | S9b | erledigt 2026-10-24 |
| S10 | Dreizehn Modell-Grafiken | S9 | erledigt 2026-10-24 |
| S11 | Bestandsgrafiken neu gezeichnet: flach, ohne Header, Zahlen aus dem Modell | S10 | erledigt 2026-10-25 |
| S12 | Abschluss: Captions Pflicht, Pixel-Asserts weg, Evidenzbasis geprüft, Altlasten und PRIMER aufgeräumt | S11 | erledigt 2026-10-25 |

Unabhängig voneinander sind alle Schritte ab S8, soweit sie nicht in der Spalte
„hängt ab von“ stehen; neue Grafiken brauchen nur `model_data` und `model_graphics`.

---

# Teil C — Die Schritte

## S0 bis S7b — der Ausgangsstand (September 2026)

Die ersten Schritte haben die Grafik-Bibliothek aufgebaut. Ihre Inhalte gelten
weiter, die Form wurde in S11 erneuert; die Tabelle sagt, was heute wo liegt.

| Schritt | Inhalt | Grafiken heute (`img/…`) |
|---|---|---|
| S0, S1 | Palette, Font, Namen; `main.py`, `visuals_utils.py`, Lizenz | — (Code) |
| S2 | CodeMeta-Typen, WikiProject-Properties, Crosswalk, Datenmodell | `chublets-codemeta-overview`, `chublets-wikidata-properties-overview`, `chublets-codemeta-wikidata-crosswalk`, `chublets-wikibase-datamodel` |
| S3 | FAIR-Prinzipien | `chublets-fair4rs-chain`, `fair-{findable,accessible,interoperable,reusable}-badge`, `chublets-fair`, `chublets-fair-{findable,accessible,interoperable,reusable}` |
| S4, S4b | vier Schritte | `chublets-four-step-pattern`, `step-{1-ingest,2-model,3-curate-link,4-export-publish}-badge`, `chublets-four-steps`, `chublets-step-{ingest,model,curate-link,export-publish}` |
| S5 | Architektur | `chublets-software-architecture` |
| S6, S6b, S6c | open-archaeo | `open-archaeo-wikidata-pipeline`, `open-archaeo-two-routes`, `open-archaeo-python-route`, `open-archaeo-openrefine-route` |
| S7, S7b | Talk-Closing | `chublets-talk-closing` (Logo eingebettet aus `img/source/`) |

Was die Schritte bei der Arbeit gelehrt haben, steht in den Befunden 1–13 (A1).
Zwei Entscheidungen daraus: Das Logo wird als verschachteltes `<svg>` eingebettet
(ein Renderlauf, SVG und PNG beweisbar identisch), und echte Rasterbilder ohne
Vektororiginal würden weiterhin per `paste_raster()` auf das fertige PNG gelegt.

## S8 — Datenschicht und Captions

**Ziel.** Die Modell-Grafiken lesen ihre Zahlen aus einer einzigen, geprüften
Schicht, nicht aus je eigenen CSV-Lesern.

**Gebaut (2026-10-24).**
- `py/vendor_sources.py` kopiert 38 Dateien unverändert aus den vier
  Quell-Checkouts nach `data/raw/<repo>/` und schreibt
  `data/raw/vendor-manifest.csv` (SHA-256, Zeilenenden normalisiert) und
  `data/raw/SNAPSHOT.md`. `--check` prüft ohne Netz.
- `py/model_data.py`: `load()` liefert 168 `Prop`, 13 `Cls`, die DataCite-
  Bridge und die Pack-Zusammenfassung; Felder siehe Befund 15.
- `py/captions.py` + `captions.yaml`: Captions außerhalb der Grafiken.
- Schritt `model-data` (zuerst) und `captions` (zuletzt) in `main.py`.

**Prüfung.** `python main.py --only model-data` muss „vendored files match",
„168 properties: 10 kernel + 149 pack + 9 review", „14 topics cover all 168
properties exactly once" melden. Zweimal laufen lassen ändert nichts.

## S9 — Themen-Taxonomie

**Ziel.** Jede der 168 Properties in genau einem Themenfeld, für die
Katalog-Grafik `property-topics` und die Spalten der Herkunfts-Grafiken.

**Stand.** `data/topics.yaml` ist von Flo freigegeben (2026-10-24, „Die Themen
passen zunächst" — spätere Änderungen sind möglich) und hat 14 Themen (Kernel;
Property-Beschreibung; Identität und Namen; Registry-IDs; Quellcode und
Entwicklung; Plattform, Anforderungen und Abhängigkeiten; Dateien, Formate
und Standards; Versionen, Releases und Daten; Links, Medien und Web;
Agenten-Rollen; Person und Organisation; Rechte, Förderung und Zugang;
Klassifikation, Features und Relationen; Publikation, Zitation und Review).
`python py/topics.py` druckt die Review-Tabelle (Thema × Herkunft,
WikiProject-Gruppe, CodeMeta-Typ). Änderungen am Zuschnitt sind eine
Änderung an dieser einen Datei; die Grafiken folgen automatisch.

## S9b — LaTeX-Tabellen für den Appendix

**Ziel.** Die Statistiken und Werte des Datenmodells (welche Properties aus
Wikidata, CodeMeta, gecrosswalkt, neu) als fertige Tabellen für das
Overleaf-Paper.

**Gebaut (2026-10-24).** `py/tables_data.py` baut elf neutrale `Table`-Objekte
aus `model_data` und `topics` (Kennzahlen; Properties nach Herkunft und Status;
Evidenz je Status; Themen nach Herkunft und nach Status; Katalog der 168
Properties nach Thema; 84 CodeMeta-Terme; WikiProject-Gruppen; DataCite-Evidenz;
Klassen; Quellen). Alle Zahlen kommen aus den Daten, `build()` prüft die Summen
(168, 153, 84, 68 ...). `py/latex_utils.py` schreibt sie als `longtable`
(nur ASCII, ohne Zeitstempel) nach `tex/`, `tex/appendix-tables.tex` bindet alle
ein. Das Escaping lehnt unbekannte Zeichen ab, statt sie durchzureichen.

**Prüfung.** `python main.py --only tables` zweimal: `git status` unverändert.
Kompilieren mit `longtable` + `array` ergibt keine Fehler und keine
Overfull-Boxen (11 Tabellen, 15 Seiten in `article`, 11 pt, A4). Die Spaltenbreiten
sind auf `\linewidth` bezogen und rechnen das Padding ein; bei anderer
Schriftgröße im Paper ggf. `\renewcommand{\chubletstablesize}{\scriptsize}`.

## S9c — HTML-Übersicht

**Ziel.** Eine schnelle Übersicht aller Grafiken und Tabellen, die auf GitHub
Pages läuft.

**Gebaut (2026-10-24).** `py/step_gallery.py` schreibt zwei Seiten:
`docs/index.html` (Grafiken) und `docs/tables.html` (die elf Tabellen; seit
dem Folgepatch eigene Seite). Beide: eine Datei, Hell/Dunkel, ohne CDN und ohne
Webfont. `img/` wird nach `docs/img/` kopiert (Vorschau ist das PNG, weil ein
SVG in `<img>` keine Schrift nachladen kann), `fonts/` nach `docs/fonts/` (damit
das geöffnete SVG Fira Sans findet) und die Downloads nach `docs/data/` (CSV und
`.tex` je Tabelle). Grafiken erscheinen mit Caption (eingeklappt), Alt-Text,
Quellen und Lizenz aus `captions.yaml`; fehlt der Eintrag, steht „No caption yet".
Die Tabellen sind sortier- und filterbar. Platzhalter in Captions füllt
`model_data.caption_facts()`: `n_props`, `n_classes`, `n_kernel`, `n_pack`,
`n_review`, `n_topics`, `n_codemeta_terms`, `n_crosswalked`, `n_codemeta_only`,
`n_wikidata_only`, `n_chublets_addition`, `n_no_status`, `n_kernel_classes`,
`n_pack_classes`, `n_stub_classes`, `n_twin`, `n_close_match`, `n_with_codemeta`,
`n_schema_org`, `n_datacite`, `n_wikiproject`, `n_oa_half` sowie die Item- und
Aussagezahlen aus `entity_facts()`; die vollständige Liste steht in
`model_data.caption_facts()`.

**Prüfung.** Im Headless-Browser: keine JS-Fehler, Sortieren (Summenzeile bleibt
unten), Filter, keine horizontale Seitenscroll bei 390 px Breite.

## S10 — Modell-Grafiken

**Ziel.** Dreizehn Grafiken des Datenmodells, flach unter `img/`, ohne Titel,
Header oder Footer, jede im Paper allein lesbar.

**Werkzeug.** `py/model_graphics.py`: Text mit gemessener Breite (Pillow, die
vendorte Fira Sans), Boxen, Chips, Umbruch, `Canvas` (zuschneiden auf Inhalt plus
10 px) und `save()` (SVG und PNG). Koordinaten auf zwei Stellen gerundet, damit
das SVG auf jeder Plattform dieselben Bytes hat. Zwei Paletten: Hausfarben für
die Herkunft einer Property, Semantik-Schema nur für Modell-Elemente.
`visuals_utils.font_face_css(rel_prefix)` bekam einen Parameter (`../fonts` für
flache Grafiken).

**Gebaut (2026-10-24).**
- `class-tree` (`py/step_class_tree.py`): 13 Klassen, Unterklassen (P1),
  Wikidata-Äquivalent (P4), CIDOC-CRM-Klasse (eigene oder geerbte);
  built-in / für chublets definiert / aus Wikidata übernommen (Stub) durch
  Füllung und Rand. Layout-Annahmen (eine Wurzel Q3, Q106 als einziges
  Zwei-Eltern-Kind) werden geprüft; ändert sich das Modell, bricht der Schritt ab,
  statt falsch zu zeichnen.
- `property-origin` (`py/step_property_origin.py`): ein Balken über die 168
  Properties nach Herkunft im Crosswalk, darunter je Gruppe, wie viele ein
  Wikidata-Pendant (P4), einen Close Match (P100), einen CodeMeta-Term, einen
  schema.org-Term (P102) und ein DataCite-Element (gestrichelt, über CodeMeta
  abgeleitet) haben.
- `property-topics` (`py/step_property_topics.py`): 14 Themen aus
  `data/topics.yaml`, je Zeile Beschreibung, ein Quadrat je Property nach Herkunft
  gefärbt, Anzahl und die ersten vier Properties als Beispiele.
- `property-vocabulary-overlap` (`py/step_property_vocabulary_overlap.py`;
  im Vorschlag „property-origin-flow"): ein Balken, sechs Gruppen (52 / 12 / 13 /
  37 / 46 / 8); Klammer oben „Wikidata-Property (P4): 114", unten „CodeMeta-Term:
  83", Überlappung 37, Vereinigung 160 von 168. Der Schritt prüft, dass die sechs
  Gruppen die Properties lückenlos teilen.
- `entity-overview` (`py/step_entity_overview.py`): 13 Klassen, 826 Items,
  168 Properties; Items nach Klasse (444 chublets / 368 sonstige / 14 ohne Klasse)
  und nach Herkunft (803 open-archaeo / 6 Wikidata / 17 Stubs); Pfeile
  „instance of (P2)" und „statements". Die 6873 Aussagen zählen Demo und Kernel;
  die 6852 in früheren Notizen waren ohne Kernel.

- `property-metadata-layer`: eine Property ist selbst eine Entität; Beispiel
  „programmed in“ (P123), sieben Zeilen (P4, P100, P101, P102, P9, P10, P5) mit
  Beispielwert und Balken „bei wie vielen der 168 Properties vorhanden“
  (114 / 22 / 83 / 71 / 135 / 71 / 4).
- `chublet-item`: das echte Item Q360 (SPARQLing Unicorn QGIS Plugin, 39
  Aussagen) wie eine Item-Seite: Klassen orange, Items grau, Literale als Text,
  Qualifier darunter, Referenzzahl je Aussage; gezeigt wird eine Auswahl.
- `statement-provenance`: links die Anatomie einer Aussage (Version 0.17.4 von
  Q360 mit zwei Qualifiern und zwei Referenzgruppen), rechts die Nutzung: 6873
  Aussagen nach Herkunft, 6440 mit Referenz, 1352 mit Qualifier, häufigste
  Qualifier. Ohne Herkunft sind 320 Aussagen (Kernel und einzelne Items).
- `codemeta-coverage`: alle 83 CodeMeta-Terme als Chips nach CodeMeta-Typ,
  violett = gemappt (37), türkis = nur CodeMeta (46). `relatedLink` hat zwei
  Zeilen und zählt einmal; die Gruppe „(v2 term)“ ist mit ihrer Hauptgruppe
  zusammengelegt. Der Schritt prüft die Summe gegen `mapping-summary`.
- `chublet-identity`: das Item pastclim (Q424) mit seinem Identitätsblock
  (instance of chublet, maintained by WikiProject, part of Plattform und
  Sammlung), drei von allen Chublets geteilte Items (je 417 Nutzer), darunter
  die 7 Merges aus `merges.csv` (Eintrag der Quellenliste und Wikidata-Item =
  dasselbe).
- `wikibase-bootstrap`: die Phasen core (3 Klassen, 10 Properties), model (7
  Klassen, 158 Properties) und items (803 + 6; die 17 Stubs werden nicht
  geschrieben), die Regeln des Push und der Ablauf bei nicht leerem Ziel
  (Inventory, Adopt-Liste mit 93 Paaren, Lauf). Quelle: README und Dateien des
  Use Case `chublets` in `wikibase-federation`.
- `static-vs-federation`: ein CSV-Modell, zwei Wege. Aussagen über die beiden
  Repositories stehen nur dort, wo ihre Dokumentation sie trägt
  (`wikibase-static`: schreibgeschützte statische HTML-Seiten, nie
  Schreibzugriff; `wikibase-federation`: Push mit `wbeditentity`).
- `model-evidence-base`: sechs Quellen (Crosswalk, CodeMeta-Terms-Seite,
  WikiProject-Liste, Wikidata-Prüfung mit 246 Checks und 14 Abweichungen,
  Entscheidungstabellen, open-archaeo mit 416 Einträgen) und was sie speisen.
  Die Zahl 15 „Terme ohne Workbook-Zeile“ stammt aus `mapping-summary` (frühere
  Notizen nannten 16); 68 + 15 = 83 Terme, in S12 gegen die live Repos geprüft.
- **Lizenz-Regel (2026-10-24, „immer“):** jede Grafik, Tabelle und Caption ist
  CC BY 4.0 von Florian Thiery. `visuals_utils.CREATOR` und `LICENCE` sind die
  einzige Quelle; sie stehen in den SVG-Metadaten (`<metadata>`), im Kopf jeder
  `.tex`-Datei, auf den Übersichtsseiten und in `LICENSE-GRAPHICS.md`.
- `caption_facts()` liefert jetzt auch Item- und Aussagezahlen
  (`entity_facts` in `model_data.py`), damit Captions und Übersichtsseite
  dieselben Zahlen haben.

**Wording.** Tabellen und Grafiken enthalten „Starter Pack" nirgends;
`tables_data._check_wording` und `model_graphics.save` brechen sonst ab. In der
Quellentabelle heißt es „modelling repository".

**Prüfung.** Zwei Läufe ändern nichts; Zahlen stimmen mit `table-property-evidence`
überein (114 / 22 / 83 / 71 / 34); Captions rendern mit den Fakten aus
`caption_facts()`. Alle 13 Grafiken sind gebaut und von Flo auf GitHub gegengelesen; die
Durchsicht im Paper steht noch aus.

## S11 — Bestandsgrafiken neu gezeichnet

**Ziel.** Alle Grafiken aus S2–S7b im neuen Stil: flach unter `img/`, ohne Header,
Footer und „Block“-Wort, Zahlen aus dem Modell, Captions in `captions.yaml`,
Step-IDs unverändert.

**Gebaut (2026-10-24 bis 2026-10-25, in zwölf Patches).**
- Gruppe A (Block 1): `py/codemeta_diagram.py` baut beide CodeMeta-Diagramme
  (Kasten je Typ, Hierarchie, Summe gegen `mapping-summary`); die WikiProject-Grafik
  zeigt die 63 Properties in acht Gruppen; `chublets-wikibase-datamodel` zeigt, wie
  die 168 Properties aus 114 Wikidata-Äquivalenten und 83 CodeMeta-Termen entstehen.
- Gruppe B (vier Schritte): `py/four_steps.py` baut die Panels; Collage
  `chublets-four-steps` und vier Einzelbilder.
- Gruppe C (FAIR): `py/fair_panels.py`; Collage `chublets-fair` und vier Einzelbilder.
- Gruppe D: `py/oa_graphics.py` (Reihen aus Kästen mit Pfeilen) für Architektur und die vier
  open-archaeo-Grafiken; Talk-Closing flach und mit gerundeten Koordinaten.
- Auf Wunsch zurückgebracht (2026-10-25): die Ketten `chublets-four-step-pattern`
  und `chublets-fair4rs-chain` und die acht Einzel-Badges (`py/chain_banner.py`), mit
  neu gezeichneten Icons (`py/icons.py`) und zentriert.
- Weggefallen: Block-Ordner, Schrittköpfe, `chublets-…-detail`-Dateien, die alten
  Zahlen („46+ / 35“).

**Abnahme.** `python main.py --strict` ohne Fehler; keine Datei unter `img/block-*`,
`img/system-architecture` oder `img/talk`; zwei Läufe ändern nichts; jede Grafik hat
eine Caption.

## S12 — Abschluss

**Ziel.** Das Repository ist rund: nichts Halbes, nichts Überholtes.

**Gebaut (2026-10-25).**
- `captions.REQUIRE_ALL = True`; alle 43 Grafiken haben einen Eintrag.
- `class-tree` berechnet Spaltenbreiten aus dem gemessenen Text, `property-vocabulary-overlap`
  lässt Legendeneinträge umbrechen; es gibt keinen Pixel-Assert mehr.
- `model-evidence-base` gegen die live Repos geprüft (Commits unverändert, 68 + 15 = 83;
  63 WikiProject-Properties mit Hinweis auf nicht gelistete Registry-IDs).
- Entfernt: `py/crosswalk_data.py`, `data/raw/codemeta-wikidata-crosswalk.xlsx`,
  `data/raw/wikidata-software-properties.csv`, ungenutzte Helfer aus `visuals_utils.py`.
- PRIMER und README neu geschrieben (Stand statt Chronik).

**Abnahme.** `python main.py --strict` ohne Fehler und ohne Hinweis auf fehlende Captions;
zwei Läufe ändern nichts; `grep -ril starter img/*.svg tex docs/*.html` ohne Treffer.

---

# Teil D — Offene Punkte

- **Windows-Lauf der letzten Patches.** Die SVGs wurden auf Linux gebaut und geprüft; ein
  Lauf auf Windows (Referenzplattform) kann Breiten ändern (Befund 16). Flo prüft beim
  nächsten Lauf.
- **Konstante 562** (Einträge von `open-archaeo.csv`) steht in
  `py/step_open_archaeo_two_routes.py`, nicht in den vendorten Dateien; beim nächsten
  Snapshot von `open-archaeo` aus der Quelle belegen (Befund 11).
- **Dünne Icons.** Lupe, Verzweigung, Dreieck und Haken sind etwas dünner gezeichnet als
  die neuen Icons; auf Zuruf angleichen.
- **Zweite Variante des Talk-Closings** (Ring plus angebundene externe Hubs wie
  Wikidata/nfdi.software) nur auf Zuruf.
- **`CITATION.cff`** nennt nur MIT; ob dort beide Lizenzen stehen sollen (`license` als
  Liste), entscheidet Flo. Die Tabellen gelten als CC BY 4.0 (abgeleitet aus Wikidata CC0
  und dem ConnOSS-Crosswalk CC BY 4.0).
- **Annahmen in den Tabellen.** Klassen Q372, Q378, Q379 heißen „importer stub“, weil ihr
  `origin` im Modell `wikidata-stub` lautet; der DataCite-Wert einer Property ist über
  CodeMeta abgeleitet, nicht veröffentlicht (Spaltenüberschrift und Caption sagen das).
- **Klassenhierarchie unverifiziert.** Die Verifikation der Demo prüfte nur Label und
  Datentyp, nicht die Hierarchie; der Klassenbaum zeigt das Modell, nicht eine geprüfte
  Wikidata-Hierarchie (Caption sagt das).
- **Demo-README** zählt 63 Properties mit Item-Werten und Range, die Tabellen zählen 66
  (`model-data`, NOTE); wahrscheinlich Stand vor den neun Review-Zeilen, bei Gelegenheit in
  der Demo nachziehen.
- **Zahlen im Paper:** 153 (Pack), 158 (Demo, P100–P257), 168 (mit Kernel): im Text immer
  sagen, welche Menge gemeint ist (Befund 15).
- **Curate & Link, Export & Publish** bleiben auf Konzeptstand (A4), bis es echten
  chublets-Wikibase-Code gibt.
