r"""Update the V10 section of EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb after human sign-off.

Scope: cells 91 (markdown), 92 (code, re-executed read-only to refresh its embedded
output) and 93 (markdown). The 90 frozen v3 cells (indices 1..90) and the v3 notebook
itself are verified byte-identical before and after the write. No preprocessing is run;
the refreshed output comes from executing the V10 status cell in-process (read-only).
"""
import hashlib
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

ROOT = Path(r"E:\REU_DATA")
V3 = ROOT / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb"
V4 = ROOT / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb"
SIGNOFF = ROOT / "signoff_finalization_v2"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


MD_91 = """### V10 — Human ICA sign-off workflow status (v4 addition, read-only)

**What the next cell does.** Loads the formal review table built for the human sign-off pass
(`signoff_finalization_v2\\ica_review_table_v1.csv`), verifies its required schema, prints the
current decision counts, cross-checks the evidence figures on disk, and prints the feature-input
split from the updated QC summary (v3). It writes nothing and modifies nothing.

**Why this step exists.** The independent audit (`audit_finalization_v1`, 2026-10-12) refused
the v3 pass's automated ICA approvals: acceptance of an ICA-cleaned file requires a human
looking at the component evidence. V10 makes the state of that gate explicit inside the main
notebook instead of leaving it buried in side folders.

**Sign-off sessions (reviewer: Anushri Kajagar).** All 30 rows are now reviewed:
**16 APPROVED, 14 REJECTED, 0 open** — 28 decided on 2026-10-14, then `P07_maths`
APPROVED and `P08_meditation` REJECTED on 2026-11-01. The 5 pre-existing ICA
exclusions were confirmed REJECTED. Decisions and full comments live in the
review table and the append-only decision log
(`ica_signoff_decisions_log_v1.csv`, 33 entries).

**Feature input is now per-recording.** The 16 APPROVED recordings use their `*_eeg_ica.fif`
(artifact-window registers still honoured); the other 24 EEG recordings use the cleaned
`*_eeg.fif`. See `signoff_finalization_v2\\eeg_qc_summary_v3.csv`.

**Validation performed.** Schema assert on the 11 required columns; 30 unique rows; existence
of every component-map and before/after evidence figure; decision-vocabulary check; every
feature-input path in the QC summary verified on disk.

**Limitations remaining.** No sign-off row is open; the acquisition reference remains UNKNOWN
(see `audit_finalization_v1\\reports\\acquisition_reference_note_v1.md`); no feature extraction
or Dosha classification has started.
"""

MD_93 = """### Final v4 summary — preprocessing + sign-off gate

- **Preprocessing itself is final.** 40 cleaned `*_eeg.fif`, 30 `*_eeg_ica.fif`, per-recording
  JSONs, registers, and QC tables are consistent and verified (v3 report + independent audit).
- **The human ICA sign-off gate is complete (30 of 30 decided).** 16 APPROVED / 14 REJECTED /
  0 open — 28 rows on 2026-10-14, then `P07_maths` APPROVED and `P08_meditation` REJECTED on
  2026-11-01. All 5 pre-existing ICA exclusions remain REJECTED. Decisions live in
  `signoff_finalization_v2\\ica_review_table_v1.csv` with the append-only decision log.
- **Feature inputs depend on the sign-off:** ICA output for the 16 approved recordings,
  cleaned pre-ICA file for the other 24. Honour the artifact-window register for every row.
- **Nothing downstream has started** — no feature extraction, no questionnaires, no Dosha
  classification. That work may begin with the documented constraints in force (artifact-window
  register, 5 excluded ICA files, unknown acquisition reference).
- **Change log / validation:** `signoff_finalization_v2\\CHANGE_LOG.md` and
  `signoff_finalization_v2\\VALIDATION_REPORT.md`.
"""

