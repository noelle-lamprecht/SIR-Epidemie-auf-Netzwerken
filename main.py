"""
SIR Epidemic Model Simulation on Networks

This script simulates the SIR (Susceptible-Infected-Recovered) model with birth/death rates,
which makes it effectively a SIRD (Susceptible-Infected-Recovered-Dead) model.

The model includes:
- S: Susceptible individuals
- I: Infected individuals
- R: Recovered/Removed individuals (includes deaths due to disease)

Parameters:
- beta: Infection rate
- gamma: Recovery rate
- mu: Birth/death rate (natural mortality)
"""

def main():
    print("Hello from sir-epidemie-auf-netzwerken! help help")


if __name__ == "__main__":
    main()

# /// script
# dependencies = [
#   "numpy",
#   "matplotlib",
#   "pandas",
# ]
# ///

# Import required libraries
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import pandas as pd

def plot_sir(t, s, i, r, title):
    """
    Plot the SIR model results over time.

    Parameters:
    t: Time array
    s: Susceptible population over time
    i: Infected population over time
    r: Recovered/removed population over time
    title: Plot title
    """
    plt.figure(figsize=(10, 6))
    plt.axhline(0, color='black', linewidth=1)  # Add horizontal line at y=0
    plt.plot(t, s, color='blue', linewidth=2.5, label='S')      # Susceptible
    plt.plot(t, i, color='red', linewidth=2.5, label='I')       # Infected
    plt.plot(t, r, color='grey', linewidth=2.5, label='R')      # Recovered/Removed
    plt.ylim(0, 1000)  # Set y-axis limits
    plt.title(title)
    plt.xlabel("Zeit")          # Time
    plt.ylabel("Anzahl Personen")  # Number of people
    plt.legend()
    # "theme_classic" Look - hide top and right spines
    plt.gca().spines[['top', 'right']].set_visible(False)
    # Save plot instead of showing (for headless environments)
    plt.savefig(f"{title.replace(' ', '_')}.png")
    plt.close()

# --- Equilibrium Conditions 1 ---
# First simulation scenario with equilibrium initial conditions

# Model parameters
N = 1000      # Total population
tmax = 500    # Maximum time steps
t = np.arange(1, tmax + 1)  # Time array from 1 to tmax

# Epidemiological parameters
beta = 0.3    # Infection rate (probability of infection per contact)
gamma = 0.3   # Recovery rate (1/gamma = average recovery time)
mu = 0.3      # Birth/death rate (natural mortality rate)

# Initial values based on equilibrium formulas
# These formulas give initial conditions that would maintain equilibrium
S_start = (gamma * N / beta) - 100  # Susceptible at start
R_start = N * (1 - gamma / beta) / (1 + mu / gamma)  # Recovered at start
I_start = N - R_start - S_start    # Infected at start (population conservation)

print(f"Check Summe 1: {S_start + I_start + R_start}")  # Verify population conservation

# Initialize arrays for simulation
s_t = np.zeros(tmax); s_t[0] = S_start
i_t = np.zeros(tmax); i_t[0] = I_start
r_t = np.zeros(tmax); r_t[0] = R_start

# Main simulation loop
for k in range(1, tmax):
    # SIR model differential equations (discrete time approximation)
    s_t[k] = s_t[k-1] - beta/N * s_t[k-1] * i_t[k-1] + mu * r_t[k-1]  # Susceptible change
    i_t[k] = i_t[k-1] + beta/N * s_t[k-1] * i_t[k-1] - gamma * i_t[k-1]  # Infected change
    r_t[k] = r_t[k-1] + gamma * i_t[k-1] - mu * r_t[k-1]  # Recovered change

# Plot the first simulation
plot_sir(t, s_t, i_t, r_t, "Equilibrium Conditions 1")

# --- Equilibrium Conditions 2 ---
# Second simulation scenario with different parameters

# Different epidemiological parameters
beta = 0.6    # Higher infection rate
gamma = 0.1   # Lower recovery rate (longer infections)
mu = 0.3      # Same birth/death rate

# Different initial conditions (almost all susceptible, no recovered)
S_start = N   # All population susceptible
R_start = 0   # No recovered initially
I_start = N - R_start - S_start  # No infected initially (this will be 0)

print(f"Check Summe 2: {S_start + I_start + R_start}")  # Verify population conservation

# Initialize arrays for second simulation
s_t2 = np.zeros(tmax); s_t2[0] = S_start
i_t2 = np.zeros(tmax); i_t2[0] = I_start
r_t2 = np.zeros(tmax); r_t2[0] = R_start

# Main simulation loop for second scenario
for k in range(1, tmax):
    # Same SIR equations with new parameters
    s_t2[k] = s_t2[k-1] - beta/N * s_t2[k-1] * i_t2[k-1] + mu * r_t2[k-1]
    i_t2[k] = i_t2[k-1] + beta/N * s_t2[k-1] * i_t2[k-1] - gamma * i_t2[k-1]
    r_t2[k] = r_t2[k-1] + gamma * i_t2[k-1] - mu * r_t2[k-1]

# Plot the second simulation
plot_sir(t, s_t2, i_t2, r_t2, "Equilibrium Conditions 2")