"""
Módulo: guia_2.py
Descripción: Resolución interactiva de los Ejercicios 1 al 5 de la Guía de
             Laboratorio N° 2 (Aproximaciones Numéricas y Errores).
"""

import math
from aritmetica_flotante import (
    normalizar_k_digitos,
    operar_flotante,
    error_absoluto,
    error_relativo
)


def resolver_ejercicio_1():
    """Ejercicio 1: Cálculo de errores absoluto y relativo en aproximaciones clásicas."""
    print("\n" + "=" * 90)
    print("EJERCICIO 1: CÁLCULO DE ERROR ABSOLUTO Y RELATIVO (p vs p*)")
    print("=" * 90)

    # Nota en f: en el PDF figura p = 8, pero el valor p* = 39900 corresponde al factorial 8! = 40320
    casos = [
        ("a", "π", math.pi, "22/7", 22.0 / 7.0),
        ("b", "π", math.pi, "3.1416", 3.1416),
        ("c", "e", math.e, "2.718", 2.718),
        ("d", "√2", math.sqrt(2.0), "1.414", 1.414),
        ("e", "e^10", math.exp(10.0), "22000", 22000.0),
        ("f", "8! (40320)", float(math.factorial(8)), "39900", 39900.0)
    ]

    print(f"{'Ítem':<6} | {'Valor Exacto (p)':<18} | {'Aprox (p*)':<14} | {'Error Absoluto':<16} | {'Error Relativo':<16}")
    print("-" * 90)

    for item, nom_p, p_val, nom_aprox, aprox_val in casos:
        e_abs = error_absoluto(p_val, aprox_val)
        e_rel = error_relativo(p_val, aprox_val)
        print(f"({item})   | {nom_p:<8} = {p_val:<7.5f} | {nom_aprox:<14} | {e_abs:<16.4e} | {e_rel:<16.4e}")

    print("=" * 90)
    input("\nPresione Enter para continuar...")


def resolver_ejercicios_2_y_3():
    """Ejercicios 2 y 3: Aritmética normalizada a 3 dígitos (Redondeo vs Truncamiento)."""
    print("\n" + "=" * 105)
    print("EJERCICIOS 2 Y 3: ARITMÉTICA CON NORMALIZACIÓN A 3 DÍGITOS (REDONDEO VS TRUNCAMIENTO)")
    print("=" * 105)

    def calcular_expresion(expr_id, modo):
        if expr_id == 'a':  # 133 + 0.921
            return operar_flotante(133.0, 0.921, '+', 3, modo)
        elif expr_id == 'b':  # 133 - 0.499
            return operar_flotante(133.0, 0.499, '-', 3, modo)
        elif expr_id == 'c':  # (121 - 119) - 0.327
            paso1 = operar_flotante(121.0, 119.0, '-', 3, modo)
            return operar_flotante(paso1, 0.327, '-', 3, modo)
        elif expr_id == 'd':  # (121 - 0.327) - 119
            paso1 = operar_flotante(121.0, 0.327, '-', 3, modo)
            return operar_flotante(paso1, 119.0, '-', 3, modo)
        elif expr_id == 'e':  # (2/9) * (9/7)
            paso1 = operar_flotante(2.0, 9.0, '/', 3, modo)
            paso2 = operar_flotante(9.0, 7.0, '/', 3, modo)
            return operar_flotante(paso1, paso2, '*', 3, modo)

    operaciones = [
        ('a', "133 + 0.921", 133.0 + 0.921),
        ('b', "133 - 0.499", 133.0 - 0.499),
        ('c', "(121 - 119) - 0.327", (121.0 - 119.0) - 0.327),
        ('d', "(121 - 0.327) - 119", (121.0 - 0.327) - 119.0),
        ('e', "(2/9) * (9/7)", (2.0 / 9.0) * (9.0 / 7.0))
    ]

    print(f"{'Ítem':<4} | {'Operación':<20} | {'Exacto (5 dec)':<15} | {'Redondeo 3d':<12} | {'Err Rel (Red)':<14} | {'Truncado 3d':<12} | {'Err Rel (Trun)':<14}")
    print("-" * 105)

    for item, desc, val_ex in operaciones:
        res_red = calcular_expresion(item, 'redondeo')
        err_rel_red = error_relativo(val_ex, res_red)

        res_trun = calcular_expresion(item, 'truncamiento')
        err_rel_trun = error_relativo(val_ex, res_trun)

        print(f"({item}) | {desc:<20} | {val_ex:<15.5f} | {res_red:<12.4g} | {err_rel_red:<14.4e} | {res_trun:<12.4g} | {err_rel_trun:<14.4e}")

    print("=" * 105)
    print("OBSERVACIÓN TEÓRICA CLAVE (Ítems c y d):")
    print("• En aritmética exacta: (121 - 119) - 0.327 == (121 - 0.327) - 119 = 1.673.")
    print("• En máquina de 3 dígitos: el ítem (d) sufre pérdida de dígitos significativos")
    print("  al restar números casi iguales en punto flotante, alterando la propiedad asociativa.")
    input("\nPresione Enter para continuar...")


