# HOLD case evidence (v1) — the seven recordings held for component-level review

**Status: PROVISIONAL REVIEW RECORD ONLY.** Nothing in this file changes a decision. All seven
recordings remain **HOLD FOR REVIEW** exactly as instructed; they are excluded from final ICA
sign-off until their component-level evidence is resolved. No ICA file, figure, audit or packet
was modified, and `ica_signoff_v1.csv` was not created.

Companion files in `E:\REU_DATA\provisional_review_v1\`:

| File | Contents |
|---|---|
| `provisional_decision_report_v1.md` / `.csv` | all 25 pending recordings, provisional decisions |
| `hold_component_metrics_v1.csv` | per removed component: window correlations, alpha share, muscle, frontal weight (16 rows) |
| `hold_case_metrics_v1.csv` | per-recording roll-up of the quantitative evidence below (7 rows) |
| `verification_v1.csv` | six-source component-index cross-check (25/25 PASS) |

## How to read this document

* **Metrics** come from `component_metrics_v1.csv`, `packet_manifest_v2.csv`,
  `ica_audit_v1.csv`, `ica_report.json` and the evidence `.npz` arrays. Every number is quoted
  from a source; nothing is estimated. Values with no source are `NOT AVAILABLE`.
* **Topography readings** are observations of the frozen component maps in
  `EEG processed\eeg\figures_v2\ica\` (viewed read-only).
* **Time-course readings** are observations of `component_evidence_v1\timeseries\<rec>_...png`
  (fixed middle 30 s window, rule-picked, never hand-picked) and **spectrum readings** of
  `component_evidence_v1\spectra\<rec>_...png` (full recording, Welch `nperseg=4096`).
* **Window correlations** (`r EOG window`, `r posterior window`) are computed in this pass from
  `arrays\<rec>_evidence.npz`: Pearson r between the removed source and the EOG proxy
  (Fp1/Fpz/Fp2 mean) / posterior reference (O1/O2/Oz mean) inside that same 30 s window.
  They are **not** the same quantity as the full-recording `eog_corr` in `ica_report.json`;
  both are shown.
* **Alpha share** = fraction of that component's own 1–45 Hz source power lying in 8–12 Hz.
  **Removed alpha share** = the removed components' share of the recording's *total* source
  alpha power (removed ÷ (removed + retained)).
* The documented removal rule (verified against every `ica_report.json` in this pass, notebook
  `EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb` cell V7): a component is removed when
  `|eog_corr| >= 0.40` **and** `frontal_weight >= 0.35` (or `muscle_frac >= 0.70`), capped at 6.

### Summary of the seven

| recording_id | removed ICs | alpha loss % | variance red. % | eog max (comp) | eog max (audit channel-level) | strongest supporting evidence | strongest counter-evidence | recommendation |
|---|---|---|---|---|---|---|---|---|
| P02_meditation | [5] | 9.99 | 7.04 | 0.537 | 0.537 | sign-segregated frontal topography, \|r\| above threshold | alpha bump inside the removed source, window \|r\| only 0.435 | **RETAIN HOLD** |
| P08_calm | [0, 1] | -2.15 (alpha gain) | 47.75 | 0.662 | 0.883 | IC0 time-locked to a ~700 µV frontal transient; alpha *increased* | IC0 topography is weak/diffuse, not focal frontal | **RECONSIDER** (lean approve after checks) |
| P08_maths | [2, 3, 4] | 12.80 | 18.87 | 0.618 | 0.898 | IC3 shows repeated blink-shaped transients in-window | IC2/IC4 have no ocular event in-window; IC4 \|r\|=0.419 vs 0.40 | **RETAIN HOLD** |
| P08_meditation | [2, 5] | 10.56 | 18.09 | 0.518 | 0.717 | frontal topographies, highest removed HF fraction (0.103) | both removed sources carry an alpha bump (10.2% / 8.3%); no blinks in-window | **RETAIN HOLD** |
| P10_calm | [0, 1, 2] | 8.01 | 75.27 | 0.617 | 0.930 | all three react to a ~900 µV ocular event in-window | heaviest removal of the seven; IC1 window r with posterior = 0.821; ocular-looking IC6 retained | **RETAIN HOLD** |
| P10_maths | [0, 1, 2] | 7.83 | 61.97 | 0.590 | 0.912 | IC0 time-locked to a ~900 µV ocular event in-window | IC2 has no ocular signature in-window (r = -0.092); highest removed alpha share (9.27%) | **RETAIN HOLD** |
| P10_meditation | [0, 1] | -10.23 (alpha gain) | 49.12 | 0.600 | 0.820 | frontal topographies, both clear the rule comfortably | no ocular event in the evidence window at all; lowest removed alpha share (1.06%) but 49% variance removed; more frontal-looking IC5 retained | **RETAIN HOLD** |

---

# 1. P02_meditation — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [5] | manifest, audit, evidence index, `ica_report.json`, `.npz`, metrics flags (all agree) |
| eog_corr, IC5 (full recording) | 0.537 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.537 | same |
| eog_corr max, channel-level on removed activity | 0.537 | `ica_audit_v1.csv` |
| r(IC5 vs EOG proxy) in the 30 s window | 0.435 | computed from `.npz` |
| r(IC5 vs posterior) in the 30 s window | -0.244 | computed from `.npz` |
| frontal_weight, IC5 (topography) | 0.493 | `component_metrics_v1.csv` |
| frontal_weight, removal level | 0.493 | manifest / audit |
| muscle_frac, IC5 | 0.068 | `component_metrics_v1.csv` |
| removed high-frequency fraction (30–45 Hz) | 0.073 | manifest / audit |
| Alpha share of IC5's own source PSD | 0.1231 (peak 9.52 Hz) | `component_metrics_v1.csv` / `.npz` |
| IC5 share of total source alpha power | 0.0241 | computed from `.npz` |
| 1–4 Hz power fraction of IC5 | 0.4254 | `component_metrics_v1.csv` |
| Posterior alpha loss | 9.99 % | manifest / audit |
| Variance reduction | 7.04 % | manifest / audit |
| Guards | alpha PASS, eog PASS, frontal PASS, variance PASS, near-guard NO | manifest |

**Evidence files:** component map `EEG processed\eeg\figures_v2\ica\P02_meditation_components.png`;
time course `component_evidence_v1\timeseries\P02_meditation_component_timecourses.png`
(window 283.2–313.2 s of 596.4 s); spectra `component_evidence_v1\spectra\P02_meditation_component_spectra.png`
(full 596.4 s); arrays `component_evidence_v1\arrays\P02_meditation_evidence.npz`;
packet page `EEG processed\quality_control\ica_signoff_packet_v2_review\P02_meditation.html`.

### Component topography (viewed)
IC5 is a **sign-segregated, zero-sum frontal pattern**: a positive band across
Fp1/Fpz/Fp2/F7–F8 with a diffuse negative return over central and parietal sensors, and no
posterior hotspot. This is the textbook shape of a blink/EOC component and it is the shape the
packet's first review point asks for. Every other component on the sheet is retained.

### Time course (viewed)
In the displayed window IC5 (red) is a **continuous, quasi-stationary trace with no discrete
blink transients**; the EOG proxy in the same window shows no large events either (the full-recording
envelope peaks near 100 µV elsewhere, but not here). The window therefore cannot demonstrate
blink locking — it was picked by the fixed middle-window rule, not for ocular content.

### Power spectrum (viewed)
IC5's source PSD sits **above most retained components at 1–7 Hz and 25–45 Hz** and shows a
**local bump at ~9.5–10 Hz inside the alpha band**. The channel panel shows a clear posterior
alpha peak (~10 Hz) that survives the removal (alpha loss 9.99 %).

### Evidence supporting artifact removal
1. Topography is focal and frontal with a compensatory diffuse return — matches the packet's
   ocular criterion and the sign-segregated/zero-sum identity behind `frontal_weight = 0.493`.
2. Full-recording |eog_corr| = 0.537 clears the 0.40 threshold by a clear margin; window
   correlation 0.435 also clears it.
3. `muscle_frac` = 0.068 — the component is not muscle, and `removed_hf_fraction` = 0.073 is modest.
4. Impact is small and non-destructive: variance removed 7.04 %, posterior alpha loss 9.99 %,
   and the removed component holds only **2.4 % of the recording's total source alpha power**.

### Evidence suggesting possible loss of neural activity
1. **12.3 % of IC5's own power lies in 8–12 Hz** with a spectral peak at 9.52 Hz — the largest
   alpha share among the seven HOLD removals — so the component is not purely aperiodic.
2. In a meditation recording a frontal-midline theta/alpha generator is a live possibility, and
   the topography's frontal band **includes Fz/F3/F4**, not only Fp1/Fpz/Fp2.
3. Window correlation with the EOG proxy (0.435) is only 0.035 above the threshold, and the
   window itself contains no blinks to confirm the relationship.

### Missing / inconclusive evidence
* No dedicated EOG channel exists — only a frontal-electrode proxy, which is contaminated by
  frontal EEG (hence the alpha bump also visible in the EOG-proxy channel spectrum).
* No blink-triggered average of IC5 over the full 596 s.
* No quantitative topography peak (which electrode carries maximum |weight|: Fp vs Fz). No ICA
  object was ever saved, so the topography exists only as the frozen PNG.
* No per-component posterior-alpha before/after comparison (only the aggregate 9.99 %).

### Checks needed to resolve
1. Extract IC5's topography weights numerically (refit with the documented parameters,
   `fastica, n_components=20, decim=5, random_state=42`, read-only) and locate the peak electrode.
2. Compute a blink-triggered average of IC5 around every EOG-proxy peak in the full recording.
3. Recompute posterior alpha after excluding **only** IC5 and compare against the 9.99 % total.
4. Test IC5 ↔ EOG-proxy coherence in 0.5–4 Hz (ocular content) versus 8–12 Hz (neural content).

### Recommendation: **RETAIN HOLD**
The ocular reading is plausible (frontal sign-segregated map, |r| = 0.537) but the component
also carries a genuine alpha-range bump, the window offers no blink to confirm the label, and
the whole removal is small (7.04 % variance) so neither outcome is costly — which is exactly
why it should be settled by the four checks above rather than by inference. Nothing in the
evidence is strong enough to overturn the hold, and nothing here justifies rejection.

---

# 2. P08_calm — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [0, 1] | six sources, all agree |
| eog_corr IC0 / IC1 (full recording) | -0.662 / 0.587 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.662 | same |
| eog_corr max, channel-level on removed activity | 0.883 | `ica_audit_v1.csv` |
| r(IC0 / IC1 vs EOG proxy) in window | -0.626 / 0.296 | computed from `.npz` |
| r(IC0 / IC1 vs posterior) in window | 0.469 / -0.296 | computed from `.npz` |
| frontal_weight IC0 / IC1 (topography) | 0.571 / 0.500 | `component_metrics_v1.csv` |
| frontal_weight, removal level | 0.508 | manifest / audit |
| muscle_frac IC0 / IC1 | 0.012 / 0.012 | `component_metrics_v1.csv` |
| removed high-frequency fraction | 0.007 | manifest / audit |
| Alpha share of IC0 / IC1 source PSD | 0.0192 (peak 11.96 Hz) / 0.0404 (peak 10.99 Hz) | `component_metrics_v1.csv` |
| IC0+IC1 share of total source alpha power | 0.0207 | computed from `.npz` |
| 1–4 Hz power fraction of IC0 / IC1 | 0.9038 / 0.7832 | `component_metrics_v1.csv` |
| Posterior alpha **change** | **+2.15 % (alpha loss -2.15 %)** | manifest / audit |
| Variance reduction | 47.75 % | manifest / audit |
| Guards | all PASS, near-guard NO | manifest |

**Evidence files:** `figures_v2\ica\P08_calm_components.png`;
`component_evidence_v1\timeseries\P08_calm_component_timecourses.png` (283.4–313.4 s of 596.7 s);
`component_evidence_v1\spectra\P08_calm_component_spectra.png` (full 596.7 s);
`arrays\P08_calm_evidence.npz`; packet page `...\P08_calm.html`.

### Component topographies (viewed)
**IC1** shows a strong positive frontal band over Fp1/Fpz/Fp2/F7–F8 with a diffuse negative
return — a clear blink/EOC map. **IC0** is much weaker and **diffuse**: a low-amplitude frontal
warm patch with no well-defined focal peak, which is the least convincing ocular map in this
recording.

### Time course (viewed)
**IC0 contains a large slow deflection at ~291–295 s that lines up exactly with an enormous
EOG-proxy transient (~-700 µV) inside the displayed window** — the single strongest piece of
temporal artifact evidence in any of the seven cases. **IC1 shows plateau/step-like morphology**
throughout the window (flat stretches joined by abrupt jumps), which is the signature of an
electrode step or DC shift rather than a phasic blink. The full-recording EOG envelope carries
further spikes up to ~1000 µV (e.g. ~485 s).

### Power spectrum (viewed)
Both removed sources are the **lowest curves of all 20 components across 1–45 Hz**
(~10⁻⁴–10⁻² a.u.²/Hz): their power is dominated by **sub-1 Hz drift** (1–4 Hz fractions of
0.90 and 0.78), with no alpha peak of their own. The posterior channel PSD shows no alpha
deficit after the removal — posterior alpha slightly **increased**.

### Evidence supporting artifact removal
1. IC0 is time-locked in-window to a ~700 µV frontal transient; IC1's full-recording
   |eog_corr| = 0.587 and its step-like morphology both indicate non-neural offsets.
2. Both maps are frontal; frontal weights 0.571 / 0.500.
3. `muscle_frac` = 0.012 for both and `removed_hf_fraction` = 0.007 — no muscle involvement.
4. **Posterior alpha increased by 2.15 %**, so the removal demonstrably does not strip the
   alpha rhythm; the removed components hold only 2.1 % of total source alpha power.
5. The 47.75 % variance removed is concentrated below 1 Hz, i.e. drift/ocular, not oscillatory EEG.

### Evidence suggesting possible loss of neural activity
1. **IC0's window correlation with the posterior reference is +0.469**, higher than its
   correlation with the EOG proxy in the same window (-0.626 is larger in magnitude, but 0.469
   is substantial) — a mixed component, not a purely ocular one.
2. IC0's topography is weak and diffuse rather than focal-frontal, so some neural share cannot
   be excluded from the map alone.
3. The audit's channel-level EOG figure (0.883) and the component-level figure (0.662) disagree
   by 0.221 on this recording; both are correct but they answer different questions, and the
   larger number should not be read as component evidence.

### Missing / inconclusive evidence
* Whether IC1's plateaus are electrode steps (visible on all channels) or a neural slow shift —
  not testable from the component figure alone.
* No blink-triggered average; no numeric topography peaks.
* The reason IC0 and IC1, both drift-dominated, jointly account for 47.75 % of channel variance
  is not decomposed per component.

### Checks needed to resolve
1. Open the raw/cleaned Fp1/Fpz/Fp2 traces around 291 s and confirm the transient is ocular.
2. Check whether IC1's steps appear simultaneously on all 24 channels (electrode step) or only
   frontally (neural/ocular).
3. Quantify IC0's and IC1's topography peak electrodes by refitting the documented decomposition
   read-only.
4. Recompute posterior alpha excluding IC0 alone and IC1 alone, to attribute the (positive)
   alpha change.

### Recommendation: **RECONSIDER — evidence leans ocular/drift, provisional approval is
defensible once checks 1–3 confirm**
This is the only one of the seven where the counter-evidence is weak: alpha *increased*,
muscle content is negligible, the removed power is sub-1 Hz drift, and IC0 is visibly locked to
a huge frontal transient. The residual doubts (diffuse IC0 map, step morphology of IC1) are
answerable by checks 1–3. **No decision is changed here** — it stays HOLD until you accept
those checks.

---

# 3. P08_maths — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [2, 3, 4] | six sources, all agree |
| eog_corr IC2 / IC3 / IC4 (full recording) | -0.618 / -0.505 / 0.419 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.618 | same |
| eog_corr max, channel-level on removed activity | 0.898 | `ica_audit_v1.csv` |
| r(IC2 / IC3 / IC4 vs EOG proxy) in window | -0.155 / **-0.898** / -0.115 | computed from `.npz` |
| r(IC2 / IC3 / IC4 vs posterior) in window | -0.015 / **0.744** / 0.102 | computed from `.npz` |
| frontal_weight IC2 / IC3 / IC4 | 0.618 / 0.500 / 0.618 | `component_metrics_v1.csv` |
| frontal_weight, removal level | 0.544 | manifest / audit |
| muscle_frac IC2 / IC3 / IC4 | 0.026 / 0.022 / 0.038 | `component_metrics_v1.csv` |
| removed high-frequency fraction | 0.008 | manifest / audit |
| Alpha share of IC2 / IC3 / IC4 source PSD | 0.0223 (peak 8.30 Hz) / 0.0439 (peak 11.96 Hz) / 0.0140 (peak 8.06 Hz) | `component_metrics_v1.csv` |
| IC2+IC3+IC4 share of total source alpha power | 0.0377 | computed from `.npz` |
| 1–4 Hz power fraction IC2 / IC3 / IC4 | 0.8577 / 0.7047 / 0.8577 | `component_metrics_v1.csv` |
| Posterior alpha loss | 12.80 % | manifest / audit |
| Variance reduction | 18.87 % | manifest / audit |
| Guards | all PASS, near-guard NO | manifest |

**Evidence files:** `figures_v2\ica\P08_maths_components.png`;
`component_evidence_v1\timeseries\P08_maths_component_timecourses.png` (284.6–314.6 s of 599.2 s);
`component_evidence_v1\spectra\P08_maths_component_spectra.png` (full 599.2 s);
`arrays\P08_maths_evidence.npz`; packet page `...\P08_maths.html`.

### Component topographies (viewed)
**IC3** is a frontal negative band with a diffuse posterior return — the clearest ocular map of
the three. **IC2** is weak and diffuse with only a mild frontal tilt. **IC4** is a **focal
left-anterior** pattern (Fp1/F7 dominance) rather than a symmetric frontal band, which is
compatible with a lateral eye movement but also with a left-frontal neural or temporal source.

### Time course (viewed)
**IC3 shows repeated blink-shaped negative transients at ~287, 291.5, 295.5, 300.5, 305, 307,
309 and 311.5 s**, each aligned with an EOG-proxy spike (100–125 µV) in the channel panel above —
strong, directly observable artifact evidence. **IC2 and IC4 are essentially flat in this
window**, with only small deflections at 295.5 s and 305 s; they show no ocular transients here.

### Power spectrum (viewed)
All three removed sources sit in the **lower half of the source-PSD distribution**; IC3 shows a
small alpha bump near 11.96 Hz, IC2 and IC4 peak below 8.5 Hz. None of them dominates the alpha
band, and the channel panel still shows a posterior alpha peak after removal (12.80 % loss).

### Evidence supporting artifact removal
1. **IC3 is blink-locked in the displayed window** and its map is textbook frontal.
2. IC2 (|r| = 0.618) and IC4 (|r| = 0.419) both clear the 0.40 threshold on the full recording,
   and all three have frontal weights ≥ 0.500 with low muscle (≤ 0.038).
3. Together they account for only **3.8 % of the recording's total source alpha power**;
   alpha loss 12.80 % stays well inside the 30 % guard.
4. `removed_hf_fraction` = 0.008 — the removed projection carries almost no 30–45 Hz content.

### Evidence suggesting possible loss of neural activity
1. **IC4's full-recording |eog_corr| = 0.419 is only 0.019 above the threshold**, and its window
   correlation is -0.115 — no ocular signature in the evidence window at all.
2. **IC2's window correlation is -0.155**, likewise uninformative; its removal rests on the
   full-recording value (0.618) and a weak, diffuse map.
3. IC4's focal left-anterior topography is the one shape that could plausibly be neural
   (left-frontal) rather than ocular.
4. Retained IC5 and IC6 also show frontal-looking maps; they are correctly excluded by the rule
   (|eog_corr| = 0.260 and 0.286 < 0.40), but the visual asymmetry between removed and retained
   frontal maps is unresolved.

### Missing / inconclusive evidence
* No blink-triggered average for IC2 or IC4 — the two components whose justification is
  statistical rather than visual.
* No numeric topography peak for IC4 (Fp1 vs F7 vs F3).
* No per-component alpha attribution for the 12.80 % loss.

### Checks needed to resolve
1. Blink-triggered average of IC2 and IC4 across the full 599 s (does either track blinks?).
2. Numerically locate IC4's topography peak; if it is centred on F7/temporal rather than Fp1,
   treat it as a possible neural/muscle source and re-examine.
3. Posterior alpha before/after excluding IC3 alone versus the full trio.
4. Review `artifact_log_v1.csv` for this recording to see whether ocular windows overlap the
   IC2/IC4 activity.

### Recommendation: **RETAIN HOLD**
IC3's case is closed by the time course, but **two of the three removed components (IC2, IC4)
have no ocular evidence in the evidence window**, and IC4 sits within 0.02 of the correlation
threshold with a topography that could be read as left-frontal neural. The checks above are
cheap and decisive; keep the hold until they are run.

---

# 4. P08_meditation — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [2, 5] | six sources, all agree |
| eog_corr IC2 / IC5 (full recording) | -0.518 / 0.498 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.518 | same |
| eog_corr max, channel-level on removed activity | 0.717 | `ica_audit_v1.csv` |
| r(IC2 / IC5 vs EOG proxy) in window | -0.310 / **0.545** | computed from `.npz` |
| r(IC2 / IC5 vs posterior) in window | 0.042 / -0.359 | computed from `.npz` |
| frontal_weight IC2 / IC5 | 0.523 / 0.483 | `component_metrics_v1.csv` |
| frontal_weight, removal level | 0.500 | manifest / audit |
| muscle_frac IC2 / IC5 | 0.065 / 0.102 | `component_metrics_v1.csv` |
| removed high-frequency fraction | **0.103** (highest of the seven) | manifest / audit |
| Alpha share of IC2 / IC5 source PSD | **0.1022** / **0.0827** (both peak 10.99 Hz) | `component_metrics_v1.csv` |
| IC2+IC5 share of total source alpha power | 0.0360 | computed from `.npz` |
| 1–4 Hz power fraction IC2 / IC5 | 0.5225 / 0.4763 | `component_metrics_v1.csv` |
| 30–45 Hz power fraction IC2 / IC5 | 0.0696 / 0.1082 | `component_metrics_v1.csv` |
| Posterior alpha loss | 10.56 % | manifest / audit |
| Variance reduction | 18.09 % | manifest / audit |
| Guards | all PASS, near-guard NO | manifest |

**Evidence files:** `figures_v2\ica\P08_meditation_components.png`;
`component_evidence_v1\timeseries\P08_meditation_component_timecourses.png` (285.0–315.0 s of 600.0 s);
`component_evidence_v1\spectra\P08_meditation_component_spectra.png` (full 600.0 s);
`arrays\P08_meditation_evidence.npz`; packet page `...\P08_meditation.html`.

### Component topographies (viewed)
**IC5** shows a positive frontal band (Fp1/Fpz/Fp2, extending to F7) with a diffuse negative
return — blink-like. **IC2** is broader and more diffuse: a wide anterior negative field with
mild central positivity, less focal than IC5.

### Time course (viewed)
Both removed sources are **continuous oscillatory traces with no discrete blink transients**
in the displayed window. The EOG proxy in this recording is the quietest of the seven — the
full-recording envelope peaks at only ~60 µV — and the window contains no large ocular events
at all.

### Power spectrum (viewed)
**Both removed sources show a clear alpha bump near 11 Hz** and sit in the upper part of the
low-frequency source group rather than at the bottom. The channel panel shows a strong posterior
alpha peak that is reduced but intact after removal (10.56 % loss). One retained source carries
a sharp ~22 Hz line.

### Evidence supporting artifact removal
1. Both components satisfy the documented rule comfortably: |r| = 0.518 / 0.498 ≥ 0.40 and
   frontal weights 0.523 / 0.483 ≥ 0.35, with frontal-band topographies.
2. **`removed_hf_fraction` = 0.103 and IC5's own 30–45 Hz share = 0.1082** — the removed
   projection carries the most high-frequency (muscle/eye-movement) content of the seven,
   consistent with ocular/facial artifact rather than cortex.
3. IC5's window correlation with the EOG proxy is 0.545, above threshold inside the evidence
   window itself.
4. `muscle_frac` (0.065 / 0.102) stays far below the 0.70 muscle criterion, so this is not a
   muscle-driven removal.

### Evidence suggesting possible loss of neural activity
1. **Both removed components carry an alpha bump (10.2 % and 8.3 % of their own power at
   10.99 Hz)** — the second-highest alpha shares in the HOLD set.
2. **IC2's window correlation with the EOG proxy is only -0.310**, below the 0.40 threshold;
   its justification is entirely the full-recording statistic.
3. No blink transient is visible in the window, and the recording's ocular load is very low
   (~60 µV peaks), so the "ocular" label is inferred rather than observed.
4. Posterior alpha drops 10.56 % — twice the loss of P10_calm, although still well inside the guard.

### Missing / inconclusive evidence
* Whether the alpha bump in IC2/IC5 is volume-conducted posterior alpha sharing a frontal map,
  or a genuine frontal alpha/theta generator — cannot be separated from the PNG.
* Attribution of the 0.103 removed high-frequency fraction to IC2 versus IC5.
* No blink-triggered average (the recording has too few large ocular events in this window).

### Checks needed to resolve
1. Compute the 8–12 Hz and 30–45 Hz shares per component over the **full** recording for IC2 and
   IC5 (values above are from the saved metrics; confirm they are not window-specific).
2. Topography peak extraction for IC2 and IC5 — is the alpha bump's map posterior-dominant?
3. Posterior alpha before/after excluding IC2 alone versus IC5 alone.
4. Inspect a window containing an actual ocular event (the ~475 s envelope peak) rather than the
   fixed middle window.

### Recommendation: **RETAIN HOLD**
Two-sided evidence: the rule is satisfied and the removed projection has the highest
high-frequency content of the seven (0.103), yet both components visibly carry alpha power and
the recording has almost no ocular activity to attribute it to. Neither approving nor rejecting
follows from the current evidence — hold and run checks 1–4.

---

# 5. P10_calm — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [0, 1, 2] | six sources, all agree |
| eog_corr IC0 / IC1 / IC2 (full recording) | 0.484 / -0.617 / 0.502 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.617 | same |
| eog_corr max, channel-level on removed activity | 0.930 (highest of the seven) | `ica_audit_v1.csv` |
| r(IC0 / IC1 / IC2 vs EOG proxy) in window | 0.181 / **-0.893** / 0.458 | computed from `.npz` |
| r(IC0 / IC1 / IC2 vs posterior) in window | -0.171 / **0.821** / -0.505 | computed from `.npz` |
| frontal_weight IC0 / IC1 / IC2 | 0.561 / 0.580 / 0.500 | `component_metrics_v1.csv` |
| frontal_weight, removal level | 0.516 | manifest / audit |
| muscle_frac IC0 / IC1 / IC2 | 0.018 / **0.140** / 0.035 | `component_metrics_v1.csv` |
| removed high-frequency fraction | 0.031 | manifest / audit |
| Alpha share of IC0 / IC1 / IC2 source PSD | 0.0054 / 0.0662 / 0.0621 (all peak 8.06 Hz) | `component_metrics_v1.csv` |
| IC0+IC1+IC2 share of total source alpha power | 0.0415 | computed from `.npz` |
| 30–45 Hz power fraction IC1 | 0.1604 | `component_metrics_v1.csv` |
| Posterior alpha loss | 8.01 % | manifest / audit |
| Variance reduction | **75.27 %** (highest of the seven) | manifest / audit |
| Guards | all PASS, near-guard NO | manifest |

**Evidence files:** `figures_v2\ica\P10_calm_components.png`;
`component_evidence_v1\timeseries\P10_calm_component_timecourses.png` (283.6–313.6 s of 597.3 s);
`component_evidence_v1\spectra\P10_calm_component_spectra.png` (full 597.3 s);
`arrays\P10_calm_evidence.npz`; packet page `...\P10_calm.html`.

### Component topographies (viewed)
**IC2** shows a strong positive frontal band (Fp1/Fpz/Fp2/F7) with a diffuse negative return —
blink-like. **IC1** is a frontal negative band with a slight right bias. **IC0** is a weak,
almost featureless map with a small right-anterior hotspot — the least focal of the three.
Note that **retained IC6 shows a strong frontal-positive / posterior-negative map** that is
visually similar to the removed family.

### Time course (viewed)
**All three removed sources show transients at ~305–307 s that coincide with a massive
EOG-proxy deflection (about -500 → +400 µV) inside the displayed window.** IC0 is otherwise
nearly flat (its variance is concentrated in the ocular events), IC1 and IC2 carry the event
plus smaller bumps at 284–286 s and 302 s. The full-recording EOG envelope has many peaks up to
~800 µV — this is an ocularly busy recording.

### Power spectrum (viewed)
**IC0 is the lowest source PSD of all 20 across the band** (alpha share 0.5 %). IC1 and IC2
have modest low-frequency power with no strong alpha peak. The **EOG-proxy channel PSD is the
highest curve across nearly the whole band**, confirming a dominant frontal artifact. Posterior
alpha survives with only 8.01 % loss.

### Evidence supporting artifact removal
1. Direct temporal evidence: all three removed sources respond to a ~900 µV ocular event inside
   the fixed window; audit channel-level |r| = 0.930 is the highest of the seven.
2. IC2's map is textbook frontal; frontal weights 0.561 / 0.580 / 0.500.
3. Alpha is essentially preserved (8.01 % loss) and IC0 contains almost no alpha (0.54 %).
4. 75.27 % of channel variance is removed from a recording whose EOG-proxy PSD dominates every
   other channel — the variance removed is ocular/drift, not oscillatory EEG.

### Evidence suggesting possible loss of neural activity
1. **IC1's window correlation with the posterior reference is +0.821** — in this window IC1
   co-varies very strongly with posterior signals, which is not the signature of a purely
   ocular component.
2. **IC1's `muscle_frac` = 0.140 (16 % of its power at 30–45 Hz)** is the highest muscle
   fraction in the HOLD set; it is well below the 0.70 criterion but marks it as a
   muscle/eye-movement mixed component.
3. **Retained IC6 has a strongly frontal map yet was never a candidate** (|eog_corr| = 0.093),
   so ocular-looking activity may remain while a mixed component was removed.
4. **75.27 % variance reduction from three components is the heaviest removal of the seven**
   (the alpha-guard exclusion P07_meditation sits at 99.8 %, i.e. this is in the same order of
   magnitude as recordings that failed); the guard is "< 80 %", so it passes by only 4.7 points.

### Missing / inconclusive evidence
* No decomposition of the 75.27 % per component (how much comes from IC0 alone).
* No blink-triggered average; no numeric topography peaks for IC0–IC2 or for retained IC6.
* The posterior coupling of IC1 (+0.821) is unexplained: ocular event volume conduction versus
  genuine posterior involvement.

### Checks needed to resolve
1. Blink-triggered average of IC0, IC1, IC2 over the full 597 s.
2. Posterior alpha before/after excluding **IC1 alone**, and compare with the 8.01 % total.
3. Explain IC1 ↔ posterior coupling in the window: recompute both correlations in a window with
   no ocular event.
4. Re-examine retained IC6: confirm |eog_corr| = 0.093 and frontal weight 0.416 make it a
   non-candidate under the rule, and decide whether the rule should be revisited for this recording.
5. Cross-check `artifact_log_v1.csv` for P10 calm (ocularity of flagged windows).

### Recommendation: **RETAIN HOLD**
This case has the strongest raw artifact evidence of the seven (time-locked ~900 µV events,
audit channel-level |r| = 0.930) **and** the largest removal (75.27 %, only 4.7 points from the
guard) plus an unexplained posterior coupling of IC1 and an ocular-looking retained component.
Both facts need to be settled by checks 1–4 before the hold is lifted — in either direction.

---

# 6. P10_maths — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [0, 1, 2] | six sources, all agree |
| eog_corr IC0 / IC1 / IC2 (full recording) | -0.590 / -0.499 / -0.486 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.590 | same |
| eog_corr max, channel-level on removed activity | 0.912 | `ica_audit_v1.csv` |
| r(IC0 / IC1 / IC2 vs EOG proxy) in window | **-0.867** / -0.428 / **-0.092** | computed from `.npz` |
| r(IC0 / IC1 / IC2 vs posterior) in window | 0.761 / 0.497 / 0.084 | computed from `.npz` |
| frontal_weight IC0 / IC1 / IC2 | 0.601 / 0.500 / 0.610 | `component_metrics_v1.csv` |
| frontal_weight, removal level | 0.542 | manifest / audit |
| muscle_frac IC0 / IC1 / IC2 | 0.047 / 0.035 / 0.067 | `component_metrics_v1.csv` |
| removed high-frequency fraction | 0.029 | manifest / audit |
| Alpha share of IC0 / IC1 / IC2 source PSD | 0.0083 / **0.0937** / **0.0830** (peaks 8.06 Hz) | `component_metrics_v1.csv` |
| IC0+IC1+IC2 share of total source alpha power | **0.0927** (highest of the seven) | computed from `.npz` |
| 1–4 Hz power fraction IC0 / IC1 / IC2 | 0.8734 / 0.6668 / 0.6591 | `component_metrics_v1.csv` |
| Posterior alpha loss | 7.83 % | manifest / audit |
| Variance reduction | 61.97 % | manifest / audit |
| Guards | all PASS, near-guard NO | manifest |

**Evidence files:** `figures_v2\ica\P10_maths_components.png`;
`component_evidence_v1\timeseries\P10_maths_component_timecourses.png` (283.2–313.2 s of 596.4 s);
`component_evidence_v1\spectra\P10_maths_component_spectra.png` (full 596.4 s);
`arrays\P10_maths_evidence.npz`; packet page `...\P10_maths.html`.

### Component topographies (viewed)
All three removed components show the **same family of pattern**: a negative band across the
anterior scalp (Fp1/Fpz/Fp2 with F7/F8) and a mild positive return centrally — three variants
of one ocular source. Retained IC4 has a comparable frontal tilt but is excluded by the rule
(|eog_corr| = 0.220).

### Time course (viewed)
**IC0 shows a large slow biphasic deflection at ~302–304 s that is time-locked to a massive
EOG-proxy event (about -550 → +350 µV) inside the displayed window**; IC1 and IC2 respond to
the same instant with sharper transients, and IC1 deflects again at ~309.5 s matching a smaller
EOG bump. The full-recording EOG envelope peaks near ~700 µV.

### Power spectrum (viewed)
**IC0 has essentially no alpha** (0.83 % share; it is the bottom curve at 8–12 Hz). **IC1 and
IC2 show visible alpha-range bumps near 8–10 Hz** with shares of 9.4 % and 8.3 %. The channel
panel still shows a posterior alpha peak after removal (7.83 % loss).

### Evidence supporting artifact removal
1. IC0 is directly time-locked in-window to a ~900 µV ocular event (window r = -0.867); audit
   channel-level |r| = 0.912.
2. Three matching frontal topographies; all three clear the rule (full-recording |r| =
   0.590 / 0.499 / 0.486, frontal weights 0.601 / 0.500 / 0.610).
3. Muscle content is low (≤ 0.067) and `removed_hf_fraction` = 0.029.
4. Posterior alpha loss is small (7.83 %) and IC0 — the component carrying most of the removed
   variance — has essentially no alpha.

### Evidence suggesting possible loss of neural activity
1. **The trio holds 9.27 % of the recording's total source alpha power — the highest of the
   seven** — and IC1/IC2 individually hold 9.4 % and 8.3 % with peaks at 8.06 Hz, sitting on
   the alpha/theta boundary.
2. **IC2's window correlation with the EOG proxy is only -0.092**: no ocular signature at all in
   the evidence window; its removal rests on the full-recording value (-0.486) and the map.
3. 61.97 % variance removed from three components — a heavy removal, second only to P10_calm.
4. Window correlations of IC1/IC2 with the posterior reference are also positive (0.497 / 0.084),
   so at least part of their variance co-varies with posterior signals.

### Missing / inconclusive evidence
* No per-component attribution of the 61.97 % variance or the 7.83 % alpha loss.
* No blink-triggered average for IC1 and IC2.
* No numeric topography peaks (are IC1/IC2 frontal-only, or do they include Fz/Pz?).

### Checks needed to resolve
1. Blink-triggered average of IC1 and IC2 across the full 596 s.
2. Determine whether the 8–10 Hz bumps of IC1/IC2 are frontal-midline theta (neural) or
   ocular-contaminated alpha: extract topographies and compare with the posterior alpha map.
3. Posterior alpha before/after excluding IC0 alone (expected: nearly unchanged) versus the trio.
4. Cross-check `artifact_log_v1.csv` for P10 maths and the flagged ocular windows.

### Recommendation: **RETAIN HOLD**
IC0's case is well supported by the window, but **IC2 has no ocular evidence in the window
(r = -0.092)**, **IC1 and IC2 together carry the highest alpha share of the seven (9.27 %)**,
and the removal takes 61.97 % of variance. Checks 1–3 decide whether the second and third
components are ocular family members or alpha-bearing neural sources; keep the hold until then.

---

# 7. P10_meditation — HOLD

### Metrics (all available)

| Metric | Value | Source |
|---|---|---|
| Removed component indices | [0, 1] | six sources, all agree |
| eog_corr IC0 / IC1 (full recording) | 0.600 / 0.559 | `component_metrics_v1.csv` / `ica_report.json` |
| eog_corr max over all 20 components | 0.600 | same |
| eog_corr max, channel-level on removed activity | 0.820 | `ica_audit_v1.csv` |
| r(IC0 / IC1 vs EOG proxy) in window | **-0.061** / 0.253 | computed from `.npz` |
| r(IC0 / IC1 vs posterior) in window | 0.259 / -0.101 | computed from `.npz` |
| frontal_weight IC0 / IC1 (topography) | 0.628 / 0.489 | `component_metrics_v1.csv` |
| frontal_weight, removal level | **0.567** (highest of the seven) | manifest / audit |
| muscle_frac IC0 / IC1 | 0.046 / 0.042 | `component_metrics_v1.csv` |
| removed high-frequency fraction | 0.056 | manifest / audit |
| Alpha share of IC0 / IC1 source PSD | 0.0336 (peak 9.77 Hz) / 0.0247 (peak 9.52 Hz) | `component_metrics_v1.csv` |
| IC0+IC1 share of total source alpha power | **0.0106** (lowest of the seven) | computed from `.npz` |
| 1–4 Hz power fraction IC0 / IC1 | 0.7785 / 0.8058 | `component_metrics_v1.csv` |
| Posterior alpha **change** | **+10.23 % (alpha loss -10.23 %)** | manifest / audit |
| Variance reduction | 49.12 % | manifest / audit |
| Guards | all PASS, near-guard NO | manifest |

**Evidence files:** `figures_v2\ica\P10_meditation_components.png`;
`component_evidence_v1\timeseries\P10_meditation_component_timecourses.png` (283.9–313.9 s of 597.8 s);
`component_evidence_v1\spectra\P10_meditation_component_spectra.png` (full 597.8 s);
`arrays\P10_meditation_evidence.npz`; packet page `...\P10_meditation.html`.

### Component topographies (viewed)
**IC0** shows a positive frontal band centred on the left-anterior region (Fp1/F7) with a
diffuse negative return; **IC1** is a similar frontal band shifted slightly. Both are
sign-segregated and zero-sum (consistent with `frontal_weight` = 0.628 / 0.489 and the
removal-level 0.567). **Retained IC5 shows a strong focal Fp1/Fpz positive hotspot** — visually
the most blink-like map on the sheet — yet it is not a removal candidate (|eog_corr| = 0.105).

### Time course (viewed)
In the displayed window **both removed sources are essentially featureless**: flat traces with
small plateau steps at ~286.5 s and ~288.5 s, and **no blink transients whatsoever**. The EOG
proxy in this window shows no large events either; the full recording has only a few ocular
peaks (largest near ~277 s, ~900 µV, and ~540 s).

### Power spectrum (viewed)
**IC0 and IC1 are the two lowest source PSDs of all 20 components across the entire 1–45 Hz
band** — their power lives below 1 Hz (1–4 Hz fractions 0.78 / 0.81). The channel panel shows a
clean posterior alpha peak that **increased by 10.23 %** after removal.

### Evidence supporting artifact removal
1. Both components clear the rule with room to spare: full-recording |eog_corr| = 0.600 / 0.559
   and frontal weights 0.628 / 0.489 (removal-level 0.567, the highest of the seven).
2. Topographies are frontal and sign-segregated — the ocular shape the packet asks for.
3. **Posterior alpha increased by 10.23 %** and the removed components hold only **1.06 % of
   the recording's total source alpha power** — the removal demonstrably does not take alpha.
4. Muscle content is low (0.046 / 0.042); `removed_hf_fraction` = 0.056.

### Evidence suggesting possible loss of neural activity
1. **There is no ocular event anywhere in the evidence window**: IC0's window correlation with
   the EOG proxy is -0.061 and IC1's is 0.253 — both below threshold — and neither source
   correlates with the posterior reference either (0.259 / -0.101).
2. The two removed components have the **least 1–45 Hz power of all 20** yet account for
   **49.12 % of channel variance**: they are slow frontal drift/step components. Removing nearly
   half the recording's variance in this way may be stripping slow frontal activity (DC shifts,
   frontal slow potentials) rather than blinks — a legitimate concern for a meditation
   paradigm where frontal slow/theta activity is meaningful.
3. The plateau/step morphology in the window suggests **electrode steps**, which are an
   instrumentation artifact to be fixed at the channel level, not necessarily an ICA component
   to be removed — and if they are neural slow shifts, the removal is over-aggressive.
4. **Retained IC5 has a more focal frontal map than either removed component** but was not a
   candidate (|eog_corr| = 0.105) — the selection rule and the visual evidence disagree.

### Missing / inconclusive evidence
* The ocular events at ~277 s and ~540 s are outside the fixed window, so blink locking cannot
  be assessed from the supplied evidence.
* No quantified topography peaks (IC0/IC1 versus retained IC5).
* No test of whether the +10.23 % alpha gain is genuine posterior enhancement or a side effect
  of removing a component that shared variance with the posterior reference.
* No check of whether the plateau steps appear on all channels simultaneously.

### Checks needed to resolve
1. Re-render the time course over a window containing an ocular event (e.g. 270–300 s) and
   recompute IC0/IC1 correlations there.
2. Determine the origin of the plateau steps: inspect all 24 channels at 286.5 s and 288.5 s
   (simultaneous → electrode step; frontal-only → ocular/neural).
3. Extract numeric topographies for IC0, IC1 and retained IC5; compare peak electrodes.
4. Verify the posterior alpha gain from the saved `.fif` files (before/after PSD at O1/O2/Oz),
   and confirm it is not an artefact of the metric.

### Recommendation: **RETAIN HOLD — the most ambiguous of the seven**
The rule is satisfied on paper, but the evidence window contains no ocular activity, both
removed components carry the least oscillatory power of all 20 while accounting for half the
channel variance, posterior alpha *increased*, and a more frontal-looking component is retained.
This is precisely the "ambiguous evidence" the reviewer said must not be auto-classified.
Resolve checks 1–4 before any reconsideration; do not reject — no guard failed.

---

## Shared limitations (apply to all seven)

1. **No dedicated EOG channel.** The EOG proxy is the Fp1/Fpz/Fp2 mean, which also carries
   frontal EEG (including alpha) — it inflates `eog_corr` for any frontal component, neural or
   not. This is the single largest source of ambiguity in all seven cases.
2. **The evidence window is fixed (middle 30 s), rule-picked, not ocular-picked.** Four of the
   seven windows contain no large ocular event, so temporal artifact evidence is unavailable
   exactly where it is most needed.
3. **No ICA object was ever saved**, so topographies exist only as frozen PNGs; numeric weights,
   peak electrodes and component round-trip tests are `NOT AVAILABLE` without a read-only refit.
4. **Per-component before/after alpha is not computed anywhere** — only the aggregate posterior
   alpha loss per recording.
5. **Two different EOG metrics and two different frontal-weight metrics** exist (report
   section 8 of `provisional_decision_report_v1.md`); on 6 of the 7 HOLD recordings the audit's
   channel-level figure is substantially higher than the component-level figure. Both are
   correct and both are reported; neither should be quoted as the other.
6. **Ambiguity is not rejection.** No recording here failed a guard, so none of them can be
   REJECTED on this evidence; they are held, per instruction.

## Decision status

| Recording | Status after this pass | Recommendation for your review |
|---|---|---|
| P02_meditation | HOLD FOR REVIEW (unchanged) | RETAIN HOLD |
| P08_calm | HOLD FOR REVIEW (unchanged) | RECONSIDER — evidence leans ocular/drift |
| P08_maths | HOLD FOR REVIEW (unchanged) | RETAIN HOLD |
| P08_meditation | HOLD FOR REVIEW (unchanged) | RETAIN HOLD |
| P10_calm | HOLD FOR REVIEW (unchanged) | RETAIN HOLD |
| P10_maths | HOLD FOR REVIEW (unchanged) | RETAIN HOLD |
| P10_meditation | HOLD FOR REVIEW (unchanged) | RETAIN HOLD |

**No HOLD decision was changed by this pass.** No ICA sign-off file was written; Phase C was not
started.
