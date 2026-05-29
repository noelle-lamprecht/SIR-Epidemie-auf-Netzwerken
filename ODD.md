# ODD-Beschreibung des Modells

## 1. Zweck und Muster
Das Modell simuliert die Ausbreitung einer Infektionskrankheit mit einem SIR-Kompartmentansatz. Es dient dazu, typische Epidemieverläufe zu analysieren, insbesondere den Anstieg der Infizierten, den Gipfel der Ausbreitung und den anschließenden Rückgang. Zwei Szenarien werden verglichen:
#####- Ein Szenario mit Gleichgewichts-ähnlichen Anfangsbedingungen.##### Hat keinen Mehrwert, da sich dieses Modell sofort ausgleicht und keine nennenswerte Daten zeigt.
- Ein Szenario mit ###fast### vollständig anfälliger Population und einem einzelnen Indexfall.

## 2. Entitäten, Zustandsvariablen und Skalen
Entitäten:
- Population als aggregiertes System (nicht individuelle Knoten).

Zustandsvariablen:
- S(t): Anzahl der empfänglichen Personen.
- I(t): Anzahl der infizierten Personen.
- R(t): Anzahl der genesenen Personen.
- N: Gesamtbevölkerung.
- beta: Ansteckungsrate.
- gamma: Genesungsrate.
- #####mu: Geburts-/Sterberate (Rückgang aus R nach S).#####

Skalen:
- #####Zeit: Diskrete Zeitschritte t = 1..500.#####
- Raum: Keine räumliche Auflösung; Modell ist homogen über die Population.

## 3. Prozessübersicht und Zeitplanung
Jeder Zeitschritt umfasst die folgenden Prozesse in Reihenfolge:
1. Infektionen: Suszeptible Personen können sich durch Kontakt mit Infizierten anstecken.
2. Genesungen: Infizierte Personen erholen sich mit Rate gamma.
3. Rückkehr von Genesenen: Genesene Personen können mit Rate mu wieder empfänglich werden.
4. Aktualisierung der Zustände: Alle Kompartimente werden gleichzeitig aktualisiert.

## 4. Designkonzepte
- Grundprinzipien: Stochastische Epidemiedynamik wird als deterministische diskrete Differenzengleichung abgebildet.
- Interaktion: Die Infektionsdynamik ist homogen über die gesamte Population.
- Beobachtung: Erfasst wird vor allem der zeitliche Verlauf von I(t) (Epidemiekurve).
- Feedback:
  - Positives Feedback: Mehr Infizierte erhöhen die Ansteckung neuer Suszeptibler.
  - Negatives Feedback: Mit wachsendem R(t) und I(t) sinkt der Anteil der Suszeptiblen.
- Nichtlinearität: Die Infektionsrate hängt vom Produkt S * I ab.

## 5. Initialisierung
- Gesamtpopulation N = 1000.
- Zeithorizont tmax = 500.
- Zwei Szenarien werden initialisiert:
  - Szenario 1:
    - beta = 0.3
    - gamma = 0.3
    - mu = 0.3
    - S(0) = 100
    - I(0) = 900
    - R(0) = 0
  - Szenario 2:
    - beta = 0.6
    - gamma = 0.1
    - mu = 0.3
    - S(0) = 999
    - I(0) = 1
    - R(0) = 0

## 6. Eingabedaten
- N = 1000
- tmax = 500
- beta, gamma, mu für die beiden Szenarien
- Anfangszustände S(0), I(0), R(0)

## 7. Submodelle
### 7.1 Infektionslogik
- Suszeptible Personen infizieren sich proportional zu beta/N * S * I.
- Formel: Delta I = beta / N * S(t-1) * I(t-1) - gamma * I(t-1).

### 7.2 Genesungslogik
- Infizierte erholen sich mit Rate gamma.
- Formel: Delta R = gamma * I(t-1) - mu * R(t-1).

