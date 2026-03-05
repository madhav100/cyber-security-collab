# QuantRun — Docker + Kubernetes Batch Platform (Financial Model Sweeps)

Run Monte Carlo / parameter-sweep jobs as Kubernetes Jobs using one Docker image, write outputs to a PVC, and aggregate results locally.

## Project structure

```
quantrun/
├── common/
├── docker/
│   └── Dockerfile
├── k8s/
│   ├── jobs/
│   │   └── model-job.yaml
│   ├── namespaces.yaml
│   └── workflows/
│       └── helper-pod.yaml
├── models/
│   └── var_mc/
│       └── run.py
├── results/
└── scripts/
    ├── aggregate.py
    └── submit_sweep.py
```

## 1) Build and test locally

```bash
cd quantrun
docker build -f docker/Dockerfile -t quantrun:local .

docker run --rm \
  -e MODEL=var_mc \
  -e RUN_ID=test-001 \
  -e CONFIG_JSON='{"mu":0.0003,"sigma":0.012,"n":50000,"seed":7,"alpha":0.05}' \
  -e OUT_DIR=/output \
  -v "$PWD/results:/output" \
  quantrun:local

cat results/var_mc/test-001/result.json
```

## 2) Start local Kubernetes

Use either kind or minikube.

```bash
# kind
kind create cluster --name quantrun

# or minikube
minikube start
```

## 3) Load image into cluster

```bash
# kind
kind load docker-image quantrun:local --name quantrun

# minikube
eval "$(minikube -p minikube docker-env)"
docker build -f docker/Dockerfile -t quantrun:local .
```

## 4) Create namespace and PVC

```bash
kubectl apply -f k8s/namespaces.yaml
```

## 5) Submit a 200-job sweep

```bash
python scripts/submit_sweep.py
```

## 6) Track status

```bash
kubectl -n quant-dev get jobs
kubectl -n quant-dev get pods -w
kubectl -n quant-dev logs <pod-name>
```

## 7) Pull and aggregate results

```bash
kubectl apply -f k8s/workflows/helper-pod.yaml
kubectl -n quant-dev cp results-helper:/output ./cluster_results
python scripts/aggregate.py
```

## 8) Cleanup

```bash
kubectl -n quant-dev delete jobs --all
kubectl -n quant-dev delete pod results-helper
kubectl delete ns quant-dev
```

## Next upgrades

- Switch to Kubernetes Indexed Jobs for cleaner sweep indexing.
- Add checkpointing to periodically persist partial run state.
- Add a submit API and optional web UI.
- Add Prometheus/Grafana metrics for jobs.
- Move results to object storage for non-local clusters.
