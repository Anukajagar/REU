"""Build notebooks/EEG_Feature_Extraction.ipynb (v1).

The notebook is a report over the outputs of extract_eeg_features.py.  It
loads the saved tables if they exist and only runs extraction on a clean
checkout.  Build with:
    py -3.14 "EEG features/scripts/build_eeg_feature_notebook.py" --force
Then execute with:
    py -3.14 reports_final_v3/scripts/run_nb.py "notebooks/EEG_Feature_Extraction.ipynb"
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(r"E:\REU_DATA")
OUT_NB = ROOT / "notebooks" / "EEG_Feature_Extraction.ipynb"

import sys

if OUT_NB.exists() and "--force" not in sys.argv:
    raise SystemExit(f"REFUSING TO OVERWRITE {OUT_NB}; pass --force to rebuild")


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


cells = [
    md(
        """
# EEG Feature Extraction (v1)

**Project:** Analysis of Neuro-Acoustic Features from EEG and Speech Signals for Dosha Characterization

**Scope:** sensor-space EEG feature extraction from the finalised preprocessing outputs.
No rereferencing, no interpolation, no connectivity, no EEG-speech fusion, no Dosha modelling.

This notebook is the human-readable report for `EEG features/scripts/extract_eeg_features.py`.
It loads the saved tables if they exist; on a clean checkout it runs the extraction once.
"""
    ),
    md(
        """
## 1. Inputs and rules

- Feature input file per recording: `signoff_finalization_v2/eeg_qc_summary_v3.csv` (`feature_input_file`).
- 16 recordings use `*_eeg_ica.fif`; 24 use the cleaned pre-ICA `*_eeg.fif` (16 APPROVED ICA outputs).
- 931 one-second artifact windows from `audit_finalization_v1/eeg/artifact_log_v1.csv` are skipped.
- No file in the repository is modified. All outputs are new files under `EEG features/`.
- The acquisition reference is unknown (QC-01), so no Laplacian/CSD/connectivity features are computed.
"""
    ),
    code(
        """
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from IPython.display import Image, Markdown, display

ROOT = Path(r"E:\\REU_DATA")
OUT = ROOT / "EEG features"
sys.path.insert(0, str(OUT / "scripts"))
import eeg_feature_lib as lib  # noqa: E402

print("library:", lib.__file__)
print("outputs exist:", (OUT / "eeg_features_recording_level.csv").exists())
print("feature families:", len(lib.SPECTRAL_FEATURES), "spectral,",
      len(lib.TEMPORAL_FEATURES), "temporal,", len(lib.NONLINEAR_FEATURES), "nonlinear")
"""
    ),
    md(
        """
### Input verification

The QC summary is the machine-readable source of truth for the per-recording
feature input.  It carries the final ICA sign-off decision (16 APPROVED /
14 REJECTED / 0 open) and the readiness label from the independent audit.
"""
    ),
    code(
        """
qc = lib.load_qc()
art = lib.load_artifacts()
print("QC rows:", len(qc), "| artifact windows:", len(art))
display(qc.groupby("condition").size().to_frame("recordings"))
display(qc[["participant_id", "condition", "feature_input_file",
            "ica_formal_signoff_decision", "audit_readiness"]].head(8))
"""
    ),
    md(
        """
## 2. Extraction

If the output tables are missing, the next cell runs the full extraction
(about 8 minutes on this machine).  If they exist it loads them.  To rebuild
deliberately, delete `EEG features/*.csv` or run the CLI with `--force`.
"""
    ),
    code(
        """
if not (OUT / "eeg_features_recording_level.csv").exists():
    print("No outputs found; running full extraction...")
    result = lib.run_extraction(force=False)
    print(result["outputs"])
else:
    print("Existing outputs found; loading. Delete them or use the CLI --force to rebuild.")
"""
    ),
    code(
        """
ch = pd.read_csv(OUT / "eeg_features_channel_level.csv")
rec = pd.read_csv(OUT / "eeg_features_recording_level.csv")
par = pd.read_csv(OUT / "eeg_features_participant_level.csv")
ep = pd.read_csv(OUT / "eeg_features_epoch_level.csv")
log = pd.read_csv(OUT / "eeg_feature_extraction_log.csv")
qcr = pd.read_csv(OUT / "eeg_feature_extraction_quality_report.csv")

for name, df in [("channel-level", ch), ("recording-level", rec),
                 ("participant-level", par), ("epoch-level", ep),
                 ("extraction log", log), ("QC report", qcr)]:
    print(f"{name:18s} {df.shape[0]:>7d} rows x {df.shape[1]:>3d} cols")
"""
    ),
    md(
        """
### Channel-level table

One row per recording x channel (40 x 24 = 960).  M1/M2 are retained here for
transparency but flagged `is_scalp_eeg = False` and excluded from all
recording-level aggregates.  Spectral features use the epoch-averaged Welch
PSD; temporal and nonlinear features are averaged over valid epochs.
"""
    ),
    code(
        """
key = ["recording_id", "channel", "region", "is_scalp_eeg", "rms_uv",
       "abs_power_theta_uv2", "abs_power_alpha_uv2", "abs_power_beta_uv2",
       "rel_power_alpha", "spectral_entropy", "perm_entropy", "higuchi_fd",
       "dfa_alpha", "alpha_peak_freq_hz"]
display(ch[key].head(10))
display(ch[key].describe().T[["mean", "std", "min", "max"]].round(4))
"""
    ),
    md(
        """
### Recording-level table

One row per participant x condition (40).  Global features are means/SDs across
the 22 scalp channels; regional band powers use the fixed region map; asymmetry
is `log10(right) - log10(left)` for eight homologous pairs.
"""
    ),
    code(
        """
