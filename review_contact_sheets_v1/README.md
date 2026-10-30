# ICA component-map review contact sheets (v1)

Review-only visual aids for the ICA sign-off pass. **No verdict, disposition, guard result or
sign-off decision is assigned, inferred or written by this folder.** Labels reproduce values
already present in the packet manifest, verbatim.

## Outputs

| Path | What it is |
|---|---|
| `E:\REU_DATA\review_contact_sheets_v1\contact_sheet_ica_maps_all30_v1.png` | Contact sheet, all 30 ICA recording maps (5 x 6), each tile labelled `participant \| condition` + `removed components: [...]` (2360 x 3474) |
| `E:\REU_DATA\review_contact_sheets_v1\contact_sheet_near_guard_3_v1.png` | Contact sheet, the 3 near-guard recordings: P02 calm, P06 maths, P09 maths (2040 x 1008) |
| `E:\REU_DATA\review_contact_sheets_v1\contact_sheet_labels_all30_v1.csv` | Label table behind both sheets: participant, condition, recording, `components_removed`, source ZIP entry, per-image SHA-256, frozen-original path (33 rows = 30 + 3) |
| `E:\REU_DATA\review_contact_sheets_v1\build_contact_sheets_v1.py` | Script that regenerates the two PNGs and the CSV (read-only against sources) |

## Sources (read-only)

- `E:\REU_DATA\EEG processed\quality_control\ica_signoff_packet_v2_review.zip`
  - `component_maps/*.png` (30 images, read from the ZIP in memory, never extracted in place)
  - `packet_manifest_v2.csv` (source of `participant`, `condition`, `components_removed`,
    `near_guard_flag`)
- `E:\REU_DATA\EEG processed\eeg\figures_v2\ica\` — frozen originals, opened read-only for
  byte-identity comparison only.

Tile order: participant ascending, then condition calm -> maths -> meditation.
Near-guard tile order: P02_calm, P06_maths, P09_maths as requested.

## Verification performed

- 30/30 manifest rows present; 30/30 component-map PNGs found in the ZIP.
- 30/30 bundled PNGs byte-identical (SHA-256) to the frozen originals in `figures_v2\ica\`.
- The 3 requested near-guard recordings match the manifest's `near_guard_flag == YES` set exactly
  (P02_calm, P06_maths, P09_maths).
- Source ZIP SHA-256 before and after the build: `B86EFABA5CEB0FD39F9AAECEE11610B66106A44D3D8262C31C385E0427D2489E`
  (unchanged).
- Frozen figure folder still holds 30 PNGs; newest mtime `2026-10-10 22:11:22` (no writes today).

## Not touched

Raw `P01`-`P10`, `EEG processed\eeg\figures_v2\`, `audit_finalization_v1\`, `reports_final_v3\`,
both packet trees (`ica_signoff_packet*`), the packet ZIPs, and `INVENTORY_BASELINE.csv` were all
read only. Nothing was moved, renamed, edited or deleted.
