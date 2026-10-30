"""Build the human ICA sign-off review notebook (v1).

Creates notebooks\\EEG_ICA_Signoff_Review_v1.ipynb - a NEW file. Refuses to
overwrite. The notebook is read-only against all existing artifacts; its only
write target is ica_review_table_v1.csv (and an append-only decision log),
both inside signoff_finalization_v2\\, and only via the guarded record_decision()
helper when a human reviewer chooses to use it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"E:\REU_DATA")
OUT = ROOT / "notebooks" / "EEG_ICA_Signoff_Review_v1.ipynb"

KERNEL = {
    "display_name": "Python 3.14 (mne stack)",
    "language": "python",
    "name": "python314-mne",
}


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip("\n").splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip("\n").splitlines(keepends=True),
    }


CELLS = [
    md(
        """
# EEG ICA human sign-off — review notebook (v1)

**Purpose:** let a human reviewer inspect the evidence for each of the 30 ICA recordings and
record a formal decision (`APPROVED` / `REJECTED` / `NEEDS_REVIEW`). This notebook **does not
run ICA, does not regenerate any figure, and does not modify any existing result.**

**Companion files (all in `E:\\REU_DATA\\signoff_finalization_v2\\`):**

| File | What it is |
|---|---|
| `ica_review_table_v1.csv` | The formal review table (30 rows, exact required schema). Starts fully pending. |
| `ica_review_context_v1.csv` | Full metrics + absolute evidence paths per recording. |
| `beforeafter_evidence_v1\\*_beforeafter.png` | New before/after waveform + PSD figures for all 30 (built read-only from saved `.fif` files). |

**Evidence bundles built by earlier passes (read-only, untouched):**

- Component maps (30): `E:\\REU_DATA\\ica_visual_review_bundle_v1\\component_maps\\` (byte-identical copies of `EEG processed\\eeg\\figures_v2\\ica\\`)
- Component timecourses + spectra (25 pending recordings): `ica_visual_review_bundle_v1\\timecourses\\`, `...\\spectra\\`
- Contact sheet of all 30 maps: `review_contact_sheets_v1\\contact_sheet_ica_maps_all30_v1.png`
- Prior provisional recommendations (NOT formal sign-off): `provisional_review_v2\\provisional_decision_report_v2.csv`
- Per-component metrics: `component_evidence_v1\\component_metrics_v1.csv`

## Safety rules

1. **Nothing here is auto-approved.** Every row starts as `NEEDS_REVIEW`; a decision only exists
   when a human records it (here or by editing the CSV directly with the same care).
2. **Do not alter ICA components or rerun ICA** during sign-off. Review the saved outputs only.
3. **The 5 previously excluded ICA outputs stay excluded** unless the reviewer explicitly
   reinstates them *with evidence* in the comments (they destroyed posterior alpha).
4. **Until a recording is `APPROVED`, the feature input is the cleaned `*_eeg.fif`**, not the
   `*_eeg_ica.fif` (policy of `audit_finalization_v1`).
5. This notebook writes to exactly two places, both under `signoff_finalization_v2\\`:
   `ica_review_table_v1.csv` and the append-only `ica_signoff_decisions_log_v1.csv`.
"""
    ),
    md(
        """
## 1. Load the review state

**What the next cell does:** loads the review table and the context metrics, prints the current
decision counts, and verifies the table still has the required schema.
**Validation:** fails loudly if the schema or row count is wrong. Read-only.
"""
    ),
    code(
        r"""
from pathlib import Path
import pandas as pd
from IPython.display import Image, display

SIGNOFF_DIR = Path(r"E:\REU_DATA\signoff_finalization_v2")
REVIEW_TABLE = SIGNOFF_DIR / "ica_review_table_v1.csv"
CONTEXT = SIGNOFF_DIR / "ica_review_context_v1.csv"
DECISION_LOG = SIGNOFF_DIR / "ica_signoff_decisions_log_v1.csv"

