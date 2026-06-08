import matplotlib.pyplot as plt
import networkx as nx

# Parameter: 50 Personen, jeder startet mit 4 festen Nachbarn, 10% Neuverdrahtung
N = 50
K = 4
P_REWIRE = 0.10

# Netzwerk generieren
ws_graph = nx.watts_strogatz_graph(n=N, k=K, p=P_REWIRE, seed=42)

# Zeichnen (im Kreis-Layout, um den ursprünglichen Ring und die Abkürzungen zu sehen)
plt.figure(figsize=(6, 6))
pos = nx.circular_layout(ws_graph)
nx.draw_networkx(ws_graph, pos, node_size=150, node_color="lightgreen", with_labels=False)
plt.title(f"Watts-Strogatz Small-World (N={N}, k={K}, p_rewire={P_REWIRE})")
plt.show()