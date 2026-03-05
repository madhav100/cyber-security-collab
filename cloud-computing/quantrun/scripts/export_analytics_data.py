import json
from pathlib import Path

SUMMARY_PATH = Path("cluster_results/summary.json")
OUT_PATH = Path("analytics/data/analytics.json")
CPU_REQUEST_CORES = 0.5


def main() -> None:
    if not SUMMARY_PATH.exists():
        raise SystemExit(
            f"Missing {SUMMARY_PATH}. Run aggregation first to generate summary data."
        )

    rows = json.loads(SUMMARY_PATH.read_text())
    payload = {
        "cpu_request_cores": CPU_REQUEST_CORES,
        "jobs": rows,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT_PATH} with {len(rows)} jobs")


if __name__ == "__main__":
    main()