REQUIRED_COLUMNS = ["participant_id", "condition", "recording_id", "components_removed",
                    "artifact_evidence", "signal_quality_review", "alpha_loss_review",
                    "decision", "reviewer", "review_date", "comments"]
ALLOWED_DECISIONS = {"APPROVED", "REJECTED", "NEEDS_REVIEW"}

review = pd.read_csv(REVIEW_TABLE, keep_default_na=False)
context = pd.read_csv(CONTEXT, keep_default_na=False)

assert list(review.columns) == REQUIRED_COLUMNS, f"schema changed: {list(review.columns)}"
assert len(review) == 30 and review["recording_id"].is_unique, "expected 30 unique recordings"
assert set(review["decision"]) <= ALLOWED_DECISIONS, "unknown decision value in table"

print(f"Review table: {REVIEW_TABLE}")
print(f"Rows: {len(review)}   Decision counts: {review['decision'].value_counts().to_dict()}")
print(f"Feature-input policy in force: cleaned *_eeg.fif for ALL 40 EEG recordings "
      f"until a row is formally APPROVED.")
review[["recording_id", "components_removed", "decision", "reviewer", "review_date"]].head(10)
"""
    ),
    md(
        """
## 2. How to review one recording

For the recording you are reviewing, work through this checklist. All four figures exist for
all 30 recordings; the timecourse/spectrum figures exist for the 25 originally pending ones
(the 5 excluded ones never had them — use the before/after figure and the component map).

1. **Component map** — the removed component indices (from `components_removed`) should look
   *ocular/frontal* (eye-blink dipole over Fp sites), not like a cortical alpha patch over
   occipital channels and not like diffuse high-frequency muscle.
2. **Timecourse** — removed components should carry blink-shaped transients or clear
   non-neural events, not sustained rhythmic brain activity.
3. **Spectrum** — removed components should not carry a strong 8–12 Hz alpha peak.
4. **Before/after figure** (new, all 30) — top panel: blinks disappear from frontal channels
   while central/posterior rhythms stay; middle: the *removed* activity is frontal/ocular;
   bottom: how much posterior alpha power was lost (compare with the stored report value in
   the title).
5. **Metrics in the context CSV** — `eog_corr_max` (removal rule ≥ 0.40), `frontal_weight`
   (≥ 0.35), `alpha_loss_pct` (guard 30%), `variance_reduction_pct`, `near_guard_flag`.
6. **Warnings** — near-guard rows (25–30% alpha loss) and the 5 exclusion rows need extra
   care; their prior recommendations are in `comments`.

Then record your decision with the helper in the next section (or edit the CSV directly).
"""
    ),
    md(
        """
## 3. Evidence viewer

**What the next cell defines:** `show_recording(recording_id)` — prints the review-table fields
and all available evidence figures for one recording. Read-only. Example call is included;
delete or change the example id as needed.
"""
    ),
    code(
        r"""
def show_recording(rid: str, table: pd.DataFrame = None, ctx: pd.DataFrame = None) -> None:
    # Display every piece of review evidence for one recording_id (e.g. 'P02_calm').
    t = review if table is None else table
    c = context if ctx is None else ctx
    row = t[t["recording_id"] == rid]
    assert len(row) == 1, f"unknown recording_id: {rid}"
    row, cx = row.iloc[0], c[c["recording_id"] == rid].iloc[0]

    print("=" * 78)
    print(f"{rid}   components removed: {row['components_removed']}   decision: {row['decision']}")
    print("-" * 78)
    print(f"artifact_evidence:       {row['artifact_evidence']}")
    print(f"signal_quality_review:   {row['signal_quality_review']}")
    print(f"alpha_loss_review:       {row['alpha_loss_review']}")
    print(f"comments:                {row['comments']}")
    print("-" * 78)
    print(f"audit disposition: {cx['audit_disposition']} | near-guard: {cx['near_guard_flag']} | "
          f"prior recommendation: {cx['prior_recommendation']}")
    print(f"feature input until sign-off: {cx['feature_input_until_signoff']}")

    for label, path in [
        ("component map (bundle)", cx["evidence_component_map"]),
        ("timecourse (bundle)", cx["evidence_timecourse"]),
        ("spectrum (bundle)", cx["evidence_spectrum"]),
        ("before/after waveform+PSD (new)", cx["evidence_beforeafter"]),
    ]:
        if path in ("NOT AVAILABLE", "PENDING", ""):
            print(f"[{label}] NOT AVAILABLE")
            continue
        p = Path(path)
        if not p.exists() and not (SIGNOFF_DIR / path).exists():
            print(f"[{label}] MISSING FILE: {path}")
            continue
        display(Image(filename=str(p if p.exists() else SIGNOFF_DIR / path)))

