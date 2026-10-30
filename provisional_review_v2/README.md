# Provisional ICA Visual Sign-Off Decision Record — v2

**Status:** Provisional recommendation set from external visual review. **Not a completed human sign-off.** No formal mentor approval is claimed anywhere in this record.

**Created:** 2026-10-13
**Output root:** `E:\REU_DATA\provisional_review_v2\`

## What this is

One decision per recording (30 total), derived from the reviewer's recording-by-recording recommendations against the supplied review bundle (`ica_visual_review_bundle_v1`). Decisions and reason text are recorded **verbatim** from the review message — no decision was silently changed, no verdict was invented, and passing automated guard checks is explicitly **not** treated as proof that removed components are artifacts.

## Files

| File | Contents |
| --- | --- |
| `provisional_decision_report_v2.csv` | 30 rows × 14 columns (25 pending + 5 previously excluded) |

## Decision counts

| Decision | Count | Meaning |
| --- | --- | --- |
| `APPROVE_PROVISIONAL` | 18 | Recommended for human confirmation; **not yet formally signed off**. |
| `HOLD` | 7 | Do **not** use the ICA-cleaned file for features until the uncertainty is resolved. |
| `EXCLUSION_CONFIRMATION_REQUIRED` | 5 | Previously excluded recording; do **not** reinstate without reviewing adequate evidence. |

### APPROVE_PROVISIONAL (18)
`P01_calm`, `P01_maths`, `P02_calm`*, `P02_maths`, `P03_calm`, `P03_meditation`, `P03_maths`, `P04_calm`, `P04_maths`, `P05_calm`, `P05_meditation`, `P05_maths`, `P06_calm`, `P06_meditation`, `P06_maths`*, `P07_calm`, `P07_maths`, `P09_maths`*

### HOLD (7)
`P02_meditation`, `P08_calm`, `P08_meditation`, `P08_maths`, `P10_calm`, `P10_meditation`, `P10_maths`

### EXCLUSION_CONFIRMATION_REQUIRED (5)
`P01_meditation`, `P04_meditation`, `P07_meditation`, `P09_calm`, `P09_meditation`

`*` = carries a preserved near-guard warning (see below).

## Preserved warnings (near-guard, requirement 4)

Passing automated guard checks is **not** sufficient on its own to approve ICA removal; the decision also depends on whether the removed component looks like an ocular/muscle artifact and whether its removal damages brain activity.

| Recording | Warning |
| --- | --- |
| `P02_calm` | Near-guard alpha loss 28.60%; confirm ocular vs neural. |
| `P06_maths` | Near-guard alpha loss 29.43%; ocular reading noted but close to the guard. |
| `P09_maths` | Near-guard alpha loss 25.24%; verify topography and spectrum before final approval. |

## Separation of the two groups (requirement 5)

- **25 pending recordings** (`source_set = pending_25`): full evidence in the bundle (component map + time course + spectrum).
- **5 previously excluded recordings** (`source_set = previously_excluded_5`): **time-course and power-spectrum plots are unavailable** in the supplied bundle (`evidence_timecourse` / `evidence_spectrum` = `NOT AVAILABLE`). They are kept separate and cannot be independently confirmed from this visual evidence alone. `P07_meditation` also carries a variance-reduction caution (99.80%).

## CSV column dictionary

| Column | Meaning |
| --- | --- |
| `recording_id` | `<participant>_<condition>` |
| `participant`, `condition` | Split identifiers |
| `source_set` | `pending_25` or `previously_excluded_5` |
| `components_removed` | ICA component indices removed (copied verbatim from bundle manifest) |
| `alpha_loss_pct` | Posterior alpha loss % (copied verbatim; negative = alpha gain) |
| `near_guard_flag` | `YES` if alpha loss in the 25–30% near-guard band |
| `decision` | `APPROVE_PROVISIONAL` / `HOLD` / `EXCLUSION_CONFIRMATION_REQUIRED` |
| `reason` | Reviewer's reason, verbatim from the review message |
| `warnings` | Preserved near-guard / exclusion-gap / HOLD notes; `none` otherwise |
| `review_status` | Constant `PROVISIONAL_RECOMMENDATION_NOT_FORMAL_SIGNOFF` |
| `evidence_component_map` | Bundle-relative path to component-map PNG |
| `evidence_timecourse` | Bundle-relative path to time-course PNG, or `NOT AVAILABLE` |
| `evidence_spectrum` | Bundle-relative path to power-spectrum PNG, or `NOT AVAILABLE` |

## Protections observed

- **New output only.** Raw data, cleaned EEG, ICA FIF files, frozen figures, notebooks, the existing v1 audit (`audit_finalization_v1`), the existing v1 review packet, the v1 provisional review (`provisional_review_v1`), and the review bundle (`ica_visual_review_bundle_v1`) were **not** modified (verified via SHA-256 re-hash; 175 protected files, 0 changed).
- No `ica_signoff_v1.csv` created. Phase C not started. No feature extraction begun.
- No decision silently changed; `HOLD` retained where evidence is insufficient; the 5 exclusions remain excluded.
- Metric context columns copied verbatim from the review bundle manifest; no values invented or recomputed.

## Provenance

- Decisions, reasons, and warnings: reviewer's recording-by-recording recommendations (review message, 2026-10-13).
- Context metrics + evidence paths: `ica_visual_review_bundle_v1\manifest\ica_visual_review_manifest_v1.csv` (itself sourced from `packet_manifest_v2.csv`).
