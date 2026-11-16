import numpy as np
import matplotlib.pyplot as plt
from metodos_edo import metodo_euler, medir_tiempo, mostrar_y_limpiar_grafico

# Parámetros del modelo logístico
GAMMA = 3.0
TAU = 0.1
P0 = 5.0
T0, TF = 0.0, 2.0


def f_poblacion(t: float, P: float) -> float:
    """EDO logística: P'(t) = gamma * P(t) - tau * P(t)^2"""
    return GAMMA * P - TAU * (P**2)


def solucion_exacta(t: np.ndarray | float) -> np.ndarray | float:
    """Solución analítica dada en el enunciado."""
    return GAMMA / (TAU + ((GAMMA / P0) - TAU) * np.exp(-GAMMA * t))


if __name__ == "__main__":
    # 1. Medición de tiempos puros
    t_h05 = medir_tiempo(metodo_euler, f_poblacion, T0, P0, TF, 0.5)
    t_h025 = medir_tiempo(metodo_euler, f_poblacion, T0, P0, TF, 0.25)

    # 2. Ejecución paso a paso reutilizando metodo_euler
    ts_05, Ps_05 = metodo_euler(f_poblacion, T0, P0, TF, 0.5, verbose=True, var_x="t", var_y="P")
    ts_025, Ps_025 = metodo_euler(f_poblacion, T0, P0, TF, 0.25, verbose=True, var_x="t", var_y="P")

    # 3. Evaluación exacta en los nodos y cálculo de errores
    P_ex_05 = solucion_exacta(ts_05)
    err_05 = np.abs(P_ex_05 - Ps_05)

    P_ex_025 = solucion_exacta(ts_025)
    err_025 = np.abs(P_ex_025 - Ps_025)

    # 4. Tabla comparativa unificada en la malla más fina (h = 0.25)
    print("\n=== TABLA COMPARATIVA: EULER (h=0.5 vs h=0.25) FRENTE A SOLUCIÓN EXACTA ===")
    print(f"{'t_i':<6} | {'P Exacta':<11} | {'Euler h=0.5':<12} | {'Err (h=0.5)':<12} | {'Euler h=0.25':<13} | {'Err (h=0.25)':<12}")
    print("-" * 80)

    dict_05 = dict(zip(ts_05, zip(Ps_05, err_05)))
    for t, p_ex, p_25, e_25 in zip(ts_025, P_ex_025, Ps_025, err_025):
        if t in dict_05:
            p_5, e_5 = dict_05[t]
            col_05 = f"{p_5:<12.6f} | {e_5:<12.6f}"
        else:
            col_05 = f"{'---':<12} | {'---':<12}"
        print(f"{t:<6.2f} | {p_ex:<11.6f} | {col_05} | {p_25:<13.6f} | {e_25:<12.6f}")

    print("-" * 80)
    print(f"{'Tiempo de ejecución (cálculo puro):':<34} | {t_h05:>8.2f} µs | {'':<12} | {t_h025:>9.2f} µs")
    print("=" * 80)

    # 5. Gráficos comparativos con limpieza automática
    t_continuo = np.linspace(T0, TF, 200)
    P_continuo = solucion_exacta(t_continuo)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Curvas de población P(t)
    ax1.plot(t_continuo, P_continuo, "k--", linewidth=1.8, label="Solución Exacta")
    ax1.plot(ts_05, Ps_05, "o-", color="#d62728", linewidth=2, markersize=7, label=f"Euler h = 0.5 ({t_h05:.1f} µs)")
    ax1.plot(ts_025, Ps_025, "s-", color="#1f77b4", linewidth=2, markersize=6, label=f"Euler h = 0.25 ({t_h025:.1f} µs)")
    ax1.axhline(GAMMA / TAU, color="gray", linestyle=":", linewidth=1.2, label="Capacidad de carga (γ/τ = 30)")
    ax1.set_title("Crecimiento Logístico: $P'(t) = 3P - 0.1P^2$", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Tiempo t", fontsize=11)
    ax1.set_ylabel("Población P(t)", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.7)
    ax1.legend()

    # Error absoluto por nodo
    ax2.plot(ts_05, err_05, "o--", color="#d62728", linewidth=1.8, markersize=7, label="Error Absoluto (h = 0.5)")
    ax2.plot(ts_025, err_025, "s-", color="#1f77b4", linewidth=1.8, markersize=6, label="Error Absoluto (h = 0.25)")
    ax2.set_title("Evolución del Error Absoluto $|P_{exacta} - P_{Euler}|$", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Tiempo t", fontsize=11)
    ax2.set_ylabel("Error Absoluto", fontsize=11)
    ax2.set_xticks(ts_025)
    ax2.grid(True, linestyle=":", alpha=0.7)
    ax2.legend()

    mostrar_y_limpiar_grafico(fig, "comparacion_ej2.png")