"""SIR-Epidemie auf einem Barabási-Albert-Netzwerk.

Dieses Skript erzeugt ein skalierungsfreies Netzwerk und simuliert
eine SIR-Ausbreitung mit veränderbaren Parametern.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class BarabasiAlbertParams:
    node_count: int = 500
    edges_per_new_node: int = 3
    seed: int = 42


@dataclass
class SIRParams:
    beta: float = 0.08
    gamma: float = 0.03
    initial_infected_count: int = 3
    max_steps: int = 200
    seed: int = 42


def generate_barabasi_albert_network(params: BarabasiAlbertParams) -> Dict[int, Set[int]]:
    """Generiert ein Barabási-Albert-Netzwerk als Adjazenzliste."""
    random.seed(params.seed)
    n = params.node_count
    m = params.edges_per_new_node
    if m < 1 or m >= n:
        raise ValueError("edges_per_new_node muss zwischen 1 und node_count-1 liegen")

    graph: Dict[int, Set[int]] = {i: set() for i in range(n)}
    target_nodes: List[int] = list(range(m))
    source_nodes: List[int] = []

    for source in range(m):
        for target in range(source + 1, m):
            graph[source].add(target)
            graph[target].add(source)
            source_nodes.append(source)
            source_nodes.append(target)

    for new_node in range(m, n):
        selected: Set[int] = set()
        while len(selected) < m:
            chosen = random.choice(source_nodes)
            selected.add(chosen)

        for target in selected:
            graph[new_node].add(target)
            graph[target].add(new_node)
            source_nodes.append(new_node)
            source_nodes.append(target)

    return graph


def simulate_sir(
    graph: Dict[int, Set[int]],
    params: SIRParams,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simuliert den SIR-Prozess auf dem gegebenen Netzwerk."""
    random.seed(params.seed)
    n = len(graph)
    susceptible: Set[int] = set(graph.keys())
    infected: Set[int] = set()
    recovered: Set[int] = set()

    initial_infected = random.sample(list(susceptible), params.initial_infected_count)
    infected.update(initial_infected)
    susceptible.difference_update(initial_infected)

    s_history = [len(susceptible)]
    i_history = [len(infected)]
    r_history = [len(recovered)]

    for step in range(params.max_steps):
        if not infected:
            break

        new_infected: Set[int] = set()
        new_recovered: Set[int] = set()

        for node in infected:
            for neighbor in graph[node]:
                if neighbor in susceptible:
                    if random.random() < params.beta:
                        new_infected.add(neighbor)

        for node in infected:
            if random.random() < params.gamma:
                new_recovered.add(node)

        susceptible.difference_update(new_infected)
        infected.update(new_infected)
        infected.difference_update(new_recovered)
        recovered.update(new_recovered)

        s_history.append(len(susceptible))
        i_history.append(len(infected))
        r_history.append(len(recovered))

    return np.array(s_history), np.array(i_history), np.array(r_history)


def plot_sir_curves(
    s: np.ndarray,
    i: np.ndarray,
    r: np.ndarray,
    params: SIRParams,
    ba_params: BarabasiAlbertParams,
    save_file: str | None = None,
) -> None:
    """Zeigt die SIR-Verläufe an."""
    fig, ax = plt.subplots(figsize=(10, 6))
    t = np.arange(len(s))
    ax.plot(t, s, label="Susceptible", color="tab:blue")
    ax.plot(t, i, label="Infected", color="tab:red")
    ax.plot(t, r, label="Recovered", color="tab:green")
    ax.set_xlabel("Zeit in Schritten")
    ax.set_ylabel("Anzahl der Knoten")
    ax.set_title(
        f"SIR auf Barabási-Albert-Netzwerk (N={ba_params.node_count}, m={ba_params.edges_per_new_node})"
    )
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    if save_file:
        fig.savefig(save_file)
        print(f"SIR-Diagramm gespeichert als: {save_file}")
    plt.show()
    plt.close(fig)


