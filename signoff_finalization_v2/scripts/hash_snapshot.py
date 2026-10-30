r"""Snapshot SHA-256 of every file under E:\REU_DATA except .git and the output folder of this pass.

Read-only. Writes one JSON line per file plus a summary to the given output path.
Used before and after the signoff_finalization_v2 pass to prove no protected file changed.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"E:\REU_DATA")
EXCLUDE_DIRS = {".git", "signoff_finalization_v2"}


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> None:
    out_path = Path(sys.argv[1])
    rows = []
    t0 = time.time()
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if rel.parts and rel.parts[0] in EXCLUDE_DIRS:
            continue
        try:
            rows.append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "size": p.stat().st_size,
                    "sha256": sha256(p),
                }
            )
        except (OSError, PermissionError) as exc:  # pragma: no cover
            rows.append({"path": str(rel).replace("\\", "/"), "error": str(exc)})
    summary = {
        "files": len(rows),
        "errors": sum(1 for r in rows if "error" in r),
        "total_bytes": sum(r.get("size", 0) for r in rows),
        "seconds": round(time.time() - t0, 1),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "files": rows}, f)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
