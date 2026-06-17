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
Zeit: 1 Zeitschritt entspricht 1 Tag. Die Gesamtdauer beträgt 730 Zeitschritte.
Raum: Nicht-räumlich (netzwerkbasiert / "Well-Mixed" innerhalb der Verbindungspunkte).



### 1.3 Prozessübersicht und Terminierung

Innerhalb jedes Zeitschritts (Tages) werden folgende Prozesse nacheinander für alle Agenten ausgeführt:

1. Infektionsphase: Alle infizierten Agenten wählen zufällig Kontakte aus der Population (entsprechend ihrer `max_verbindungen`) und können diese mit der Wahrscheinlichkeit (beta) anstecken.

2. Zustands-Update: Infizierte Agenten genesen mit der Wahrscheinlichkeit (gamma).

Genesene Agenten (R) zählen ihre Immunitätstage hoch. Nach Ablauf von 30 Tagen werden sie wieder anfällig (S), es sei denn, es war ihre zweite Infektion – dann werden sie dauerhaft immun (M).

3. Demografie (Mortalität): Jeder Agent kann mit der Wahrscheinlichkeit `STERBERATE_TAG` sterben und wird aus der Simulation gelöscht.
4. Demografie (Natalität): Basierend auf der aktuellen Populationsgröße und der `GEBURTENRATE_TAG` werden neue Agenten im Zustand (S) geboren.


5. Datenerfassung: Die Systemzustände werden für die Endauswertung aufgezeichnet.

---

## 2. Design Concepts (Entwurfskonzepte)

Emergenz: Die Gesamtverlaufskurven (Wellenbewegungen, Herdenimmunität oder das Aussterben des Virus) entstehen dynamisch aus den individuellen, stochastischen Interaktionen der einzelnen Agenten.
Anpassung / Ziele: Keine. Die Agenten handeln rein regelbasiert und zeigen kein adaptives Verhalten (z.B. freiwillige Isolation bei Infektion).
Wahrnehmung: Infizierte Agenten "sehen" die gesamte Population, um potenzielle Kontakte für ihre Verbindungspunkte auszuwählen.
Interaktion: Direkte stochastische Interaktion zwischen infizierten Agenten und ihren zufällig ausgewählten Kontaktpartnern.
Stochastik: Zufallsprozesse steuern die Kontaktwahl, den Erfolg einer Infektion, die Genesung sowie Geburten und Todesfälle. Dies spiegelt reale biologische und gesellschaftliche Unschärfen wider.
Kollektiv: Die Agenten sind in den drei Szenarien durch ihre Kontaktstrukturen (homogen vs. heterogen) organisiert.
Beobachtung: Am Ende jedes Zeitschritts werden die Summen aller Agenten pro Zustand (S, I, R, M) und die Gesamtbevölkerung (N) aggregiert und grafisch als Liniendiagramm ausgegeben.

---

## 3. Details

### 3.1 Initialisierung

Die Startpopulation wird mit (N = 300) Agenten instanziiert.
Szenario 1: 5 Agenten starten im Zustand (I) (`infektions_counter = 1`), alle anderen in (S). Jeder Agent erhält fix `max_verbindungen = 4`.
Szenario 2: 5 Agenten starten in (I), alle anderen in (S). Jeder Agent erhält zufällig gleichverteilt zwischen 1 und 4 `max_verbindungen`.
Szenario 3: 1 Agent startet in (I), alle anderen in (S). Jeder Agent erhält zufällig gleichverteilt zwischen 1 und 4 `max_verbindungen`.

### 3.2 Eingangsdaten

Das Modell nutzt die demografischen Kennzahlen Österreichs (hochgerechnet/angepasst auf das Jahr 2026), umgerechnet von Jahres- auf Tageswerte:

Geburtenrate: ca. 8,2 pro 1.000 Einwohner pro Jahr (8.2 / 1000 / 365) pro Tag.
Sterberate: ca. 9,4 pro 1.000 Einwohner pro Jahr (9.4 / 1000 / 365) pro Tag.

### 3.3 Submodelle

#### Infektions-Wahrscheinlichkeit

Für jeden Kontakt eines Infizierten mit einem gesunden Agenten (S) gilt:


Zufallszahl zwischen 0 und 1 < ANSTECKUNGSRATE (0.05) -> Infektion erfolgreich

#### Genesungs-Wahrscheinlichkeit

Für jeden Infizierten (I) gilt in jedem Zeitschritt:


Zufallszahl zwischen 0 und 1 < GENESUNGSRATE (0.02) -> Wechsel zu (R)

#### Immunitäts-Ablauf und Reinfektion

Wenn ein Agent im Zustand (R) den Wert `tage_seit_genesung == 30` erreicht, greift folgende Logik:


IF infektions_counter >= 2 -> Status = M (Dauerhaft Immun)

ELSE -> Status = S (Wieder Anfällig)