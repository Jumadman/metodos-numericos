import numpy as np
import matplotlib.pyplot as plt
from metodos_edo import metodo_euler_hasta_cero, medir_tiempo, mostrar_y_limpiar_grafico

# Parámetros físicos del tanque
K = 0.06
Y0 = 3.0
T0 = 0.0
H = 0.5


def f_drenaje(t: float, y: float) -> float:
    """EDO de vaciado de tanque: dy/dt = -k * sqrt(y)"""
    return -K * np.sqrt(max(y, 0.0))


def solucion_exacta_tanque(t: np.ndarray | float) -> np.ndarray | float:
    """Solución analítica: y(t) = (sqrt(y0) - (k/2)*t)^2 para t <= 2*sqrt(y0)/k."""
    raiz = np.sqrt(Y0) - (K / 2.0) * np.asarray(t)
    return np.where(raiz > 0, raiz**2, 0.0)


if __name__ == "__main__":
    # 1. Medición pura de tiempo de ejecución
    tiempo_euler = medir_tiempo(metodo_euler_hasta_cero, f_drenaje, T0, Y0, H)

    # 2. Ejecución paso a paso hasta que y <= 0
    ts, ys_euler = metodo_euler_hasta_cero(f_drenaje, T0, Y0, H, verbose=True)

    # 3. Cálculo de solución exacta y errores
    ys_exacta = solucion_exacta_tanque(ts)
    errores = np.abs(ys_exacta - np.maximum(ys_euler, 0.0))

    t_vaciado_exacto = (2.0 * np.sqrt(Y0)) / K
    t_vaciado_euler_paso = ts[-1]
    t_vaciado_euler_interp = ts[-2] - ys_euler[-2] / f_drenaje(ts[-2], ys_euler[-2])

    # 4. Tabla resumen cada 5 minutos + tramo final de vaciado
    print("\n=== TABLA COMPARATIVA: DRENAJE DE TANQUE (EULER h = 0.5 min vs EXACTA) ===")
    print(f"{'t (min)':<9} | {'y Exacta (m)':<14} | {'y Euler (m)':<14} | {'Error Abs. (m)':<15}")
    print("-" * 60)
    for t, y_ex, y_eu, err in zip(ts, ys_exacta, ys_euler, errores):
        if np.isclose(t % 5.0, 0.0) or t >= 55.0:
            print(f"{t:<9.2f} | {y_ex:<14.6f} | {y_eu:<14.6f} | {err:<15.6f}")

    print("-" * 60)
    print(f"Tiempo de vaciado exacto (analítico)     : {t_vaciado_exacto:.4f} min")
    print(f"Tiempo de vaciado Euler (paso discreto)  : {t_vaciado_euler_paso:.2f} min (Paso {len(ts)-1})")
    print(f"Tiempo de vaciado Euler (interpolado)    : {t_vaciado_euler_interp:.4f} min")
    print(f"Error absoluto en tiempo de vaciado      : {abs(t_vaciado_exacto - t_vaciado_euler_paso):.4f} min")
    print(f"Tiempo de ejecución (cálculo puro)       : {tiempo_euler:.2f} µs")
    print("=" * 60)

    # 5. Gráficos comparativos con limpieza automática
    t_cont = np.linspace(T0, 60.0, 300)
    y_cont = solucion_exacta_tanque(t_cont)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Gráfico 1: Nivel de agua y(t)
    ax1.plot(t_cont, y_cont, "k--", linewidth=1.8, label=f"Solución Exacta (vacía en {t_vaciado_exacto:.2f} min)")
    ax1.plot(
        ts, np.maximum(ys_euler, 0.0), "-", color="#d62728", linewidth=2,
        label=f"Euler h = 0.5 min (vacía en {t_vaciado_euler_paso:.2f} min)"
    )
    ax1.axvline(t_vaciado_euler_paso, color="#d62728", linestyle=":", alpha=0.8)
    ax1.axvline(t_vaciado_exacto, color="k", linestyle=":", alpha=0.8)
    ax1.set_title("Vaciado de Tanque Cilíndrico: $\\frac{dy}{dt} = -0.06\\sqrt{y}$", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Tiempo t (minutos)", fontsize=11)
    ax1.set_ylabel("Profundidad del agua y (m)", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.7)
    ax1.legend()

    # Gráfico 2: Evolución del error absoluto
    ax2.plot(ts, errores, "-", color="#1f77b4", linewidth=2, label="Error Absoluto $|y_{exacta} - y_{Euler}|$")
    ax2.set_title("Error de Subestimación en el Nivel del Agua", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Tiempo t (minutos)", fontsize=11)
    ax2.set_ylabel("Error Absoluto (m)", fontsize=11)
    ax2.grid(True, linestyle=":", alpha=0.7)
    ax2.legend()

    mostrar_y_limpiar_grafico(fig, "comparacion_ej4.png")