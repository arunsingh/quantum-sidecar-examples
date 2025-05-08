"""
oilandgas_qaoa.qaoa
===================

Utilities to build and execute a parameterised QAOA Quil circuit aimed at
pruning seismic-search combinatorial spaces.  Designed to be called from
Flatcar-based Kubernetes workloads *or* local dev laptops.

Public API
----------
build_circuit(layers=4, n_qubits=8)
submit_via_gateway(program, params, values, shots=2000)


--------------------How it works----------
This python is a fully-featured oilandgas_qaoa/qaoa.py module.
It gives you two public helpers exactly as referenced in the earlier Quick-start script:

build_circuit(layers: int = 4, n_qubits: int = 8) -> tuple[str, list[str]]
Returns a parameterised Quil program (string) and the ordered list of symbolic
parameter names (theta[0] … theta[n-1]).

submit_via_gateway(program: str, params: list[str], values: list[float], *, shots: int = 2_000) -> dict
Detects QPU_GATEWAY_HOST in the environment; if present, runs the job via the
gRPC gateway → Rigetti QCS. If absent (local dev), it falls back to Cirq’s
density-matrix simulator.

Both paths return a dictionary:
```bash
{
  "bitstring_hist": dict[str, int],   # '00011001': 113 …
  "expectation": float                # mean(|1⟩) over all shots
}

```

| Topic                 | Detail                                                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Parameter Mapping** | Quil placeholders are literal `theta[0]`, `theta[1]`, …; `submit_via_gateway` packages them into the `params` map expected by the gateway.                                           |
| **Local Fallback**    | Uses **Cirq’s** `DensityMatrixSimulator` so offline developers (or CI) can still execute the pipeline without Rigetti credentials.                                                   |
| **Return Type**       | A `@dataclass` (`QuilResult`) for readability; plain `dict` in JSON-serialisable form.                                                                                               |
| **Minimal Parser**    | `_submit_local` includes a tiny, *non-robust* translator from a subset of Quil to Cirq gates—good enough for demo, but feel free to swap in `qcel` or `cirq-rigetti` for production. |


"""

from __future__ import annotations

import os
import json
import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple, Dict

import numpy as np

# -- Optional imports ---------------------------------------------------------
_QPU_HOST = os.getenv("QPU_GATEWAY_HOST")
if _QPU_HOST:
    try:
        import grpc

        from gateways.qpu_gateway.proto import quantum_pb2, quantum_pb2_grpc  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "QPU_GATEWAY_HOST env var set but gRPC client stubs missing. "
            "Run `pip install -e gateways/qpu_gateway/` or unset the env."
        ) from exc
else:
    # local simulation fallback
    import cirq


# --------------------------------------------------------------------------- #
# 1.  Circuit construction helper                                             #
# --------------------------------------------------------------------------- #
def build_circuit(layers: int = 4, n_qubits: int = 8) -> Tuple[str, List[str]]:
    """
    Build a parameterised QAOA Quil circuit.

    Parameters
    ----------
    layers : int
        Depth `p` of QAOA (alternating RX and ZZ entangling layers).
    n_qubits : int
        Number of qubits / problem bits.

    Returns
    -------
    program : str
        Quil source with DECLARE statements and param placeholders
        `theta[0] … theta[m-1]`.
    params : list[str]
        Ordered list of parameter names to be substituted at run-time.
    """
    param_syms = [f"theta[{i}]" for i in range(layers * 2)]
    prog_lines = ["DECLARE ro BIT[1]"]
    # Layer construction -----------------------------------------------------
    sym_iter = iter(param_syms)
    for _layer in range(layers):
        beta = next(sym_iter)
        gamma = next(sym_iter)
        # Single-qubit RX rotations
        for q in range(n_qubits):
            prog_lines.append(f"RX({beta}) {q}")
        # Entangling ZZ between line qubits
        for q in range(n_qubits - 1):
            prog_lines.append(f"CZ {q} {q+1}")
            prog_lines.append(f"RZ({gamma}) {q+1}")
            prog_lines.append(f"CZ {q} {q+1}")
    # Measure first qubit to keep example small
    prog_lines.append("MEASURE 0 ro[0]")
    program = "\n".join(prog_lines)
    return program, param_syms


