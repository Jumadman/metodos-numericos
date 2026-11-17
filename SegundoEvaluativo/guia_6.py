"""
Módulo: guia_5.py
Descripción: Contiene los modelos matemáticos y la resolución guiada e interactiva
             de los Ejercicios 1, 2, 3 y 4 de la Guía de Laboratorio N° 5 (2026).
"""

"""
Script: ejercicio_2_guia_6.py
Descripción: Resolución analítica y computacional del Ejercicio 2 de la
             Guía de Laboratorio N° 6 comparando todas las combinaciones posibles.
"""

from SegundoEvaluativo.metodos_integracion import (
    trapecios_compuesto,
    combinacion_simpson_1_3_y_trapecio,
    combinacion_simpson_1_3_y_3_8
)


def resolver_ejercicio_2():
    # Datos de la tabla del Ejercicio 2 (Guía N° 6)
    t = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    y = [0.0, 0.15, 0.30, 0.55, 0.73, 0.81]

    n = len(t) - 1
    h = t[1] - t[0]

    print("=" * 95)
    print("EJERCICIO 2 - GUÍA DE LABORATORIO N° 6: INTEGRACIÓN NUMÉRICA")
    print(f"Intervalo total: t in [{t[0]}, {t[-1]}] | Paso h = {h:.2f} | Cantidad de subintervalos: n = {n}")
    print("=" * 95)
    print("Tabla de datos:")
    print("  t : " + "  ".join(f"{ti:6.2f}" for ti in t))
    print("  y : " + "  ".join(f"{yi:6.2f}" for yi in y))
    print("-" * 95)

    # 1. Regla de los Trapecios Compuesta (5 subintervalos)
    res_trap = trapecios_compuesto(t, y)

    # 2. Combinación Simpson 1/3 (4 intervalos) + Trapecio en el último intervalo
    res_simp_trap_fin = combinacion_simpson_1_3_y_trapecio(t, y, posicion_trapecio='final')

    # 3. Combinación Trapecio en el primer intervalo + Simpson 1/3 (4 intervalos)
    res_simp_trap_ini = combinacion_simpson_1_3_y_trapecio(t, y, posicion_trapecio='inicio')

    # 4. Combinación Óptima: Simpson 1/3 (2 intervalos) + Simpson 3/8 (3 intervalos al final)
    res_optima_fin = combinacion_simpson_1_3_y_3_8(t, y, posicion_3_8='final')

    # 5. Combinación Óptima: Simpson 3/8 (3 intervalos al inicio) + Simpson 1/3 (2 intervalos)
    res_optima_ini = combinacion_simpson_1_3_y_3_8(t, y, posicion_3_8='inicio')

    # Cuadro comparativo
    print(f"{'Esquema / Combinación Aplicada':<48} | {'Fórmula Empleada':<28} | {'Valor Integral':<14}")
    print("-" * 95)
    print(f"{res_trap['metodo']:<48} | {'Trapecios Puro (n=5)':<28} | {res_trap['integral']:<14.6f}")
    print(f"{res_simp_trap_fin['metodo']:<48} | {'Simpson 1/3 (4) + Trap (1)':<28} | {res_simp_trap_fin['integral_total']:<14.6f}")
    print(f"{res_simp_trap_ini['metodo']:<48} | {'Trap (1) + Simpson 1/3 (4)':<28} | {res_simp_trap_ini['integral_total']:<14.6f}")
    print(f"{res_optima_fin['metodo']:<48} | {'Simpson 1/3 (2) + 3/8 (3)':<28} | {res_optima_fin['integral_total']:<14.6f}")
    print(f"{res_optima_ini['metodo']:<48} | {'Simpson 3/8 (3) + 1/3 (2)':<28} | {res_optima_ini['integral_total']:<14.6f}")
    print("=" * 95)

    print("\nANÁLISIS TEÓRICO DE RESULTADOS:")
    print("1. n = 5 es impar; por definición, la regla de Simpson 1/3 compuesta no puede cubrir toda la tabla.")
    print("2. Al combinar Simpson 1/3 con Trapecios, el error global queda limitado por Trapecios (O(h^2)).")
    print("3. La combinación más precisa es Simpson 1/3 + Simpson 3/8: ambas fórmulas aproximan mediante")
    print("   polinomios de grado 2 y 3 respectivamente y comparten orden de error local O(h^5) y global O(h^4).")
    print(f"-> Resultado óptimo recomendado: Integral ≈ {res_optima_fin['integral_total']:.6f}")


if __name__ == '__main__':
    resolver_ejercicio_2()