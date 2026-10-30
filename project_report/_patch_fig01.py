"""One-shot patch: replace fig_master_workflow() with a corrected layout."""
from pathlib import Path

p = Path(r"E:\REU_DATA\project_report\make_report_figures.py")
s = p.read_text(encoding="utf-8")
start = s.index("def fig_master_workflow():")
end = s.index("# ============================================================================\n# FIGURE 2")

new = r'''def fig_master_workflow():
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

    farrow(ax, (16, y), (16, y - 3.0))
    farrow(ax, (47, y), (47, y - 3.0))
    farrow(ax, (81, y), (81, y - 3.0))

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

    farrow(ax, (50, 80), (24.5, 71.4))
    farrow(ax, (50, 80), (74.5, 71.4))
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


'''

p.write_text(s[:start] + new + s[end:], encoding="utf-8")
print("patched fig_master_workflow")
