"""Validation suite for the signoff_finalization_v2 pass (Phase D).

Runs non-destructive checks only:
  V1  builder scripts compile
  V2  review table schema + vocabulary + all-pending integrity (real table)
  V3  review table <-> packet manifest <-> ica_audit id/disposition agreement
  V4  QC summary: 50 rows, feature-input files exist on disk, recount = 931
  V5  before/after evidence: 30 figures + index cross-checks
  V6  notebook integrity: v3 hash unchanged; v4 = banner + identical 90 cells + V10
  V7  guard tests of the review-notebook helpers on a TEMP COPY (real table untouched)
  V8  hash-snapshot diff: only signoff_finalization_v2\\ and the 2 new notebooks changed

Writes: validation_results_v2.csv (+ stdout). Refuses to overwrite.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(r"E:\REU_DATA")
SIGNOFF = ROOT / "signoff_finalization_v2"
OUT_CSV = SIGNOFF / "validation_results_v2.csv"
BEFORE = Path(r"C:\Users\anush\AppData\Local\Temp\opencode\reu_audit\hashes_before.json")
AFTER = Path(r"C:\Users\anush\AppData\Local\Temp\opencode\reu_audit\hashes_after.json")

REQUIRED_COLUMNS = ["participant_id", "condition", "recording_id", "components_removed",
                    "artifact_evidence", "signal_quality_review", "alpha_loss_review",
                    "decision", "reviewer", "review_date", "comments"]
ALLOWED = {"APPROVED", "REJECTED", "NEEDS_REVIEW"}

results: list[dict] = []


def check(vid: str, name: str, fn) -> None:
    try:
        detail = fn()
        results.append({"id": vid, "check": name, "status": "PASS",
                        "detail": str(detail) if detail is not None else ""})
        print(f"[PASS] {vid} {name}" + (f" — {detail}" if detail else ""))
    except Exception as exc:  # noqa: BLE001 - report any failure, keep going
        results.append({"id": vid, "check": name, "status": "FAIL", "detail": repr(exc)})
        print(f"[FAIL] {vid} {name} — {exc!r}")


def v1_scripts_compile() -> str:
    scripts = sorted((SIGNOFF / "scripts").glob("*.py"))
    assert len(scripts) >= 6, f"only {len(scripts)} scripts"
    for s in scripts:
        compile(s.read_text(encoding="utf-8"), str(s), "exec")
    return f"{len(scripts)} scripts compile"


def v2_review_table_integrity() -> str:
    t = pd.read_csv(SIGNOFF / "ica_review_table_v1.csv", keep_default_na=False)
    assert list(t.columns) == REQUIRED_COLUMNS, list(t.columns)
    assert len(t) == 30 and t["recording_id"].is_unique
    assert set(t["decision"]) <= ALLOWED
    assert (t["decision"] == "NEEDS_REVIEW").all(), "a decision was auto-filled"
    assert (t["reviewer"].str.strip() == "").all() and (t["review_date"].str.strip() == "").all()
    assert t["artifact_evidence"].str.len().gt(0).all()
    assert t["signal_quality_review"].str.len().gt(0).all()
    assert t["alpha_loss_review"].str.len().gt(0).all()
    return "30 rows, all NEEDS_REVIEW, reviewer/date empty, evidence fields populated"


def v3_cross_source_agreement() -> str:
    t = pd.read_csv(SIGNOFF / "ica_review_table_v1.csv", keep_default_na=False)
    packet = pd.read_csv(ROOT / "EEG processed" / "quality_control" / "ica_signoff_packet_v2" / "packet_manifest_v2.csv")
    audit = pd.read_csv(ROOT / "audit_finalization_v1" / "eeg" / "ica_audit_v1.csv")
    assert set(t["recording_id"]) == set(f"{r.participant}_{r.condition}" for r in packet.itertuples())
    excl_packet = {f"{r.participant}_{r.condition}" for r in packet.itertuples() if r.audit_disposition == "EXCLUDED"}
    excl_audit = {f"{r.participant}_{r.condition}" for r in audit.itertuples() if r.audit_ica_disposition == "EXCLUDED"}
    assert excl_packet == excl_audit == {"P01_meditation", "P04_meditation", "P07_meditation", "P09_calm", "P09_meditation"}
    return f"30 ids match packet; excluded-5 identical across packet and audit: {sorted(excl_packet)}"


def v4_qc_summary() -> str:
    qc = pd.read_csv(SIGNOFF / "eeg_qc_summary_v2.csv", keep_default_na=False)
    assert len(qc) == 50 and (qc["modality"] == "eeg").sum() == 40 and (qc["modality"] == "speech").sum() == 10
    missing = [f for f in qc["feature_input_file"] if f and not Path(f).exists()]
    assert not missing, f"missing feature inputs: {missing[:3]}"
    eeg = qc[qc["modality"] == "eeg"]
    assert int(pd.to_numeric(eeg["artifact_windows_audit_recount"]).sum()) == 931
    assert eeg["sampling_rate_verified"].eq("MATCH").all()
    assert (eeg["ica_formal_signoff_decision"] == "NEEDS_REVIEW").sum() == 30
    assert (eeg["ica_formal_signoff_decision"] == "NOT_APPLICABLE_NO_ICA").sum() == 10
    return "50 rows; 50/50 feature inputs exist; recount 931; 30 pending + 10 not-applicable"


def v5_beforeafter() -> str:
    figs = sorted((SIGNOFF / "beforeafter_evidence_v1").glob("*_beforeafter.png"))
    idx = pd.read_csv(SIGNOFF / "beforeafter_evidence_v1" / "beforeafter_index_v1.csv")
    assert len(figs) == 30 and len(idx) == 30
    assert (idx["status"] == "BUILT").all()
    assert idx["figure"].map(lambda p: Path(p).exists()).all()
    assert (idx["variance_crosscheck"] == "OK").sum() == 30
    ok = int((idx["alpha_crosscheck"] == "OK_METHOD_TOLERANT").sum())
    assert ok == 29, f"alpha crosscheck OK count {ok}"
    outlier = idx[idx["alpha_crosscheck"] != "OK_METHOD_TOLERANT"]["recording_id"].tolist()
    assert outlier == ["P07_meditation"], outlier
    return "30 figures; variance 30/30 OK; alpha 29/30 within 5 pp; 1 documented outlier (P07_meditation)"


def v6_notebook_integrity() -> str:
    v3 = ROOT / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb"
    v4 = ROOT / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb"
    before = {r["path"]: r["sha256"] for r in json.loads(BEFORE.read_text())["files"]}
    assert before["notebooks/EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb"] == hashlib.sha256(v3.read_bytes()).hexdigest(), "v3 changed!"
    nb3 = json.loads(v3.read_text(encoding="utf-8"))
    nb4 = json.loads(v4.read_text(encoding="utf-8"))
    assert len(nb3["cells"]) == 90 and len(nb4["cells"]) == 94
    for i in range(90):
        assert nb4["cells"][i + 1] == nb3["cells"][i], f"cell {i} drifted in v4"
    assert nb4["cells"][0]["cell_type"] == "markdown" and "v4" in "".join(nb4["cells"][0]["source"])
    v10 = "".join(nb4["cells"][92]["source"])
    assert "V10" in v10 and nb4["cells"][92]["outputs"], "V10 output not embedded"
    return "v3 hash unchanged; v4 = banner + 90 identical cells + V10 (output embedded)"


def v7_guard_tests() -> str:
    review_nb = json.loads((ROOT / "notebooks" / "EEG_ICA_Signoff_Review_v1.ipynb").read_text(encoding="utf-8"))
    code_cells = ["".join(c["source"]) for c in review_nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) == 4
    load_src, _show_src, record_src, validate_src = code_cells

    tmp = Path(tempfile.mkdtemp(prefix="signoff_guard_"))
    try:
        tmp_table = tmp / "ica_review_table_v1.csv"
        tmp_log = tmp / "log.csv"
        shutil.copy(SIGNOFF / "ica_review_table_v1.csv", tmp_table)
        real_hash_before = hashlib.sha256((SIGNOFF / "ica_review_table_v1.csv").read_bytes()).hexdigest()

        ns: dict = {}
        exec(compile(load_src, "load", "exec"), ns)
        exec(compile(record_src, "record", "exec"), ns)
        exec(compile(validate_src, "validate", "exec"), ns)

        rd = ns["record_decision"]
        # 1. invalid decision rejected
        try:
            rd("P02_calm", "MAYBE", "X", "2026-10-13", table_path=tmp_table, log_path=tmp_log)
            raise AssertionError("invalid decision accepted")
        except AssertionError as e:
            assert "decision must be one of" in str(e)
        # 2. APPROVED without reviewer rejected
        try:
            rd("P02_calm", "APPROVED", "", "2026-10-13", table_path=tmp_table, log_path=tmp_log)
            raise AssertionError("anonymous approval accepted")
        except AssertionError as e:
            assert "reviewer" in str(e).lower()
        # 3. bad date rejected
        try:
            rd("P02_calm", "APPROVED", "Test Reviewer", "13-10-2026", table_path=tmp_table, log_path=tmp_log)
            raise AssertionError("malformed date accepted")
        except ValueError:
            pass
        # 4. excluded row approved WITHOUT reinstatement evidence -> validation must fail
        rd("P09_calm", "APPROVED", "Test Reviewer", "2026-10-13", table_path=tmp_table, log_path=tmp_log)
        try:
            ns["validate_signoff_table"](table_path=tmp_table)
            raise AssertionError("exclusion bypass accepted")
        except AssertionError as e:
            assert "reinstatement evidence" in str(e)
        # 5. excluded row approved WITH evidence comment -> validation passes; still 29 pending
        rd("P09_calm", "REJECTED", "Test Reviewer", "2026-10-13",
           comments_add="exclusion confirmed with evidence: alpha loss 40.2% > guard",
           table_path=tmp_table, log_path=tmp_log)
        out = ns["validate_signoff_table"](table_path=tmp_table)
        assert out["counts"].get("REJECTED") == 1 and len(out["pending"]) == 29
        # 6. log has 2 appended rows; real table untouched
        log = pd.read_csv(tmp_log)
        assert len(log) == 2
        real_hash_after = hashlib.sha256((SIGNOFF / "ica_review_table_v1.csv").read_bytes()).hexdigest()
        assert real_hash_before == real_hash_after, "real review table was modified by guard tests!"
        return "6 guard scenarios pass; real table hash unchanged during tests"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def v8_hash_diff() -> str:
    before = {r["path"]: r["sha256"] for r in json.loads(BEFORE.read_text())["files"]}
    after = {r["path"]: r["sha256"] for r in json.loads(AFTER.read_text())["files"]}
    changed = [p for p in before if p in after and before[p] != after[p]]
    removed = [p for p in before if p not in after]
    added = sorted(p for p in after if p not in before)
    allowed_prefix = "signoff_finalization_v2/"
    allowed_new = {"notebooks/EEG_ICA_Signoff_Review_v1.ipynb",
                   "notebooks/EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb"}
    bad_changed = [p for p in changed]
    bad_added = [p for p in added if not p.startswith(allowed_prefix) and p not in allowed_new]
    assert not bad_changed, f"pre-existing files changed: {bad_changed}"
    assert not removed, f"files removed: {removed}"
    assert not bad_added, f"unexpected new files outside the pass: {bad_added}"
    return f"0 pre-existing files changed; {len(added)} new files, all inside signoff_finalization_v2/ or the 2 new notebooks"


def main() -> None:
    if OUT_CSV.exists():
        sys.exit(f"REFUSING TO OVERWRITE {OUT_CSV}")
    check("V1", "builder scripts compile", v1_scripts_compile)
    check("V2", "review table schema/vocabulary/all-pending", v2_review_table_integrity)
    check("V3", "review table vs packet vs audit agreement", v3_cross_source_agreement)
    check("V4", "QC summary rows, feature inputs, recounts", v4_qc_summary)
    check("V5", "before/after evidence completeness + cross-checks", v5_beforeafter)
    check("V6", "notebook integrity (v3 frozen, v4 exact superset)", v6_notebook_integrity)
    check("V7", "review-notebook guard tests (temp copy)", v7_guard_tests)
    check("V8", "hash-snapshot diff (no protected file changed)", v8_hash_diff)
    df = pd.DataFrame(results)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"\nWROTE {OUT_CSV}")
    print("SUMMARY:", df["status"].value_counts().to_dict())
    if (df["status"] == "FAIL").any():
        sys.exit(1)


if __name__ == "__main__":
    main()
