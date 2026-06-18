import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
import networkx as nx  
import numpy as np

# --- CONFIGURATION ---
SCENARIO = 1
YEARS = 2
TIME_STEPS = 365 * YEARS  # 730 days (2 years)
POPULATION_SIZE = 300

IMMUNITY_DURATION = 30
INITIAL_INFECTED = 5


# --- BARABÁSI-ALBERT NETWORK PARAMETERS ---
# M determines how many edges a new node receives when it is created.

M_EDGES = 2


# --- AGENT CLASS ---
class Person:

    def __init__(self, status="S", id=0):
        self.id = id  # ID
        self.status = status  # 'S', 'I', 'R'
        self.days_since_recovery = 0
        self.contacts = []


# --- INITIALIZE SIMULATION ---
# Create people with IDs
population = [Person(id=i) for i in range(POPULATION_SIZE)]

# Set initial infected people
for i in range(INITIAL_INFECTED):
    population[i].status = "I"


# --- BARABÁSI-ALBERT NETWORK CREATION ---

ba_graph = nx.barabasi_albert_graph(n=POPULATION_SIZE, m=M_EDGES, seed=42)


for edge in ba_graph.edges():
    p1_id, p2_id = edge
    population[p1_id].contacts.append(population[p2_id])
    population[p2_id].contacts.append(population[p1_id])


# Statistic lists for plotting
stats_S, stats_I, stats_R, stats_total = [], [], [], []
status_history = []
season_change = []

max_infected = 0
peak_day = 0

print("-" * 65)
print(
    f"{'Day':<5} | {'Susceptible (S)':<15} | {'Infected (I)':<15} | {'Recovered (R)':<15}"
)
print("-" * 65)

