"""
Hybrid VQE optimiser that off‑loads energy evaluation to Rigetti QCS
if QPU_GATEWAY_HOST is provided; otherwise uses PyQuil's QVM.
"""
import os, json, grpc
import numpy as np
from scipy.optimize import minimize
from pyquil import Program
from pyquil.paulis import sZ
from pyquil.api import get_qc, QuantumComputer

_QPU_HOST = os.getenv("QPU_GATEWAY_HOST")
if _QPU_HOST:
    import quantum_pb2, quantum_pb2_grpc

class RedistrictVQE:
    def __init__(self, graph, shots=1000):
        self.graph = graph
        self.n_qubits = len(graph.nodes)
        self.shots = shots
        self.qc: QuantumComputer | None = (
            None if _QPU_HOST else get_qc("9q-square-qvm")
        )

    def _ansatz(self, params):
        prog = Program()
        for q, th in enumerate(params):
            prog += Program(f"RX({th}) {q}")
        return prog

    def _energy(self, params):
        prog = self._ansatz(params)
        if _QPU_HOST:
            return self._energy_qpu(prog, params)
        return self._energy_qvm(prog)

    def _energy_qvm(self, prog):
        bitstrings = self.qc.run_and_measure(prog, self.shots)
        return np.random.rand()  # placeholder

    def _energy_qpu(self, prog, params):
        channel = grpc.insecure_channel(_QPU_HOST)
        stub = quantum_pb2_grpc.QuantumServiceStub(channel)
        req = quantum_pb2.RunQuilRequest(
            program=prog.out(),
            shots=self.shots,
            params={f"theta[{i}]": float(p) for i, p in enumerate(params)},
        )
        ro = []
        for resp in stub.RunQuil(req):
            ro.extend(resp.ro)
        return np.mean(ro)

    def optimise(self):
        init = np.random.uniform(0, 2 * np.pi, size=self.n_qubits)
        res = minimize(self._energy, init, method="COBYLA", options={"maxiter": 50})
        return res
