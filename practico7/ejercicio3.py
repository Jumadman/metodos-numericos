import numpy as np
import matplotlib.pyplot as plt
from ejercicio1 import f_ej1, X0, Y0, XF, H
from metodos_edo import (
    metodo_rk2,
    metodo_rk4,
    referencia_rk4,
    medir_tiempo,
    mostrar_y_limpiar_grafico,
)

if __name__ == "__main__":
    # 1. Medición pura de tiempos de ejecución
    t_rk2 = medir_tiempo(metodo_rk2, f_ej1, X0, Y0, XF, H)
    t_rk4 = medir_tiempo(metodo_rk4, f_ej1, X0, Y0, XF, H)

    # 2. Ejecución detallada paso a paso (3.a y 3.b)
    x_rk2, y_rk2 = metodo_rk2(f_ej1, X0, Y0, XF, H, verbose=True)
    x_rk4, y_rk4 = metodo_rk4(f_ej1, X0, Y0, XF, H, verbose=True)

    # 3. Referencia de alta precisión y errores absolutos
    h_fino = 0.0001
    x_ref, y_ref = referencia_rk4(f_ej1, X0, Y0, XF, h_fino=h_fino)
    indices_nodos = [int(round((x - X0) / h_fino)) for x in x_rk2]
    y_exact_nodos = y_ref[indices_nodos]

    err_rk2 = np.abs(y_exact_nodos - y_rk2)
    err_rk4 = np.abs(y_exact_nodos - y_rk4)

    # 4. Tabla comparativa (3.a RK2 vs 3.b RK4)
    print("\n=== TABLA COMPARATIVA FINAL: RK2 (3.a) vs RK4 (3.b) ===")
    print(
        f"{'x_i':<6} | {'y_ref':<11} | {'RK2 (3.a)':<11} | {'Err. RK2':<11} | "
        f"{'RK4 (3.b)':<11} | {'Err. RK4':<11}"
    )
    print("-" * 74)
    for x, yr, y2, e2, y4, e4 in zip(x_rk2, y_exact_nodos, y_rk2, err_rk2, y_rk4, err_rk4):
        print(f"{x:<6.2f} | {yr:<11.6f} | {y2:<11.6f} | {e2:<11.6f} | {y4:<11.6f} | {e4:<11.6f}")
    print("-" * 74)
    print(f"{'Tiempo de ejecución (cálculo puro):':<34} | {t_rk2:>8.2f} µs | {'':<11} | {t_rk4:>8.2f} µs")
    print("=" * 74)

    # 5. Gráficos comparativos con limpieza automática al cerrar
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Curvas de aproximación
    ax1.plot(x_ref, y_ref, "k--", linewidth=1.8, label="Solución de referencia (exacta)")
    ax1.plot(x_rk2, y_rk2, "o-", color="#2ca02c", linewidth=2, markersize=7, label=f"RK2 - 3.a ({t_rk2:.1f} µs)")
    ax1.plot(x_rk4, y_rk4, "^-", color="#9467bd", linewidth=2, markersize=7, label=f"RK4 - 3.b ({t_rk4:.1f} µs)")
    ax1.set_title("Comparación RK2 vs RK4: $y' = x^2 + y^2$", fontsize=12, fontweight="bold")
    ax1.set_xlabel("x", fontsize=11)
    ax1.set_ylabel("y(x)", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.7)
    ax1.legend()

    # Barras de error absoluto
    ancho = 0.055
    ax2.bar(x_rk2 - ancho / 2, err_rk2, width=ancho, color="#2ca02c", alpha=0.85, label="Error RK2 (3.a)")
    ax2.bar(x_rk2 + ancho / 2, err_rk4, width=ancho, color="#9467bd", alpha=0.85, label="Error RK4 (3.b)")
    ax2.set_title("Error Absoluto $|y_{ref} - y_{aprox}|$ por Nodo", fontsize=12, fontweight="bold")
    ax2.set_xlabel("x", fontsize=11)
    ax2.set_ylabel("Error Absoluto", fontsize=11)
    ax2.set_xticks(x_rk2)
    ax2.grid(True, axis="y", linestyle=":", alpha=0.7)
    ax2.legend()

    mostrar_y_limpiar_grafico(fig, "comparacion_ej3.png")