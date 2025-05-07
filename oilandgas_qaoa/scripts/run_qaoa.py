#!/usr/bin/env python3
"""
End‑to‑end QAOA seismic feature‑selection demo.
Run inside cluster or locally with QPU_GATEWAY_HOST env var.

Arun Singh, arunsingh.in@gmail.com
"""
import os, numpy as np, matplotlib.pyplot as plt
from oilandgas_qaoa.qaoa import build_circuit, submit_via_gateway

PROGRAM, SYM = build_circuit(layers=4)
theta = np.random.uniform(0, np.pi, len(SYM))
result = submit_via_gateway(PROGRAM, SYM, theta, shots=2_000)

print("Expectation:", result["expectation"])
plt.plot(result["bitstring_hist"])
plt.savefig("qaoa_hist.png")
