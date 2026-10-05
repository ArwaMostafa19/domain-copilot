# Synthetic corpus: D5 industrial field maintenance

All content in this directory is **synthetic**. Alpha Manufacturing and Beta
Manufacturing are fictional organisations created for this project. There is no
real company, site, asset, person or service in this corpus, and there are no
credentials or personal data.

The corpus exists to exercise the future ingestion, retrieval and answer
pipeline for the workflow:

```text
symptom -> identify equipment and manual revision -> diagnostic sequence
        -> safety prerequisites -> work order
```

## Layout

```text
corpus/
  manifest.json                       generated index of every document
  tenant-alpha/                       15 documents, metric, Ridgeway Works
  tenant-beta/                        15 documents, imperial, Harbor Works
```

Every document is Markdown with a metadata front matter block. The same
metadata is repeated as a document control table inside the document body, so a
reader that ignores front matter still sees tenant, equipment, type, revision,
effective date and status.

Six of the documents are also committed as PDF next to their Markdown source,
with the same base name, so the corpus offers a second input format:

| PDF sample | Rendered from | Why this one |
| --- | --- | --- |
| `tenant-alpha/hydraulic-press-manual-rev-a.pdf` | `hydraulic-press-manual-rev-a.md` | superseded revision, to test conflict handling across formats |
| `tenant-alpha/hydraulic-press-manual-rev-b.pdf` | `hydraulic-press-manual-rev-b.md` | current equipment manual, longest document |
| `tenant-alpha/hydraulic-press-lockout-tagout.pdf` | `hydraulic-press-lockout-tagout.md` | numbered safety procedure |
| `tenant-beta/hydraulic-press-manual-rev-b.pdf` | `hydraulic-press-manual-rev-b.md` | imperial equivalent of the same equipment |
| `tenant-beta/hydraulic-press-energy-control.pdf` | `hydraulic-press-energy-control.md` | different isolation sequence, different tag colour |
| `tenant-beta/chiller-alarm-troubleshooting.pdf` | `chiller-alarm-troubleshooting.md` | alarm codes that do not exist in the Alpha corpus |

Markdown stays the source of truth. `manifest.json` lists the samples under
`format_samples` with the sha256 of the PDF bytes, and `--check` re-renders them
and fails if a committed PDF is stale or unexpected.

| Tenant | Site | Unit system | Documents | Source series |
| --- | --- | --- | --- | --- |
| `tenant-alpha` | Ridgeway Works, Building 2 | bar, mm, N.m, l/min | 15 | `AM-DOC-####` |
| `tenant-beta` | Harbor Works, Line 1 | psi, in, lbf.ft, gpm | 15 | `BM-DOC-####` |

## Regenerating

The corpus is generated, not hand maintained. The generator is deterministic:
no randomness, no network, no third party dependency.

```bash
python scripts/generate_corpus.py           # rewrite the corpus and manifest
python scripts/generate_corpus.py --check   # fail if the committed corpus is stale
```

`tests/unit/test_corpus.py` runs `--check` plus the corpus invariants, so a
drift between the generator and the committed files fails CI.

Editing the corpus means editing `scripts/corpus_docs_alpha.py` or
`scripts/corpus_docs_beta.py` and regenerating, never editing the Markdown
files directly.

## Second input format

Markdown is the canonical, committed format. PDF is the second format: six
representative documents are committed as samples, and the dependency free
exporter can render all 30 on demand for parser fixtures.

```bash
python scripts/export_corpus_pdf.py                       # corpus/_export/pdf
python scripts/export_corpus_pdf.py --tenant tenant-alpha --out build/pdf
```

The output is byte identical on every run, so the PDF rendition can be used as a
reproducible fixture for a second parser. The bulk export is not committed;
`corpus/_export/` is git ignored.

## How the page count is measured

The page count is measured by exporting every Markdown document and reading the
total the exporter prints:

```bash
python scripts/export_corpus_pdf.py
```

The current run prints `30 documents, 151 pages`. The 30 Markdown documents
contain 65,669 words, counted as whitespace-delimited tokens across the
generated Markdown (`len(text.split())` per document). Page count depends on the
exporter layout, while the word count is the layout-independent measure.

## Revision pairs

Two documents per tenant exist in two revisions with **different values**, not
just a different revision label. The superseded revision carries
`status: "superseded"` in metadata; its body contains no pointer to the newer
revision, so a system that ignores revision and effective date metadata will
quote the wrong number.

| Document | Rev A | Rev B |
| --- | --- | --- |
| Alpha hydraulic press manual | `2023-03-01` | `2025-06-01` |
| Alpha hydraulic press PM | `2023-04-15` | `2025-07-01` |
| Alpha overhead crane manual | `2022-11-01` | `2025-02-10` |
| Beta hydraulic press manual | `2023-01-20` | `2025-05-15` |
| Beta hydraulic press PM | `2023-02-10` | `2025-06-01` |
| Beta overhead crane manual | `2022-12-05` | `2025-03-01` |

## Deliberately difficult cases

