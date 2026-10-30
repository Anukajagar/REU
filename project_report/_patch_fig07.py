"""One-shot patch: replace fig_ica_decision_flow() with a corrected layout."""
from pathlib import Path

p = Path(r"E:\REU_DATA\project_report\make_report_figures.py")
s = p.read_text(encoding="utf-8")
start = s.index("def fig_ica_decision_flow():")
end = s.index("# ============================================================================\n# FIGURE 8")

new = r'''def fig_ica_decision_flow():
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
         "NOT_APPLICABLE\n10 speech recordings\n0.6–1.1 min (< 2 min)",
         fc="#F2F4F7", ec=GREY, tc=GREY, fs=8.4, lw=1.5)
    farrow(ax, (14, 84), (14, 60.6), color=GREY, ls=(0, (4, 3)))
    farrow(ax, (14, 48), (16.5, 45.4), color=GREY, ls=(0, (4, 3)))

    # ---- Automated audit header ----------------------------------------
    ax.text(50, 66,
            "Automated quantitative audit (V7b) — recomputed from the saved .fif files, cross-checked 30/30",
            ha="center", fontsize=9.6, fontweight="bold", color=NAVY)
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
        (1, "NOT_APPLICABLE\n10 speech recordings (< 2 min)\noutside the sign-off table", GREY),
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


'''

p.write_text(s[:start] + new + s[end:], encoding="utf-8")
print("patched fig_ica_decision_flow")
