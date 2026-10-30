# -*- coding: utf-8 -*-
"""Create two presentation figures:

1) 01_eeg_preprocessing_pipeline.png   - high-level arrow flow of the preprocessing steps
2) 02_overall_preprocessing_result.png - one composite figure averaged over all 40 recordings

Run:  python make_presentation_figures.py
The averaged statistics are cached in ppt_figures/_overall_stats.npz, so re-running
only redraws the figures unless you delete that cache file.
"""
from pathlib import Path
import gc

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MPath
import mne
import bioread
from scipy.signal import stft

mne.set_log_level("ERROR")

REPO = Path(r"E:/REU_DATA")
RAW_DIR = REPO
PROC_DIR = REPO / "processed" / "eeg"
OUT_DIR = REPO / "presentation_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE = OUT_DIR / "_overall_stats.npz"

CONDITIONS = {
    "01calm": "calm",
    "02meditation": "meditation",
    "03maths": "maths",
    "04speech": "speech",
}
SUFFIX_OF = {v: k for k, v in CONDITIONS.items()}
PARTICIPANTS = [f"P{i:02d}" for i in range(1, 11)]
CONDS = ["calm", "meditation", "maths", "speech"]

BANDS = {
    "Delta\n1-4 Hz": (1, 4),
    "Theta\n4-8 Hz": (4, 8),
    "Alpha\n8-13 Hz": (8, 13),
    "Beta\n13-30 Hz": (13, 30),
    "Gamma\n30-45 Hz": (30, 45),
}
SEG_S = 30          # seconds used for the averaged spectrogram
SPECT_CH = "Cz"


