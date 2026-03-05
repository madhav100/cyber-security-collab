import json
from pathlib import Path

root = Path("cluster_results/var_mc")
rows = []
for res in root.glob("*/result.json"):
    d = json.loads(res.read_text())
    cfg = d["config"]
    rows.append(
        {
            "run_id": d["run_id"],
            "mu": cfg["mu"],
            "sigma": cfg["sigma"],
            "seed": cfg["seed"],
            "var": d["metric"]["var_value"],
            "duration_s": d["duration_s"],
        }
    )

rows.sort(key=lambda r: (r["sigma"], r["mu"], r["seed"]))
out = Path("cluster_results/summary.json")
out.write_text(json.dumps(rows, indent=2))
print(f"Wrote {out} with {len(rows)} rows")
