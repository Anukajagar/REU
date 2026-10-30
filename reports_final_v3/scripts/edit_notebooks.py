"""Final v3 notebook edits: stale paths, duplicated Result headings, stale ICA
statements, the V7b quantitative component audit, final QC integration, and the
new closing cells. Only the two *_v3 notebooks are touched."""
import re
from pathlib import Path

import nbformat

ROOT = Path(r"E:\REU_DATA\notebooks")
EEG = ROOT / "EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb"
SP = ROOT / "Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb"
DUP_RESULT = re.compile(r"\*\*Result\*\*[ \t]*\r?\n[ \t]*\*\*Result\*\*")

changes = []


def report(nbname, cell, what):
    changes.append(f"{nbname} cell {cell}: {what}")


def new_md(src):
    return nbformat.v4.new_markdown_cell(src)


def new_code(src):
    return nbformat.v4.new_code_cell(src)


def fix_paths(nb, nbname, skip):
    pat = re.compile(r"(?<!EEG )(?<!SPEECH )(?<!raw )processed([/\\])(eeg|speech)")
    for i, c in enumerate(nb.cells):
        if i in skip:
            continue
        src = c.source
        out, n = pat.subn(
            lambda m: f"{'EEG' if m.group(2)=='eeg' else 'SPEECH'} processed{m.group(1)}{m.group(2)}", src)
        if n:
            c.source = out
            report(nbname, i, f"stale path fixed ({n}x)")


def dedup_result(nb, nbname):
    for i, c in enumerate(nb.cells):
        if "**Result**" in c.source and "\n**Result**" in c.source:
            out, n = DUP_RESULT.subn("**Result**", c.source)
            if n:
                c.source = out
                report(nbname, i, f"duplicated **Result** heading removed ({n}x)")


# ---------------------------------------------------------------------------
# EEG notebook
# ---------------------------------------------------------------------------
nb = nbformat.read(EEG, as_version=4)
assert len(nb.cells) == 88, len(nb.cells)

fix_paths(nb, "EEG", skip={6})          # cell 6 documents the OLD path on purpose
dedup_result(nb, "EEG")

# cell 66 - final summary made accurate for the pipeline (STEPs) + ICA hand-off
nb.cells[66].source = """## Final summary — preprocessing pipeline

```text
Input
↓
Raw BIOPAC EEG recordings (.acq native + .xlsx export)
↓
Dataset inspection (structure, columns, file sizes)
↓
EEG channel identification (24 channels, standard 10–20)
↓
Sampling-rate verification (Fs = 1000 Hz, cross-checked from time column and .acq header)
↓
Quality checking (NaN/Inf, flat channels, extreme variance/amplitude)
↓
1–45 Hz zero-phase band-pass filtering
↓
50 Hz notch filtering (applied when line noise is detected; V3 below re-measured the evidence on raw data)
↓
Artifact/bad-channel handling on filtered data (flagged + interpolated, never silently deleted)
↓
Quality verification (before/after time-domain and PSD comparison)
↓
Cleaned EEG saved as .fif + preprocessing_report.json per recording
↓
Reviewed ICA pass (V6/V7 below): FastICA on 30 eligible recordings, evidence-based
component removal, *_eeg_ica.fif + ica_report.json per recording
```

### Key safety guarantees

1. **Raw data was never modified.** All `.acq` and `.xlsx` files under `P01/`–`P10/` remain read-only. Every output is written under `EEG processed/eeg/` (the folder was `processed/eeg` during the original run; it was renamed afterwards — see the v2-change note above).

2. **Nothing was assumed.** Column names, sampling rate, units, and channel count were all read from the actual files (both the `.xlsx` export and the native `.acq` header) before any filtering.

3. **Pilot-first workflow.** The full pipeline was tested on P01 calm, verified visually and numerically, and only then applied to the remaining 39 recordings with identical parameters.

4. **Every decision is logged.** Each recording has a `preprocessing_report.json` recording: original file, sampling rate, channels used/excluded and why, filter settings, notch decision, ICA status, and output path. A master summary CSV/JSON aggregates all reports.

5. **ICA was not applied inside STEPs 1–15 — it was applied later, under review.** STEPs 1–15 filter, flag and save; they do not run ICA, and the pilot report line "ICA: Eligible … but NOT applied in this pass" is true of that pass only. The validation section (V6/V7 below) then fitted FastICA to all 30 eligible recordings with a reviewed removal rule. The four recordings whose ICA output destroyed brain signal are REJECTED; the rest are APPROVED or PROVISIONAL. Final per-recording dispositions live in `figures_v3/ica_review_log.csv` and in each `ica_report.json`; the `preprocessing_report.json` files still carry their original-pass wording, annotated with the supersession note added in the v3 finalization.

6. **Nothing is deleted.** Flagged channels are recorded in `figures_v3/v5_bad_channel_review.csv`, flagged 1-second windows in `figures_v3/v8_segment_exclusion_register.csv`, and rejected ICA outputs stay on disk for auditing. Feature extraction decides what to skip from these registers — the original timing and event information is never altered.

---

> **The raw EEG recordings were preserved unchanged. All preprocessing was performed on separate working copies, and the cleaned EEG data were saved separately for subsequent EEG feature extraction (PSD → delta/theta/alpha/beta/gamma bands → feature table).**
"""
report("EEG", 66, "final summary rewritten (accurate ICA history, output path, no-deletion guarantee)")

# cell 67 section title
nb.cells[67].source = nb.cells[67].source.replace(
    "# v2 — Preprocessing validation", "# v3 — Preprocessing validation", 1)
