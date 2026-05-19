# SIR-Epidemie-auf-Netzwerken

1. Purpose and patterns
The model is designed to simulate the spread of an infectious disease on different network structures in order to analyze structural effects. As general patterns, an SIR dynamic is expected, characterized by an exponential increase in infected individuals, a peak of infections, and a subsequent decline due to immunity. Furthermore, different epidemic curves are expected depending on the network type, even when using the same parameters.
2. Entities, State Variables, and Scales
The model includes the following entities:
•	Nodes: Represent individuals.
•	Edges: Represent contacts.
The state variables per node are:
•	State: Can be Susceptible ($S$), Infected ($I$), or Recovered ($R$).
•	Degree: The number of connections a node has.
•	Duration of infection: As an optional extension.
•	(Other variables/symbols listed in the document: $\delta$, $\beta I$, $\mu$, $P_0$).
Scales:
•	Time: Discrete time steps ($t=0,1,2,...$).
•	Space: Implicitly defined by the network structure (there is no physical space).
3. Process Overview and Scheduling
For each time step, the following sequence of processes is executed, with all states being updated simultaneously:
    1.	Contacts
    2.	Infections: Susceptible individuals can become infected through contact with infected individuals.
    3.	Recoveries: Infected individuals recover after a certain amount of time.
    4.	State Update
4. Design Concepts
•	Basic Principles: The model is based on stochastic state transitions within fixed graph structures.
•	Interaction: Interaction is locally limited to the edges of the network.
•	Stochasticity: Both the network generation (initialization) and the infection processes use random numbers to represent real-world uncertainties.
•	Observation: The primary measure recorded over time is the number of currently infected individuals (the epidemic curve). "Hubs" in scale-free networks play a critical role as super-spreaders.
•	Feedback Loops:
    o	Positive Feedback: More infected individuals lead to more contacts, which leads to even more infected individuals. This explains the exponential growth at the beginning of an epidemic.
    o	Negative Feedback: The more people are infected or recovered, the fewer susceptible individuals remain. This stabilizes the system and causes the wave to subside.
•	Nonlinearity
•	Emergence
•	Tipping Points (Kipppunkte)
5. Initialization
First, the chosen network topology is generated. One or more "index patients" are infected either randomly or deliberately (in the case of hubs) to start the spread.
6. Input Data

7. Submodels
•	Infection Logic: The probability of a healthy node becoming infected in a given step increases with the number of its infected neighbors.
•	Topology Models: Mathematical algorithms used to generate ER, WS, and BA graphs.

