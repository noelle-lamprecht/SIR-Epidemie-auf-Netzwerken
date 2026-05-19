"""
SIR-Epidemie auf Netzwerken basierend auf dem Barabasi-Albert-Modell.

Dieses Skript erzeugt ein Barabasi-Albert-Netzwerk, simuliert einen SIR-Prozess
auf den Knoten und speichert einen Zeitreihen-Plot sowie eine Netzwerk-Animation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Verwende einen nicht-interaktiven Backend für headless Umgebungen
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def generate_barabasi_albert(n, m, seed=None):
    """Erzeuge ein Barabasi-Albert-Netzwerk als Adjazenzliste."""
    # Prüfe die Eingabeparameter
    if m < 1 or m >= n:
        raise ValueError('m muss mindestens 1 und kleiner als n sein.')

    rng = np.random.default_rng(seed)
    adjacency = {i: set() for i in range(n)}

    # Beginne mit einem vollständigen Graphen aus m+1 Knoten
    # Diese initiale Struktur ist notwendig, damit neue Knoten später angehängt werden.
    for u in range(m + 1):
        for v in range(u + 1, m + 1):
            adjacency[u].add(v)
            adjacency[v].add(u)

    # Füge nach und nach neue Knoten hinzu
    for new_node in range(m + 1, n):
        # Berechne die aktuellen Knotengrade für die Preferential Attachment Wahrscheinlichkeit
        degrees = np.array([len(adjacency[u]) for u in range(new_node)], dtype=float)
        degree_sum = degrees.sum()

        # Wähle m existierende Knoten proportional zu ihrem Grad aus
        if degree_sum == 0:
            targets = rng.choice(new_node, size=m, replace=False)
        else:
            probabilities = degrees / degree_sum
            targets = rng.choice(new_node, size=m, replace=False, p=probabilities)

        # Füge die Kanten symmetrisch ein
        for target in targets:
            adjacency[new_node].add(target)
            adjacency[target].add(new_node)

    return adjacency


def simulate_sir_on_graph(adjacency, beta, gamma, initial_infected, max_steps, seed=None):
    """Simuliere den SIR-Prozess auf einem Netzwerk."""
    n = len(adjacency)
    rng = np.random.default_rng(seed)

    # Zustände: 0 = Susceptible, 1 = Infiziert, 2 = Genesen
    states = np.zeros(n, dtype=int)

    # Setze die initial infizierten Knoten
    if isinstance(initial_infected, int):
        initial_nodes = rng.choice(n, size=initial_infected, replace=False)
    else:
        initial_nodes = np.array(initial_infected, dtype=int)

    states[initial_nodes] = 1
    history = [states.copy()]

    # Simuliere Zeitschritt für Zeitschritt
    for step in range(1, max_steps):
        new_states = states.copy()
        infected_nodes = np.where(states == 1)[0]

        # Abbruch, wenn keine Infizierten mehr vorhanden sind
        if infected_nodes.size == 0:
            break

        # Infizierte können ihre Nachbarn anstecken
        for node in infected_nodes:
            for neighbor in adjacency[node]:
                if states[neighbor] == 0 and rng.random() < beta:
                    new_states[neighbor] = 1

        # Infizierte erholen sich mit Wahrscheinlichkeit gamma
        for node in infected_nodes:
            if rng.random() < gamma:
                new_states[node] = 2

        states = new_states
        history.append(states.copy())

    # Konvertiere History zu Arrays für die Auswertung
    history = np.stack(history, axis=0)
    s_history = np.sum(history == 0, axis=1)
    i_history = np.sum(history == 1, axis=1)
    r_history = np.sum(history == 2, axis=1)
    t = np.arange(len(history))

    return t, history, s_history, i_history, r_history


def plot_time_series(t, s, i, r, filename, title):
    """Speichere ein Zeitreihen-Diagramm der SIR-Verläufe."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Linien für S, I, R zeichnen
    ax.plot(t, s, color='blue', linewidth=2.5, label='Susceptible')
    ax.plot(t, i, color='red', linewidth=2.5, label='Infiziert')
    ax.plot(t, r, color='green', linewidth=2.5, label='Genesen')

    ax.set_title(title)
    ax.set_xlabel('Zeitschritt')
    ax.set_ylabel('Anzahl Knoten')
    ax.legend()
    ax.grid(alpha=0.25)

    # Speichere den Plot als PNG-Datei
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)


def animate_network(adjacency, positions, history, filename='sir_network_animation.gif', interval=200):
    """Erstelle eine Animation des Netzwerks mit Zustandänderungen."""
    n = len(positions)
    fig, ax = plt.subplots(figsize=(8, 8))

    # Entferne Achsenbeschriftung für die Netzwerkdarstellung
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('SIR auf Barabasi-Albert-Netzwerk')

    # Zeichne alle Kanten im Netzwerk
    for u, neighbors in adjacency.items():
        for v in neighbors:
            if u < v:
                x = [positions[u, 0], positions[v, 0]]
                y = [positions[u, 1], positions[v, 1]]
                ax.plot(x, y, color='gray', linewidth=0.8, alpha=0.4, zorder=1)

    scatter = ax.scatter(positions[:, 0], positions[:, 1], s=80, edgecolor='black', linewidth=0.4, zorder=2)

    # Farbzuordnung für die drei Zustände
    color_map = np.array(['blue', 'red', 'green'])

    def update(frame):
        # Aktualisiere die Farbe der Knoten für jeden Zeitschritt
        colors = color_map[history[frame]]
        scatter.set_color(colors)
        ax.set_title(f'SIR auf Barabasi-Albert-Netzwerk — Schritt {frame}')
        return scatter,

    animation = FuncAnimation(fig, update, frames=history.shape[0], interval=interval, blit=True)

    try:
        writer = PillowWriter(fps=int(1000 / interval))
        animation.save(filename, writer=writer)
        print(f'Animation gespeichert als {filename}')
    except Exception:
        print('Konnte .gif nicht speichern. Bitte prüfen Sie, ob Pillow installiert ist.')
    plt.close(fig)


def create_random_positions(n, seed=None):
    """Generiere zufällige 2D-Positionen für die Plot-Darstellung des Netzwerks."""
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, size=(n, 2))


def main():
    # Netzwerkinitialisierung
    n = 200  # Anzahl Knoten
    m = 3    # Anzahl neuer Kanten pro hinzugefügtem Knoten

    # SIR-Parameter
    beta = 0.04   # Infektionswahrscheinlichkeit pro Kontakt
    gamma = 0.01  # Erholungswahrscheinlichkeit pro Schritt
    initial_infected = 5
    max_steps = 120
    seed = 42

    print('Erzeuge Barabasi-Albert-Netzwerk...')
    adjacency = generate_barabasi_albert(n, m, seed=seed)
    positions = create_random_positions(n, seed=seed)

    print('Simuliere SIR-Epidemie...')
    t, history, s_history, i_history, r_history = simulate_sir_on_graph(
        adjacency,
        beta,
        gamma,
        initial_infected,
        max_steps,
        seed=seed,
    )

    # Ergebnisplots speichern
    plot_time_series(
        t,
        s_history,
        i_history,
        r_history,
        filename='sir_network_time_series.png',
        title='SIR-Epidemie auf einem Barabasi-Albert-Netzwerk',
    )

    animate_network(
        adjacency,
        positions,
        history,
        filename='sir_network_animation.gif',
        interval=200,
    )

    print('Fertig. Erstellte Dateien: sir_network_time_series.png und sir_network_animation.gif')


if __name__ == '__main__':
    main()