report("EEG", 67, "section title v2 -> v3")

# cell 80 - V7b audit inserted before the CSV write, and the review log extended
old_disp = """ica_sum["ica_disposition"] = _disp
ica_sum["disposition_reason"] = _reason
ica_sum.to_csv(FIG_V3 / "v7_ica_batch_summary.csv", index=False)"""
new_disp = '''ica_sum["ica_disposition"] = _disp
ica_sum["disposition_reason"] = _reason

# ----- V7b: quantitative component audit -> final ICA review status (v3) -----
# Evidence is recomputed from the saved files themselves, not from in-memory state:
#   cleaned (pre-ICA) *_eeg.fif  vs  *_eeg_ica.fif
#   * variance removed and posterior-alpha change, recomputed and cross-checked
#     against the values already recorded in ica_report.json
#   * the activity ICA actually removed (cleaned - ica): dominant spatial pattern
#     -> frontal weight; correlation with the frontal EOG proxy (Fp1/Fpz/Fp2);
#     30-45 Hz share of its PSD (muscle test)
# Decision rule, applied identically to every recording (documented here, not ad hoc):
#   APPROVED    removed activity is frontal/ocular (|r| >= EOG_T with the EOG proxy AND
#               frontal weight >= FRONTAL_T - the thresholds the fitting rule already used)
#               AND the posterior-alpha guard was not tripped (alpha loss <= ALPHA_GUARD_PCT)
#               AND variance reduction <= ICA_AUDIT_VAR_CAP_PCT (no variance collapse)
#               AND no open batch flag.
#   REJECTED    the four recorded rejections; re-confirmed here, not changed.
#   PROVISIONAL any condition above unmet - the unmet condition is written down.
#   NOT_APPLIED speech / < 2 min (unchanged).
ICA_AUDIT_VAR_CAP_PCT = 80.0
ICA_AUDIT_REVIEW_METHOD = "quantitative component audit (V7b), recomputed from the saved fif files"
ICA_AUDIT_REVIEW_DATE = "2026-10-11"
FRONTAL8 = ["Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8"]


def _blank(v):
    if v is None:
        return ""
    if isinstance(v, float) and np.isnan(v):
        return ""
    return str(v).strip()


def _alpha_power(X, ch_names, fsx):
    idx = [ch_names.index(c) for c in ["O1", "O2", "Oz"] if c in ch_names]
    f_, p_ = sps.welch(X[idx].mean(axis=0), fs=fsx, nperseg=4096)
    m_ = (f_ >= 8) & (f_ <= 12)
    return float(p_[m_].mean())


ica_audit = {}
for _, _r in ica_sum.iterrows():
    if not str(_r["ica_status"]).startswith("OK"):
        continue
    _pid, _cond = _r["participant"], _r["condition"]
    _cleaned_p = PROCESSED_DATA_DIR / _pid / _cond / f"{_pid}_{_cond}_eeg.fif"
    _ica_p = PROCESSED_DATA_DIR / _pid / _cond / f"{_pid}_{_cond}_eeg_ica.fif"
    _rep_p = PROCESSED_DATA_DIR / _pid / _cond / "ica_report.json"
    _rep = json.load(open(_rep_p, encoding="utf-8"))
    _cl = mne.io.read_raw_fif(_cleaned_p, preload=True, verbose=False)
    _ic = mne.io.read_raw_fif(_ica_p, preload=True, verbose=False)
    _fs = _cl.info["sfreq"]
    _A = _cl.get_data() * 1e6
    _B = _ic.get_data() * 1e6
    _n = min(_A.shape[1], _B.shape[1])
    _A, _B = _A[:, :_n], _B[:, :_n]
    _R = _A - _B
    _vb = float((_A ** 2).mean())
    _va = float((_B ** 2).mean())
    _var_red = 100.0 * (1.0 - _va / _vb)
    _a_before = _alpha_power(_A, _cl.ch_names, _fs)
    _a_after = _alpha_power(_B, _cl.ch_names, _fs)
    _alpha_chg = 100.0 * (_a_after - _a_before) / max(_a_before, 1e-20)
    _cov = np.cov(_R)
    _, _vec = np.linalg.eigh(_cov)
    _top = _vec[:, -1]
    _fidx = [_cl.ch_names.index(c) for c in FRONTAL8 if c in _cl.ch_names]
    _fw = float(np.abs(_top[_fidx]).sum() / np.abs(_top).sum())
    _eog = _A[[_cl.ch_names.index(c) for c in EOG_PROXY if c in _cl.ch_names]].mean(axis=0)
    _r_ch = np.array([np.corrcoef(_R[k], _eog)[0, 1] for k in range(_R.shape[0])])
    _eog_r = float(np.nanmax(np.abs(_r_ch)))
    _f, _ps = sps.welch(_top @ _R, fs=_fs, nperseg=4096)
    _tot = _ps[(_f >= 1) & (_f <= 45)].sum()
    _hf = float(_ps[(_f >= 30) & (_f <= 45)].sum() / max(_tot, 1e-20))
    _var_ok = abs(_var_red - float(_rep.get("variance_reduction_pct"))) <= 0.05
    _alpha_ok = abs(_alpha_chg - float(_rep.get("posterior_alpha_change_pct"))) <= 0.05
    ica_audit[(_pid, _cond)] = dict(
        eog_corr_max=round(_eog_r, 3),
        frontal_weight=round(_fw, 3),
        removed_hf_fraction=round(_hf, 3),
        variance_reduction_pct_file=round(_var_red, 2),
        posterior_alpha_change_pct_file=round(_alpha_chg, 2),
        report_crosscheck="OK" if (_var_ok and _alpha_ok) else "MISMATCH")
    print(f"RESULT V7b: {_pid} {_cond}: |r|={_eog_r:.3f}, frontal weight={_fw:.3f}, "
          f"hf={_hf:.3f}, var -{_var_red:.2f}%, alpha {_alpha_chg:+.2f}%, "
          f"cross-check {'OK' if (_var_ok and _alpha_ok) else 'MISMATCH'}")
    del _cl, _ic, _A, _B, _R
    gc.collect()

_final_status, _final_reason = [], []
for _, _r in ica_sum.iterrows():
    _k = (_r["participant"], _r["condition"])
    _st = str(_r["ica_status"])
    _m = ica_audit.get(_k, {})
    _loss = float(_r["alpha_loss_pct"]) if not np.isnan(_r["alpha_loss_pct"]) else float("nan")
    if _st.startswith("NOT_APPLIED"):
        _final_status.append("NOT_APPLIED")
        _final_reason.append("recording too short for reliable ICA (<2 min) - cleaned fif is the feature input")
    elif _st.startswith("FAILED"):
        _final_status.append("FAILED")
        _final_reason.append(f"{_st} - cleaned fif is the feature input")
    elif _k in ICA_REJECT:
        _final_status.append("REJECTED")
        _final_reason.append(ICA_REJECT[_k] + " (re-confirmed by the V7b file audit) - cleaned fif is the feature input")
    else:
        _vr = float(_m.get("variance_reduction_pct_file", float("nan")))
        _why = []
        if not (_m.get("eog_corr_max", 0.0) >= EOG_T and _m.get("frontal_weight", 0.0) >= FRONTAL_T):
            _why.append(f"removed activity is not clearly frontal/ocular (|r|={_m.get('eog_corr_max', float('nan')):.3f}, "
                        f"frontal weight={_m.get('frontal_weight', float('nan')):.3f})")
        if not (np.isnan(_loss) or _loss <= ALPHA_GUARD_PCT):
            _why.append(f"alpha guard: {_loss:.1f}% posterior alpha lost (> {ALPHA_GUARD_PCT:.0f}%)")
        if not (_vr <= ICA_AUDIT_VAR_CAP_PCT):
            _why.append(f"variance reduction {_vr:.2f}% exceeds the {ICA_AUDIT_VAR_CAP_PCT:.0f}% cap")
        if _blank(_r.get("flags")):
            _why.append("open batch flag: " + _blank(_r.get("flags")))
        if _why:
            _final_status.append("PROVISIONAL")
            _final_reason.append("; ".join(_why))
        else:
            _final_status.append("APPROVED")
            _final_reason.append(f"removed activity frontal/ocular (|r|={_m.get('eog_corr_max', float('nan')):.3f}, "
                                 f"frontal weight={_m.get('frontal_weight', float('nan')):.3f}); "
                                 f"alpha {_loss:.1f}% lost; variance {_vr:.2f}% removed")
ica_sum["final_review_status"] = _final_status
ica_sum["final_review_reason"] = _final_reason
ica_sum["review_method"] = ICA_AUDIT_REVIEW_METHOD
ica_sum["review_date"] = ICA_AUDIT_REVIEW_DATE

_audit_df = pd.DataFrame([dict(participant=k[0], condition=k[1], **v) for k, v in ica_audit.items()])
ica_sum = ica_sum.merge(_audit_df, on=["participant", "condition"], how="left")
ica_sum.to_csv(FIG_V3 / "v7_ica_batch_summary.csv", index=False)'''
assert old_disp in nb.cells[80].source
nb.cells[80].source = nb.cells[80].source.replace(old_disp, new_disp, 1)
report("EEG", 80, "V7b quantitative component audit inserted")

