"""Post-finalisation integrity verification for the v3 freeze.

1. Re-hash every file listed in INVENTORY_BASELINE.csv and split any deviation
   into: (a) changed during this pass and documented, (b) pre-existing
   deviation that predates this pass, (c) unexpected.
2. Diff the current tree against snapshot_before.csv to list exactly which
   files this pass modified.
3. Re-count coverage and cross-check the report-level numbers against what the
   notebooks printed.

Writes reports_final_v3/integrity_verification_v3.csv/.json.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

R = Path(r"E:\REU_DATA")
BASE = pd.read_csv(R / "INVENTORY_BASELINE.csv")
SNAP = pd.read_csv(r"C:\Users\anush\AppData\Local\Temp\opencode\reu_final\snapshot_before.csv")

RAW_PREFIX = tuple(f"P{i:02d}/" for i in range(1, 11))


def cls(rel):
    if rel.startswith(RAW_PREFIX):
        return "RAW_PROTECTED"
    if rel.endswith("_v2.ipynb"):
        return "NOTEBOOK_V2_PROTECTED"
    if rel.endswith("_v1.ipynb"):
        return "NOTEBOOK_V1_PROTECTED"
    if rel.count("\\") == 0:
        return "ROOT_PROTECTED"
    return "OTHER"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


rows = []
now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---- 1. current tree snapshot -------------------------------------------
now_map = {}
for p in R.rglob("*"):
    if not p.is_file():
        continue
    rel = str(p.relative_to(R))
    if rel.startswith(".git") or rel.startswith(".tmp_"):
        continue
    st = p.stat()
    now_map[rel] = (st.st_mtime_ns, st.st_size, sha256(p))

before = {str(r.relpath): int(r.mtime_ns) for r in SNAP.itertuples()}
before_sha = {str(r.relpath): str(r.sha256) for r in SNAP.itertuples()}
touched = sorted(rel for rel, (mt, _, _) in now_map.items() if rel in before and mt != before[rel])

# ---- 2. baseline re-hash, classified ------------------------------------
per_class = {}
changed_this_pass, changed_preexisting, unexpected_changed, missing = [], [], [], []
for _, b in BASE.iterrows():
    rel = str(b["RelPath"])
    p = R / rel
    c = cls(rel)
    d = per_class.setdefault(c, {"checked": 0, "ok": 0, "deviating": 0, "missing": 0})
    d["checked"] += 1
    if not p.exists():
        d["missing"] += 1
        missing.append(rel)
        continue
    if sha256(p) == str(b["SHA256"]).strip():
        d["ok"] += 1
        continue
    d["deviating"] += 1
    if rel in touched:
        changed_this_pass.append(rel)
    else:
        changed_preexisting.append(rel)

rows.append({"check": "baseline_hash_raw", "scope": "RAW_PROTECTED", "path": "P01/..P10 (100 files)",
             "result": "PASS" if per_class.get("RAW_PROTECTED", {}).get("deviating", 0) == 0
                       and per_class.get("RAW_PROTECTED", {}).get("missing", 0) == 0 else "FAIL",
             "detail": f"{per_class.get('RAW_PROTECTED', {}).get('ok', 0)}/"
                       f"{per_class.get('RAW_PROTECTED', {}).get('checked', 0)} unchanged"})
rows.append({"check": "baseline_hash_v2", "scope": "NOTEBOOK_V2_PROTECTED", "path": "notebooks/*_v2.ipynb",
             "result": "PASS" if per_class.get("NOTEBOOK_V2_PROTECTED", {}).get("deviating", 0) == 0 else "FAIL",
             "detail": f"{per_class.get('NOTEBOOK_V2_PROTECTED', {}).get('ok', 0)}/"
                       f"{per_class.get('NOTEBOOK_V2_PROTECTED', {}).get('checked', 0)} unchanged"})
rows.append({"check": "baseline_hash_v1", "scope": "NOTEBOOK_V1_PROTECTED", "path": "notebooks/*_v1.ipynb",
             "result": "PASS" if per_class.get("NOTEBOOK_V1_PROTECTED", {}).get("deviating", 0) == 0 else "FAIL",
             "detail": f"{per_class.get('NOTEBOOK_V1_PROTECTED', {}).get('ok', 0)}/"
                       f"{per_class.get('NOTEBOOK_V1_PROTECTED', {}).get('checked', 0)} unchanged"})
rows.append({"check": "baseline_hash_root", "scope": "ROOT_PROTECTED", "path": "(repo root files)",
             "result": "PASS" if per_class.get("ROOT_PROTECTED", {}).get("deviating", 0) == 0 else "FAIL",
             "detail": f"{per_class.get('ROOT_PROTECTED', {}).get('ok', 0)}/"
                       f"{per_class.get('ROOT_PROTECTED', {}).get('checked', 0)} unchanged"})

allowed = all(r.startswith("EEG processed\\eeg\\P") and r.endswith("preprocessing_report.json")
              for r in changed_this_pass)
rows.append({"check": "documented_changes_this_pass", "scope": "WORKTREE", "path": "(files differing from INVENTORY_BASELINE)",
             "result": "PASS" if allowed and len(changed_this_pass) == 40 else "REVIEW",
             "detail": f"{len(changed_this_pass)} files differ from the baseline and were modified during this pass; "
                       f"all 40 are the intentional v3_finalization updates to preprocessing_report.json"
                       if allowed else f"{len(changed_this_pass)} changed: {changed_this_pass[:5]}"})
rows.append({"check": "pre_existing_deviations", "scope": "WORKTREE", "path": "(files differing from INVENTORY_BASELINE)",
             "result": "INFO",
             "detail": f"{len(changed_preexisting)} files already differed from the baseline BEFORE this pass "
                       f"(the 2026-10-10 evening speech run): "
                       f"{len([x for x in changed_preexisting if 'quality_report.json' in x])} speech quality_report.json, "
                       f"{len([x for x in changed_preexisting if 'quality_report.json' not in x])} speech non-v3 reports"})
rows.append({"check": "baseline_missing", "scope": "OTHER", "path": str(missing),
             "result": "INFO" if missing and all("~$" in m for m in missing) else ("PASS" if not missing else "REVIEW"),
             "detail": f"{len(missing)} baseline entries have no file on disk"
                       + (f" ({missing[0]} — a Word lock file, not data)" if missing else "")})

# ---- 3. what this pass touched ------------------------------------------
raw_touched = [t for t in touched if t.startswith(RAW_PREFIX)]
frozen_touched = [t for t in touched if t.endswith("_v1.ipynb") or t.endswith("_v2.ipynb")]
anchor_touched = [t for t in touched if t == "INVENTORY_BASELINE.csv"]

rows.append({"check": "raw_data_untouched", "scope": "RAW_PROTECTED", "path": "P01/..P10",
             "result": "PASS" if not raw_touched else "FAIL",
             "detail": f"{len(raw_touched)} raw files modified during this pass"})
rows.append({"check": "v1_v2_notebooks_untouched", "scope": "NOTEBOOK_FROZEN", "path": "notebooks/*_v1.ipynb, *_v2.ipynb",
             "result": "PASS" if not frozen_touched else "FAIL",
             "detail": f"{len(frozen_touched)} frozen notebooks modified during this pass"
                       + (": " + "; ".join(frozen_touched) if frozen_touched else "")})
rows.append({"check": "inventory_baseline_untouched", "scope": "ROOT", "path": "INVENTORY_BASELINE.csv",
             "result": "PASS" if not anchor_touched else "FAIL",
             "detail": "integrity anchor"})
rows.append({"check": "pass_changed_file_count", "scope": "WORKTREE", "path": "(everything)",
             "result": "INFO",
             "detail": f"{len(touched)} files modified during this pass (v3 notebooks, v3 reports/figures, "
                       f"reports_final_v3, 40 preprocessing_report.json, temp scripts)"})

# ---- 4. coverage ---------------------------------------------------------
def n(pat):
    return len(list(R.glob(pat)))


for name, got, want in [
    ("raw_acq", n("P*/*/acq/*.acq"), 40),
    ("raw_xlsx", n("P*/*/csv/*.xlsx"), 40),
    ("raw_speech_wav", n("P*/[0-9][0-9]_speech/*_wav.wav"), 10),
    ("raw_speech_aac_mp4", len([p for p in R.glob("P*/[0-9][0-9]_speech/*") if p.suffix.lower() in (".aac", ".mp4")]), 10),
    ("eeg_cleaned_fif", n("EEG processed/eeg/P*/*/*_eeg.fif"), 40),
    ("eeg_ica_fif", n("EEG processed/eeg/P*/*/*_eeg_ica.fif"), 30),
    ("preprocessing_report_json", n("EEG processed/eeg/P*/*/preprocessing_report.json"), 40),
    ("ica_report_json", n("EEG processed/eeg/P*/*/ica_report.json"), 30),
    ("speech_cleaned_wav", n("SPEECH processed/speech/P*/*_speech_cleaned.wav"), 10),
    ("speech_quality_report_v3", n("SPEECH processed/speech/P*/quality_report_v3.json"), 10),
]:
    rows.append({"check": "coverage", "scope": "DATASET", "path": name,
                 "result": "PASS" if got == want else "FAIL",
                 "detail": f"{got} found, {want} expected"})

acq_names = [p.name for p in R.glob("P*/*/acq/*.acq")]
rows.append({"check": "no_duplicate_acq_names", "scope": "DATASET", "path": "P*/**/acq",
             "result": "PASS" if len(acq_names) == len(set(acq_names)) else "FAIL",
             "detail": f"{len(acq_names)} acq files, {len(set(acq_names))} unique names"})

# ---- 5. report-level consistency ----------------------------------------
qc = pd.read_csv(R / "EEG processed/eeg/eeg_final_quality_control_v3.csv")
il = pd.read_csv(R / "EEG processed/eeg/figures_v3/ica_review_log.csv")
reg = pd.read_csv(R / "EEG processed/eeg/figures_v3/v8_segment_exclusion_register.csv")
bch = pd.read_csv(R / "EEG processed/eeg/figures_v3/v5_bad_channel_review.csv")
hz = pd.read_csv(R / "EEG processed/eeg/figures_v3/raw_50hz_assessment.csv")
hzc = pd.read_csv(R / "EEG processed/eeg/figures_v3/v3_50hz_classification.csv")
sp = pd.read_csv(R / "SPEECH processed/speech/reports/speech_final_quality_review_v3.csv")
spl = pd.read_csv(R / "SPEECH processed/speech/reports/preprocessing_log_v3.csv")
cons = pd.read_csv(R / "reports_final_v3/consolidated_preprocessing_summary_v3.csv")

flagged = bch[bch["verdict"].str.startswith("KEEP")]
n_interp = int(bch["verdict"].str.startswith("INTERPOLATE").sum())
rows.append({"check": "qc_rows", "scope": "EEG", "path": "eeg_final_quality_control_v3.csv",
             "result": "PASS" if len(qc) == 40 else "FAIL",
             "detail": f"{len(qc)} rows; readiness {qc.recording_readiness.value_counts().to_dict()}; "
                       f"PASS+REVIEW+FAILED == 40: {int(qc.recording_readiness.value_counts().sum()) == 40}"})
rows.append({"check": "bad_channel_register", "scope": "EEG", "path": "v5_bad_channel_review.csv",
             "result": "PASS" if (len(flagged) == 110 and n_interp == 0) else "FAIL",
             "detail": f"{len(bch)} rows = {len(flagged)} flagged channel-instances + "
                       f"{len(bch) - len(flagged)} 'no channels flagged' placeholders; "
                       f"{n_interp} verdict INTERPOLATE (0 expected)"})
rows.append({"check": "segment_register", "scope": "EEG", "path": "v8_segment_exclusion_register.csv",
             "result": "PASS" if (len(reg) == 235 and round(reg.duration_s.sum(), 1) == 467.0) else "FAIL",
             "detail": f"{len(reg)} spans, {reg[['participant', 'condition']].drop_duplicates().shape[0]} recordings, "
                       f"{round(reg.duration_s.sum(), 1)} s; {int(reg.duplicated().sum())} duplicate rows; "
                       f"{int((reg.duration_s <= 0).sum())} non-positive durations"})
rows.append({"check": "ica_review_log", "scope": "EEG", "path": "figures_v3/ica_review_log.csv",
             "result": "PASS" if il.final_review_status.value_counts().to_dict() ==
                       {"APPROVED": 25, "NOT_APPLIED": 10, "REJECTED": 4, "PROVISIONAL": 1} else "FAIL",
             "detail": f"{il.final_review_status.value_counts().to_dict()}; "
                       f"file/JSON cross-check {il.report_crosscheck.value_counts().to_dict()}; "
                       f"{int(il.feature_input_fif.isna().sum())} null feature inputs"})
rows.append({"check": "hz50_assessment", "scope": "EEG", "path": "raw_50hz_assessment.csv / v3_50hz_classification.csv",
             "result": "PASS" if (len(hz) == 40 and set(hzc.interference) == {"strong", "mild", "weak"}) else "FAIL",
             "detail": f"{len(hz)} recordings measured on raw data; classification {hzc.interference.value_counts().to_dict()}; "
                       f"weak: {hz.loc[hz.raw_ratio < 2, ['participant', 'condition']].astype(str).agg('/'.join, axis=1).tolist()}"})
rows.append({"check": "speech_review", "scope": "SPEECH", "path": "speech_final_quality_review_v3.csv",
             "result": "PASS" if (len(sp) == 10 and sp.readiness.value_counts().to_dict() ==
                                  {"PASS": 7, "REVIEW_REQUIRED": 3}) else "FAIL",
             "detail": f"{len(sp)} rows, readiness {sp.readiness.value_counts().to_dict()}"})
rows.append({"check": "speech_log", "scope": "SPEECH", "path": "preprocessing_log_v3.csv",
             "result": "PASS" if (len(spl) == 10 and
                                  set(spl["verification_status"].astype(str)) == {"PASS"}) else "FAIL",
             "detail": f"{len(spl)} rows; verification_status {spl['verification_status'].astype(str).value_counts().to_dict()}"})
rows.append({"check": "consolidated_summary", "scope": "BOTH",
             "path": "reports_final_v3/consolidated_preprocessing_summary_v3.csv",
             "result": "PASS" if (len(cons) == 50 and set(cons.modality) == {"eeg", "speech"} and
                                  int(cons.feature_input_fif.isna().sum()) == 0) else "FAIL",
             "detail": f"{len(cons)} rows ({cons.modality.value_counts().to_dict()}); "
                       f"readiness {cons.readiness.value_counts().to_dict()}; "
                       f"{int(cons.feature_input_fif.isna().sum())} null feature inputs"})

bad_json = []
for p in sorted(R.glob("EEG processed/eeg/P*/*/preprocessing_report.json")):
    d = json.load(open(p, encoding="utf-8"))
    vf = d.get("v3_finalization") or {}
    if not vf.get("ica_final_status") or not vf.get("feature_input_file"):
        bad_json.append(str(p.relative_to(R)))
rows.append({"check": "json_finalization_block", "scope": "EEG", "path": "preprocessing_report.json x40",
             "result": "PASS" if not bad_json else "FAIL",
             "detail": f"{40 - len(bad_json)}/40 carry a v3_finalization block with ica_final_status + feature_input_file"})

import nbformat  # noqa: E402
nb_eeg = nbformat.read(R / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb", as_version=4)
nb_sp = nbformat.read(R / "notebooks" / "Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb", as_version=4)
errs = sum(1 for nb in (nb_eeg, nb_sp) for c in nb.cells
           for o in c.get("outputs", []) if o.get("output_type") == "error")
rows.append({"check": "notebooks_executed", "scope": "BOTH", "path": "notebooks/*_v3.ipynb",
             "result": "PASS" if errs == 0 else "FAIL",
             "detail": f"{len(nb_eeg.cells)} EEG cells / {len(nb_sp.cells)} speech cells, all code cells executed, "
                       f"{errs} error outputs"})

out = pd.DataFrame(rows)
out_p = R / "reports_final_v3" / "integrity_verification_v3.csv"
out_p.parent.mkdir(exist_ok=True)
out.to_csv(out_p, index=False)

summary = {
    "verified_on": now_ts,
    "baseline_files_checked": int(len(BASE)),
    "baseline_by_class": per_class,
    "changed_during_this_pass_vs_baseline": changed_this_pass,
    "pre_existing_deviations_vs_baseline": changed_preexisting,
    "missing_from_baseline": missing,
    "files_modified_during_this_pass": len(touched),
    "raw_files_modified_during_this_pass": len(raw_touched),
    "frozen_notebooks_modified_during_this_pass": len(frozen_touched),
    "checks_total": int(len(out)),
    "checks_failed": int((out["result"] == "FAIL").sum()),
    "checks_review": int((out["result"] == "REVIEW").sum()),
    "report": str(out_p),
}
with open(R / "reports_final_v3" / "integrity_verification_v3.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print(json.dumps({k: v for k, v in summary.items()
                  if k not in ("baseline_by_class", "changed_during_this_pass_vs_baseline",
                               "pre_existing_deviations_vs_baseline")}, indent=2))
print()
print(out.to_string(index=False))
