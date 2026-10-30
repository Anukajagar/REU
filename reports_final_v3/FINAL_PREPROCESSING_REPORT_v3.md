# REU EEG + Speech Preprocessing — Final Report (v3 freeze)

**Date:** 2026-10-12
**Scope:** Final inspection, correction, regeneration and validation of the EEG and speech preprocessing pipeline. Feature extraction and Dosha classification are **out of scope** and were not started.
**Notebooks:** `notebooks/EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb` (90 cells), `notebooks/Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb` (53 cells). Both fully executed under kernel `python314-mne`, 0 error outputs.

---

## 1. What was inspected

| Area | Finding before this pass |
|---|---|
| Raw coverage | 40 `.acq` + 40 `.xlsx` (P01–P10 × calm/meditation/maths/speech), 10 speech `.wav` + 10 `.aac`/`.mp4`. Complete. |
| Cleaned outputs | 40 `*_eeg.fif`, 30 `*_eeg_ica.fif`, 40 `preprocessing_report.json`, 30 `ica_report.json`. Complete, no duplicate `.acq` names. |
| Speech outputs | 10 `Pxx_speech_cleaned.wav`, 10 `quality_report_v3.json`. Complete. |
| Final QC reports | `eeg_final_quality_control_v3.csv` 40×30, `speech_final_quality_review_v3.csv` 10×12. Present. |
| Registers | `v5_bad_channel_review.csv` 110 flagged / 0 interpolate; `v8_segment_exclusion_register.csv` 235 spans / 33 recordings / 467.0 s; `ica_review_log.csv` 40 rows; `raw_50hz_assessment.csv` 40 rows. |
| Notebook hygiene | Duplicated `**Result**` headings in 11 EEG + 6 speech markdown cells. Stale `processed/eeg` / `processed/speech` paths in 8 EEG + 9 speech cells. Section and closing titles still said "v2". A stray backspace character corrupting `backups_pre_validation_20261010` in speech cell 4. |
| ICA documentation | The notebook's final summary said "ICA was documented, not blindly applied … it was not run automatically", while V6/V7 *did* fit FastICA to 30 recordings. A direct contradiction. |
| ICA review status | `ica_review_log.csv` carried only `PROVISIONAL` (26) / `REJECTED` (4) / `NOT_APPLIED` (10). No recording had been positively approved; the component maps had never been audited against the saved files. |
| Per-recording JSONs | `preprocessing_report.json` said `ICA: … NOT applied in this pass` and `Output file: E:\REU_DATA\processed\eeg\…` — a folder that does not exist. |

---

## 2. Corrections made

All corrections are inside the two `*_v3.ipynb` notebooks, except the deliberate JSON annotation (§2.6).

### 2.1 Stale paths (documentation only)
`processed/eeg` → `EEG processed/eeg` and `processed/speech` → `SPEECH processed/speech` in every cell that described the *current* output location. Cells 6 (EEG) and 4 (speech), which document the *historical* rename, were deliberately left untouched so they still record the old path.

### 2.2 Duplicated headings, stale titles
Removed the doubled `**Result**` line from 11 EEG and 6 speech markdown cells. Retitled `# v2 — Preprocessing validation` → `# v3 — …`, `# v2 — Speech quality review` → `# v3 — …`, and both closing summaries to `### Final v3 summary — …`.

### 2.3 Stray control character
Speech cell 4 contained `backups_pre_validation_20261010` with a literal backspace (`0x08`) in place of the `b`. Removed.

### 2.4 Mislabelled report file
Speech STEP 13 documentation said `quality_report.json`; the step actually writes `quality_report_v3.json`. Documentation corrected.

### 2.5 ICA narrative reconciled (F2)
EEG cell 66 now states the true chronology — STEPs 1–15 do not run ICA; V6/V7 fitted it later under review — and cell 82 records the reconciliation instead of asserting a contradiction. Nothing historical was deleted.

### 2.6 Per-recording JSONs finalised
All 40 `preprocessing_report.json` files received a `v3_finalization` block: corrected output path, cleaned and ICA `.fif` paths, the final ICA review status + reason + method + date, and the exact `feature_input_file`. The original `ICA` and `Output file` wording is preserved and annotated, not overwritten. **These are the only 40 pre-existing files this pass modified** (see §5).

