# ICA Visual Review Bundle v1

**Purpose:** Self-contained, read-only evidence bundle for external human visual review of ICA component rejection across 30 recordings. Built for review in ChatGPT (or any viewer) **before** sign-off. This bundle assigns **no verdicts** and contains **no sign-off decisions**.

**Created:** 2026-10-13
**Bundle root:** `E:\REU_DATA\ica_visual_review_bundle_v1\`

---

## What this bundle is (and is not)

| Is | Is NOT |
|---|---|
| Copies of **existing** frozen figures | Regenerated or re-run ICA outputs |
| A manifest of **existing** QC metrics | A sign-off record (`ica_signoff_v1.csv`) |
| A convenience package for external review | A decision document, Phase C artifact, or new QC table |
| Read-only with respect to all source data | A modification of any raw/cleaned EEG, ICA, figures, notebooks, QC, or audit files |

No source file was modified, overwritten, or regenerated to produce this bundle. All figure PNGs are byte-identical copies of the frozen originals; all metric values are copied verbatim from the existing QC manifest (see *Provenance*).

---

## Folder structure

```
ica_visual_review_bundle_v1\
├── README.md                                   ← this file
├── manifest\
│   └── ica_visual_review_manifest_v1.csv       ← 30 rows (one per recording)
├── component_maps\                             ← 30 PNGs (all recordings)
│   └── <recording_id>_components.png
├── timecourses\                                ← 25 PNGs (pending recordings only)
│   └── <recording_id>_component_timecourses.png
└── spectra\                                    ← 25 PNGs (pending recordings only)
    └── <recording_id>_component_spectra.png
