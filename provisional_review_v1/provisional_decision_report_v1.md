# Provisional ICA decision report (v1) — 25 recordings pending sign-off

**Status: PROVISIONAL REVIEW RECORD ONLY.** This file records the reviewer's provisional recommendations against the existing evidence. It is **not** a final ICA sign-off, it does not approve any recording for feature use, and it does not start Phase C. `ica_signoff_v1.csv` was **not** created.

- Report: `E:\REU_DATA\provisional_review_v1\provisional_decision_report_v1.md`
- Machine-readable rows: `E:\REU_DATA\provisional_review_v1\provisional_decision_report_v1.csv` (25 rows, 31 columns)
- HOLD detail: `E:\REU_DATA\provisional_review_v1\hold_case_evidence_v1.md`
- Verification: `E:\REU_DATA\provisional_review_v1\verification_v1.csv`

## 1. Scope

- Recordings in scope: **25** rows with `audit_disposition = HUMAN_SIGNOFF_PENDING` in `EEG processed\quality_control\ica_signoff_packet_v2\packet_manifest_v2.csv`.
- **18** recorded as **APPROVED — PROVISIONAL**, **7** kept as **HOLD FOR REVIEW**.
- **No recording is classified REJECTED.** Ambiguous evidence is never treated as rejection: the seven ambiguous cases are held instead.

### Review table provenance (`NOT AVAILABLE`)

The reviewer's own review-table file is **NOT AVAILABLE** anywhere in this repository (searched all `*.md`, `*.csv`, `*.json`, `*.txt`, `*.html`, `*.py`, `*.ipynb` for APPROVE/HOLD markers; no file holds the 18/7 split). Only the seven HOLD ids were supplied verbatim in the review instruction. The APPROVE set is therefore **derived** as *25 pending minus the 7 HOLD ids*, which reproduces the stated count of 18 exactly. If a review-table file exists elsewhere, this derivation must be reconciled against it before any final sign-off.

## 2. Sources (all opened read-only)

