# Provisional ICA Review Record — v1

Provisional review of the 25 `HUMAN_SIGNOFF_PENDING` recordings.

## Decisions

- **18 × APPROVED — PROVISIONAL**
- **7 × HOLD FOR REVIEW** (kept out of final sign-off):
  `P02_meditation`, `P08_calm`, `P08_maths`, `P08_meditation`,
  `P10_calm`, `P10_maths`, `P10_meditation`

No decision was changed by the evidence write-up; the only lean toward
approval (`P08_calm` — RECONSIDER) is recorded as a recommendation in
`hold_case_evidence_v1.md`, not applied.

## Files

| File | Contents |
| --- | --- |
| `provisional_decision_report_v1.md` | Main report, sections 1–11 (scope/provenance, sources, verification, metrics, rationale + warnings, near-guard warnings, exclusions + speech, metric definitions, NOT AVAILABLE list, protections, files created) |
| `provisional_decision_report_v1.csv` | Same decisions as data: 25 rows × 31 columns |
| `hold_case_evidence_v1.md` | Detailed evidence per HOLD case: metrics tables with sources, topography/time-course/spectrum readings, evidence for/against artifact, missing evidence, resolution checks, recommendation |
| `hold_case_metrics_v1.csv` | Per-HOLD-case metric roll-up (7 rows) |
| `hold_component_metrics_v1.csv` | Per-removed-component rows for the HOLD cases (16 rows) |
| `verification_v1.csv` | 25/25 PASS across 6 independent sources (manifest, audit, evidence index, `ica_report.json`, npz `removed_components`, metrics `removed_flag`) |
| `preserved_exclusions_v1.csv` | 5 alpha-guard exclusions, unchanged |
| `preserved_speech_not_applied_v1.csv` | 10 speech `NOT_APPLIED` rows, unchanged |
| `build_provisional_review_v1.py` | Builder (read-only inputs, SHA-256 logged) |
| `make_report_v1.py` | Report generator |
| `build_log_v1.txt` | Build log |

## Preserved unchanged

- Near-guard alpha-loss warnings: `P02_calm` 28.60%, `P06_maths` 29.43%,
  `P09_maths` 25.24%
- 5 alpha-guard exclusions
- 10 speech `NOT_APPLIED` statuses

## Protections observed

- Raw data, `*_eeg_ica.fif`, `ica_report.json`, frozen figures
  (`figures_v2\ica`), `audit_finalization_v1`, sign-off packets and review
  artifacts were **not** modified (verified via mtimes; all predate build).
- `ica_signoff_v1.csv` was **not** created anywhere.
- Phase C was **not** started.
- Missing evidence is marked `NOT AVAILABLE` with a reason; no values invented.

## Provenance

- Pending set and HOLD split: derived from
  `EEG processed\quality_control\ica_signoff_packet_v2\packet_manifest_v2.csv`
  (the user's review-table file is **NOT AVAILABLE** in the repo; derivation
  documented in report section 1).
- V7b removal rule verified in `notebooks\EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb`
  cell 80; audit metric definitions in `EEG_Audit_and_Finalization_v1.ipynb`
  cell 19 (both metric definitions reported side by side in report section 8).
