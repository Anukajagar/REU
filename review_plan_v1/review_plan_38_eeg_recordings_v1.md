# Review plan — the 38 EEG recordings marked REVIEW_REQUIRED (audit v1)

**Date:** 2026-10-12
**Scope:** inventory and review planning only. No EEG reprocessing, no feature extraction, no status changes.
**Output folder:** `E:\REU_DATA\review_plan_v1\` (new files only).

Companion machine-readable outputs:

| File | Contents |
|---|---|
| `review_summary_table_v1.csv` | 38 rows — one per REVIEW_REQUIRED EEG recording: exact reason, issue codes, evidence paths, action classes, recommended next action. |
| `issue_counts_v1.csv` | Counts by issue type. |

## 0. What REVIEW_REQUIRED means here

`reports\status_criteria_v1.csv` sets REVIEW_REQUIRED when **any** of these is open:
flagged artifact windows > 0; notch applied on weak (< 2×) raw 50 Hz evidence; any channel meeting INTERPOLATE criteria; ICA output present but `EXCLUDED` or `HUMAN_SIGNOFF_PENDING`; or filter reproduction outside tolerance on the tested subset.

It does **not** mean defective or unusable. The audit summary states this explicitly: *"A REVIEW_REQUIRED recording is usable with its documented constraint — it is not defective."* Of the 40 EEG recordings, only P07/speech and P09/speech are PASS (zero artifact windows, no open ICA action) — the same data characteristics that, with one more window, would have flipped them.

Statuses were **not** changed by this plan: every row keeps `REVIEW_REQUIRED`. Nothing was marked PASS.

## 1. Sources and method (read-only)

| Source file | Used for |
|---|---|
| `audit_finalization_v1\reports\master_recording_qc_v1.csv` | The 38-row scope (40 EEG rows − 2 PASS) and the exact `key_open_items` reason text. |
| `audit_finalization_v1\eeg\eeg_audit_quality_control_v1.csv` | Per-recording open items: artifact counts, ICA disposition, flagged channels, 50 Hz class, filter status. |
| `audit_finalization_v1\eeg\ica_audit_v1.csv` | ICA disposition, components removed, alpha loss, component-map path + existence. |
| `audit_finalization_v1\eeg\bad_channel_audit_v1.csv` | Per-channel verdicts (119 rows; 110 flagged instances overall). |
| `audit_finalization_v1\eeg\artifact_log_v1.csv` | 931 artifact windows, all `amplitude >200 uV`, all `SKIP_IN_FEATURE_EXTRACTION`. |
| Context: `raw_50hz_audit_v1.csv`, `filter_verification_v1.csv`, `status_disagreements_v1.csv`, `reports\status_criteria_v1.csv`, `reports\unresolved_issues_v1.md` | Reason classes, policy, disagreements. |

Joins keyed on `participant` + `condition`. Every count below was recomputed from these files, not copied from prose.

## 2. The 38 recordings and the exact reason each is marked REVIEW_REQUIRED

**Reason codes:** `A` artifact windows · `I-H` ICA pending human sign-off · `I-E` ICA excluded (alpha guard) · `I-NA` ICA not applied (speech < 2 min — context only) · `C` flagged channels (verdict KEEP) · `F` notch on weak 50 Hz evidence · `V3` disagrees with v3 PASS · `INV` needs investigation.

| # | Recording | Codes | Exact reason (verbatim from `master_recording_qc_v1.csv` / EEG QC `open_items`) |
|---|---|---|---|
| 1 | P01 calm | A+I-H+C | 72 artifact window(s), 125 s — skip in feature extraction; ICA output pending human sign-off (component maps in figures_v2/ica) — features use the cleaned fif meanwhile |
| 2 | P01 meditation | I-E | ICA output excluded: posterior alpha change −77.9 % (re-confirmed from the saved files) — use the cleaned fif |
| 3 | P01 maths | A+I-H+C | 33 artifact window(s), 55 s — skip in feature extraction; ICA output pending human sign-off — features use the cleaned fif meanwhile |
| 4 | P01 speech | A+I-NA+C | 2 artifact window(s), 2 s — skip in feature extraction |
| 5 | P02 calm | A+I-H+C | 110 artifact window(s), 141 s — skip in feature extraction; ICA output pending human sign-off — features use the cleaned fif meanwhile |
| 6 | P02 meditation | I-H+C+V3 | ICA output pending human sign-off — features use the cleaned fif meanwhile *(v3 said PASS)* |
| 7 | P02 maths | A+I-H+C | 114 artifact window(s), 143 s — skip in feature extraction; ICA output pending human sign-off — features use the cleaned fif meanwhile |
| 8 | P02 speech | A+I-NA+C+F | 2 artifact window(s), 4 s — skip in feature extraction; **notch applied although raw 50 Hz evidence is weak (1.40×)** |
| 9 | P03 calm | A+I-H+C | 7 artifact window(s), 7 s — skip in feature extraction; ICA output pending human sign-off |
| 10 | P03 meditation | A+I-H+C | 1 artifact window(s), 1 s — skip in feature extraction; ICA output pending human sign-off |
| 11 | P03 maths | A+I-H+C | 43 artifact window(s), 92 s — skip in feature extraction; ICA output pending human sign-off |
| 12 | P03 speech | A+I-NA+C | 3 artifact window(s), 4 s — skip in feature extraction |
| 13 | P04 calm | A+I-H | 8 artifact window(s), 11 s — skip in feature extraction; ICA output pending human sign-off |
| 14 | P04 meditation | A+I-E | 1 artifact window(s), 1 s — skip in feature extraction; ICA output excluded: posterior alpha change −87.6 % — use the cleaned fif |
| 15 | P04 maths | A+I-H | 13 artifact window(s), 15 s — skip in feature extraction; ICA output pending human sign-off |
| 16 | P04 speech | A+I-NA | 1 artifact window(s), 1 s — skip in feature extraction |
| 17 | P05 calm | A+I-H+C | 80 artifact window(s), 110 s — skip in feature extraction; ICA output pending human sign-off |
| 18 | P05 meditation | A+I-H+V3 | 1 artifact window(s), 1 s — skip in feature extraction; ICA output pending human sign-off *(v3 said PASS)* |
| 19 | P05 maths | A+I-H+C | 50 artifact window(s), 59 s — skip in feature extraction; ICA output pending human sign-off |
| 20 | P05 speech | A+I-NA | 4 artifact window(s), 6 s — skip in feature extraction |
| 21 | P06 calm | A+I-H+C | 51 artifact window(s), 64 s — skip in feature extraction; ICA output pending human sign-off |
| 22 | P06 meditation | I-H+C+V3 | ICA output pending human sign-off *(v3 said PASS)* |
| 23 | P06 maths | A+I-H+C | 70 artifact window(s), 133 s — skip in feature extraction; ICA output pending human sign-off |
| 24 | P06 speech | A+I-NA | 2 artifact window(s), 5 s — skip in feature extraction |
| 25 | P07 calm | A+I-H+C | 15 artifact window(s), 21 s — skip in feature extraction; ICA output pending human sign-off |
| 26 | P07 meditation | A+I-E+C+INV-1 | 5 artifact window(s), 12 s — skip in feature extraction; ICA output excluded: posterior alpha change −63.7 % — use the cleaned fif; **plus the single >5 mV transient (largest in the dataset)** |
| 27 | P07 maths | A+I-H+C | 46 artifact window(s), 60 s — skip in feature extraction; ICA output pending human sign-off |
| 28 | P08 calm | A+I-H+C | 35 artifact window(s), 55 s — skip in feature extraction; ICA output pending human sign-off |
| 29 | P08 meditation | I-H+C+V3 | ICA output pending human sign-off *(v3 said PASS)* |
| 30 | P08 maths | A+I-H+C | 11 artifact window(s), 31 s — skip in feature extraction; ICA output pending human sign-off |
| 31 | P08 speech | A+I-NA+C | 2 artifact window(s), 2 s — skip in feature extraction |
| 32 | P09 calm | A+I-E+C+INV-2 | 51 artifact window(s), 115 s — skip in feature extraction; ICA output excluded: **40.2 % posterior alpha lost (> 30 % guard)** — use the cleaned fif; human review needed before any use (`ica_status = PROVISIONAL`) |
| 33 | P09 meditation | A+I-E+C | 25 artifact window(s), 66 s — skip in feature extraction; ICA output excluded: posterior alpha change −86.6 % — use the cleaned fif |
| 34 | P09 maths | A+I-H+C | 17 artifact window(s), 25 s — skip in feature extraction; ICA output pending human sign-off |
| 35 | P10 calm | A+I-H+C | 22 artifact window(s), 39 s — skip in feature extraction; ICA output pending human sign-off |
| 36 | P10 meditation | A+I-H+C | 4 artifact window(s), 12 s — skip in feature extraction; ICA output pending human sign-off |
| 37 | P10 maths | A+I-H+C | 27 artifact window(s), 46 s — skip in feature extraction; ICA output pending human sign-off |
| 38 | P10 speech | A+I-NA+C | 3 artifact window(s), 5 s — skip in feature extraction |

Flagged-channel lists per recording are in `review_summary_table_v1.csv` (`flagged_channels`). Only the doubled prefix in the source ("ICA output excluded: ICA output excluded:") was collapsed above; wording otherwise unchanged.

**Four recordings have no artifact windows at all** and are REVIEW_REQUIRED solely (or mainly) because of ICA: P01 meditation, P02 meditation, P06 meditation, P08 meditation.

## 3. Issue groups, evidence, and the recommended next review action

### 3.1 ICA pending human sign-off — 25 recordings — **HUMAN_APPROVAL**
- **Evidence:** `eeg\ica_audit_v1.csv` (`audit_ica_disposition = HUMAN_SIGNOFF_PENDING`, crosschecks `OK/OK`); component maps, all 30 present: `EEG processed\eeg\figures_v2\ica\Pxx_<cond>_components.png`; reviewer metrics `eog_corr_max_recomputed`, `frontal_weight_recomputed`, `alpha_change_pct_recomputed`.
- **Action:** reviewer opens each PNG plus its metrics row and records accept/reject per recording. Until then the feature input stays the cleaned (non-ICA) `.fif` — that is the current, intended state, not a defect.
- **Not:** an automatic approval. The v3 pass auto-approved these by code rule; the audit refuses to accept them without a human.

### 3.2 ICA output excluded (alpha guard) — 5 recordings — **HUMAN_APPROVAL (confirm)**
- **Recordings:** P01 meditation (−77.9 %), P04 meditation (−87.6 %), P07 meditation (−63.7 %), P09 meditation (−86.6 %), P09 calm (40.2 % > 30 % guard).
- **Evidence:** `eeg\ica_audit_v1.csv` (`alpha_loss_pct`, `audit_ica_disposition = EXCLUDED`, `ica_fif_disposition = EXCLUDED from feature input`); maps in `figures_v2\ica\`.
- **Action:** confirm the exclusion stands; the cleaned `.fif` remains the feature input. Files stay on disk for auditing — do not delete.

### 3.3 Flagged artifact windows — 34 recordings (931 windows, 1469 s) — **DOCUMENTED_LIMITATION_ACCEPT**
- **Evidence:** `eeg\artifact_log_v1.csv`, every row `disposition = SKIP_IN_FEATURE_EXTRACTION`, every `reason = amplitude >200 uV on >=1 channel`.
- **Action:** accept under the existing skip policy that feature extraction must honour; optionally spot-check a handful of windows. Largest loads: P02 maths 114/143 s, P02 calm 110/141 s, P05 calm 80/110 s, P06 maths 70/133 s, P01 calm 72/125 s, P09 calm 51/115 s.
- **Note:** the count differs from v3 (931 vs 235) because the audit scans the cleaned files features will actually read; not a disagreement.

### 3.4 Flagged channels — 30 recordings (109 instances) — **DOCUMENTED_LIMITATION_ACCEPT**
- **Evidence:** `eeg\bad_channel_audit_v1.csv` — all verdicts `KEEP (artifact-like, not hardware fault)`; `channels_interpolated_recommendation = 0` for every recording; 0 hardware faults.
- **Most frequent:** Fpz 21, Fp2 21, Fp1 20, F8 17, F7 16 (frontal/ocular), then T8, M2, Cz, O2, F4, Oz, P8 (1 each).
- **Action:** accept as documented. No channel action now; any later interpolation must be done explicitly from this table.

### 3.5 Notch on weak raw 50 Hz evidence — 1 recording — **DOCUMENTED_LIMITATION_ACCEPT** (escalate optional)
- **Recordings:** P02 speech (raw ratio 1.397×, class `weak`, below the 2× support threshold; notch still applied).
- **Evidence:** `eeg\raw_50hz_audit_v1.csv`; reason text in `eeg\eeg_audit_quality_control_v1.csv` and `master_recording_qc_v1.csv`.
- **Action:** analysis lead accepts it as a recorded limitation, or flags it for a future reprocess. **No reprocessing in this pass.**

### 3.6 Status disagreement with v3 — 4 recordings — **HUMAN_APPROVAL (policy confirm)**
- **Recordings:** P02, P05, P06, P08 meditation (v3 `PASS` → audit `REVIEW_REQUIRED`).
- **Evidence:** `eeg\status_disagreements_v1.csv` (`agrees_with_v3 = False`); explained in `reports\audit_final_summary_v1.md` — v3 auto-approved their ICA output, the audit requires human sign-off.
- **Action:** confirm the stricter rule is the intended policy. This is a deliberate disagreement, not an error to reconcile silently.

### 3.7 Further investigation — 2 recordings — **FURTHER_INVESTIGATION**
- **P07 meditation:** single >5 mV transient (largest in the dataset; p99 is 48 µV). Evidence: `eeg\artifact_log_v1.csv`, `reports\unresolved_issues_v1.md` item 10. Action: verify the window is logged once and not double-counted.
- **P09 calm:** `ica_status = PROVISIONAL` with 40.2 % posterior alpha loss over the 30 % guard. Evidence: `eeg\status_disagreements_v1.csv`, `eeg\ica_audit_v1.csv`. Action: resolve provisional vs guard before any ICA output is used.

### 3.8 Context, not status drivers
- **Filter chain not re-tested:** 30 recordings (`not re-tested (subset design)`); the 8 tested recordings all reproduce to < 1e-9 V (`eeg\filter_verification_v1.csv`). Accepted as a documented design choice.
- **ICA not applied:** the 8 speech-condition rows in this list (0.6–1.1 min, below the 2 min reliability rule). No ICA question arises.
- **Global limitations applying to all 40 EEG recordings** (recorded, out of scope for these 38 rows): acquisition reference UNKNOWN (`reports\acquisition_reference_note_v1.md` — blocks reference-sensitive features), assumed 10-20 montage, EOG proxy from Fp1/Fpz/Fp2.

## 4. Counts by issue type

Unique EEG recordings reviewed: **38** (of 40; P07 speech and P09 speech are PASS).

| Issue | Recordings |
|---|---|
| Flagged artifact windows > 0 | 34 |
| ICA pending human sign-off | 25 |
| Flagged channels (KEEP, 0 interpolated) | 30 |
| ICA output excluded (alpha guard) | 5 |
| Status disagrees with v3 PASS | 4 |
| Needs further investigation | 2 |
| Notch on weak 50 Hz evidence | 1 |
| Filter not re-tested (context, not a driver) | 30 |
| ICA not applied — speech too short (context, not a driver) | 8 |

A recording can appear in several rows. Across the 38 rows there are **99 driving issue instances** (A 34 + C 30 + I-H 25 + I-E 5 + V3 4 + F 1), or **109 code instances** counting the 8 `I-NA` and 2 `INV` context codes — an average of 2.6 issues per recording.

Action-class roll-up over the 38 rows:

| Action classes | Recordings |
|---|---|
| HUMAN_APPROVAL + DOCUMENTED_LIMITATION_ACCEPT | 27 |
| DOCUMENTED_LIMITATION_ACCEPT only | 8 |
| HUMAN_APPROVAL + DOCUMENTED_LIMITATION_ACCEPT + FURTHER_INVESTIGATION | 2 |
| HUMAN_APPROVAL only | 1 (P01 meditation) |

## 5. Suggested review order

1. **Policy confirmations first (fast, unblock the rest):** the 4 v3 disagreements → confirm the human-sign-off rule.
2. **ICA exclusions (5):** confirm each exclusion; then P09 calm's provisional status.
3. **ICA sign-off (25):** work through `figures_v2\ica\` PNGs + `ica_audit_v1.csv`; record accept/reject per recording. This is the only step that can change how many recordings leave REVIEW_REQUIRED — and only by an explicit human decision, outside this plan.
4. **Documented limitations (accept in bulk):** artifact-window skip policy, kept channels, P02 speech notch, filter subset — sign off as accepted constraints.
5. **Investigation (2):** P07 meditation transient, P09 calm provisional.
6. **Global blockers (separate track):** acquisition reference, montage/EOG assumptions — needed before reference-sensitive features, independent of these 38.

## 6. Guardrails observed

- Read-only inputs: no raw data, processed EEG, existing report, existing CSV, or preprocessing setting was modified.
- No recording was marked PASS; no approval status was changed; `readiness_unchanged = REVIEW_REQUIRED` on all 38 rows.
- Only three new files were created, all in `E:\REU_DATA\review_plan_v1\`.
- No EEG reprocessing and no feature extraction were performed or planned here.
