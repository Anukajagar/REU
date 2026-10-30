# REU_DATA — Directory Structure Map

Project: *Analysis of Neuro-Acoustic Features from EEG and Speech Signals for Dosha Characterization* (Proposal 01, Annexure 2).

This file is an index only. **No original file was moved, renamed, edited, or deleted to produce it.**
Integrity proof: `INVENTORY_BASELINE.csv` (500 files, 8.88 GB, SHA-256 per file).

---

## Top-level layout

```
E:\REU_DATA\
├── P01 … P10                  RAW, READ-ONLY (10 files each, ~720-743 MB each)
│   ├── NN_eeg\
│   │   ├── acq\               4 × .acq   original BIOPAC recordings
│   │   └── csv\               4 × .xlsx  exported channel data
│   └── NN_speech\             .wav (audio) + .aac/.mp4 (video)
│
├── EEG processed\             DERIVED (324 files, 1754 MB)
│   └── eeg\
│       ├── P01…P10\{calm,meditation,maths,speech}\  *.fif cleaned EEG
│       ├── figures\P01…P10\   per-participant QC plots
│       ├── preprocessing_summary.csv / .json
│       └── preprocessing_visualisation_summary.csv
│
├── SPEECH processed\          DERIVED (54 files, 23 MB)
│   └── speech\
│       ├── P01…P10\           *_speech_cleaned.wav + quality_report.json
│       ├── plots\             spectrograms, waveforms, noise assessment
│       └── reports\           audio_quality_report.csv, speech_inventory.csv,
│                               preprocessing_log.csv, final_summary.json, …
│
├── EEG presentation_figures\  DERIVED (4 files) — poster/slide figures + .npz
├── notebooks\                 CODE (3 × .ipynb + make_presentation_figures.py)
├── information\               DOCS (9 files)
│   ├── Annexure 2_salma.docx          REU proposals 01 & 02
│   ├── My doubts in REU.docx
│   ├── WhatsApp Video 2026-04-24….mp4
│   ├── research paper for reu\        5 × .pdf
│   └── ~$ doubts in REU.docx          Word lock/temp file (162 B)
│
├── KLE_PRAKRITI_QUESTIONNARIE.xlsx    LABELS (10 participants answered)
├── KLE_TRAITS_QUESTIONNARIE.xlsx      LABELS (10 participants answered)
│
├── INVENTORY_BASELINE.csv     integrity manifest (created by this pass)
├── STRUCTURE.md               this file (created by this pass)
├── .gitignore                 FROZEN — untouched
├── AGENTS.md                  FROZEN — untouched
└── README.md                  FROZEN — untouched
```

## Counts verified at baseline

| Area | Files | Size |
| --- | ---: | ---: |
| P01–P10 (raw) | 100 | 7,276 MB |
| EEG processed | 324 | 1,754 MB |
| SPEECH processed | 54 | 23 MB |
| EEG presentation_figures | 4 | 1.8 MB |
| notebooks | 4 | 8.5 MB |
| information | 9 | 32 MB |
| Questionnaires (root) | 2 | <1 MB |
| Frozen files (.gitignore, AGENTS.md, README.md) | 3 | <1 MB |
| **Total** | **500** | **8.88 GB** |

Raw breakdown: 40 `.acq`, 40 `.xlsx` (EEG export), 20 `.wav`, 8 `.aac`, 3 `.mp4`.
Derived breakdown: 40 `.fif`, 272 `.png`, 52 `.json`.

---

## Separation rules in force

- `P01`–`P10` are **raw and read-only**. Nothing is written into them.
- All derived output lives outside the raw folders, in `EEG processed\` and `SPEECH processed\`.
- No preprocessing, feature extraction, or model training was run during this reorganisation.

## Known issue — output path mismatch (NOT changed, needs a decision)

`EEG_Dataset_Analysis_and_Preprocessing.ipynb` writes to `E:\REU_DATA\processed\eeg\…`
`Speech_Dataset_Analysis_and_Preprocessing.ipynb` writes to `E:\REU_DATA\processed\speech\…`

The actual outputs live in `EEG processed\eeg\…` and `SPEECH processed\speech\…`, and the
JSON inside them still records the original `…\processed\…` path. `processed\` does not exist.

Consequence: re-running either notebook would create a **second, duplicate** output tree.
Resolving this requires renaming folders or editing notebooks — both await approval.

## Other findings left untouched

- `docs/agents/*.md` are tracked in git but missing on disk (`git status` shows 3 × `D`).
- `.gitignore` ignores only `P*/`; the 1.75 GB `EEG processed\` is untracked and would be staged by `git add -A`.
- Folder names `EEG processed`, `SPEECH processed`, `EEG presentation_figures` contain spaces and mixed casing.
- Questionnaires sit loose at the repository root.
- `information\~$ doubts in REU.docx` is a Word lock file.