def resolver_ejercicio_4():
    """Ejercicio 4: Cancelación sustractiva en ecuaciones cuadráticas y fórmula racionalizada."""
    print("\n" + "=" * 95)
    print("EJERCICIO 4: CANCELACIÓN CATASTRÓFICA EN ECUACIÓN CUADRÁTICA")
    print("Ecuación: x² + 62.10x + 1 = 0  (a = 1, b = 62.10, c = 1)")
    print("=" * 95)

    a, b, c = 1.0, 62.10, 1.0
    # Valores de referencia de alta precisión dados por la cátedra
    x1_exacto = -0.01610723
    x2_exacto = -62.08390

    # 4.a Fórmula clásica con redondeo a 4 dígitos normalizados
    # x1 = (-b + sqrt(b^2 - 4ac)) / (2a)
    b_cuad = normalizar_k_digitos(b ** 2, 4, 'redondeo')               # 62.10^2 = 3856.41 -> 3856
    cuatro_ac = normalizar_k_digitos(4.0 * a * c, 4, 'redondeo')       # 4.000
    discrim = normalizar_k_digitos(b_cuad - cuatro_ac, 4, 'redondeo')  # 3856 - 4 = 3852
    raiz_disc = normalizar_k_digitos(math.sqrt(discrim), 4, 'redondeo') # sqrt(3852) = 62.064... -> 62.06

    # Aquí ocurre la cancelación catastrófica: -62.10 + 62.06
    num_x1_clasico = normalizar_k_digitos(-b + raiz_disc, 4, 'redondeo')  # -0.04000
    x1_clasico = normalizar_k_digitos(num_x1_clasico / (2.0 * a), 4, 'redondeo') # -0.02000

    num_x2_clasico = normalizar_k_digitos(-b - raiz_disc, 4, 'redondeo')  # -124.2
    x2_clasico = normalizar_k_digitos(num_x2_clasico / (2.0 * a), 4, 'redondeo') # -62.10

    # 4.b Fórmula racionalizada para evitar cancelación sustractiva
    # x1 = -2c / (b + sqrt(b^2 - 4ac))
    den_x1_rac = normalizar_k_digitos(b + raiz_disc, 4, 'redondeo')       # 62.10 + 62.06 = 124.2
    x1_racionalizado = normalizar_k_digitos((-2.0 * c) / den_x1_rac, 4, 'redondeo') # -2 / 124.2 = -0.01610

    # x2 alternativo = -(b + sqrt(b^2 - 4ac)) / (2a)
    x2_racionalizado = x2_clasico

    print("\nCOMPARACIÓN DE RESULTADOS CON REDONDEO A 4 DÍGITOS:")
    print(f"{'Raíz':<6} | {'Exacta (Ref)':<16} | {'Fórmula Clásica':<16} | {'Err Rel Clásico':<16} | {'Racionalizada':<16} | {'Err Rel Racionaliz':<18}")
    print("-" * 95)
    print(f"x1     | {x1_exacto:<16.8f} | {x1_clasico:<16.5f} | {error_relativo(x1_exacto, x1_clasico):<16.4e} | "
          f"{x1_racionalizado:<16.5f} | {error_relativo(x1_exacto, x1_racionalizado):<18.4e}")
    print(f"x2     | {x2_exacto:<16.8f} | {x2_clasico:<16.5f} | {error_relativo(x2_exacto, x2_clasico):<16.4e} | "
          f"{x2_racionalizado:<16.5f} | {error_relativo(x2_exacto, x2_racionalizado):<18.4e}")
    print("=" * 95)
    print("CONCLUSIÓN:")
    print("• En x1 clásico, restar números casi idénticos (-62.10 + 62.06) causa CANCELACIÓN CATASTRÓFICA")
    print("  produciendo un error relativo del orden del 24%.")
    print("• Al racionalizar el numerador (x1 = -2c / (b + sqrt(b^2 - 4ac))), la suma en el denominador")
    print("  preserva las 4 cifras significativas, reduciendo el error relativo a menos del 0.05%.")
    input("\nPresione Enter para continuar...")


