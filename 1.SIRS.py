# What is the SIR model?
 # It is a model with 3 states that a person can take during the simulation.
 # S = Susceptible: A person is healthy but can be infected by the virus.
 # I = Infected: The person carries a virus and is contagious to susceptible people.
 # R = Recovered: The person has overcome the disease and is (for now) immune.


import random
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
SCENARIO = 1
YEARS = 2
TIME_STEPS = YEARS * 365
POPULATION_SIZE = 300

INFECTION_RATE = 0.05
RECOVERY_RATE = 0.02
IMMUNITY_DURATION = 30

# Set scenario-specific parameters
if SCENARIO == 1:
    INITIAL_INFECTED = 5
    MIN_CONTACTS = 4
    MAX_CONTACTS = 4
elif SCENARIO == 2:
    INITIAL_INFECTED = 5
    MIN_CONTACTS = 1
    MAX_CONTACTS = 4
elif SCENARIO == 3:
    INITIAL_INFECTED = 1
    MIN_CONTACTS = 1
    MAX_CONTACTS = 4


# --- AGENT CLASS ---

class Person:

    def __init__(self, status="S"):
        self.status = status  # 'S' (Susceptible), 'I' (Infected), 'R' (Recovered)
        self.days_since_recovery = 0
        self.max_contacts = random.randint(MIN_CONTACTS, MAX_CONTACTS)


# --- INITIALIZE SIMULATION ---
population = [Person() for _ in range(POPULATION_SIZE)]

# Set initial infected persons
for i in range(INITIAL_INFECTED):
    population[i].status = "I"

# Statistic lists for the plot
stats_S, stats_I, stats_R = [], [], []

# Variables for peak analysis
max_infected = 0
peak_day = 0

print("-" * 65)
print(
    f"{'Day':<5} | {'Susceptible (S)':<15} | {'Infected (I)':<15} | {'Recovered (R)':<15}"
)
print("-" * 65)

# --- SIMULATION LOOP  ---
for t in range(TIME_STEPS):
    # 1. Make contacts and transmit infections
    infected = [p for p in population if p.status == "I"]

    for inf in infected:
        contacts = random.sample(population, min(inf.max_contacts, len(population)))
        for contact in contacts:
            if contact.status == "S":
                if random.random() < INFECTION_RATE:
                    contact.status = "I"

    # 2. Update statuses (recovery, immunity expiration)
    for p in population:
        if p.status == "I":
            if random.random() < RECOVERY_RATE:
                p.status = "R"
                p.days_since_recovery = 0
        elif p.status == "R":
            p.days_since_recovery += 1
            if p.days_since_recovery >= IMMUNITY_DURATION:
                p.status = "S"

    # 3. Collect data
    S_count = sum(1 for p in population if p.status == "S")
    I_count = sum(1 for p in population if p.status == "I")
    R_count = sum(1 for p in population if p.status == "R")

    stats_S.append(S_count)
    stats_I.append(I_count)
    stats_R.append(R_count)

    # Peak tracker: when are the most people infected
    if I_count > max_infected:
        max_infected = I_count
        peak_day = t

    # 4. Print numbers to the console every 10 days
    if t % 10 == 0 or t == TIME_STEPS - 1:
        print(f"{t:<5} | {S_count:<15} | {I_count:<15} | {R_count:<15}")

print("-" * 65)
print(f"\nANALYSIS:")
print(
    f"The peak occurred on day {peak_day} with {max_infected} simultaneously infected."
)
print("-" * 65)

# --- PLOT ---
plt.figure(figsize=(12, 7))
plt.plot(stats_S, "b", label="Susceptible (S)")
plt.plot(stats_I, "r", label="Infected (I)")
plt.plot(stats_R, "g", label="Recovered (R)")

# Vertical dashed line at the peak day in the plot
plt.axvline(
    x=peak_day,
    color="gray",
    linestyle="--",
    label=f"Peak (Day {peak_day})",
    alpha=0.7,
)

plt.title(
    f"Agent-based SIRS model - Scenario {SCENARIO}"
)
plt.xlabel("Time steps (days)")
plt.ylabel("Number of people")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.show()
