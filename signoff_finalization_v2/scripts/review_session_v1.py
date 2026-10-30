r"""CLI twin of EEG_ICA_Signoff_Review_v1.ipynb for guided review sessions.

Mirrors the notebook's guarded record_decision()/validate_signoff_table() logic
exactly, with one extra safety: the excluded-5 reinstatement rule is enforced at
record time (the notebook enforces it at gate time), so the table can never hold
a state that would fail the validation gate.

Usage:
  py review_session_v1.py status
  py review_session_v1.py show <recording_id>
  py review_session_v1.py record <recording_id> <APPROVED|REJECTED|NEEDS_REVIEW>
                                 --reviewer NAME --date YYYY-MM-DD [--comment TEXT]

Reads:  ica_review_context_v1.csv (metrics), ica_review_table_v1.csv (state)
Writes: ica_review_table_v1.csv (one row) + append-only ica_signoff_decisions_log_v1.csv
Never touches ICA outputs, figures, or any other file.
"""
import argparse
import sys
from datetime import date as _date
from pathlib import Path

import pandas as pd

SIGNOFF_DIR = Path(r"E:\REU_DATA\signoff_finalization_v2")
REVIEW_TABLE = SIGNOFF_DIR / "ica_review_table_v1.csv"
CONTEXT = SIGNOFF_DIR / "ica_review_context_v1.csv"
DECISION_LOG = SIGNOFF_DIR / "ica_signoff_decisions_log_v1.csv"

REQUIRED_COLUMNS = ["participant_id", "condition", "recording_id", "components_removed",
                    "artifact_evidence", "signal_quality_review", "alpha_loss_review",
                    "decision", "reviewer", "review_date", "comments"]
ALLOWED_DECISIONS = {"APPROVED", "REJECTED", "NEEDS_REVIEW"}
EXCLUDED5 = {"P01_meditation", "P04_meditation", "P07_meditation", "P09_calm", "P09_meditation"}


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    t = pd.read_csv(REVIEW_TABLE, keep_default_na=False)
    c = pd.read_csv(CONTEXT, keep_default_na=False)
    assert list(t.columns) == REQUIRED_COLUMNS, f"schema changed: {list(t.columns)}"
    assert len(t) == 30 and t["recording_id"].is_unique, "expected 30 unique recordings"
    assert set(t["decision"]) <= ALLOWED_DECISIONS, "unknown decision value in table"
    return t, c


def cmd_status() -> None:
    t, _ = load()
    counts = t["decision"].value_counts().to_dict()
    pending = t.loc[t["decision"] == "NEEDS_REVIEW", "recording_id"].tolist()
    print(f"decision counts: {counts}")
    print(f"pending ({len(pending)}): {', '.join(pending) if pending else '-'}")
    n_app = int((t["decision"] == "APPROVED").sum())
    print(f"feature inputs in force: ICA fif for {n_app} APPROVED recording(s); "
          f"cleaned pre-ICA fif for the other {40 - n_app} EEG recordings")


def cmd_show(rid: str) -> None:
    t, c = load()
    row = t[t["recording_id"] == rid]
    assert len(row) == 1, f"unknown recording_id: {rid}"
    row, cx = row.iloc[0], c[c["recording_id"] == rid].iloc[0]

    print("=" * 78)
    print(f"{rid}  components removed: {row['components_removed']}  decision: {row['decision']}")
    print("-" * 78)
    print(f"prior recommendation : {cx['prior_recommendation']}")
    print(f"audit disposition    : {cx['audit_disposition']}   near-guard: {cx['near_guard_flag']}")
    print(f"eog_corr_max         : {cx['eog_corr_max']}  (rule >= 0.40)")
    print(f"frontal_weight       : {cx['frontal_weight']}  (rule >= 0.35)")
    print(f"removed_hf_fraction  : {cx['removed_hf_fraction']}")
    print(f"alpha_loss_pct       : {cx['alpha_loss_pct']}  (guard 30%)   "
          f"variance_reduction_pct: {cx['variance_reduction_pct']}")
    print(f"guards_all_pass      : {cx['guards_all_pass']}   "
          f"artifact windows: {cx['artifact_windows_n']} / {cx['artifact_windows_s']} s")
    print(f"flagged channels     : {cx['flagged_channels']} (KEEP, none interpolated)")
    print(f"prior reason         : {cx['prior_reason']}")
    print("-" * 78)
    for k in ("evidence_component_map", "evidence_timecourse", "evidence_spectrum",
              "evidence_beforeafter"):
        print(f"{k}: {cx[k]}")
    print("=" * 78)


