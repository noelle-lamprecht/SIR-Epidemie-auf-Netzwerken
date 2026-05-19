# ODD-Beschreibung des Modells

## 1. Zweck und Muster
Das Modell simuliert die Ausbreitung einer Infektionskrankheit mit einem SIR-Kompartmentansatz. Es dient dazu, typische Epidemieverläufe zu analysieren, insbesondere den Anstieg der Infizierten, den Gipfel der Ausbreitung und den anschließenden Rückgang. Zwei Szenarien werden verglichen:
- Ein Szenario mit Gleichgewichts-ähnlichen Anfangsbedingungen.
- Ein Szenario mit fast vollständig anfälliger Population und einem einzelnen Indexfall.

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
- mu: Geburts-/Sterberate (Rückgang aus R nach S).

Skalen:
- Zeit: Diskrete Zeitschritte t = 1..500.
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
