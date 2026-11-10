"""CLI for EEG feature extraction (v1).

Examples
--------
Full extraction (refuses to overwrite existing outputs):
    py -3.14 "EEG features/scripts/extract_eeg_features.py"

Deliberate rebuild:
    py -3.14 "EEG features/scripts/extract_eeg_features.py" --force

Pilot to a temporary folder (one recording):
    py -3.14 "EEG features/scripts/extract_eeg_features.py" --limit P01_calm \
        --out-dir "C:\\Users\\anush\\AppData\\Local\\Temp\\opencode\\eeg_pilot" --force
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import eeg_feature_lib as lib  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=lib.OUT_DIR,
                        help=f"output directory (default: {lib.OUT_DIR})")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing outputs (delete deliberately otherwise)")
    parser.add_argument("--limit", type=str, default="",
                        help="comma-separated recording IDs, e.g. P01_calm,P02_maths")
    parser.add_argument("--no-figures", action="store_true", help="skip figure generation")
    args = parser.parse_args()

    limit = [s.strip() for s in args.limit.split(",") if s.strip()] or None
    result = lib.run_extraction(
        out_dir=args.out_dir,
        force=args.force,
        limit=limit,
        make_plots=not args.no_figures,
    )
    print("\nDONE")
    for k, v in result["outputs"].items():
        print(f"  {k:12s} {v}")
    for p in result["figures"]:
        print(f"  figure       {p}")
    print(f"  recordings   {result['n_recordings']}")
    print(f"  runtime_s    {result['runtime_s']:.1f}")


if __name__ == "__main__":
    main()
