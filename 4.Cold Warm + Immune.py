#This code simulates the Winter and Summer seasonal influence 
# in a Barabási–Albert SIR epidemic model with demographics and long-term immunity.

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
import networkx as nx  # IMPORTANT 
import numpy as np

# --- CONFIGURATION ---
SCENARIO = 1
YEARS = 2
TIME_STEPS = 365 * YEARS  # 730 days (2 years)
POPULATION_SIZE = 300

IMMUNITY_DURATION = 30

# Austrian rates (converted to daily values)
BIRTH_RATE_DAY = (8.2 / 1000) / 365
DEATH_RATE_DAY = (9.4 / 1000) / 365

INITIAL_INFECTED = 5


# --- BARABÁSI-ALBERT NETWORK PARAMETERS ---

M_EDGES = 2


# --- AGENT CLASS (People) ---
class Person:
    def __init__(self, status="S", id=0, position=(0.0, 0.0)):
        self.id = id  # ID 
        self.status = status  # 'S', 'I', 'R', 'M'
        self.infection_counter = 0
        self.days_since_recovery = 0
        self.position = position
        # Contacts 
        self.contacts = []


# --- INITIALIZE SIMULATION ---
random_state = np.random.RandomState(42)
positions = {i: tuple(random_state.rand(2)) for i in range(POPULATION_SIZE)}
population = [Person(id=i, position=positions[i]) for i in range(POPULATION_SIZE)]

# Track next available ID for newborns
next_id = POPULATION_SIZE

# Set initial infected people
for i in range(INITIAL_INFECTED):
    population[i].status = "I"
    population[i].infection_counter = 1


# --- BARABÁSI-ALBERT NETWORK INITIALIZATION ---

ba_graph = nx.barabasi_albert_graph(n=POPULATION_SIZE, m=M_EDGES, seed=42)

for edge in ba_graph.edges():
    p1_id, p2_id = edge
    population[p1_id].contacts.append(population[p2_id])
    population[p2_id].contacts.append(population[p1_id])

# Statistic lists for plotting
stats_S, stats_I, stats_R, stats_M, stats_total = [], [], [], [], []
status_history = []
graph_history = []
seasons_change = []

max_infected = 0
peak_day = 0
max_population = POPULATION_SIZE
min_population = POPULATION_SIZE

