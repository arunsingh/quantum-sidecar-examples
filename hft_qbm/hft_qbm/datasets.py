import numpy as np
import pandas as pd

def make_orderbook(n_rows: int = 2_000) -> pd.DataFrame:
    """Synthetic limit‑order‑book with bid/ask depth and micro‑price."""
    ts = pd.date_range("2025-05-01", periods=n_rows, freq="200ms")
    bid = 100 + np.cumsum(np.random.randn(n_rows) * 0.02)
    ask = bid + np.abs(np.random.randn(n_rows) * 0.01)
    depth = np.random.randint(100, 400, size=n_rows)
    return pd.DataFrame({"ts": ts, "bid": bid, "ask": ask, "depth": depth})
