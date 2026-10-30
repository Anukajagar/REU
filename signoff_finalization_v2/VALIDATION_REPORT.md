# Validation report — signoff_finalization_v2 pass (2026-10-13)

**Machine-readable results:** `validation_results_v2.csv` (8 checks, **8 PASS, 0 FAIL**).
**Method:** static checks + fact assertions + hash snapshots + guard tests on temp
copies. No preprocessing was re-run; no notebook was executed end-to-end.

## Checks performed

| ID | Check | Result | How |
|---|---|---|---|
| V1 | All 8 builder/validator scripts compile | PASS | `compile()` each file |
| V2 | Review table: exact 11-column schema, 30 unique rows, vocabulary, **all `NEEDS_REVIEW`**, reviewer/date empty, evidence fields populated | PASS | direct asserts |
| V3 | Review table ↔ `packet_manifest_v2` ↔ `ica_audit_v1`: same 30 ids; the excluded-5 identical across sources | PASS | set equality |
| V4 | QC summary: 50 rows (40+10), **50/50 feature-input files exist on disk**, artifact recount = 931, sampling 40/40 MATCH, 30 pending + 10 not-applicable | PASS | rejoin + filesystem check |
| V5 | Before/after evidence: 30 figures + index; variance cross-check 30/30 OK; alpha cross-check 29/30 within 5 pp; the 1 outlier (P07 meditation) explicitly flagged | PASS | index asserts |
| V6 | Notebook integrity: v3 SHA-256 unchanged; v4 = 1 banner + 90 byte-identical cells + V10 with embedded output | PASS | hash + cell-object equality |
| V7 | Guard tests of the review-notebook helpers **on a temp copy**: invalid decision rejected; anonymous approval rejected; malformed date rejected; excluded-row approval without reinstatement evidence blocked by validation; valid decision + log append works; **real table hash unchanged** | PASS | 6 scenarios |
| V8 | Full-tree SHA-256 diff (1,103 → 1,105 files, ~11.6 GB): **0 pre-existing files changed, 0 removed**; all new files inside `signoff_finalization_v2\` or the 2 new notebooks | PASS | snapshot diff |

## Counts reconciled against sources

| Quantity | Value | Sources agreeing |
|---|---|---|
| Raw EEG recordings | 40 `.acq` + 40 `.xlsx` | filesystem, sampling-rate verification |
| Cleaned / ICA files | 40 `*_eeg.fif` + 30 `*_eeg_ica.fif` (+ 40+30 JSONs) | filesystem, v3 report, audit |
| ICA dispositions (audit) | 25 `HUMAN_SIGNOFF_PENDING` + 5 `EXCLUDED` + 10 `NOT_APPLIED` | `ica_audit_v1.csv`, packet manifest, review table |
| Formal sign-off decisions | **0 of 30** (all `NEEDS_REVIEW`) | review table |
| EEG readiness | audit scope: 2 PASS / 38 REVIEW_REQUIRED; v3 scope: 6 / 34 | master QC, v3 QC |
| Artifact windows | 931 spans / 34 recordings (audit recount) | `artifact_log_v1.csv` |
| Sampling rate | 40/40 MATCH at 1000 Hz | `sampling_rate_verification.csv` |

## What was NOT verified (honest limits)

- **The v3 pipeline was not re-executed.** The claim "v3 runs end-to-end" is
  inherited from the 2026-10-12 report (90 cells, 0 errors at that time); this
  pass verified file integrity and cell identity, not re-execution. Re-running
  is forbidden by the task rules (it would refit ICA and rewrite outputs).
- **The new notebook cells were executed standalone, not via Jupyter.** V10's
  embedded output was produced by running the exact cell code in-process
  (read-only); the review notebook is a tool for the reviewer and was validated
  by guard tests, not pre-executed with figures.
- **End-to-end run of `EEG_ICA_Signoff_Review_v1.ipynb` in Jupyter** requires a
  human session (it displays ~90 PNGs); its logic was tested headlessly (V7).
- Prior passes' internal claims (e.g., filter reproduction < 1e-9 V, mono
  reconstruction r ≥ 0.995) were **not** independently re-derived here; they are
  cited from their reports and were consistent with everything re-checked.

## Unresolved issues at the end of this pass

All 20 are classified in `qc_issue_classification_v2.csv`. The four requiring
human action:

1. **QC-02 — formal ICA sign-off 0/30** (workflow now delivered; a human must decide).
2. **QC-03 — confirm the 5 ICA exclusions** (evidence now includes new before/after figures).
3. **QC-09 — policy confirmation** of the 4 meditation readiness downgrades (v3 PASS → audit REVIEW).
4. **QC-13 — near-guard visual confirmations** (P02 calm, P06 maths, P09 maths).

Plus the acquisition-team items (QC-01 reference; QC-12 montage/EOG assumptions)
which cannot be resolved from data in this repository.
