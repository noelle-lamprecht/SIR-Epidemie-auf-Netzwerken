# Example of a Watts-Strogatz random graph

import matplotlib.pyplot as plt
import networkx as nx

# Parameters: 50 people, each starts with 4 fixed neighbors, 10% rewiring
N = 50
K = 4
P_REWIRE = 0.10

# Generate the network
ws_graph = nx.watts_strogatz_graph(n=N, k=K, p=P_REWIRE, seed=42)

# Draw the graph in a circular layout to show the original ring and shortcuts
plt.figure(figsize=(6, 6))
pos = nx.circular_layout(ws_graph)
nx.draw_networkx(ws_graph, pos, node_size=150, node_color="lightgreen", with_labels=False)
plt.title(f"Watts-Strogatz small-world graph (N={N}, k={K}, p_rewire={P_REWIRE})")
plt.show()