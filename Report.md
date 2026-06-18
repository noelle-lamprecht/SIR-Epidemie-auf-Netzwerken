# Eine agentenbasierte Analyse des SIRS-Modells unter Einfluss von Netzwerktopologien, Demografie und Saisonalität  

 
## Abstract 

Dieser Bericht untersucht die Ausbreitungsdynamik von Infektionskrankheiten mithilfe agentenbasierter Modellierung (ABM). Ausgehend vom klassischen SIRS-Modell (Susceptible-Infected-Recovered-Susceptible) wird die Evolution einer Epidemie über fünf Komplexitätsstufen hinweg simuliert: (1) ein stochastisches Grundmodell mit homogen gemischten Zufallskontakten, (2) die Implementierung einer skalenfreien Netzwerktopologie nach dem Barabási-Albert-Modell (Preferential Attachment), (3) die Erweiterung um demografische Prozesse (Geburts- und Sterberaten) inklusive permanenter Immunität nach Mehrfachinfektionen, sowie (4, 5) die mathematische Modellierung mehrjähriger Saisonalitätseffekte. Die Ergebnisse zeigen, dass strukturelle Netzwerkknoten (Hubs) die initiale Ausbreitungsgeschwindigkeit massiv beschleunigen, während demografische Fluktuationen und temporäre Immunitäten zu zyklischen Wellenbewegungen führen. Das Modell demonstriert, dass rein homogene Interaktionsannahmen die realen epidemiologischen Verläufe systematisch unterschätzen. 

   

## 1. Introduction 

Infektionskrankheiten begleiten die Menschheit seit Jahrhunderten und stellen bis heute eine bedeutende Herausforderung für Gesundheitssysteme und Gesellschaften dar. Um die Ausbreitung von Krankheiten besser zu verstehen, werden epidemiologische Modelle eingesetzt. Eines der bekanntesten Modelle ist das von Kermack und McKendrick entwickelte SIRS-Modell. Dabei wird die Bevölkerung in die drei Zustände „Susceptible“ (anfällig), „Infected“ (infiziert) und „Recovered“ (genesen) eingeteilt. 

Obwohl klassische SIRS-Modelle wichtige Erkenntnisse liefern, beruhen sie auf mehreren Vereinfachungen. Häufig wird angenommen, dass alle Personen mit gleicher Wahrscheinlichkeit miteinander in Kontakt kommen. Darüber hinaus bleiben Bevölkerungsgröße und Umweltbedingungen meist konstant. Reale Gesellschaften weisen jedoch komplexe soziale Netzwerke, Geburten- und Sterbeprozesse sowie saisonale Schwankungen auf. 

Agentenbasierte Modelle ermöglichen es, solche Faktoren abzubilden. Jeder Agent repräsentiert dabei eine einzelne Person mit eigenen Eigenschaften und Zuständen. Dadurch können individuelle Interaktionen und deren Auswirkungen auf das Gesamtsystem untersucht werden. 

Die zentrale Forschungsfrage dieses Projekts lautet: 

Wie beeinflusst die schrittweise Integration von realistischer Netzwerktopologie, demografischer Dynamik und saisonalen Umwelteinflüssen den epidemischen Verlauf in einem agentenbasierten SIRS-Modell? 

 
Zur Beantwortung dieser Frage wurde ein bestehendes agentenbasiertes SIRS-Modell schrittweise erweitert. Ziel war es, den Einfluss jeder zusätzlichen Modellkomponente auf die Dynamik der Epidemie zu analysieren und die Unterschiede zwischen einfachen und realitätsnäheren Modellvarianten sichtbar zu machen. 

  

## 2. Method 

### 2.1 Modellarchitektur und Entitäten 

Das Modell besteht aus autonomen Agenten (Klasse `Person`), die sich in einer geschlossenen oder dynamischen Population befinden. Jeder Agent besitzt zu jedem Zeitschritt t (ein Tag) einen diskreten Zustand: 

-S (Susceptible): Gesund, aber empfänglich für das Virus. 

