import random
import matplotlib.pyplot as plt
import numpy as np

# --- KONFIGURATION ---
SZENARIO = 1  # Wähle hier: 1, 2 oder 3
JAHRE = 4
ZEITSCHRITTE = 365 * JAHRE  # 1460 Tage (4 Jahre)
ANZAHL_PERSONEN = 300

BASIS_ANSTECKUNGSRATE = 0.05
GENESUNGSRATE = 0.02
IMMUNITAETS_DAUER = 30

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
        self.status = status  # 'S' (Anfällig), 'I' (Infiziert), 'R' (Genesen)
        self.tage_seit_genesung = 0  # Tracker für die 30 Zeitschritte Immunität
        self.max_verbindungen = random.randint(
            VERBINDUNGEN_MIN, VERBINDUNGEN_MAX
        )


# --- SIMULATION INITIALISIEREN ---
population = [Person() for _ in range(ANZAHL_PERSONEN)]

# Erste Infizierte setzen
for i in range(URSPRUNGLICH_INFIZIERT):
    population[i].status = "I"

# Statistik-Listen für die Grafik
stats_S, stats_I, stats_R = [], [], []
stats_rate = []

# Variablen für die Peak-Analyse (Höhepunkt der Welle)
max_infizierte = 0
peak_tag = 0

print("-" * 75)
print(
    f"{'Tag':<5} | {'Anfällig (S)':<12} | {'Infiziert (I)':<12} | {'Genesen (R)':<12} | {'Ansteckungsrate':<15}"
)
print("-" * 75)

# --- SIMULATIONS-SCHLEIFE (Zeitschritte) ---
for t in range(ZEITSCHRITTE):

    # =========================================================================
    # === DYNAMISCHE SAISONALITÄT ÜBER MEHRERE JAHRE ===
    # Die Cosinus-Kurve wiederholt sich nun alle 365 Tage exakt von vorn.
    # =========================================================================
    saisonaler_faktor = np.cos(2 * np.pi * t / 365)
    aktuelle_ansteckungsrate = BASIS_ANSTECKUNGSRATE + (saisonaler_faktor * 0.03)
    stats_rate.append(aktuelle_ansteckungsrate)

    # 1. Kontakte knüpfen und Infektionen übertragen
    infizierte = [p for p in population if p.status == "I"]

    for inf in infizierte:
        kontakte = random.sample(
            population, min(inf.max_verbindungen, len(population))
        )
        for kontakt in kontakte:
            if kontakt.status == "S":
                if random.random() < aktuelle_ansteckungsrate:
                    kontakt.status = "I"

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

    if I_count > max_infizierte:
        max_infizierte = I_count
        peak_tag = t

    # 4. Zahlen alle 30 Tage in der Konsole ausgeben (Intervall erhöht wegen der langen Laufzeit)
    if t % 30 == 0 or t == ZEITSCHRITTE - 1:
        print(f"{t:<5} | {S_count:<12} | {I_count:<12} | {R_count:<12} | {aktuelle_ansteckungsrate*100:<13.2f}%")

print("-" * 75)
print(f"\nANALYSE:")
print(
    f"Der absolute Höchststand der gesamten 4 Jahre war an Tag {peak_tag} mit {max_infizierte} gleichzeitig Infizierten."
)
print("-" * 75)

# --- AUSWERTUNG UND PLOT ---
fig, ax1 = plt.subplots(figsize=(15, 8))

# Erste Y-Achse für die Personen-Anzahlen
ax1.plot(stats_S, "b", label="Anfällig (S)", alpha=0.8)
ax1.plot(stats_I, "r", label="Infiziert (I)", linewidth=2)
ax1.plot(stats_R, "g", label="Temporär Genesen (R)", alpha=0.8)
ax1.set_xlabel("Zeitschritte (Tage)")
ax1.set_ylabel("Anzahl Personen")

# Zweite Y-Achse (Rechts) für die saisonale Ansteckungsrate
ax2 = ax1.twinx()
ax2.plot(stats_rate, "orange", linestyle=":", alpha=0.5, label="Ansteckungsrate")
ax2.set_ylabel("Ansteckungsrate", color="orange")
ax2.tick_params(axis='y', labelcolor="orange")

# =========================================================================
# === VISUELLE JAHRESZEITEN-MARKIERUNG IM PLOT ===
# Wir färben die "Wintermonate" (Anfang/Ende eines Jahres) im Hintergrund grau.
# =========================================================================
for jahr in range(JAHRE):
    start_jahr = jahr * 365
    # Erster Winterteil (Januar/Februar -> Tag 0 bis 60 des jeweiligen Jahres)
    ax1.axvspan(start_jahr, start_jahr + 60, color='gray', alpha=0.1)
    # Zweiter Winterteil (November/Dezember -> Tag 300 bis 365 des jeweiligen Jahres)
    ax1.axvspan(start_jahr + 300, start_jahr + 365, color='gray', alpha=0.1)

# Textbeschriftung für die Jahre hinzufügen
for jahr in range(JAHRE):
    ax1.text(jahr * 365 + 150, 280, f"Jahr {jahr+1}", fontsize=10, weight='bold', horizontalalignment='center')
# =========================================================================

# Vertikale Linie für den allzeit Peak
ax1.axvline(
    x=peak_tag,
    color="darkred",
    linestyle="--",
    label=f"Allzeit-Peak (Tag {peak_tag})",
    alpha=0.7,
)

plt.title(f"4-Jahres-Langzeitsimulation (SIRS-Modell mit saisonalen Wellen)")
ax1.grid(True, linestyle="--", alpha=0.3)

# Legenden zusammenführen
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

plt.show()