# --- SIMULATION LOOP ---
for t in range(TIME_STEPS):


    # --- SEASONAL RATES CHECK ---
    # t // 182 determines the phase.
    # Even phases (0, 2) = Cold
    # Odd (1, 3) = Warm

    if (t // 182) % 2 == 0:
        current_infection_rate = 0.05  # Cold season 
        current_recovery_rate = 0.02
    else:
        current_infection_rate = 0.03  # Warm season 
        current_recovery_rate = 0.04   # Faster recovery in summer
    # Saving for lines in graph
    if t % 182 == 0 and t > 0:
        season_change.append(t)

     
    # --- BARABÁSI-ALBERT NETWORK APPLICATION (infections) ---
    # 1. Infections are only passed to direct network neighbors.

    infected = [p for p in population if p.status == "I"]

    for inf in infected:
        for contact in inf.contacts:
            if contact.status == "S":
                if random.random() < current_infection_rate:  # Seasonal rate applied
                    contact.status = "I"
    

    # 2. Status updates (recovery, immunity expiration)
    for p in population:
        if p.status == "I":
            if random.random() < current_recovery_rate:  # Seasonal rate applied
                p.status = "R"
                p.days_since_recovery = 0
        elif p.status == "R":
            p.days_since_recovery += 1
            if p.days_since_recovery >= IMMUNITY_DURATION:
                p.status = "S"

    # 3. Statistics data
    S_count = sum(1 for p in population if p.status == "S")
    I_count = sum(1 for p in population if p.status == "I")
    R_count = sum(1 for p in population if p.status == "R")

    stats_S.append(S_count)
    stats_I.append(I_count)
    stats_R.append(R_count)
    stats_total.append(len(population))
    status_history.append([p.status for p in population])

    if I_count > max_infected:
        max_infected = I_count
        peak_day = t

    if t % 10 == 0 or t == TIME_STEPS - 1:
        print(f"{t:<5} | {S_count:<15} | {I_count:<15} | {R_count:<15}")

print("-" * 65)
print(f"\nANALYSIS:")
print(
    f"The peak occurred on day {peak_day} with {max_infected} simultaneously infected."
)

last_day = TIME_STEPS - 1
last_S = stats_S[-1]
last_I = stats_I[-1]
last_R = stats_R[-1]
print(
    f"At the last time step (day {last_day}), {last_S} people were susceptible, {last_I} infected, and {last_R} temporarily recovered."
)
print("-" * 65)

# --- EVALUATION, ANIMATION, AND PLOT ---
pos = nx.spring_layout(ba_graph, seed=42)
color_map = {"S": "#4285f4", "I": "#de2d26", "R": "#2ca02c"}
node_colors_history = [[color_map[status] for status in statuses] for statuses in status_history]

fig, (ax_net, ax_stats) = plt.subplots(
    2,
    1,
    figsize=(12, 12),
    gridspec_kw={"height_ratios": [2, 1]},
)

ax_stats.set_xlim(0, TIME_STEPS)
ax_stats.set_ylim(0, POPULATION_SIZE)
ax_stats.set_xlabel("Time steps (days)")
ax_stats.set_ylabel("Number of people")
ax_stats.grid(True, linestyle="--", alpha=0.4)
ax_stats.set_title("SIRS statistics over time (incl. Seasonality)")
line_S, = ax_stats.plot([], [], "b", label="Susceptible (S)")
line_I, = ax_stats.plot([], [], "r", label="Infected (I)")
line_R, = ax_stats.plot([], [], "g", label="Recovered (R)")
ax_stats.axvline(x=peak_day, color="gray", linestyle="--", alpha=0.7, label=f"Peak (Day {peak_day})")
ax_stats.legend(loc="upper right")
ax_net.set_title(f"Barabási-Albert network Cold-Warm animation (M={M_EDGES})")
ax_net.axis("off")
ax_net.legend(
    handles=[
        Patch(color=color_map["S"], label="Susceptible (S)"),
        Patch(color=color_map["I"], label="Infected (I)"),
        Patch(color=color_map["R"], label="Recovered (R)"),
    ],
    loc="upper right",  
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
    ax_net.set_title(f"Barabási-Albert network Cold-Warm animation (M={M_EDGES})")
    nx.draw_networkx_edges(ba_graph, pos=pos, ax=ax_net, alpha=0.3)
    line_S.set_data([], [])
    line_I.set_data([], [])
    line_R.set_data([], [])
    frame_text.set_text("")
    return line_S, line_I, line_R, frame_text


def update(frame):
    ax_net.clear()
    ax_net.axis("off")
    ax_net.set_title(f"Barabási-Albert network Cold-Warm animation (M={M_EDGES})")
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
    ax_net.legend(
        handles=[
            Patch(color=color_map["S"], label="Susceptible (S)"),
            Patch(color=color_map["I"], label="Infected (I)"),
            Patch(color=color_map["R"], label="Recovered (R)"),
        ],
        loc="upper right",
        framealpha=0.9,
    )

    x = list(range(frame + 1))
    line_S.set_data(x, stats_S[: frame + 1])
    line_I.set_data(x, stats_I[: frame + 1])
    line_R.set_data(x, stats_R[: frame + 1])
    frame_text.set_text(
        f"Day: {frame}   S: {stats_S[frame]}   I: {stats_I[frame]}   R: {stats_R[frame]}"
    )
    return line_S, line_I, line_R, frame_text

ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(status_history),
    init_func=init,
    interval=30,
    blit=False,
)

fig.tight_layout()
plt.show()

# --- STATIC FINAL PLOT WITH ---
plt.figure(figsize=(12, 7))
plt.plot(stats_S, "b", label="Susceptible (S)")
plt.plot(stats_I, "r", label="Infected (I)")
plt.plot(stats_R, "g", label="Recovered (R)")
plt.plot(stats_total, "k--", label="Total population (N)", alpha=0.5)

# dotted lines for season changes
for change in season_change:
    plt.axvline(x=change, color="gray", linestyle=":", alpha=0.6)

# Line for the peak
plt.axvline(x=peak_day, color="darkred", linestyle="--", alpha=0.8, label=f"Peak (Day {peak_day}: {max_infected} people)")

# Text for the seasons
plt.text(50, POPULATION_SIZE * 0.9, "COLD (Start)", fontsize=10, color="gray", weight="bold")
plt.text(230, POPULATION_SIZE * 0.9, "WARM", fontsize=10, color="orange", weight="bold")
plt.text(410, POPULATION_SIZE * 0.9, "COLD", fontsize=10, color="gray", weight="bold")
plt.text(590, POPULATION_SIZE * 0.9, "WARM", fontsize=10, color="orange", weight="bold")

plt.title(f"SIRS model with seasonal effect in a Barabási-Albert network (M={M_EDGES})")
plt.xlabel("Time steps (days)")
plt.ylabel("Number of people")
plt.grid(True, linestyle="--", alpha=0.3)
plt.legend(loc="upper right")  
plt.tight_layout()
plt.show()
