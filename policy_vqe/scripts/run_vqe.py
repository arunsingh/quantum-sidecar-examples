#!/usr/bin/env python3
from policy_vqe.graph_utils import counties_to_graph
from policy_vqe.vqe import RedistrictVQE

counties = ["A", "B", "C"]
edges = [("A", "B"), ("B", "C")]
G = counties_to_graph(counties, edges)

solver = RedistrictVQE(G)
res = solver.optimise()
print(res)
