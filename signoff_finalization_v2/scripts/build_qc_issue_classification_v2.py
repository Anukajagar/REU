"""Build the QC issue classification table (v2).

Classifies every open/closed QC issue as exactly one of:
  RESOLVED_WITH_EVIDENCE | REQUIRES_HUMAN_REVIEW | REQUIRES_TECHNICAL_CORRECTION |
  DOCUMENTED_LIMITATION_OR_WAIVER

Read-only against every existing artifact. Cheap fact-checks are asserted at
build time so the classifications cannot silently drift from the evidence.
Writes: qc_issue_classification_v2.csv and .md into signoff_finalization_v2\\.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"E:\REU_DATA")
OUT_CSV = ROOT / "signoff_finalization_v2" / "qc_issue_classification_v2.csv"
OUT_MD = ROOT / "signoff_finalization_v2" / "qc_issue_classification_v2.md"

CLASSES = [
    "RESOLVED_WITH_EVIDENCE",
    "REQUIRES_HUMAN_REVIEW",
    "REQUIRES_TECHNICAL_CORRECTION",
    "DOCUMENTED_LIMITATION_OR_WAIVER",
]


def main() -> None:
    for p in (OUT_CSV, OUT_MD):
        if p.exists():
            sys.exit(f"REFUSING TO OVERWRITE {p}")

    # ---- cheap fact checks backing the classifications ----
    samp = pd.read_csv(ROOT / "EEG processed" / "quality_control" / "sampling_rate_verification.csv")
    assert len(samp) == 40 and samp["status"].eq("MATCH").all(), "sampling-rate evidence changed"

    old_tree = ROOT / "processed"
    new_tree = ROOT / "EEG processed" / "eeg"
    assert not old_tree.exists(), "legacy 'processed' tree unexpectedly exists"
    assert new_tree.exists()

    maps_v2 = list((ROOT / "EEG processed" / "eeg" / "figures_v2" / "ica").glob("*.png"))
    maps_v3 = list((ROOT / "EEG processed" / "eeg" / "figures_v3" / "ica").glob("*.png"))
    assert len(maps_v2) == 30 and len(maps_v3) == 0, (len(maps_v2), len(maps_v3))

    art = pd.read_csv(ROOT / "audit_finalization_v1" / "eeg" / "artifact_log_v1.csv")
    p07m = art[(art["participant"] == "P07") & (art["condition"] == "meditation")]
    p07_big = p07m[p07m["peak_uV"] > 5000]
    assert len(p07m) >= 1, "P07 meditation has no artifact windows"
    assert len(p07_big) == 2, f"expected two >5 mV windows for P07 meditation, got {len(p07_big)}"

    review = pd.read_csv(ROOT / "signoff_finalization_v2" / "ica_review_table_v1.csv")
    assert (review["decision"] == "NEEDS_REVIEW").all() and len(review) == 30

    ba = pd.read_csv(ROOT / "signoff_finalization_v2" / "beforeafter_evidence_v1" / "beforeafter_index_v1.csv")
    assert len(ba) == 30 and (ba["status"] == "BUILT").all()

    issues = [
        dict(
            issue_id="QC-01",
            title="Physical acquisition reference is UNKNOWN",
            scope="40 EEG recordings",
            evidence="audit_finalization_v1/reports/acquisition_reference_note_v1.md (no rereference call in any notebook, no reference attribute in .acq headers, no acquisition docs in information/)",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Acquisition team (only they can answer)",
            interim_disposition="Documented as UNKNOWN; no reference applied or assumed. Reference-sensitive features (Laplacian, CSD, linked-mastoid) must not be computed until answered. NOT to be guessed.",
        ),
        dict(
            issue_id="QC-02",
            title="Formal human ICA sign-off outstanding (0 of 30 decided)",
            scope="30 ICA recordings",
            evidence="signoff_finalization_v2/ica_review_table_v1.csv (all rows decision=NEEDS_REVIEW, reviewer/date empty); audit_finalization_v1 ica_audit_v1.csv (25 HUMAN_SIGNOFF_PENDING)",
            classification="REQUIRES_HUMAN_REVIEW",
            action_owner="Human reviewer (mentor or designated reviewer)",
            interim_disposition="Review workflow delivered: review table + context + component maps + timecourses + spectra + new before/after figures for all 30. Feature input stays the cleaned *.fif until APPROVED. The v3 auto-APPROVED labels are NOT accepted as sign-off.",
        ),
        dict(
            issue_id="QC-03",
            title="5 ICA outputs excluded (alpha guard) - exclusion never formally confirmed",
            scope="P01/P04/P07/P09 meditation, P09 calm",
            evidence="ica_audit_v1.csv (audit_ica_disposition=EXCLUDED; alpha losses -77.9/-87.6/-63.7/-86.6%, P09 calm 40.2% > 30% guard); files preserved on disk",
            classification="REQUIRES_HUMAN_REVIEW",
            action_owner="Human reviewer",
            interim_disposition="Exclusions preserved; review table rows carry EXCLUSION_CONFIRMATION_REQUIRED context and now include new before/after figures for all 5 (previously they had none). Do not reinstate without evidence.",
        ),
        dict(
            issue_id="QC-04",
            title="110 flagged channel instances never interpolated (0 INTERPOLATE)",
            scope="31 EEG recordings",
            evidence="audit_finalization_v1/eeg/bad_channel_audit_v1.csv (all verdicts KEEP, artifact-like, 0 hardware faults)",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Analysis lead",
            interim_disposition="Retained by design. Any later interpolation must be explicit and driven from bad_channel_audit_v1.csv.",
        ),
        dict(
            issue_id="QC-05",
            title="P02 speech EEG: notch applied on weak raw 50 Hz evidence (1.40x)",
            scope="1 EEG recording",
            evidence="audit_finalization_v1/eeg/raw_50hz_audit_v1.csv; eeg_audit_quality_control_v1.csv notch_rationale",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Analysis lead (accept or schedule future reprocess)",
            interim_disposition="Kept as-is, recorded in QC tables. No reprocessing performed in this pass.",
        ),
        dict(
            issue_id="QC-06",
            title="P07 meditation cleaned file contains two >5 mV transients (prior docs said 'single')",
            scope="1 EEG recording",
            evidence=(
                f"artifact_log_v1.csv: {len(p07m)} windows logged for P07 meditation; "
                f"{len(p07_big)} of them exceed 5 mV (Fpz peaks "
                + " and ".join(f"{v/1000:.2f} mV @ {a:.0f}-{b:.0f} s" for v, a, b in
                               zip(p07_big['peak_uV'], p07_big['t_start_s'], p07_big['t_end_s']))
                + "), each logged once (no duplicates)"
            ),
            classification="RESOLVED_WITH_EVIDENCE",
            action_owner="none - logged",
            interim_disposition=(
                "Correction of prior wording: unresolved_issues_v1 item 10 said 'a single >5 mV "
                "transient'; the register shows TWO ~23.3 mV Fpz events (215-219 s and 264-268 s), "
                "each logged once. Both windows are in the artifact register with disposition "
                "SKIP_IN_FEATURE_EXTRACTION and must be skipped in feature extraction. ICA output "
                "for this recording is separately EXCLUDED (QC-03)."
            ),
        ),
        dict(
            issue_id="QC-07",
            title="Sampling-rate consistency (median-delta-t export artifact suggested 833 Hz)",
            scope="40 EEG recordings",
            evidence="EEG processed/quality_control/sampling_rate_verification.csv (2026-10-13): 40/40 MATCH; ACQ 1000.0 Hz each; mean/span estimator 999.9984-1000.0003 Hz; 6-significant-digit timestamp quantization explains the median bias",
            classification="RESOLVED_WITH_EVIDENCE",
            action_owner="none",
            interim_disposition="Fs = 1000 Hz verified per-file from .acq headers and cross-checked against .xlsx timestamps. Both estimators reported side by side in the verification CSV.",
        ),
        dict(
            issue_id="QC-08",
            title="Output path fork: historical 'processed\\eeg' vs actual 'EEG processed\\eeg'",
            scope="documentation + per-recording JSONs",
            evidence="E:\\REU_DATA\\processed does not exist (asserted at build); v3 notebook cell uses 'EEG processed/eeg'; per-recording preprocessing_report.json original wording preserved + annotated with v3_finalization block (reports_final_v3 pass)",
            classification="RESOLVED_WITH_EVIDENCE",
            action_owner="none",
            interim_disposition="No rename performed (risky, no benefit). Current notebooks point at the real folder; re-running the notebook writes only into 'EEG processed/eeg'. Historical JSON wording kept for traceability.",
        ),
        dict(
            issue_id="QC-09",
            title="Readiness disagreement: v3 PASS (6) vs audit PASS (2) on 4 meditation recordings",
            scope="P02/P05/P06/P08 meditation",
            evidence="audit_finalization_v1/eeg/status_disagreements_v1.csv (agrees_with_v3=False); cause: v3 auto-approved ICA by code rule, audit requires human sign-off",
            classification="REQUIRES_HUMAN_REVIEW",
            action_owner="Analysis lead / mentor (policy confirmation)",
            interim_disposition="Deliberate, documented disagreement. Audit (stricter) rule is in force: these recordings remain REVIEW_REQUIRED until QC-02 completes.",
        ),
        dict(
            issue_id="QC-10",
            title="figures_v3/ica empty - component maps only in figures_v2/ica",
            scope="30 component maps",
            evidence=f"build check: figures_v2/ica = {len(maps_v2)} PNGs, figures_v3/ica = {len(maps_v3)} PNGs (v3 run reused cached v2 fits, so no new maps were written)",
            classification="RESOLVED_WITH_EVIDENCE",
            action_owner="none",
            interim_disposition="Maps exist and are verified present; review workflow references figures_v2/ica (and byte-identical copies in ica_visual_review_bundle_v1).",
        ),
        dict(
            issue_id="QC-11",
            title="P07 meditation alpha-loss magnitude is method-sensitive",
            scope="1 EEG recording",
            evidence=f"beforeafter_evidence_v1/beforeafter_index_v1.csv: independent Welch recomputation gives {float(ba.loc[ba.recording_id=='P07_meditation','alpha_change_recomputed_pct'].iloc[0]):+.1f}% vs stored report {float(ba.loc[ba.recording_id=='P07_meditation','alpha_change_report_pct'].iloc[0]):+.1f}% (diff > 5 pp, only such case in 30); 29/30 within 5 pp",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="none (both methods agree the ICA output is unusable)",
            interim_disposition="Status (EXCLUDED) unchanged; the two PSD estimators disagree on magnitude for this recording (it also has a 99.8% variance collapse and the dataset's largest transient). Recorded for transparency.",
        ),
        dict(
            issue_id="QC-12",
            title="Assumed metadata: standard 10-20 montage (no digitised positions) and Fp-proxy EOG (no dedicated EOG channel)",
            scope="40 EEG recordings",
            evidence="acquisition_reference_note_v1.md; montage attached with on_missing='ignore' in the v3 pipeline",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Acquisition team (confirm cap layout)",
            interim_disposition="All topographic statements (ICA frontal weights etc.) rest on these assumptions. Recorded; not silently treated as measured facts.",
        ),
        dict(
            issue_id="QC-13",
            title="Three near-guard alpha losses (25-30%) awaiting visual confirmation",
            scope="P02 calm (28.6%), P06 maths (29.4%), P09 maths (25.2%)",
            evidence="packet_manifest_v2.csv near_guard_flag=YES; provisional_review_v2 preserved warnings; beforeafter_evidence_v1 now provides direct visual evidence for each",
            classification="REQUIRES_HUMAN_REVIEW",
            action_owner="Human reviewer (as part of QC-02)",
            interim_disposition="Flagged in the review table's signal_quality_review and alpha_loss_review fields; no threshold was moved.",
        ),
        dict(
            issue_id="QC-14",
            title="Speech: P05 low estimated SNR (13.8 dB)",
            scope="1 speech recording",
            evidence="speech_audit_quality_control_v1.csv (estimated_snr_db=13.8); noise reduction deliberately not applied",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Analysis lead",
            interim_disposition="REVIEW_REQUIRED; cleaned file valid; MFCC/energy features will inherit the noise floor.",
        ),
        dict(
            issue_id="QC-15",
            title="Speech: P09 / P10 large stereo level differences (+10.1 / +11.7 dB)",
            scope="2 speech recordings",
            evidence="speech_audit_quality_control_v1.csv level_diff_R_minus_L_dB; mono conversion verified r>=0.995 (mono_verification_v1.csv)",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Analysis lead (confirm lag-aligned mean is the right combination)",
            interim_disposition="Both channels preserved via lag-aligned mean; documented.",
        ),
        dict(
            issue_id="QC-16",
            title="Speech: P10 source clipping (0.003% samples, right channel)",
            scope="1 speech recording",
            evidence="speech_audit_quality_control_v1.csv source_clipping_pct; 0 clipped samples survive in cleaned mono file",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="none unless re-recording possible",
            interim_disposition="Repair would alter the signal; recorded as a source limitation.",
        ),
        dict(
            issue_id="QC-17",
            title="931 artifact windows (34 recordings) are register-only - nothing removed",
            scope="34 EEG recordings",
            evidence="artifact_log_v1.csv (all amplitude >200 uV, all SKIP_IN_FEATURE_EXTRACTION); recount in build_qc_summary_v2.py matches 931",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Feature-extraction stage (must honour the register)",
            interim_disposition="Policy accepted: flag and skip, never silently delete. Timing and events preserved.",
        ),
        dict(
            issue_id="QC-18",
            title="STRUCTURE.md baseline counts are stale (describe the 2026-10-10 layout)",
            scope="documentation",
            evidence="STRUCTURE.md says 500 files/4 notebooks; later passes added review_plan_v1, ica_visual_review_bundle_v1, component_evidence_v1, provisional_review_v1/v2, review_contact_sheets_v1, audit_finalization_v1, reports_final_v3, signoff_finalization_v2",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="none (left untouched deliberately - it is the baseline record)",
            interim_disposition="Treat STRUCTURE.md + INVENTORY_BASELINE.csv as the 2026-10-10 integrity anchor, not as the current inventory. Current state: signoff_finalization_v2/README.md.",
        ),
        dict(
            issue_id="QC-19",
            title="Duplicate review bundles at repo root ('ica_visual_review_bundle_v1 (2).zip', 'provisional_review_v2.zip')",
            scope="2 zip files",
            evidence="filesystem listing; unpacked folders exist alongside",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Project owner (optional cleanup - deletion not performed)",
            interim_disposition="Harmless duplicates of already-unpacked content; left in place because deleting is out of scope for a non-destructive pass.",
        ),
        dict(
            issue_id="QC-20",
            title="Filter chain re-verified on a subset only (8 of 40)",
            scope="40 EEG recordings",
            evidence="filter_verification_v1.csv: 8 tested recordings reproduce to <1e-9 V; 30 marked 'not re-tested (subset design)'",
            classification="DOCUMENTED_LIMITATION_OR_WAIVER",
            action_owner="Analysis lead",
            interim_disposition="Accepted design choice from the audit; identical filter parameters applied pipeline-wide in the v3 run.",
        ),
    ]

    df = pd.DataFrame(issues)
    assert set(df["classification"]) <= set(CLASSES)
    assert df["issue_id"].is_unique

    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    order = {c: i for i, c in enumerate(CLASSES)}
    dfs = df.sort_values(["classification", "issue_id"], key=lambda s: s.map(order) if s.name == "classification" else s)
    lines = [
        "# QC issue classification (v2) - evidence-based",
        "",
        "Generated by `signoff_finalization_v2/scripts/build_qc_issue_classification_v2.py`.",
        "Source facts asserted at build time (see script). No issue was closed without evidence;",
        "nothing was auto-approved.",
        "",
        f"Counts: " + ", ".join(f"{c} {int((df['classification']==c).sum())}" for c in CLASSES) + f" (total {len(df)})",
        "",
        "| ID | Issue | Class | Owner | Interim disposition |",
        "|---|---|---|---|---|",
    ]
    for _, r in dfs.iterrows():
        lines.append(f"| {r['issue_id']} | {r['title']} | {r['classification']} | {r['action_owner']} | {r['interim_disposition'][:160]}{'...' if len(r['interim_disposition'])>160 else ''} |")
    lines += [
        "",
        "Full evidence paths are in the CSV (`evidence` column).",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {OUT_CSV} ({len(df)} issues)")
    print(f"WROTE {OUT_MD}")
    print("classification counts:", df["classification"].value_counts().to_dict())


if __name__ == "__main__":
    main()