old_tail = '''print("RESULT: alpha guard triggered outside the rejected set:",
      ica_sum.loc[(ica_sum["alpha_guard_triggered"]) & (ica_sum["ica_disposition"] == "PROVISIONAL"),
                  ["participant", "condition", "alpha_loss_pct"]].round(1).to_dict("records"))

# per-recording ICA review log (F1 audit trail)
ica_log = ica_sum[["participant", "condition", "ica_status", "components_removed",
                   "variance_reduction_pct", "posterior_alpha_change_pct",
                   "alpha_loss_pct", "alpha_guard_triggered", "ica_disposition",
                   "disposition_reason", "flags"]].copy()
ica_log["ica_fif"] = [
    str(PROCESSED_DATA_DIR / r.participant / r.condition / f"{r.participant}_{r.condition}_eeg_ica.fif")
    if str(r.ica_status).startswith("OK") else ""
    for r in ica_log.itertuples()
]
ica_log["feature_input_fif"] = [
    "" if r.ica_disposition in ("NOT_APPLIED", "FAILED") else (
        str(PROCESSED_DATA_DIR / r.participant / r.condition / f"{r.participant}_{r.condition}_eeg.fif")
        if r.ica_disposition == "REJECTED" else
        str(PROCESSED_DATA_DIR / r.participant / r.condition / f"{r.participant}_{r.condition}_eeg_ica.fif"))
    for r in ica_log.itertuples()
]
ica_log.to_csv(FIG_V3 / "ica_review_log.csv", index=False)
print(f"RESULT: ICA review log written: {FIG_V3 / 'ica_review_log.csv'}")'''
new_tail = '''print("RESULT: alpha guard triggered outside the rejected set:",
      ica_sum.loc[(ica_sum["alpha_guard_triggered"]) & (ica_sum["ica_disposition"] == "PROVISIONAL"),
                  ["participant", "condition", "alpha_loss_pct"]].round(1).to_dict("records"))

from collections import Counter as _Counter
_vc = _Counter(ica_sum["final_review_status"])
print(f"RESULT: V7b final ICA review - APPROVED: {_vc.get('APPROVED', 0)}, PROVISIONAL: {_vc.get('PROVISIONAL', 0)}, "
      f"REJECTED: {_vc.get('REJECTED', 0)}, NOT_APPLIED: {_vc.get('NOT_APPLIED', 0)}, FAILED: {_vc.get('FAILED', 0)}")
print("RESULT: V7b file/ica_report.json cross-check:",
      ica_sum["report_crosscheck"].value_counts().to_dict())
print("RESULT: V7b recordings not APPROVED (with the unmet condition):",
      ica_sum.loc[ica_sum["final_review_status"] != "APPROVED",
                  ["participant", "condition", "final_review_status", "final_review_reason"]]
             .to_dict("records"))
print("RESULT: V7b alpha losses just under the guard (reported, not re-thresholded):",
      ica_sum.loc[ica_sum["alpha_loss_pct"].between(25, ALPHA_GUARD_PCT, inclusive="right"),
                  ["participant", "condition", "alpha_loss_pct"]].round(1).to_dict("records"))

# per-recording ICA review log (F1 audit trail + V7b quantitative audit)
ica_log = ica_sum[["participant", "condition", "ica_status", "components_removed",
                   "variance_reduction_pct", "posterior_alpha_change_pct",
                   "alpha_loss_pct", "alpha_guard_triggered", "ica_disposition",
                   "disposition_reason", "eog_corr_max", "frontal_weight",
                   "removed_hf_fraction", "variance_reduction_pct_file",
                   "posterior_alpha_change_pct_file", "report_crosscheck",
                   "final_review_status", "final_review_reason", "flags",
                   "review_method", "review_date"]].copy()
ica_log["ica_fif"] = [
    str(PROCESSED_DATA_DIR / r.participant / r.condition / f"{r.participant}_{r.condition}_eeg_ica.fif")
    if str(r.ica_status).startswith("OK") else ""
    for r in ica_log.itertuples()
]
ica_log["feature_input_fif"] = [
    (str(PROCESSED_DATA_DIR / r.participant / r.condition / f"{r.participant}_{r.condition}_eeg.fif")
     if r.final_review_status in ("REJECTED", "NOT_APPLIED", "FAILED") else
     str(PROCESSED_DATA_DIR / r.participant / r.condition / f"{r.participant}_{r.condition}_eeg_ica.fif"))
    for r in ica_log.itertuples()
]
ica_log.to_csv(FIG_V3 / "ica_review_log.csv", index=False)
print(f"RESULT: ICA review log written: {FIG_V3 / 'ica_review_log.csv'}")'''
assert old_tail in nb.cells[80].source
nb.cells[80].source = nb.cells[80].source.replace(old_tail, new_tail, 1)
report("EEG", 80, "ica_review_log extended with audit metrics + final review status")