### 7.3 Rückgang von Genesenen
- Ein Teil der Genesenen wechselt wieder in die empfängliche Klasse.
- Formel: Delta S = -beta / N * S(t-1) * I(t-1) + mu * R(t-1).

### 7.4 Numerische Integration
- Die Kompartimentwerte werden für jeden Zeitschritt simultan aktualisiert.
- Werte werden auf 0 abgeschnitten, um negative Populationsgrößen zu vermeiden.





Das ist ein hervorragender und absolut professioneller Ansatz! Ein **ODD (Overview, Design Concepts, Details)** Protokoll ist der weltweite Standard, um agentenbasierte Modelle (ABMs) präzise und wissenschaftlich sauber zu dokumentieren. Es sorgt dafür, dass jeder genau versteht, wie deine Simulation im Hintergrund aufgebaut ist.

Hier ist das vollständige ODD-Protokoll für dein erweitertes SIR-Modell:

---

# ODD Protokoll: Agentenbasiertes SIR-Modell mit Netzwerkkontakten und Demografie

## 1. Übersicht

### 1.1 Zweck

Der Zweck des Modells ist es, die Ausbreitungsdynamik einer Infektionskrankheit in einer geschlossenen, aber demografisch dynamischen Population (basierend auf österreichischen Raten) zu untersuchen. Dabei wird analysiert, wie sich unterschiedliche Kontaktdichten (Szenario 1 vs. Szenario 2/3), die Anzahl der Erstinfizierten sowie die Möglichkeit einer Reinfektion mit anschließender dauerhafter Immunität auf den Verlauf der Epidemie auswirken.

### 1.2 Entitäten, Zustandsvariablen und Skalen

Entitäten (Agenten): Personen der Population.
Zustandsvariablen der Agenten:
`status`: Aktueller Zustand 
S = Anfällig
I = Infiziert
R = Temporär Genesen
M = Dauerhaft Immun
`infektions_counter`: Anzahl, wie oft der Agent bereits infiziert wurde (Ganzzahl größer/gleich 0).
`tage_seit_genesung`: Zeitschritte, die seit dem Wechsel in den Zustand "R" vergangen sind.
`max_verbindungen`: Individuelle maximale Anzahl täglicher Kontakte (netzwerkspezifisch).


Globale Variablen:
 `ANZAHL_PERSONEN` (N)
 `ANSTECKUNGSRATE` (beta)
 `GENESUNGSRATE` (gamma)
 `IMMUNITAETS_DAUER`
 `GEBURTENRATE_TAG`
 `STERBERATE_TAG`
Skalen: 
Zeit: 1 Zeitschritt entspricht 1 Tag. Die Gesamtdauer beträgt 200 Zeitschritte.
Raum: Nicht-räumlich (netzwerkbasiert / "Well-Mixed" innerhalb der Verbindungspunkte).



### 1.3 Prozessübersicht und Terminierung

Innerhalb jedes Zeitschritts (Tages) werden folgende Prozesse nacheinander für alle Agenten ausgeführt:

1. Infektionsphase: Alle infizierten Agenten wählen zufällig Kontakte aus der Population (entsprechend ihrer `max_verbindungen`) und können diese mit der Wahrscheinlichkeit (beta) anstecken.
2. Zustands-Update: Infizierte Agenten genesen mit der Wahrscheinlichkeit (gamma).

Genesene Agenten (R) zählen ihre Immunitätstage hoch. Nach Ablauf von 30 Tagen werden sie wieder anfällig (S), es sei denn, es war ihre zweite Infektion – dann werden sie dauerhaft immun (M).


3. Demografie (Mortalität): Jeder Agent kann mit der Wahrscheinlichkeit `STERBERATE_TAG` sterben und wird aus der Simulation gelöscht.
4. Demografie (Natalität): Basierend auf der aktuellen Populationsgröße und der `GEBURTENRATE_TAG` werden neue Agenten im Zustand $S$ geboren.
5. Datenerfassung: Die Systemzustände werden für die Endauswertung aufgezeichnet.