print("-" * 85)
print(
    f"{'Day':<5} | {'Susceptible (S)':<13} | {'Infected (I)':<13} | {'Temporary (R)':<13} | {'Immune (M)':<10} | {'Total (N)':<10}"
)
print("-" * 85)

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
        
    # Saving season change days for visual lines in graph
    if t % 182 == 0 and t > 0:
        seasons_change.append(t)

    
    # --- BARABÁSI-ALBERT NETWORK APPLICATION (infections) ---
    # 1. Infections are only passed to direct network neighbors.
    
    infected = [p for p in population if p.status == "I"]

    for inf in infected:
        for contact in inf.contacts:
            if contact.status == "S":
                if random.random() < current_infection_rate:  # Seasonal rate applied
                    contact.status = "I"
                    contact.infection_counter += 1
    

    # 2. Status updates (recovery, immunity expiration)
    for p in population:
        if p.status == "I":
            if random.random() < current_recovery_rate:  # Seasonal rate applied
                p.status = "R"
                p.days_since_recovery = 0
        elif p.status == "R":
            p.days_since_recovery += 1
            if p.days_since_recovery >= IMMUNITY_DURATION:
                if p.infection_counter >= 2:
                    p.status = "M"  # Permanently immune after 2 infections!!!
                else:
                    p.status = "S"  # if not: Susceptible again

    # 3. Demography: deaths
    survivors = []
    for p in population:
        if random.random() > DEATH_RATE_DAY:
            survivors.append(p)
        else:
            if ba_graph.has_node(p.id):
                ba_graph.remove_node(p.id)
            for neighbor in p.contacts:
                if p in neighbor.contacts:
                    neighbor.contacts.remove(p)

    population = survivors

    # 4. Demography: births
    birth_count = sum(
        1 for _ in range(len(population)) if random.random() < BIRTH_RATE_DAY
    )

    for _ in range(birth_count):
        positions[next_id] = tuple(random_state.rand(2))
        new_baby = Person(status="S", id=next_id, position=positions[next_id])

        if len(population) >= M_EDGES:
            node_list = list(ba_graph.nodes())
            degrees = [ba_graph.degree(n) for n in node_list]
            total_degree = sum(degrees)

            if total_degree > 0:
                probabilities = [g / total_degree for g in degrees]
                chosen_partner_ids = np.random.choice(
                    node_list,
                    size=M_EDGES,
                    replace=False,
                    p=probabilities,
                )

                ba_graph.add_node(new_baby.id)
                for p_id in chosen_partner_ids:
                    ba_graph.add_edge(new_baby.id, p_id)
                    for current_person in population:
                        if current_person.id == p_id:
                            current_person.contacts.append(new_baby)
                            new_baby.contacts.append(current_person)
                            break

        population.append(new_baby)
        next_id += 1

    # 5. Statistics data
    S_count = sum(1 for p in population if p.status == "S")
    I_count = sum(1 for p in population if p.status == "I")
    R_count = sum(1 for p in population if p.status == "R")
    M_count = sum(1 for p in population if p.status == "M")
    total_count = len(population)

    stats_S.append(S_count)
    stats_I.append(I_count)
    stats_R.append(R_count)
    stats_M.append(M_count)
    stats_total.append(total_count)
    status_history.append({p.id: p.status for p in population})
    graph_history.append(ba_graph.copy())

    if total_count > max_population:
        max_population = total_count
    if total_count < min_population:
        min_population = total_count

    if I_count > max_infected:
        max_infected = I_count
        peak_day = t

    # 6. Print statistics every 10 days
    if t % 10 == 0 or t == TIME_STEPS - 1:
        print(
            f"{t:<5} | {S_count:<13} | {I_count:<13} | {R_count:<13} | {M_count:<10} | {total_count:<10}"
        )

zero_infected_day = next((day for day, count in enumerate(stats_I) if count == 0), None)

print("-" * 85)
print(f"\nANALYSE:")
print(f"The peak occurred on day {peak_day} with {max_infected} simultaneously infected.")
print("-" * 85)

# --- ANALYSIS, ANIMATION AND PLOT ---

pos = positions
color_map = {"S": "#4285f4", "I": "#de2d26", "R": "#2ca02c", "M": "#9467bd"}

fig, (ax_net, ax_stats) = plt.subplots(
    2,
    1,
    figsize=(12, 12),
    gridspec_kw={"height_ratios": [2, 1]},
)

ax_stats.set_xlim(0, TIME_STEPS)
ax_stats.set_ylim(0, max(stats_total) + 10)
ax_stats.set_xlabel("Time steps (days)")
ax_stats.set_ylabel("Number of people")
ax_stats.grid(True, linestyle="--", alpha=0.4)
ax_stats.set_title("SIRS-DB: statistics over time (including seasonality)")
line_S, = ax_stats.plot([], [], "b", label="Susceptible (S)")
line_I, = ax_stats.plot([], [], "r", label="Infected (I)")
line_R, = ax_stats.plot([], [], "g", label="Temporary Recovered (R)")
line_M, = ax_stats.plot([], [], "m", label="Permanently Immune (M)")
line_N, = ax_stats.plot([], [], "k--", label="Total population (N)", alpha=0.5)
ax_stats.axvline(x=peak_day, color="gray", linestyle="--", alpha=0.7, label=f"Peak (Day {peak_day})")
ax_stats.legend(loc="upper right")  # upper right