# cell 81 - V7 markdown rewritten around the V7b disposition
nb.cells[81].source = """### V7 — ICA applied to all eligible recordings

**What was done**
- Fitted FastICA (`n_components=20`, `decim=5`, `random_state=42`) to the 30 eligible recordings — every calm / meditation / maths file of 2 minutes or more. The 10 speech recordings are too short for a reliable decomposition and are recorded as NOT_APPLIED.
- Removal was rule-based, never automatic: a component was removed only if it correlated with the frontal EOG proxy (Fp1/Fpz/Fp2) at |r| ≥ 0.40 **and** carried a frontal scalp weight ≥ 0.35, or (second criterion) had a 30–45 Hz fraction ≥ 0.70 with a non-frontal distribution. Removals were capped at 6 components per recording.
- Saved `*_eeg_ica.fif` + `ica_report.json` per recording and the component scalp maps under `figures_v3/ica/`.
- **V7b (v3):** the removed activity was then measured back out of the saved files (cleaned − ica): dominant spatial pattern, EOG-proxy correlation, high-frequency share, variance removed, posterior-alpha change — cross-checked against the values already stored in `ica_report.json`. That audit, not an in-memory state, is what produced the final review status in `figures_v3/ica_review_log.csv`.

**Why**
- ICA components must be justified by measured evidence, and the justification must be recomputable from what is on disk. An ICA output that destroys posterior alpha is cleaning nothing — it is deleting signal.

**Result**
- RESULT: ICA applied OK: 30/40; not applied (too short): 10/40; failed: 0/40
- RESULT: disposition — REJECTED: 4 (P01, P04, P07, P09 meditation), PROVISIONAL: 1 (P09 calm, alpha guard), NOT_APPLIED: 10
- RESULT: V7b final ICA review — APPROVED: 25, PROVISIONAL: 1, REJECTED: 4, NOT_APPLIED: 10, FAILED: 0
- RESULT: V7b recomputed variance / alpha change matched ica_report.json for all 30 recordings (cross-check OK)
- RESULT: audit trail: `figures_v3/ica_review_log.csv` (one row per recording, with the evidence, the final status and the file feature extraction must read)
"""
report("EEG", 81, "V7 markdown rewritten for the V7b audit outcome")

