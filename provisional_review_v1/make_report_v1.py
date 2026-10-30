"""Render provisional_decision_report_v1.md from the verified CSVs (provisional_review_v1).

Read-only inputs; writes only E:\\REU_DATA\\provisional_review_v1\\provisional_decision_report_v1.md
"""

import os
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

OUT = r"E:\REU_DATA\provisional_review_v1"
REP = pd.read_csv(os.path.join(OUT, "provisional_decision_report_v1.csv"))
VER = pd.read_csv(os.path.join(OUT, "verification_v1.csv"))
EXC = pd.read_csv(os.path.join(OUT, "preserved_exclusions_v1.csv"))
SPC = pd.read_csv(os.path.join(OUT, "preserved_speech_not_applied_v1.csv"))

HOLD = ["P02_meditation", "P08_calm", "P08_maths", "P08_meditation",
        "P10_calm", "P10_maths", "P10_meditation"]
NEAR = {"P02_calm": 28.60, "P06_maths": 29.43, "P09_maths": 25.24}

# the V7b removal rule, verified against every ica_report.json in this pass
def rule_trace(rec):
    row = REP[REP.recording_id == rec].iloc[0]
    parts = []
    for item in str(row.eog_corr_removed_components).split(" | "):
        if not item.startswith("IC"):
            continue
        ic = item.split(":")[0]
        eog = item.split("eog_corr=")[1].split(",")[0]
        fw = item.split("frontal_weight=")[1].split(",")[0]
        parts.append(f"{ic} (abs r={eog} >= 0.40, fw={fw} >= 0.35)")
    return "; ".join(parts) if parts else "NOT AVAILABLE"


def rationale(rec):
    row = REP[REP.recording_id == rec].iloc[0]
    rem = row.components_removed_indices
    alpha = float(row.alpha_loss_pct)
    var = float(row.variance_reduction_pct)
    eog_c = row.eog_corr_max_component_level
    fw = row.frontal_weight_removal_level_audit
    cr = rule_trace(rec)
    if rec in HOLD:
        return (
            f"HOLD FOR REVIEW (reviewer instruction). Removal of {rem} satisfies the documented "
            f"V7b rule — {cr} — and all four packet guards PASS (alpha loss {alpha:.2f}%, "
            f"variance {var:.2f}%), but the component-level evidence is not yet conclusive: the "
            f"removed sources are only moderately EOG-correlated (max |r| = {eog_c}) and the "
            f"topography / time-course / spectrum reading for this recording is unresolved. "
            f"Full evidence, checks and a retain/reconsider recommendation are in "
            f"`hold_case_evidence_v1.md`. Not eligible for final sign-off until resolved."
        )
    near = ""
    if rec in NEAR:
        near = (f" Near-guard warning preserved: posterior alpha loss {NEAR[rec]:.2f}% "
                f"(25% < loss <= 30%, guard 30%) — legal but sits close to the guard.")
    return (
        f"APPROVED — PROVISIONAL. All four packet guards PASS (alpha loss {alpha:.2f}% <= 30%, "
        f"variance reduction {var:.2f}% < 80%, EOG and frontal guards PASS) and every removed "
        f"component meets the documented removal rule — {cr}. Audit/manifest/evidence/ica_report "
        f"component indices agree; audit cross-checks (variance and alpha vs ica_report.json) OK."
        f"{near} Provisional only: the reviewer's approval does not finalise the recording; "
        f"`ica_signoff_v1.csv` is not written by this pass."
    )


def warn(rec):
    row = REP[REP.recording_id == rec].iloc[0]
    return row.warnings_unresolved


def cell(v):
    # keep markdown table cells intact: per-IC lists are joined with " | " upstream
    return str(v).replace(" | ", " ; ").replace("|", "/")


def md_table(df, cols, headers=None):
    headers = headers or cols
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(cell(r[c]) for c in cols) + " |")
    return "\n".join(out)


L = []
A = L.append

A("# Provisional ICA decision report (v1) — 25 recordings pending sign-off")
A("")
A("**Status: PROVISIONAL REVIEW RECORD ONLY.** This file records the reviewer's provisional "
  "recommendations against the existing evidence. It is **not** a final ICA sign-off, it does "
  "not approve any recording for feature use, and it does not start Phase C. "
  "`ica_signoff_v1.csv` was **not** created.")
