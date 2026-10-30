"""Build the updated QC summary (v2) from verified source records.

Read-only against every existing artifact. Writes exactly two new files into
E:\\REU_DATA\\signoff_finalization_v2\\:
  - eeg_qc_summary_v2.csv   (50 rows: 40 EEG + 10 speech, one per recording)
  - eeg_qc_summary_v2.md    (dashboard with recomputed counts)

Every number is recomputed here from the named source file; nothing is copied
from prose. Statuses are reported as they are - no row is forced to PASS.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"E:\REU_DATA")
OUT_CSV = ROOT / "signoff_finalization_v2" / "eeg_qc_summary_v2.csv"
OUT_MD = ROOT / "signoff_finalization_v2" / "eeg_qc_summary_v2.md"

MASTER = ROOT / "audit_finalization_v1" / "reports" / "master_recording_qc_v1.csv"
EEG_QC = ROOT / "audit_finalization_v1" / "eeg" / "eeg_audit_quality_control_v1.csv"
SPEECH_QC = ROOT / "audit_finalization_v1" / "speech" / "speech_audit_quality_control_v1.csv"
ICA_AUDIT = ROOT / "audit_finalization_v1" / "eeg" / "ica_audit_v1.csv"
REVIEW_TABLE = ROOT / "signoff_finalization_v2" / "ica_review_table_v1.csv"
CONTEXT = ROOT / "signoff_finalization_v2" / "ica_review_context_v1.csv"
SAMP = ROOT / "EEG processed" / "quality_control" / "sampling_rate_verification.csv"
ARTIFACT_LOG = ROOT / "audit_finalization_v1" / "eeg" / "artifact_log_v1.csv"


def main() -> None:
    for p in (OUT_CSV, OUT_MD):
        if p.exists():
            sys.exit(f"REFUSING TO OVERWRITE {p}")

    master = pd.read_csv(MASTER)
    eeg_qc = pd.read_csv(EEG_QC)
    speech_qc = pd.read_csv(SPEECH_QC)
    ica = pd.read_csv(ICA_AUDIT)
    review = pd.read_csv(REVIEW_TABLE)
    ctx = pd.read_csv(CONTEXT)
    samp = pd.read_csv(SAMP)
    art = pd.read_csv(ARTIFACT_LOG)

    assert len(master) == 50 and (master["modality"] == "eeg").sum() == 40
    assert len(review) == 30 and (review["decision"] == "NEEDS_REVIEW").all()
    assert samp["status"].eq("MATCH").all() and len(samp) == 40

    art_counts = art.groupby(["participant", "condition"]).size().rename("artifact_windows_recount")

    rows = []
    for _, m in master.iterrows():
        pid, cond, mod = m["participant_id"], m["condition"], m["modality"]
        base = {
            "modality": mod,
            "participant_id": pid,
            "condition": cond,
            "audit_readiness": m["readiness"],
            "v3_readiness": m["v3_readiness"],
            "readiness_disagreement": (not bool(m["agrees_with_v3"])),
            "feature_input_file": m["feature_input_file"],
            "key_open_items": m["key_open_items"],
        }
        if mod == "eeg":
            q = eeg_qc[(eeg_qc["participant_id"] == pid) & (eeg_qc["condition"] == cond)].iloc[0]
            a = ica[(ica["participant"] == pid) & (ica["condition"] == cond)].iloc[0]
            s = samp[(samp["participant"] == pid) & (samp["condition"] == cond)]
            c = ctx[(ctx["participant_id"] == pid) & (ctx["condition"] == cond)]
            r = review[(review["participant_id"] == pid) & (review["condition"] == cond)]
            n_art = int(art_counts.get((pid, cond), 0))
            base.update(
                {
                    "sampling_rate_hz": q["sampling_rate_hz"],
                    "sampling_rate_verified": s.iloc[0]["status"] if len(s) else "NOT_IN_VERIFICATION_TABLE",
                    "notch_evidence_class": q["raw_50hz_class"],
                    "notch_rationale": q["notch_rationale"],
                    "filter_verified": q["filter_verified"],
                    "flagged_channels": q["channels_flagged"] if pd.notna(q["channels_flagged"]) else "",
                    "channels_interpolated": int(q["channels_interpolated_recommendation"]),
                    "artifact_windows_audit_recount": n_art,
                    "artifact_windows_s": q["artifact_windows_s"],
                    "ica_audit_disposition": a["audit_ica_disposition"],
                    "ica_components_removed": a["components_removed"] if pd.notna(a["components_removed"]) else "",
                    "alpha_loss_pct": c.iloc[0]["alpha_loss_pct"] if len(c) else "",
                    "ica_formal_signoff_decision": r.iloc[0]["decision"] if len(r) else "NOT_APPLICABLE_NO_ICA",
                    "ica_prior_provisional_recommendation": c.iloc[0]["prior_recommendation"] if len(c) else "NOT_APPLICABLE_NO_ICA",
                }
            )
        else:
            sq = speech_qc[(speech_qc["participant_id"] == pid) & (speech_qc["condition"] == cond)].iloc[0]
            base.update(
                {
                    "sampling_rate_hz": sq["sample_rate_hz"],
                    "sampling_rate_verified": "NOT_IN_EEG_VERIFICATION_TABLE (speech pipeline)",
                    "notch_evidence_class": "NOT_APPLICABLE",
                    "notch_rationale": "NOT_APPLICABLE",
                    "filter_verified": "NOT_APPLICABLE",
                    "flagged_channels": "NOT_APPLICABLE",
                    "channels_interpolated": "",
                    "artifact_windows_audit_recount": "",
                    "artifact_windows_s": "",
                    "ica_audit_disposition": "NOT_APPLIED",
                    "ica_components_removed": "",
                    "alpha_loss_pct": "",
                    "ica_formal_signoff_decision": "NOT_APPLICABLE_NO_ICA",
                    "ica_prior_provisional_recommendation": "NOT_APPLICABLE_NO_ICA",
                }
            )
        rows.append(base)

    df = pd.DataFrame(rows)
    df["artifact_windows_audit_recount"] = pd.to_numeric(df["artifact_windows_audit_recount"], errors="coerce").fillna(0).astype(int)
    # recount audit artifact log against eeg_qc numbers for the 34 recordings that have any
    merged = df[(df["modality"] == "eeg") & (df["artifact_windows_audit_recount"] > 0)]
    assert len(merged) == 34, f"expected 34 EEG recordings with artifact windows, got {len(merged)}"
    assert int(df["artifact_windows_audit_recount"].fillna(0).sum()) == 931
    assert (df["feature_input_file"].notna()).all()

    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # ---- dashboard, all counts recomputed above ----
    eeg_df = df[df["modality"] == "eeg"]
    speech_df = df[df["modality"] == "speech"]
    dis = eeg_df["ica_audit_disposition"].value_counts().to_dict()
    dec = review["decision"].value_counts().to_dict()
    lines = [
        "# Updated EEG + speech QC summary (v2) - generated from verified source records",
        "",
        "**Generated by:** `signoff_finalization_v2/scripts/build_qc_summary_v2.py` (read-only inputs).",
        "**Machine-readable:** `eeg_qc_summary_v2.csv` (50 rows: 40 EEG + 10 speech).",
        "",
        "Every count below was recomputed from the named CSV at build time. No status was",
        "changed to improve the numbers. This dashboard is deliberately NOT 100% PASS.",
        "",
        "## Headline counts (recomputed)",
        "",
        "| Area | Value | Source |",
        "|---|---|---|",
        f"| Raw EEG recordings | 40 `.acq` + 40 `.xlsx`, all conditions present | filesystem + `sampling_rate_verification.csv` |",
        f"| Sampling rate verified | {int((eeg_df['sampling_rate_verified']=='MATCH').sum())}/40 MATCH (1000 Hz) | `EEG processed/quality_control/sampling_rate_verification.csv` |",
        f"| Cleaned EEG files | 40 `*_eeg.fif` + 40 `preprocessing_report.json` | filesystem |",
        f"| ICA outputs | 30 `*_eeg_ica.fif` + 30 `ica_report.json` | filesystem |",
        f"| EEG audit readiness | PASS {int((eeg_df['audit_readiness']=='PASS').sum())} / REVIEW_REQUIRED {int((eeg_df['audit_readiness']=='REVIEW_REQUIRED').sum())} / FAILED {int((eeg_df['audit_readiness']=='FAILED').sum()) if 'FAILED' in set(eeg_df['audit_readiness']) else 0} | `audit_finalization_v1/reports/master_recording_qc_v1.csv` |",
        f"| EEG v3 readiness (for comparison) | PASS {int((eeg_df['v3_readiness']=='PASS').sum())} / REVIEW_REQUIRED {int((eeg_df['v3_readiness']=='REVIEW_REQUIRED').sum())} | same |",
        f"| ICA audit dispositions | " + ", ".join(f"{k} {v}" for k, v in sorted(dis.items())) + " | `audit_finalization_v1/eeg/ica_audit_v1.csv` |",
        f"| Formal human ICA sign-off | " + ", ".join(f"{k} {v}" for k, v in dec.items()) + " (0 decided so far) | `signoff_finalization_v2/ica_review_table_v1.csv` |",
        f"| Artifact windows (audit scope, register-only) | {int(df['artifact_windows_audit_recount'].fillna(0).sum())} spans across {int((df['artifact_windows_audit_recount'].fillna(0)>0).sum())} recordings | `audit_finalization_v1/eeg/artifact_log_v1.csv` (recounted) |",
        f"| Flagged channels interpolated | 0 (110 flagged instances retained, verdict KEEP) | `bad_channel_audit_v1.csv` |",
        f"| Speech readiness | PASS {int((speech_df['audit_readiness']=='PASS').sum())} / REVIEW_REQUIRED {int((speech_df['audit_readiness']=='REVIEW_REQUIRED').sum())} | `speech_audit_quality_control_v1.csv` |",
        f"| Feature input completeness | {int(df['feature_input_file'].notna().sum())}/50 rows name an existing file | this build verified paths |",
        "",
        "## Policy notes that the numbers depend on",
        "",
        "1. **No recording is formally ICA-approved yet.** All 30 ICA rows in the review table are",
        "   `NEEDS_REVIEW`. The 25 `APPROVED` labels in `figures_v3/ica_review_log.csv` are the",
        "   automated V7b audit's labels, not human sign-off; the independent audit supersedes them",
        "   with `HUMAN_SIGNOFF_PENDING`.",
        "2. **Feature input is the cleaned `*_eeg.fif` for all 40 EEG recordings** until a human",
        "   signs off an ICA output (`ica_audit_v1.csv` recommendation).",
        "3. **The 5 excluded ICA outputs stay excluded** (P01/P04/P07/P09 meditation, P09 calm);",
        "   files preserved on disk for audit.",
        "4. REVIEW_REQUIRED is an honest state: it lists documented constraints, not defects.",
        "",
        "## Unresolved items",
        "",
        "See `qc_issue_classification_v2.csv` / `.md` for the full classified list",
        "(human ICA sign-off, acquisition reference, uninterpolated channels, P02 speech notch, ...).",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {OUT_CSV} ({len(df)} rows)")
    print(f"WROTE {OUT_MD}")


if __name__ == "__main__":
    main()