def plot_degree_distribution(graph: Dict[int, Set[int]], ba_params: BarabasiAlbertParams, save_file: str | None = None) -> None:
    """Zeigt die Knotengradverteilung des BA-Netzwerks."""
    fig, ax = plt.subplots(figsize=(8, 5))
    degrees = [len(neighbors) for neighbors in graph.values()]
    ax.hist(degrees, bins=range(min(degrees), max(degrees) + 2), color="tab:purple", edgecolor="black")
    ax.set_xlabel("Knotengrad")
    ax.set_ylabel("Anzahl der Knoten")
    ax.set_title(f"Gradverteilung im Barabási-Albert-Netzwerk (N={ba_params.node_count}, m={ba_params.edges_per_new_node})")
    fig.tight_layout()
    if save_file:
        fig.savefig(save_file)
        print(f"Gradverteilung gespeichert als: {save_file}")
    plt.show()
    plt.close(fig)


def animate_sir_curves(
    s: np.ndarray,
    i: np.ndarray,
    r: np.ndarray,
    params: SIRParams,
    ba_params: BarabasiAlbertParams,
    save_file: str | None = None,
) -> None:
    """Erzeugt eine Animation der SIR-Kurven über die Zeit."""
    fig, ax = plt.subplots(figsize=(10, 6))
    t = np.arange(len(s))

    line_s, = ax.plot([], [], label="Susceptible", color="tab:blue")
    line_i, = ax.plot([], [], label="Infected", color="tab:red")
    line_r, = ax.plot([], [], label="Recovered", color="tab:green")
    marker_i, = ax.plot([], [], marker="o", color="tab:red", lw=0)

    ax.set_xlim(0, len(s) - 1)
    ax.set_ylim(0, max(max(s), max(i), max(r)) * 1.05)
    ax.set_xlabel("Zeit in Schritten")
    ax.set_ylabel("Anzahl der Knoten")
    ax.set_title(
        f"Animierte SIR-Kurven auf Barabási-Albert-Netzwerk (N={ba_params.node_count}, m={ba_params.edges_per_new_node})"
    )
    ax.legend()
    ax.grid(alpha=0.3)

    def update(frame: int):
        line_s.set_data(t[: frame + 1], s[: frame + 1])
        line_i.set_data(t[: frame + 1], i[: frame + 1])
        line_r.set_data(t[: frame + 1], r[: frame + 1])
        marker_i.set_data([frame], [i[frame]])
        return line_s, line_i, line_r, marker_i

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(s),
        interval=100,
        blit=True,
        repeat=False,
    )

    if save_file:
        try:
            anim.save(save_file, writer="pillow", fps=10)
            print(f"Animation gespeichert als: {save_file}")
        except Exception as err:
            print(f"Konnte Animation nicht speichern: {err}")
    plt.tight_layout()
    plt.show()
    plt.close(fig)


def main() -> None:
    ba_params = BarabasiAlbertParams(
        node_count=1000,
        edges_per_new_node=4,
        seed=2026,
    )

    sir_params = SIRParams(
        beta=0.05,
        gamma=0.02,
        initial_infected_count=5,
        max_steps=300,
        seed=2026,
    )

    graph = generate_barabasi_albert_network(ba_params)
    s, i, r = simulate_sir(graph, sir_params)

    print("Parameter:")
    print(f"  Knoten: {ba_params.node_count}")
    print(f"  Neue Kanten pro Knoten: {ba_params.edges_per_new_node}")
    print(f"  Infektionswahrscheinlichkeit beta: {sir_params.beta}")
    print(f"  Genesungswahrscheinlichkeit gamma: {sir_params.gamma}")
    print(f"  Anfangsinfizierte: {sir_params.initial_infected_count}")
    print(f"  Simulationsschritte: {len(s)}")
    print(f"  Max. Infected: {i.max() if len(i) else 0}")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    plot_degree_distribution(graph, ba_params, save_file=os.path.join(output_dir, "degree_distribution.png"))
    plot_sir_curves(s, i, r, sir_params, ba_params, save_file=os.path.join(output_dir, "sir_curves.png"))
    animate_sir_curves(
        s,
        i,
        r,
        sir_params,
        ba_params,
        save_file=os.path.join(output_dir, "sir_animation.gif"),
    )


if __name__ == "__main__":
    main()





