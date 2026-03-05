import json
import os
import time
from pathlib import Path


def main():
    model = os.environ.get("MODEL", "simple_job")
    run_id = os.environ.get("RUN_ID", "run-000")
    cfg_json = os.environ.get("CONFIG_JSON", "{}")
    out_dir = os.environ.get("OUT_DIR", "/output")

    cfg = json.loads(cfg_json)
    message = str(cfg.get("message", "hello-from-k8s-job"))
    repeat = int(cfg.get("repeat", 1))
    sleep_ms = int(cfg.get("sleep_ms", 50))

    start = time.time()
    output_lines = []
    for i in range(max(1, repeat)):
        line = f"[{run_id}] {message} #{i + 1}"
        print(line)
        output_lines.append(line)
        time.sleep(max(0, sleep_ms) / 1000)
    end = time.time()

    p = Path(out_dir) / model / run_id
    p.mkdir(parents=True, exist_ok=True)

    summary_value = sum(len(line) for line in output_lines)
    meta = {
        "model": model,
        "run_id": run_id,
        "config": cfg,
        "started_at": start,
        "finished_at": end,
        "duration_s": end - start,
        "metric": {
            "output_chars": summary_value,
            "lines_printed": len(output_lines),
        },
    }

    (p / "result.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
