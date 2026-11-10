# Speech Feature Extraction - Summary

**Generated:** 2026-10-31T08:48:24Z
**Notebook:** `notebooks/Speech_Feature_Extraction.ipynb`
**Status:** COMPLETE

## 1. Scope

Speech feature extraction only - no EEG feature extraction, no EEG-speech fusion, no
machine learning, no classification or prediction. n = 10 participants; all results are
exploratory. No audio file was modified, renamed, moved or overwritten; every output was
written to the new directory `SPEECH features/`.

## 2. Inputs (verified, not assumed)

- 10/10 preprocessed recordings: `SPEECH processed/speech/P01-P10/Pxx_speech_cleaned.wav`
- All 16 kHz, mono, PCM_16; durations 40.7-78.6 s; SHA-256 recorded in the log.
- All matched `speech_final_quality_review_v3.csv` (sample rate, channels, duration).
- Documented limitations carried forward: P05 low SNR (13.8 dB), P09 and P10 stereo-origin.

## 3. Voice-quality prototype (subset P01 ordinary / P05 low-SNR / P08 additional)

| participant_id | snr_db | pyin_f0_median_hz | pratt_f0_median_hz | jitter_local_pct | shimmer_local_pct | hnr_mean_db | cpps_db |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | 20.79 | 125.40 | 113.70 | 2.37 | 9.45 | 12.84 | 7.55 |
| P05 | 13.82 | 132.90 | 128.50 | 2.41 | 17.29 | 8.33 | 6.95 |
| P08 | 18.96 | 142.40 | 86.40 | 2.55 | 11.16 | 13.07 | 7.06 |

Decisions:
- **RETAINED:** F0 (librosa.pyin, cross-checked against Praat To Pitch), HNR
  (Praat Harmonicity cc), CPPS (Praat PowerCepstrogram, official test defaults:
  trend 'Exponential decay', fit 'Robust', peak search 75-500 Hz, tolerance 0.05).
- **EXCLUDED:** jitter (local/rap) and shimmer (local) - defined for sustained phonation,
  not running speech; the prototype shows shimmer rises from ~9.5% (P01) to ~17.3% (P05)
  purely from recording noise, i.e. the measure tracks SNR rather than voice. Values were
  computed diagnostically but are NOT in the feature tables.

## 4. Features extracted (consistent parameters for all participants)

- **A. Pitch (librosa.pyin, 75-500 Hz, 64 ms frame, 10 ms hop, voiced frames only):**
  f0_mean_hz, f0_median_hz, f0_min_hz, f0_max_hz, f0_std_hz, f0_range_hz, f0_cv, f0_semitone_std, f0_voiced_fraction_pct
- **B. Energy (RMS, 25 ms frame / 10 ms hop, dBFS):**
  rms_dbfs_mean, rms_dbfs_std, rms_dbfs_min, rms_dbfs_max, rms_dbfs_range
- **C. Spectral (n_fft 512, 10 ms hop):**
  spectral_centroid_mean_hz, spectral_centroid_std_hz, spectral_bandwidth_mean_hz, spectral_bandwidth_std_hz, spectral_rolloff85_mean_hz, spectral_rolloff85_std_hz, zcr_mean, zcr_std
- **D. MFCC (n_mfcc 13, n_mels 40, n_fft 512):** mean + SD per coefficient
  (26 columns: mfcc00_mean, mfcc00_std, mfcc01_mean, mfcc01_std, mfcc02_mean, mfcc02_std, ...).
- **E. Voice quality (Praat):** hnr_mean_db, hnr_std_db, cpps_db
- **F. Timing/fluency (energy VAD: noise floor = 10th pct, speech level = 90th pct,
  noise-floor + 6 dB threshold; pauses >= 250 ms between speech):**
  total_duration_s, speech_duration_s, silence_duration_s, speech_ratio_pct, n_pauses_ge250ms, mean_pause_s, median_pause_s, max_pause_s, n_pauses_ge1s, leading_silence_s, trailing_silence_s, speaking_rate_sy_per_s_est, articulation_rate_sy_per_s_est, syllable_nuclei_count_est
  Speaking/articulation rates are *estimates* from energy-peak syllable counting
  (>=3 dB prominence, >=80 ms separation); no word transcript exists, so no WPM is claimed.

## 5. Outputs written to `SPEECH features/`

| File | Rows x cols |
|---|---|
| `speech_features_recording_level.csv` | 10 x 82 |
| `speech_features_participant_level.csv` | 10 x 29 |
| `speech_features_frame_level.csv` | 48962 x 25 |
| `feature_extraction_log.csv` | 10 x 7 |
| `feature_extraction_quality_report.csv` | 145 x 4 |
| `figures/fig01_f0_distributions.png` | F0 summary + contours |
| `figures/fig02_energy_spectral_mfcc.png` | energy / spectral / MFCC distributions |
| `figures/fig03_vad_pauses.png` | VAD timeline + pause validation |
| `figures/fig04_voice_quality_timing.png` | HNR, CPPS, speaking rates |
| `figures/fig05_correlation_qc.png` | feature correlations + QC outcomes |

## 6. Coverage and processing result

- Recordings processed: **10/10**, failures: 0.
- QC checks: {'PASS': 140, 'WARN': 5} (145 checks total; outliers and anomalies are
  reported, never removed or imputed).

## 7. Dosha labels

**Not integrated - UNAVAILABLE.** The questionnaires (`KLE_PRAKRITI_QUESTIONNARIE.xlsx`,
`KLE_TRAITS_QUESTIONNARIE.xlsx`) contain raw item responses only; no computed
Vata/Pitta/Kapha column exists, and no scoring methodology was found anywhere in the
repository. Labels were NOT calculated, guessed or inferred. The `dosha_label` column is
empty with `dosha_label_status` recording the reason; tables can be joined later on
`participant_id` once an approved scoring methodology or label file is provided.

## 8. Limitations

1. n = 10 exploratory participants - no inferential statistics, no generalization.
2. Reading-task variability: durations span 40.7-78.6 s; rates are per-recording estimates.
3. Jitter/shimmer intentionally excluded (sustained-phonation measures on running speech).
4. VAD is energy-based; cross-validated against preprocessing reports with differences
   reported per participant (tolerance 10 percentage points).
5. P05 (low SNR), P09/P10 (stereo origin) carry documented limitations - visible per row
   in every table.
6. Speaking/articulation rates are automated syllable-count estimates, not human transcripts.

## 9. What remains before fusion/modelling (out of scope here)

1. Clinician-approved Dosha labels (or scoring methodology) joined on `participant_id`.
2. EEG feature extraction (separate task/directory).
3. EEG-speech temporal alignment and fusion.
4. Modelling/classification with proper cross-validation - only after 1-3 exist.
