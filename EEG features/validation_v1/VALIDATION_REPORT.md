# EEG Feature Extraction - Validation Report (v1)

**Generated:** 2026-11-02T07:56:12Z
**Scope:** read-only validation of `EEG features/` v1 plus the cleaned-only sensitivity pass.

## Result

- Checks: **17**
- Status counts: **{'PASS': 16, 'WARN': 1}**

## Checks

| ID | Category | Check | Status | Value |
|---|---|---|---|---|
| V01 | structure | Output row counts | PASS | channel=960, recording=40, participant=10 |
| V02 | structure | 24 channels per recording; 10 per condition | PASS | channels=[np.int64(24)]; {'calm': 10, 'maths': 10, 'meditation': 10, 'speech': 10} |
| V03 | structure | No duplicate keys | PASS | 0 |
| V04 | values | No NaN/inf in channel features | PASS | 0 |
| V05 | values | Relative band powers sum to 1 | PASS | max |dev|=6.66e-16 |
| V06 | rules | Feature-input policy | PASS | 16 ICA / 24 cleaned; rejected ICA used=0 |
| V07 | rules | 931 artifact windows; no epoch overlaps an artifact | PASS | windows=931, overlapping epoch starts=0 |
| V08 | rules | M1/M2 non-scalp; 22 scalp channels aggregated | PASS | non_scalp=['M1', 'M2'], recordings_with_22=40/40 |
| V09 | rules | No labels or reference-sensitive features | PASS | [] |
| V10 | integrity | Input SHA-256 unchanged since extraction | PASS | 0 mismatches |
| V11 | independent | Spectral recomputation from saved PSD (trapezoid) | PASS | max relative diff=1.16e-07 |
| V11b | independent | Integration-rule sensitivity (rectangle vs trapezoid) | WARN | max relative diff=68.0% |
| V12 | independent | Independent temporal RMS recomputation | PASS | max relative diff=0.00e+00 |
| V13 | independent | Nonlinear kernel synthetic tests | PASS | HFD white=1.99, sine=1.08; DFA white=0.54, 1/f=1.43; PE white=0.99, const=0.00; LZ random>const=True |
| V14 | qc | Primary QC report has no FAIL | PASS | 0 FAIL |
| V15 | log | Extraction log 40/40 OK | PASS | 40 rows, status={'OK': 40} |
| V16 | structure | 10 participants with 4 recordings each | PASS | rows=10, n_recordings=[np.int64(4)] |

## Independent checks

- **V11** recomputes band power from the saved mean PSD with the same trapezoid rule,
  validating the table-to-PSD mapping. **V11b** reports what happens if rectangle
  integration is used instead; the difference is expected at low frequencies because
  the 1/f PSD is steep and the bands have few bins, so V11b is a warning, not a failure.
- **V12** recomputes RMS directly from the raw `.fif` epochs with `scipy.signal.detrend`,
  outside the library's epoch builder.
- **V13** runs the nonlinear kernels on synthetic signals with known expected values
  (white noise HFD ~2, sine HFD ~1, white-noise DFA ~0.5, 1/f DFA ~1.5).
- **V07** checks every saved epoch start against the artifact register; no valid epoch
  may overlap a registered artifact window.
- **V10** re-hashes every input file and compares it with the hash recorded at extraction.

## Sensitivity

The cleaned-only sensitivity tables and comparison are in
`validation_v1/sensitivity_cleaned_only/`.  See `sensitivity_summary.md` for the
feature-level agreement and key condition contrasts.

### Concrete sensitivity findings

- 118 of 151 numeric recording-level features have Pearson r >= 0.80;
  31 are moderate (0.50-0.80) and 0 are below 0.50.
- Alpha power is highly stable (r=0.999) and the meditation-vs-maths/calm alpha
  difference survives the input change. Beta power, Higuchi FD and alpha peak
  frequency are also stable (r >= 0.94).
- Theta power, delta power and RMS are sensitive to the ICA/cleaned choice.
  The RMS meditation-vs-maths contrast changes sign; the theta contrast keeps its
  direction but changes magnitude substantially.
- Frontal alpha asymmetry is stable across recordings (r=0.952), but its
  meditation-calm contrast is ~0.0002 and should not be interpreted.

| Feature | Pearson r | Interpretation |
|---|---:|---|
| abs_power_theta_uv2_mean | 0.687 | sensitivity-dependent |
| rms_uv_mean | 0.788 | sensitivity-dependent |
| dfa_alpha_mean | 0.844 | acceptable |
| alpha_peak_freq_hz_mean | 0.944 | stable |
| frontal_alpha_asymmetry | 0.952 | stable |
| higuchi_fd_mean | 0.988 | stable |
| abs_power_beta_uv2_mean | 0.998 | stable |
| abs_power_alpha_uv2_mean | 0.999 | stable |

- Key condition contrasts with a sign flip: **2** (rms_uv_mean, dfa_alpha_mean).
  The RMS flip is meaningful; the DFA flip is a near-zero meditation-calm difference.
- Recommendation: keep the policy-compliant primary table; report the cleaned-only
  table alongside theta, delta, RMS and any feature with r < 0.80. Do not claim a
  condition effect for a feature whose contrast sign flips.

## What this does and does not prove

- It proves the saved tables are structurally consistent, rule-compliant, reproducible
  from the saved inputs, and free of artifact-window leakage.
- It does **not** prove the features are clinically valid, reference-independent, or
  suitable for Dosha classification.  n = 10 and the provisional labels remain the
  binding limitations.