def record(rid: str, decision: str, reviewer: str, review_date: str, comment: str) -> None:
    assert decision in ALLOWED_DECISIONS, f"decision must be one of {sorted(ALLOWED_DECISIONS)}"
    if decision in ("APPROVED", "REJECTED"):
        assert reviewer.strip(), "APPROVED/REJECTED require a non-empty reviewer name"
        assert review_date.strip(), "APPROVED/REJECTED require review_date (YYYY-MM-DD)"
        _date.fromisoformat(review_date)  # raises if malformed
    if rid in EXCLUDED5 and decision == "APPROVED":
        assert "evidence" in comment.lower(), (
            "excluded recording can only be APPROVED with explicit reinstatement "
            "evidence in the comment (word 'evidence')"
        )

    t = pd.read_csv(REVIEW_TABLE, keep_default_na=False)
    assert list(t.columns) == REQUIRED_COLUMNS
    idx = t.index[t["recording_id"] == rid]
    assert len(idx) == 1, f"unknown recording_id: {rid}"
    i = idx[0]
    prior = t.at[i, "decision"]
    t.at[i, "decision"] = decision
    t.at[i, "reviewer"] = reviewer.strip()
    t.at[i, "review_date"] = review_date.strip()
    if comment.strip():
        t.at[i, "comments"] = (str(t.at[i, "comments"]) + " | REVIEWER: " + comment.strip()).strip(" |")
    t.to_csv(REVIEW_TABLE, index=False, encoding="utf-8")

    log_row = pd.DataFrame([{
        "recording_id": rid, "prior_decision": prior, "decision": decision,
        "reviewer": reviewer.strip(), "review_date": review_date.strip(),
        "comments_add": comment.strip(),
    }])
    if DECISION_LOG.exists():
        log_row.to_csv(DECISION_LOG, mode="a", header=False, index=False, encoding="utf-8")
    else:
        log_row.to_csv(DECISION_LOG, index=False, encoding="utf-8")
    print(f"RECORDED {rid}: {prior} -> {decision} (reviewer={reviewer!r}, date={review_date})")

    validate()


def validate() -> None:
    t, ctx = load()
    decided = t[t["decision"].isin(["APPROVED", "REJECTED"])]
    missing = decided[(decided["reviewer"].str.strip() == "") | (decided["review_date"].str.strip() == "")]
    assert len(missing) == 0, f"anonymous decisions: {missing['recording_id'].tolist()}"
    for _, r in t[t["recording_id"].isin(EXCLUDED5) & (t["decision"] == "APPROVED")].iterrows():
        assert "evidence" in str(r["comments"]).lower(), \
            f"{r['recording_id']}: approved without reinstatement evidence"
    for _, r in decided.iterrows():
        c = ctx[ctx["recording_id"] == r["recording_id"]].iloc[0]
        for path in (c["evidence_component_map"], c["evidence_beforeafter"]):
            if path not in ("NOT AVAILABLE", "PENDING", ""):
                assert Path(path).exists(), f"missing evidence: {path}"
    counts = t["decision"].value_counts().to_dict()
    pending = t.loc[t["decision"] == "NEEDS_REVIEW", "recording_id"].tolist()
    print(f"VALIDATION PASSED  counts={counts}")
    print(f"still pending ({len(pending)}): {', '.join(pending) if pending else '-'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sp = sub.add_parser("show"); sp.add_argument("recording_id")
    rp = sub.add_parser("record")
    rp.add_argument("recording_id")
    rp.add_argument("decision")
    rp.add_argument("--reviewer", default="")
    rp.add_argument("--date", dest="review_date", default="")
    rp.add_argument("--comment", default="")
    args = ap.parse_args()

    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "show":
        cmd_show(args.recording_id)
    else:
        record(args.recording_id, args.decision, args.reviewer, args.review_date, args.comment)


if __name__ == "__main__":
    sys.exit(main())