-I (Infected): Infiziert und infektiös gegenüber Kontakten aus dem Zustand S.  

-R (Recovered): Temporär immun nach einer überstandenen Infektion. 

-M (Immune/Maternally Protected): Dauerhaft immun (eingeführt in Erweiterung 3 & 4). 


### 2.2 Eingesetzte Bibliotheken 

Für die technische Implementierung in Python wurden folgende Kernbibliotheken verwendet: 

- `random`: Zur stochastischen Modellierung von Infektionswahrscheinlichkeiten, Genesen und zufälligen Stichprobenziehungen. 

- `matplotlib.pyplot` & `matplotlib.animation` & `matplotlib.patches` : Zur visuellen Aufbereitung der zeitlichen Verläufe sowie zur Erstellung dynamischer Netzwerkanimationen. 

- `networkx`: Zur Generierung und manipulation des Barabási-Albert-Graphen sowie zur Berechnung topologischer Eigenschaften (z.B. Knotengradverteilung). 

- `numpy`: Zur effizienten Generierung von Zufallsmatrizen (Zufallszahlen-Generatoren mit festem Seed) und zur Berechnung der trigonometrischen Saisonalitätskurve. 
  

### 2.3 Evolution des Quellcodes und Modellannahmen 

#### Codebeispiel 1: Das stochastische SIRS-Grundmodell mit dynamischen Zufallskontakten 

Im ersten Modellschritt wählen infizierte Agenten in jedem Schritt eine vollkommen zufällige Teilmenge aus der Gesamtbevölkerung aus. Dies simuliert eine homogene Masseninteraktion (z.B. öffentlicher Nahverkehr oder Großveranstaltungen). 


# 1. Make contacts and transmit infections 

```phython 

infected = [p for p in population if p.status == "I"] 

  
for inf in infected: 

    contacts = random.sample(population, min(inf.max_contacts, len(population))) 

    for contact in contacts: 

        if contact.status == "S": 

            if random.random() < INFECTION_RATE: 

                contact.status = "I" 
```

Erklärung: Für jeden Infizierten wird mittels random.sample eine Menge an Kontakten gezogen, die durch das individuelle Limit max_contacts begrenzt ist. Trifft ein infektiöser Agent auf einen Agenten im Zustand S, erfolgt die Transmission stochastisch mit der Wahrscheinlichkeit INFECTION_RATE (5%). Diese Modellannahme geht von festen sozialen Strukturen aus. 

#### Codebeispiel 2: Implementierung der Barabási-Albert-Netzwerktopologie 

Um reale soziale Netzwerke ("Scale-Free Networks") abzubilden, wurde das Kontaktsystem auf einen Graphen umgestellt, der nach dem Prinzip des bevorzugten Aufbaus (Preferential Attachment) generiert wird. Reiche Knoten (Hubs) werden dabei tendenziell noch reicher. 

# Transfer the graph connections into our person objects 
```python
ba_graph = nx.barabasi_albert_graph(n=POPULATION_SIZE, m=M_EDGES, seed=42) 


for edge in ba_graph.edges(): 

    p1_id, p2_id = edge 

    population[p1_id].contacts.append(population[p2_id]) 

    population[p2_id].contacts.append(population[p1_id]) 
```

  
Erklärung: Das Interaktionsnetzwerk wird über networkx initialisiert. Jeder neue Knoten verbindet sich bei der Entstehung mit m=2 bestehenden Knoten. Die Kanten werden anschließend als permanente Objektreferenzen in die Liste contacts des Agenten gespiegelt. Ein Infizierter kann nun ausschließlich Kontakte zu seinen direkten Netzwerknachbarn aufbauen, was die Infektionsketten lokalisiert. 


#### Codebeispiel 3: Demografische Dynamik und strukturelles Preferential Attachment bei Geburt 

In der dritten Stufe verlässt das Modell die Annahme einer konstanten Populationsgröße. Es werden tägliche Geburts- und Sterberaten auf Basis realer österreichischer Demografiedaten implementiert. Neugeborene müssen mathematisch korrekt in das bestehende Barabási-Netzwerk integriert werden. 