### 2.7 Closing cells added
- EEG cells 88–89: the JSON finalisation back-patch + its What/Why/Result.
- Speech cells 51–52: a consolidated both-modality summary written to `reports_final_v3/`.

---

## 3. The V7b quantitative component audit (new)

The 26 `PROVISIONAL` dispositions were an unresolved TODO. Rather than inventing a human sign-off, the removed activity was **measured back out of the saved files** and a documented decision rule was applied identically to all 30 ICA recordings.

**Evidence recomputed from disk** (cleaned `*_eeg.fif` vs `*_eeg_ica.fif`):
- variance removed and posterior-alpha (O1/O2/Oz) change — **cross-checked against the values already stored in `ica_report.json`**
- the removed activity itself (cleaned − ica): dominant spatial pattern → **frontal weight**; correlation with the frontal EOG proxy (Fp1/Fpz/Fp2) → **|r|**; 30–45 Hz share of its PSD → muscle test

**Decision rule (documented in the notebook, not ad hoc):**

| Status | Condition |
|---|---|
| **APPROVED** | \|r\| ≥ 0.40 **and** frontal weight ≥ 0.35 (the thresholds the fitting rule already used) **and** alpha loss ≤ 30 % **and** variance reduction ≤ 80 % **and** no open batch flag |
| **REJECTED** | the four previously audited rejections — re-confirmed here, not changed |
| **PROVISIONAL** | any condition above unmet; the unmet condition is written down |
| **NOT_APPLIED** | speech / < 2 min (unchanged) |

**Outcome:**

| Status | n | Recordings |
|---|---|---|
| APPROVED | 25 | — |
| PROVISIONAL | 1 | P09 calm (−40.2 % posterior alpha, above the 30 % guard) |
| REJECTED | 4 | P01, P04, P07, P09 meditation (alpha −77.9 / −87.6 / −63.7 / −86.6 %; P07 also a −99.8 % variance collapse) |
| NOT_APPLIED | 10 | all speech recordings (< 2 min) |

- Recomputed variance / alpha change **matched `ica_report.json` for 30/30** recordings.
- EOG correlation ≥ 0.537 and frontal weight ≥ 0.35 in **all 30**; removed activity is genuinely ocular, not muscle (30–45 Hz fraction 0.003–0.103).
- No false rejections were introduced and no rejection was reversed.

`review_method = "quantitative component audit (V7b), recomputed from the saved fif files"`, `review_date = 2026-10-11`. This is labelled as an automated audit, **not** a human sign-off.

**Feature input is now explicit** in `ica_review_log.csv`, `eeg_final_quality_control_v3.csv` and every JSON: 26 recordings read the `*_eeg_ica.fif`; 14 (4 REJECTED + 10 NOT_APPLIED) read the cleaned `*_eeg.fif`.

---

## 4. Final QC counts

### 4.1 EEG — `eeg_final_quality_control_v3.csv` (40 rows, 32 cols)

| Readiness | n |
|---|---|
| PASS | **6** |
| REVIEW_REQUIRED | **34** |
| FAILED | **0** |

**EEG modality status: `READY_WITH_DOCUMENTED_LIMITATIONS`.**

- **PASS (6):** P02 meditation, P05 meditation, P06 meditation, P07 speech, P08 meditation, P09 speech — no flagged segments, ICA approved or not applicable, notch supported by raw evidence.
- **REVIEW_REQUIRED (34):** all carry at least one *documented* limitation (segment register entries, a REJECTED/PROVISIONAL ICA output, or weak raw 50 Hz evidence). None is a defect; every one is something feature extraction must respect.

Nothing was relabelled to make the numbers look better — REVIEW_REQUIRED is the honest state.

### 4.2 Speech — `speech_final_quality_review_v3.csv` (10 rows, 12 cols)

| Readiness | n |
|---|---|
| PASS | **7** (P01–P04, P06–P08) |
| REVIEW_REQUIRED | **3** |
| FAILED | **0** |