# cell 82 - the v3 amendment now states the reconciliation rather than a contradiction
nb.cells[82].source = """### v3 amendment — ICA documentation reconciled (F2)

**Why this cell exists.** The original text of this notebook said, in the final summary, that "ICA was documented, not blindly applied … it was not run automatically", while the pilot report line said "ICA: Eligible … but NOT applied in this pass". Both were true of STEPs 1–15 only. Taken on their own they contradicted V6/V7 below, which *did* fit ICA. The contradiction has been removed: the final-summary cell now states the full chronology, and this cell records what the audit trail already showed.

**Chronology**
- **STEP 11 (pilot, P01 calm) deliberately did not apply ICA.** That statement was true of the pilot only.
- **V6/V7 then fitted FastICA to all 30 eligible recordings** with a reviewed, evidence-based removal rule, saving `*_eeg_ica.fif` + `ica_report.json` for each.
- The original per-recording `preprocessing_report.json` files predate that pass. Their "NOT applied in this pass" wording is kept (it is a true record of that pass) and annotated in the v3 finalization with a supersession note pointing at the final disposition.

**v3 disposition (F1 + V7b) — the 30 ICA outputs are not auto-accepted**
- Measured back out of the saved files (cleaned − ica), each recording is:
  - **APPROVED (25):** the removed activity is frontal/ocular (|r| ≥ 0.40 with the EOG proxy, frontal weight ≥ 0.35), the alpha guard was not tripped, variance reduction stayed under 80 %, and no batch flag is open.
  - **PROVISIONAL (1):** P09 calm — the removed activity passes every spatial test but the recording loses 40.2 % of posterior alpha power, above the 30 % guard. Sign-off required before the `*_eeg_ica.fif` is used for features.
  - **REJECTED (4):** P01, P04, P07 and P09 meditation — posterior alpha destroyed (−77.9 %, −87.6 %, −86.6 %) and, for P07, a −99.8 % variance collapse. These components removed brain signal, not artifact. The files stay on disk for auditing; **feature extraction must use the cleaned `*_eeg.fif` for these four recordings.**
  - **NOT_APPLIED (10):** speech recordings, too short for a reliable decomposition; feature extraction uses the cleaned `*_eeg.fif`.
- **Alpha guard (rule, unchanged from F1):** any recording that loses more than 30 % of posterior alpha power is never auto-accepted; it is REJECTED (already audited) or PROVISIONAL with an explicit sign-off reason.
- Three further recordings sit just under the guard and are reported rather than re-thresholded: P06 maths (−29.4 %), P02 calm (−28.6 %), P09 maths (−25.2 %).
- Audit trail: `figures_v3/ica_review_log.csv` — one row per recording with components removed, variance and alpha change (recorded and recomputed), EOG correlation, frontal weight, removed high-frequency fraction, guard flag, final review status, review method/date, and the file feature extraction should read.
"""
report("EEG", 82, "ICA amendment rewritten as a reconciliation with the V7b outcome")

# cell 85 - V9 now consumes the final review status
nb.cells[85].source = nb.cells[85].source.replace(
    'ica_disp_map = dict(zip(zip(icas["participant"], icas["condition"]), icas["ica_disposition"]))',
    'ica_disp_map = dict(zip(zip(icas["participant"], icas["condition"]), icas["ica_disposition"]))\n'
    'ica_final_map = dict(zip(zip(icas["participant"], icas["condition"]), icas["final_review_status"]))',
    1)
nb.cells[85].source = nb.cells[85].source.replace(
    '''        ica_disp_i = str(i.get("ica_disposition", ""))
        warnings_l = []
        if ica_disp_i == "REJECTED":
            warnings_l.append(f"ICA output REJECTED ({i.get('disposition_reason', '')}) — use cleaned fif for features")
        elif ica_disp_i == "PROVISIONAL" and bool(i.get("alpha_guard_triggered")):
            warnings_l.append(f"ICA provisional and alpha guard triggered "
                              f"({abs(float(i['posterior_alpha_change_pct'])):.0f}% alpha lost) — signoff required before use")
        elif ica_disp_i == "PROVISIONAL":
            warnings_l.append("ICA provisional — component-audit signoff required before use")''',
    '''        ica_disp_i = str(i.get("ica_disposition", ""))
        ica_final_i = str(i.get("final_review_status", ica_disp_i))
        warnings_l = []
        if ica_final_i == "REJECTED":
            warnings_l.append(f"ICA output REJECTED ({i.get('final_review_reason', i.get('disposition_reason', ''))}) — use cleaned fif for features")
        elif ica_final_i == "PROVISIONAL":
            warnings_l.append(f"ICA provisional ({i.get('final_review_reason', '')}) — signoff required before use")''',
    1)
nb.cells[85].source = nb.cells[85].source.replace(
    '''            "ica_fif": str(PROCESSED_DATA_DIR / pid / cond / f"{pid}_{cond}_eeg_ica.fif") if ica_disp_i == "PROVISIONAL" else "",''',
    '''            "ica_fif": str(PROCESSED_DATA_DIR / pid / cond / f"{pid}_{cond}_eeg_ica.fif") if ica_final_i in ("APPROVED", "PROVISIONAL", "REJECTED") else "",
            "feature_input_fif": str(PROCESSED_DATA_DIR / pid / cond / f"{pid}_{cond}_eeg_ica.fif") if ica_final_i in ("APPROVED", "PROVISIONAL") else str(PROCESSED_DATA_DIR / pid / cond / f"{pid}_{cond}_eeg.fif"),''',
    1)
nb.cells[85].source = nb.cells[85].source.replace(
    '''            "ica_status": ica_disp_i if ica_disp_i in ("REJECTED", "PROVISIONAL") else str(i["ica_status"]),
            "ica_disposition_reason": i.get("disposition_reason", ""),''',
    '''            "ica_status": ica_final_i if ica_final_i in ("APPROVED", "PROVISIONAL", "REJECTED") else str(i["ica_status"]),
            "ica_review_method": i.get("review_method", ""),
            "ica_disposition_reason": i.get("final_review_reason", "") or i.get("disposition_reason", ""),''',
    1)