# Birth-Logic: A new baby enters the Barabási network 
```python
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

                node_list, size=M_EDGES, replace=False, p=probabilities 

            ) 
```

Erklärung: Stirbt ein Agent, wird sein Knoten gelöscht und alle Referenzen in den Nachbarlisten entfernt. Wird ein Agent geboren (status="S"), berechnet das System die Knotengrade (degrees) aller lebenden Netzwerkteilnehmer. Die Wahrscheinlichkeit einer Kopplung ist proportional zum aktuellen Grad des Knotens. Die Auswahl erfolgt stochastisch ohne Zurücklegen via np.random.choice. Zudem wurde eine funktionale Erweiterung integriert: Nach der zweiten überstandenen Infektion (infection_counter >= 2) wechselt ein Agent permanent in den Zustand M (dauerhafte Immunität). 


Codebeispiel 4: Kalt-Warm-Wechsel 

In der finalen Modellstufe wird der kontinuierliche Verlauf durch ein zweiphasiges, saisonales System ersetzt. Über einen Zeitraum von 2 Jahren (730 Zeitschritte) hinweg schalten die epidemiologischen Raten abrupt alle 182 Tage um. 
```python
--- SEASONAL RATES CHECK --- 

t // 182 determines the phase. Even phases = Cold, Odd = Warm 

if (t // 182) % 2 == 0: current_infection_rate = 0.05 # Cold season current_recovery_rate = 0.02 else: current_infection_rate = 0.03 # Warm season current_recovery_rate = 0.04 # Faster recovery in summer 

Saving season change days for visual lines in graph 

if t % 182 == 0 and t > 0: seasons_change.append(t) 
```