| Case | Where |
| --- | --- |
| Conflicting revisions: relief set point 240 bar (Rev A) vs 210 bar (Rev B) | `tenant-alpha/hydraulic-press-manual-rev-a.md`, `...-rev-b.md` |
| Conflicting revisions: oil analysis 500 h vs 300 h | same pair |
| Conflicting revisions: 2000 psi vs 1750 psi, tie rod 3000 h vs 1500 h | `tenant-beta/hydraulic-press-*` |
| Conflicting revisions: rope discard 8 vs 6 wires, deflection 25 mm vs 20 mm, hoist 8 m/min vs 6 m/min above 3.0 t | `tenant-alpha/overhead-crane-manual-rev-a.md`, `...-rev-b.md` |
| Conflicting revisions: rope discard 8 vs 6 wires, deflection 30 mm vs 22 mm, hoist 26 ft/min vs 16 ft/min above 2.0 t, hook height 12 ft vs 11 ft 6 in | `tenant-beta/overhead-crane-manual-rev-a.md`, `...-rev-b.md` |
| Missing information: ball screw pre-load not specified, only a commissioning sheet reference | `tenant-alpha/machining-centre-lubrication-schedule.md` |
| Missing information: P-100A accumulator pre-charge, HP-200B grease quantity, brake shims, work instruction WI-2204, rope replacement procedure AM-PM-OC5T-ROPE | several |
| Ambiguous symptoms: unstable pressure with 7 to 8 candidate causes that need specific measurements to separate | `tenant-alpha/hydraulic-press-troubleshooting-guide.md`, `tenant-beta/hydraulic-press-troubleshooting-guide.md` |
| Ambiguous symptoms: intermittent chiller trip, compressor high temperature trip, crane will not hold load | both `chiller-*`, `air-compressor-*`, crane inspection |
| Safety critical prerequisites: six step isolation, accumulator bled below 5 bar (10 psi), mechanical block, attempt start, two person countersignature | `tenant-alpha/hydraulic-press-lockout-tagout.md`, `tenant-beta/hydraulic-press-energy-control.md` |
| Safety critical prerequisites: no person under a suspended load, calibrated test weights only, never a vehicle as a test load | both `overhead-crane-inspection-procedure.md` |
| Safety critical prerequisites: no diagnostic step before zero energy verification, "a diagnostic measurement is never a reason to work with the circuit charged" | both `hydraulic-power-unit-diagnostic-procedure.md` |
| Similar equipment names: HP-200, HP-200B, HP-210, HP-200S, HP-250, HP-100, OC-5T, OC-5TS, OC-5TL, GM-45, GM-45S, AC-75/AC-75S, CNC-3X/CNC-3XL, P-100/P-110 | several |
| Tenant specific facts: pressure limits, intervals, alarm codes, lubricant grades, belt ply, unit system | see below |

### Tenant specific facts that must not leak

| Fact | Alpha | Beta |
| --- | --- | --- |
| Press frame and rating | four post, 2000 kN | H-frame, 160 tons |
| Press relief set point (current) | 210 bar | 1750 psi |
| Max working pressure | 205 bar | 1650 psi |
| Minimum tool clamp pressure | 180 bar, clamp circuit | 1800 psi |
| Press safeguard | monitored two-hand control, 900 ms hold to run | light curtain, 1000 ms hold to run, muting prohibited |
| Oil analysis interval (current) | every 300 running hours | every 500 running hours |
| Stored energy on the press | nitrogen accumulator AC-1, as-built pre-charge, bleed to 5 bar | accumulator AC-2, 1000 psi pre-charge, bleed to 10 psi, plus a 1 in die cushion |
| Chiller controller codes | A-series, e.g. A01 high head pressure | F, H and E series, e.g. F-13 high head pressure |
| Chiller ambient limit | 32 degC | 95 degF |
| Chiller glycol, minimum | 20 percent | 25 percent |
| Compressor lubricant | synthetic ester AM-CO-100S | mineral BM-1160 |
| Compressor nominal pressure | 8.0 bar | 120 psi |
| Machining centre way lube | ISO VG 68 | ISO VG 46 |
| Spindle re-greasing interval | 2000 running hours | 3000 running hours |
| Conveyor belt | 18 mm, 2 ply, sag 1.5 percent | 3/4 in, 3 ply, sag 2 percent |
| Gearmotor ratio and oil | i = 25, 1.8 l | i = 30, 2.2 l |
| Crane span | 5.0 t at 14.6 m | 5.0 t at 59 ft |
| Crane control | pendant sockets along the runway | radio pendant with control zone check |
| Max hook height (current) | 4.2 m | 11 ft 6 in |
| Backlash acceptance | not specified anywhere in the Alpha corpus | 0.03 mm verified monthly |

## Documents that are referenced but not in this corpus

The corpus deliberately references controlled documents that do not exist here,
because "the manual is silent" has to be demonstrable. Documents that are part
of this corpus are named by their canonical `ALPHA-*` / `BETA-*` identifier in
`corpus/manifest.json`. Documents that are referenced but deliberately absent
are named by their customer source-register identifier (`AM-*` / `BM-*`), which
is what the source records use. The absent set is:

`AM-MAN-HP210`, `AM-SAF-HP210-LOTO-1`, `AM-PM-HP200`, `AM-PM-HP200B`,
`AM-PM-CV200-LOCK`, `AM-PM-OC5T-ROPE`, `AM-MAN-AC75-1`, `AM-MAN-CH450-1`,
`AM-MAN-CV200-1`, `AM-MAN-CNC3X-1`, `BM-PM-HP200`, `BM-MAN-AC90-1`,
`BM-MAN-CH450-1`, `BM-MAN-CV200-1`, `BM-MAN-CNC3X-1`, `BM-PM-OC5T-ROPE`,
`BM-PM-OC5T-LIMIT`, `WI-2204`, commissioning sheets `CM-HP200-01` and
`CM-CNC3X-01`, the asset register, the lifting equipment register and the
pressure vessel register.

`AM-PM-HP200` and `BM-PM-HP200` name the press preventive-maintenance
programme as a whole rather than a single revision; in this corpus that
programme is `ALPHA-PM-HP200-A`, `ALPHA-PM-HP200-B`, `BETA-PM-HP200-A` and
`BETA-PM-HP200-B`. The programme-level reference is used only where the source
record does not pin a revision.

A question whose answer only exists in one of those must be answered with
"not enough information in the corpus", never with a value read elsewhere.