# Erdős-Rényi random graph example
import matplotlib.pyplot as plt
import networkx as nx

# Parameters
N = 50 # number of nodes (people)
P = 0.10 # probability of connection = 10%

# Generate the network
er_graph = nx.erdos_renyi_graph(n=N, p=P,)

# Draw the graph
plt.figure(figsize=(6, 6))
nx.draw_networkx(er_graph, node_size=150, node_color="lightblue", with_labels=False)
plt.title(f"Erdős-Rényi random graph (N={N}, p={P})")
plt.show()