# --------------------------------------------------------------------------- #
# 2.  Execution helper (gateway OR local sim)                                 #
# --------------------------------------------------------------------------- #
@dataclass
class QuilResult:
    bitstring_hist: Dict[str, int]
    expectation: float


def submit_via_gateway(
    program: str,
    params: list[str],
    values: list[float] | np.ndarray,
    *,
    shots: int = 2_000,
) -> QuilResult | dict:
    """
    Run a parameterised Quil program either on a Rigetti QPU via the quantum
    side-car gateway **or** locally using Cirq's density-matrix simulator.

    Parameters
    ----------
    program : str
        Quil source with parameter symbols (as produced by ``build_circuit``).
    params : list[str]
        Ordered list of parameter names.
    values : list[float] or np.ndarray
        Substitution values (same length as ``params``).
    shots : int
        Number of shots / samples.

    Returns
    -------
    dict
        { "bitstring_hist": { '0...': int, '1...': int, ... },
          "expectation": float }
    """
    if _QPU_HOST:
        return _submit_remote(program, params, values, shots)  # type: ignore
    return _submit_local(program, params, values, shots)  # type: ignore


# -------------------------------------------------------------------- helpers


def _submit_remote(program: str, params: list[str], values, shots: int) -> QuilResult:
    """Send RunQuilRequest over gRPC; stream results back."""
    param_dict = {k: float(v) for k, v in zip(params, values)}
    req = quantum_pb2.RunQuilRequest(program=program, shots=shots, params=param_dict)

    channel = grpc.insecure_channel(_QPU_HOST)
    stub = quantum_pb2_grpc.QuantumServiceStub(channel)

    histogram: Counter[str] = Counter()
    for resp in stub.RunQuil(req):
        histogram.update(map(str, resp.ro))  # server returns list[int] = bit 0/1
    total_shots = sum(histogram.values())
    expectation = histogram.get("1", 0) / total_shots
    return QuilResult(dict(histogram), expectation)


def _submit_local(
    program: str,
    params: list[str],
    values,
    shots: int,
) -> QuilResult:
    """Use Cirq density-matrix simulator as offline fallback."""
    # Convert Quil -> Cirq quickly (primitive, demo-only)
    q_count = _count_qubits(program)
    qs = cirq.LineQubit.range(q_count)
    circuit = cirq.Circuit()
    # Replace params inline
    for line in program.splitlines():
        if line.startswith("DECLARE") or line.startswith("MEASURE"):
            continue
        for k, v in zip(params, values):
            line = line.replace(k, str(v))
        toks = line.split()
        gate, *args = toks
        if gate.startswith("RX"):
            angle = float(gate[3:-1])
            circuit += cirq.rx(angle)(qs[int(args[0])])
        elif gate == "CZ":
            circuit += cirq.CZ(qs[int(args[0])], qs[int(args[1])])
        elif gate.startswith("RZ"):
            angle = float(gate[3:-1])
            circuit += cirq.rz(angle)(qs[int(args[0])])
    sim = cirq.DensityMatrixSimulator()
    result = sim.run(circuit, repetitions=shots)
    bits = ["".join(map(str, r[::-1])) for r in result.measurements.values()][0]
    hist = dict(Counter(bits))
    expectation = bits.count("1") / shots
    return QuilResult(hist, expectation)


def _count_qubits(program: str) -> int:
    """Naïve scan to guess highest qubit index."""
    hi = 0
    for line in program.splitlines():
        for tok in line.split():
            if tok.isdigit():
                hi = max(hi, int(tok))
    return hi + 1
