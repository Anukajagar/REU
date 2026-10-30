# signoff_finalization_v2 — deliverables index

**Pass date:** 2026-10-13. **Nothing outside this folder and the two new
notebooks was created, modified, or deleted** (SHA-256 verified, 0 changes to
1,103 pre-existing files).

## The sign-off workflow (what a human does next)

1. Open `E:\REU_DATA\notebooks\EEG_ICA_Signoff_Review_v1.ipynb` (kernel with
   pandas + IPython; no MNE needed — figures are PNGs).
2. For each of the 30 ICA recordings, call `show_recording("P02_calm")` etc.
   You get: the review-table evidence text, the component map, timecourse,
   spectrum, and the new before/after waveform+PSD figure, plus all metrics.
3. Record decisions with
   `record_decision(rid, "APPROVED"|"REJECTED"|"NEEDS_REVIEW", reviewer, review_date, comments_add=...)`.
   Guards: no anonymous decisions, valid date required, excluded recordings
   cannot be approved without explicit reinstatement evidence in the comments.
4. Run the validation-gate cell at any time; it prints remaining pendings.

Suggested review order: the 5 exclusion confirmations first, then the 7 HOLD
cases, then the 3 near-guard recordings, then the rest.

## Files

| Path | Purpose |
|---|---|
| `ica_review_table_v1.csv` | Formal review table (required schema; all 30 rows `NEEDS_REVIEW`) |
| `ica_review_context_v1.csv` | Metrics + absolute evidence paths per recording |
| `beforeafter_evidence_v1\` | 30 new before/after ICA figures + index (built read-only from saved `.fif`) |
| `eeg_qc_summary_v2.csv` / `.md` | Updated 50-row QC summary; counts recomputed, not forced to PASS |
| `qc_issue_classification_v2.csv` / `.md` | 20 QC issues classified (resolved / human review / correction / waiver) |
| `scripts\` | All builders + validator (each refuses to overwrite its outputs) |
| `validation_results_v2.csv` | V1–V8 results (8 PASS) |
| `CHANGE_LOG.md` · `VALIDATION_REPORT.md` · `MENTOR_SUMMARY.md` | Pass documentation |
| `..\notebooks\EEG_ICA_Signoff_Review_v1.ipynb` | Human review interface |
| `..\notebooks\EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb` | Finalized notebook (v3 frozen cells + V10 status section) |

## Evidence bundles from earlier passes (read-only, referenced by the table)

`ica_visual_review_bundle_v1\` (maps/timecourses/spectra) ·
`component_evidence_v1\` (per-component metrics, npz) ·
`review_contact_sheets_v1\` · `provisional_review_v2\` (prior recommendations) ·
`EEG processed\eeg\figures_v2\ica\` (frozen maps) ·
`audit_finalization_v1\` (independent audit) ·
`EEG processed\quality_control\` (sampling-rate verification, sign-off packets)

## Regenerating outputs

Every `scripts\build_*.py` refuses to overwrite its output files (delete the
specific output deliberately if a rebuild is truly wanted). `validate_finalization_v2.py`
expects fresh `hashes_before/after.json` snapshots (temp dir) — rerun the hash
script first if the protected tree changed for an unrelated reason.