def resolver_ejercicio_5():
    """Ejercicio 5: Evaluación de polinomios y propagación de error (Forma Estándar vs Horner)."""
    print("\n" + "=" * 95)
    print("EJERCICIO 5: EVALUACIÓN POLINÓMICA DIRECTA VS FORMA ANIDADA DE HORNER")
    print("Polinomio: f(x) = x³ - 6x² + 3x - 0.149   en   x = 4.71")
    print("=" * 95)

    x = 4.71

    # 5.a Forma estándar término a término sin normalizar (redondeo vs truncamiento a 3 dígitos)
    def evaluar_terminos(modo):
        x_k = normalizar_k_digitos(x, 3, modo)
        x2_k = normalizar_k_digitos(x_k * x_k, 3, modo)
        x3_k = normalizar_k_digitos(x2_k * x_k, 3, modo)
        seis_x2_k = normalizar_k_digitos(6.0 * x2_k, 3, modo)
        tres_x_k = normalizar_k_digitos(3.0 * x_k, 3, modo)
        c = 0.149

        # Operaciones sucesivas de izquierda a derecha
        p1 = normalizar_k_digitos(x3_k - seis_x2_k, 3, modo)
        p2 = normalizar_k_digitos(p1 + tres_x_k, 3, modo)
        res_f = normalizar_k_digitos(p2 - c, 3, modo)

        return x_k, x2_k, x3_k, seis_x2_k, tres_x_k, res_f

    # Valores exactos con precisión completa
    x_ex = x
    x2_ex = x ** 2
    x3_ex = x ** 3
    seis_x2_ex = 6.0 * x2_ex
    tres_x_ex = 3.0 * x_ex
    f_ex = x3_ex - seis_x2_ex + tres_x_ex - 0.149

    _, x2_tr, x3_tr, s_x2_tr, t_x_tr, f_tr = evaluar_terminos('truncamiento')
    _, x2_rd, x3_rd, s_x2_rd, t_x_rd, f_rd = evaluar_terminos('redondeo')

    # Tabla pedida en la consigna 5.a
    print("\nTABLA DE TÉRMINOS EVALUADOS (CONSIGNA 5.a):")
    print(f"{'Modalidad':<22} | {'x':<7} | {'x²':<10} | {'x³':<10} | {'6x²':<10} | {'3x':<10} | {'f(4.71)':<12}")
    print("-" * 95)
    print(f"{'Exacto':<22} | {x_ex:<7.2f} | {x2_ex:<10.4f} | {x3_ex:<10.4f} | {seis_x2_ex:<10.4f} | {tres_x_ex:<10.4f} | {f_ex:<12.5f}")
    print(f"{'3 Dígitos (Truncado)':<22} | {x:<7.2f} | {x2_tr:<10.3f} | {x3_tr:<10.3f} | {s_x2_tr:<10.3f} | {t_x_tr:<10.3f} | {f_tr:<12.3f}")
    print(f"{'3 Dígitos (Redondeado)':<22} | {x:<7.2f} | {x2_rd:<10.3f} | {x3_rd:<10.3f} | {s_x2_rd:<10.3f} | {t_x_rd:<10.3f} | {f_rd:<12.3f}")
    print("-" * 95)

    # 5.b Forma anidada de Horner: f(x) = ((x - 6)x + 3)x - 0.149
    def evaluar_horner(modo):
        x_k = normalizar_k_digitos(x, 3, modo)
        paso1 = normalizar_k_digitos(x_k - 6.0, 3, modo)
        paso2 = normalizar_k_digitos(paso1 * x_k, 3, modo)
        paso3 = normalizar_k_digitos(paso2 + 3.0, 3, modo)
        paso4 = normalizar_k_digitos(paso3 * x_k, 3, modo)
        return normalizar_k_digitos(paso4 - 0.149, 3, modo)

    f_horner_tr = evaluar_horner('truncamiento')
    f_horner_rd = evaluar_horner('redondeo')

    print("\nCOMPARACIÓN DE ERRORES: FORMA DIRECTA VS FORMA ANIDADA DE HORNER (CONSIGNA 5.b):")
    print(f"{'Esquema de Evaluación':<32} | {'Resultado':<12} | {'Error Absoluto':<16} | {'Error Relativo':<16}")
    print("-" * 85)
    print(f"{'Valor Exacto':<32} | {f_ex:<12.5f} | {'---':<16} | {'---':<16}")
    print(f"{'Directo (Truncamiento 3d)':<32} | {f_tr:<12.3f} | {error_absoluto(f_ex, f_tr):<16.4e} | {error_relativo(f_ex, f_tr):<16.4e}")
    print(f"{'Directo (Redondeo 3d)':<32} | {f_rd:<12.3f} | {error_absoluto(f_ex, f_rd):<16.4e} | {error_relativo(f_ex, f_rd):<16.4e}")
    print(f"{'Horner Anidado (Truncado 3d)':<32} | {f_horner_tr:<12.3f} | {error_absoluto(f_ex, f_horner_tr):<16.4e} | {error_relativo(f_ex, f_horner_tr):<16.4e}")
    print(f"{'Horner Anidado (Redondeado 3d)':<32} | {f_horner_rd:<12.3f} | {error_absoluto(f_ex, f_horner_rd):<16.4e} | {error_relativo(f_ex, f_horner_rd):<16.4e}")
    print("=" * 85)
    print("CONCLUSIÓN:")
    print("• La forma anidada de Horner reduce drásticamente las multiplicaciones (de 5 a 2),")
    print("  minimizando la acumulación y propagación del error por redondeo y truncamiento.")
    input("\nPresione Enter para continuar...")


