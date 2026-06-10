import random
import matplotlib.pyplot as plt
import networkx as nx  # WICHTIG für das Netzwerk-Modell
import numpy as np

# --- KONFIGURATION ---
SZENARIO = 1
JAHRE = 2
ZEITSCHRITTE = 365 * JAHRE  # 730 Tage (2 Jahre)
ANZAHL_PERSONEN = 300

ANSTECKUNGSRATE = 0.05
GENESUNGSRATE = 0.02
IMMUNITAETS_DAUER = 30

# Österreichische Raten (auf Tagesbasis umgerechnet)
GEBURTENRATE_TAG = (8.2 / 1000) / 365
STERBERATE_TAG = (9.4 / 1000) / 365

URSPRUNGLICH_INFIZIERT = 5

# =========================================================================
# === BARABÁSI-ALBERT NETZWERK PARAMETER ===
# M_KANTEN bestimmt, wie viele Kontakte neue Personen knüpfen (Dichte)
# =========================================================================
M_KANTEN = 2


# --- AGENTEN-KLASSE (Die Personen) ---
class Person:

    def __init__(self, status="S", id=0):
        self.id = id  # ID zur eindeutigen Zuordnung im Netzwerk
        self.status = status  # 'S', 'I', 'R', 'M'
        self.infektions_counter = 0
        self.tage_seit_genesung = 0
        # Die Kontakte werden fest im Netzwerk verwaltet
        self.kontakte = []


# --- SIMULATION INITIALISIEREN ---
population = [Person(id=i) for i in range(ANZAHL_PERSONEN)]

# Nächste freie ID für Neugeborene tracken
naechste_id = ANZAHL_PERSONEN

# Erste Infizierte setzen
for i in range(URSPRUNGLICH_INFIZIERT):
    population[i].status = "I"
    population[i].infektions_counter = 1

# =========================================================================
# === BARABÁSI-ALBERT NETZWERK INITIALISIERUNG ===
# Wir bauen den Start-Graphen und verknüpfen die Agenten initial miteinander.
# =========================================================================
ba_graph = nx.barabasi_albert_graph(n=ANZAHL_PERSONEN, m=M_KANTEN, seed=42)

for edge in ba_graph.edges():
    p1_id, p2_id = edge
    population[p1_id].kontakte.append(population[p2_id])
    population[p2_id].kontakte.append(population[p1_id])
# =========================================================================

# Statistik-Listen für die Grafik
stats_S, stats_I, stats_R, stats_M, stats_N = [], [], [], [], []

max_infizierte = 0
peak_tag = 0

print("-" * 85)
print(
    f"{'Tag':<5} | {'Anfällig (S)':<13} | {'Infiziert (I)':<13} | {'Temporär (R)':<13} | {'Immun (M)':<10} | {'Gesamt (N)':<10}"
)
print("-" * 85)

# --- SIMULATIONS-SCHLEIFE (Zeitschritte) ---
for t in range(ZEITSCHRITTE):

    # =========================================================================
    # === BARABÁSI-ALBERT NETZWERK ANWENDUNG (Infektionen) ===
    # Infektionen werden nur an direkte Netzwerk-Nachbarn weitergegeben.
    # =========================================================================
    infizierte = [p for p in population if p.status == "I"]

    for inf in infizierte:
        for kontakt in inf.kontakte:
            if kontakt.status == "S":
                if random.random() < ANSTECKUNGSRATE:
                    kontakt.status = "I"
                    kontakt.infektions_counter += 1
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
                if p.infektions_counter >= 2:
                    p.status = "M"  # Dauerhaft immun nach 2 Infektionen
                else:
                    p.status = "S"  # Wieder anfällig

    # 3. Demografie: Sterbefälle
    # Wenn eine Person stirbt, müssen wir sie auch aus den Kontaktlisten aller anderen löschen!
    ueberlebende = []
    for p in population:
        if random.random() > STERBERATE_TAG:
            ueberlebende.append(p)
        else:
            # Person stirbt -> Sie wird aus dem networkx-Graphen entfernt
            if ba_graph.has_node(p.id):
                ba_graph.remove_node(p.id)
            # Aus den Kontaktlisten der Nachbarn löschen
            for nachbar in p.kontakte:
                if p in nachbar.kontakte:
                    nachbar.kontakte.remove(p)

    population = ueberlebende

    # 4. Demografie: Geburten
    # Ein neues Baby kommt ins Barabási-Netzwerk ("Preferential Attachment")
    anzahl_geburten = sum(
        1 for _ in range(len(population)) if random.random() < GEBURTENRATE_TAG
    )

    for _ in range(anzahl_geburten):
        neues_baby = Person(status="S", id=naechste_id)

        if len(population) >= M_KANTEN:
            # Das mathematische Barabási-Modell berechnet, welche alten Knoten die neuen Kontakte bekommen
            # Knoten mit hohem "Degree" (vielen Kontakten) werden bevorzugt gewählt.
            knoten_liste = list(ba_graph.nodes())
            grade = [ba_graph.degree(n) for n in knoten_liste]
            summe_grade = sum(grade)

            if summe_grade > 0:
                wahrscheinlichkeiten = [g / summe_grade for g in grade]
                # Wähle M_KANTEN existierende IDs basierend auf ihrer Beliebtheit
                gewaehlte_partner_ids = np.random.choice(
                    knoten_liste,
                    size=M_KANTEN,
                    replace=False,
                    p=wahrscheinlichkeiten,
                )

                # Im Graphen und in den Objekten verknüpfen
                ba_graph.add_node(neues_baby.id)
                for p_id in gewaehlte_partner_ids:
                    ba_graph.add_edge(neues_baby.id, p_id)
                    # Den passenden Agenten in der Population suchen und verknüpfen
                    for akt_person in population:
                        if akt_person.id == p_id:
                            akt_person.kontakte.append(neues_baby)
                            neues_baby.kontakte.append(akt_person)
                            break

        population.append(neues_baby)
        naechste_id += 1

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

plt.axvline(
    x=peak_tag,
    color="gray",
    linestyle="--",
    label=f"Peak (Tag {peak_tag})",
    alpha=0.7,
)

plt.title(
    f"SIRS-Modell mit Barabási-Netzwerk, Dauerimmunität & Demografie (M={M_KANTEN})"
)
plt.xlabel("Zeitschritte (Tage)")
plt.ylabel("Anzahl Personen")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.show()
