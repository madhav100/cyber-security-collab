import json
import math
import os
import random
import time
from pathlib import Path


def mc_var(mu: float, sigma: float, n: int, seed: int, alpha: float = 0.05):
    rng = random.Random(seed)
    samples = []
    for _ in range(n):
        # simple normal using Box-Muller
        u1 = max(rng.random(), 1e-12)
        u2 = rng.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        r = mu + sigma * z
        samples.append(r)

    samples.sort()
    idx = int(alpha * n)
    return samples[idx]


def main():
    model = os.environ.get("MODEL", "var_mc")
    run_id = os.environ.get("RUN_ID", "run-000")
    cfg_json = os.environ.get("CONFIG_JSON", "{}")
    out_dir = os.environ.get("OUT_DIR", "/output")

    cfg = json.loads(cfg_json)
    mu = float(cfg.get("mu", 0.0005))
    sigma = float(cfg.get("sigma", 0.01))
    n = int(cfg.get("n", 200000))
    seed = int(cfg.get("seed", 42))
    alpha = float(cfg.get("alpha", 0.05))

    start = time.time()
    var = mc_var(mu, sigma, n, seed, alpha)
    end = time.time()

    p = Path(out_dir) / model / run_id
    p.mkdir(parents=True, exist_ok=True)

    meta = {
        "model": model,
        "run_id": run_id,
        "config": cfg,
        "started_at": start,
        "finished_at": end,
        "duration_s": end - start,
        "metric": {"var_alpha": alpha, "var_value": var},
    }

    (p / "result.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