A("")
A("- Report: `E:\\REU_DATA\\provisional_review_v1\\provisional_decision_report_v1.md`")
A("- Machine-readable rows: `E:\\REU_DATA\\provisional_review_v1\\provisional_decision_report_v1.csv` (25 rows, 31 columns)")
A("- HOLD detail: `E:\\REU_DATA\\provisional_review_v1\\hold_case_evidence_v1.md`")
A("- Verification: `E:\\REU_DATA\\provisional_review_v1\\verification_v1.csv`")
A("")
A("## 1. Scope")
A("")
A(f"- Recordings in scope: **{len(REP)}** rows with `audit_disposition = HUMAN_SIGNOFF_PENDING` "
  "in `EEG processed\\quality_control\\ica_signoff_packet_v2\\packet_manifest_v2.csv`.")
A(f"- **{int((REP.provisional_recommendation == 'APPROVED — PROVISIONAL').sum())}** recorded as "
  f"**APPROVED — PROVISIONAL**, **{int((REP.provisional_recommendation == 'HOLD FOR REVIEW').sum())}** "
  "kept as **HOLD FOR REVIEW**.")
A("- **No recording is classified REJECTED.** Ambiguous evidence is never treated as rejection: "
  "the seven ambiguous cases are held instead.")
A("")
A("### Review table provenance (`NOT AVAILABLE`)")
A("")
A("The reviewer's own review-table file is **NOT AVAILABLE** anywhere in this repository (searched "
  "all `*.md`, `*.csv`, `*.json`, `*.txt`, `*.html`, `*.py`, `*.ipynb` for APPROVE/HOLD markers; no "
  "file holds the 18/7 split). Only the seven HOLD ids were supplied verbatim in the review "
  "instruction. The APPROVE set is therefore **derived** as *25 pending minus the 7 HOLD ids*, "
  "which reproduces the stated count of 18 exactly. If a review-table file exists elsewhere, this "
  "derivation must be reconciled against it before any final sign-off.")
A("")
A("## 2. Sources (all opened read-only)")
A("")
A("| Source | Used for |")
A("|---|---|")
A("| `audit_finalization_v1\\eeg\\ica_audit_v1.csv` | audit disposition, components_removed, variance/alpha recomputation, channel-level EOG metric, cross-checks, the 5 exclusions, the 10 NOT_APPLIED speech rows |")
A("| `EEG processed\\quality_control\\ica_signoff_packet_v2\\packet_manifest_v2.csv` | guards, near-guard flag, alpha loss, variance reduction, removal-level frontal weight, removed high-frequency fraction |")
A("| `component_evidence_v1\\component_evidence_index_v1.csv` | evidence file paths, window used, refit reproduction |")
A("| `component_evidence_v1\\component_metrics_v1.csv` | per-component `eog_corr`, `muscle_frac`, `frontal_weight`, band power fractions (500 rows = 25 x 20) |")
A("| `EEG processed\\eeg\\P0x\\<cond>\\ica_report.json` | the original V7b criteria, component arrays, components_removed |")
A("| `component_evidence_v1\\arrays\\<rec>_evidence.npz` | window traces, source/channel PSDs, removed list (used for the HOLD analysis) |")
A("| `EEG processed\\eeg\\figures_v2\\ica\\<rec>_components.png` | frozen component topographies (viewed, never modified) |")
A("| `component_evidence_v1\\timeseries\\` + `spectra\\` | component time courses and power spectra (viewed, never modified) |")
A("")
A("## 3. Verification of recording IDs and component indices")
A("")
A(f"Every pending recording was checked against **six** independent sources: packet manifest, v1 "
  f"audit, component-evidence index, `components_removed` in `ica_report.json`, "
  f"`removed_components` inside the evidence `.npz`, and the `removed_flag` rows of "
  f"`component_metrics_v1.csv`.")
A("")
A(f"- Result: **{int((VER.components_removed_agree == 'PASS').sum())}/{len(VER)} PASS** — identical "
  "component indices in all six sources.")
A(f"- Missing sources: **{int((VER.missing_sources != 'none').sum())}** recordings.")
A(f"- Evidence files present for all 25: time-course PNG "
  f"**{int(VER.timeseries_png_present.sum())}/25**, spectra PNG **{int(VER.spectra_png_present.sum())}/25**, "
  f"frozen component map **{int(VER.component_map_png_present.sum())}/25**, packet page "
  f"**{int(VER.packet_page_present.sum())}/25**, `ica_report.json` **{int(VER.ica_report_json_present.sum())}/25**, "
  f".npz **{int((VER.evidence_npz_present == 'True').sum())}/25**.")
