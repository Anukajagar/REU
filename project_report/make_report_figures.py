"""
Generate the high-resolution figures used by the REU project documentation report.

READ-ONLY with respect to the whole dataset: this script only *reads* CSV/JSON
artifacts produced by earlier pipeline passes and *writes* PNG files into
E:\\REU_DATA\\project_report\\figures\\.  No raw EEG, raw speech or original
dataset file is opened for writing anywhere.

Usage:  py make_report_figures.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = Path(r"E:\REU_DATA")
OUT = ROOT / "project_report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Shared design system (kept identical across every figure)
# ----------------------------------------------------------------------------
NAVY = "#16324F"
BLUE = "#2E6DA4"
STEEL = "#5B84B1"
TEAL = "#2A9D8F"
AMBER = "#E9A13B"
RED = "#C1443C"
GREY = "#6B7280"
LGREY = "#C9D2DD"
BG = "#FFFFFF"
PANEL = "#F4F7FA"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": "#8A97A6",
        "axes.linewidth": 0.9,
        "axes.grid": True,
        "grid.color": "#DCE3EB",
        "grid.linewidth": 0.7,
        "xtick.color": "#3A4653",
        "ytick.color": "#3A4653",
        "text.color": "#1B2733",
        "figure.facecolor": BG,
        "savefig.facecolor": BG,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.18,
    }
)

DEC_COLORS = {
    "APPROVED": TEAL,
    "REJECTED": RED,
    "NEEDS_REVIEW": AMBER,
    "PROVISIONAL": AMBER,
    "NOT_APPLIED": GREY,
}


def save(fig, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(f"  wrote {path.name}")
    return path


# ----------------------------------------------------------------------------
# Flowchart helpers
# ----------------------------------------------------------------------------
def fbox(
    ax,
    x,
    y,
    w,
    h,
    text,
    fc=PANEL,
    ec=NAVY,
    tc="#12212F",
    fs=8.4,
    weight="normal",
    lw=1.2,
    style="round,pad=0.02,rounding_size=0.03",
    align="center",
):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=style,
            linewidth=lw,
            edgecolor=ec,
            facecolor=fc,
            mutation_aspect=1.0,
        )
    )
    if align == "left":
        tx, ha = x + w * 0.035, "left"
    else:
        tx, ha = x + w / 2, "center"
    ax.text(
        tx,
        y + h / 2,
        text,
        ha=ha,
        va="center",
        fontsize=fs,
        color=tc,
        fontweight=weight,
        linespacing=1.35,
    )


def farrow(ax, p0, p1, color=NAVY, lw=1.4, style="-|>", shrink=0.0, rad=0.0, ls="-"):
    ax.add_patch(
        FancyArrowPatch(
            p0,
            p1,
            arrowstyle=style,
            mutation_scale=13,
            linewidth=lw,
            color=color,
            linestyle=ls,
            shrinkA=shrink,
            shrinkB=shrink,
            connectionstyle=f"arc3,rad={rad}",
            zorder=3,
        )
    )


def bare_axes(ax=None, xlim=(0, 1), ylim=(0, 1), title=None, figsize=(10, 6)):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.grid(False)
    if title:
        ax.set_title(title, color=NAVY, pad=10)
    return fig, ax


def stage_label(ax, x, y, text, color):
    ax.text(
        x,
        y,
        text,
        fontsize=8.6,
        fontweight="bold",
        color="white",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=color, edgecolor="none"),
    )


# ============================================================================
# FIGURE 1 - Master workflow: raw data -> current state -> planned work
# ============================================================================
def fig_master_workflow():
    fig, ax = bare_axes(figsize=(13.4, 10.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    ax.text(
        50, 97.4,
        "End-to-End Project Workflow — Raw Data Collection to Current Preprocessing State",
        ha="center", va="center", fontsize=14, fontweight="bold", color=NAVY,
    )
    ax.text(
        50, 94.2,
        "Teal / blue = completed work   ·   amber = open item awaiting a decision   ·   grey dashed = planned, not started",
        ha="center", va="center", fontsize=9, color=GREY,
    )

    # ---- Stage A : data collection -------------------------------------
    stage_label(ax, 7.5, 89.5, "A · DATA COLLECTION — COMPLETE", TEAL)
    y = 80.0
    fbox(ax, 2, y, 28, 7.4,
         "EEG recordings\nBIOPAC .acq + .xlsx · 10 participants × 4 conditions\n40 recordings · 24 channels · 1000 Hz · µV",
         fc="#E8F5F2", ec=TEAL, fs=8.0)
    fbox(ax, 33, y, 28, 7.4,
         "Speech recordings\n.wav (PCM 16-bit) + .aac/.mp4 · 10 participants\n40.7–78.6 s · 44.1 / 48 kHz · mono + stereo",
         fc="#E8F5F2", ec=TEAL, fs=8.0)
    fbox(ax, 64, y, 34, 7.4,
         "Phenotype labels\nKLE Prakriti questionnaire (16 items)\nKLE Traits questionnaire (18 items) · 10 participants",
         fc="#E8F5F2", ec=TEAL, fs=8.0)

    # EEG recordings feed the EEG pipeline; speech recordings feed the speech
    # pipeline (straight arrows — the old diagonals implied cross-over).
    farrow(ax, (16, y), (16, 71.4))
    farrow(ax, (56, y), (56, 71.4))
    # Phenotype labels are NOT an input to preprocessing — note only.
    ax.text(81, 76.4, "used later, at the classification stage",
            ha="center", va="center", fontsize=8.2, color=GREY, style="italic")

    # ---- Stage B : preprocessing ---------------------------------------
    stage_label(ax, 7.5, 73.6, "B · PREPROCESSING — COMPLETE", BLUE)

    fbox(ax, 2, 55.0, 45, 16.0,
         "EEG pipeline — EEG_Dataset_Analysis_and_Preprocessing_v3.ipynb\n"
         "(90 cells · 0 error outputs)\n"
         "\n"
         "1  Read-only inspection of all 40 .acq / .xlsx pairs\n"
         "2  Band-pass 1–45 Hz, zero-phase FIR\n"
         "3  Conditional 50 Hz IIR notch on raw evidence\n"
         "4  Bad-channel check after filtering: 110 flagged, 0 interpolated\n"
         "5  FastICA (20 comps, seed 42) on 30 recordings ≥ 2 min\n"
         "6  1-second residual-artifact register — recorded, never deleted",
         fc="#EAF1F8", ec=BLUE, fs=7.6, align="left")

    fbox(ax, 51, 55.0, 47, 16.0,
         "Speech pipeline — Speech_Dataset_Analysis_and_Preprocessing_v3.ipynb\n"
         "(53 cells · 0 error outputs)\n"
         "\n"
         "1  Inventory + validation of 10 WAV and 10 AAC/MP4 files (PASS 10/10)\n"
         "2  Quality metrics measured BEFORE any change (SNR, clipping, silence)\n"
         "3  Resample 44.1 / 48 kHz → 16 kHz, polyphase FIR, anti-aliasing\n"
         "4  Stereo → mono by integer-lag alignment + mean (P07–P10 only)\n"
         "5  Noise reduction NOT applied — documented decision (STEP 10)\n"
         "6  Silence NOT trimmed — documented decision (STEP 11)",
         fc="#EAF1F8", ec=BLUE, fs=7.6, align="left")

    # (speech box feeds only the speech pipeline via the straight arrow above)
    farrow(ax, (24.5, 55), (24.5, 51.0))
    farrow(ax, (74.5, 55), (74.5, 51.0))

    # ---- Stage C : verification / audit ---------------------------------
    stage_label(ax, 7.5, 47.6, "C · VERIFICATION & AUDIT — COMPLETE", NAVY)
    fbox(ax, 2, 33.0, 45, 13.0,
         "Independent audit & verification\n"
         "· Sampling rate re-read from headers: 40/40 MATCH at 1000 Hz\n"
         "· Filter chain reproduced to < 1×10⁻⁹ V (8-recording subset)\n"
         "· ICA metrics re-derived: 30/30 match their own saved reports\n"
         "· Raw integrity: 100/100 files byte-identical to the baseline\n"
         "· Speech outputs re-validated: 10/10 (16 kHz, mono, PCM_16)",
         fc="#FFF6E8", ec=AMBER, fs=7.8)

    fbox(ax, 51, 33.0, 47, 13.0,
         "Evidence packages & human ICA sign-off\n"
         "· Component maps / time-courses / spectra for all 30 ICA recordings\n"
         "· Before–after waveform + PSD evidence for all 30 recordings\n"
         "· Formal review table with guarded decision logging\n"
         "· Sign-off session 2026-10-14 (reviewer: Anushri Kajagar)\n"
         "   APPROVED 15 · REJECTED 13 · NEEDS_REVIEW 2",
         fc="#FFF6E8", ec=AMBER, fs=7.8)

    farrow(ax, (24.5, 48.6), (24.5, 46.4), color=AMBER)
    farrow(ax, (74.5, 48.6), (74.5, 46.4), color=AMBER)

    # ---- Stage D : current state ----------------------------------------
    stage_label(ax, 7.5, 29.6, "D · CURRENT STATE — ANALYSIS-READY", STEEL)
    fbox(ax, 2, 17.0, 96, 10.0,
         "50 recordings released for feature extraction — every one names the exact input file\n"
         "EEG 40  ·  audit readiness PASS 2 / REVIEW_REQUIRED 38 / FAILED 0\n"
         "Feature input: 15 × *_eeg_ica.fif (human-approved ICA)  +  25 × cleaned *_eeg.fif  ·  Speech 10 × *_speech_cleaned.wav\n"
         "Honour: 931 registered artifact windows (skip) · no reference-sensitive features until the acquisition reference is answered",
         fc="#EDF3FA", ec=STEEL, fs=8.4)

    farrow(ax, (74.5, 33), (60, 27.4))
    farrow(ax, (24.5, 33), (40, 27.4))

    # ---- Stage E : planned ----------------------------------------------
    stage_label(ax, 7.5, 13.4, "E · PLANNED WORK — NOT STARTED", GREY)
    stages = [
        ("Feature extraction\nspectral · temporal\nnonlinear EEG +\nprosodic / spectral\nspeech features", 2),
        ("Feature selection\nidentify the most\ndiscriminative\nattributes", 21.5),
        ("Model development\nML / DL mapping to\nVata · Pitta · Kapha\nclassification", 41),
        ("Evaluation\nmetrics + feature–\nDosha correlation\nanalysis", 60.5),
        ("Prototype &\napplication\ndemonstration", 80),
    ]
    for text, x in stages:
        fbox(ax, x, 3.0, 18, 9.4, text,
             fc="#F2F4F7", ec=GREY, tc=GREY, fs=7.6, lw=1.3)
    for i in range(len(stages) - 1):
        x0 = stages[i][1] + 18
        farrow(ax, (x0, 7.7), (x0 + 1.5, 7.7), color=GREY, ls=(0, (4, 3)))

    farrow(ax, (50, 17), (50, 12.6), color=GREY, ls=(0, (4, 3)))
    ax.text(
        50, 1.0,
        "Stage E corresponds to Tasks 3–5 of the approved REU proposal; none of it has been started.",
        ha="center", fontsize=8.4, color=GREY, style="italic",
    )
    save(fig, "fig01_master_workflow.png")


# ============================================================================
# FIGURE 2 - Dataset composition
# ============================================================================
def fig_dataset_composition():
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.3))
    fig.suptitle(
        "Dataset Composition at a Glance",
        fontsize=14, fontweight="bold", color=NAVY, y=1.03,
    )

    # Panel A - recordings per condition
    ax = axes[0]
    conds = ["calm", "meditation", "maths", "speech"]
    eeg = [10, 10, 10, 10]
    x = np.arange(4)
    ax.bar(x, eeg, width=0.55, color=BLUE, label="EEG recordings")
    ax.bar(x, [1, 1, 1, 1], width=0.55, bottom=eeg, color=TEAL, label="Speech recordings")
    for i in range(4):
        ax.text(i, 10.5, "10", ha="center", fontsize=9, color=BLUE, fontweight="bold")
        ax.text(i, 11.4, "1", ha="center", fontsize=8.5, color=TEAL)
    ax.set_xticks(x)
    ax.set_xticklabels(["calm", "meditation", "maths", "speech"])
    ax.set_ylabel("recordings")
    ax.set_ylim(0, 13.5)
    ax.set_title("A · 10 participants × 4 conditions", color=NAVY)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(axis="x", visible=False)

    # Panel B - raw file inventory
    ax = axes[1]
    labels = [".acq\n(EEG native)", ".xlsx\n(EEG export)", ".wav\n(speech)", ".aac/.mp4\n(speech)"]
    vals = [40, 40, 10, 10]
    cols = [NAVY, STEEL, TEAL, AMBER]
    bars = ax.bar(np.arange(4), vals, width=0.6, color=cols)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, str(v), ha="center",
                fontsize=10, fontweight="bold", color=NAVY)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("files")
    ax.set_ylim(0, 48)
    ax.set_title("B · Raw file inventory (100 files, 8.88 GB)", color=NAVY)
    ax.grid(axis="x", visible=False)

    # Panel C - derived outputs
    ax = axes[2]
    items = [
        "cleaned EEG .fif",
        "ICA EEG .fif",
        "cleaned speech .wav",
        "per-recording JSON",
    ]
    vals = [40, 30, 10, 70]
    cols = [BLUE, AMBER, TEAL, GREY]
    bars = ax.barh(np.arange(len(items))[::-1], vals, height=0.55, color=cols)
    for b, v in zip(bars, vals):
        ax.text(v + 1.5, b.get_y() + b.get_height() / 2, str(v), va="center",
                fontsize=10, fontweight="bold", color=NAVY)
    ax.set_yticks(np.arange(len(items))[::-1])
    ax.set_yticklabels(items, fontsize=9)
    ax.set_xlabel("files produced")
    ax.set_xlim(0, 82)
    ax.set_title("C · Derived outputs written by the pipelines", color=NAVY)
    ax.grid(axis="y", visible=False)

    fig.tight_layout()
    save(fig, "fig02_dataset_composition.png")


# ============================================================================
# FIGURE 3 - EEG stage flowchart with parameters
# ============================================================================
def fig_eeg_pipeline():
    fig, ax = bare_axes(figsize=(13.0, 7.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(13, 99)
    ax.text(50, 97, "EEG Preprocessing Pipeline — Stages, Parameters and Rationale",
            ha="center", fontsize=14, fontweight="bold", color=NAVY)

    cols = [
        (1.5, "1 · READ &\nVERIFY", NAVY, [
            ("bioread reads .acq header\nFs = 1000 Hz · 24 ch · µV", "Nothing guessed:\nevery value from the file"),
            ("cross-check vs .xlsx export\n609,000-row time column", "Two independent sources\nprotect against export errors"),
        ]),
        (26.5, "2 · FILTER", BLUE, [
            ("Band-pass 1–45 Hz\nzero-phase FIR (Hamming)", "Removes DC drift (<1 Hz)\nand fast noise (>45 Hz)"),
            ("Conditional 50 Hz IIR notch\nwidth 2 Hz, only if lift ≥ 6 dB", "Line noise removed only\nwhen it is actually present"),
        ]),
        (51.5, "3 · ARTIFACTS", TEAL, [
            ("Bad-channel check AFTER filtering\nflat · MAD · 20× median rules", "Filtering first avoids false\nflags from DC offset / hum"),
            ("1-second residual scan\n|amp| > 200 µV → register", "Register only — timing and\nevents are never destroyed"),
        ]),
        (76.5, "4 · ICA + OUTPUT", AMBER, [
            ("FastICA, 20 components\nseed 42 · decim 5 · 30 recordings", "Removal needs converging\nevidence, never a bare label"),
            ("Save .fif + JSON report\n40 cleaned · 30 ICA files", "Every setting recorded\nfor full reproducibility"),
        ]),
    ]

    for x0, header, color, rows in cols:
        fbox(ax, x0, 87.5, 22, 6.0, header, fc=color, ec=color, tc="white",
             fs=10.5, weight="bold")
        y = 63.0
        for main, why in rows:
            fbox(ax, x0, y, 22, 14.5, main, fc="#F7FAFD", ec=color, fs=8.4)
            fbox(ax, x0, y - 9.6, 22, 8.4, why, fc="#FFFFFF", ec=LGREY,
                 tc=GREY, fs=7.8, lw=1.0)
            ax.text(x0 + 11, y - 1.0, "WHY", ha="center", fontsize=6.4,
                    color=color, fontweight="bold")
            y -= 27.5
        if x0 < 76:
            farrow(ax, (x0 + 22, 78), (x0 + 25, 78), color=NAVY, lw=1.8)
            farrow(ax, (x0 + 22, 50), (x0 + 25, 50), color=NAVY, lw=1.8)

    # bottom rules
    fbox(ax, 1.5, 15.0, 97, 8.0,
         "SAFETY RULES ENFORCED THROUGHOUT — raw P01–P10 folders are READ-ONLY and re-hashed against INVENTORY_BASELINE.csv after every pass (100/100 files unchanged)\n"
         "No channel, segment or sample is ever silently deleted — flagged content is registered, not removed, so original timing and events are preserved\n"
         "Every decision is written to a register, CSV table or per-recording JSON report, so any reported result can be re-derived from the saved files",
         fc="#EAF1F8", ec=BLUE, fs=8.4)
    save(fig, "fig03_eeg_pipeline.png")


# ============================================================================
# FIGURE 4 - Speech stage flowchart
# ============================================================================
def fig_speech_pipeline():
    fig, ax = bare_axes(figsize=(13.0, 6.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 82)
    ax.text(50, 78, "Speech Preprocessing Pipeline — Stages and Documented Decisions",
            ha="center", fontsize=14, fontweight="bold", color=NAVY)

    steps = [
        ("1 · INVENTORY\n& VALIDATION", "10 WAV + 10 AAC/MP4\npaired by container duration\nPASS 10/10", NAVY),
        ("2 · QUALITY\nBASELINE", "SNR · clipping · DC · silence\nmeasured BEFORE any change\n25 ms window / 10 ms hop", NAVY),
        ("3 · RESAMPLE\nto 16 kHz", "scipy.signal.resample_poly\npolyphase FIR, anti-aliasing\n> 8 kHz energy ≤ 0.47 %", BLUE),
        ("4 · STEREO → MONO\n(P07–P10)", "integer-lag alignment then\narithmetic mean — no channel\ndiscarded, lag ≤ 23 samples", BLUE),
        ("5 · VERIFY\nOUTPUTS", "16 kHz · mono · PCM_16\nduration match ≤ 0.05 s\nverification_status PASS 10/10", TEAL),
    ]
    w = 18.0
    for i, (head, body, color) in enumerate(steps):
        x = 1.0 + i * 19.6
        fbox(ax, x, 58, w, 13, head, fc=color, ec=color, tc="white",
             fs=9.2, weight="bold")
        fbox(ax, x, 34, w, 20, body, fc="#F7FAFD", ec=color, fs=8.0)
        if i < len(steps) - 1:
            farrow(ax, (x + w, 64.5), (x + w + 1.6, 64.5), color=NAVY, lw=1.8)

    ax.text(50, 26.5, "Decisions deliberately taken — recorded in the notebook, applied to every recording",
            ha="center", fontsize=10, fontweight="bold", color=NAVY)

    decisions = [
        ("Noise reduction: NOT applied", TEAL,
         "Estimated SNR ≥ 13.8 dB everywhere; quiet frames\n"
         "show low-frequency room tone, not hiss.\n"
         "Spectral gating risked altering the formants,\n"
         "F0 contour, jitter and shimmer that this\n"
         "research will measure later."),
        ("Silence / pauses: NOT trimmed", TEAL,
         "Pauses are part of natural reading and are\n"
         "informative (speaking rate, pause structure).\n"
         "Longest pause in the dataset is 2.29 s —\n"
         "normal, not a failure. Gain normalisation is\n"
         "also NOT applied: levels kept as recorded."),
        ("AAC → WAV conversion: NOT required", TEAL,
         "Every participant folder already holds a .wav\n"
         "beside its .aac/.mp4, and all 10 pairs matched\n"
         "within 0.5 s tolerance. Re-conversion would\n"
         "only add a lossy step."),
    ]
    for i, (title, color, body) in enumerate(decisions):
        x = 1.0 + i * 32.6
        fbox(ax, x, 7.0, 31.0, 15.5, f"{title}\n\n{body}",
             fc="#E8F5F2", ec=color, fs=7.6, align="left")
    save(fig, "fig04_speech_pipeline.png")


# ============================================================================
# FIGURE 5 - 50 Hz raw evidence per recording
# ============================================================================
def fig_50hz():
    d = pd.read_csv(ROOT / "audit_finalization_v1" / "eeg" / "raw_50hz_audit_v1.csv")
    d = d.sort_values("raw_ratio", ascending=False).reset_index(drop=True)
    labels = [f"{r.participant} {r.condition}" for r in d.itertuples()]
    colmap = {"strong": BLUE, "mild": AMBER, "weak": RED}
    colors = [colmap.get(c, GREY) for c in d["interference_class"]]

    fig, ax = plt.subplots(figsize=(13.0, 4.4))
    x = np.arange(len(d))
    ax.bar(x, d["raw_ratio"], color=colors, width=0.72)
    ax.axhline(2.0, color=RED, ls="--", lw=1.4)
    ax.text(len(d) - 0.4, 2.6, "2× support threshold", color=RED, fontsize=8.5,
            ha="right", fontweight="bold")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=90, fontsize=6.8)
    ax.set_ylabel("50 Hz peak ÷ local noise floor (×, log scale)")
    ax.set_title(
        "Raw 50 Hz mains interference measured on the unfiltered .acq files (all 40 recordings)",
        color=NAVY,
    )
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=colmap["strong"]),
        plt.Rectangle((0, 0), 1, 1, color=colmap["mild"]),
        plt.Rectangle((0, 0), 1, 1, color=colmap["weak"]),
    ]
    ax.legend(
        handles,
        ["strong ≥ 10×  (33)", "mild 2–10×  (6)", "weak < 2×  (1: P02 speech 1.40×)"],
        frameon=False, fontsize=8.6, loc="upper right",
    )
    ax.grid(axis="x", visible=False)
    ax.set_ylim(bottom=0.7)
    fig.tight_layout()
    save(fig, "fig05_raw_50hz_evidence.png")


# ============================================================================
# FIGURE 6 - Flagged channels + artifact windows
# ============================================================================
def fig_artifacts():
    bad = pd.read_csv(ROOT / "audit_finalization_v1" / "eeg" / "bad_channel_audit_v1.csv")
    keep = bad[bad["verdict"].astype(str).str.startswith("KEEP")]
    counts = keep["channel"].value_counts()
    order = list(counts.index)

    art = pd.read_csv(ROOT / "audit_finalization_v1" / "eeg" / "artifact_log_v1.csv")
    per_rec = (
        art.groupby(["participant", "condition"], sort=False)
        .agg(spans=("duration_s", "size"), seconds=("duration_s", "sum"))
        .reset_index()
    )
    per_rec["id"] = per_rec["participant"] + " " + per_rec["condition"]
    per_rec = per_rec.sort_values("spans", ascending=False).reset_index(drop=True)

    fig, axes = plt.subplots(1, 2, figsize=(13.4, 4.8))
    fig.suptitle(
        "Artifact Handling — Everything Is Registered, Nothing Is Deleted",
        fontsize=14, fontweight="bold", color=NAVY, y=1.02,
    )

    ax = axes[0]
    cols = [RED if c.startswith("Fp") else (AMBER if c.startswith("F") else STEEL)
            for c in order]
    ax.bar(np.arange(len(order)), counts.values, color=cols, width=0.68)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(order, rotation=90, fontsize=8)
    ax.set_ylabel("flagged channel instances")
    ax.set_title(f"A · Channels flagged for review ({int(counts.sum())} instances · 0 interpolated)",
                 color=NAVY, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    for i, v in enumerate(counts.values):
        ax.text(i, v + 0.4, str(v), ha="center", fontsize=7.4, color=NAVY)
    ax.set_ylim(0, max(counts.values) * 1.18)

    ax = axes[1]
    ax.bar(np.arange(len(per_rec)), per_rec["spans"], color=BLUE, width=0.7)
    ax.set_xticks(np.arange(len(per_rec)))
    ax.set_xticklabels(per_rec["id"], rotation=90, fontsize=7)
    ax.set_ylabel("1-second windows flagged")
    ax.set_title(
        f"B · Residual artifact windows per recording (931 spans · 34 recs · 1469 s)",
        color=NAVY, fontsize=10.5,
    )
    ax.grid(axis="x", visible=False)
    zero = 40 - len(per_rec)
    ax.text(0.99, 0.94,
            f"{zero} recordings have no flagged window",
            transform=ax.transAxes, ha="right", fontsize=8.4, color=GREY,
            style="italic")

    fig.tight_layout()
    save(fig, "fig06_artifact_burden.png")


# ============================================================================
# FIGURE 7 - ICA decision flow
# ============================================================================
def fig_ica_decision_flow():
    fig, ax = bare_axes(figsize=(13.0, 7.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.text(50, 97, "ICA Processing and Validation — Decision Flow",
            ha="center", fontsize=14, fontweight="bold", color=NAVY)

    # ---- Row 1 : fit chain ---------------------------------------------
    row1 = [
        (1, 23, "Eligibility\n≥ 16 channels AND\nduration ≥ 2 min"),
        (27, 23, "Fit\nFastICA · 20 components\nseed 42 · decim 5"),
        (53, 23, "Candidate detection\n|EOG corr| ≥ 0.40 AND\nfrontal weight ≥ 0.35"),
        (79, 20, "Cap\n≤ 6 comps\nper recording"),
    ]
    for x, w, text in row1:
        fbox(ax, x, 84, w, 11, text, fc="#EAF1F8", ec=BLUE, fs=8.6)
    for x in (24, 50, 76):
        farrow(ax, (x, 89.5), (x + 3, 89.5), color=NAVY, lw=1.8)

    # ---- Speech branch (short recordings never enter ICA) ---------------
    fbox(ax, 1, 48, 26, 12,
         "SHORT EEG RECORDINGS\n10 speech-condition EEG\n0.6–1.1 min (< 2 min rule)",
         fc="#F2F4F7", ec=GREY, tc=GREY, fs=8.4, lw=1.5)
    farrow(ax, (14, 84), (14, 60.6), color=GREY, ls=(0, (4, 3)))
    farrow(ax, (14, 48), (16.5, 45.4), color=GREY, ls=(0, (4, 3)))

    # ---- Automated audit header ----------------------------------------
    ax.text(50, 66,
            "Automated quantitative audit (V7b) — recomputed from the saved .fif files, cross-checked 30/30",
            ha="center", fontsize=9.6, fontweight="bold", color=NAVY,
            zorder=4,
            bbox=dict(boxstyle="square,pad=0.25", facecolor="white", edgecolor="none"))
    farrow(ax, (51.5, 84), (51.5, 68.2), color=NAVY, lw=1.8)
    farrow(ax, (51.5, 64), (51.5, 60.6), color=NAVY, lw=1.8)

    # ---- Guard strip ----------------------------------------------------
    guards = [
        "EOG-proxy\ncorrelation\n|r| ≥ 0.40",
        "Frontal\ntopographic\nweight ≥ 0.35",
        "Posterior\nalpha loss\n≤ 30 % guard",
        "Variance\nreduction\n≤ 80 %",
        "No open\nbatch\nflag",
    ]
    for i, text in enumerate(guards):
        x = 30 + i * 14
        fbox(ax, x, 48, 13, 12, text, fc="#FFF6E8", ec=AMBER, fs=7.8, lw=1.4)

    # ---- Outcomes -------------------------------------------------------
    outcomes = [
        (1, "NOT_APPLICABLE\n10 speech-condition EEG recordings\n(< 2 min) · outside the sign-off table", GREY),
        (34, "HUMAN_SIGNOFF_PENDING\n25 recordings · 3 near-guard (25–30 %)\nautomated APPROVED by the V7b rule", TEAL),
        (67, "EXCLUDED — alpha guard breached\n5 recordings\nnot usable as feature input", RED),
    ]
    for x, text, color in outcomes:
        fbox(ax, x, 33, 31, 12, text, fc="#FFFFFF", ec=color, fs=8.4, lw=1.7)
    farrow(ax, (64.5, 48), (49.5, 45.6), color=TEAL, lw=1.5, rad=0.12)
    farrow(ax, (64.5, 48), (82.5, 45.6), color=RED, lw=1.5, rad=-0.12)

    # ---- Sign-off banner ------------------------------------------------
    fbox(ax, 1, 27, 98, 4.4,
         "Formal human sign-off — EEG_ICA_Signoff_Review_v1.ipynb · session 2026-10-14 (reviewer: Anushri Kajagar)",
         fc=NAVY, ec=NAVY, tc="white", fs=8.8, weight="bold")
    farrow(ax, (49.5, 33), (49.5, 31.6), color=TEAL, lw=1.5)
    farrow(ax, (82.5, 33), (82.5, 31.6), color=RED, lw=1.5)

    # ---- Sign-off outcomes ----------------------------------------------
    signoffs = [
        (4, "APPROVED  15\n\nuse *_eeg_ica.fif for\nfeature extraction", TEAL),
        (36, "REJECTED  13\n\nuse cleaned *_eeg.fif;\nICA file kept on disk for audit", RED),
        (68, "NEEDS_REVIEW  2\n\nP07 maths · P08 meditation\nstill open — cleaned file in use", AMBER),
    ]
    for x, text, color in signoffs:
        fbox(ax, x, 6, 28, 16, text, fc="#FFFFFF", ec=color, fs=8.8, lw=1.9)
    for x in (18, 50, 82):
        farrow(ax, (x, 27), (x, 22.6), color=NAVY, lw=1.5)

    ax.text(50, 2.4,
            "Guards and thresholds were never relaxed — a recording failing any guard falls back to the cleaned pre-ICA file.",
            ha="center", fontsize=8.4, color=GREY, style="italic")
    save(fig, "fig07_ica_decision_flow.png")


# ============================================================================
# FIGURE 8 - Posterior alpha change per ICA recording
# ============================================================================
def fig_alpha_loss():
    log = pd.read_csv(ROOT / "EEG processed" / "eeg" / "figures_v3" / "ica_review_log.csv")
    # keep only recordings where ICA was actually fit — the 10 short
    # speech-condition rows carry the status "NOT_APPLIED (…)" and have no
    # alpha value, which would otherwise render as empty rows
    log = log[log["ica_status"].str.startswith("OK")].copy()

    tbl = pd.read_csv(ROOT / "signoff_finalization_v2" / "ica_review_table_v1.csv")
    dec = dict(zip(tbl["recording_id"], tbl["decision"]))
    log["rid"] = log["participant"] + "_" + log["condition"]
    log["decision"] = log["rid"].map(dec)

    log = log.sort_values("posterior_alpha_change_pct").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12.8, 7.4))
    y = np.arange(len(log))
    colors = [DEC_COLORS.get(d, GREY) for d in log["decision"]]
    ax.barh(y, log["posterior_alpha_change_pct"], color=colors, height=0.72)

    ax.axvline(-30, color=NAVY, ls="--", lw=1.6)
    ax.axvline(-25, color=LGREY, ls=":", lw=1.4)
    tr = ax.get_xaxis_transform()  # x in data units, y in axes fraction
    ax.text(-29.5, 0.99, "30 % alpha guard", color=NAVY,
            fontsize=9, fontweight="bold", va="top", transform=tr)
    ax.text(-24.5, 0.92, "25 % near-guard band", color=GREY,
            fontsize=8.4, va="top", transform=tr)

    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{r.participant} {r.condition}" for r in log.itertuples()], fontsize=8.4
    )
    for i, v in enumerate(log["posterior_alpha_change_pct"]):
        ax.text(
            v - 2.2 if v < 0 else v + 2.2,
            i,
            f"{v:+.1f}%",
            va="center",
            ha="right" if v < 0 else "left",
            fontsize=7.6,
            color="#33414F",
        )
    ax.set_xlim(-100, 30)
    ax.set_xlabel("change in posterior (O1 / O2 / Oz) alpha power after ICA  (%)")
    ax.set_title(
        "Effect of ICA on posterior alpha — the guard that drove four rejections",
        color=NAVY,
    )
    ax.grid(axis="y", visible=False)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=DEC_COLORS["APPROVED"]),
        plt.Rectangle((0, 0), 1, 1, color=DEC_COLORS["REJECTED"]),
        plt.Rectangle((0, 0), 1, 1, color=DEC_COLORS["NEEDS_REVIEW"]),
    ]
    ax.legend(
        handles,
        ["human sign-off APPROVED (15)", "human sign-off REJECTED (13)",
         "NEEDS_REVIEW (2)"],
        frameon=False, fontsize=9, loc="lower right",
    )
    fig.tight_layout()
    save(fig, "fig08_posterior_alpha.png")


# ============================================================================
# FIGURE 9 - Variance removed vs alpha lost
# ============================================================================
def fig_variance_alpha():
    log = pd.read_csv(ROOT / "EEG processed" / "eeg" / "figures_v3" / "ica_review_log.csv")
    log = log[log["ica_status"] != "NOT_APPLIED"].copy()
    tbl = pd.read_csv(ROOT / "signoff_finalization_v2" / "ica_review_table_v1.csv")
    dec = dict(zip(tbl["recording_id"], tbl["decision"]))
    log["rid"] = log["participant"] + "_" + log["condition"]
    log["decision"] = log["rid"].map(dec)

    fig, ax = plt.subplots(figsize=(9.6, 6.4))
    for d, g in log.groupby("decision"):
        ax.scatter(
            g["variance_reduction_pct"],
            -g["posterior_alpha_change_pct"],
            s=76,
            color=DEC_COLORS.get(d, GREY),
            edgecolor="white",
            linewidth=0.9,
            label=f"{d} ({len(g)})",
            zorder=4,
        )
    ax.axhline(30, color=NAVY, ls="--", lw=1.5)
    ax.axvline(80, color=GREY, ls="--", lw=1.5)
    ax.text(81, 4, "80 % variance cap", color=GREY, fontsize=8.6)
    ax.text(1.5, 31.4, "30 % posterior-alpha guard", color=NAVY,
            fontsize=8.8, fontweight="bold")

    for _, r in log.iterrows():
        alpha = -r["posterior_alpha_change_pct"]
        if alpha > 38 or r["variance_reduction_pct"] > 78 or r["decision"] == "NEEDS_REVIEW":
            ax.annotate(
                f"{r['participant']} {r['condition']}",
                (r["variance_reduction_pct"], alpha),
                textcoords="offset points",
                xytext=(7, 5),
                fontsize=7.6,
                color="#33414F",
            )

    ax.set_xlabel("total variance removed by ICA  (%)")
    ax.set_ylabel("posterior alpha power lost  (%)")
    ax.set_xlim(-3, 105)
    ax.set_ylim(-4, 96)
    ax.set_title(
        "ICA removal magnitude vs. neural signal cost — 30 recordings with ICA fitted",
        color=NAVY,
    )
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    save(fig, "fig09_variance_vs_alpha.png")


# ============================================================================
# FIGURE 10 - ICA disposition evolution
# ============================================================================
def fig_ica_evolution():
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.5))
    fig.suptitle(
        "How the ICA Decision Evolved — three successive, documented stages",
        fontsize=14, fontweight="bold", color=NAVY, y=1.03,
    )

    # Stage 1 : eligibility
    ax = axes[0]
    vals = [30, 10]
    ax.pie(
        vals,
        labels=["ICA fitted\n30 recordings\n(≥ 2 min)", "not applicable\n10 recordings\n(speech, < 2 min)"],
        colors=[BLUE, LGREY],
        autopct=lambda p: f"{int(round(p * sum(vals) / 100))}",
        startangle=90,
        textprops={"fontsize": 8.6},
        wedgeprops={"edgecolor": "white", "linewidth": 1.6},
        pctdistance=0.62,
    )
    ax.set_title("Stage 1 · Automated fit\n(V6/V7, FastICA 20 comps)", color=NAVY)

    # Stage 2 : automated audit
    ax = axes[1]
    labels = ["APPROVED", "PROVISIONAL", "REJECTED", "NOT_APPLIED"]
    vals = [25, 1, 4, 10]
    bars = ax.bar(np.arange(4), vals,
                  color=[TEAL, AMBER, RED, GREY], width=0.66)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.7, str(v), ha="center",
                fontsize=10.5, fontweight="bold", color=NAVY)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(["APPROVED", "PROV.", "REJECTED", "NOT_APPL."], fontsize=8.4)
    ax.set_ylabel("recordings")
    ax.set_ylim(0, 30)
    ax.set_title("Stage 2 · Automated V7b audit\n(2026-10-11, not a human sign-off)",
                 color=NAVY)
    ax.grid(axis="x", visible=False)

    # Stage 3 : human sign-off
    ax = axes[2]
    labels = ["APPROVED", "REJECTED", "NEEDS_REVIEW"]
    vals = [15, 13, 2]
    bars = ax.bar(np.arange(3), vals, color=[TEAL, RED, AMBER], width=0.58)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, str(v), ha="center",
                fontsize=10.5, fontweight="bold", color=NAVY)
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(["APPROVED", "REJECTED", "NEEDS_REVIEW"], fontsize=8.4)
    ax.set_ylabel("recordings")
    ax.set_ylim(0, 18)
    ax.set_title("Stage 3 · Formal human sign-off\n(2026-10-14, Anushri Kajagar)",
                 color=NAVY)
    ax.grid(axis="x", visible=False)

    fig.tight_layout()
    save(fig, "fig10_ica_evolution.png")


# ============================================================================
# FIGURE 11 - Quality-control readiness
# ============================================================================
def fig_readiness():
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.6),
                             gridspec_kw={"width_ratios": [1.25, 1]})
    fig.suptitle(
        "Quality-Control Readiness — Reported Honestly, Not Forced to PASS",
        fontsize=14, fontweight="bold", color=NAVY, y=1.03,
    )

    ax = axes[0]
    groups = ["EEG\npipeline pass (v3)\nn = 40", "EEG\nindependent audit\nn = 40", "Speech\nindependent audit\nn = 10"]
    passv = [6, 2, 7]
    rev = [34, 38, 3]
    fail = [0, 0, 0]
    x = np.arange(3)
    ax.bar(x, passv, width=0.5, color=TEAL, label="PASS")
    ax.bar(x, rev, width=0.5, bottom=passv, color=AMBER, label="REVIEW_REQUIRED")
    ax.bar(x, fail, width=0.5, color=RED, label="FAILED")
    for i in range(3):
        if passv[i]:
            ax.text(i, passv[i] / 2, str(passv[i]), ha="center", va="center",
                    color="white", fontweight="bold", fontsize=11)
        ax.text(i, passv[i] + rev[i] / 2, str(rev[i]), ha="center", va="center",
                color="#4A3208", fontweight="bold", fontsize=11)
        ax.text(i, passv[i] + rev[i] + 1.2, str(fail[i]), ha="center",
                color=RED, fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=8.8)
    ax.set_ylabel("recordings")
    ax.set_ylim(0, 46)
    ax.set_title("A · Readiness under each rule set", color=NAVY)
    ax.legend(frameon=False, fontsize=8.8, loc="upper right")
    ax.grid(axis="x", visible=False)
    ax.text(0.0, -0.30,
            "REVIEW_REQUIRED = usable with documented constraints. The stricter audit rule is in force (2 PASS / 38 REVIEW).",
            transform=ax.transAxes, fontsize=8.4, color=GREY, style="italic")

    # feature input split
    ax = axes[1]
    vals = [15, 25, 10]
    labs = ["EEG: ICA file\n(15 human-approved)", "EEG: cleaned file\n(25 fallback)", "Speech: cleaned wav\n(10)"]
    ax.pie(
        vals,
        labels=labs,
        colors=[TEAL, BLUE, STEEL],
        autopct=lambda p: f"{p:.0f} %",
        startangle=100,
        textprops={"fontsize": 8.6},
        wedgeprops={"edgecolor": "white", "linewidth": 1.8},
        pctdistance=0.68,
    )
    ax.set_title("B · Feature-extraction input now in force\n(every file path verified on disk)",
                 color=NAVY)

    fig.tight_layout()
    save(fig, "fig11_qc_readiness.png")


# ============================================================================
# FIGURE 12 - Speech quality per participant
# ============================================================================
def fig_speech_quality():
    d = pd.read_csv(ROOT / "SPEECH processed" / "speech" / "reports" /
                    "audio_quality_report_v3.csv")
    x = np.arange(len(d))

    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.3))
    fig.suptitle("Speech Quality Assessment Before Any Processing Change",
                 fontsize=14, fontweight="bold", color=NAVY, y=1.04)

    ax = axes[0]
    cols = [RED if v < 15 else TEAL for v in d["estimated_snr_db"]]
    ax.bar(x, d["estimated_snr_db"], color=cols, width=0.66)
    ax.axhline(15, color=RED, ls="--", lw=1.5)
    ax.text(len(d) - 0.4, 15.8, "15 dB review threshold", color=RED,
            fontsize=8.4, ha="right", fontweight="bold")
    for i, v in enumerate(d["estimated_snr_db"]):
        ax.text(i, v + 0.5, f"{v:.1f}", ha="center", fontsize=7.4, color=NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels(d["participant_id"], fontsize=8.4)
    ax.set_ylabel("estimated SNR (dB)")
    ax.set_ylim(0, 29)
    ax.set_title("A · Estimated SNR  (P05 = 13.8 dB)", color=NAVY)
    ax.grid(axis="x", visible=False)

    ax = axes[1]
    ax.bar(x - 0.17, d["noise_floor_db"], width=0.34, color=GREY, label="noise floor")
    ax.bar(x + 0.17, d["speech_level_db"], width=0.34, color=BLUE, label="speech level")
    ax.set_xticks(x)
    ax.set_xticklabels(d["participant_id"], fontsize=8.4)
    ax.set_ylabel("level (dBFS)")
    ax.set_title("B · Level structure", color=NAVY)
    ax.legend(frameon=False, fontsize=8.4)
    ax.grid(axis="x", visible=False)

    ax = axes[2]
    cols = [RED if v > 0 else STEEL for v in d["clipping_pct"]]
    ax.bar(x, np.maximum(d["clipping_pct"], 0.000001), color=cols, width=0.66)
    ax.axhline(0.000001, color=GREY, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(d["participant_id"], fontsize=8.4)
    ax.set_ylabel("clipped samples (% of file, log)")
    ax.set_yscale("log")
    ax.set_title("C · Clipping  (P10 source only, 0.003 %)", color=NAVY)
    ax.grid(axis="x", visible=False)

    fig.tight_layout()
    save(fig, "fig12_speech_quality.png")


# ============================================================================
# FIGURE 13 - Timeline of project passes
# ============================================================================
def fig_timeline():
    fig, ax = bare_axes(figsize=(13.4, 7.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.text(50, 97, "Project Chronology — What Was Done, In What Order",
            ha="center", fontsize=14, fontweight="bold", color=NAVY)

    entries = [
        ("2026-10-10", "Dataset organisation & integrity baseline",
         "500 files / 8.88 GB indexed; SHA-256 recorded in INVENTORY_BASELINE.csv", TEAL),
        ("2026-10-10", "Original EEG + speech preprocessing run",
         "40 cleaned .fif, 30 ICA .fif, 10 cleaned .wav, per-recording JSON reports", TEAL),
        ("2026-10-11", "v3 validation & freeze pass",
         "V1–V9 checks; raw 50 Hz re-measured; component audit (V7b); 40 JSONs finalised", TEAL),
        ("2026-10-12", "Independent audit & finalization (v1)",
         "Re-derived from saved files: filter < 1e-9 V, ICA 30/30, 931 spans, raw 100/100", BLUE),
        ("2026-10-12", "Review plan + PSD figure defect fix",
         "38 REVIEW_REQUIRED recordings planned; 4 blank PSD panels corrected (0 left)", BLUE),
        ("2026-10-13", "Evidence packaging & sign-off workflow",
         "Component evidence, visual bundle, contact sheets, packet v2, 20 QC issues", AMBER),
        ("2026-10-14", "Formal human ICA sign-off",
         "28 of 30 decided: 15 APPROVED / 13 REJECTED / 2 NEEDS_REVIEW", AMBER),
        ("Next", "Feature extraction → model → classification",
         "Tasks 3–5 of the proposal — NOT STARTED", GREY),
    ]

    y0 = 84
    step = 10.6
    ax.plot([9, 9], [4, y0 + 3.5], color=LGREY, lw=3, solid_capstyle="round", zorder=1)

    for i, (date, title, detail, color) in enumerate(entries):
        y = y0 - i * step
        future = color == GREY
        ax.scatter([9], [y], s=190, color="white", edgecolor=color,
                   linewidth=2.4, zorder=3)
        ax.text(9, y, str(i + 1) if not future else "→", ha="center", va="center",
                fontsize=8.6, fontweight="bold", color=color, zorder=4)
        ax.text(13.5, y + 1.4, date, fontsize=9.2, fontweight="bold", color=color,
                va="center")
        ax.text(13.5, y - 1.6, title, fontsize=9.6, fontweight="bold",
                color=NAVY, va="center")
        ax.text(50, y, detail, fontsize=8.6, color="#3A4653", va="center",
                style="italic" if future else "normal",
                bbox=dict(boxstyle="round,pad=0.45",
                          facecolor=PANEL if not future else "#F2F4F7",
                          edgecolor=LGREY, linewidth=0.8))

    save(fig, "fig13_timeline.png")


# ============================================================================
# FIGURE 14 - Work-package status overview
# ============================================================================
def fig_status_overview():
    rows = [
        ("Data collection — EEG (40 recordings)", 100, "Complete", TEAL),
        ("Data collection — speech (10 recordings)", 100, "Complete", TEAL),
        ("Questionnaire / label capture", 100, "Complete", TEAL),
        ("EEG preprocessing pipeline", 100, "Complete", TEAL),
        ("Speech preprocessing pipeline", 100, "Complete", TEAL),
        ("Filtering verification (subset of 8)", 100, "Complete", TEAL),
        ("Sampling-rate verification (40/40)", 100, "Complete", TEAL),
        ("Independent audit of saved outputs", 100, "Complete", TEAL),
        ("Raw-integrity verification (100/100)", 100, "Complete", TEAL),
        ("ICA evidence packaging for review", 100, "Complete", TEAL),
        ("Formal human ICA sign-off (28/30)", 93, "2 open", AMBER),
        ("Acquisition-reference confirmation", 0, "Blocked — awaiting lab", RED),
        ("Feature extraction (Task 3)", 0, "Not started", GREY),
        ("Feature selection (Task 3)", 0, "Not started", GREY),
        ("Model development (Task 4)", 0, "Not started", GREY),
        ("Evaluation & application (Task 5)", 0, "Not started", GREY),
    ]
    fig, ax = plt.subplots(figsize=(12.4, 6.4))
    y = np.arange(len(rows))[::-1]
    for i, (label, pct, status, color) in enumerate(rows):
        ax.barh(y[i], 100, color="#EDF1F5", height=0.62, zorder=1)
        if pct > 0:
            ax.barh(y[i], pct, color=color, height=0.62, zorder=2)
        ax.text(101.5, y[i], status, va="center", fontsize=8.6,
                color=color, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_xlim(0, 132)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"])
    ax.set_title("Implementation Status by Work Package", color=NAVY, loc="left")
    ax.grid(axis="y", visible=False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    fig.text(0.012, 0.018,
             "Percentages describe this project's own status records — no unfinished task is counted as complete.",
             fontsize=8.4, color=GREY, style="italic")
    fig.tight_layout()
    save(fig, "fig14_status_overview.png")


# ============================================================================
# FIGURE 15 - EEG vs speech pipeline comparison (side by side summary)
# ============================================================================
def fig_modality_comparison():
    fig, ax = bare_axes(figsize=(13.0, 5.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.text(50, 96, "Side-by-Side Summary of the Two Preprocessing Pipelines",
            ha="center", fontsize=14, fontweight="bold", color=NAVY)

    rows = [
        ("Input", "40 × .acq + 40 × .xlsx\nBIOPAC, 24 ch, 1000 Hz",
         "10 × .wav + 10 × .aac/.mp4\n44.1 / 48 kHz, mono + stereo"),
        ("Read / validated", "bioread header read;\n40/40 recordings present",
         "soundfile + mutagen metadata;\nvalidation PASS 10/10"),
        ("Band limiting", "band-pass 1–45 Hz\nzero-phase FIR",
         "resample to 16 kHz\n(polyphase FIR, anti-aliasing)"),
        ("Line noise / hum", "conditional 50 Hz IIR notch\n(evidence-driven)",
         "not applicable"),
        ("Channel handling", "bad-channel flags only\n110 flagged · 0 interpolated",
         "stereo → mono lag-aligned mean\n(P07–P10; both channels kept)"),
        ("Artifact removal", "ICA (30 rec.) + 1-s register\nregister only, never deleted",
         "deliberately none\n(noise reduction not applied)"),
        ("Outputs", "40 cleaned .fif · 30 ICA .fif\n+ per-recording JSON reports",
         "10 cleaned .wav (16 kHz mono)\n+ per-recording JSON reports"),
        ("Readiness", "PASS 2 · REVIEW 38 · FAILED 0",
         "PASS 7 · REVIEW 3 · FAILED 0"),
    ]

    fbox(ax, 2, 84, 24, 7, "Aspect", fc=NAVY, ec=NAVY, tc="white",
         fs=10, weight="bold")
    fbox(ax, 28, 84, 34, 7, "EEG pipeline", fc=BLUE, ec=BLUE, tc="white",
         fs=10, weight="bold")
    fbox(ax, 64, 84, 34, 7, "Speech pipeline", fc=TEAL, ec=TEAL, tc="white",
         fs=10, weight="bold")

    y = 74.5
    for i, (aspect, eeg, speech) in enumerate(rows):
        h = 8.4
        shade = PANEL if i % 2 == 0 else "#FFFFFF"
        fbox(ax, 2, y, 24, h, aspect, fc=shade, ec=LGREY, tc=NAVY, fs=8.6,
             weight="bold", lw=0.9)
        fbox(ax, 28, y, 34, h, eeg, fc=shade, ec=LGREY, fs=8.2, lw=0.9)
        fbox(ax, 64, y, 34, h, speech, fc=shade, ec=LGREY, fs=8.2, lw=0.9)
        y -= 9.0

    save(fig, "fig15_modality_comparison.png")


# ============================================================================
def main():
    print("Generating report figures ->", OUT)
    fig_master_workflow()
    fig_dataset_composition()
    fig_eeg_pipeline()
    fig_speech_pipeline()
    fig_50hz()
    fig_artifacts()
    fig_ica_decision_flow()
    fig_alpha_loss()
    fig_variance_alpha()
    fig_ica_evolution()
    fig_readiness()
    fig_speech_quality()
    fig_timeline()
    fig_status_overview()
    fig_modality_comparison()
    print("done.")


if __name__ == "__main__":
    main()