# Example (uncomment):
# show_recording("P02_calm")
print("Helper loaded. Call e.g. show_recording('P02_calm') to inspect a recording.")
"""
    ),
    md(
        """
## 4. Record a decision (guarded)

**What the next cell defines:** `record_decision(...)` — the only sanctioned write path.

Guards enforced:

- decision must be one of `APPROVED`, `REJECTED`, `NEEDS_REVIEW`;
- `APPROVED`/`REJECTED` require a non-empty `reviewer` and `review_date` (ISO `YYYY-MM-DD`) —
  no anonymous decisions, no invented defaults;
- recording_id must exist; each decision is also appended to an **append-only** log file
  (`ica_signoff_decisions_log_v1.csv`) for auditability;
- the review table is the only file updated, and only that one row.

Prefer editing in a copy first? Just call the helper with `table_path=...` pointing to a copy.
"""
    ),
    code(
        r"""
from datetime import date as _date

def record_decision(rid: str, decision: str, reviewer: str, review_date: str,
                    comments_add: str = "", table_path: Path = None,
                    log_path: Path = None) -> None:
    # Record one human decision into the review table (+ append-only log).
    table_path = Path(table_path) if table_path else REVIEW_TABLE
    log_path = Path(log_path) if log_path else DECISION_LOG

    assert decision in ALLOWED_DECISIONS, f"decision must be one of {sorted(ALLOWED_DECISIONS)}"
    if decision in ("APPROVED", "REJECTED"):
        assert reviewer.strip(), "APPROVED/REJECTED require a non-empty reviewer name"
        assert review_date.strip(), "APPROVED/REJECTED require review_date (YYYY-MM-DD)"
        _date.fromisoformat(review_date)  # raises if malformed

    t = pd.read_csv(table_path, keep_default_na=False)
    assert list(t.columns) == REQUIRED_COLUMNS
    idx = t.index[t["recording_id"] == rid]
    assert len(idx) == 1, f"unknown recording_id: {rid}"
    i = idx[0]
    prior = t.at[i, "decision"]
    t.at[i, "decision"] = decision
    t.at[i, "reviewer"] = reviewer.strip()
    t.at[i, "review_date"] = review_date.strip()
    if comments_add.strip():
        t.at[i, "comments"] = (str(t.at[i, "comments"]) + " | REVIEWER: " + comments_add.strip()).strip(" |")
    t.to_csv(table_path, index=False, encoding="utf-8")

    log_row = pd.DataFrame([{
        "recording_id": rid, "prior_decision": prior, "decision": decision,
        "reviewer": reviewer.strip(), "review_date": review_date.strip(),
        "comments_add": comments_add.strip(),
    }])
    if log_path.exists():
        log_row.to_csv(log_path, mode="a", header=False, index=False, encoding="utf-8")
    else:
        log_row.to_csv(log_path, index=False, encoding="utf-8")
    print(f"RECORDED {rid}: {prior} -> {decision} (reviewer={reviewer!r}, date={review_date})")

# Example (uncomment ONLY when you are ready to make a real decision):
# record_decision("P02_calm", "APPROVED", reviewer="<your name>", review_date="YYYY-MM-DD",
#                 comments_add="removed IC0 is a clear blink component; alpha loss acceptable")
print("record_decision() loaded. No decision has been written.")
"""
    ),
    md(
        """
