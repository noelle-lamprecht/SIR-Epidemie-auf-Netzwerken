import random
import matplotlib.pyplot as plt
import numpy as np

# --- KONFIGURATION ---
SZENARIO = 1  # Wähle hier: 1, 2 oder 3
ZEITSCHRITTE = 200
ANZAHL_PERSONEN = 300

ANSTECKUNGSRATE = 0.05
GENESUNGSRATE = 0.02
IMMUNITAETS_DAUER = 30

# Österreichische Raten (auf Tagesbasis umgerechnet: Jahresrate / 365)
GEBURTENRATE_TAG = (8.2 / 1000) / 365
STERBERATE_TAG = (9.4 / 1000) / 365

# Szenario-spezifische Parameter setzen
if SZENARIO == 1:
    URSPRUNGLICH_INFIZIERT = 5
    VERBINDUNGEN_MIN = 4
    VERBINDUNGEN_MAX = 4
elif SZENARIO == 2:
    URSPRUNGLICH_INFIZIERT = 5
    VERBINDUNGEN_MIN = 1
    VERBINDUNGEN_MAX = 4
elif SZENARIO == 3:
    URSPRUNGLICH_INFIZIERT = 1
    VERBINDUNGEN_MIN = 1
    VERBINDUNGEN_MAX = 4


# --- AGENTEN-KLASSE (Die Personen) ---
class Person:

    def __init__(self, status="S"):
        self.status = status  # 'S' (Anfällig), 'I' (Infiziert), 'R' (Genesen), 'M' (Dauerhaft Immun)
        self.infektions_counter = 0  # Wie oft schon infiziert?
        self.tage_seit_genesung = 0  # Tracker für die 30 Zeitschritte Immunität
        self.max_verbindungen = random.randint(
            VERBINDUNGEN_MIN, VERBINDUNGEN_MAX
        )


# --- SIMULATION INITIALISIEREN ---
population = [Person() for _ in range(ANZAHL_PERSONEN)]

# Erste Infizierte setzen
for i in range(URSPRUNGLICH_INFIZIERT):
    population[i].status = "I"
    population[i].infektions_counter = 1

# Statistik-Listen für die Grafik
stats_S, stats_I, stats_R, stats_M, stats_N = [], [], [], [], []

# Variablen für die Peak-Analyse (Höhepunkt der Welle)
max_infizierte = 0
peak_tag = 0

print("-" * 85)
print(
    f"{'Tag':<5} | {'Anfällig (S)':<13} | {'Infiziert (I)':<13} | {'Temporär (R)':<13} | {'Immun (M)':<10} | {'Gesamt (N)':<10}"
)
print("-" * 85)

# --- SIMULATIONS-SCHLEIFE (Zeitschritte) ---
for t in range(ZEITSCHRITTE):
    # 1. Kontakte knüpfen und Infektionen übertragen
    infizierte = [p for p in population if p.status == "I"]

    for inf in infizierte:
        kontakte = random.sample(
            population, min(inf.max_verbindungen, len(population))
        )
        for kontakt in kontakte:
            if kontakt.status == "S":
                if random.random() < ANSTECKUNGSRATE:
                    kontakt.status = "I"
                    kontakt.infektions_counter += 1

    # 2. Status-Updates (Genesung, Immunitäts-Ablauf)
    for p in population:
        if p.status == "I":
            if random.random() < GENESUNGSRATE:
                p.status = "R"
                p.tage_seit_genesung = 0
        elif p.status == "R":
            p.tage_seit_genesung += 1
            if p.tage_seit_genesung >= IMMUNITAETS_DAUER:
                if p.infektions_counter >= 2:
                    p.status = "M"  # Vollkommen Immun nach 2 Infektionen
                else:
                    p.status = "S"  # Wieder anfällig nach 30 Schritten

    # 3. Demografie: Sterbefälle
    neue_population = []
    for p in population:
        if random.random() > STERBERATE_TAG:
            neue_population.append(p)
    population = neue_population

    # 4. Demografie: Geburten
    anzahl_geburten = sum(
        1 for _ in range(len(population)) if random.random() < GEBURTENRATE_TAG
    )
    for _ in range(anzahl_geburten):
        population.append(Person(status="S"))

    # 5. Daten für Statistik sammeln
    S_count = sum(1 for p in population if p.status == "S")
    I_count = sum(1 for p in population if p.status == "I")
    R_count = sum(1 for p in population if p.status == "R")
    M_count = sum(1 for p in population if p.status == "M")
    N_count = len(population)

    stats_S.append(S_count)
    stats_I.append(I_count)
    stats_R.append(R_count)
    stats_M.append(M_count)
    stats_N.append(N_count)

    # Peak-Tracker: Halte fest, wann die meisten infiziert waren
    if I_count > max_infizierte:
        max_infizierte = I_count
        peak_tag = t

    # 6. Zahlen alle 10 Tage in der Konsole ausgeben
    if t % 10 == 0 or t == ZEITSCHRITTE - 1:
        print(
            f"{t:<5} | {S_count:<13} | {I_count:<13} | {R_count:<13} | {M_count:<10} | {N_count:<10}"
        )

print("-" * 85)
print(f"\nANALYSE:")
print(
    f"Der Höhepunkt (Peak) war an Tag {peak_tag} mit {max_infizierte} gleichzeitig Infizierten."
)
print(
    f"Am Ende der Simulation (Tag {ZEITSCHRITTE-1}) gibt es {M_count} dauerhaft immune Personen."
)
print("-" * 85)

# --- AUSWERTUNG UND PLOT ---
plt.figure(figsize=(12, 7))
plt.plot(stats_S, "b", label="Anfällig (S)")
plt.plot(stats_I, "r", label="Infiziert (I)")
plt.plot(stats_R, "g", label="Temporär Genesen (R)")
plt.plot(stats_M, "m", label="Dauerhaft Immun (M)")
plt.plot(stats_N, "k--", label="Gesamtbevölkerung (N)", alpha=0.5)

# Zeichne eine vertikale gestrichelte Linie am Peak-Tag
plt.axvline(
    x=peak_tag,
    color="gray",
    linestyle="--",
    label=f"Peak (Tag {peak_tag})",
    alpha=0.7,
)

plt.title(
    f"Agentenbasiertes SIR-Modell - Szenario {SZENARIO} (Österreichische Demografie)"
)
plt.xlabel("Zeitschritte (Tage)")
plt.ylabel("Anzahl Personen")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.show()