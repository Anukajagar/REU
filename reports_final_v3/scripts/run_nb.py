"""Execute a notebook cell-by-cell with nbclient, printing progress. Keeps outputs."""
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

path = Path(sys.argv[1])
timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 900

nb = nbformat.read(path, as_version=4)
client = NotebookClient(nb, timeout=timeout, kernel_name="python314-mne",
                        resources={"metadata": {"path": str(path.parent)}},
                        allow_errors=False)
t_all = time.time()
with client.setup_kernel():
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        first = (cell.source.strip().splitlines() or [""])[0][:90]
        t0 = time.time()
        try:
            client.execute_cell(cell, i)
        except Exception as e:
            print(f"FAIL cell {i}: {first}", flush=True)
            nbformat.write(nb, path)
            print("notebook saved with outputs up to the failure", flush=True)
            raise
        dt = time.time() - t0
        err = any(o.get("output_type") == "error" for o in cell.get("outputs", []))
        flag = " ERROR" if err else ""
        print(f"ok cell {i:3d} {dt:7.1f}s{flag}  {first}", flush=True)
        if err:
            nbformat.write(nb, path)
            raise RuntimeError(f"cell {i} produced an error")
print(f"ALL OK in {time.time()-t_all:.1f}s", flush=True)
nbformat.write(nb, path)
print("saved:", path)
