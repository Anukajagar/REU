# EEG Feature Extraction - Summary (v1)

**Generated:** 2026-11-02T07:57:02Z
**Notebook:** `notebooks/EEG_Feature_Extraction.ipynb`
**Script:** `EEG features/scripts/extract_eeg_features.py`
**Status:** COMPLETE

## 1. Scope

Sensor-space EEG feature extraction only - no rereferencing, no interpolation, no connectivity,
no EEG-speech fusion, no Dosha modelling. Inputs are the finalised preprocessing outputs
selected by `signoff_finalization_v2/eeg_qc_summary_v3.csv`.

## 2. Inputs (verified, not assumed)

- 40/40 EEG recordings read successfully (16 `*_eeg_ica.fif`, 24 cleaned `*_eeg.fif`).
- 24 channels at 1000 Hz; data already band-passed 1-45 Hz and notched by the preprocessing stage.
- 931 one-second artifact windows skipped (`SKIP_IN_FEATURE_EXTRACTION`), 34 recordings.
- Artifact windows come from the cleaned-file audit; for ICA inputs they are applied conservatively.

## 3. Epochs and features

- 2.0 s epochs, 1.0 s step, linear detrend per epoch; any epoch overlapping an artifact window is skipped.
- Valid epochs per recording: 30-599; valid duration by condition (s):

| condition | min | max | mean |
|---|---:|---:|---:|
| calm | 343.0 | 580.0 | 482.5 |
| maths | 339.0 | 566.0 | 487.7 |
| meditation | 503.0 | 599.0 | 582.6 |
| speech | 30.0 | 59.0 | 40.5 |

- Spectral (per channel, Welch PSD of the epoch-averaged signal): absolute/relative/log band power
  for delta 1-4, theta 4-8, alpha 8-12, beta 12-30, gamma 30-45 Hz; total power; spectral
  centroid; 95% spectral edge; alpha peak frequency/power; theta/alpha, alpha/beta, delta/theta,
  beta/gamma ratios; spectral entropy; simple log-log aperiodic exponent (2-40 Hz, alpha 7-13 Hz
  excluded).
- Temporal (per epoch, averaged): RMS, variance, peak-to-peak, zero-crossing rate, Hjorth
  activity/mobility/complexity, line length, Hilbert envelope mean/SD, lag-1 autocorrelation.
- Nonlinear (per epoch at 250 Hz, averaged): permutation entropy (order 3), Lempel-Ziv
  complexity, Higuchi fractal dimension (kmax 8), DFA exponent (scales 4-64).
- Laterality: log10(right) - log10(left) absolute power for 8 homologous pairs in theta/alpha/beta;
  frontal alpha asymmetry is the mean of F3/F4 and F7/F8.
- M1/M2 are retained in the channel-level table but excluded from all scalp aggregates.

## 4. Outputs

| File | Rows x cols |
|---|---|
| `eeg_features_channel_level.csv` | 960 x 62 |
| `eeg_features_recording_level.csv` | 40 x 158 |
| `eeg_features_participant_level.csv` | 10 x 155 |
| `eeg_features_epoch_level.csv` | 382392 x 24 |
| `eeg_feature_extraction_log.csv` | 40 x 18 |
| `eeg_feature_extraction_quality_report.csv` | 25 x 5 |
| `eeg_psd_by_recording.npz` | 40 recordings x 22 scalp channels x PSD bins |
| `figures/` | 7 PNGs |

## 5. Coverage and QC

- Recordings processed: **40/40**, failures: 0.
- QC checks: {'PASS': 21, 'WARN': 4}.
- No NaN/inf in the channel-level feature table: 0 rows.
- All 40 feature-input paths exist; SHA-256 recorded in the extraction log.

## 6. Limitations

1. n = 10 participants; all results are exploratory. No inferential statistics, classification or
   generalization is claimed.
2. The feature-input policy mixes ICA-cleaned and cleaned files across conditions within participants
   (16 ICA / 24 cleaned). A cleaned-only sensitivity analysis is complete in
   `validation_v1/sensitivity_cleaned_only/`: alpha/beta/Higuchi-FD/alpha-peak are stable,
   while theta/delta/RMS are sensitive to the input choice.
3. The 1 Hz high-pass attenuates low delta; delta 1-4 Hz should be interpreted with that caveat.
4. Gamma 30-45 Hz is a narrow residual band and may contain muscle activity despite artifact
   windowing and ICA.
5. The acquisition reference is unknown (QC-01), so no Laplacian, CSD, average-reference or
   connectivity features were computed.
6. The 110 flagged channel instances were not interpolated (QC-04); they are used as recorded.
7. Speech-condition EEG has only 30-59 s of valid data (37-67 s raw) versus ~10 min for calm/meditation/maths, so condition comparisons must account
   for different effective sample sizes.
8. Dosha labels are provisional and are not merged here. Join on `participant_id` only with an
   explicit provisional-label caveat.
9. The aperiodic exponent is a simple log-log fit excluding 7-13 Hz, not a FOOOF/SPECPARAM
   decomposition.

## 7. Next steps

1. Use the completed cleaned-only sensitivity result (`validation_v1/sensitivity_cleaned_only/`)
   when interpreting theta, delta, RMS or any feature with r < 0.80; alpha/beta/HFD/alpha-peak
   conclusions are stable.
2. Join provisional labels (`Questionnaire_Analysis/participant_labels_v1.csv`) and speech features
   (`analysis_ready/participant_master_v1.csv`) on `participant_id`, keeping the provisional flag.
3. Confirm the acquisition reference before adding reference-sensitive features or connectivity.
4. Decide the interpolation policy for the 110 flagged channels (QC-04).
5. Only after labels are validated: feature selection and modelling with participant-level
   cross-validation; n = 10 is too small for train/test splits that claim generalization.

## 8. Reproduce

```
py -3.14 "EEG features/scripts/extract_eeg_features.py" --force
py -3.14 reports_final_v3/scripts/run_nb.py "notebooks/EEG_Feature_Extraction.ipynb"
```