def menu_guia_2():
    """Submenú interactivo principal de la Guía de Laboratorio N° 2."""
    while True:
        print("\n" + "=" * 90)
        print("GUÍA DE LABORATORIO N° 2 - APROXIMACIONES NUMÉRICAS Y ERRORES")
        print("=" * 90)
        print("  1. Ejercicio 1: Error Absoluto y Relativo de aproximaciones elementales")
        print("  2. Ejercicios 2 y 3: Operaciones con normalización a 3 dígitos (Redondeo vs Truncamiento)")
        print("  3. Ejercicio 4: Cancelación sustractiva en fórmula cuadrática (Fórmula Racionalizada)")
        print("  4. Ejercicio 5: Evaluación polinómica directa vs Forma Anidada de Horner")
        print("  5. Ejecutar la Guía N° 2 completa en secuencia")
        print("  0. Volver al Menú Principal")
        print("-" * 90)

        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            resolver_ejercicio_1()
        elif opcion == '2':
            resolver_ejercicios_2_y_3()
        elif opcion == '3':
            resolver_ejercicio_4()
        elif opcion == '4':
            resolver_ejercicio_5()
        elif opcion == '5':
            resolver_ejercicio_1()
            resolver_ejercicios_2_y_3()
            resolver_ejercicio_4()
            resolver_ejercicio_5()
        elif opcion == '0':
            break
        else:
            print("Opción no válida. Intente nuevamente.")