import matplotlib.pyplot as plt
import networkx as nx

# Parameter: 50 Personen, Wahrscheinlichkeit für eine Verbindung = 10%
N = 50
P = 0.10

# Netzwerk generieren
er_graph = nx.erdos_renyi_graph(n=N, p=P, seed=42)

# Zeichnen
plt.figure(figsize=(6, 6))
nx.draw_networkx(er_graph, node_size=150, node_color="lightblue", with_labels=False)
plt.title(f"Erdős-Rényi Zufallsnetzwerk (N={N}, p={P})")
plt.show()