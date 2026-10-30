# Change log — signoff_finalization_v2 pass (2026-10-13)

**Scope:** finalize the EEG preprocessing documentation, complete the human ICA
sign-off *workflow* (not the sign-off itself), and re-derive QC summaries from
verified source records. Feature extraction, speech processing changes, and
Dosha classification were **not** started.

**Safety outcome:** 0 pre-existing files were modified, renamed, moved, or
deleted (proved by SHA-256 snapshot diff, 1,103 → 1,105 files; see
`validation_results_v2.csv` V8). Raw `P01`–`P10`, all `.fif`/`.json` outputs,
the frozen v3 notebook, the v1 audit, and every existing review artifact are
byte-identical to their pre-pass state.

---

## New files created (all under `E:\REU_DATA\signoff_finalization_v2\` unless noted)

| File | What it is |
|---|---|
| `scripts/hash_snapshot.py` | SHA-256 snapshot tool (run before/after; snapshots in temp, not in repo) |
| `scripts/build_ica_review_table_v1.py` | Builds the formal review table + context table (refuses overwrite) |
| `scripts/build_beforeafter_evidence_v1.py` | Builds 30 before/after ICA waveform+PSD figures read-only from saved `.fif` |
| `scripts/build_qc_summary_v2.py` | Rebuilds the 50-row QC summary + dashboard from source CSVs |
| `scripts/build_qc_issue_classification_v2.py` | Classifies 20 QC issues into 4 evidence-based classes (fact-asserted) |
| `scripts/build_review_notebook_v1.py` | Builds the human review notebook (guarded decision recording) |
| `scripts/build_notebook_v4.py` | Builds `notebooks\EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb` (v3 copy + V10) |
| `scripts/validate_finalization_v2.py` | 8-check validation suite |
| `ica_review_table_v1.csv` | **The formal ICA sign-off table** — 30 rows × required schema, all `NEEDS_REVIEW`, reviewer/date empty |
| `ica_review_context_v1.csv` | 30 rows × 32 metrics/evidence columns for the reviewer |
| `beforeafter_evidence_v1\` (30 PNG + `beforeafter_index_v1.csv`) | New before/after ICA evidence for **all 30** recordings (fills the gap: only 4 existed before) |
| `eeg_qc_summary_v2.csv` / `.md` | Updated QC summary, counts recomputed from verified sources |
| `qc_issue_classification_v2.csv` / `.md` | 20 issues: 4 RESOLVED_WITH_EVIDENCE, 4 REQUIRES_HUMAN_REVIEW, 12 DOCUMENTED_LIMITATION_OR_WAIVER |
| `validation_results_v2.csv` | V1–V8, all PASS |
| `CHANGE_LOG.md`, `VALIDATION_REPORT.md`, `MENTOR_SUMMARY.md`, `README.md` | This documentation |
| `notebooks\EEG_ICA_Signoff_Review_v1.ipynb` | Human review interface (evidence viewer + guarded `record_decision` + validation gate) |
| `notebooks\EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb` | Finalized notebook: banner + 90 frozen v3 cells (identical, **not re-executed**) + new read-only V10 sign-off status section |

## Corrections made to facts (in new files only)

1. **P07 meditation "single >5 mV transient" → two transients.** The register
   shows two >5 mV windows (Fpz, 23.35 mV at 215–219 s and 23.33 mV at
   264–268 s), each logged once. Prior audit prose said "single". Corrected in
   `qc_issue_classification_v2` QC-06; the register itself was already correct.
2. **Alpha cross-check method note.** Independent Welch recomputation matches
   the stored `ica_report.json` alpha change within 5 pp for 29/30 recordings;
   P07 meditation differs by 29 pp (both methods agree the ICA output is
   unusable). Documented as QC-11; no status changed.
3. **"Auto-approved" labels are not sign-off.** The v3 `APPROVED` labels
   (25) are the automated V7b audit's; the review table records
   `NEEDS_REVIEW` for all 30 until a human decides (audit policy).

## What was deliberately NOT changed

- Raw data, cleaned/ICA `.fif`, all per-recording JSONs, `figures_v2`/`figures_v3`,
  `audit_finalization_v1`, `reports_final_v3`, `provisional_review_v1/v2`,
  `ica_visual_review_bundle_v1`, `component_evidence_v1`, and the frozen
  v3/v2/v1 notebooks.
- The output-folder naming fork (`EEG processed\eeg` vs historical
  `processed\eeg`): documented (QC-08), not renamed — renaming would break
  every recorded path for no processing benefit.
- `STRUCTURE.md` (baseline record; staleness documented as QC-18).
- No decision was auto-recorded; no reviewer name or date was invented.

---

## Follow-up session (2026-10-14): human ICA sign-off + dashboard/notebook refresh

**Scope:** the human reviewer (Anushri Kajagar) worked all 30 pending rows through the
guarded review loop (`scripts/review_session_v1.py`, CLI twin of the review notebook).
No preprocessing was re-run; no ICA was refit; no raw or frozen artifact was modified.

| Outcome | Detail |
|---|---|
| Decisions recorded | 15 APPROVED / 13 REJECTED / 2 NEEDS_REVIEW (P07_maths, P08_meditation kept open by explicit reviewer choice) |
| Exclusion confirmations | All 5 pre-existing ICA exclusions confirmed REJECTED (QC-03 closed; QC-02 now 28/30) |
| `ica_review_table_v1.csv` | 30 rows carry reviewer + date + full comments (the only table updated) |
| `ica_signoff_decisions_log_v1.csv` | New append-only log, 31 entries (one per recorded action) |
| `eeg_qc_summary_v3.csv` / `.md` | New dashboard (v2 kept for history): per-recording sign-off decisions, feature-input split ICA 15 / cleaned 25, all 40 paths verified on disk |
| `notebooks\EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb` | V10 cells (91–93) refreshed to 15/13/2 with re-executed read-only status output; 90 frozen v3 cells re-verified identical; v3 hash unchanged |
| New scripts | `scripts/review_session_v1.py`, `scripts/build_qc_summary_v3.py` (refuses overwrite), `scripts/update_notebook_v4_signoff_v3.py` (frozen-cell integrity asserted before/after write) |

**Policy change in force:** feature input is now per-recording — `*_eeg_ica.fif` for the
15 APPROVED recordings, cleaned pre-ICA `*_eeg.fif` for the other 25; artifact-window
registers remain skip-in-features everywhere. Audit-scope readiness labels (2 PASS /
38 REVIEW) were not reopened. The acquisition reference remains UNKNOWN.
