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
