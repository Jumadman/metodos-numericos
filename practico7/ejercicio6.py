import numpy as np
import matplotlib.pyplot as plt
from metodos_edo import (
    metodo_euler_modificado,
    metodo_milne,
    medir_tiempo,
    mostrar_y_limpiar_grafico,
)

# Condiciones iniciales y parámetros del Ejercicio 6
X0, Y0 = 0.0, 1.0
H = 0.05
XF_INICIAL = 0.15  # 4 puntos iniciales: 0.00, 0.05, 0.10, 0.15
XF_FINAL = 0.30    # Completa el intervalo (0; 0.3) pasando por 0.20 y 0.25
TOL = 1e-7         # Tolerancia estricta para un arranque preciso de Milne


def f_ej6(x: float, y: float) -> float:
    """EDO lineal del Ejercicio 6: y' = 3x + 3y"""
    return 3.0 * x + 3.0 * y


def solucion_exacta_ej6(x: np.ndarray | float) -> np.ndarray | float:
    """Solución exacta dada en el enunciado: y = (4/3)*e^(3x) - x - 1/3"""
    return (4.0 / 3.0) * np.exp(3.0 * np.asarray(x)) - np.asarray(x) - (1.0 / 3.0)


if __name__ == "__main__":
    # 1. Medición pura de tiempos de ejecución de cada etapa
    t_euler_mod = medir_tiempo(metodo_euler_modificado, f_ej6, X0, Y0, XF_INICIAL, H, TOL)

    # 2. Etapa 6.a: Hallar los 4 valores iniciales [0.00, 0.05, 0.10, 0.15] con Euler Modificado
    x_init, y_init = metodo_euler_modificado(f_ej6, X0, Y0, XF_INICIAL, H, TOL, verbose=True)

    # Medición pura del tramo de Milne (x = 0.20, 0.25, 0.30)
    t_milne = medir_tiempo(metodo_milne, f_ej6, x_init, y_init, XF_FINAL, H)

    # 3. Etapa 6.b: Aplicar Milne hasta x = 0.30 (incluyendo x = 0.20 y x = 0.25)
    xs_total, ys_total, yps_total = metodo_milne(f_ej6, x_init, y_init, XF_FINAL, H, verbose=True)

    # 4. Etapa 6.c: Evaluación exacta y cálculo de errores absolutos y relativos
    ys_exacta = solucion_exacta_ej6(xs_total)
    err_abs = np.abs(ys_exacta - ys_total)
    err_rel_pct = (err_abs / ys_exacta) * 100.0

    # 5. Tabla comparativa completa por consola
    print("\n=== TABLA COMPARATIVA FINAL: EJERCICIO 6 (INTERVALO [0; 0.3]) ===")
    print(
        f"{'i':<3} | {'x_i':<6} | {'y Exacta':<11} | {'y Numérica':<11} | "
        f"{'Err. Abs.':<11} | {'Err. Rel.%':<10} | {'Método aplicado':<20}"
    )
    print("-" * 88)
    for i, (x, y_ex, y_num, ea, er) in enumerate(zip(xs_total, ys_exacta, ys_total, err_abs, err_rel_pct)):
        metodo = "Condición inicial" if i == 0 else ("Euler Mod. (6.a)" if i < 4 else "Milne (6.b)")
        print(
            f"{i:<3} | {x:<6.2f} | {y_ex:<11.6f} | {y_num:<11.6f} | "
            f"{ea:<11.6f} | {er:<9.4f}% | {metodo:<20}"
        )
    print("-" * 88)
    print(f"Tiempo Euler Modificado (arranque 6.a) : {t_euler_mod:.2f} µs")
    print(f"Tiempo Método de Milne  (continuación) : {t_milne:.2f} µs")
    print(f"Tiempo total combinado                 : {t_euler_mod + t_milne:.2f} µs")
    print("=" * 88)

    # 6. Gráficos comparativos con limpieza automática al cerrar
    x_cont = np.linspace(X0, XF_FINAL, 200)
    y_cont = solucion_exacta_ej6(x_cont)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Gráfico 1: Trayectoria exacta vs aproximación híbrida (Euler Modificado + Milne)
    ax1.plot(x_cont, y_cont, "k--", linewidth=1.8, label="Solución Exacta: $\\frac{4}{3}e^{3x} - x - \\frac{1}{3}$")
    ax1.plot(
        xs_total[:4], ys_total[:4], "s-", color="#1f77b4", linewidth=2, markersize=7,
        label=f"6.a) Euler Modificado ({t_euler_mod:.1f} µs)"
    )
    ax1.plot(
        xs_total[3:], ys_total[3:], "D-", color="#ff7f0e", linewidth=2.2, markersize=7,
        label=f"6.b) Método de Milne ({t_milne:.1f} µs)"
    )
    ax1.set_title("Solución Híbrida (Euler Modificado + Milne): $y' = 3x + 3y$", fontsize=11, fontweight="bold")
    ax1.set_xlabel("x", fontsize=11)
    ax1.set_ylabel("y(x)", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.7)
    ax1.legend()

    # Gráfico 2: Error absoluto en cada paso de integración
    colores = ["#7f7f7f"] + ["#1f77b4"] * 3 + ["#ff7f0e"] * 3
    ax2.bar(xs_total, err_abs, width=0.028, color=colores, alpha=0.88)
    ax2.set_title("6.c) Error Absoluto $|y_{exacta} - y_{num}|$ por Paso", fontsize=11, fontweight="bold")
    ax2.set_xlabel("x", fontsize=11)
    ax2.set_ylabel("Error Absoluto", fontsize=11)
    ax2.set_xticks(xs_total)
    ax2.grid(True, axis="y", linestyle=":", alpha=0.7)

    # Leyenda manual para diferenciar barras de arranque vs Milne
    from matplotlib.patches import Patch
    ax2.legend(handles=[
        Patch(facecolor="#1f77b4", alpha=0.88, label="Tramo 6.a: Euler Modificado"),
        Patch(facecolor="#ff7f0e", alpha=0.88, label="Tramo 6.b: Método de Milne"),
    ])

    mostrar_y_limpiar_grafico(fig, "comparacion_ej6.png")