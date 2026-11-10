# Cleaned-only sensitivity analysis (v1)

**Generated:** 2026-11-02T07:56:03Z
**Scope:** recompute the v1 EEG features for all 40 recordings on the cleaned
pre-ICA `*_eeg.fif` file, then compare with the policy-compliant primary table.
No primary output was modified.

## Why this pass exists

The primary table uses 16 ICA-cleaned and 24 cleaned recordings, and the mix differs
by condition (maths is mostly ICA; speech is all cleaned; meditation is mostly cleaned).
This pass removes that preprocessing difference so condition effects can be checked.

## Outputs

- `sensitivity_cleaned_only/eeg_features_recording_level.csv` — 40 rows (all cleaned)
- `sensitivity_cleaned_only/eeg_features_channel_level.csv` — 960 rows
- `sensitivity_cleaned_only/eeg_features_participant_level.csv` — 10 rows
- `sensitivity_cleaned_only/eeg_feature_extraction_log.csv` — 40 rows
- `sensitivity_comparison_v1.csv` — feature-level agreement
- `sensitivity_condition_contrasts_v1.csv` — key condition contrasts
- `figures/fig01_key_feature_agreement.png`, `figures/fig02_alpha_condition_means.png`

## Agreement across 40 recordings

- Features with Pearson r >= 0.80: **118**
- Features with 0.50 <= r < 0.80: **31**
- Features with r < 0.50: **0**
- Total numeric recording-level features compared: **151**

### Key features

| Feature | Pearson r | Spearman r | Mean abs diff | Rel. diff % |
|---|---:|---:|---:|---:|
| abs_power_theta_uv2_mean | 0.687 | 0.603 | 2.857 | 33.4 |
| rms_uv_mean | 0.788 | 0.719 | 0.9416 | 10.4 |
| dfa_alpha_mean | 0.844 | 0.844 | 0.03058 | 2.5 |
| alpha_peak_freq_hz_mean | 0.944 | 0.935 | 0.142 | 1.5 |
| frontal_alpha_asymmetry | 0.952 | 0.936 | 0.01574 | 18.0 |
| higuchi_fd_mean | 0.988 | 0.988 | 0.01196 | 0.8 |
| abs_power_beta_uv2_mean | 0.998 | 0.996 | 0.2592 | 2.4 |
| abs_power_alpha_uv2_mean | 0.999 | 0.926 | 0.4777 | 4.5 |

### Key condition contrasts

| Feature | Contrast | Primary diff | Cleaned diff | Change % | Sign flip |
|---|---|---:|---:|---:|---|
| abs_power_alpha_uv2_mean | meditation_minus_maths | 22.95 | 22.37 | 2.5 | False |
| abs_power_alpha_uv2_mean | meditation_minus_calm | 20.56 | 20.67 | 0.5 | False |
| abs_power_theta_uv2_mean | meditation_minus_maths | -1.72 | -9.176 | 433.6 | False |
| abs_power_theta_uv2_mean | meditation_minus_calm | -4.706 | -7.893 | 67.7 | False |
| abs_power_beta_uv2_mean | meditation_minus_maths | -1.094 | -1.676 | 53.2 | False |
| abs_power_beta_uv2_mean | meditation_minus_calm | -0.7258 | -0.7943 | 9.4 | False |
| rms_uv_mean | meditation_minus_maths | 1.007 | -0.8153 | 181.0 | True |
| rms_uv_mean | meditation_minus_calm | -1.219 | -2.33 | 91.2 | False |
| higuchi_fd_mean | meditation_minus_maths | -0.2272 | -0.1972 | 13.2 | False |
| higuchi_fd_mean | meditation_minus_calm | -0.1458 | -0.1261 | 13.5 | False |
| dfa_alpha_mean | meditation_minus_maths | 0.1065 | 0.03283 | 69.2 | False |
| dfa_alpha_mean | meditation_minus_calm | 0.008188 | -0.03125 | 481.7 | True |
| alpha_peak_freq_hz_mean | meditation_minus_maths | 1.27 | 1.627 | 28.1 | False |
| alpha_peak_freq_hz_mean | meditation_minus_calm | 0.4727 | 0.6773 | 43.3 | False |
| frontal_alpha_asymmetry | meditation_minus_maths | -0.01686 | -0.02139 | 26.9 | False |
| frontal_alpha_asymmetry | meditation_minus_calm | 0.0002029 | 0.01428 | 6939.7 | False |

## Concrete findings

- **Stable and usable:** alpha power (r=0.999), beta power (r=0.998),
  Higuchi FD (r=0.988), and alpha peak frequency (r=0.944). The
  meditation-vs-maths/calm alpha difference survives the input change
  (22.95 vs 22.37 uV^2 for meditation-maths).
- **Stable at recording level but with a near-zero contrast:** frontal alpha
  asymmetry (r=0.952); its meditation-calm contrast is ~0.0002 and should not
  be interpreted.
- **Moderately stable:** DFA (r=0.844); the meditation-maths contrast keeps its
  direction, but the near-zero meditation-calm contrast changes sign.
- **Sensitive to ICA:** theta power (r=0.687) and RMS (r=0.788).
  The theta meditation-maths difference changes from -1.72 to -9.18 uV^2 (same
  direction, much larger after removing ICA), and the RMS meditation-maths contrast
  changes sign (+1.01 to -0.82 uV).
- **Delta, the aperiodic offset, and several asymmetry/regional features** are also
  only moderately stable (r about 0.51-0.68); they should not drive condition-level
  conclusions on their own.
- **No feature had r < 0.50**, so no feature is wholly determined by the input choice,
  but the sensitive features need both tables reported side by side.

## Recommendation

- Keep the policy-compliant primary table for the approved pipeline.
- Use the cleaned-only table as the sensitivity result for theta, delta, RMS and any
  feature with r < 0.80.
- Alpha/beta/HFD/alpha-peak conclusions are robust to the input choice.
- Do not claim a condition effect for a feature whose contrast sign flips between the
  two tables.

- Sign flips in key contrasts: **2** (RMS meditation-maths is meaningful; DFA meditation-calm is a near-zero difference).
- Total sensitivity runtime: 3.6 min

## Reproduce

```
py -3.14 "EEG features/scripts/sensitivity_cleaned_only.py"
```
