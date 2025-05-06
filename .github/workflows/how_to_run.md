# How to Install and run end-to-end 🚀🧑‍🚀

## 1. Prerequisites

- Kubernetes ≥ 1.27 (Flatcar/Ubuntu OK)

- Helm, Linkerd (or skip for non‑mTLS)

- Rigetti QCS account & API key

- Docker registry (GHCR by default)  

## 2. Deploy Gateway

```
kubectl create ns quantum
kubectl create secret generic rigetti-creds -n quantum \
  --from-literal=apiKey=$RIGETTI_KEY \
  --from-literal=apiSecret=$RIGETTI_SECRET

helm upgrade --install qpu-gw charts/qpu-gateway \
  --namespace quantum \
  --set global.image.tag=v0.1.0

```
## 3. Port‑forward & Test

```
kubectl -n quantum port-forward svc/qpu-gateway 50051:50051 &
python oilandgas_qaoa/examples/ping.py


Expected:

Connected to gateway
Result expectation 0.5012



```

## 4. Run Notebook

```
docker run --rm -it -p 8888:8888 \
  -e QPU_GATEWAY_HOST=qpu-gateway.quantum:50051 \
  ghcr.io/arunsingh/qruntime:0.1.0
# open browser http://localhost:8888

```

## 5. Scale Gateway

```
kubectl -n quantum scale deploy/qpu-gateway --replicas=4

```