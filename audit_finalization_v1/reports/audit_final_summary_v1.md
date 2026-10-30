# Final audit summary — EEG and speech preprocessing (v1)

**Date:** 2026-10-12
**Pass:** independent audit and finalization of the frozen v3 preprocessing outputs.
**Out of scope and not started:** feature extraction, model training, any reprocessing.

## Is the preprocessing finalised?

Yes. Both v3 pipelines' outputs have now been independently re-verified from the saved files:

- **Raw data untouched:** 100/100 raw files byte-identical to `INVENTORY_BASELINE.csv` (checked before and after the audit).
- **EEG:** 40/40 recordings verified from `.acq` headers (Fs = 1000 Hz measured, 24 canonical labels, durations match); 50 Hz evidence recomputed on raw unfiltered data for all 40 (33 strong / 6 mild / 1 weak = P02 speech); filter chain reproduced to < 1e-9 V on an 8-recording subset (also proving the uV→V conversion); 110 flagged channels re-verified (0 interpolation candidates); ICA evidence recomputed for all 30 ICA files (30/30 match their own reports); artifact windows recomputed on the actual feature-input files (931 spans / 34 recordings / 1469 s, register-only).
- **Speech:** 20/20 raw files untouched; 10/10 cleaned WAVs pass integrity (16 kHz, mono, PCM_16, finite, duration match); resampling proven real (`resample_poly` frame counts + band-limited spectra; source energy > 8 kHz max 0.469 %); mono conversion proven for all 10 by reconstruction (r > 0.995); quality flags re-derived with uniform thresholds (low SNR = P05 only; clipping = P10 source only); 16 kHz confirmed suitable for MFCC / F0 / formant features.

## Which recordings are eligible for feature extraction, and why?

**None are cleared yet — the audit itself must be reviewed first** (per the project gate). After that review, all 50 recordings have a named, verified input file; eligibility conditions:

| Modality | PASS now | REVIEW_REQUIRED | Feature input |
|---|---|---|---|
| EEG (40) | 2 — P07 speech, P09 speech | 38 | Cleaned `*_eeg.fif` for **all 40** until ICA sign-off |
| Speech (10) | 7 — P01–P04, P06–P08 | 3 — P05 (SNR), P09 (+10.1 dB stereo), P10 (clipping + +11.7 dB) | `Pxx_speech_cleaned.wav` for all 10 |

A REVIEW_REQUIRED recording is **usable with its documented constraint** — it is not defective. The constraints that feature extraction must honour, all machine-readable:

1. Read the feature input from `reports/master_recording_qc_v1.csv` (one row per recording, 50 rows, no missing inputs).
2. Skip the 931 flagged windows in `eeg/artifact_log_v1.csv` (`disposition = SKIP_IN_FEATURE_EXTRACTION`).
3. Use the cleaned (non-ICA) EEG `.fif` for every recording until a human signs off the 25 `HUMAN_SIGNOFF_PENDING` ICA outputs (review packet: component maps in `EEG processed\eeg\figures_v2\ica\` + `eeg/ica_audit_v1.csv`).
4. Do not use the 5 `EXCLUDED` ICA files (P01/P04/P07/P09 meditation, P09 calm).
5. Do not compute reference-sensitive EEG features until the acquisition reference is confirmed (`reports/acquisition_reference_note_v1.md`).

## Disagreements with the v3 statuses (all deliberate)

- **4 EEG recordings** (P02/P05/P06/P08 meditation): v3 PASS → audit REVIEW_REQUIRED, because v3 auto-APPROVED their ICA output and the audit requires human sign-off.
- **Speech:** 10/10 agreement with v3 — the same three flagged recordings, now proven to fall out of uniform metric thresholds instead of participant-ID branches.
- The larger artifact-window count (931 vs v3's 235) is not a disagreement: the audit describes the cleaned files features will actually read; v3 described ICA files for 26 recordings, where ICA had already removed many blink windows. On the 14 recordings v3 also scanned on cleaned files, the registers match exactly.

## Where everything is

| Deliverable | Path |
|---|---|
| EEG audit notebook | `notebooks\EEG_Audit_and_Finalization_v1.ipynb` |
| Speech audit notebook | `notebooks\Speech_Audit_and_Finalization_v1.ipynb` |
| **Master QC table (50 rows)** | `audit_finalization_v1\reports\master_recording_qc_v1.csv` |
| EEG audit QC + disagreements | `audit_finalization_v1\eeg\eeg_audit_quality_control_v1.csv`, `status_disagreements_v1.csv` |
| Speech audit QC + disagreements | `audit_finalization_v1\speech\speech_audit_quality_control_v1.csv`, `status_disagreements_v1.csv` |
| Artifact log (EEG windows) | `audit_finalization_v1\eeg\artifact_log_v1.csv` |
| ICA audit (sign-off packet data) | `audit_finalization_v1\eeg\ica_audit_v1.csv` |
| Bad-channel audit | `audit_finalization_v1\eeg\bad_channel_audit_v1.csv` |
| Raw 50 Hz / filter / units / metadata evidence | `audit_finalization_v1\eeg\raw_50hz_audit_v1.csv`, `filter_verification_v1.csv`, `units_verification_v1.csv`, `metadata_verification_v1.csv` |
| Speech evidence tables | `audit_finalization_v1\speech\{output_integrity, resample_verification, mono_verification, quality_recompute, rate_suitability}_v1.csv` |
| Status criteria (explicit PASS/REVIEW/EXCLUDED rules) | `audit_finalization_v1\reports\status_criteria_v1.csv`, `speech_status_criteria_v1.csv` |
| Integrity checks | `audit_finalization_v1\reports\raw_integrity_pre_v1.csv`, `raw_integrity_speech_pre_v1.csv` |
| **Unresolved issues** | `audit_finalization_v1\reports\unresolved_issues_v1.md` |
| Acquisition reference note | `audit_finalization_v1\reports\acquisition_reference_note_v1.md` |

**Nothing outside `audit_finalization_v1\` was created, modified, renamed or deleted by this pass.** Raw data and all v3 outputs were opened read-only.
