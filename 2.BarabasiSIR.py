#Alt: Früher hatte jeder Agent einfach eine Zahl (max_verbindungen), die bestimmte,
    #wie viele Zufallskontakte er pro Tag aus einem Lostopf zieht.
#Neu: Jeder Agent hat nun eine eindeutige id (0 bis 299) und eine leere Liste self.kontakte.
#In dieser Liste speichern wir fest ab, wer die „Freunde“ oder Kontakte dieser Person im Netzwerk sind.
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
import networkx as nx  # WICHTIG: networkx wird für das Barabási-Modell benötigt!
import numpy as np

# --- KONFIGURATION ---
SZENARIO = 1
JAHRE = 2
ZEITSCHRITTE = 365 * JAHRE  # 730 Tage (2 Jahre)
ANZAHL_PERSONEN = 300

ANSTECKUNGSRATE = 0.05
GENESUNGSRATE = 0.02
IMMUNITAETS_DAUER = 30 

URSPRUNGLICH_INFIZIERT = 5

# =========================================================================
# === BARABÁSI-ALBERT NETZWERK PARAMETER ===
# M bestimmt, wie viele Kanten ein neuer Knoten beim Erstellen erhält.
# Höheres M = dichteres Netzwerk (mehr Kontakte für alle).
# =========================================================================
M_KANTEN = 2 


# --- AGENTEN-KLASSE (Die Personen) ---
class Person:

    def __init__(self, status="S", id=0):
        self.id = id  # Eindeutige ID zur Zuordnung im Netzwerk
        self.status = status  # 'S', 'I', 'R'
        self.tage_seit_genesung = 0
        # Die Kontakte werden jetzt fest durch das Netzwerk vorgegeben!
        self.kontakte = []


# --- SIMULATION INITIALISIEREN ---
# Personen mit IDs erstellen
population = [Person(id=i) for i in range(ANZAHL_PERSONEN)]

# Erste Infizierte setzen
for i in range(URSPRUNGLICH_INFIZIERT):
    population[i].status = "I"

# =========================================================================
# === BARABÁSI-ALBERT NETZWERK ERSTELLUNG ===
# Hier generieren wir den Scale-Free-Graphen. Das Prinzip lautet: "Rich get richer".
# Knoten, die schon viele Verbindungen haben, bekommen wahrscheinlicher neue dazu.
# =========================================================================
ba_graph = nx.barabasi_albert_graph(n=ANZAHL_PERSONEN, m=M_KANTEN, seed=42)

# Die Verbindungen aus dem Netzwerk-Graphen in unsere Personen-Objekte übertragen
for edge in ba_graph.edges():
    p1_id, p2_id = edge
    # Person 1 kennt Person 2 und umgekehrt (ungerichtetes Netzwerk)
    population[p1_id].kontakte.append(population[p2_id])
    population[p2_id].kontakte.append(population[p1_id])
# =========================================================================

# Statistik-Listen für die Grafik
stats_S, stats_I, stats_R, stats_N = [], [], [], []
status_history = []

max_infizierte = 0
peak_tag = 0

print("-" * 65)
print(
    f"{'Tag':<5} | {'Anfällig (S)':<15} | {'Infiziert (I)':<15} | {'Genesen (R)':<15}"
)
print("-" * 65)

# --- SIMULATIONS-SCHLEIFE (Zeitschritte) ---
for t in range(ZEITSCHRITTE):

    # =========================================================================
    # === BARABÁSI-ALBERT NETZWERK ANWENDUNG (Infektionsphase) ===
    # Der Infizierte trifft nun NICHT mehr zufällige Leute aus der Gesamtbevölkerung,
    # sondern NUR noch seine festen Nachbarn aus dem Barabási-Netzwerk.
    # =========================================================================
    infizierte = [p for p in population if p.status == "I"]

    for inf in infizierte:
        # Seine Kontakte sind fest in inf.kontakte hinterlegt (die Netzwerk-Nachbarn)
        for kontakt in inf.kontakte:
            if kontakt.status == "S":
                if random.random() < ANSTECKUNGSRATE:
                    kontakt.status = "I"
    # =========================================================================

    # 2. Status-Updates (Genesung, Immunitäts-Ablauf)
    for p in population:
        if p.status == "I":
            if random.random() < GENESUNGSRATE:
                p.status = "R"
                p.tage_seit_genesung = 0
        elif p.status == "R":
            p.tage_seit_genesung += 1
            if p.tage_seit_genesung >= IMMUNITAETS_DAUER:
                p.status = "S"

    # 3. Daten für Statistik sammeln
    S_count = sum(1 for p in population if p.status == "S")
    I_count = sum(1 for p in population if p.status == "I")
    R_count = sum(1 for p in population if p.status == "R")

    stats_S.append(S_count)
    stats_I.append(I_count)
    stats_R.append(R_count)
    stats_N.append(ANZAHL_PERSONEN)
    status_history.append([p.status for p in population])

    if I_count > max_infizierte:
        max_infizierte = I_count
        peak_tag = t

    if t % 10 == 0 or t == ZEITSCHRITTE - 1:
        print(f"{t:<5} | {S_count:<15} | {I_count:<15} | {R_count:<15}")

