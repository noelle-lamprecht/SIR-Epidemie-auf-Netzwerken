# ODD Protocol: Agent-based SIR Model with Network Contacts and Demography

## 1. Overview

### 1.1 Purpose

The purpose of the model is to investigate the spread dynamics of an infectious disease in a closed but demographically dynamic population (based on Austrian rates). The analysis examines how different contact densities (Scenario 1 vs. Scenario 2/3), the number of initially infected people, and the possibility of reinfection with subsequent permanent immunity affect the course of the epidemic.

### 1.2 Entities, State Variables and Scales

Entities (Agents): People in the population.
Agent state variables:
`status`: Current state
S = Susceptible
I = Infected
R = Temporarily Recovered
M = Permanently Immune
`infection_counter`: Number of times the agent has been infected (integer ≥ 0).
`days_since_recovery`: Time steps elapsed since transitioning to "R" state.
`max_contacts`: Individual maximum number of daily contacts (network-specific).


Global variables:
 `POPULATION_SIZE` (N)
 `INFECTION_RATE` (beta)
 `RECOVERY_RATE` (gamma)
 `IMMUNITY_DURATION`
 `BIRTH_RATE_DAY`
 `DEATH_RATE_DAY`
Scales:
Time: 1 time step = 1 day. Total duration = 730 time steps.
Space: Non-spatial (network-based / "well-mixed" within contact points).



### 1.3 Process Overview and Termination

Within each time step (day), the following processes are executed sequentially for all agents:

1. Infection phase: All infected agents randomly select contacts from the population (according to their `max_contacts`) and can infect them with probability (beta).

2. Status update: Infected agents recover with probability (gamma).

Recovered agents (R) increment their immunity days. After 30 days elapse, they return to susceptible (S), unless it was their second infection – then they become permanently immune (M).

3. Demography (Mortality): Each agent can die with probability `DEATH_RATE_DAY` and is removed from the simulation.
4. Demography (Natality): Based on current population size and `BIRTH_RATE_DAY`, new agents are born in state (S).


5. Data collection: System states are recorded for final evaluation.

---

## 2. Design Concepts

Emergence: Overall trajectory curves (wave movements, herd immunity, or virus extinction) emerge dynamically from individual stochastic interactions of agents.
Adaptation / Objectives: None. Agents act purely rule-based and show no adaptive behavior (e.g., voluntary isolation upon infection).
Sensing: Infected agents "see" the entire population to select potential contacts for their connection points.
Interaction: Direct stochastic interaction between infected agents and their randomly selected contact partners.
Stochasticity: Random processes control contact selection, infection success, recovery, births, and deaths. This reflects real biological and societal uncertainty.
Collectives: Agents are organized in the three scenarios through their contact structures (homogeneous vs. heterogeneous).
Observation: At the end of each time step, the sums of all agents per state (S, I, R, M) and total population (N) are aggregated and output graphically as a line plot.

---

## 3. Details

### 3.1 Initialization

The initial population is instantiated with (N = 300) agents.
Scenario 1: 5 agents start in state (I) (`infection_counter = 1`), all others in (S). Each agent receives fixed `max_contacts = 4`.
Scenario 2: 5 agents start in (I), all others in (S). Each agent receives randomly uniformly distributed between 1 and 4 `max_contacts`.
Scenario 3: 1 agent starts in (I), all others in (S). Each agent receives randomly uniformly distributed between 1 and 4 `max_contacts`.

### 3.2 Input Data

The model uses Austrian demographic figures (extrapolated/adjusted to 2026), converted from yearly to daily values:

Birth rate: approx. 8.2 per 1,000 inhabitants per year (8.2 / 1000 / 365) per day.
Death rate: approx. 9.4 per 1,000 inhabitants per year (9.4 / 1000 / 365) per day.

### 3.3 Submodels

#### Infection Probability

For each contact of an infected agent with a healthy agent (S):


Random number between 0 and 1 < INFECTION_RATE (0.05) -> Infection successful

#### Recovery Probability

For each infected agent (I) in each time step:


Random number between 0 and 1 < RECOVERY_RATE (0.02) -> Transition to (R)

#### Immunity Expiration and Reinfection

When an agent in state (R) reaches `days_since_recovery == 30`, the following logic applies:


IF infection_counter >= 2 -> Status = M (Permanently Immune)

ELSE -> Status = S (Susceptible again)