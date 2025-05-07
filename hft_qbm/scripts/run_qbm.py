#!/usr/bin/env python3
import os, torch
from hft_qbm.datasets import make_orderbook
from hft_qbm.qbm import QBMHead

df = make_orderbook(2000)
X = torch.tensor(df[["bid", "ask", "depth"]].values, dtype=torch.float32)
model = QBMHead(input_dim=3)
out = model(X[:64])
print("Sampler output:", out[:10])