**Speech modality status: `READY_WITH_DOCUMENTED_LIMITATIONS`.**
- **P05** — low estimated SNR (13.8 dB). A recording property, not a processing defect. Noise reduction was deliberately not applied and that decision is logged.
- **P09** — stereo level difference +10.1 dB. Both channels preserved via lag-aligned mean.
- **P10** — 129 clipped samples in the right channel only (0.003 %); 0 clipped samples in the processed mono file. Repair would alter the signal, so it is recorded as a limitation.

`preprocessing_log_v3.csv`: 10/10 `verification_status = PASS` (the STEP 13 false-FAIL, F3, was already fixed and re-verified).

### 4.3 ICA — `figures_v3/ica_review_log.csv` (40 rows, 23 cols)
APPROVED 25 · PROVISIONAL 1 · REJECTED 4 · NOT_APPLIED 10 · FAILED 0. Cross-check OK 30/30. No null feature inputs.

### 4.4 Artifact register — `figures_v3/v8_segment_exclusion_register.csv`
235 spans · 33/40 recordings · 467.0 s · 0 duplicate rows · 0 non-positive durations. **Register only — nothing was removed; original timing and events are preserved.** Seven recordings have zero flagged windows.

### 4.5 Consolidated — `reports_final_v3/consolidated_preprocessing_summary_v3.csv/.json`
50 rows (40 EEG + 10 speech), one per modality/participant/condition, naming the exact file feature extraction must read. 0 null feature inputs.

---

## 5. Integrity and freeze confirmation

`reports_final_v3/integrity_verification_v3.csv/.json` — **32 checks, 0 FAIL, 0 REVIEW.**

| Check | Result |
|---|---|
| Raw `.acq`/`.xlsx`/`.wav`/`.aac` re-hashed vs `INVENTORY_BASELINE.csv` | **0/100 changed** |
| v1 + v2 notebooks vs baseline | **0/4 changed** |
| Root-protected files vs baseline | **5/5 unchanged** |
| `INVENTORY_BASELINE.csv` itself | **unmodified** |
| Coverage | 40 acq, 40 xlsx, 10 wav, 10 aac/mp4, 40 cleaned fif, 30 ica fif, 40+30 JSONs, 10 cleaned wav, 10 `quality_report_v3.json` — all exact |
| Duplicate `.acq` basenames | 0 |
| Files this pass modified | **121**, of which the only pre-existing artifacts are the **40 intentional `preprocessing_report.json` finalisations** |
| Notebooks executed | 90 + 53 cells, 0 error outputs |

**Pre-existing deviations (not caused by this pass):** 13 speech non-v3 reports (`quality_report.json` ×10, `reports/final_summary.json`, `missing_files_report.csv`, `preprocessing_log.csv`) already differed from `INVENTORY_BASELINE.csv` **before** this pass — they were rewritten by the 2026-10-10 evening run. They are left as-is.

**One baseline entry has no file on disk:** `information/~$ doubts in REU.docx` — a Microsoft Word lock file, not data.

---

## 6. Paths