# =====================================================================================
# FIGURE 1 - high-level preprocessing flow (arrow diagram)
# =====================================================================================
def make_flowchart():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(50, 98.5, "EEG Preprocessing Pipeline - High-Level Overview",
            ha="center", va="top", fontsize=24, fontweight="bold", color="#0f172a")
    ax.text(50, 93.0, "P01-P10  ·  calm / meditation / maths / speech  ·  40 BIOPAC recordings  ·  "
                      "24 channels  ·  Fs = 1000 Hz",
            ha="center", va="top", fontsize=14, color="#475569")

    w, h = 27, 18
    xs = [16, 50, 84]
    ys = [77, 48, 19]

    steps = [
        # row 1
        dict(x=xs[0], y=ys[0], title="1. Raw data",
             lines=["BIOPAC .acq + .xlsx exports", "P01-P10, 4 conditions", "read-only, never modified"],
             fc="#dbeafe", ec="#1d4ed8"),
        dict(x=xs[1], y=ys[0], title="2. Dataset inspection",
             lines=["24 EEG channels (10-20)", "verify Fs = 1000 Hz, units (uV)", "no column / rate assumptions"],
             fc="#e0f2fe", ec="#0369a1"),
        dict(x=xs[2], y=ys[0], title="3. Quality check",
             lines=["NaN / Inf scan per channel", "flat (dead) electrode check", "candidate bad channels logged"],
             fc="#fef3c7", ec="#b45309"),
        # row 2
        dict(x=xs[0], y=ys[1], title="4. Band-pass filter",
             lines=["1-45 Hz zero-phase FIR", "removes DC baseline drift", "and high-frequency noise"],
             fc="#ffedd5", ec="#c2410c"),
        dict(x=xs[1], y=ys[1], title="5. 50 Hz notch filter",
             lines=["IIR notch, Q = 30", "applied only if line noise", "is detected in the PSD"],
             fc="#ffedd5", ec="#c2410c"),
        dict(x=xs[2], y=ys[1], title="6. Bad-channel handling",
             lines=["detection on filtered data", "interpolate clearly-bad only", "flag (never silently drop)"],
             fc="#fee2e2", ec="#b91c1c"),
        # row 3
        dict(x=xs[0], y=ys[2], title="7. Verify before / after",
             lines=["time-domain · PSD", "spectrogram · variance", "40 / 40 recordings checked"],
             fc="#dcfce7", ec="#15803d"),
        dict(x=xs[1], y=ys[2], title="8. Save outputs",
             lines=["cleaned .fif per recording", "preprocessing_report.json", "under processed/eeg/"],
             fc="#ede9fe", ec="#6d28d9"),
        dict(x=xs[2], y=ys[2], title="9. Analysis-ready data",
             lines=["P01-P10, 40 recordings", "PSD · band power · features", "raw data still untouched"],
             fc="#d1fae5", ec="#047857"),
    ]

    def draw_box(s):
        ax.add_patch(FancyBboxPatch((s["x"] - w / 2, s["y"] - h / 2), w, h,
                                    boxstyle="round,pad=0,rounding_size=1.5",
                                    linewidth=2.0, edgecolor=s["ec"], facecolor=s["fc"], zorder=2))
        ax.text(s["x"], s["y"] + h / 2 - 3.0, s["title"], ha="center", va="top",
                fontsize=15.5, fontweight="bold", color=s["ec"], zorder=3)
        ax.text(s["x"], s["y"] + h / 2 - 7.4, "\n".join(s["lines"]), ha="center", va="top",
                fontsize=11, color="#1f2937", zorder=3, linespacing=1.3)

    def straight_arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.42,head_length=0.85",
                                    color="#334155", lw=2.4, shrinkA=0, shrinkB=0,
                                    mutation_scale=22), zorder=4)

    def wrap_arrow(x_start, y_start, y_mid, x_end, y_end):
        verts = [(x_start, y_start), (x_start, y_mid), (x_end, y_mid), (x_end, y_end)]
        codes = [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.LINETO]
        ax.add_patch(FancyArrowPatch(path=MPath(verts, codes), arrowstyle="-|>",
                                     color="#334155", lw=2.4, mutation_scale=22,
                                     shrinkA=0, shrinkB=0, zorder=4))

    for s in steps:
        draw_box(s)

    gap = w / 2 + 1.0
    for row in (0, 1, 2):
        y = ys[row]
        for x0, x1 in zip(xs[:-1], xs[1:]):
            straight_arrow(x0 + gap, y, x1 - gap, y)

    mids = [(ys[0] + ys[1]) / 2, (ys[1] + ys[2]) / 2]
    wrap_arrow(xs[2], ys[0] - h / 2 - 0.5, mids[0], xs[0], ys[1] + h / 2 + 0.8)
    wrap_arrow(xs[2], ys[1] - h / 2 - 0.5, mids[1], xs[0], ys[2] + h / 2 + 0.8)
    for m in mids:
        ax.text((xs[0] + xs[2]) / 2, m + 0.6, "next", ha="center", va="bottom",
                fontsize=10.5, style="italic", color="#64748b")

    ax.text(50, 4.0,
            "Safety rule: raw .acq / .xlsx stay read-only  ·  every result written to E:/REU_DATA/processed/eeg/  ·  "
            "pipeline: EEG_Dataset_Analysis_and_Preprocessing.ipynb",
            ha="center", va="center", fontsize=11.5, color="#64748b",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f1f5f9", edgecolor="#cbd5e1"))

    out = OUT_DIR / "01_eeg_preprocessing_pipeline.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("saved:", out)


# =====================================================================================
# FIGURE 2 - one composite figure: average result over all 40 recordings
# =====================================================================================
def band_db(psds, freqs, fmin, fmax):
    m = (freqs >= fmin) & (freqs <= fmax)
    return float(10 * np.log10(psds[:, m].mean() + 1e-20))


def compute_stats():
    """Average PSD / spectrogram / band power / variance over all 40 recordings."""
    psd_b, psd_a = [], []
    bands_b, bands_a = [], []
    std_b, std_a = [], []
    sg_b_sum = sg_a_sum = None
    freqs = ch_names = t_s = f_s = None
    n_rec = 0
    band_names = list(BANDS.keys())

    for pid in PARTICIPANTS:
        i = int(pid[1:])
        acq_dir = RAW_DIR / pid / f"{i:02d}_eeg" / "acq"
        for cond in CONDS:
            acq_matches = list(acq_dir.glob(f"{pid}_*{SUFFIX_OF[cond]}.acq"))
            fif_path = PROC_DIR / pid / cond / f"{pid}_{cond}_eeg.fif"
            if not acq_matches or not fif_path.exists():
                print("  skip", pid, cond)
                continue

            df = bioread.read_file(str(acq_matches[0]))
            fs = int(df.samples_per_second)
            ch_names = [c.name for c in df.channels]
            data = np.vstack([c.data for c in df.channels]) * 1e-6
            raw_b = mne.io.RawArray(data, mne.create_info(ch_names=ch_names, sfreq=fs,
                                                          ch_types="eeg"), verbose=False)
            del df, data
            raw_a = mne.io.read_raw_fif(fif_path, verbose=False)

            P_b, freqs = raw_b.compute_psd(fmin=1, fmax=80, verbose=False).get_data(return_freqs=True)
            P_a, _ = raw_a.compute_psd(fmin=1, fmax=80, verbose=False).get_data(return_freqs=True)
            psd_b.append(10 * np.log10(P_b.mean(axis=0) + 1e-20))
            psd_a.append(10 * np.log10(P_a.mean(axis=0) + 1e-20))

            bands_b.append([band_db(P_b, freqs, lo, hi) for lo, hi in BANDS.values()])
            bands_a.append([band_db(P_a, freqs, lo, hi) for lo, hi in BANDS.values()])

            std_b.append(raw_b.get_data().std(axis=1) * 1e6)
            std_a.append(raw_a.get_data().std(axis=1) * 1e6)

            n = SEG_S * fs
            assert raw_b.n_times >= n, f"{pid} {cond} shorter than {SEG_S}s"
            xb = raw_b.get_data(picks=SPECT_CH)[0][:n] * 1e6
            xa = raw_a.get_data(picks=SPECT_CH)[0][:n] * 1e6
            f_s, t_s, Zb = stft(xb, fs=fs, nperseg=2048, noverlap=1024)
            _, _, Za = stft(xa, fs=fs, nperseg=2048, noverlap=1024)
            db_b = 10 * np.log10(np.abs(Zb) + 1e-12)
            db_a = 10 * np.log10(np.abs(Za) + 1e-12)
            sg_b_sum = db_b if sg_b_sum is None else sg_b_sum + db_b
            sg_a_sum = db_a if sg_a_sum is None else sg_a_sum + db_a

            n_rec += 1
            print(f"  {n_rec:2d}/40 {pid} {cond}")
            del raw_b, raw_a
            gc.collect()

    stats = dict(
        n_rec=n_rec, freqs=freqs,
        psd_b=np.array(psd_b), psd_a=np.array(psd_a),
        band_names=np.array(band_names),
        bands_b=np.array(bands_b), bands_a=np.array(bands_a),
        ch_names=np.array(ch_names),
        std_b=np.array(std_b), std_a=np.array(std_a),
        sg_f=f_s, sg_t=t_s,
        sg_b=sg_b_sum / n_rec, sg_a=sg_a_sum / n_rec,
    )
    np.savez(CACHE, **stats)
    print("cache written:", CACHE)
    return stats


def load_stats():
    if CACHE.exists():
        d = dict(np.load(CACHE, allow_pickle=True))
        print(f"cache loaded: {CACHE}  (n_rec = {int(d['n_rec'])})")
        return d
    return compute_stats()


def make_overall_result():
    d = load_stats()
    n_rec = int(d["n_rec"])
    freqs = d["freqs"]
    psd_b, psd_a = d["psd_b"], d["psd_a"]
    band_names = [str(b) for b in d["band_names"]]
    ch_names = [str(c) for c in d["ch_names"]]

    fig = plt.figure(figsize=(16, 12.5), dpi=200)
    gs = fig.add_gridspec(nrows=3, ncols=2, height_ratios=[1.0, 1.05, 1.05],
                          hspace=0.45, wspace=0.20,
                          left=0.06, right=0.97, top=0.895, bottom=0.06)

    # ---- A: averaged PSD -------------------------------------------------------------
    ax = fig.add_subplot(gs[0, :])
    m_b, s_b = psd_b.mean(axis=0), psd_b.std(axis=0)
    m_a, s_a = psd_a.mean(axis=0), psd_a.std(axis=0)
    ax.plot(freqs, m_b, color="gray", lw=2.0, label=f"Raw - before (n={n_rec})")
    ax.fill_between(freqs, m_b - s_b, m_b + s_b, color="gray", alpha=0.22)
    ax.plot(freqs, m_a, color="C0", lw=1.8, label=f"Cleaned - after (n={n_rec})")
    ax.fill_between(freqs, m_a - s_a, m_a + s_a, color="C0", alpha=0.22)
    ax.axvline(50, color="r", ls="--", alpha=0.5, label="50 Hz mains")
    i50 = int(np.argmin(np.abs(freqs - 50)))
    ax.annotate("50 Hz line noise removed",
                xy=(freqs[i50], m_a[i50]), xytext=(57, -150),
                arrowprops=dict(arrowstyle="->", color="#334155", lw=1.4),
                fontsize=11, color="#1f2937")
    i72 = int(np.argmin(np.abs(freqs - 72)))
    ax.annotate("low-pass at 45 Hz\n(noise floor about -160 dB)", xy=(freqs[i72], m_a[i72]),
                xytext=(64, -142),
                arrowprops=dict(arrowstyle="->", color="#334155", lw=1.4),
                fontsize=11, color="#1f2937")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (dB)")
    ax.set_title("A. Averaged PSD across all recordings (mean over 24 channels, band = SD across recordings)",
                 fontsize=13.5, fontweight="bold", loc="left")
    ax.set_xlim(1, 80)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=11, framealpha=0.9)

    # ---- B / C: averaged spectrograms ------------------------------------------------
    vmax = float(np.percentile(np.concatenate([d["sg_b"].ravel(), d["sg_a"].ravel()]), 99))
    vmin = vmax - 75
    for col, (img, txt) in enumerate([
        (d["sg_b"], f"B. Averaged spectrogram BEFORE  (50 Hz line + low-frequency drift)"),
        (d["sg_a"], f"C. Averaged spectrogram AFTER  (1-45 Hz band, notch applied)"),
    ]):
        axs = fig.add_subplot(gs[1, col])
        im = axs.pcolormesh(d["sg_t"], d["sg_f"], img, shading="gouraud", cmap="magma",
                            vmin=vmin, vmax=vmax)
        axs.set_title(txt, fontsize=13, fontweight="bold", loc="left")
        axs.set_ylabel("Frequency (Hz)")
        axs.set_xlabel(f"Time (s) - first {SEG_S} s, channel {SPECT_CH}")
        axs.set_ylim(0, 80)
        fig.colorbar(im, ax=axs, label="dB", fraction=0.046, pad=0.02)

    width = 0.38

    # ---- D: band power before vs after -----------------------------------------------
    ax = fig.add_subplot(gs[2, 0])
    x = np.arange(len(band_names))
    ax.bar(x - width / 2, d["bands_b"].mean(axis=0), width, yerr=d["bands_b"].std(axis=0),
           capsize=3, color="gray", alpha=0.85, label="Raw - before")
    ax.bar(x + width / 2, d["bands_a"].mean(axis=0), width, yerr=d["bands_a"].std(axis=0),
           capsize=3, color="C0", alpha=0.9, label="Cleaned - after")
    ax.set_xticks(x)
    ax.set_xticklabels(band_names, fontsize=10.5)
    ax.set_ylabel("Mean band power (dB)")
    ax.set_title("D. Band power preserved after cleaning (before ≈ after, error = SD)",
                 fontsize=13, fontweight="bold", loc="left")
    ax.set_ylim(d["bands_b"].min() - 12, 20)
    ax.set_yticks([-120, -100, -80, -60, -40, -20, 0])
    ax.legend(fontsize=10.5, loc="upper center", ncol=2, framealpha=0.9)
    ax.grid(True, axis="y", alpha=0.3)

    # ---- E: per-channel std before vs after ------------------------------------------
    ax = fig.add_subplot(gs[2, 1])
    mb = d["std_b"].mean(axis=0)
    ma = d["std_a"].mean(axis=0)
    x = np.arange(len(ch_names))
    ax.bar(x - width / 2, mb, width, color="gray", alpha=0.85, label="Raw - before")
    ax.bar(x + width / 2, ma, width, color="C0", alpha=0.9, label="Cleaned - after")
    ax.set_yscale("log")
    ax.set_ylim(4, 3000)
    ax.set_xticks(x)
    ax.set_xticklabels(ch_names, rotation=60, ha="right", fontsize=9)
    ax.set_ylabel("Standard deviation (µV, log scale)")
    red = (1 - ma.mean() / mb.mean()) * 100
    ax.set_title("E. Per-channel variability, averaged over 40 recordings",
                 fontsize=13, fontweight="bold", loc="left")
    ax.legend(fontsize=10.5, loc="upper right", framealpha=0.9)
    ax.grid(True, axis="y", alpha=0.3, which="both")
    ax.text(0.02, 0.95, f"Mean variance reduction: {red:.1f}%",
            transform=ax.transAxes, ha="left", va="top", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.85))

    fig.suptitle("Overall EEG preprocessing result - P01 to P10, 40 recordings "
                 "(calm · meditation · maths · speech)",
                 fontsize=19, fontweight="bold", y=0.975)
    fig.text(0.5, 0.928,
             "raw = before filtering   ·   cleaned = 1-45 Hz band-pass + 50 Hz notch   ·   "
             "every value averaged over all 40 recordings",
             ha="center", fontsize=13, color="#475569")

    out = OUT_DIR / "02_overall_preprocessing_result.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("saved:", out)
    print(f"recordings used: {n_rec}; mean variance reduction: {red:.1f}%")


if __name__ == "__main__":
    make_flowchart()
    make_overall_result()
    print("done ->", OUT_DIR)
