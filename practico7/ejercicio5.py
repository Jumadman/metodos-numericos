import numpy as np
import matplotlib.pyplot as plt
from ejercicio1 import f_ej1, X0, Y0, XF, H
from metodos_edo import (
    metodo_rk2,
    metodo_milne,
    referencia_rk4,
    medir_tiempo,
    mostrar_y_limpiar_grafico,
)

XF_MILNE = 1.0

if __name__ == "__main__":
    # 1. Obtener los 4 puntos iniciales usando RK2 (resultado del ítem 3.a)
    x_init, y_init = metodo_rk2(f_ej1, X0, Y0, XF, H, verbose=False)

    # 2. Medir tiempo puro de Milne y ejecutar paso a paso hasta x = 1.0
    tiempo_milne = medir_tiempo(metodo_milne, f_ej1, x_init, y_init, XF_MILNE, H)
    xs_total, ys_total, yps_total = metodo_milne(f_ej1, x_init, y_init, XF_MILNE, H, verbose=True)

    # 3. Referencia continua hasta antes de la asíntota (x ≈ 0.969)
    h_fino = 0.0001
    x_ref, y_ref = referencia_rk4(f_ej1, X0, Y0, 0.96, h_fino=h_fino)

    # 4. Tabla completa del Ejercicio 5 (x, y, y')
    print("\n=== TABLA COMPLETA EJERCICIO 5 ===")
    print(f"{'i':<4} | {'x_i':<6} | {'y_i':<12} | {'y\'_i = f(x,y)':<14} | {'Método':<18}")
    print("-" * 66)
    for i, (x, y, yp) in enumerate(zip(xs_total, ys_total, yps_total)):
        metodo = "Runge-Kutta 2°" if i < 4 else "Milne"
        print(f"{i:<4} | {x:<6.2f} | {y:<12.6f} | {yp:<14.6f} | {metodo:<18}")
    print("-" * 66)
    print(f"Tiempo de ejecución Milne (cálculo puro): {tiempo_milne:.2f} µs")
    print("=" * 66)

    # 5. Gráfico comparativo con limpieza automática
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_ref, y_ref, "k--", linewidth=1.8, label="Solución exacta (asíntota en x ≈ 0.969)")
    ax.plot(xs_total[:4], ys_total[:4], "o-", color="#2ca02c", linewidth=2, markersize=7, label="Runge-Kutta 2°")
    ax.plot(
        xs_total[3:], ys_total[3:], "D-", color="#ff7f0e", linewidth=2.2, markersize=7,
        label=f"Milne ({tiempo_milne:.1f} µs)"
    )
    ax.axvline(0.969, color="red", linestyle=":", alpha=0.7, label="Asíntota vertical exacta (x ≈ 0.969)")
    ax.set_ylim(0, 30)
    ax.set_title("Ejercicio 5: Continuación con Método de Milne ($y' = x^2 + y^2$)", fontsize=11, fontweight="bold")
    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel("y(x)", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.legend()

    mostrar_y_limpiar_grafico(fig, "comparacion_ej5.png")