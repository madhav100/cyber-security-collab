import json
import pathlib
import subprocess
import uuid

TEMPLATE = pathlib.Path("k8s/jobs/model-job.yaml").read_text()

messages = ["quick-smoke", "k8s-batch", "hello-cluster"]
repeats = [1, 2, 3]
sleeps = [10, 25]


def apply_job(run_id: str, cfg: dict):
    yml = TEMPLATE.replace("REPLACE_RUNID", run_id)
    yml = yml.replace("REPLACE_CONFIGJSON", json.dumps(cfg).replace('"', '\\"'))
    p = pathlib.Path("k8s/workflows/generated")
    p.mkdir(parents=True, exist_ok=True)
    f = p / f"job-{run_id}.yaml"
    f.write_text(yml)
    subprocess.check_call(["kubectl", "apply", "-f", str(f)])


count = 0
for message in messages:
    for repeat in repeats:
        for sleep_ms in sleeps:
            run_id = f"smoke-{count:03d}-{uuid.uuid4().hex[:6]}"
            cfg = {"message": message, "repeat": repeat, "sleep_ms": sleep_ms}
            apply_job(run_id, cfg)
            count += 1

print(f"submitted {count} jobs")
