"""Build the finalized notebook v4 (copy of v3 + appended V10 sign-off section).

- Reads notebooks\\EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb read-only.
- Writes a NEW file notebooks\\EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb
  (refuses to overwrite). The v3 file is never modified.
- The original 90 cells are carried over byte-identically (sources + saved
  outputs). They are NOT re-executed (re-running V6/V7 would refit ICA - out of
  scope and forbidden by the task rules).
- The new V10 code cell is executed here (read-only against all artifacts) and
  its captured stdout is embedded, so the saved output matches the code.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(r"E:\REU_DATA")
SRC = ROOT / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb"
OUT = ROOT / "notebooks" / "EEG_Dataset_Analysis_and_Preprocessing_v4.ipynb"

BANNER = """\
# v4 — identical to v3, plus a human ICA sign-off section (V10) at the end

**What changed from v3:** exactly one banner cell (this one) and the new **V10** section
appended after the v3 finalization cells. All 90 original v3 cells — sources **and** saved
outputs from the 2026-10-11 run — are carried over **unmodified and were NOT re-executed**
in this copy. The frozen v3 notebook remains untouched at
`notebooks\\EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb`.

**Do not re-run this notebook end-to-end.** V6/V7 refit ICA for 30 recordings (expensive)
and STEPs 1–15 rewrite cleaned outputs. Everything after v3 is read-only status checking.

**V10 (new):** points at the formal human sign-off workflow in
`E:\\REU_DATA\\signoff_finalization_v2\\` — the review table (all rows pending), the
evidence bundles, and the updated QC summary. No existing result was altered by v4.
"""

V10_MD = """\
### V10 — Human ICA sign-off workflow status (v4 addition, read-only)

**What the next cell does.** Loads the formal review table built for the human sign-off pass
(`signoff_finalization_v2\\ica_review_table_v1.csv`), verifies its required schema, prints the
current decision counts, cross-checks the evidence figures on disk, and prints the EEG
readiness counts from the updated QC summary. It writes nothing and modifies nothing.

**Why this step exists.** The independent audit (`audit_finalization_v1`, 2026-10-12) refused
the v3 pass's automated ICA approvals: acceptance of an ICA-cleaned file requires a human
looking at the component evidence. V10 makes the state of that gate explicit inside the main
notebook instead of leaving it buried in side folders.

**Important parameters.** None — this cell has no tunables by design; it is a status check.

**What the output means.** `decision counts` should show `NEEDS_REVIEW: 30` until a human
reviewer records decisions in the review notebook
(`notebooks\\EEG_ICA_Signoff_Review_v1.ipynb`). The 5 previously excluded ICA outputs are part
of those 30 rows and stay excluded until a reviewer explicitly reinstates them with evidence.

**Validation performed.** Schema assert on the 11 required columns; 30 unique rows; existence
of every component-map and before/after evidence figure; decision-vocabulary check.

**Limitations remaining.** The sign-off itself has not happened (0/30 decided). Until it does,
the feature input for **all 40** EEG recordings is the cleaned `*_eeg.fif`, and the acquisition
reference remains UNKNOWN (see `audit_finalization_v1\\reports\\acquisition_reference_note_v1.md`).
"""

V10_CODE = r"""
# ===== V10: human ICA sign-off status (read-only; writes nothing) =====
from pathlib import Path
import pandas as pd

SIGNOFF_DIR = Path(r"E:\REU_DATA\signoff_finalization_v2")
REVIEW_TABLE = SIGNOFF_DIR / "ica_review_table_v1.csv"
CONTEXT = SIGNOFF_DIR / "ica_review_context_v1.csv"
QC_SUMMARY = SIGNOFF_DIR / "eeg_qc_summary_v2.csv"

REQUIRED = ["participant_id", "condition", "recording_id", "components_removed",
            "artifact_evidence", "signal_quality_review", "alpha_loss_review",
            "decision", "reviewer", "review_date", "comments"]
ALLOWED = {"APPROVED", "REJECTED", "NEEDS_REVIEW"}

review = pd.read_csv(REVIEW_TABLE, keep_default_na=False)
context = pd.read_csv(CONTEXT, keep_default_na=False)
qc = pd.read_csv(QC_SUMMARY)