## 5. Validation gate

**What the next cell does:** re-reads the table and checks invariants that keep the sign-off
honest. Run it after every recording you decide, and once at the end.

Checks:

1. Schema and 30 unique rows.
2. Every decision is in the allowed vocabulary.
3. No `APPROVED`/`REJECTED` row lacks reviewer or date (nothing can be approved anonymously).
4. Every decided row's evidence files exist on disk.
5. The 5 previously excluded recordings are only `APPROVED` if the reviewer left an explicit
   reinstatement comment containing the word `evidence` (case-insensitive).
6. Prints the remaining-pending list so nothing can be quietly presented as finished.
"""
    ),
    code(
        r"""
def validate_signoff_table(table_path: Path = None) -> dict:
    table_path = Path(table_path) if table_path else REVIEW_TABLE
    t = pd.read_csv(table_path, keep_default_na=False)
    ctx = context

    assert list(t.columns) == REQUIRED_COLUMNS, "schema drift"
    assert len(t) == 30 and t["recording_id"].is_unique, "row count / uniqueness"
    assert set(t["decision"]) <= ALLOWED_DECISIONS, "vocabulary violation"

    decided = t[t["decision"].isin(["APPROVED", "REJECTED"])]
    missing_meta = decided[(decided["reviewer"].str.strip() == "") | (decided["review_date"].str.strip() == "")]
    assert len(missing_meta) == 0, f"anonymous decisions found: {missing_meta['recording_id'].tolist()}"

    excluded5 = {"P01_meditation", "P04_meditation", "P07_meditation", "P09_calm", "P09_meditation"}
    for _, r in t[t["recording_id"].isin(excluded5) & (t["decision"] == "APPROVED")].iterrows():
        assert "evidence" in str(r["comments"]).lower(), (
            f"{r['recording_id']}: excluded ICA output approved without reinstatement evidence in comments"
        )

    for _, r in decided.iterrows():
        c = ctx[ctx["recording_id"] == r["recording_id"]].iloc[0]
        for path in (c["evidence_component_map"], c["evidence_beforeafter"]):
            if path not in ("NOT AVAILABLE", "PENDING", ""):
                assert Path(path).exists() or (SIGNOFF_DIR / path).exists(), f"missing evidence: {path}"

    counts = t["decision"].value_counts().to_dict()
    pending = t.loc[t["decision"] == "NEEDS_REVIEW", "recording_id"].tolist()
    print("VALIDATION PASSED")
    print(f"  decision counts: {counts}")
    print(f"  still pending ({len(pending)}): {', '.join(pending) if pending else '-'}")
    print("  feature-input reminder: cleaned *_eeg.fif remains the input for every "
          "recording that is not formally APPROVED.")
    return {"counts": counts, "pending": pending}

validate_signoff_table()
"""
    ),
    md(
        """
## 6. What a decision means downstream

| Decision | Effect on feature extraction |
|---|---|
| `APPROVED` | The `*_eeg_ica.fif` becomes an allowed input for that recording (still honour the artifact-window register). |
| `REJECTED` | The ICA output is not used; the cleaned `*_eeg.fif` is the input. The ICA file stays on disk for audit. |
| `NEEDS_REVIEW` | Nothing changes: cleaned `*_eeg.fif` is the input; the row stays open. |

**Not in scope of this notebook (and not started anywhere):** feature extraction, questionnaire
fusion, Dosha classification, machine learning. The project gate is: validated preprocessing +
recorded human review — this notebook is the second half of that gate.
"""
    ),
]


def main() -> None:
    if OUT.exists():
        sys.exit(f"REFUSING TO OVERWRITE {OUT}")
    nb = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": KERNEL,
            "language_info": {"name": "python", "version": "3.14.4"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    # structural self-check: code cells must compile
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            compile("".join(c["source"]), f"cell{i}", "exec")
    OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"WROTE {OUT} ({len(nb['cells'])} cells; all code cells compile)")


if __name__ == "__main__":
    main()