CODE_92 = '''# ===== V10: human ICA sign-off status (read-only; writes nothing) =====
from pathlib import Path
import pandas as pd

SIGNOFF_DIR = Path(r"E:\\REU_DATA\\signoff_finalization_v2")
REVIEW_TABLE = SIGNOFF_DIR / "ica_review_table_v1.csv"
CONTEXT = SIGNOFF_DIR / "ica_review_context_v1.csv"
QC_SUMMARY = SIGNOFF_DIR / "eeg_qc_summary_v3.csv"

REQUIRED = ["participant_id", "condition", "recording_id", "components_removed",
            "artifact_evidence", "signal_quality_review", "alpha_loss_review",
            "decision", "reviewer", "review_date", "comments"]
ALLOWED = {"APPROVED", "REJECTED", "NEEDS_REVIEW"}

review = pd.read_csv(REVIEW_TABLE, keep_default_na=False)
context = pd.read_csv(CONTEXT, keep_default_na=False)
qc = pd.read_csv(QC_SUMMARY, keep_default_na=False)

assert list(review.columns) == REQUIRED, "review table schema changed"
assert len(review) == 30 and review["recording_id"].is_unique, "expected 30 unique rows"
assert set(review["decision"]) <= ALLOWED, "unknown decision value"
assert (review["reviewer"].str.strip() != "").all(), "every row must carry a reviewer"

maps_ok = context["evidence_component_map"].map(lambda p: Path(p).exists()).all()
ba_ok = context["evidence_beforeafter"].map(
    lambda p: p in ("NOT AVAILABLE", "PENDING") or Path(p).exists()).all()

eeg_qc = qc[qc["modality"] == "eeg"]
ica_input_n = int(eeg_qc["feature_input_file"].str.endswith("_eeg_ica.fif").sum())
cleaned_input_n = int(eeg_qc["feature_input_file"].str.endswith("_eeg.fif").sum())
assert ica_input_n + cleaned_input_n == 40, "feature-input split must cover 40 EEG rows"
assert eeg_qc["feature_input_file"].map(lambda p: Path(p).exists()).all(), \
    "every feature-input file must exist on disk"

print(f"Review table rows: {len(review)}  (one per ICA recording; speech-condition EEG has no ICA)")
print(f"Decision counts: {review['decision'].value_counts().to_dict()}")
print(f"Formally decided rows: {int((review['decision'] != 'NEEDS_REVIEW').sum())} of 30 "
      f"(reviewer on all rows: {sorted(set(review['reviewer']))})")
print(f"Audit dispositions: {context['audit_disposition'].value_counts().to_dict()}")
print(f"Evidence on disk - component maps all exist: {bool(maps_ok)}; "
      f"before/after figures all exist: {bool(ba_ok)}")
print(f"QC summary rows: {len(qc)} (40 EEG + 10 speech)")
print(f"EEG audit readiness: {eeg_qc['audit_readiness'].value_counts().to_dict()}")
print(f"Feature inputs now in force - ICA fif: {ica_input_n}, cleaned pre-ICA fif: {cleaned_input_n} "
      f"(all 40 paths verified on disk)")
'''


def main() -> None:
    v3_hash_before = sha256(V3)
    v3 = json.loads(V3.read_text(encoding="utf-8"))
    v4 = json.loads(V4.read_text(encoding="utf-8"))
    assert len(v4["cells"]) == 94, "unexpected v4 cell count"
    for i in range(1, 91):
        assert v4["cells"][i] == v3["cells"][i - 1], f"frozen cell mismatch at index {i}"

    review = pd.read_csv(SIGNOFF / "ica_review_table_v1.csv", keep_default_na=False)
    counts = review["decision"].value_counts().to_dict()
    assert counts.get("APPROVED") == 16 and counts.get("REJECTED") == 14, \
        f"unexpected decision counts {counts}"
    assert counts.get("NEEDS_REVIEW", 0) == 0, "sign-off is not complete"

    v4["cells"][91]["source"] = MD_91.splitlines(keepends=True)
    v4["cells"][92]["source"] = CODE_92.splitlines(keepends=True)

    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(compile(CODE_92, "<V10-status-cell>", "exec"), {"__name__": "__main__"})
    output_text = buf.getvalue()
    assert "APPROVED" in output_text, "unexpected cell output"
    assert "ICA fif: 16" in output_text, "feature-input split not refreshed"

    v4["cells"][92]["execution_count"] = 35
    v4["cells"][92]["outputs"] = [{
        "output_type": "stream",
        "name": "stdout",
        "text": output_text.splitlines(keepends=True),
    }]
    v4["cells"][93]["source"] = MD_93.splitlines(keepends=True)

    tmp = V4.with_suffix(".ipynb.tmp")
    tmp.write_text(json.dumps(v4, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, V4)

    v4_after = json.loads(V4.read_text(encoding="utf-8"))
    assert len(v4_after["cells"]) == 94
    for i in range(1, 91):
        assert v4_after["cells"][i] == v3["cells"][i - 1], f"frozen cell changed at index {i}"
    assert sha256(V3) == v3_hash_before, "v3 notebook changed"
    print("UPDATED EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb V10 cells (91-93)")
    print(f"  v3 notebook hash unchanged: {v3_hash_before[:16]}...")
    print(f"  90 frozen cells verified identical after write")
    print(f"  embedded output: {len(output_text.splitlines())} lines, decision counts {counts}")


if __name__ == "__main__":
    main()