| Source | Used for |
|---|---|
| `audit_finalization_v1\eeg\ica_audit_v1.csv` | audit disposition, components_removed, variance/alpha recomputation, channel-level EOG metric, cross-checks, the 5 exclusions, the 10 NOT_APPLIED speech rows |
| `EEG processed\quality_control\ica_signoff_packet_v2\packet_manifest_v2.csv` | guards, near-guard flag, alpha loss, variance reduction, removal-level frontal weight, removed high-frequency fraction |
| `component_evidence_v1\component_evidence_index_v1.csv` | evidence file paths, window used, refit reproduction |
| `component_evidence_v1\component_metrics_v1.csv` | per-component `eog_corr`, `muscle_frac`, `frontal_weight`, band power fractions (500 rows = 25 x 20) |
| `EEG processed\eeg\P0x\<cond>\ica_report.json` | the original V7b criteria, component arrays, components_removed |
| `component_evidence_v1\arrays\<rec>_evidence.npz` | window traces, source/channel PSDs, removed list (used for the HOLD analysis) |
| `EEG processed\eeg\figures_v2\ica\<rec>_components.png` | frozen component topographies (viewed, never modified) |
| `component_evidence_v1\timeseries\` + `spectra\` | component time courses and power spectra (viewed, never modified) |

## 3. Verification of recording IDs and component indices

Every pending recording was checked against **six** independent sources: packet manifest, v1 audit, component-evidence index, `components_removed` in `ica_report.json`, `removed_components` inside the evidence `.npz`, and the `removed_flag` rows of `component_metrics_v1.csv`.

- Result: **25/25 PASS** — identical component indices in all six sources.
- Missing sources: **0** recordings.
- Evidence files present for all 25: time-course PNG **25/25**, spectra PNG **25/25**, frozen component map **25/25**, packet page **25/25**, `ica_report.json` **25/25**, .npz **0/25**.
- No value in this report was invented; where a quantity has no source it is marked `NOT AVAILABLE` (see section 9).

## 4. Provisional decisions — metrics (25 recordings)

Metric columns are labelled by definition (section 8): `eog max (comp)` is the largest |correlation| over the 20 component sources; `eog max (audit)` is the audit's channel-level measure on the removed activity; `fw (removal)` is the audit/manifest removal-level frontal weight; `fw (per IC)` / `muscle (per IC)` are per removed component.

| recording_id | provisional recommendation | removed ICs | eog max (comp) | eog max (audit) | fw (removal) | fw (per IC) | muscle (per IC) | alpha loss % | variance red. % |
|---|---|---|---|---|---|---|---|---|---|
| P01_calm | APPROVED — PROV. | [0, 1] | 0.708 | 0.977 | 0.508 | IC0=0.500 ; IC1=0.576 | IC0=0.010 ; IC1=0.028 | 17.01 | 65.08 |
| P01_maths | APPROVED — PROV. | [0] | 0.892 | 0.892 | 0.5 | IC0=0.500 | IC0=0.009 | 18.05 | 38.15 |
| P02_calm | APPROVED — PROV. | [0] | 0.864 | 0.864 | 0.5 | IC0=0.500 | IC0=0.007 | 28.6 | 53.28 |
| P02_maths | APPROVED — PROV. | [0] | 0.923 | 0.923 | 0.5 | IC0=0.500 | IC0=0.008 | 18.95 | 60.76 |
| P02_meditation | HOLD FOR REVIEW | [5] | 0.537 | 0.537 | 0.493 | IC5=0.493 | IC5=0.068 | 9.99 | 7.04 |
| P03_calm | APPROVED — PROV. | [0] | 0.962 | 0.962 | 0.5 | IC0=0.500 | IC0=0.010 | 14.2 | 41.64 |
| P03_maths | APPROVED — PROV. | [4] | 0.801 | 0.801 | 0.485 | IC4=0.485 | IC4=0.005 | 11.55 | 1.65 |
| P03_meditation | APPROVED — PROV. | [2] | 0.823 | 0.823 | 0.5 | IC2=0.500 | IC2=0.031 | 5.0 | 11.07 |
| P04_calm | APPROVED — PROV. | [2] | 0.789 | 0.789 | 0.5 | IC2=0.500 | IC2=0.035 | 21.92 | 17.37 |
| P04_maths | APPROVED — PROV. | [1] | 0.918 | 0.918 | 0.5 | IC1=0.500 | IC1=0.015 | 14.86 | 26.75 |
| P05_calm | APPROVED — PROV. | [0] | 0.931 | 0.931 | 0.5 | IC0=0.500 | IC0=0.008 | 24.61 | 44.64 |
| P05_maths | APPROVED — PROV. | [0] | 0.957 | 0.957 | 0.5 | IC0=0.500 | IC0=0.005 | 11.11 | 67.34 |
| P05_meditation | APPROVED — PROV. | [0] | 0.904 | 0.904 | 0.5 | IC0=0.500 | IC0=0.016 | 1.72 | 33.32 |
| P06_calm | APPROVED — PROV. | [0] | 0.948 | 0.948 | 0.5 | IC0=0.500 | IC0=0.004 | 23.68 | 47.23 |
| P06_maths | APPROVED — PROV. | [0] | 0.988 | 0.988 | 0.5 | IC0=0.500 | IC0=0.002 | 29.43 | 76.15 |
| P06_meditation | APPROVED — PROV. | [1] | 0.871 | 0.871 | 0.5 | IC1=0.500 | IC1=0.038 | 0.64 | 20.65 |
| P07_calm | APPROVED — PROV. | [0] | 0.952 | 0.952 | 0.5 | IC0=0.500 | IC0=0.009 | 1.01 | 42.78 |
| P07_maths | APPROVED — PROV. | [0] | 0.978 | 0.978 | 0.5 | IC0=0.500 | IC0=0.003 | -2.52 | 72.52 |
| P08_calm | HOLD FOR REVIEW | [0, 1] | 0.662 | 0.883 | 0.508 | IC0=0.571 ; IC1=0.500 | IC0=0.012 ; IC1=0.012 | -2.15 | 47.75 |
| P08_maths | HOLD FOR REVIEW | [2, 3, 4] | 0.618 | 0.898 | 0.544 | IC2=0.618 ; IC3=0.500 ; IC4=0.618 | IC2=0.026 ; IC3=0.022 ; IC4=0.038 | 12.8 | 18.87 |
| P08_meditation | HOLD FOR REVIEW | [2, 5] | 0.518 | 0.717 | 0.5 | IC2=0.523 ; IC5=0.483 | IC2=0.065 ; IC5=0.102 | 10.56 | 18.09 |
| P09_maths | APPROVED — PROV. | [0] | 0.96 | 0.96 | 0.5 | IC0=0.500 | IC0=0.007 | 25.24 | 57.95 |
| P10_calm | HOLD FOR REVIEW | [0, 1, 2] | 0.617 | 0.93 | 0.516 | IC0=0.561 ; IC1=0.580 ; IC2=0.500 | IC0=0.018 ; IC1=0.140 ; IC2=0.035 | 8.01 | 75.27 |
| P10_maths | HOLD FOR REVIEW | [0, 1, 2] | 0.59 | 0.912 | 0.542 | IC0=0.601 ; IC1=0.500 ; IC2=0.610 | IC0=0.047 ; IC1=0.035 ; IC2=0.067 | 7.83 | 61.97 |
| P10_meditation | HOLD FOR REVIEW | [0, 1] | 0.6 | 0.82 | 0.567 | IC0=0.628 ; IC1=0.489 | IC0=0.046 ; IC1=0.042 | -10.23 | 49.12 |

## 5. Provisional decisions — rationale and unresolved issues (25 recordings)

| recording_id | rationale | warnings_or_unresolved |
|---|---|---|
| P01_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 17.01% <= 30%, variance reduction 65.08% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=-0.708 >= 0.40, fw=0.500 >= 0.35); IC1 (abs r=0.674 >= 0.40, fw=0.576 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | two different EOG metrics on this recording: audit channel-level max abs r=0.977 vs component-level max abs r=0.708 (different definitions, see report section 8) |
| P01_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 18.05% <= 30%, variance reduction 38.15% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.892 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P02_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 28.60% <= 30%, variance reduction 53.28% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.864 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Near-guard warning preserved: posterior alpha loss 28.60% (25% < loss <= 30%, guard 30%) — legal but sits close to the guard. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | near-guard alpha loss 28.60% (25% < loss <= 30%, guard = 30%) |
| P02_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 18.95% <= 30%, variance reduction 60.76% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.923 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P02_meditation | HOLD FOR REVIEW (reviewer instruction). Removal of [5] satisfies the documented V7b rule — IC5 (abs r=0.537 >= 0.40, fw=0.493 >= 0.35) — and all four packet guards PASS (alpha loss 9.99%, variance 7.04%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.537) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |
| P03_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 14.20% <= 30%, variance reduction 41.64% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=-0.962 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P03_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 11.55% <= 30%, variance reduction 1.65% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC4 (abs r=0.801 >= 0.40, fw=0.485 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P03_meditation | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 5.00% <= 30%, variance reduction 11.07% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC2 (abs r=-0.823 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P04_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 21.92% <= 30%, variance reduction 17.37% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC2 (abs r=-0.789 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P04_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 14.86% <= 30%, variance reduction 26.75% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC1 (abs r=0.918 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P05_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 24.61% <= 30%, variance reduction 44.64% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.931 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P05_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 11.11% <= 30%, variance reduction 67.34% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.957 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P05_meditation | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 1.72% <= 30%, variance reduction 33.32% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=-0.904 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P06_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 23.68% <= 30%, variance reduction 47.23% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.948 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P06_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 29.43% <= 30%, variance reduction 76.15% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=-0.988 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Near-guard warning preserved: posterior alpha loss 29.43% (25% < loss <= 30%, guard 30%) — legal but sits close to the guard. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | near-guard alpha loss 29.43% (25% < loss <= 30%, guard = 30%) |
| P06_meditation | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 0.64% <= 30%, variance reduction 20.65% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC1 (abs r=0.871 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P07_calm | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 1.01% <= 30%, variance reduction 42.78% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=-0.952 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P07_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss -2.52% <= 30%, variance reduction 72.52% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=0.978 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | none |
| P08_calm | HOLD FOR REVIEW (reviewer instruction). Removal of [0, 1] satisfies the documented V7b rule — IC0 (abs r=-0.662 >= 0.40, fw=0.571 >= 0.35); IC1 (abs r=0.587 >= 0.40, fw=0.500 >= 0.35) — and all four packet guards PASS (alpha loss -2.15%, variance 47.75%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.662) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | two different EOG metrics on this recording: audit channel-level max abs r=0.883 vs component-level max abs r=0.662 (different definitions, see report section 8); HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |
| P08_maths | HOLD FOR REVIEW (reviewer instruction). Removal of [2, 3, 4] satisfies the documented V7b rule — IC2 (abs r=-0.618 >= 0.40, fw=0.618 >= 0.35); IC3 (abs r=-0.505 >= 0.40, fw=0.500 >= 0.35); IC4 (abs r=0.419 >= 0.40, fw=0.618 >= 0.35) — and all four packet guards PASS (alpha loss 12.80%, variance 18.87%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.618) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | two different EOG metrics on this recording: audit channel-level max abs r=0.898 vs component-level max abs r=0.618 (different definitions, see report section 8); HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |
| P08_meditation | HOLD FOR REVIEW (reviewer instruction). Removal of [2, 5] satisfies the documented V7b rule — IC2 (abs r=-0.518 >= 0.40, fw=0.523 >= 0.35); IC5 (abs r=0.498 >= 0.40, fw=0.483 >= 0.35) — and all four packet guards PASS (alpha loss 10.56%, variance 18.09%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.518) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | two different EOG metrics on this recording: audit channel-level max abs r=0.717 vs component-level max abs r=0.518 (different definitions, see report section 8); HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |
| P09_maths | APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss 25.24% <= 30%, variance reduction 57.95% < 80%, EOG and frontal guards PASS) and every removed component meets the documented removal rule — IC0 (abs r=-0.960 >= 0.40, fw=0.500 >= 0.35). Audit/manifest/evidence/ica_report component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK. Near-guard warning preserved: posterior alpha loss 25.24% (25% < loss <= 30%, guard 30%) — legal but sits close to the guard. Provisional only: the reviewer's approval does not finalise the recording; `ica_signoff_v1.csv` is not written by this pass. | near-guard alpha loss 25.24% (25% < loss <= 30%, guard = 30%) |
| P10_calm | HOLD FOR REVIEW (reviewer instruction). Removal of [0, 1, 2] satisfies the documented V7b rule — IC0 (abs r=0.484 >= 0.40, fw=0.561 >= 0.35); IC1 (abs r=-0.617 >= 0.40, fw=0.580 >= 0.35); IC2 (abs r=0.502 >= 0.40, fw=0.500 >= 0.35) — and all four packet guards PASS (alpha loss 8.01%, variance 75.27%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.617) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | two different EOG metrics on this recording: audit channel-level max abs r=0.930 vs component-level max abs r=0.617 (different definitions, see report section 8); HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |
| P10_maths | HOLD FOR REVIEW (reviewer instruction). Removal of [0, 1, 2] satisfies the documented V7b rule — IC0 (abs r=-0.590 >= 0.40, fw=0.601 >= 0.35); IC1 (abs r=-0.499 >= 0.40, fw=0.500 >= 0.35); IC2 (abs r=-0.486 >= 0.40, fw=0.610 >= 0.35) — and all four packet guards PASS (alpha loss 7.83%, variance 61.97%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.59) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | two different EOG metrics on this recording: audit channel-level max abs r=0.912 vs component-level max abs r=0.590 (different definitions, see report section 8); HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |
| P10_meditation | HOLD FOR REVIEW (reviewer instruction). Removal of [0, 1] satisfies the documented V7b rule — IC0 (abs r=0.600 >= 0.40, fw=0.628 >= 0.35); IC1 (abs r=0.559 >= 0.40, fw=0.489 >= 0.35) — and all four packet guards PASS (alpha loss -10.23%, variance 49.12%), but the component-level evidence is not yet conclusive: the removed sources are only moderately EOG-correlated (max /r/ = 0.6) and the topography / time-course / spectrum reading for this recording is unresolved. Full evidence, checks and a retain/reconsider recommendation are in `hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved. | two different EOG metrics on this recording: audit channel-level max abs r=0.820 vs component-level max abs r=0.600 (different definitions, see report section 8); HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved |

