"""Build the provisional ICA review record (v1) for the 25 HUMAN_SIGNOFF_PENDING recordings.

Read-only against every input. Writes ONLY into E:\\REU_DATA\\provisional_review_v1\\.
Does not create ica_signoff_v1.csv, does not touch raw data, ICA files, frozen figures,
the v1 audit, or any sign-off packet.

Outputs
  provisional_decision_report_v1.csv   25 rows, one per pending recording
  hold_component_metrics_v1.csv        per-component rows for the 7 HOLD recordings
  hold_case_metrics_v1.csv             per-HOLD-recording roll-up used by hold_case_evidence_v1.md
  verification_v1.csv                  recording-ID / component-index cross-source checks
  build_log_v1.txt                     run log + source hashes
"""

import ast
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"E:\REU_DATA"
OUT = os.path.join(ROOT, "provisional_review_v1")

AUDIT = os.path.join(ROOT, "audit_finalization_v1", "eeg", "ica_audit_v1.csv")
MANIFEST = os.path.join(ROOT, "EEG processed", "quality_control",
                        "ica_signoff_packet_v2", "packet_manifest_v2.csv")
EV_INDEX = os.path.join(ROOT, "component_evidence_v1", "component_evidence_index_v1.csv")
EV_METRICS = os.path.join(ROOT, "component_evidence_v1", "component_metrics_v1.csv")
MAPS_DIR = os.path.join(ROOT, "EEG processed", "eeg", "figures_v2", "ica")
TS_DIR = os.path.join(ROOT, "component_evidence_v1", "timeseries")
SP_DIR = os.path.join(ROOT, "component_evidence_v1", "spectra")
NPZ_DIR = os.path.join(ROOT, "component_evidence_v1", "arrays")
PACKET_DIR = os.path.join(ROOT, "EEG processed", "quality_control", "ica_signoff_packet_v2_review")
EEG_DIR = os.path.join(ROOT, "EEG processed", "eeg")

# --- reviewer's provisional instructions (verbatim from the review message) -------------
HOLD = ["P02_meditation", "P08_calm", "P08_maths", "P08_meditation",
        "P10_calm", "P10_maths", "P10_meditation"]
NEAR_GUARD = {"P02_calm": 28.60, "P06_maths": 29.43, "P09_maths": 25.24}
ALPHA_GUARD_PCT = 30.0
NOT_AVAILABLE = "NOT AVAILABLE"

log_lines = []


def log(msg):
    line = str(msg)
    log_lines.append(line)
    print(line)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_list(x):
    if isinstance(x, list):
        return [int(v) for v in x]
    if x is None or (isinstance(x, float) and np.isnan(x)) or str(x).strip() == "":
        return None
    return [int(v) for v in ast.literal_eval(str(x))]


def fmt(v, nd=3):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return NOT_AVAILABLE
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


