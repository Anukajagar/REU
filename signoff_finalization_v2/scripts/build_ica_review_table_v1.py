"""Build the formal human ICA sign-off review table (v1) and its context table.

Read-only against every existing artifact. Writes exactly two new CSV files into
E:\\REU_DATA\\signoff_finalization_v2\\ and refuses to overwrite anything.

Design rules (from the sign-off task specification):
- Schema: participant_id, condition, recording_id, components_removed,
  artifact_evidence, signal_quality_review, alpha_loss_review, decision,
  reviewer, review_date, comments  (in that order).
- One row per ICA recording (30). Multiple windows from one participant are a
  single recording row - participants are never multiplied.
- Every decision is NEEDS_REVIEW. reviewer and review_date stay empty.
  Nothing marks a recording APPROVED or REJECTED automatically.
- Prior provisional recommendations (2026-10-13 external visual review) are
  carried verbatim into `comments`, explicitly labelled as NOT formal sign-off.
- The 5 previously excluded ICA outputs stay excluded; the table documents why.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"E:\REU_DATA")
OUT_DIR = ROOT / "signoff_finalization_v2"
TABLE_PATH = OUT_DIR / "ica_review_table_v1.csv"
CONTEXT_PATH = OUT_DIR / "ica_review_context_v1.csv"

PACKET = ROOT / "EEG processed" / "quality_control" / "ica_signoff_packet_v2" / "packet_manifest_v2.csv"
ICA_AUDIT = ROOT / "audit_finalization_v1" / "eeg" / "ica_audit_v1.csv"
EEG_QC = ROOT / "audit_finalization_v1" / "eeg" / "eeg_audit_quality_control_v1.csv"
PROV_V2 = ROOT / "provisional_review_v2" / "provisional_decision_report_v2.csv"
BUNDLE = ROOT / "ica_visual_review_bundle_v1"
EVIDENCE_INDEX = ROOT / "component_evidence_v1" / "component_evidence_index_v1.csv"

REQUIRED_COLUMNS = [
    "participant_id",
    "condition",
    "recording_id",
    "components_removed",
    "artifact_evidence",
    "signal_quality_review",
    "alpha_loss_review",
    "decision",
    "reviewer",
    "review_date",
    "comments",
]


def fmt(x, nd=3) -> str:
    if pd.isna(x):
        return "NOT AVAILABLE"
    return f"{float(x):.{nd}f}"


def build() -> None:
    for p in (TABLE_PATH, CONTEXT_PATH):
        if p.exists():
            sys.exit(f"REFUSING TO OVERWRITE existing file: {p}")

    packet = pd.read_csv(PACKET)
    audit = pd.read_csv(ICA_AUDIT)
    qc = pd.read_csv(EEG_QC)
    prov = pd.read_csv(PROV_V2)
    eidx = pd.read_csv(EVIDENCE_INDEX)

    assert len(packet) == 30, f"packet rows = {len(packet)}, expected 30"
    assert set(packet["audit_disposition"]) <= {"HUMAN_SIGNOFF_PENDING", "EXCLUDED"}

    rows, ctx_rows = [], []
    for _, p in packet.iterrows():
        pid, cond = p["participant"], p["condition"]
        rid = f"{pid}_{cond}"
        a = audit[(audit["participant"] == pid) & (audit["condition"] == cond)].iloc[0]
        q = qc[(qc["participant_id"] == pid) & (qc["condition"] == cond)].iloc[0]
        v = prov[prov["recording_id"] == rid].iloc[0]
        e = eidx[(eidx["participant"] == pid) & (eidx["condition"] == cond)]
        e = e.iloc[0] if len(e) else None

        excl = p["audit_disposition"] == "EXCLUDED"
        comps = str(p["components_removed"])

        # ---- evidence: figures actually on disk (bundle paths are relative) ----
        map_rel = f"component_maps\\{rid}_components.png"
        map_abs = BUNDLE / map_rel
        tc_rel = f"timecourses\\{rid}_component_timecourses.png"
        sp_rel = f"spectra\\{rid}_component_spectra.png"
        tc_abs = BUNDLE / tc_rel
        sp_abs = BUNDLE / sp_rel
        tc_txt = tc_rel if tc_abs.exists() else "NOT AVAILABLE"
        sp_txt = sp_rel if sp_abs.exists() else "NOT AVAILABLE"
        ba_rel = f"beforeafter_evidence_v1\\{rid}_beforeafter.png"
        ba_abs = OUT_DIR / ba_rel
        ba_txt = ba_rel if ba_abs.exists() else "PENDING (build_beforeafter_evidence_v1.py not yet run)"

        assert map_abs.exists(), f"component map missing for {rid}: {map_abs}"

        # ---- artifact_evidence (facts only, thresholds from ica_report.json) ----
        artifact_evidence = (
            f"Removed IC(s) {comps}. Max |EOG-proxy correlation| = {fmt(p['eog_corr_max'])} "
            f"(removal rule threshold 0.40); frontal weight = {fmt(p['frontal_weight'])} "
            f"(threshold 0.35); removed-activity 30-45 Hz (muscle) fraction = "
            f"{fmt(p['removed_hf_fraction'])}. Guards: EOG {p['eog_guard']}, frontal "
            f"{p['frontal_guard']}, variance {p['variance_guard']}. "
            f"Evidence figures: component map {map_rel}; timecourse {tc_txt}; "
            f"spectrum {sp_txt}; before/after waveform+PSD {ba_txt}."
        )

        # ---- signal_quality_review (audit QC facts + prior visual flags) ----
        sq_parts = [
            f"Audit readiness {q['audit_readiness']}; ICA audit disposition {a['audit_ica_disposition']}.",
            f"Artifact windows (cleaned file): {int(q['artifact_windows_n'])} spans / "
            f"{fmt(q['artifact_windows_s'], 1)} s, register-only (SKIP_IN_FEATURE_EXTRACTION).",
            f"Flagged channels (KEEP, none interpolated): {q['channels_flagged'] if pd.notna(q['channels_flagged']) else 'none'}.",
            f"Raw 50 Hz class {q['raw_50hz_class']}; notch: {q['notch_rationale']}.",
        ]
        if v["near_guard_flag"] == "YES":
            sq_parts.append("NEAR-GUARD warning: alpha loss within 25-30% band - passing automated guards is NOT proof of artifact.")
        if str(v["warnings"]) not in ("none", "nan"):
            sq_parts.append(f"Prior review warning: {v['warnings']}")
        if excl:
            sq_parts.append(
                "ICA output is EXCLUDED from feature input; the cleaned *_eeg.fif is the "
                "feature file. The *_eeg_ica.fif is preserved on disk for audit only."
            )
        else:
            sq_parts.append(
                "ICA output is pending sign-off; until APPROVED the cleaned *_eeg.fif "
                "remains the feature input."
            )
        signal_quality_review = " ".join(sq_parts)

        # ---- alpha_loss_review ----
        alpha_txt = (
            f"Posterior (O1/O2/Oz) alpha change = {fmt(p['alpha_change_pct'], 2)}% "
            f"(loss {fmt(p['alpha_loss_pct'], 2)}%; negative = alpha gain); variance "
            f"reduction = {fmt(p['variance_reduction_pct'], 2)}%; alpha guard (30% loss) "
            f"{p['alpha_guard']}"
        )
        if p["near_guard_flag"] == "YES":
            alpha_txt += "; NEAR-GUARD (25-30%) - confirm the removed component is ocular, not alpha-generator cortex."
        if excl:
            alpha_txt += (
                f"; EXCLUSION: alpha loss {fmt(p['alpha_loss_pct'], 1)}% exceeds / breaches the "
                "30% guard - confirm the exclusion stands; do not use the ICA file for features."
            )
        alpha_loss_review = alpha_txt + "."

        # ---- comments: prior recommendation, verbatim, labelled ----
        comments = (
            f"PENDING - awaiting formal human sign-off. Prior external visual-review "
            f"recommendation (2026-10-13, provisional_review_v2, NOT formal sign-off): "
            f"{v['decision']} - {v['reason']}"
        )
        if excl:
            comments += (
                " This ICA output was excluded before any visual review; time-course and "
                "spectrum figures were never built for it in the original bundle."
            )

        rows.append(
            {
                "participant_id": pid,
                "condition": cond,
                "recording_id": rid,
                "components_removed": comps,
                "artifact_evidence": artifact_evidence,
                "signal_quality_review": signal_quality_review,
                "alpha_loss_review": alpha_loss_review,
                "decision": "NEEDS_REVIEW",
                "reviewer": "",
                "review_date": "",
                "comments": comments,
            }
        )

        ctx_rows.append(
            {
                "recording_id": rid,
                "participant_id": pid,
                "condition": cond,
                "audit_disposition": p["audit_disposition"],
                "components_removed": comps,
                "eog_corr_max": p["eog_corr_max"],
                "frontal_weight": p["frontal_weight"],
                "removed_hf_fraction": p["removed_hf_fraction"],
                "alpha_loss_pct": p["alpha_loss_pct"],
                "alpha_change_pct": p["alpha_change_pct"],
                "variance_reduction_pct": p["variance_reduction_pct"],
                "alpha_guard": p["alpha_guard"],
                "eog_guard": p["eog_guard"],
                "frontal_guard": p["frontal_guard"],
                "variance_guard": p["variance_guard"],
                "guards_all_pass": p["guards_all_pass"],
                "near_guard_flag": p["near_guard_flag"],
                "audit_readiness": q["audit_readiness"],
                "artifact_windows_n": int(q["artifact_windows_n"]),
                "artifact_windows_s": q["artifact_windows_s"],
                "flagged_channels": q["channels_flagged"] if pd.notna(q["channels_flagged"]) else "",
                "raw_50hz_class": q["raw_50hz_class"],
                "notch_rationale": q["notch_rationale"],
                "feature_input_until_signoff": a["feature_input_recommendation"],
                "ica_fif": a.get("ica_fif", ""),
                "prior_recommendation": v["decision"],
                "prior_reason": v["reason"],
                "evidence_component_map": str(map_abs),
                "evidence_timecourse": str(tc_abs) if tc_txt != "NOT AVAILABLE" else "NOT AVAILABLE",
                "evidence_spectrum": str(sp_abs) if sp_txt != "NOT AVAILABLE" else "NOT AVAILABLE",
                "evidence_beforeafter": str(ba_abs) if ba_abs.exists() else "PENDING",
                "evidence_npz": e["evidence_npz"] if e is not None else "NOT AVAILABLE",
            }
        )

    table = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    context = pd.DataFrame(ctx_rows)

    # ---- guards before writing ----
    assert len(table) == 30 and table["recording_id"].is_unique
    assert (table["decision"] == "NEEDS_REVIEW").all(), "a decision was auto-filled - forbidden"
    assert (table["reviewer"] == "").all() and (table["review_date"] == "").all(), "reviewer identity invented - forbidden"
    for col in ("artifact_evidence", "signal_quality_review", "alpha_loss_review", "comments"):
        assert table[col].notna().all() and (table[col].str.len() > 0).all()
    n_excl = (context["audit_disposition"] == "EXCLUDED").sum()
    assert n_excl == 5, f"expected 5 excluded rows, got {n_excl}"

    table.to_csv(TABLE_PATH, index=False, quoting=csv.QUOTE_MINIMAL, encoding="utf-8")
    context.to_csv(CONTEXT_PATH, index=False, encoding="utf-8")
    print(f"WROTE {TABLE_PATH} ({len(table)} rows x {len(table.columns)} cols)")
    print(f"WROTE {CONTEXT_PATH} ({len(context)} rows x {len(context.columns)} cols)")
    print("decision counts:", table["decision"].value_counts().to_dict())
    print("audit dispositions:", context["audit_disposition"].value_counts().to_dict())


if __name__ == "__main__":
    build()