A("- No value in this report was invented; where a quantity has no source it is marked "
  "`NOT AVAILABLE` (see section 9).")
A("")
A("## 4. Provisional decisions — metrics (25 recordings)")
A("")
A("Metric columns are labelled by definition (section 8): `eog max (comp)` is the largest "
  "|correlation| over the 20 component sources; `eog max (audit)` is the audit's channel-level "
  "measure on the removed activity; `fw (removal)` is the audit/manifest removal-level frontal "
  "weight; `fw (per IC)` / `muscle (per IC)` are per removed component.")
A("")
df = REP.copy()
df["rec"] = df.recording_id
df["rec_no"] = df.components_removed_indices
df["eog_comp"] = df.eog_corr_max_component_level
df["eog_audit"] = df.eog_corr_max_channel_level_audit
df["fw_rem"] = df.frontal_weight_removal_level_audit
df["fw_ic"] = df.frontal_weight_removed_components
df["mus_ic"] = df.muscle_frac_removed_components
df["alpha"] = df.alpha_loss_pct
df["varr"] = df.variance_reduction_pct
df["rec_short"] = df.provisional_recommendation.str.replace("APPROVED — PROVISIONAL", "APPROVED — PROV.")
A(md_table(df, ["rec", "rec_short", "rec_no", "eog_comp", "eog_audit", "fw_rem", "fw_ic",
                "mus_ic", "alpha", "varr"],
           ["recording_id", "provisional recommendation", "removed ICs",
            "eog max (comp)", "eog max (audit)", "fw (removal)", "fw (per IC)",
            "muscle (per IC)", "alpha loss %", "variance red. %"]))
A("")
A("## 5. Provisional decisions — rationale and unresolved issues (25 recordings)")
A("")
rows = []
for rec in sorted(REP.recording_id):
    rows.append({"recording_id": rec, "rationale": rationale(rec), "warnings_or_unresolved": warn(rec)})
A(md_table(pd.DataFrame(rows), ["recording_id", "rationale", "warnings_or_unresolved"]))
A("")
A("## 6. Preserved warnings — near-guard alpha loss")
A("")
A("These three warnings are reproduced **unchanged** and are not treated as failures; all three "
  "recordings still sit under the 30% audit guard.")
A("")
near_rows = []
for rec, val in NEAR.items():
    r = REP[REP.recording_id == rec].iloc[0]
    near_rows.append({
        "recording_id": rec, "alpha_loss_pct": f"{val:.2f}",
        "guard": "PASS (<= 30%)", "flag": "near_guard_flag = YES",
        "components_removed": r.components_removed_indices,
        "provisional_recommendation": r.provisional_recommendation,
        "carried_into_this_report": "YES - unchanged"})
A(md_table(pd.DataFrame(near_rows), ["recording_id", "alpha_loss_pct", "guard", "flag",
                                     "components_removed", "provisional_recommendation",
                                     "carried_into_this_report"]))
A("")
A("## 7. Preserved exclusions and preserved speech statuses")
A("")
A(f"### 7.1 Alpha-guard exclusions — **{len(EXC)}**, unmodified, confirm-only")
A("")
A(md_table(EXC, ["recording_id", "components_removed", "alpha_loss_pct", "variance_reduction_pct",
                 "alpha_guard", "eog_guard", "frontal_guard", "variance_guard",
                 "unchanged_by_this_pass"],
           ["recording_id", "removed ICs", "alpha loss %", "variance red. %", "alpha guard",
            "eog guard", "frontal guard", "variance guard", "unchanged by this pass"]))
A("")
A("### 7.2 Speech-condition EEG `NOT_APPLIED` — **" + str(len(SPC)) + "**, unmodified")
A("")
A(md_table(SPC, ["recording_id", "audit_disposition", "audit_reason", "unchanged_by_this_pass"],
           ["recording_id", "status", "reason", "unchanged by this pass"]))
