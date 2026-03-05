import json
from pathlib import Path

root = Path("cluster_results/simple_job")
rows = []
for res in root.glob("*/result.json"):
    d = json.loads(res.read_text())
    cfg = d.get("config", {})
    metric = d.get("metric", {})
    rows.append(
        {
            "run_id": d["run_id"],
            "message": cfg.get("message", ""),
            "repeat": int(cfg.get("repeat", 1)),
            "sleep_ms": int(cfg.get("sleep_ms", 0)),
            "value": metric.get("output_chars", 0),
            "lines_printed": metric.get("lines_printed", 0),
            "duration_s": d["duration_s"],
        }
    )

rows.sort(key=lambda r: (r["message"], r["repeat"], r["sleep_ms"], r["run_id"]))
out = Path("cluster_results/summary.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(rows, indent=2))
print(f"Wrote {out} with {len(rows)} rows")
