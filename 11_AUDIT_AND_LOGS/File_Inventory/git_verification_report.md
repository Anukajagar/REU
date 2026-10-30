# Pre-Approval Verification Report — Checks C & D

Date: 2026-10-30 · Session state: **Stage C NOT executed — no files moved.**
Prepared for final-approval review. Related deliverables in this folder:
`path_dependency_report.csv` (check A), `rollback_reverse_mapping.csv` (check B),
`original_file_inventory.csv`, `proposed_file_mapping.csv`, `duplicate_content_candidates.csv`.

---

## INCIDENT LOG — `P01.zip` deleted during this session (NOT by agent operations)

| Field | Value |
|---|---|
| File | `E:\REU_DATA\P01.zip` (582,829,330 bytes) |
| SHA-256 (in original inventory) | recorded in `original_file_inventory.csv` |
| Present at inventory time | yes — hashed successfully at ~17:01 |
| Deleted | **2026-10-30 17:12:03 local** (Recycle Bin metadata `$IDFL8CV.zip` decoded) |
| Current location | `E:\$RECYCLE.BIN\S-1-5-21-1882704363-3647157423-988934180-1001\$RDFL8CV.zip` (size match exact) |
| Restorable | yes — not purged |
| Cause | **Not any agent command.** All agent operations in that window were read-only scans plus new-file writes confined to `11_AUDIT_AND_LOGS\File_Inventory\`. Deletion originated externally (user action or another process). |
| Consequence if not restored | Stage E integrity verification will report 1 missing file (1179/1180 match) |
| Recommended action | Restore via Explorer → Recycle Bin → Restore (returns original name/path), **pending your instruction** |

Pre-flight full re-hash executed at start of checks: **compared 1180 · missing 1 (P01.zip) · hash mismatches 0**.

---

## C. Git verification

### Tracked files (complete list — `git ls-files`)
```
.gitignore
AGENTS.md
README.md
docs/agents/domain.md         (worktree: DELETED, unstaged)
docs/agents/issue-tracker.md  (worktree: DELETED, unstaged)
docs/agents/triage-labels.md  (worktree: DELETED, unstaged)
```

### Findings
1. **Only 6 files are Git-tracked.** The proposed mapping keeps `.gitignore`, `AGENTS.md`,
   `README.md` in place (`Action=STAY`); therefore **zero tracked files are moved, overwritten,
   or modified by the proposed reorganization.**
2. **`docs/agents/*.md` deletions are pre-existing.** They were already `D` (deleted, unstaged)
   in the first `git status` captured at session start (16:59), before any agent write operation.
   - `git diff --stat` shows ONLY these three deletions → no tracked file has content changes.
   - All three exist intact in commit `36cad50` (`git cat-file -e HEAD:<path>` → success).
   - **Recovery when approved:** `git restore docs/agents/domain.md docs/agents/issue-tracker.md docs/agents/triage-labels.md`
   - Not executed — restoration awaits your instruction.
3. **Index state:** no staged changes (`.D` = worktree-side deletions only).
4. **`.gitignore` coverage after reorganization** (verified with `git check-ignore -v`):
   - `P*/` still matches raw data at any depth → `01_RAW_DATA/EEG/P01/…` and
     `01_RAW_DATA/SPEECH/P01/…` remain **ignored**, same as today.
   - `02_PROCESSED_DATA/EEG/Cleaned_FIF/P01/…` also ignored (same rule; matches today's behavior).
   - Non-participant paths (notebooks, QC bundles, docs) remain untracked-and-not-ignored,
     exactly as today. **Net Git impact of the moves: neutral. No `.gitignore` edit needed or proposed.**
5. Untracked content today = all research folders; after moves they re-appear untracked under new
   names — no staged/tracked content is at risk of being clobbered (`git add` is never run by the agent).

## D. Final integrity preparation

| Requirement | Status |
|---|---|
| SHA-256 for every file, before | ✅ `original_file_inventory.csv` — 1,180 rows (path, name, ext, size, mtime, SHA-256) |
| SHA-256 comparison feasible after | ✅ Proposed mapping records destination for every source; comparison = re-hash at new path vs original hash |
| Pre-flight comparison run | ✅ 1,179/1,180 identical · 0 mismatches · 1 missing (`P01.zip`, see incident) |
| Existing baseline preserved | ✅ `INVENTORY_BASELINE.csv` untouched, SHA-256 `8E6491ACF1E9535A56D1B11F12EFDCDF00E9BAA70B646EFCFB3B38C1F0DBC486` (will only change LOCATION at execution, never content) |
| Reverse mapping for rollback | ✅ `rollback_reverse_mapping.csv` — 1,180 rows with per-file `RestoreCommand` |
| Bijection check | ✅ 1,180 unique sources → 1,180 unique destinations · 0 collisions · 0 overwrite conflicts |
| Existing data edited/deleted/renamed by agent so far | ✅ none — only new report files added under `11_AUDIT_AND_LOGS\File_Inventory\` |

### Stage E verification procedure (to run after approved execution)
1. For each of the 1,180 inventory rows: locate file at its proposed destination.
2. Re-hash (SHA-256) and compare with `original_file_inventory.csv`.
3. Pass = hash equal AND count 1,180/1,180. Any mismatch/missing → **halt** and run rollback
   (see B) — restore commands executed deepest-path-first from `rollback_reverse_mapping.csv`,
   then re-hash against the original inventory to confirm full recovery.

### Rollback procedure (if Stage E verification fails)
1. Stop all further operations.
2. Read `rollback_reverse_mapping.csv`, sort rows by `RestoredPath` depth (deepest first),
   execute `RestoreCommand` for every `Action=MOVE` row (source exists → destination path is
   unique because bijection was verified; empty destination directories are created by Move-Item).
   Alternative: run rows in reverse file order — with 0 collisions, any order is safe as long as
   a destination parent is not itself waiting to receive a file (deeper-first guarantees this).
3. Recreate the two originally-empty directories (`audit_finalization_v1\figures`,
   `EEG processed\eeg\figures_v3\ica`) if absent — they are preserved, never deleted, by design.
4. Re-run full SHA-256 comparison vs `original_file_inventory.csv` → require 1,180/1,180.
5. Report result before any retry consideration.
