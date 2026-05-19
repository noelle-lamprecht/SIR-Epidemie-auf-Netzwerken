"""
SIR-Epidemie auf Netzwerken basierend auf dem Barabasi-Albert-Modell.

Dieses Skript simuliert zwei SIR-Szenarien und erzeugt saubere Plot-Ausgaben.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Verwende einen nicht-interaktiven Backend für headless Umgebungen
import matplotlib.pyplot as plt


def plot_sir(t, s, i, r, title):
    """Plot the SIR model results over time."""
    plt.figure(figsize=(10, 6))
    plt.axhline(0, color='black', linewidth=1)
    plt.plot(t, s, color='blue', linewidth=2.5, label='S')
    plt.plot(t, i, color='red', linewidth=2.5, label='I')
    plt.plot(t, r, color='grey', linewidth=2.5, label='R')
    plt.title(title)
    plt.xlabel('Zeit')
    plt.ylabel('Anzahl Personen')
    plt.legend()
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.savefig(f'{title.replace(" ", "_")}.png')
    plt.close()


def simulate_sir(N, beta, gamma, mu, tmax, S_start, I_start, R_start):
    """Simulate the SIR model with birth/death rate mu."""
    s = np.zeros(tmax, dtype=float)
    i = np.zeros(tmax, dtype=float)
    r = np.zeros(tmax, dtype=float)

    s[0] = S_start
    i[0] = I_start
    r[0] = R_start

    for k in range(1, tmax):
        s[k] = s[k - 1] - beta / N * s[k - 1] * i[k - 1] + mu * r[k - 1]
        i[k] = i[k - 1] + beta / N * s[k - 1] * i[k - 1] - gamma * i[k - 1]
        r[k] = r[k - 1] + gamma * i[k - 1] - mu * r[k - 1]

        s[k] = max(s[k], 0.0)
        i[k] = max(i[k], 0.0)
        r[k] = max(r[k], 0.0)

    return s, i, r


def main():
    np.random.seed(42)

    N = 1000
    tmax = 500
    t = np.arange(1, tmax + 1)

    # --- Scenario 1: equilibrium-like initial conditions ---
    beta = 0.3
    gamma = 0.3
    mu = 0.3

    S_start = max(0.0, gamma * N / beta - 100.0)
    R_start = max(0.0, N * (1.0 - gamma / beta) / (1.0 + mu / gamma))
    I_start = max(1.0, N - S_start - R_start)

    print(f'Check Summe 1: {S_start + I_start + R_start:.2f}')

    s_t, i_t, r_t = simulate_sir(N, beta, gamma, mu, tmax, S_start, I_start, R_start)
    plot_sir(t, s_t, i_t, r_t, 'Equilibrium Conditions 1')

    # --- Scenario 2: nearly all susceptible, one index case ---
    beta = 0.6
    gamma = 0.1
    mu = 0.3

    S_start = float(N - 1)
    I_start = 1.0
    R_start = 0.0

    print(f'Check Summe 2: {S_start + I_start + R_start:.2f}')

    s_t2, i_t2, r_t2 = simulate_sir(N, beta, gamma, mu, tmax, S_start, I_start, R_start)
    plot_sir(t, s_t2, i_t2, r_t2, 'Equilibrium Conditions 2')

    print('Simulation complete. Die Plots wurden gespeichert.')


if __name__ == '__main__':
    main()


