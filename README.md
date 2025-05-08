# Quantum‑Sidecar‑Examples 🚀🔗🧑‍🚀  

**Hybrid GPU + Rigetti QPU workflows, deployable on a Flatcar‑based Kubernetes cluster.**  
Three domain projects:

* `oilandgas_qaoa` – QAOA feature‑selection for seismic exploration  
* `hft_qbm` – QuantumbBoltzmann Machine sampler for high‑frequency trading volatility forecasts  
* `policy_vqe` – VQE optimisation for fair redistricting

The repo also contains:

* **`qpu_gateway`** – small Go gRPC service that multiplexes calls to Rigetti QCS, with Redis cache  
* **Helm chart** to deploy gateway + Redis (mTLS ready for Linkerd)  
* **Slim Python runtime** Dockerfile (multi‑arch) for notebooks & batch jobs  
* **GitHub Actions CI** (build images, produce SBOM, Cosign sign)  

---

## Quick Start

```bash
git clone https://github.com/arunsingh/quantum-sidecar-examples
cd quantum-sidecar-examples

# Build runtime container
docker buildx build --push \
  -f docker/runtime/Dockerfile \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/arunsingh/qruntime:0.1.0 .

# Build gateway
cd gateways/qpu_gateway
make docker-push   # multi-arch, tag ghcr.io/arunsingh/qpu-gateway:v0.1.0

```

## How to test Quickly : Oil and Gas QAOA Search Space Optimisation

```bash
python - <<'PY'
from oilandgas_qaoa.qaoa import build_circuit, submit_via_gateway
prog, syms = build_circuit(layers=2, n_qubits=4)
vals = [0.3, 0.7, 1.2, 2.4]
print("running locally…")
out = submit_via_gateway(prog, syms, vals, shots=1024)
print(out)
PY
# If QPU_GATEWAY_HOST is unset, you’ll get a Cirq-simulated result; set the env and it will route through the gateway 
```

## High‑Frequency Trading (Quantum Boltzmann Machine)

```bash
# Build runtime incl. qiskit
docker build -t qruntime:hft -f docker/runtime/Dockerfile docker/runtime

export QPU_GATEWAY_HOST=qpu-gateway.quantum:50051
python -m hft_qbm.notebooks.run_qbm   # or open notebook 02_qbm_hft.ipynb
```

## Redistricting Optimiser (VQE) : patching graph utils

```
pip install -e policy_vqe
python - <<'PY'
from policy_vqe.graph_utils import counties_to_graph
from policy_vqe.vqe import RedistrictVQE
G = counties_to_graph(['A','B','C'], [('A','B'),('B','C')])
solver = RedistrictVQE(G)
print(solver.optimise())
PY

```


# prerequisites:
Docker>23, docker buildx, Go1.22, Python3.11, yq, kubectl, helm, and a Rigetti QCS API key.

## Kubernetes deploy (Flatcar cluster)
```
helm install qpu-gw charts/qpu-gateway \
  --set global.image.tag=v0.1.0 \
  --set rigetti.apiKey=$(cat ~/.qcs/apiKey) \
  --set rigetti.apiSecret=$(cat ~/.qcs/secret)

```
- Linkerd mTLS auto‑injects.

- Redis is deployed as sidecar by default (redis.disabled=false to use external redis).

## Running a Notebook
```
python -m venv .venv && source .venv/bin/activate
pip install -r oilandgas_qaoa/requirements.txt
jupyter lab oilandgas_qaoa/notebooks/01_qaoa_seismic.ipynb

```
Configure environment:
```
export QPU_GATEWAY_HOST=qpu-gw.default.svc.cluster.local:50051
export RIGETTI_API_KEY=xxx
export RIGETTI_API_SECRET=yyy

```
Enjoy hybrid quantum + GPU optimisation! 🎉

## Repo Structure
| Path                   | Purpose                                 |
| ---------------------- | --------------------------------------- |
| `charts/qpu-gateway`   | Helm chart for gateway + Redis          |
| `docker/runtime`       | slim python:3.11‑slim + CUDA 12 runtime |
| `gateways/qpu_gateway` | Go source & Dockerfile                  |
| `oilandgas_qaoa`       | Cirq QAOA package & notebook            |
| `hft_qbm`              | Qiskit QBM package & notebook           |
| `policy_vqe`           | PyQuil VQE package & notebook           |


## Security & Compliance

- SBOM generated via Syft, uploaded as build artifact.

- Cosign signs every image (cosign verify ghcr.io/arunsingh/qpu-gateway:v0.1.0).

- Kyverno sample policy located in charts/qpu-gateway/kyverno/.

## Roadmap

- Add AzureQ nodes (IonQ).

- Auto‑scaling gRPC gateway (Envoy xDS).

- Fine‑grained cost analytics ($/shot, $/call) to Prometheus.

PRs welcome! 🙏
