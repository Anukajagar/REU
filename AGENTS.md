# AGENTS.md

## Repository shape

- Research data repository for *Analysis of Neuro-Acoustic Features from EEG and Speech Signals for Dosha Characterization* (n = 10; 40 EEG recordings + 10 speech recordings).
- Not an application: no package manifest, build, lint, typecheck, or CI config. Deliverables are executed notebooks, CSV/JSON tables, figures, and audit reports.
- `README.md` is a stub. `STRUCTURE.md` is a 2026-10 baseline index; the tree is now 1,200+ files / ~10 GB, so trust current CSVs/manifests over its counts.

## Data-safety rules

- `P01/`–`P10/` are **raw and read-only**. Never write, move, rename, or delete anything inside them. `INVENTORY_BASELINE.csv` holds the SHA-256 anchor.
- Do not edit prior-pass outputs in place. The convention is a new versioned folder per pass (and `vN+1` notebooks, not edits to `v3`/`v4`). Builders named `build_*.py` deliberately refuse to overwrite; delete an output explicitly only when a rebuild is intended.
- Never run `git add -A` / `git add .`, `git clean -fd`, or `git reset --hard`. Almost all data is untracked and `.gitignore` contains only `P*/`; `git add -A` would stage 300+ derived/report files plus 3 pending `docs/agents` deletions. Add explicit paths.
- Questionnaire workbooks, `Questionnaire_Analysis/`, and `analysis_ready/` are hidden by this clone's **local-only** `.git/info/exclude`. That file is not committed. Never force-add or push these; keep raw responses out of commit-tracked files.
- `11_AUDIT_AND_LOGS/File_Inventory/proposed_file_mapping.csv` is an **unexecuted proposal** (Stage C was never run). Do not move or rename files from it.
- The worktree already contains uncommitted modifications and untracked data. Treat them as user work: never revert, clean, or commit them as part of an unrelated task.

## Environment and running code

- `python` is not on PATH. Use `py -3.14` (or `C:\Users\anush\AppData\Local\Programs\Python\Python314\python.exe`).
- Notebooks run under the Jupyter kernel `python314-mne` (Python 3.14 + MNE/librosa/Praat stack, already installed).
- Execute a notebook end-to-end, keeping outputs and failing fast:
  `py -3.14 reports_final_v3/scripts/run_nb.py "notebooks/<name>.ipynb" [timeout_s]`
  The default timeout is 900 s; speech cell S4 can take ~54 min.
- Use the finalized notebooks: `EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb` (v3 + sign-off status) and `Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb`. Do **not** run the unversioned v1 notebooks: they write to `E:\REU_DATA\processed\...`, which does not exist, creating a duplicate output tree.
- Pipeline notebooks/scripts assume Windows paths rooted at `E:\REU_DATA`. Do not relocate the repo. Quote paths containing spaces (`"EEG processed"`, `"SPEECH processed"`, `"SPEECH features"`).

## Current authoritative state (2026-11-02)

- EEG/speech preprocessing is final: `reports_final_v3/FINAL_PREPROCESSING_REPORT_v3.md`.
- ICA sign-off is complete: **16 APPROVED / 14 REJECTED / 0 open** (`signoff_finalization_v2/ica_review_table_v1.csv`).
- Feature input is per recording, read from `signoff_finalization_v2/eeg_qc_summary_v3.csv`: 16 `*_eeg_ica.fif`, 24 cleaned `*_eeg.fif`, 10 speech WAVs. Never substitute `*_eeg_ica.fif` for a REJECTED row; rejected ICA files stay on disk for audit only.
- Skip the **931** registered artifact windows in `audit_finalization_v1/eeg/artifact_log_v1.csv` (`disposition = SKIP_IN_FEATURE_EXTRACTION`). The older `EEG processed/eeg/figures_v3/v8_segment_exclusion_register.csv` has 235 spans built against the pre-sign-off ICA/cleaned mix and is not the current skip list.
- Do not build reference-sensitive EEG features until the acquisition reference is confirmed (QC-01). Do not interpolate the 110 flagged channel instances implicitly (QC-04 is open).
- **Superseded docs:** the final report/consolidated summary still say 26 ICA / 14 cleaned, 235 windows, and "P09 calm provisional" — all replaced by the 2026-11-01 sign-off. `SPEECH features/feature_extraction_summary.md` saying Dosha labels are unavailable is also stale.
- Dosha labels are **provisional, literature-derived, not expert-validated**: `Questionnaire_Analysis/participant_labels_v1.csv`. The joined speech+labels table is `analysis_ready/participant_master_v1.csv` (join key `participant_id`). Do not treat labels as ground truth.
- EEG feature extraction v1 is complete and validated (`EEG features/`, 40/40; sensor-space spectral, temporal and nonlinear features). Validation: 16 PASS / 1 expected WARN. The cleaned-only sensitivity is done: alpha/beta/Higuchi-FD/alpha-peak are stable; theta/delta/RMS are input-sensitive, so report both tables for those features. Speech feature extraction is complete (`SPEECH features/`, 10/10). Next: label/speech fusion. n = 10: report exploratory results only, no inferential claims or ML.

## Key paths

| Path | Contents |
|---|---|
| `notebooks/` | Pipeline and audit notebooks (versioned; v3/v4 are final) |
| `EEG processed/eeg/` | Cleaned/ICA `.fif`, per-recording JSONs, QC registers |
| `SPEECH processed/speech/` | Cleaned WAVs and quality reports |
| `signoff_finalization_v2/` | **Current** ICA decisions and 50-row QC summary |
| `audit_finalization_v1/` | Independent audit, artifact log, signed-off evidence (pre-sign-off QC status) |
| `reports_final_v3/` | Final preprocessing report + integrity scripts |
| `Questionnaire_Analysis/` | Provisional labels, scoring key/tests, expert questions (local-only) |
| `analysis_ready/` | Joined per-participant master table (local-only) |
| `SPEECH features/` | Speech feature tables and figures |
| `EEG features/` | EEG feature tables, epoch-level data, figures, extraction scripts (v1) |
| `EEG features/validation_v1/` | Validation report + cleaned-only sensitivity tables (16 PASS / 1 WARN) |

Recording IDs are `<Pxx>_<condition>` with conditions `calm`, `meditation`, `maths`, `speech`. EEG is 24 channels at 1000 Hz; cleaned speech is 16 kHz mono PCM_16.

## Verification

- Only unit tests: `py -3.14 Questionnaire_Analysis/scripts/test_scoring.py` (should print `all tests PASSED`). There is no pytest suite.
- Other verification is scripted assertions plus SHA-256 audits, not a test runner. Prefer inspecting the saved CSVs/reports over re-running finalized pipelines.
- `signoff_finalization_v2/scripts/validate_finalization_v2.py` refuses to overwrite its dated results and expects temp hash snapshots; do not rerun it casually.

## Existing agent workflow

- Issues live in GitHub Issues via the `gh` CLI; see `docs/agents/issue-tracker.md`. `gh` is **not currently on PATH**, so install/authenticate it before using this workflow.
- Triage labels are the default unmapped vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`; see `docs/agents/triage-labels.md`.
- Domain docs use a single context (`GLOSSARY.md` + `docs/adr/`, currently absent); see `docs/agents/domain.md`.
- Those three `docs/agents/*.md` files are tracked but deleted in the worktree. Restore them with `git restore docs/agents` before relying on the references; do not stage the deletions as part of unrelated work.