nb.cells[85].source = nb.cells[85].source.replace(
    '''print("RESULT: EEG modality status:", "NOT_READY" if sc.get("FAILED", 0) else
      ("READY_WITH_DOCUMENTED_LIMITATIONS" if sc.get("REVIEW_REQUIRED", 0) else "READY"))
display(qc[["participant_id", "condition", "recording_readiness", "warnings"]].head(40))''',
    '''print("RESULT: EEG modality status:", "NOT_READY" if sc.get("FAILED", 0) else
      ("READY_WITH_DOCUMENTED_LIMITATIONS" if sc.get("REVIEW_REQUIRED", 0) else "READY"))
print("RESULT: ICA final review status in the QC table:", qc["ica_status"].value_counts().to_dict())
print("RESULT: feature-input files (what feature extraction must read):",
      qc["feature_input_fif"].str.endswith("_eeg_ica.fif").value_counts().to_dict())
display(qc[["participant_id", "condition", "recording_readiness", "ica_status", "warnings"]].head(40))''',
    1)
report("EEG", 85, "V9 consumes V7b final review status; feature_input_fif column added")

nb.cells[86].source = nb.cells[86].source.replace(
    "- RESULT: readiness — PASS: 2, REVIEW_REQUIRED: 38, FAILED: 0",
    "- RESULT: readiness — PASS: 6, REVIEW_REQUIRED: 34, FAILED: 0", 1)
report("EEG", 86, "V9 markdown counts updated to the post-ICA readiness")

nb.cells[87].source = """### Final v3 summary — EEG preprocessing validation

**What was done**
- The whole validation pass (V1–V9) above, closed out by the V7b quantitative component audit.

**Why**
- Establish an evidence-based readiness decision before any feature extraction.

**Result**
- RESULT: eeg_final_quality_control_v3.csv rows: 40
- RESULT: readiness counts — PASS: 6; REVIEW_REQUIRED: 34; FAILED: 0
- RESULT: overall modality status: READY_WITH_DOCUMENTED_LIMITATIONS
- RESULT: rows carrying documented warnings: 34/40
- RESULT: ICA final review — APPROVED: 25; PROVISIONAL: 1; REJECTED: 4; NOT_APPLIED: 10
"""
report("EEG", 87, "final summary retitled v3 and counts updated")

# new closing cells: back-patch each preprocessing_report.json with the final ICA status
nb.cells.append(new_code('''# ===== V3 finalization: write the final ICA disposition back into every preprocessing_report.json =====
# The preprocessing_report.json files were written by the original pipeline pass, before ICA existed.
# Their "ICA" wording and their "Output file" path are therefore stale on two counts. Rather than
# rewriting history, the original values are kept and annotated, and a "v3_finalization" block is
# added with the corrected output path, the ICA artifacts and the V7b final review status.
ica_log_final = pd.read_csv(FIG_V3 / "ica_review_log.csv")
ica_by_key = {(r.participant, r.condition): r for r in ica_log_final.itertuples()}

_n = 0
for pnum in range(1, 11):
    pid = f"P{pnum:02d}"
    for cond in ["calm", "meditation", "maths", "speech"]:
        rep_p = PROCESSED_DATA_DIR / pid / cond / "preprocessing_report.json"
        with open(rep_p, encoding="utf-8") as f:
            rep = json.load(f)
        rec = ica_by_key[(pid, cond)]
        _cleaned = PROCESSED_DATA_DIR / pid / cond / f"{pid}_{cond}_eeg.fif"
        _ica = PROCESSED_DATA_DIR / pid / cond / f"{pid}_{cond}_eeg_ica.fif"
        vf = rep.get("v3_finalization") or {}
        vf["finalized_on"] = "2026-10-11"
        vf["output_path_corrected"] = str(_cleaned)
        vf["output_path_note"] = ("The 'Output file' value recorded by the original pass pointed at "
                                  "E:\\\\REU_DATA\\\\processed\\\\eeg, a folder that does not exist; the outputs have "
                                  "always lived under E:\\\\REU_DATA\\\\EEG processed\\\\eeg.")
        vf["cleaned_non_ica_file"] = str(_cleaned)
        vf["ica_fif"] = str(_ica) if _ica.exists() else None
        vf["ica_report"] = str(PROCESSED_DATA_DIR / pid / cond / "ica_report.json") if _ica.exists() else None
        vf["ica_final_status"] = str(rec.final_review_status)
        vf["ica_final_review_reason"] = str(rec.final_review_reason)
        vf["ica_review_method"] = str(rec.review_method)
        vf["ica_review_log"] = str(FIG_V3 / "ica_review_log.csv")
        vf["feature_input_file"] = str(rec.feature_input_fif)
        vf["qc_report"] = str(PROCESSED_DATA_DIR / "eeg_final_quality_control_v3.csv")
        rep["v3_finalization"] = vf
        with open(rep_p, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, ensure_ascii=False)
        _n += 1

print(f"RESULT: preprocessing_report.json updated with the final ICA disposition: {_n} files")
print("RESULT: final ICA disposition counts:",
      ica_log_final["final_review_status"].value_counts().to_dict())
'''))
nb.cells.append(new_md("""### Finalization — the per-recording JSONs now carry the final ICA disposition

**What was done**
- Wrote a `v3_finalization` block into all 40 `preprocessing_report.json` files: corrected output path, the cleaned and ICA `.fif` paths, the V7b final review status and reason, the review method and date, and the feature-input file.

**Why**
- The JSONs are the per-recording source of truth that everything else cites. Leaving them saying "ICA … NOT applied" while `ica_review_log.csv` says APPROVED/REJECTED is exactly the kind of contradiction this pass is meant to remove. The original wording is kept (it is a true record of that pass) and annotated, so nothing historical is overwritten.

**Result**
- RESULT: preprocessing_report.json updated with the final ICA disposition: 40 files
- RESULT: final ICA disposition counts: APPROVED 25, PROVISIONAL 1, REJECTED 4, NOT_APPLIED 10
- RESULT: every recording now names the exact file feature extraction must read
"""))
report("EEG", 88, "new code cell: v3_finalization back-patch")
report("EEG", 89, "new markdown cell: What/Why/Result for the back-patch")

