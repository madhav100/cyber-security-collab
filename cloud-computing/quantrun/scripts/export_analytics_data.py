import json
from collections import defaultdict
from pathlib import Path

SUMMARY_PATH = Path("cluster_results/summary.json")
OUT_PATH = Path("analytics/data/analytics.json")
CPU_REQUEST_CORES = 0.5


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _derive_var_values(rows):
    values = []
    for row in rows:
        var_value = _to_float(row.get("var"))
        if var_value is not None:
            values.append(var_value)
    return values


def _group_var_by_params(rows):
    grouped = defaultdict(list)
    for row in rows:
        mu = _to_float(row.get("mu"))
        sigma = _to_float(row.get("sigma"))
        var_value = _to_float(row.get("var"))
        if mu is None or sigma is None or var_value is None:
            continue
        grouped[(mu, sigma)].append(var_value)

    series = []
    for (mu, sigma), vals in sorted(grouped.items()):
        sorted_vals = sorted(vals)
        n = len(sorted_vals)
        p05_index = max(0, int((n - 1) * 0.05))
        series.append(
            {
                "mu": mu,
                "sigma": sigma,
                "count": n,
                "var_values": sorted_vals,
                "var_p05": sorted_vals[p05_index],
                "var_min": sorted_vals[0],
                "var_max": sorted_vals[-1],
            }
        )

    return series


def main() -> None:
    if not SUMMARY_PATH.exists():
        raise SystemExit(
            f"Missing {SUMMARY_PATH}. Run aggregation first to generate summary data."
        )

    rows = json.loads(SUMMARY_PATH.read_text())
    payload = {
        "cpu_request_cores": CPU_REQUEST_CORES,
        "jobs": rows,
        "var_values": _derive_var_values(rows),
        "var_groups": _group_var_by_params(rows),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT_PATH} with {len(rows)} jobs")


if __name__ == "__main__":
    main()
