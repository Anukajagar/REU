"""Build before/after ICA evidence figures for all 30 ICA recordings (v1).

Read-only against every existing artifact: loads the SAVED cleaned (*_eeg.fif) and
ICA (*_eeg_ica.fif) files, computes waveform/PSD comparisons, and writes one new
PNG per recording plus an index CSV into
E:\\REU_DATA\\signoff_finalization_v2\\beforeafter_evidence_v1\\.

This does NOT refit ICA, does NOT modify any .fif, and does NOT regenerate any
pre-existing figure. Existing pilot before/after figures are left untouched; this
pass adds consistent coverage for recordings that never had one (26 of 30).

Window rule (fixed, never hand-picked): the MIDDLE 10 seconds of each recording.
Recomputed metrics are cross-checked against the stored ica_report.json values.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from scipy.signal import welch

ROOT = Path(r"E:\REU_DATA")
OUT_DIR = ROOT / "signoff_finalization_v2" / "beforeafter_evidence_v1"
PACKET = ROOT / "EEG processed" / "quality_control" / "ica_signoff_packet_v2" / "packet_manifest_v2.csv"
EEG_ROOT = ROOT / "EEG processed" / "eeg"

WINDOW_SEC = 10.0
FIG_DPI = 110
ALPHA_BAND = (8.0, 12.0)
PLOT_BAND = (1.0, 45.0)
POSTERIOR = ["O1", "Oz", "O2"]
EOG_PROXY = ["Fp1", "Fpz", "Fp2"]
WAVE_CHANNELS = ["Fp1", "F7", "Cz", "Pz", "O1"]


def band_power(freqs: np.ndarray, psd: np.ndarray, band) -> float:
    mask = (freqs >= band[0]) & (freqs <= band[1])
    return float(np.trapezoid(psd[mask], freqs[mask]))


def load_pair(pid: str, cond: str):
    cleaned = EEG_ROOT / pid / cond / f"{pid}_{cond}_eeg.fif"
    ica_fif = EEG_ROOT / pid / cond / f"{pid}_{cond}_eeg_ica.fif"
    report = EEG_ROOT / pid / cond / "ica_report.json"
    for p in (cleaned, ica_fif, report):
        if not p.exists():
            raise FileNotFoundError(p)
    raw_b = mne.io.read_raw_fif(cleaned, preload=True, verbose=False)
    raw_a = mne.io.read_raw_fif(ica_fif, preload=True, verbose=False)
    raw_b.pick("eeg")
    raw_a.pick("eeg")
    return raw_b, raw_a, json.loads(report.read_text(encoding="utf-8")), cleaned, ica_fif


def build_one(pid: str, cond: str) -> dict:
    rid = f"{pid}_{cond}"
    out_png = OUT_DIR / f"{rid}_beforeafter.png"
    if out_png.exists():  # resume support: never overwrite
        return {"recording_id": rid, "status": "SKIPPED_EXISTS", "figure": str(out_png)}

    t0 = time.time()
    raw_b, raw_a, report, cleaned, ica_fif = load_pair(pid, cond)
    assert raw_b.ch_names == raw_a.ch_names, f"{rid}: channel mismatch"
    assert raw_b.n_times == raw_a.n_times, f"{rid}: length mismatch"

    sfreq = raw_b.info["sfreq"]
    n = raw_b.n_times
    win_samp = int(WINDOW_SEC * sfreq)
    start = (n - win_samp) // 2
    sl = slice(start, start + win_samp)

    data_b = raw_b.get_data() * 1e6  # V -> uV
    data_a = raw_a.get_data() * 1e6
    removed = data_b - data_a
    chans = raw_b.ch_names

    # ---- recomputed metrics (full recording) ----
    f_b, psd_b = welch(data_b, fs=sfreq, nperseg=4096, axis=1)
    f_a, psd_a = welch(data_a, fs=sfreq, nperseg=4096, axis=1)
    mean_b = psd_b.mean(axis=0)
    mean_a = psd_a.mean(axis=0)

    post_idx = [chans.index(c) for c in POSTERIOR if c in chans]
    eog_idx = [chans.index(c) for c in EOG_PROXY if c in chans]
    post_psd_b = psd_b[post_idx].mean(axis=0)
    post_psd_a = psd_a[post_idx].mean(axis=0)
    alpha_b = band_power(f_b, post_psd_b, ALPHA_BAND)
    alpha_a = band_power(f_a, post_psd_a, ALPHA_BAND)
    alpha_change_re = 100.0 * (alpha_a - alpha_b) / alpha_b
    var_b = data_b.var(axis=1).mean()
    var_a = data_a.var(axis=1).mean()
    var_red_re = 100.0 * (1.0 - var_a / var_b)

    # report stores posterior_alpha_change_pct as a CHANGE (negative = alpha loss)
    alpha_rep = report.get("posterior_alpha_change_pct")
    var_rep = report.get("variance_reduction_pct")
    if alpha_rep is None:
        alpha_x = "NO_REPORT_VALUE"
    elif abs(alpha_change_re - alpha_rep) <= 5.0:
        alpha_x = "OK_METHOD_TOLERANT"
    else:
        alpha_x = "OUTLIER_SEE_INDEX_NOTE"
    var_x = "OK" if var_rep is not None and abs(var_red_re - var_rep) <= 2.0 else "NOTE"

    # ---- figure ----
    t = np.arange(win_samp) / sfreq
    fig = plt.figure(figsize=(13, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[2.4, 1.2, 1.4], hspace=0.35)

    ax1 = fig.add_subplot(gs[0])
    for j, ch in enumerate(WAVE_CHANNELS):
        i = chans.index(ch)
        off = j * 600.0
        ax1.plot(t, data_b[i, sl] - off, color="0.55", lw=0.7, label="before ICA" if j == 0 else None)
        ax1.plot(t, data_a[i, sl] - off, color="#1f77b4", lw=0.7, label="after ICA" if j == 0 else None)
    ax1.set_yticks([-j * 600.0 for j in range(len(WAVE_CHANNELS))])
    ax1.set_yticklabels(WAVE_CHANNELS)
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("channel (offset 600 uV)")
    ax1.set_title(
        f"{rid} - waveform window: middle {WINDOW_SEC:.0f} s (fixed rule), grey = cleaned (pre-ICA-removal), blue = ICA output"
    )
    ax1.legend(loc="upper right")
    ax1.grid(alpha=0.3)

    ax2 = fig.add_subplot(gs[1])
    eog_trace = removed[eog_idx].mean(axis=0)[sl]
    post_trace = removed[post_idx].mean(axis=0)[sl]
    ax2.plot(t, eog_trace, color="#d62728", lw=0.9, label="EOG proxy (Fp1/Fpz/Fp2 mean)")
    ax2.plot(t, post_trace, color="#2ca02c", lw=0.9, label="posterior proxy (O1/Oz/O2 mean)")
    ax2.axhline(0, color="k", lw=0.5)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("removed activity (uV)")
    ax2.set_title("What ICA removed (cleaned - ICA output) in the same window")
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3)

    ax3 = fig.add_subplot(gs[2])
    ok_f = (f_b >= PLOT_BAND[0]) & (f_b <= PLOT_BAND[1])
    ax3.semilogy(f_b[ok_f], mean_b[ok_f], color="0.45", lw=1.2, label="all-channel mean, before")
    ax3.semilogy(f_b[ok_f], mean_a[ok_f], color="#1f77b4", lw=1.2, label="all-channel mean, after")
    ax3.semilogy(f_b[ok_f], post_psd_b[ok_f], color="0.45", lw=1.0, ls=":", label="posterior mean, before")
    ax3.semilogy(f_b[ok_f], post_psd_a[ok_f], color="#2ca02c", lw=1.0, ls=":", label="posterior mean, after")
    ax3.axvspan(*ALPHA_BAND, color="orange", alpha=0.15, label="alpha 8-12 Hz")
    ax3.set_xlim(*PLOT_BAND)
    ax3.set_xlabel("frequency (Hz)")
    ax3.set_ylabel("PSD (uV^2/Hz)")
    ax3.set_title(
        f"Full-recording PSD - posterior alpha change recomputed here {alpha_change_re:+.1f}% "
        f"(stored report {alpha_rep if alpha_rep is not None else float('nan'):+.1f}%), "
        f"variance reduction recomputed {var_red_re:.1f}% (report {var_rep if var_rep is not None else float('nan'):.1f}%)"
    )
    ax3.legend(loc="upper right", fontsize=8)
    ax3.grid(alpha=0.3, which="both")

    fig.suptitle(
        f"{rid} - ICA components removed: {report.get('components_removed')}  |  "
        "read-only comparison of saved files; no ICA refit, no file modified",
        fontsize=10,
        y=0.995,
    )
    fig.savefig(out_png, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)

    del raw_b, raw_a, data_b, data_a, removed, psd_b, psd_a
    return {
        "recording_id": rid,
        "status": "BUILT",
        "figure": str(out_png),
        "window_start_s": round(start / sfreq, 3),
        "window_end_s": round((start + win_samp) / sfreq, 3),
        "alpha_change_recomputed_pct": round(alpha_change_re, 2),
        "alpha_change_report_pct": alpha_rep,
        "alpha_diff_pp": round(alpha_change_re - alpha_rep, 2) if alpha_rep is not None else "",
        "alpha_crosscheck": alpha_x,
        "alpha_note": (
            "independent Welch method (nperseg=4096) on saved files; small differences vs the "
            "stored report are expected (estimator details differ); a large outlier means the "
            "two methods disagree on magnitude - the EXCLUDED/APPROVED status was set from the "
            "stored report, not from this figure"
            if alpha_x != "OK_METHOD_TOLERANT"
            else "independent Welch method agrees with stored report within 5 pp"
        ),
        "variance_reduction_recomputed_pct": round(var_red_re, 2),
        "variance_reduction_report_pct": var_rep,
        "variance_crosscheck": var_x,
        "cleaned_fif": str(cleaned),
        "ica_fif": str(ica_fif),
        "seconds": round(time.time() - t0, 1),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    packet = pd.read_csv(PACKET)
    assert len(packet) == 30
    index_path = OUT_DIR / "beforeafter_index_v1.csv"
    if index_path.exists():
        sys.exit(f"REFUSING TO OVERWRITE {index_path}")

    rows = []
    for _, p in packet.iterrows():
        rid = f"{p['participant']}_{p['condition']}"
        print(f"[{len(rows)+1:02d}/30] {rid} ...", flush=True)
        rows.append(build_one(p["participant"], p["condition"]))

    df = pd.DataFrame(rows)
    df["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    df.to_csv(index_path, index=False, encoding="utf-8")
    print(f"WROTE {index_path}")
    print("status counts:", df["status"].value_counts().to_dict())
    built = df[df["status"] == "BUILT"]
    if len(built):
        print("alpha crosscheck:", built["alpha_crosscheck"].value_counts().to_dict())
        print("variance crosscheck:", built["variance_crosscheck"].value_counts().to_dict())


if __name__ == "__main__":
    main()
