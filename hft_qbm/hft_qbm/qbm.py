"""
Quantum Boltzmann Machine sampler wrapped in helper class.
Executed via side‑car gateway if QPU_HOST env var set, else falls back to local qiskit‑aer.
"""

import os, json, grpc
import numpy as np
import qiskit as qk
from qiskit_machine_learning.neural_networks import SamplerQNN
from qiskit_machine_learning.connectors import TorchConnector
import torch, torch.nn as nn

# Optional: connect to gateway
_QPU_HOST = os.getenv("QPU_GATEWAY_HOST")

if _QPU_HOST:
    import quantum_pb2, quantum_pb2_grpc  # generated via proto

class QBMHead(nn.Module):
    def __init__(self, input_dim: int = 16, n_qubits: int = 8):
        super().__init__()
        self.linear = nn.Linear(input_dim, n_qubits)

        qc = qk.QuantumCircuit(n_qubits)
        qc.h(range(n_qubits))
        for i in range(n_qubits - 1):
            qc.cz(i, i + 1)
        self.qnn = SamplerQNN(
            circuit=qc,
            sampling=True,
            shots=1024,
        )
        self.model = TorchConnector(self.qnn)

    def forward(self, x):
        z = self.linear(x)
        if _QPU_HOST:
            return self._forward_qpu(z)
        return self.model(z)

    def _forward_qpu(self, z):
        """Call gateway -> Rigetti QPU."""
        channel = grpc.insecure_channel(_QPU_HOST)
        stub = quantum_pb2_grpc.QuantumServiceStub(channel)

        probs = []
        for row in z:
            param_dict = {f"theta[{i}]": float(val) for i, val in enumerate(row)}
            req = quantum_pb2.RunQuilRequest(
                program=self._quil_template(), shots=1024, params=param_dict
            )
            ro = []
            for resp in stub.RunQuil(req):
                ro.extend(resp.ro)
            probs.append(np.mean(ro))
        return torch.tensor(probs).unsqueeze(1)

    @staticmethod
    def _quil_template():
        return "DECLAREro BIT[1]\nH 0\nMEASURE 0 ro[0]"