print("-" * 65)
print(f"\nANALYSE:")
print(
    f"Der Höhepunkt (Peak) war an Tag {peak_tag} mit {max_infizierte} gleichzeitig Infizierten."
)

last_day = ZEITSCHRITTE - 1
last_S = stats_S[-1]
last_I = stats_I[-1]
last_R = stats_R[-1]
print(
    f"Am letzten Zeitschritt (Tag {last_day}) waren {last_S} Personen anfällig, {last_I} infiziert und {last_R} temporär genesen."
)
print("-" * 65)

# --- AUSWERTUNG ANIMATION UND PLOT ---
pos = nx.spring_layout(ba_graph, seed=42)
color_map = {"S": "#4285f4", "I": "#de2d26", "R": "#2ca02c"}
node_colors_history = [[color_map[status] for status in statuses] for statuses in status_history]

fig, (ax_net, ax_stats) = plt.subplots(
    2,
    1,
    figsize=(12, 12),
    gridspec_kw={"height_ratios": [2, 1]},
)

ax_stats.set_xlim(0, ZEITSCHRITTE)
ax_stats.set_ylim(0, ANZAHL_PERSONEN)
ax_stats.set_xlabel("Zeitschritte (Tage)")
ax_stats.set_ylabel("Anzahl Personen")
ax_stats.grid(True, linestyle="--", alpha=0.4)
ax_stats.set_title("SIRS-Statistik über die Zeit")
line_S, = ax_stats.plot([], [], "b", label="Anfällig (S)")
line_I, = ax_stats.plot([], [], "r", label="Infiziert (I)")
line_R, = ax_stats.plot([], [], "g", label="Genesen (R)")
ax_stats.axvline(x=peak_tag, color="gray", linestyle="--", alpha=0.7, label=f"Peak (Tag {peak_tag})")
ax_stats.legend(loc="upper right")

ax_net.set_title(f"Barabási-Albert-Netzwerk SIRS-Animation (M={M_KANTEN})")
ax_net.axis("off")
ax_net.legend(
    handles=[
        Patch(color=color_map["S"], label="Anfällig (S)"),
        Patch(color=color_map["I"], label="Infiziert (I)"),
        Patch(color=color_map["R"], label="Genesen (R)"),
    ],
    loc="lower left",
    framealpha=0.9,
)

frame_text = ax_net.text(
    0.02,
    0.95,
    "",
    transform=ax_net.transAxes,
    fontsize=12,
    verticalalignment="top",
    bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "gray"},
)


def init():
    ax_net.clear()
    ax_net.axis("off")
    ax_net.set_title(f"Barabási-Albert-Netzwerk SIRS-Animation (M={M_KANTEN})")
    nx.draw_networkx_edges(ba_graph, pos=pos, ax=ax_net, alpha=0.3)
    line_S.set_data([], [])
    line_I.set_data([], [])
    line_R.set_data([], [])
    frame_text.set_text("")
    return line_S, line_I, line_R, frame_text


def update(frame):
    ax_net.clear()
    ax_net.axis("off")
    ax_net.set_title(f"Barabási-Albert-Netzwerk SIRS-Animation (M={M_KANTEN})")
    nx.draw_networkx_edges(ba_graph, pos=pos, ax=ax_net, alpha=0.3)
    nx.draw_networkx_nodes(
        ba_graph,
        pos=pos,
        node_color=node_colors_history[frame],
        ax=ax_net,
        node_size=120,
        edgecolors="black",
        linewidths=0.3,
    )

    x = list(range(frame + 1))
    line_S.set_data(x, stats_S[: frame + 1])
    line_I.set_data(x, stats_I[: frame + 1])
    line_R.set_data(x, stats_R[: frame + 1])
    frame_text.set_text(
        f"Tag: {frame}   S: {stats_S[frame]}   I: {stats_I[frame]}   R: {stats_R[frame]}"
    )
    return line_S, line_I, line_R, frame_text

ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(status_history),
    init_func=init,
    interval=50,
    blit=False,
)

fig.tight_layout()

plt.figure(figsize=(12, 7))
plt.plot(stats_S, "b", label="Anfällig (S)")
plt.plot(stats_I, "r", label="Infiziert (I)")
plt.plot(stats_R, "g", label="Genesen (R)")
plt.plot(stats_N, "k--", label="Gesamtbevölkerung (N)", alpha=0.5)

plt.axvline(
    x=peak_tag,
    color="gray",
    linestyle="--",
    label=f"Peak (Tag {peak_tag})",
    alpha=0.7,
)

plt.title(f"SIRS-Modell im Barabási-Albert-Netzwerk (M={M_KANTEN})")
plt.xlabel("Zeitschritte (Tage)")
plt.ylabel("Anzahl Personen")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()