```

`<recording_id>` = `<participant>_<condition>` (e.g. `P01_calm`, `P09_meditation`).

**Total figures:** 80 PNGs (30 component maps + 25 time courses + 25 power spectra).

---

## The 30 recordings at a glance

- **25 pending** human sign-off (`status = pending`): full evidence (component map + time course + spectrum).
- **5 previously excluded** (`status = previously_excluded`): `P01_meditation`, `P04_meditation`, `P07_meditation`, `P09_calm`, `P09_meditation`. For these, **only the component map and metrics are available** — time-course and power-spectrum figures were never built for the excluded set and are recorded as `NOT AVAILABLE` in the manifest.

---

## Matching a recording's figures to its metrics

1. Open `manifest\ica_visual_review_manifest_v1.csv` (UTF-8, comma-separated, header row).
2. Each row is one recording, keyed by `recording_id`.
3. The three figure columns give **relative paths** inside this bundle:
   - `component_map_figure` → e.g. `component_maps\P01_calm_components.png`
   - `timecourse_figure` → e.g. `timecourses\P01_calm_component_timecourses.png` (or `NOT AVAILABLE`)
   - `spectrum_figure` → e.g. `spectra\P01_calm_component_spectra.png` (or `NOT AVAILABLE`)
4. Join those relative paths to the bundle root to open the figure. The metric columns on the same row describe that recording.

### Manifest column dictionary

| Column | Meaning | Source |
|---|---|---|
| `recording_id` | `<participant>_<condition>` | derived key |
| `participant` | Participant ID (`P01`–`P10`) | packet manifest |
| `condition` | `calm` / `meditation` / `maths` | packet manifest |
| `status` | `pending` or `previously_excluded` | from `audit_disposition` |
| `components_removed` | ICA component indices removed (JSON-style list) | packet manifest |
| `eog_corr_max` | Max EOG correlation among components | packet manifest |
| `frontal_weight` | Frontal weight metric | packet manifest |
| `removed_hf_fraction` | High-frequency (muscle) fraction of removed activity | packet manifest |
| `alpha_loss_pct` | Posterior alpha loss % (negative = alpha gain) | packet manifest |
| `alpha_guard` | Alpha guard result (`PASS`/`FAIL`) | packet manifest |
| `eog_guard` | EOG guard result (`PASS`/`FAIL`) | packet manifest |
| `frontal_guard` | Frontal guard result (`PASS`/`FAIL`) | packet manifest |
| `variance_guard` | Variance guard result (`PASS`/`FAIL`) | packet manifest |
| `guards_all_pass` | `PASS` only if all four guards pass | packet manifest |
| `near_guard_flag` | `YES` if alpha loss is in the near-guard band (25–30%) | packet manifest |
| `variance_reduction_pct` | Variance reduced by ICA removal (%) | packet manifest |
| `component_map_figure` | Relative path to component-map PNG | bundle path |
| `timecourse_figure` | Relative path to time-course PNG, or `NOT AVAILABLE` | bundle path |
| `spectrum_figure` | Relative path to power-spectrum PNG, or `NOT AVAILABLE` | bundle path |

> Note: `removed_hf_fraction` is the recording-level muscle/high-frequency fraction of removed activity. Per-component muscle fractions are not restated here; they live in the original per-component metrics table (see *Provenance*).

---

## How to read each figure type

- **Component map** (`*_components.png`): ICA component topographies (20 components). The removed component indices (from `components_removed`) are the ones to scrutinize — they should look ocular/frontal, not cortical alpha or muscle.
- **Time course** (`*_component_timecourses.png`): Time-series snippets of components. Useful for spotting residual artifact, edge transients, or whether a removed component carries sustained brain signal.
- **Power spectrum** (`*_component_spectra.png`): Per-component PSDs. Useful for checking whether removed components carry muscle (high-frequency) or alpha (8–12 Hz) power — key context for interpreting `alpha_loss_pct`.

---

## Missing evidence (explicitly recorded, not invented)

The following required figures/metrics do **not** exist for the 5 previously excluded recordings and are recorded as `NOT AVAILABLE`. Nothing was regenerated to fill these gaps.

| Recording | Component map | Time course | Spectrum | Metrics |
|---|---|---|---|---|
| `P01_meditation` | ✔ available | **NOT AVAILABLE** | **NOT AVAILABLE** | ✔ available |
| `P04_meditation` | ✔ available | **NOT AVAILABLE** | **NOT AVAILABLE** | ✔ available |
| `P07_meditation` | ✔ available | **NOT AVAILABLE** | **NOT AVAILABLE** | ✔ available |
| `P09_calm` | ✔ available | **NOT AVAILABLE** | **NOT AVAILABLE** | ✔ available |
| `P09_meditation` | ✔ available | **NOT AVAILABLE** | **NOT AVAILABLE** | ✔ available |

These five were excluded in an earlier pass (alpha-guard failures; `P07_meditation` also failed the variance guard at 99.8%). The evidence set was only ever built for the 25 pending recordings, so time-course/spectrum figures were never created for the excluded five. Their exclusion can be reviewed from the component map + metrics alone.

---

## Provenance

| Artifact in this bundle | Read-only source |
|---|---|
| `component_maps\*.png` | `EEG processed\eeg\figures_v2\ica\` (30 frozen PNGs) |
| `timecourses\*.png` | `component_evidence_v1\timeseries\` (25 PNGs) |
| `spectra\*.png` | `component_evidence_v1\spectra\` (25 PNGs) |
| `manifest\ica_visual_review_manifest_v1.csv` | `EEG processed\quality_control\ica_signoff_packet_v2\packet_manifest_v2.csv` (metrics copied verbatim) |

All figure PNGs in this bundle are byte-identical copies of the frozen originals.

---

## Protections observed

- **Read-only** access to all source files (raw EEG, cleaned EEG, ICA FIFs, frozen figures, notebooks, QC tables, audit records, existing review packets).
- **No overwrites** of any existing file.
- **No** final verdicts, sign-off decisions, or `ica_signoff_v1.csv` created.
- **No** Phase C started.
- **No** regeneration of ICA, preprocessing, or evidence figures.

This bundle is for **external visual review only**. Sign-off decisions remain with the human reviewer.