## 6. Preserved warnings — near-guard alpha loss

These three warnings are reproduced **unchanged** and are not treated as failures; all three recordings still sit under the 30% audit guard.

| recording_id | alpha_loss_pct | guard | flag | components_removed | provisional_recommendation | carried_into_this_report |
|---|---|---|---|---|---|---|
| P02_calm | 28.60 | PASS (<= 30%) | near_guard_flag = YES | [0] | APPROVED — PROVISIONAL | YES - unchanged |
| P06_maths | 29.43 | PASS (<= 30%) | near_guard_flag = YES | [0] | APPROVED — PROVISIONAL | YES - unchanged |
| P09_maths | 25.24 | PASS (<= 30%) | near_guard_flag = YES | [0] | APPROVED — PROVISIONAL | YES - unchanged |

## 7. Preserved exclusions and preserved speech statuses

### 7.1 Alpha-guard exclusions — **5**, unmodified, confirm-only

| recording_id | removed ICs | alpha loss % | variance red. % | alpha guard | eog guard | frontal guard | variance guard | unchanged by this pass |
|---|---|---|---|---|---|---|---|---|
| P01_meditation | [0, 2, 6] | 77.88 | 43.29 | FAIL | PASS | PASS | PASS | YES |
| P04_meditation | [0, 1, 7] | 87.58 | 35.4 | FAIL | PASS | PASS | PASS | YES |
| P07_meditation | [0, 1] | 63.7 | 99.8 | FAIL | PASS | PASS | FAIL | YES |
| P09_calm | [3] | 40.17 | 10.15 | FAIL | PASS | PASS | PASS | YES |
| P09_meditation | [8, 14] | 86.63 | 4.56 | FAIL | PASS | PASS | PASS | YES |