assert list(review.columns) == REQUIRED, "review table schema changed"
assert len(review) == 30 and review["recording_id"].is_unique, "expected 30 unique rows"
assert set(review["decision"]) <= ALLOWED, "unknown decision value"
# NOTE: rows may legitimately be decided later; V10 only reports the counts.

maps_ok = context["evidence_component_map"].map(lambda p: Path(p).exists()).all()
ba_ok = context["evidence_beforeafter"].map(
    lambda p: p in ("NOT AVAILABLE", "PENDING") or Path(p).exists()).all()

eeg_qc = qc[qc["modality"] == "eeg"]
print(f"Review table rows: {len(review)}  (one per ICA recording; speech-condition EEG has no ICA)")
print(f"Decision counts: {review['decision'].value_counts().to_dict()}")
print(f"Audit dispositions: {context['audit_disposition'].value_counts().to_dict()}")
print(f"Formally decided rows: {int((review['decision'] != 'NEEDS_REVIEW').sum())}")
print(f"Evidence on disk — component maps all exist: {bool(maps_ok)}; "
      f"before/after figures all exist: {bool(ba_ok)}")
print(f"QC summary rows: {len(qc)} (40 EEG + 10 speech)")
print(f"EEG audit readiness: {eeg_qc['audit_readiness'].value_counts().to_dict()}")
print("Feature-input policy in force: cleaned *_eeg.fif for all 40 EEG recordings "
      "until a recording is formally APPROVED by a human reviewer.")
"""

V10_FINAL_MD = """\
### Final v4 summary — preprocessing + sign-off gate

- **Preprocessing itself is final.** 40 cleaned `*_eeg.fif`, 30 `*_eeg_ica.fif`, per-recording
  JSONs, registers, and QC tables are consistent and verified (v3 report + independent audit).
- **The human ICA sign-off gate is open, not closed.** Use
  `notebooks\\EEG_ICA_Signoff_Review_v1.ipynb` to review the 30 ICA recordings and record
  decisions in `signoff_finalization_v2\\ica_review_table_v1.csv`.
- **Nothing downstream has started** — no feature extraction, no questionnaires, no Dosha
  classification. That work may begin only after the review table is complete and the
  documented constraints (artifact-window register, excluded ICA files, unknown acquisition
  reference) are honoured.
- **Change log / validation:** `signoff_finalization_v2\\CHANGE_LOG.md` and
  `signoff_finalization_v2\\VALIDATION_REPORT.md`.
"""


def main() -> None:
    if OUT.exists():
        sys.exit(f"REFUSING TO OVERWRITE {OUT}")
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    assert len(nb["cells"]) == 90, f"unexpected v3 cell count {len(nb['cells'])}"

    # capture a real execution of the V10 code for embedding
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(V10_CODE, "V10", "exec"), {})
    captured = buf.getvalue()
    assert "Review table rows: 30" in captured, captured
    assert "maps all exist: True" in captured, captured

    banner_cell = {"cell_type": "markdown", "metadata": {},
                   "source": BANNER.splitlines(keepends=True)}
    v10_md_cell = {"cell_type": "markdown", "metadata": {},
                   "source": V10_MD.splitlines(keepends=True)}
    v10_code_cell = {
        "cell_type": "code",
        "execution_count": 34,
        "metadata": {},
        "outputs": [{"output_type": "stream", "name": "stdout",
                     "text": captured.splitlines(keepends=True)}],
        "source": V10_CODE.strip("\n").splitlines(keepends=True),
    }
    v10_final_cell = {"cell_type": "markdown", "metadata": {},
                      "source": V10_FINAL_MD.splitlines(keepends=True)}

    nb["cells"] = [banner_cell] + nb["cells"] + [v10_md_cell, v10_code_cell, v10_final_cell]
    compile(V10_CODE, "V10", "exec")

    OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"WROTE {OUT} ({len(nb['cells'])} cells = 1 banner + 90 frozen v3 + 3 V10)")
    print("--- embedded V10 output ---")
    print(captured)


if __name__ == "__main__":
    main()
