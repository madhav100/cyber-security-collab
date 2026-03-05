import itertools
import json
import pathlib
import subprocess
import uuid

TEMPLATE = pathlib.Path("k8s/jobs/model-job.yaml").read_text()

# Example grid: 10 sigmas x 10 mus x 2 seeds = 200 jobs
sigmas = [0.006 + 0.001 * i for i in range(10)]
mus = [0.0001 + 0.00005 * i for i in range(10)]
seeds = [11, 22]  # 2 seeds


def apply_job(run_id: str, cfg: dict):
    yml = TEMPLATE.replace("REPLACE_RUNID", run_id)
    yml = yml.replace("REPLACE_CONFIGJSON", json.dumps(cfg).replace('"', '\\"'))
    p = pathlib.Path("k8s/workflows/generated")
    p.mkdir(parents=True, exist_ok=True)
    f = p / f"job-{run_id}.yaml"
    f.write_text(yml)
    subprocess.check_call(["kubectl", "apply", "-f", str(f)])


count = 0
for sigma, mu, seed in itertools.product(sigmas, mus, seeds):
    run_id = f"sweep-{count:03d}-{uuid.uuid4().hex[:6]}"
    cfg = {"mu": mu, "sigma": sigma, "n": 50000, "seed": seed, "alpha": 0.05}
    apply_job(run_id, cfg)
    count += 1

print(f"submitted {count} jobs")