# ---------------------------------------------------------------- load sources
log("=== provisional_review_v1 build ===")
log("built_utc=" + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
for p in (AUDIT, MANIFEST, EV_INDEX, EV_METRICS):
    log(f"source sha256 {os.path.basename(p)} {sha256(p)}")

audit = pd.read_csv(AUDIT)
man = pd.read_csv(MANIFEST)
evidx = pd.read_csv(EV_INDEX)
evmet = pd.read_csv(EV_METRICS)

pending = man[man.audit_disposition == "HUMAN_SIGNOFF_PENDING"].copy()
excluded = man[man.audit_disposition == "EXCLUDED"].copy()
pending["recording"] = pending.participant + "_" + pending.condition
pending_ids = sorted(pending.recording.tolist())
log(f"pending rows={len(pending_ids)} excluded rows={len(excluded)}")
assert len(pending_ids) == 25, pending_ids

approve_ids = [r for r in pending_ids if r not in HOLD]
log(f"HOLD={len(HOLD)} APPROVE={len(approve_ids)}")
assert len(approve_ids) == 18 and len(HOLD) == 7
assert sorted(HOLD) == sorted([h for h in HOLD if h in pending_ids]), "HOLD id not in pending set"

# ---------------------------------------------------------------- per-recording build
rows = []
verif = []
hold_comp_rows = []
hold_rollup = []

for rec in pending_ids:
    part, cond = rec.split("_")
    mrow = pending[pending.recording == rec].iloc[0]
    arow = audit[(audit.participant == part) & (audit.condition == cond)]
    irow = evidx[evidx.recording == rec]
    mrows = evmet[evmet.recording == rec]

    srcs = {}
    srcs["packet_manifest_v2.csv"] = parse_list(mrow.components_removed)
    srcs["ica_audit_v1.csv"] = parse_list(arow.components_removed.iloc[0]) if len(arow) else None
    srcs["component_evidence_index_v1.csv"] = parse_list(irow.components_removed.iloc[0]) if len(irow) else None
    rep_p = os.path.join(EEG_DIR, part, cond, "ica_report.json")
    rep = json.load(open(rep_p, encoding="utf-8")) if os.path.exists(rep_p) else None
    srcs["ica_report.json"] = parse_list(rep.get("components_removed")) if rep else None
    npz_p = os.path.join(NPZ_DIR, f"{rec}_evidence.npz")
    z = np.load(npz_p, allow_pickle=True) if os.path.exists(npz_p) else None
    srcs["evidence_npz.removed_components"] = [int(v) for v in z["removed_components"]] if z else None
    flag = sorted(int(c) for c in mrows[mrows.removed_flag == True].component) if len(mrows) else None
    srcs["component_metrics_v1.csv.removed_flag"] = flag

    agree = len({tuple(v) for v in srcs.values() if v is not None}) == 1
    missing = [k for k, v in srcs.items() if v is None]
    verif.append({
        "recording_id": rec,
        "sources_checked": len(srcs),
        "components_removed_agree": "PASS" if agree else "FAIL",
        "components_removed": str(srcs["packet_manifest_v2.csv"]),
        "missing_sources": "; ".join(missing) if missing else "none",
        "evidence_npz_present": "True" if z is not None else "False",
        "timeseries_png_present": os.path.exists(os.path.join(TS_DIR, f"{rec}_component_timecourses.png")),
        "spectra_png_present": os.path.exists(os.path.join(SP_DIR, f"{rec}_component_spectra.png")),
        "component_map_png_present": os.path.exists(os.path.join(MAPS_DIR, f"{rec}_components.png")),
        "packet_page_present": os.path.exists(os.path.join(PACKET_DIR, f"{rec}.html")),
        "ica_report_json_present": os.path.exists(rep_p),
        "n_components_in_metrics": int(len(mrows)),
    })
    removed = srcs["packet_manifest_v2.csv"]

    # component-level metrics for the removed indices
    rem_rows = mrows[mrows.component.isin(removed)].sort_values("component") if removed else mrows.iloc[0:0]
    rem_desc = []
    for r in rem_rows.itertuples():
        rem_desc.append(
            f"IC{int(r.component)}: eog_corr={fmt(r.eog_corr)}, "
            f"muscle_frac={fmt(r.muscle_frac)}, frontal_weight={fmt(r.frontal_weight)}, "
            f"alpha_8_12_frac={fmt(r.frac_power_8_12hz, 4)}")

    comp_max = float(mrows.eog_corr.abs().max()) if len(mrows) else None
    rem_max = float(rem_rows.eog_corr.abs().max()) if len(rem_rows) else None

    alpha_loss = float(mrow.alpha_loss_pct)
    var_red = float(mrow.variance_reduction_pct)
    near = (mrow.near_guard_flag == "YES") or (rec in NEAR_GUARD)

    warnings = []
    if rec in NEAR_GUARD:
        warnings.append(f"near-guard alpha loss {NEAR_GUARD[rec]:.2f}% (25% < loss <= 30%, guard = {ALPHA_GUARD_PCT:.0f}%)")
    elif near:
        warnings.append(f"near-guard alpha loss {alpha_loss:.2f}% (25% < loss <= 30%, guard = {ALPHA_GUARD_PCT:.0f}%)")
    if mrow.alpha_guard != "PASS":
        warnings.append(f"alpha guard {mrow.alpha_guard}")
    if mrow.eog_guard != "PASS":
        warnings.append(f"eog guard {mrow.eog_guard}")
    if mrow.frontal_guard != "PASS":
        warnings.append(f"frontal guard {mrow.frontal_guard}")
    if mrow.variance_guard != "PASS":
        warnings.append(f"variance guard {mrow.variance_guard}")
    if arow.crosscheck_var_vs_report.iloc[0] != "OK" or arow.crosscheck_alpha_vs_report.iloc[0] != "OK":
        warnings.append("audit vs ica_report.json cross-check NOT OK")
    if comp_max is not None and abs(comp_max - float(arow.eog_corr_max_recomputed.iloc[0])) > 0.0015:
        warnings.append(
            f"two different EOG metrics on this recording: audit channel-level "
            f"max abs r={float(arow.eog_corr_max_recomputed.iloc[0]):.3f} vs component-level "
            f"max abs r={comp_max:.3f} (different definitions, see report section 8)")
    if rec in HOLD:
        warnings.append("HOLD FOR REVIEW - excluded from final ICA sign-off until component-level evidence is resolved")

    rec_w = {
        "recording_id": rec,
        "participant": part,
        "condition": cond,
        "audit_disposition": mrow.audit_disposition,
        "provisional_recommendation": "HOLD FOR REVIEW" if rec in HOLD else "APPROVED — PROVISIONAL",
        "components_removed_indices": str(removed),
        "eog_corr_removed_components": " | ".join(rem_desc) if rem_desc else NOT_AVAILABLE,
        "eog_corr_max_component_level": fmt(comp_max),
        "eog_corr_max_removed_component_level": fmt(rem_max),
        "eog_corr_max_channel_level_audit": fmt(float(arow.eog_corr_max_recomputed.iloc[0])) if len(arow) else NOT_AVAILABLE,
        "frontal_weight_removal_level_audit": fmt(float(mrow.frontal_weight), 3),
        "frontal_weight_removed_components": " | ".join(
            f"IC{int(r.component)}={fmt(r.frontal_weight)}" for r in rem_rows.itertuples()) if len(rem_rows) else NOT_AVAILABLE,
        "muscle_frac_removed_components": " | ".join(
            f"IC{int(r.component)}={fmt(r.muscle_frac)}" for r in rem_rows.itertuples()) if len(rem_rows) else NOT_AVAILABLE,
        "muscle_frac_max_component_level": fmt(float(mrows.muscle_frac.max())) if len(mrows) else NOT_AVAILABLE,
        "removed_hf_fraction_manifest": fmt(float(mrow.removed_hf_fraction)),
        "alpha_loss_pct": fmt(alpha_loss, 2),
        "alpha_change_pct": fmt(float(mrow.alpha_change_pct), 2),
        "variance_reduction_pct": fmt(var_red, 2),
        "alpha_guard": mrow.alpha_guard,
        "eog_guard": mrow.eog_guard,
        "frontal_guard": mrow.frontal_guard,
        "variance_guard": mrow.variance_guard,
        "near_guard_flag": mrow.near_guard_flag,
        "review_table_source": "NOT AVAILABLE (review table not present in repo); APPROVE set derived as 25 pending minus the 7 HOLD ids listed in the review message",
        "warnings_unresolved": "; ".join(warnings) if warnings else "none",
        "evidence_timecourse_png": irow.timecourse_png.iloc[0] if len(irow) else NOT_AVAILABLE,
        "evidence_spectra_png": irow.spectra_png.iloc[0] if len(irow) else NOT_AVAILABLE,
        "evidence_component_map_png": arow.component_map_file.iloc[0] if len(arow) else NOT_AVAILABLE,
        "evidence_npz": irow.evidence_npz.iloc[0] if len(irow) else NOT_AVAILABLE,
        "evidence_packet_page": os.path.join(PACKET_DIR, f"{rec}.html"),
        "evidence_ica_report_json": rep_p,
    }
    rows.append(rec_w)

    # ---------------- HOLD-only deeper evidence from the npz
    if rec in HOLD:
        if z is None:
            hold_rollup.append({"recording_id": rec, "npz": "NOT AVAILABLE"})
        else:
            t = z["t_s"]
            src = z["sources_window"].astype(float)
            eog = z["eog_proxy_uv"].astype(float)
            post = z["posterior_uv"].astype(float)
            freqs = z["freqs_hz"]
            psd_src = z["psd_sources"]
            band = (freqs >= 8) & (freqs <= 12)
            tot_band = (freqs >= 1) & (freqs <= 45)
            eog_c = z["eog_corr"].astype(float)
            mus = z["muscle_frac"].astype(float)
            fw = z["frontal_weight"].astype(float)
            det = []
            for c in removed:
                s = src[c]
                r_eog = float(np.corrcoef(s, eog)[0, 1])
                r_post = float(np.corrcoef(s, post)[0, 1])
                a_frac = float(psd_src[c][band].sum() / max(psd_src[c][tot_band].sum(), 1e-20))
                det.append({
                    "component": int(c),
                    "eog_corr_full_metrics": float(eog_c[c]),
                    "corr_source_vs_eog_window": round(r_eog, 3),
                    "corr_source_vs_posterior_window": round(r_post, 3),
                    "muscle_frac": float(mus[c]),
                    "frontal_weight": float(fw[c]),
                    "alpha_band_share_of_source_psd": round(a_frac, 4),
                    "alpha_peak_hz": float(mrows[mrows.component == c].source_psd_alpha_peak_hz.iloc[0]),
                    "frac_power_1_4hz": float(mrows[mrows.component == c].frac_power_1_4hz.iloc[0]),
                    "frac_power_30_45hz": float(mrows[mrows.component == c].frac_power_30_45hz.iloc[0]),
                    "source_rms_a_u": float(mrows[mrows.component == c].source_rms_a_u.iloc[0]),
                })
                hold_comp_rows.append({
                    "recording_id": rec, "participant": part, "condition": cond,
                    "component": int(c), "removed_flag": True,
                    **{k: v for k, v in det[-1].items() if k != "component"},
                })
            ret = [c for c in range(20) if c not in removed]
            rem_a = float(sum(psd_src[c][band].sum() for c in removed))
            ret_a = float(sum(psd_src[c][band].sum() for c in ret))
            hold_rollup.append({
                "recording_id": rec,
                "components_removed": str(removed),
                "alpha_loss_pct": alpha_loss,
                "variance_reduction_pct": var_red,
                "eog_corr_max_component_level": round(float(np.abs(eog_c).max()), 3),
                "eog_corr_max_removed": round(float(np.abs(eog_c[removed]).max()), 3),
                "eog_corr_max_channel_level_audit": float(arow.eog_corr_max_recomputed.iloc[0]),
                "frontal_weight_removal_level_audit": float(mrow.frontal_weight),
                "muscle_frac_max_removed": round(float(max(d["muscle_frac"] for d in det)), 3),
                "max_alpha_share_removed": round(max(d["alpha_band_share_of_source_psd"] for d in det), 4),
                "removed_alpha_psd_sum": round(rem_a, 4),
                "retained_alpha_psd_sum": round(ret_a, 4),
                "removed_share_of_total_alpha_psd": round(rem_a / max(rem_a + ret_a, 1e-20), 4),
                "max_abs_corr_source_vs_eog": round(max(abs(d["corr_source_vs_eog_window"]) for d in det), 3),
                "max_abs_corr_source_vs_posterior": round(max(abs(d["corr_source_vs_posterior_window"]) for d in det), 3),
                "detail": " ; ".join(
                    f"IC{d['component']}(r_eog={d['corr_source_vs_eog_window']}, "
                    f"r_post={d['corr_source_vs_posterior_window']}, "
                    f"alpha_share={d['alpha_band_share_of_source_psd']}, "
                    f"fw={d['frontal_weight']}, muscle={d['muscle_frac']})" for d in det),
            })

# ---------------------------------------------------------------- exclusions / speech
excl_rows = []
for r in excluded.itertuples():
    excl_rows.append({
        "recording_id": f"{r.participant}_{r.condition}",
        "audit_disposition": r.audit_disposition,
        "components_removed": r.components_removed,
        "alpha_loss_pct": r.alpha_loss_pct,
        "variance_reduction_pct": r.variance_reduction_pct,
        "alpha_guard": r.alpha_guard,
        "variance_guard": r.variance_guard,
        "eog_guard": r.eog_guard,
        "frontal_guard": r.frontal_guard,
        "unchanged_by_this_pass": "YES",
    })

audit_speech = audit[audit.audit_ica_disposition == "NOT_APPLIED"]
speech_rows = [{
    "recording_id": f"{r.participant}_{r.condition}",
    "audit_disposition": r.audit_ica_disposition,
    "audit_reason": r.audit_reason,
    "feature_input_recommendation": r.feature_input_recommendation,
    "unchanged_by_this_pass": "YES",
} for r in audit_speech.itertuples()]

# ---------------------------------------------------------------- write outputs
def write_csv(name, recs):
    p = os.path.join(OUT, name)
    if not recs:
        raise ValueError(f"no rows for {name}")
    keys = list(recs[0].keys())
    for r in recs:
        for k in keys:
            r.setdefault(k, "")
    with open(p, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(recs)
    log(f"wrote {name} ({len(recs)} rows)")


write_csv("provisional_decision_report_v1.csv", rows)
write_csv("verification_v1.csv", verif)
if hold_comp_rows:
    write_csv("hold_component_metrics_v1.csv", hold_comp_rows)
if hold_rollup:
    write_csv("hold_case_metrics_v1.csv", hold_rollup)
write_csv("preserved_exclusions_v1.csv", excl_rows)
write_csv("preserved_speech_not_applied_v1.csv", speech_rows)

# integrity summary
n_pass = sum(1 for v in verif if v["components_removed_agree"] == "PASS")
log(f"component-index agreement: {n_pass}/{len(verif)} PASS")
bad = [v for v in verif if v["components_removed_agree"] != "PASS" or v["missing_sources"] != "none"]
log("rows with any source problem: " + (", ".join(v["recording_id"] for v in bad) if bad else "none"))
log("HOLD count in report: " + str(sum(1 for r in rows if r["provisional_recommendation"] == "HOLD FOR REVIEW")))
log("APPROVED count in report: " + str(sum(1 for r in rows if r["provisional_recommendation"] == "APPROVED — PROVISIONAL")))
log("near-guard rows: " + ", ".join(f"{k}={v}" for k, v in NEAR_GUARD.items()))
log("excluded rows preserved: " + str(len(excl_rows)))
log("speech NOT_APPLIED rows preserved: " + str(len(speech_rows)))

with open(os.path.join(OUT, "build_log_v1.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(log_lines) + "\n")

print("\n--- HOLD rollup ---")
for h in hold_rollup:
    print(json.dumps({k: v for k, v in h.items() if k != "detail"}, ensure_ascii=False))
    print("   ", h.get("detail", ""))
