import numpy as np
import matplotlib.pyplot as plt
from metodos_edo import (
    metodo_euler,
    metodo_euler_modificado,
    referencia_rk4,
    medir_tiempo,
    mostrar_y_limpiar_grafico,
)

# Condiciones iniciales y parámetros del Ejercicio 1
X0, Y0, XF = 0.0, 1.0, 0.6
H = 0.2
TOL = 0.001


def f_ej1(x: float, y: float) -> float:
    """Ecuación diferencial del Ejercicio 1: y' = x^2 + y^2"""
    return x**2 + y**2


if __name__ == "__main__":
    # 1. Medición pura de tiempo de ejecución (sin I/O de consola)
    tiempo_euler = medir_tiempo(metodo_euler, f_ej1, X0, Y0, XF, H)
    tiempo_mod = medir_tiempo(metodo_euler_modificado, f_ej1, X0, Y0, XF, H, TOL)

    # 2. Ejecución detallada paso a paso
    xe, ye = metodo_euler(f_ej1, X0, Y0, XF, H, verbose=True)
    xm, ym = metodo_euler_modificado(f_ej1, X0, Y0, XF, H, TOL, verbose=True)

    # 3. Curva de referencia con RK4 (h = 0.0001) y cálculo de errores en los nodos
    h_fino = 0.0001
    x_ref, y_ref = referencia_rk4(f_ej1, X0, Y0, XF, h_fino=h_fino)
    indices_nodos = [int(round((x - X0) / h_fino)) for x in xe]
    y_exact_nodos = y_ref[indices_nodos]

    err_euler = np.abs(y_exact_nodos - ye)
    err_mod = np.abs(y_exact_nodos - ym)

    # 4. Tabla resumen por consola
    print("\n=== TABLA COMPARATIVA FINAL (EJERCICIO 1) ===")
    print(f"{'x_i':<6} | {'y_ref':<11} | {'Euler':<11} | {'Err. Euler':<11} | {'Euler Mod.':<11} | {'Err. Mod.':<11}")
    print("-" * 74)
    for x, yr, y_e, ee, y_m, em in zip(xe, y_exact_nodos, ye, err_euler, ym, err_mod):
        print(f"{x:<6.2f} | {yr:<11.6f} | {y_e:<11.6f} | {ee:<11.6f} | {y_m:<11.6f} | {em:<11.6f}")
    print("-" * 74)
    print(f"{'Tiempo de ejecución (cálculo puro):':<34} | {tiempo_euler:>8.2f} µs | {'':<11} | {tiempo_mod:>8.2f} µs")
    print("=" * 74)

    # 5. Gráficos comparativos con limpieza automática al cerrar
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot(x_ref, y_ref, "k--", linewidth=1.8, label="Solución de referencia (RK4)")
    ax1.plot(xe, ye, "o-", color="#d62728", linewidth=2, markersize=7, label=f"Euler Simple ({tiempo_euler:.1f} µs)")
    ax1.plot(xm, ym, "s-", color="#1f77b4", linewidth=2, markersize=7, label=f"Euler Modificado ({tiempo_mod:.1f} µs)")
    ax1.set_title("Comparación de Aproximaciones: $y' = x^2 + y^2$", fontsize=12, fontweight="bold")
    ax1.set_xlabel("x", fontsize=11)
    ax1.set_ylabel("y(x)", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.7)
    ax1.legend()

    ancho = 0.055
    ax2.bar(xe - ancho / 2, err_euler, width=ancho, color="#d62728", alpha=0.85, label="Error Euler Simple")
    ax2.bar(xe + ancho / 2, err_mod, width=ancho, color="#1f77b4", alpha=0.85, label="Error Euler Modificado")
    ax2.set_title("Error Absoluto $|y_{ref} - y_{aprox}|$ por Nodo", fontsize=12, fontweight="bold")
    ax2.set_xlabel("x", fontsize=11)
    ax2.set_ylabel("Error Absoluto", fontsize=11)
    ax2.set_xticks(xe)
    ax2.grid(True, axis="y", linestyle=":", alpha=0.7)
    ax2.legend()

    mostrar_y_limpiar_grafico(fig, "comparacion_ej1.png")