### 7.2 Speech-condition EEG `NOT_APPLIED` — **10**, unmodified

| recording_id | status | reason | unchanged by this pass |
|---|---|---|---|
| P01_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P02_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P03_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P04_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P05_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P06_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P07_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P08_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P09_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |
| P10_speech | NOT_APPLIED | no ICA output (speech condition - too short for reliable ICA) | YES |

## 8. Metric definitions used in this report

| Column | Definition | Source |
|---|---|---|
| `eog max (comp)` | max abs Pearson r between each of the 20 ICA sources and the EOG proxy (Fp1/Fpz/Fp2 mean), full recording | `component_metrics_v1.csv` / `ica_report.json` |
| `eog max (audit)` | max abs r between **each channel of the removed activity** (cleaned minus ICA file) and the EOG proxy — a different quantity, computed channel-wise | `ica_audit_v1.csv` |
| `fw (removal)` | frontal weight of the dominant eigenvector of the removal's covariance (removal is rank-1) | `ica_audit_v1.csv` / manifest |
| `fw (per IC)` | sum of \|weight\| over the 8 frontal electrodes / over all 24, for that component's topography | `component_metrics_v1.csv` |
| `muscle (per IC)` | fraction of that component's source power in 30-45 Hz | `component_metrics_v1.csv` |
| `alpha loss %` | posterior (O1/O2/Oz) 8-12 Hz power change after ICA, sign-flipped so loss is positive | manifest / audit |
| `variance red. %` | channel-space variance removed by the ICA step | manifest / audit |

