# SIR Epidemics on Networks  
#Made with Copilot
This repository contains Python simulations of epidemic dynamics on networks using SIRS and SIRS models with seasonal effects, demographics, and Barabási-Albert network structure.

## Requirements

- Python 3.14 or newer
- numpy
- matplotlib
- pandas
- networkx

Install dependencies with:

```bash
python -m pip install numpy matplotlib pandas networkx
```

## Usage

Run one of the simulation scripts from the repository root:

- `1.SIR.py` — basic agent-based SIR(S) model with random contacts
- `2.BarabasiSIR.py` — SIR(S) model on a Barabási-Albert network
- `3.BarabasiSIRDB.py` — SIR(S) model with demographics and long-term immunity
- `4.Cold Warm + Immune.py` — seasonal SIRS model with demographics and permanent immunity after repeat infections
- `5.Cold Warm.py` — seasonal SIRS model on a Barabási-Albert network

Example:

```bash
python "5.Cold Warm.py"
```

If your file name contains spaces, wrap it in quotes.

## What happens when you run a script

- The simulation runs for a fixed number of days
- Daily infection and recovery events are computed using random draws
- A network structure is built using the Barabási-Albert model where applicable
- The code prints daily or periodic counts of Susceptible, Infected, and Recovered individuals
- A plot or animation window opens showing the epidemic dynamics over time

## Notes

- `4.Cold Warm + Immune.py` and `5.Cold Warm.py` use season-dependent infection and recovery rates
- `4.Cold Warm + Immune.py` also includes birth/death dynamics and permanent immunity after repeated infection
- Adjust configuration constants in each file to change population size, infection rates, immunity duration, and simulation length
