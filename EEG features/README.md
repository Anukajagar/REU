# EEG features — v1

**Status:** COMPLETE + VALIDATED (2026-11-02). **Scope:** sensor-space EEG feature
extraction only — no rereferencing, interpolation, connectivity, EEG-speech fusion,
or Dosha modelling.

Read `eeg_feature_extraction_summary.md` for methods, QC, and limitations,
`notebooks/EEG_Feature_Extraction.ipynb` for the executed report, and
`validation_v1/VALIDATION_REPORT.md` for the validation and sensitivity result.

## Inputs

- `signoff_finalization_v2/eeg_qc_summary_v3.csv` — per-recording `feature_input_file`
  (16 `*_eeg_ica.fif`, 24 cleaned `*_eeg.fif`).
- `audit_finalization_v1/eeg/artifact_log_v1.csv` — 931 one-second windows with
  `disposition = SKIP_IN_FEATURE_EXTRACTION` (34 recordings).
- No input was modified; all outputs are new files in this folder.

## Outputs

| File | Rows x cols | Purpose |
|---|---:|---|
| `eeg_features_channel_level.csv` | 960 x 62 | One row per recording x channel (24 channels; M1/M2 flagged non-scalp) |
| `eeg_features_recording_level.csv` | 40 x 158 | Primary analysis table: participant x condition |
| `eeg_features_participant_level.csv` | 10 x 155 | Convenience mean across conditions |
| `eeg_features_epoch_level.csv` | 382,392 x 24 | Valid 2 s epochs only; useful for re-aggregation/QC |
| `eeg_feature_extraction_log.csv` | 40 x 18 | Input hash, epochs, runtime, status |
| `eeg_feature_extraction_quality_report.csv` | 25 x 5 | Q01-Q21 PASS, Q22-Q25 documented WARN |
| `eeg_psd_by_recording.npz` | 40 x 22 x 1001 | Average PSD per recording (scalp channels) |
| `figures/` | 7 PNGs | PSD, band power, topography, alpha peak, asymmetry, correlations, artifact impact |

The epoch-level CSV is ~128 MB. Do not `git add -A`; add files explicitly.

## Validation and sensitivity

| File | Purpose |
|---|---|
| `validation_v1/VALIDATION_REPORT.md` | 17 checks: 16 PASS, 1 expected WARN |
| `validation_v1/validation_results_v1.csv` | Machine-readable check table |
| `validation_v1/sensitivity_cleaned_only/` | All 40 recordings recomputed on cleaned `*_eeg.fif` |
| `validation_v1/sensitivity_cleaned_only/sensitivity_comparison_v1.csv` | Feature-level agreement (Pearson/Spearman) |
| `validation_v1/sensitivity_cleaned_only/sensitivity_summary.md` | Concrete findings and recommendation |

What holds up:

- **Stable:** alpha power (r=0.999), beta power (r=0.998), Higuchi FD (r=0.988),
  alpha peak frequency (r=0.944), frontal alpha asymmetry (r=0.952 at recording level).
  The meditation-vs-maths/calm alpha difference survives the input change.
- **Sensitive to the ICA/cleaned choice:** theta power (r=0.687), RMS (r=0.788),
  delta power (~0.66), aperiodic offset and several asymmetry/regional features.
  The RMS meditation-vs-maths contrast changes sign.
- **Recommendation:** keep the policy-compliant primary table; report the cleaned-only
  table alongside theta, delta, RMS and any feature with r < 0.80. Do not claim a
  condition effect for a feature whose contrast sign flips.

Validation checks include input SHA-256 re-verification, artifact-window overlap
(zero leaks), independent PSD/RMS recomputation, nonlinear-kernel synthetic tests,
and no NaN/duplicate/rule violations.

## Reproduce

```powershell
py -3.14 "EEG features/scripts/extract_eeg_features.py" --force
py -3.14 "EEG features/scripts/sensitivity_cleaned_only.py"
py -3.14 "EEG features/scripts/validate_eeg_features.py"
py -3.14 reports_final_v3/scripts/run_nb.py "notebooks/EEG_Feature_Extraction.ipynb"
```

The extractor refuses to overwrite existing outputs unless `--force` is passed.
A one-recording smoke test:

```powershell
py -3.14 "EEG features/scripts/extract_eeg_features.py" --limit P01_calm `
  --out-dir "C:\Users\anush\AppData\Local\Temp\opencode\eeg_pilot" --force
```

## Method summary

- 2.0 s epochs, 1.0 s step, linear detrend; skip any epoch overlapping an artifact window.
- Spectral: absolute/relative/log band power (delta 1-4, theta 4-8, alpha 8-12,
  beta 12-30, gamma 30-45 Hz), total power, centroid, 95% edge, alpha peak,
  four band ratios, spectral entropy, simple log-log aperiodic exponent.
- Temporal: RMS, variance, peak-to-peak, zero-crossing rate, Hjorth
  activity/mobility/complexity, line length, Hilbert envelope, lag-1 autocorrelation.
- Nonlinear (250 Hz): permutation entropy (order 3), Lempel-Ziv complexity,
  Higuchi fractal dimension (kmax 8), DFA exponent (scales 4-64).
- Laterality: log10(right) - log10(left) for 8 homologous pairs in theta/alpha/beta.
- M1/M2 are retained in the channel table but excluded from scalp aggregates.

## Key caveats

- The 16 ICA / 24 cleaned input mix varies within participants across conditions.
  The cleaned-only sensitivity check is complete: alpha/beta/HFD/alpha-peak are stable;
  theta/delta/RMS are not. Use both tables for the sensitive features.
- Artifact windows were derived on cleaned files; for ICA inputs they are applied
  conservatively (some may already be removed).
- The acquisition reference is unknown (QC-01), so no reference-sensitive features
  or connectivity were computed.
- n = 10 exploratory participants; no inferential statistics or ML.
- Dosha labels are provisional and are not merged here.
