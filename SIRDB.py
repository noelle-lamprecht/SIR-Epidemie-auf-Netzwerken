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
GEBURTENRATE_TAG = (8.3 / 1000) / 365
STERBERATE_TAG = (9.5 / 1000) / 365

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

# --- SIMULATIONS-SCHLEIFE (Zeitschritte) ---
for t in range(ZEITSCHRITTE):
    # 1. Kontakte knüpfen und Infektionen übertragen
    # Wir mischen die Population für zufällige tägliche Kontakte
    infizierte = [p for p in population if p.status == "I"]
    anfaellige = [p for p in population if p.status == "S"]

    for inf in infizierte:
        # Der Infizierte trifft so viele Leute, wie er Verbindungspunkte hat
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
            # Versucht zu genesen
            if random.random() < GENESUNGSRATE:
                p.status = "R"
                p.tage_seit_genesung = 0
        elif p.status == "R":
            # Tracker hochzählen
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
            neue_population.append(p)  # Person überlebt
    population = neue_population

    # 4. Demografie: Geburten
    # Die Anzahl der Geburten basiert auf der aktuellen Populationsgröße
    anzahl_geburten = sum(
        1 for _ in range(len(population)) if random.random() < GEBURTENRATE_TAG
    )
    for _ in range(anzahl_geburten):
        population.append(Person(status="S"))  # Babys werden gesund geboren

    # 5. Daten für Statistik sammeln
    S_count = sum(1 for p in population if p.status == "S")
    I_count = sum(1 for p in population if p.status == "I")
    R_count = sum(1 for p in population if p.status == "R")
    M_count = sum(1 for p in population if p.status == "M")

    stats_S.append(S_count)
    stats_I.append(I_count)
    stats_R.append(R_count)
    stats_M.append(M_count)
    stats_N.append(len(population))

# --- AUSWERTUNG UND PLOT ---
plt.figure(figsize=(12, 7))
plt.plot(stats_S, "b", label="Anfällig (S)")
plt.plot(stats_I, "r", label="Infiziert (I)")
plt.plot(stats_R, "g", label="Temporär Genesen (R)")
plt.plot(stats_M, "m", label="Dauerhaft Immun (M)")
plt.plot(stats_N, "k--", label="Gesamtbevölkerung (N)", alpha=0.5)

plt.title(
    f"Agentenbasiertes SIR-Modell - Szenario {SZENARIO} (Österreichische Demografie)"
)
plt.xlabel("Zeitschritte (Tage)")
plt.ylabel("Anzahl Personen")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.show()