The two EOG columns and the two frontal-weight columns are **not interchangeable**. They coincide on 18 of the 25 recordings and differ on 7 (P01_calm, P08_calm, P08_maths, P08_meditation, P10_calm, P10_maths, P10_meditation); both values are shown rather than reconciled, because they answer different questions and neither is wrong.

## 9. Values marked `NOT AVAILABLE`

| Item | Status | Why |
|---|---|---|
| Reviewer's review-table file (the 18 APPROVE marks) | NOT AVAILABLE | not present anywhere in the repository; APPROVE set derived as 25 pending minus the 7 listed HOLD ids (see section 1) |
| Muscle fraction at recording level | NOT AVAILABLE | no recording-level muscle metric exists in the audit or manifest; only per-component `muscle_frac` (reported per removed IC) and the audit's `removed_hf_fraction` are available, both are reported |
| Any ICA topography not already frozen in `figures_v2\ica\` | NOT AVAILABLE | no ICA object was ever saved; topographies exist only as the 30 frozen PNGs (documented in `component_evidence_v1\README.md`) |
| Component-level metrics for conditions without ICA (speech) | NOT AVAILABLE | ICA never applied (< 2 min), by design |

## 10. Protections observed by this pass

- Raw data under `P01`-`P10`: **not modified**.
- Existing ICA files (`*_eeg_ica.fif`), `ica_report.json`, frozen figures in `EEG processed\eeg\figures_v2\`: **not modified**.
- v1 audit (`audit_finalization_v1\`) and both sign-off packets (`ica_signoff_packet*`, `ica_signoff_packet_v2_review.zip`): **not modified, not overwritten**.
- Existing review artefacts (`review_plan_v1\`, `review_contact_sheets_v1\`, `component_evidence_v1\`, `reports_final_v3\`): **not modified**.
- `ica_signoff_v1.csv`: **not created**. Phase C: **not started**.
- Everything written by this pass lives in `E:\REU_DATA\provisional_review_v1\`.

## 11. Files created by this pass

| File | Contents |
|---|---|
| `provisional_decision_report_v1.md` | this report |
| `provisional_decision_report_v1.csv` | 25 rows x 31 columns, decisions + metrics + rationale + warnings + evidence paths |
| `hold_case_evidence_v1.md` | detailed evidence for the 7 HOLD recordings |
| `hold_component_metrics_v1.csv` | 16 removed-component rows for the 7 HOLD recordings, with window correlations and alpha shares |
| `hold_case_metrics_v1.csv` | 7 HOLD roll-up rows (quantitative evidence used in the HOLD write-up) |
| `verification_v1.csv` | 25 rows: six-source component-index cross-check + evidence-file presence |
| `preserved_exclusions_v1.csv` | the 5 alpha-guard exclusions, copied unchanged |
| `preserved_speech_not_applied_v1.csv` | the 10 speech `NOT_APPLIED` rows, copied unchanged |
| `build_provisional_review_v1.py` | read-only builder for the CSVs + verification |
| `make_report_v1.py` | renders this markdown from the CSVs |
| `build_log_v1.txt` | run log with source SHA-256 hashes |
| `README.md` | folder index and re-run instructions |

---

*Generated by `make_report_v1.py` from the verified CSVs in this folder. Provisional record only — awaiting reviewer sign-off before any final decision file is written.*