Erklärung: Mittels Ganzzahldivision (t // 182) wird das Jahr in zwei gleich lange Hälften geteilt. In der kalten Phase (Phasen 0 und 2) herrschen eine hohe Ansteckungsrate (0.05) und eine niedrige Genesungsrate (0.02). In der warmen Phase (Phase 1 und 3) sinkt die Ansteckungsrate auf 0.03, während sich die Genesungsrate auf 0.04 verdoppelt (Simulation eines gestärkten Immunsystems im Sommer). Die Übergangstage werden im Array seasons_change für die spätere Visualisierung festgehalten. 


## 3. Results 

Die Simulationen lieferten über die verschiedenen Entwicklungsstufen hinweg stark divergierende Systemzustände. 

### 3.1 Das Basismodell 

Unter der Annahme einer homogenen Durchmischung (Szenario 1: 4 Kontakte pro Tag, fixe Raten) zeigt das System den klassischen Verlauf einer Epidemie. Die infizierte Kurve steigt rasant an und erreicht einen steilen Peak, bevor der Mangel an anfälligen Personen (Susceptibles) durch die temporäre Immunität der Genesenen die Welle bricht. Da die Immunität nach exakt 30 Tagen abläuft, formiert sich nach einer Verzögerung ein gedämpftes, endemisches Gleichgewicht, bei dem das Virus dauerhaft in der Population zirkuliert. 


###  3.2 Der Einfluss des Barabási-Albert-Netzwerks 

Durch den Übergang von rein zufälligen Kontakten hin zu einer fixierten, skalenfreien Netzwerktopologie (Barabási-Albert-Graph) verändert sich die Dynamik des Infektionsgeschehens auf struktureller Ebene. Da es sich um eine stochastische Simulation handelt, führt jeder Durchlauf aufgrund von Zufallswerten zu leicht variierenden Kurvenverläufen; die epidemiologischen Kerneigenschaften bleiben jedoch konsistent. 

Zu Beginn der Simulation zeigt sich auch hier ein steiler, rasanter Anstieg der Infektionszahlen (Infected, rot). Dies liegt an der Topologie des Netzwerks: Sobald das Virus einen sogenannten "Hub" (einen Knoten mit überdurchschnittlich vielen Verbindungen) erreicht, breitet sich die Krankheit in sehr kurzer Zeit über dessen Kontakte aus.  

Nach dem ersten Peak bricht die Welle jedoch nicht tief ein, sondern geht – ähnlich wie das homogene Grundmodell – in ein stabiles, endemisches Gleichgewicht über. Der fundamentale Unterschied liegt hierbei in der Ursache dieses Plateaus: Während im Basismodell das Gleichgewicht durch die tägliche, vollkommene Neumischung der Kontakte gehalten wird, ist es im Barabási-Albert-Netzwerk an die starre Kantenstruktur gebunden. Das Virus zirkuliert kontinuierlich entlang etablierter sozialer Pfade. 

Weil die temporäre Immunität (Recovered, grün) im Modell zeitlich begrenzt ist, entsteht ein geschlossener, dynamischer Kreislauf: Sobald Individuen gesund und wieder anfällig (Susceptible, blau) werden, sorgt das starre Netzwerk dafür, dass sie durch ihre direkt verbundenen, infizierten Nachbarn hocheffizient reinfiziert werden. Die Annahme, dass sich das Virus in kleinen Populationen durch lokale Cluster-Immunität selbst isoliert und ausstirbt, wird durch die Simulationsdaten widerlegt. Das Netzwerk verhindert ein Erlöschen der Epidemie und stabilisiert das Infektionsgeschehen dauerhaft auf einem hohen Niveau. 


### 3.3 Ergebnisse des demografischen Netzwerkmodells mit Dauerimmunität 

Die Einführung von Geburts- und Sterbeprozessen führt in Kombination mit der dauerhaften Immunität nach der zweiten Infektion zu einer grundlegenden strukturellen Veränderung des Infektionsgeschehens. Da es sich um eine stochastische Simulation handelt, hängen die exakten Zeitpunkte vom Zufall ab; die grundlegenden Dynamiken eines Durchlaufs lassen sich jedoch sehr deutlich an den Kurvenverläufen nachvollziehen. 

Wie in der Simulation zu sehen ist, führt die Akkumulation von dauerhaft immunen Agenten (Dauerhaft Immun, lila) zu einem rasanten Anstieg dieser Gruppe von dauerhaft immunen Personen in den ersten 300 Tagen. Da Agenten nach ihrer zweiten überstandenen Infektion permanent in den Zustand M wechseln, sind am Ende mehr als zwei Drittel der gesamten Bevölkerung dauerhaft geschützt. Die Infektionskurve (Infiziert, rot) erreicht dabei recht früh in der Simulation ihren absoluten Höchststand (Peak), bevor sie durch die einsetzende Immunisierung kontinuierlich nach unten gedrückt wird. 

Dieser massive Anstieg der lila Kurve hat einen entscheidenden topologischen Effekt auf das Barabási-Albert-Netzwerk: Die dauerhaft immunen Agenten blockieren die starren Übertragungswege im Graph und wirken wie biologische Schutzwände (strukturelle Herdenimmunität). Obwohl sich in der zweiten Hälfte der Simulation die Anzahl der anfälligen Personen (Anfällig, blau) wieder auf einem stabilen Niveau einpendelt, sind diese gesunden Individuen durch die immunen Agenten isoliert. Das Virus kann sich im Netzwerk nicht mehr effektiv ausbreiten, da die Kontakte zu den verbleibenden gesunden Clustern blockiert sind. Infolgedessen sinkt die effektive Reproduktionszahl dauerhaft unter den kritischen Wert von 1, sodass die Infektionskette abbricht und die Epidemie im hinteren Drittel des simulierten Zeitraums vollständig erlischt. 

 
### 3.4 Saisonalitätseffekte 

Im Kalt-Warm-Modell (4 & 5) zeigt sich ein unregelmäßiges, oszillierendes Verhalten. Anstatt in ein stabiles, konstantes Gleichgewicht überzugehen, antwortet die Infektionskurve direkt auf die Kosinus-Modulation der Ansteckungsrate. In der simulierten Kältezeit kommt es zu sekundären und tertiären Ausbruchswellen. Bei der Wärmezeit sinkt die Kurve der Infizierten fast auf null, schwillt jedoch bei darauffolgender Kälte, angetrieben durch nachwachsende Anfällige, deren Immunität erloschen ist, erneut an. Die Modelle 4 und 5 unterscheiden sich lediglich im Punkt (M) permanente Immunität, welche zur Folge hat, dass durch diese die Krankheit schneller terminiert wird als, dass sie überhaupt in eine weitere Saison kommen kann. Bei Modell 4 bricht die Infektion spätestens in der ersten Warmphase ab (nach ~320 Tagen) 
 

## 4. Discussion, Conclusion and Limitations 

### Beantwortung der Forschungsfrage  

Die agentenbasierte Simulation konnte zeigen, dass epidemiologische Dynamiken massiv von strukturellen, demografischen und zeitlichen Rahmenbedingungen abhängen. Der Übergang zu einer skalenfreien Netzwerktopologie verdeutlicht, dass die Existenz von Super-Spreadern (Hubs) die initiale Ausbreitung stark beschleunigt, während die Fixierung der Kontakte im späteren Verlauf zu einer Stabilisierung des Infektionsgeschehens auf einem endemischen Plateau führt.  

Die Integration demografischer Prozesse zeigt, dass ein ständiger Zufluss neuer Individuen (Geburten) zwar theoretisch kontinuierlich neue, nicht-immune Agenten nachliefert, dieser Effekt jedoch durch den Mechanismus einer dauerhaften Immunität nach Zweitinfektion vollständig überkompensiert werden kann. Die Akkumulation dauerhaft geschützter Individuen blockiert die sozialen Pfade im Netzwerk, etabliert eine strukturelle Herdenimmunität und führt letztendlich zur vollständigen Elimination des Erregers. Wird das System zusätzlich um Kalt-/Warm-Perioden erweitert, verhindert der halbjährliche Wechsel der Umgebungsbedingungen das Verharren in einem statischen Gleichgewicht und erzwingt stattdessen die typischen, zyklischen Wellenbewegungen realer Infektionswellen.  

### Limitationen des Modells  

Obwohl das Modell wesentliche Aspekte der Realität abbildet, unterliegt es kritischen Vereinfachungen und somit Grenzen.  

Homogene Parameter: Die Infektions- und Genesungsraten sind für alle Agenten identisch. In der Realität variieren diese stark nach Alter, Vorerkrankungen und Immunstatus.  

Statische Netzwerktopologie: Das Barabási-Albert-Netzwerk wird einmalig generiert. Im echten Leben verändern Menschen ihr Kontaktverhalten adaptiv während einer Pandemie (z.B. durch Lockdowns, freiwillige Isolation oder Maskenpflicht).  

Geringe Populationsgröße: Mit N=300 Individuen ist das System anfällig für stochastisches Rauschen. Bestimmte Phänomene, wie das langfristige Überleben des Virus in kleinen Sub-Clustern, würden sich erst bei größeren Populationen (N>10.000) verlässlich analysieren lassen.  

### Ausblick und Weiterentwicklung  

Um die Belastbarkeit des Modells zu erhöhen, sollte ein dynamisches Netzwerk implementiert werden, bei dem ungesunde Agenten (I) isoliert werden und ihre Kanten temporär getrennt werden (Adaptive Rewiring). Zudem könnte die Einbindung von geografischen Koordinaten (Continuous Space oder Grid) anstelle rein abstrakter Netzwerkkanten die Modellierung von lokalen Quarantänemaßnahmen ermöglichen. 

### References 

Kermack, W. O., & McKendrick, A. G. (1927). A contribution to the mathematical theory of epidemics.Proceedings of the Royal Society of London. Series A, 115(772), 700-721. (Grundlagen der kompartimentellen Modellierung). 

Barabási, A. L., & Albert, R. (1999). Emergence of scaling in random networks. Science, 286(5439), 509-512. (Mathematische Herleitung der skalenfreien Netzwerktopologie). 

STATISTIK AUSTRIA. (2026). Geburtenbilanz 2025 zum 6. Mal in Folge negativ: 11 048 mehr Sterbefälle als Geborene 
