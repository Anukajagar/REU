# Mentor summary — EEG preprocessing status (2026-10-13)

> **Updated 2026-11-01:** the human ICA sign-off gate described in this note is
> now **complete — 30 of 30 rows decided**. The "Honest QC state" and "What
> remains before feature extraction" sections below reflect that final state;
> everything else still describes the 2026-10-13 pass.

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
- **ICA sign-off is complete: 30 of 30 rows decided** (16 APPROVED / 14 REJECTED,
  0 open). Recorded in `ica_review_table_v1.csv` — 28 on 2026-10-14, the final 2
  (`P07_maths` APPROVED, `P08_meditation` REJECTED) on 2026-11-01. Feature input
  follows the `feature_input_file` column of `eeg_qc_summary_v3.csv`:
  **16 recordings use `*_eeg_ica.fif`, 24 use the cleaned pre-ICA `*_eeg.fif`**.
  All 5 original ICA exclusions stayed REJECTED.
- Acquisition reference is **unknown** — reference-sensitive features must wait
  for the acquisition team. Electrode positions are assumed 10–20; the EOG
  detector uses an Fp-channel proxy (no dedicated EOG was recorded).

## What remains before feature extraction

1. ~~A human signs the 30-row review table~~ — **done** (2026-11-01).
2. Feature extraction follows machine-readable rules: input file per
   recording from `eeg_qc_summary_v3.csv` (`feature_input_file`); skip the
   931 registered windows (`SKIP_IN_FEATURE_EXTRACTION`); never use the 5
   excluded ICA files unless reinstated with evidence; no reference-sensitive
   features until QC-01 closes. Two decisions are still open for the analysis
   lead, neither blocking: whether to interpolate the 110 flagged channel
   instances (QC-04), and whether reference-sensitive features are needed at
   all (QC-01).

*Detailed files: `MENTOR_SUMMARY` companions `README.md`, `eeg_qc_summary_v3.md`,
`qc_issue_classification_v2.md` (pre-sign-off snapshot), `VALIDATION_REPORT.md`,
`CHANGE_LOG.md`.*