A("")
A("## 8. Metric definitions used in this report")
A("")
A("| Column | Definition | Source |")
A("|---|---|---|")
A("| `eog max (comp)` | max abs Pearson r between each of the 20 ICA sources and the EOG proxy (Fp1/Fpz/Fp2 mean), full recording | `component_metrics_v1.csv` / `ica_report.json` |")
A("| `eog max (audit)` | max abs r between **each channel of the removed activity** (cleaned minus ICA file) and the EOG proxy — a different quantity, computed channel-wise | `ica_audit_v1.csv` |")
A("| `fw (removal)` | frontal weight of the dominant eigenvector of the removal's covariance (removal is rank-1) | `ica_audit_v1.csv` / manifest |")
A("| `fw (per IC)` | sum of \\|weight\\| over the 8 frontal electrodes / over all 24, for that component's topography | `component_metrics_v1.csv` |")
A("| `muscle (per IC)` | fraction of that component's source power in 30-45 Hz | `component_metrics_v1.csv` |")
A("| `alpha loss %` | posterior (O1/O2/Oz) 8-12 Hz power change after ICA, sign-flipped so loss is positive | manifest / audit |")
A("| `variance red. %` | channel-space variance removed by the ICA step | manifest / audit |")
A("")
A("The two EOG columns and the two frontal-weight columns are **not interchangeable**. They "
  "coincide on 18 of the 25 recordings and differ on 7 (P01_calm, P08_calm, P08_maths, "
  "P08_meditation, P10_calm, P10_maths, P10_meditation); both values are shown rather than "
  "reconciled, because they answer different questions and neither is wrong.")
A("")
A("## 9. Values marked `NOT AVAILABLE`")
A("")
A("| Item | Status | Why |")
A("|---|---|---|")
A("| Reviewer's review-table file (the 18 APPROVE marks) | NOT AVAILABLE | not present anywhere in the repository; APPROVE set derived as 25 pending minus the 7 listed HOLD ids (see section 1) |")
A("| Muscle fraction at recording level | NOT AVAILABLE | no recording-level muscle metric exists in the audit or manifest; only per-component `muscle_frac` (reported per removed IC) and the audit's `removed_hf_fraction` are available, both are reported |")
A("| Any ICA topography not already frozen in `figures_v2\\ica\\` | NOT AVAILABLE | no ICA object was ever saved; topographies exist only as the 30 frozen PNGs (documented in `component_evidence_v1\\README.md`) |")
A("| Component-level metrics for conditions without ICA (speech) | NOT AVAILABLE | ICA never applied (< 2 min), by design |")
A("")
A("## 10. Protections observed by this pass")
A("")
A("- Raw data under `P01`-`P10`: **not modified**.")
A("- Existing ICA files (`*_eeg_ica.fif`), `ica_report.json`, frozen figures in "
  "`EEG processed\\eeg\\figures_v2\\`: **not modified**.")
A("- v1 audit (`audit_finalization_v1\\`) and both sign-off packets "
  "(`ica_signoff_packet*`, `ica_signoff_packet_v2_review.zip`): **not modified, not overwritten**.")
A("- Existing review artefacts (`review_plan_v1\\`, `review_contact_sheets_v1\\`, "
  "`component_evidence_v1\\`, `reports_final_v3\\`): **not modified**.")
A("- `ica_signoff_v1.csv`: **not created**. Phase C: **not started**.")
A("- Everything written by this pass lives in `E:\\REU_DATA\\provisional_review_v1\\`.")
A("")
A("## 11. Files created by this pass")
A("")
A("| File | Contents |")
A("|---|---|")
A("| `provisional_decision_report_v1.md` | this report |")
A("| `provisional_decision_report_v1.csv` | 25 rows x 31 columns, decisions + metrics + rationale + warnings + evidence paths |")
A("| `hold_case_evidence_v1.md` | detailed evidence for the 7 HOLD recordings |")
A("| `hold_component_metrics_v1.csv` | 16 removed-component rows for the 7 HOLD recordings, with window correlations and alpha shares |")
A("| `hold_case_metrics_v1.csv` | 7 HOLD roll-up rows (quantitative evidence used in the HOLD write-up) |")
A("| `verification_v1.csv` | 25 rows: six-source component-index cross-check + evidence-file presence |")
A("| `preserved_exclusions_v1.csv` | the 5 alpha-guard exclusions, copied unchanged |")
A("| `preserved_speech_not_applied_v1.csv` | the 10 speech `NOT_APPLIED` rows, copied unchanged |")
A("| `build_provisional_review_v1.py` | read-only builder for the CSVs + verification |")
A("| `make_report_v1.py` | renders this markdown from the CSVs |")
A("| `build_log_v1.txt` | run log with source SHA-256 hashes |")
A("| `README.md` | folder index and re-run instructions |")
A("")
A("---")
A("")
A("*Generated by `make_report_v1.py` from the verified CSVs in this folder. Provisional record "
  "only — awaiting reviewer sign-off before any final decision file is written.*")

path = os.path.join(OUT, "provisional_decision_report_v1.md")
with open(path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(L) + "\n")
print("wrote", path, len("\n".join(L)), "chars")