| Artefact | Path |
|---|---|
| EEG notebook (final) | `E:\REU_DATA\notebooks\EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb` |
| Speech notebook (final) | `E:\REU_DATA\notebooks\Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb` |
| Raw data (untouched) | `E:\REU_DATA\P01\ … \P10\` |
| Integrity anchor (untouched) | `E:\REU_DATA\INVENTORY_BASELINE.csv` |
| Cleaned EEG | `E:\REU_DATA\EEG processed\eeg\Pxx\<cond>\Pxx_<cond>_eeg.fif` |
| ICA EEG | `…\Pxx_<cond>_eeg_ica.fif` + `ica_report.json` |
| EEG final QC | `E:\REU_DATA\EEG processed\eeg\eeg_final_quality_control_v3.csv` |
| EEG registers / logs | `E:\REU_DATA\EEG processed\eeg\figures_v3\` (`ica_review_log.csv`, `v5_bad_channel_review.csv`, `v8_segment_exclusion_register.csv`, `raw_50hz_assessment.csv`, `v3_50hz_classification.csv`, `v7_ica_batch_summary.csv`, `ica/*.png`) |
| EEG per-recording reports | `E:\REU_DATA\EEG processed\eeg\Pxx\<cond>\preprocessing_report.json` |
| Cleaned speech | `E:\REU_DATA\SPEECH processed\speech\Pxx\Pxx_speech_cleaned.wav` |
| Speech reports | `E:\REU_DATA\SPEECH processed\speech\reports\` (`speech_final_quality_review_v3.csv`, `preprocessing_log_v3.csv`, `audio_quality_report_v3.csv`, `speech_inventory_v3.csv`, `missing_files_report_v3.csv`, `final_summary_v3.json`) |
| **Consolidated summary** | `E:\REU_DATA\reports_final_v3\consolidated_preprocessing_summary_v3.csv` / `.json` |
| **Integrity verification** | `E:\REU_DATA\reports_final_v3\integrity_verification_v3.csv` / `.json` |
| **This report** | `E:\REU_DATA\reports_final_v3\FINAL_PREPROCESSING_REPORT_v3.md` |
| Verification scripts | `E:\REU_DATA\reports_final_v3\scripts\` |

---

## 7. Unresolved limitations

1. **Four meditation recordings have unusable ICA output** (P01, P04, P07, P09). The decomposition destroyed posterior alpha. Feature extraction must use the cleaned `*_eeg.fif` for these. They are not deleted; they remain on disk for auditing.
2. **P09 calm is PROVISIONAL, not approved.** It loses 40.2 % of posterior alpha. The `*_eeg_ica.fif` must not be used until a human signs off on the component maps. Until then the cleaned `*_eeg.fif` is the safe input.
3. **Three recordings sit just under the alpha guard** — P06 maths (−29.4 %), P02 calm (−28.6 %), P09 maths (−25.2 %). They are APPROVED under the stated rule and reported transparently. No threshold was moved.
4. **Weak raw 50 Hz evidence for P02 speech** (raw ratio 1.40×). The notch was still applied because the pipeline notches when *any* lift is detected; the weakness is recorded in the QC table rather than hidden.
5. **110 flagged channel instances were never interpolated** (0 INTERPOLATE). They are retained for review. Any later stage that interpolates must do so explicitly from `v5_bad_channel_review.csv`.
6. **34/40 EEG recordings carry documented limitations.** This is the honest state of the data, not a processing failure.
7. **Speech S4 is very slow** (~54 min). Its integer-lag search uses `np.correlate(..., mode="full")` on 48 kHz, 10 s windows — O(n²). It was **left unchanged** because altering it would change the reported lag/correlation values. Budget for it on any re-run.
8. **The ICA audit is automated, not human-reviewed.** The V7b rule is quantitative and reproducible from the saved files; a human looking at the 30 scalp-map figures would be a strictly better check and has not been done.

---

## 8. Conclusions

### 8.1 Is the preprocessing finalised? — **Yes.**
Both v3 notebooks run end-to-end from raw data with zero errors. Every stale path, duplicated heading, mislabelled file and contradictory ICA statement has been corrected. The 40 per-recording JSONs carry the final disposition. The V7b audit closed the outstanding ICA question with evidence recomputed from the saved files, and it matched the recorded values 30/30. No further preprocessing work is outstanding.

### 8.2 Is it approved for analysis (feature extraction)? — **Yes, with the documented fallbacks.**
50 recordings (40 EEG + 10 speech) are ready, with a named input file for every single one. Feature extraction must honour three constraints, all machine-readable:
- read `feature_input_fif` from `consolidated_preprocessing_summary_v3.csv` / `ica_review_log.csv` (26 ICA files, 14 cleaned files);
- skip the 235 flagged windows in `v8_segment_exclusion_register.csv`;
- treat P09 calm as provisional until signed off.
No FAILED recordings. Nothing needs reprocessing.

### 8.3 What limitations remain? — **Eight, all recorded.**
Four unusable ICA outputs (meditation), one provisional ICA (P09 calm), three near-threshold alpha losses, one weak-notch recording, 110 uninterpolated flagged channels, 34/40 EEG recordings carrying documented warnings, one slow cell, and the absence of a human ICA sign-off. None of these is hidden, none was tuned away, and none blocks analysis — they are exactly the things the feature-extraction stage has to respect.
