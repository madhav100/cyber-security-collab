import json
from collections import defaultdict
from pathlib import Path

SUMMARY_PATH = Path("cluster_results/summary.json")
OUT_PATH = Path("analytics/data/analytics.json")
CPU_REQUEST_CORES = 0.1


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _metric_value(row):
    # prefer simplified metric name; keep compatibility with older summaries
    return _to_float(row.get("value", row.get("var")))


def _derive_values(rows):
    values = []
    for row in rows:
        metric_value = _metric_value(row)
        if metric_value is not None:
            values.append(metric_value)
    return values


def _group_values(rows):
    grouped = defaultdict(list)
    for row in rows:
        message = str(row.get("message", "unknown"))
        repeat = int(row.get("repeat", 0) or 0)
        metric_value = _metric_value(row)
        if metric_value is None:
            continue
        grouped[(message, repeat)].append(metric_value)

    series = []
    for (message, repeat), vals in sorted(grouped.items()):
        sorted_vals = sorted(vals)
        n = len(sorted_vals)
        p05_index = max(0, int((n - 1) * 0.05))
        series.append(
            {
                "message": message,
                "repeat": repeat,
                "count": n,
                "values": sorted_vals,
                "p05": sorted_vals[p05_index],
                "min": sorted_vals[0],
                "max": sorted_vals[-1],
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
        "value_values": _derive_values(rows),
        "value_groups": _group_values(rows),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT_PATH} with {len(rows)} jobs")


if __name__ == "__main__":
    main()