ax_net.set_title(f"Barabási-Albert network Cold-Warm animation (M={M_EDGES})")
ax_net.axis("off")
ax_net.legend(
    handles=[
        Patch(color=color_map["S"], label="Susceptible (S)"),
        Patch(color=color_map["I"], label="Infected (I)"),
        Patch(color=color_map["R"], label="Recovered (R)"),
        Patch(color=color_map["M"], label="Permanently Immune (M)"),
    ],
    loc="upper right",  # upper right so that it doesn't overlap with the network
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
    nx.draw_networkx_edges(graph_history[0], pos=pos, ax=ax_net, alpha=0.3)
    line_S.set_data([], [])
    line_I.set_data([], [])
    line_R.set_data([], [])
    line_M.set_data([], [])
    line_N.set_data([], [])
    frame_text.set_text("")
    return line_S, line_I, line_R, line_M, line_N, frame_text


def update(frame):
    ax_net.clear()
    ax_net.axis("off")
    ax_net.set_title(f"Barabási-Albert network Cold-Warm animation (M={M_EDGES})")
    nx.draw_networkx_edges(graph_history[frame], pos=pos, ax=ax_net, alpha=0.3)
    node_colors = [
        color_map[status_history[frame][node]]
        for node in graph_history[frame].nodes()
    ]
    nx.draw_networkx_nodes(
        graph_history[frame],
        pos=pos,
        node_color=node_colors,
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
            Patch(color=color_map["M"], label="Permanently Immune (M)"),
        ],
        loc="upper right",
        framealpha=0.9,
    )

    x = list(range(frame + 1))
    line_S.set_data(x, stats_S[: frame + 1])
    line_I.set_data(x, stats_I[: frame + 1])
    line_R.set_data(x, stats_R[: frame + 1])
    line_M.set_data(x, stats_M[: frame + 1])
    line_N.set_data(x, stats_total[: frame + 1])
    frame_text.set_text(
        f"Day: {frame}   S: {stats_S[frame]}   I: {stats_I[frame]}   R: {stats_R[frame]}   M: {stats_M[frame]}"
    )
    return line_S, line_I, line_R, line_M, line_N, frame_text

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

# --- STATIC FINAL PLOT WITH SEASON MARKERS ---
plt.figure(figsize=(12, 7))
plt.plot(stats_S, "b", label="Susceptible (S)")
plt.plot(stats_I, "r", label="Infected (I)")
plt.plot(stats_R, "g", label="Temporary Recovered (R)")
plt.plot(stats_M, "m", label="Permanently Immune (M)")
plt.plot(stats_total, "k--", label="Total population (N)", alpha=0.5)

# Gray dotted lines for season changes
for change in seasons_change:
    plt.axvline(x=change, color="gray", linestyle=":", alpha=0.6)

# Dark red dashed line for the peak
plt.axvline(x=peak_day, color="darkred", linestyle="--", alpha=0.8, label=f"Peak (Day {peak_day}: {max_infected} people)")

if 'zero_infected_day' in globals() and zero_infected_day is not None:
    plt.axvline(x=zero_infected_day, color="darkgray", linestyle="--", alpha=0.7, label=f"0 infected (day {zero_infected_day})")

# Text labels for seasons in the diagram
plt.text(50, max(stats_total) * 0.9, "COLD (Start)", fontsize=10, color="gray", weight="bold")
plt.text(230, max(stats_total) * 0.9, "WARM", fontsize=10, color="orange", weight="bold")
plt.text(410, max(stats_total) * 0.9, "COLD", fontsize=10, color="gray", weight="bold")
plt.text(590, max(stats_total) * 0.9, "WARM", fontsize=10, color="orange", weight="bold")

plt.title(f"Seasonal influence with Barabási network, long-term immunity & demographics (M={M_EDGES})")
plt.xlabel("Time steps (days)")
plt.ylabel("Number of people")
plt.grid(True, linestyle="--", alpha=0.3)
plt.legend(loc="upper right")
plt.tight_layout()
plt.show()
