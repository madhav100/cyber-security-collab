# QuantRun — Docker + Kubernetes Batch Platform (Lightweight Job Smoke Tests)

Run simple Kubernetes Jobs using one Docker image, write outputs to a PVC, and aggregate results locally.

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
│   └── simple_job/
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
  -e MODEL=simple_job \
  -e RUN_ID=test-001 \
  -e CONFIG_JSON='{"message":"hello-local","repeat":2,"sleep_ms":10}' \
  -e OUT_DIR=/output \
  -v "$PWD/results:/output" \
  quantrun:local

cat results/simple_job/test-001/result.json
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

## 5) Submit a lightweight sweep

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

## 9) Analytics dashboard

Generate analytics input from your aggregated summary:

```bash
python scripts/export_analytics_data.py
```

Serve the dashboard locally:

```bash
cd analytics
python -m http.server 8000
```

Open `http://localhost:8000` to view:
- Kubernetes compute KPIs (job count, average/p95 duration, compute score)
- Job duration timeline
- Job output distribution (P05 marker)