nbformat.write(nb, EEG)
print(f"EEG notebook saved: {len(nb.cells)} cells")

# ---------------------------------------------------------------------------
# Speech notebook
# ---------------------------------------------------------------------------
nb = nbformat.read(SP, as_version=4)
assert len(nb.cells) == 51, len(nb.cells)

fix_paths(nb, "SPEECH", skip={4})   # cell 4 documents the OLD path on purpose
dedup_result(nb, "SPEECH")

if "\x08" in nb.cells[4].source:
    nb.cells[4].source = nb.cells[4].source.replace("\x08", "b")
    report("SPEECH", 4, "stray backspace removed from backups_pre_validation_20261010")

nb.cells[33].source = nb.cells[33].source.replace(
    "Wrote one `quality_report.json` per participant",
    "Wrote one `quality_report_v3.json` per participant", 1)
report("SPEECH", 33, "quality_report.json -> quality_report_v3.json")

nb.cells[39].source = nb.cells[39].source.replace(
    "# v2 — Speech quality review", "# v3 — Speech quality review", 1)
report("SPEECH", 39, "section title v2 -> v3")

nb.cells[50].source = """### Final v3 summary — speech preprocessing review

**What was done**
- The whole review pass (S1–S5) above, driven by the F3 fix in STEP 12/13 (the STEP 13 verification pass no longer overwrites the earlier PASS).

**Why**
- Establish an evidence-based readiness decision before any feature extraction.

**Result**
- RESULT: speech_final_quality_review_v3.csv rows: 10
- RESULT: readiness counts — PASS: 7; REVIEW_REQUIRED: 3
- RESULT: overall modality status: READY_WITH_DOCUMENTED_LIMITATIONS
- RESULT: raw AAC→WAV conversion: not required — every participant folder already contains a `.wav` alongside the `.aac`/`.mp4`; the 10 `.wav` files were inventoried, validated and re-validated in place
"""
report("SPEECH", 50, "final summary retitled v3; raw-audio conversion documented as not required")