rkey = ["recording_id", "input_variant", "n_epochs_used", "valid_duration_s",
        "artifact_fraction", "rms_uv_mean", "abs_power_alpha_uv2_mean",
        "alpha_peak_freq_hz_mean", "frontal_alpha_asymmetry"]
display(rec[rkey].to_string(index=False))
"""
    ),
    code(
        """
summary = rec.groupby("condition").agg(
    n=("recording_id", "size"),
    valid_s_mean=("valid_duration_s", "mean"),
    rms_mean=("rms_uv_mean", "mean"),
    alpha_power_mean=("abs_power_alpha_uv2_mean", "mean"),
    alpha_peak_mean=("alpha_peak_freq_hz_mean", "mean"),
    frontal_asym_mean=("frontal_alpha_asymmetry", "mean"),
).round(3)
display(summary)
"""
    ),
    md(
        """
### Participant-level table

Convenience aggregate: mean across the available conditions.  The
recording-level table remains the primary analysis table because condition
effects are large (especially alpha during meditation).
"""
    ),
    code(
        """
pkey = ["participant_id", "n_recordings", "conditions_available",
        "rms_uv_mean", "abs_power_alpha_uv2_mean", "alpha_peak_freq_hz_mean",
        "frontal_alpha_asymmetry"]
display(par[pkey].to_string(index=False))
"""
    ),
    md(
        """
## 3. Quality control

Checks Q01-Q21 are expected to pass; Q22-Q25 are documented warnings, not
defects.  The most important warning is the ICA/cleaned input mix: the feature
input differs within participants across conditions.  The cleaned-only
sensitivity check is reported in section 6.
"""
    ),
    code(
        """
display(qcr[["check_id", "check", "status", "value"]].to_string(index=False))
print(qcr["status"].value_counts().to_dict())
"""
    ),
    code(
        """
display(log[["recording_id", "input_variant", "n_epochs_used",
            "valid_duration_s", "artifact_fraction", "status", "runtime_s"]].to_string(index=False))
print("total extraction time (sum of per-recording runtimes):",
      round(log["runtime_s"].sum(), 1), "s")
"""
    ),
    md(
        """
## 4. Figures

The saved figures are descriptive only.  No inferential test is performed and
no feature is selected or tuned on the labels.
"""
    ),
    code(
        """
for p in sorted((OUT / "figures").glob("*.png")):
    print(p.name)
    display(Image(filename=str(p)))
"""
    ),
    md(
        """
## 5. Summary and limitations

The generated summary contains the full methods, output inventory and the
documented limitations.  Read it as part of this notebook, not as a substitute
for it.
"""
    ),
    code(
        """
display(Markdown((OUT / "eeg_feature_extraction_summary.md").read_text(encoding="utf-8")))
"""
    ),
    md(
        """
## 6. Validation and sensitivity

The read-only validation pass is in `validation_v1/`.  It re-hashes every input,
checks the artifact-window rule, recomputes PSD/RMS independently, and runs the
nonlinear kernels on synthetic signals.  The cleaned-only sensitivity pass
recomputes all 40 recordings on `*_eeg.fif` and compares them with the
policy-compliant primary table.
"""
    ),
    code(
        """
val = pd.read_csv(OUT / "validation_v1" / "validation_results_v1.csv")
display(val[["check_id", "category", "check", "status", "value"]].to_string(index=False))
print(val["status"].value_counts().to_dict())
"""
    ),
    code(
        """
sens_dir = OUT / "validation_v1" / "sensitivity_cleaned_only"
comp = pd.read_csv(sens_dir / "sensitivity_comparison_v1.csv")
con = pd.read_csv(sens_dir / "sensitivity_condition_contrasts_v1.csv")
key_feats = ["abs_power_alpha_uv2_mean", "abs_power_beta_uv2_mean",
             "abs_power_theta_uv2_mean", "rms_uv_mean", "higuchi_fd_mean",
             "dfa_alpha_mean", "alpha_peak_freq_hz_mean", "frontal_alpha_asymmetry"]
display(comp[comp.feature.isin(key_feats)][
    ["feature", "pearson_r", "spearman_r", "mean_abs_diff", "mean_rel_diff_pct"]
].to_string(index=False))
display(con.to_string(index=False))
print("key sign flips:", int(con["sign_flip"].sum()))
"""
    ),
    code(
        """
for p in sorted((sens_dir / "figures").glob("*.png")):
    print(p.name)
    display(Image(filename=str(p)))
"""
    ),
    code(
        """
display(Markdown((OUT / "validation_v1" / "VALIDATION_REPORT.md").read_text(encoding="utf-8")))
"""
    ),
    md(
        """
## 7. Next steps

1. Use the cleaned-only sensitivity table when interpreting theta, delta, RMS or
   any feature with r < 0.80; alpha/beta/HFD/alpha-peak conclusions are stable.
2. Join provisional labels (`Questionnaire_Analysis/participant_labels_v1.csv`) and
   speech features (`analysis_ready/participant_master_v1.csv`) on `participant_id`,
   keeping the provisional flag.
3. Confirm the acquisition reference (QC-01) before adding reference-sensitive
   features or connectivity.
4. Decide the interpolation policy for the 110 flagged channels (QC-04).
5. Only after labels are validated: feature selection and modelling with
   participant-level cross-validation.  n = 10 is exploratory.
"""
    ),
]

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {
    "display_name": "Python 3.14 (mne stack)",
    "language": "python",
    "name": "python314-mne",
}
nb.metadata["language_info"] = {"name": "python"}
OUT_NB.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, str(OUT_NB))
print(f"WROTE {OUT_NB} ({len(cells)} cells)")
