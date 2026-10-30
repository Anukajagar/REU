# Mentor summary — EEG preprocessing status (2026-10-13)

**Project:** Analysis of Neuro-Acoustic Features from EEG and Speech Signals for
Dosha Characterization. **Scope of this note:** EEG preprocessing quality control
and the human ICA review gate. Feature extraction has deliberately not started.

## What the preprocessing did (per recording, 40 EEG recordings)

1. **Verified the data before touching it** — 24 standard 10–20 channels,
   Fs = 1000 Hz read from each BIOPAC `.acq` header and cross-checked against the
   `.xlsx` exports (40/40 recordings MATCH; an apparent 833 Hz value in 30 files
   was traced to timestamp quantization in the export, not a rate error).
2. **Band-pass 1–45 Hz** (zero-phase FIR) and a **50 Hz notch applied only when
   line-noise lift was detected** on raw data (one recording, P02 speech, has
   weak 1.40× evidence — kept and documented, not hidden).
3. **Artifact assessment without silent deletion** — 110 channel instances
   flagged (all ocular/muscle-like, verdict KEEP, 0 hardware faults, 0
   interpolated) and 931 one-second windows registered for skipping (34
   recordings, ~1,469 s). Everything is in registers; nothing was removed.
4. **ICA on the 30 recordings ≥ 2 min** (FastICA, 20 components, fixed seed;
   removal rule: |EOG-proxy correlation| ≥ 0.40 and frontal weight ≥ 0.35).
   The 10 speech recordings (~1 min) are below the reliability rule — no ICA.
5. **Evidence-based rejection of 4 ICA outputs** whose removal destroyed
   posterior alpha (P01/P04/P07/P09 meditation: −78/−88/−64/−87% alpha), plus
   P09 calm (−40%, over the 30% guard). All 30 ICA files remain on disk for audit.

## Evidence supporting the outputs

- Per-recording JSONs + master QC tables; an **independent audit pass** re-derived
  50 Hz evidence, filter reproduction, ICA metrics, and artifact windows from the
  saved files and matched the recorded values (30/30 on ICA metrics).
- This pass added **before/after ICA waveform+PSD figures for all 30 recordings**
  (read-only from the saved files; previously only 4 existed).
- Raw data integrity: 100/100 raw files byte-identical to the inventory baseline
  across all passes, including this one (SHA-256).

## Honest QC state (not forced to look green)

- EEG: **2 PASS / 38 REVIEW_REQUIRED** (audit criteria) — REVIEW_REQUIRED means
  "usable with documented constraints", not defective.
- **No ICA output is formally approved yet.** A complete human review workflow is
  ready: `notebooks\EEG_ICA_Signoff_Review_v1.ipynb` +
  `signoff_finalization_v2\ica_review_table_v1.csv` (30 rows, all pending;
  18 prior provisional recommendations carried as non-binding context).
- Acquisition reference is **unknown** — reference-sensitive features must wait
  for the acquisition team. Electrode positions are assumed 10–20; the EOG
  detector uses an Fp-channel proxy (no dedicated EOG was recorded).

## What remains before feature extraction

1. **A human signs the 30-row review table** (the only step that can change how
   many recordings use ICA-cleaned vs cleaned files).
2. Feature extraction then follows machine-readable rules: input file per
   recording from `eeg_qc_summary_v2.csv`; skip the 931 registered windows;
   never use the 5 excluded ICA files unless reinstated with evidence; no
   reference-sensitive features until QC-01 closes.

*Detailed files: `MENTOR_SUMMARY` companions `README.md`, `eeg_qc_summary_v2.md`,
`qc_issue_classification_v2.md`, `VALIDATION_REPORT.md`, `CHANGE_LOG.md`.*