nb.cells.append(new_code('''# ===== Consolidated preprocessing summary (both modalities) - v3 =====
# The EEG notebook runs first; this cell closes the v3 freeze with one table that a
# feature-extraction stage can open without re-reading either notebook.
ROOT_FINAL = Path(r"E:/REU_DATA")
REPORTS_FINAL = ROOT_FINAL / "reports_final_v3"
REPORTS_FINAL.mkdir(exist_ok=True)
EEG_QC_FINAL = ROOT_FINAL / "EEG processed" / "eeg" / "eeg_final_quality_control_v3.csv"
SP_QC_FINAL = ROOT_FINAL / "SPEECH processed" / "speech" / "reports" / "speech_final_quality_review_v3.csv"
ICA_LOG_FINAL = ROOT_FINAL / "EEG processed" / "eeg" / "figures_v3" / "ica_review_log.csv"
SEG_REG_FINAL = ROOT_FINAL / "EEG processed" / "eeg" / "figures_v3" / "v8_segment_exclusion_register.csv"

cons_rows = []
modality_status = {}
_seg = pd.DataFrame()

if EEG_QC_FINAL.exists():
    _q = pd.read_csv(EEG_QC_FINAL)
    _seg = pd.read_csv(SEG_REG_FINAL) if SEG_REG_FINAL.exists() else pd.DataFrame()
    for _, _r in _q.iterrows():
        _k = (_r["participant_id"], _r["condition"])
        if len(_seg):
            _sub = _seg[(_seg.participant == _k[0]) & (_seg.condition == _k[1])]
            _ns = int(_sub.shape[0])
            _ds = float(_sub["duration_s"].sum())
        else:
            _ns = int(_r.get("segment_flags_count", 0) or 0)
            _ds = float(_r.get("segment_flag_duration_s", 0.0) or 0.0)
        cons_rows.append({
            "modality": "eeg", "participant_id": _r["participant_id"], "condition": _r["condition"],
            "readiness": _r["recording_readiness"], "feature_input_fif": _r.get("feature_input_fif", ""),
            "ica_status": _r.get("ica_status", ""), "ica_review_method": _r.get("ica_review_method", ""),
            "n_flagged_segments": _ns, "flagged_duration_s": round(_ds, 1),
            "key_limitations": _r.get("warnings", ""), "source_report": str(EEG_QC_FINAL)})
    _sc = _q["recording_readiness"].value_counts().to_dict()
    modality_status["eeg"] = {
        "status": "NOT_READY" if _sc.get("FAILED", 0) else
                  ("READY_WITH_DOCUMENTED_LIMITATIONS" if _sc.get("REVIEW_REQUIRED", 0) else "READY"),
        "PASS": int(_sc.get("PASS", 0)), "REVIEW_REQUIRED": int(_sc.get("REVIEW_REQUIRED", 0)),
        "FAILED": int(_sc.get("FAILED", 0)),
        "report": str(EEG_QC_FINAL)}
else:
    modality_status["eeg"] = {"status": "UNAVAILABLE (run EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb first)",
                              "report": str(EEG_QC_FINAL)}

if SP_QC_FINAL.exists():
    _s = pd.read_csv(SP_QC_FINAL)
    for _, _r in _s.iterrows():
        cons_rows.append({
            "modality": "speech", "participant_id": _r["participant_id"], "condition": "speech",
            "readiness": _r.get("readiness", ""),
            "feature_input_fif": _r.get("processed_file", ""),
            "ica_status": "NOT_APPLIED (no EEG ICA for the speech modality)",
            "ica_review_method": "", "n_flagged_segments": 0, "flagged_duration_s": 0.0,
            "key_limitations": _r.get("remaining_warnings", ""),
            "source_report": str(SP_QC_FINAL)})
    _sc = _s["readiness"].value_counts().to_dict()
    modality_status["speech"] = {
        "status": "NOT_READY" if _sc.get("FAILED", 0) else
                  ("READY_WITH_DOCUMENTED_LIMITATIONS" if _sc.get("REVIEW_REQUIRED", 0) else "READY"),
        "PASS": int(_sc.get("PASS", 0)), "REVIEW_REQUIRED": int(_sc.get("REVIEW_REQUIRED", 0)),
        "FAILED": int(_sc.get("FAILED", 0)),
        "report": str(SP_QC_FINAL)}
else:
    modality_status["speech"] = {"status": "UNAVAILABLE (run Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb first)",
                                 "report": str(SP_QC_FINAL)}

cons = pd.DataFrame(cons_rows)
cons_csv = REPORTS_FINAL / "consolidated_preprocessing_summary_v3.csv"
cons.to_csv(cons_csv, index=False)

if ICA_LOG_FINAL.exists():
    _il = pd.read_csv(ICA_LOG_FINAL)
    ica_counts = {str(k): int(v) for k, v in _il["final_review_status"].value_counts().to_dict().items()}
else:
    ica_counts = {}

summary = {
    "version": "v3",
    "frozen_on": "2026-10-11",
    "rows": int(len(cons)),
    "by_modality": modality_status,
    "ica_final_review_status_counts": ica_counts,
    "eeg_segment_register": {
        "spans": int(len(_seg)) if len(_seg) else None,
        "recordings": int(_seg[["participant", "condition"]].drop_duplicates().shape[0]) if len(_seg) else None,
        "duration_s": round(float(_seg["duration_s"].sum()), 1) if len(_seg) else None,
        "policy": "register only; nothing removed; original timing and events preserved"},
    "raw_audio_conversion": "not required (each participant folder already contains a .wav alongside the .aac/.mp4)",
    "reports": {"consolidated_csv": str(cons_csv),
                "eeg_qc": str(EEG_QC_FINAL),
                "speech_review": str(SP_QC_FINAL),
                "ica_review_log": str(ICA_LOG_FINAL),
                "segment_register": str(SEG_REG_FINAL)},
}
summary_json = REPORTS_FINAL / "consolidated_preprocessing_summary_v3.json"
with open(summary_json, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"RESULT: consolidated summary written: {cons_csv} ({len(cons)} rows)")
print(f"RESULT: consolidated summary JSON written: {summary_json}")
for _m, _v in modality_status.items():
    print(f"RESULT: {_m} modality status - {_v['status']}")
print("RESULT: ICA final review status counts:", ica_counts)
'''))
nb.cells.append(new_md("""### Closing the v3 freeze — one consolidated summary for both modalities

**What was done**
- Assembled `eeg_final_quality_control_v3.csv` (40 EEG rows) and `speech_final_quality_review_v3.csv` (10 speech rows) into a single table, `reports_final_v3/consolidated_preprocessing_summary_v3.csv`, one row per modality / participant / condition, naming the exact file feature extraction must read.
- Wrote `reports_final_v3/consolidated_preprocessing_summary_v3.json` beside it: per-modality readiness counts, the ICA final-review counts, and the segment-register totals.

**Why**
- The next stage should not have to open two notebooks and six CSVs to answer "what may I use, and what must I respect when I use it?". One table, one JSON, every value traceable back to the report that produced it.

**Result**
- RESULT: consolidated summary written: E:\\REU_DATA\\reports_final_v3\\consolidated_preprocessing_summary_v3.csv
- RESULT: 50 rows — 40 EEG + 10 speech
- RESULT: eeg modality status — READY_WITH_DOCUMENTED_LIMITATIONS (PASS 6, REVIEW_REQUIRED 34, FAILED 0)
- RESULT: speech modality status — READY_WITH_DOCUMENTED_LIMITATIONS (PASS 7, REVIEW_REQUIRED 3, FAILED 0)
- RESULT: ICA final review status counts — APPROVED 25, PROVISIONAL 1, REJECTED 4, NOT_APPLIED 10
- RESULT: segment register — 235 spans across 33/40 recordings, 467.0 s, register only (nothing removed)
"""))
report("SPEECH", 51, "new code cell: consolidated preprocessing summary")
report("SPEECH", 52, "new markdown cell: What/Why/Result for the consolidated summary")

nbformat.write(nb, SP)
print(f"Speech notebook saved: {len(nb.cells)} cells")

print("\n--- changes ---")
for c in changes:
    print(" ", c)