---

## 2. Design Concepts (Entwurfskonzepte)

* **Emergenz (Emergence):** Die Gesamtverlaufskurven (Wellenbewegungen, Herdenimmunität oder das Aussterben des Virus) entstehen dynamisch aus den individuellen, stochastischen Interaktionen der einzelnen Agenten.
* **Anpassung (Adaptation) / Ziele (Objectives):** Keine. Die Agenten handeln rein regelbasiert und zeigen kein adaptives Verhalten (z.B. freiwillige Isolation bei Infektion).
* **Sensing (Wahrnehmung):** Infizierte Agenten "sehen" die gesamte Population, um potenzielle Kontakte für ihre Verbindungspunkte auszuwählen.
* **Interaktion (Interaction):** Direkte stochastische Interaktion zwischen infizierten Agenten und ihren zufällig ausgewählten Kontaktpartnern.
* **Stochastik (Stochasticity):** Zufallsprozesse steuern die Kontaktwahl, den Erfolg einer Infektion, die Genesung sowie Geburten und Todesfälle. Dies spiegelt reale biologische und gesellschaftliche Unschärfen wider.
* **Kollektive (Collectives):** Die Agenten sind in den drei Szenarien durch ihre Kontaktstrukturen (homogen vs. heterogen) organisiert.
* **Beobachtung (Observation):** Am Ende jedes Zeitschritts werden die Summen aller Agenten pro Zustand ($S, I, R, M$) und die Gesamtbevölkerung ($N$) aggregiert und grafisch als Liniendiagramm ausgegeben.

---

## 3. Details (Details)

### 3.1 Initialization (Initialisierung)

* Die Startpopulation wird mit $N = 300$ Agenten instanziiert.
* **Szenario 1:** 5 Agenten starten im Zustand $I$ (`infektions_counter = 1`), alle anderen in $S$. Jeder Agent erhält fix `max_verbindungen = 4`.
* **Szenario 2:** 5 Agenten starten in $I$, alle anderen in $S$. Jeder Agent erhält zufällig gleichverteilt zwischen 1 und 4 `max_verbindungen`.
* **Szenario 3:** 1 Agent startet in $I$, alle anderen in $S$. Jeder Agent erhält zufällig gleichverteilt zwischen 1 und 4 `max_verbindungen`.

### 3.2 Input Data (Eingangsdaten)

Das Modell nutzt die demografischen Kennzahlen Österreichs (hochgerechnet/angepasst auf das Jahr 2026), umgerechnet von Jahres- auf Tageswerte:

* Geburtenrate: ca. 8,3 pro 1.000 Einwohner pro Jahr $\rightarrow \frac{8.3}{1000} / 365$ pro Tag.
* Sterberate: ca. 9,5 pro 1.000 Einwohner pro Jahr $\rightarrow \frac{9.5}{1000} / 365$ pro Tag.

### 3.3 Submodels (Submodelle)

#### Infektions-Wahrscheinlichkeit

Für jeden Kontakt eines Infizierten mit einem gesunden Agenten ($S$) gilt:


$$\text{Zufallszahl zwischen 0 und 1} < \text{ANSTECKUNGSRATE } (0.05) \rightarrow \text{Infektion erfolgreich}$$

#### Genesungs-Wahrscheinlichkeit

Für jeden Infizierten ($I$) gilt in jedem Zeitschritt:


$$\text{Zufallszahl zwischen 0 und 1} < \text{GENESUNGSRATE } (0.02) \rightarrow \text{Wechsel zu } R$$

#### Immunitäts-Ablauf und Reinfektion

Wenn ein Agent im Zustand $R$ den Wert `tage_seit_genesung == 30` erreicht, greift folgende Logik:


$$\text{IF } \text{infektions\_counter} \ge 2 \rightarrow \text{Status} = M \quad (\text{Dauerhaft Immun})$$

$$\text{ELSE} \rightarrow \text{Status} = S \quad (\text{Wieder Anfällig})$$