import networkx as nx

def counties_to_graph(counties, adjacencies):
    """
    counties: list[str]; adjacencies: list[tuple[str,str]]
    returns NetworkX Graph (undirected)
    """
    G = nx.Graph()
    G.add_nodes_from(counties)
    G.add_edges_from(adjacencies)
    return G
