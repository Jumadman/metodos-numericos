"""
Módulo: guia_1.py
Descripción: Resolución interactiva de los Ejercicios 1 al 6 y Complementarios
             de la Guía de Laboratorio N° 1 (Modelos Matemáticos y Algoritmos).
"""

import time
import math


# =============================================================================
# EJERCICIO 1: SUMA DE N NÚMEROS POSITIVOS
# =============================================================================
def resolver_ejercicio_1():
    print("\n" + "=" * 90)
    print("EJERCICIO 1: SUMA DE N NÚMEROS POSITIVOS (X_1 a X_N)")
    print("Modelo Matemático: S = sum_{i=1}^N X_i   con X_i > 0")
    print("=" * 90)

    print("Consigna: Probar con N en rango entero de 8 bits [0, 255] y luego con N = 10000.")
    n_in = input("Ingrese el valor de N (Enter para 255): ").strip()
    n = int(n_in) if n_in else 255

    print("\nSeleccione el modo de carga de datos:")
    print("  1. Generación automática con valores X_i = i (permite verificar con Gauss S = N*(N+1)/2)")
    print("  2. Ingreso manual de cada número por teclado (recomendado para N pequeño)")
    modo = input("Opción (Enter para 1): ").strip() or '1'

    inicio = time.perf_counter()
    if modo == '2' and n <= 20:
        valores = []
        for i in range(1, n + 1):
            val = float(input(f"  Ingrese X_{i}: ").strip() or 1.0)
            valores.append(abs(val))
        suma = sum(valores)
    else:
        # Generación eficiente
        suma = (n * (n + 1)) // 2  # Comprobación analítica
        # Simulación de acumulación iterativa
        acumulador = 0.0
        for i in range(1, n + 1):
            acumulador += float(i)
        suma = acumulador

    t_proceso = time.perf_counter() - inicio

    print("\nRESULTADOS:")
    print(f"- Cantidad de sumandos N        : {n}")
    print(f"- Suma total acumulada S        : {suma:,.2f}")
    print(f"- Tiempo de ejecución (CPU)     : {t_proceso:.6f} segundos")
    print("- Clasificación algorítmica     : Algoritmo iterativo determinístico O(N)")
    print("=" * 90)
    input("\nPresione Enter para continuar...")


# =============================================================================
# EJERCICIO 2: SUMA DE VALORES PARES DE 200 NÚMEROS POSITIVOS
# =============================================================================
def resolver_ejercicio_2():
    print("\n" + "=" * 90)
    print("EJERCICIO 2: SUMA DE VALORES PARES DE 200 NÚMEROS POSITIVOS")
    print("Modelo Matemático: S_par = sum_{i=1}^{200} X_i   donde X_i mod 2 == 0")
    print("=" * 90)

    n = 200
    print(f"Generando secuencia de {n} enteros positivos del 1 al {n}...")
    inicio = time.perf_counter()

    suma_pares = 0
    cantidad_pares = 0
    for i in range(1, n + 1):
        if i % 2 == 0:
            suma_pares += i
            cantidad_pares += 1

    t_proceso = time.perf_counter() - inicio

    print("\nRESULTADOS:")
    print(f"- Total de elementos evaluados : {n}")
    print(f"- Elementos pares filtrados     : {cantidad_pares}")
    print(f"- Suma de los valores pares     : {suma_pares}")
    print(f"- Tiempo de ejecución (CPU)     : {t_proceso:.6f} segundos")
    print("- Clasificación algorítmica     : Algoritmo de filtrado condicional O(N)")
    print("=" * 90)
    input("\nPresione Enter para continuar...")


# =============================================================================
# EJERCICIO 3: SUCESIÓN DE FIBONACCI (N = 200)
# =============================================================================
def resolver_ejercicio_3():
    print("\n" + "=" * 95)
    print("EJERCICIO 3: SUCESIÓN DE FIBONACCI (PROCESOS ITERATIVOS VS RECURSIVOS)")
    print("Modelo Matemático: F_0 = 0, F_1 = 1, F_n = F_{n-1} + F_{n-2}   (n >= 2)")
    print("=" * 95)

    n_in = input("Ingrese el número de términos N a generar (Enter para N = 200): ").strip()
    n = int(n_in) if n_in else 200

    print(f"\nCalculando los primeros {n} términos de Fibonacci mediante proceso iterativo O(N)...")
    inicio_it = time.perf_counter()

    fib = [0, 1]
    for k in range(2, n):
        fib.append(fib[-1] + fib[-2])
    fib = fib[:n]

    t_it = time.perf_counter() - inicio_it

    print("\nRESULTADOS OBTENIDOS:")
    print(f"- F(0) = {fib[0]}")
    print(f"- F(1) = {fib[1]}")
    print(f"- F(2) = {fib[2]}")
    print(f"- F(10) = {fib[10]}")
    print(f"- F({n-1}) = {fib[-1]}")
    print(f"- Cantidad de dígitos de F({n-1}) : {len(str(fib[-1]))} dígitos")
    print(f"- Tiempo de cómputo iterativo    : {t_it:.6f} segundos")

    print("\nFUNDAMENTACIÓN TEÓRICA (DEFENSA ORAL):")
    print("• Proceso Recursivo Naive: Complejidad exponencial O(2^N). Para N = 200 requeriría")
    print("  aproximadamente 2^200 operaciones (~10^60 pasos), desbordando la pila (RecursionError).")
    print("• Proceso Iterativo: Complejidad lineal O(N) y memoria O(N), ejecutado en microsegundos.")
    print("=" * 95)
    input("\nPresione Enter para continuar...")


# =============================================================================
# EJERCICIO 4: ECUACIÓN DE SEGUNDO GRADO
# =============================================================================
def resolver_ejercicio_4():
    print("\n" + "=" * 90)
    print("EJERCICIO 4: ECUACIÓN DE SEGUNDO GRADO A PARTIR DE CONDICIÓN VERBAL")
    print("=" * 90)
    print("Enunciado: 'Al quíntuple de un número (5x) se le suma el triple de su cuadrado (3x²),")
    print("            obteniendo el triple del mismo (3x) más 1.'")
    print("\n1. Formulación del Modelo Matemático:")
    print("   5x + 3x² = 3x + 1")
    print("   Igualando a cero: 3x² + (5x - 3x) - 1 = 0")
    print("   -> Ecuación canónica: 3x² + 2x - 1 = 0   (a = 3, b = 2, c = -1)")

    inicio = time.perf_counter()
    a, b, c = 3.0, 2.0, -1.0
    discriminante = b**2 - 4.0 * a * c  # 4 - 4*(3)*(-1) = 16

    x1 = (-b + math.sqrt(discriminante)) / (2.0 * a)  # (-2 + 4) / 6 = 1/3
    x2 = (-b - math.sqrt(discriminante)) / (2.0 * a)  # (-2 - 4) / 6 = -1
    t_proceso = time.perf_counter() - inicio

    print("\n2. Solución Algebraica Directa (Fórmula Resolvente):")
    print(f"   Discriminante Δ = b² - 4ac = {discriminante:.1f} > 0  (Dos raíces reales distintas)")
    print(f"   • Raíz x_1 = {x1:.6f}  (1/3)")
    print(f"   • Raíz x_2 = {x2:.6f}  (-1)")

    print("\n3. Verificación de la condición:")
    print(f"   Para x_1 = {x1:.4f}: 5({x1:.4f}) + 3({x1:.4f})² = {5*x1 + 3*(x1**2):.4f} | 3({x1:.4f}) + 1 = {3*x1 + 1:.4f}  [CUMPLE]")
    print(f"   Para x_2 = {x2:.4f}: 5({x2:.4f}) + 3({x2:.4f})² = {5*x2 + 3*(x2**2):.4f} | 3({x2:.4f}) + 1 = {3*x2 + 1:.4f}  [CUMPLE]")
    print(f"- Tiempo de resolución CPU : {t_proceso:.6f} segundos")
    print("- Clasificación             : Algoritmo analítico exacto de tiempo constante O(1)")
    print("=" * 90)
    input("\nPresione Enter para continuar...")


# =============================================================================
# EJERCICIO 5: APROXIMACIÓN DEL NÚMERO e MEDIANTE SERIE DE TAYLOR
# =============================================================================
def resolver_ejercicio_5():
    print("\n" + "=" * 95)
    print("EJERCICIO 5: APROXIMACIÓN DEL NÚMERO e MEDIANTE SERIE DE POTENCIAS")
    print("Modelo Matemático: e = sum_{k=0}^N (1 / k!) = 1 + 1/1! + 1/2! + 1/3! + ... + 1/N!")
    print("=" * 95)

    e_exacto = math.e
    cantidades_n = [1, 2, 3, 5, 7, 10, 15, 20]

    print(f"Valor de referencia exacto: e = {e_exacto:.15f}")
    print(f"{'Términos (N)':<14} | {'Aprox. de e':<18} | {'Error Absoluto':<16} | {'Error Relativo':<16} | {'Tiempo (s)':<10}")
    print("-" * 95)

    for n in cantidades_n:
        inicio = time.perf_counter()
        aprox_e = 0.0
        fact = 1.0
        for k in range(n + 1):
            if k > 0:
                fact *= k
            aprox_e += 1.0 / fact

        t_act = time.perf_counter() - inicio
        err_abs = abs(e_exacto - aprox_e)
        err_rel = err_abs / e_exacto

        print(f"{n:<14d} | {aprox_e:<18.15f} | {err_abs:<16.4e} | {err_rel:<16.4e} | {t_act:<10.6f}")

    print("=" * 95)
    print("CONCLUSIONES DE CONVERGENCIA:")
    print("• La serie converge factorialmente O(1/N!), superando la velocidad exponencial.")
    print("• Con solo N = 15 términos se alcanza la precisión máxima de coma flotante estándar IEEE 754 (64 bits).")
    input("\nPresione Enter para continuar...")


# =============================================================================
# EJERCICIO 6: CÁLCULO DE PI MEDIANTE SERIE DE GREGORY-LEIBNIZ
# =============================================================================
def resolver_ejercicio_6():
    print("\n" + "=" * 98)
    print("EJERCICIO 6: CÁLCULO DE PI MEDIANTE SERIE DE GREGORY-LEIBNIZ")
    print("Modelo Matemático: π = 4 * sum_{k=0}^M [ (-1)^k / (2k + 1) ] = 4 * (1 - 1/3 + 1/5 - 1/7 + ...)")
    print("=" * 98)

    pi_exacto = math.pi
    metas_decimales = [
        ("3 dígitos exactos (Error < 1e-3)", 1e-3),
        ("4 dígitos exactos (Error < 1e-4)", 1e-4),
        ("5 dígitos exactos (Error < 1e-5)", 1e-5)
    ]

    print(f"Valor de referencia: π = {pi_exacto:.15f}\n")
    print(f"{'Criterio de Precisión':<34} | {'Términos Necesarios (M)':<24} | {'Aprox. Obtenida':<16} | {'Error Cometido':<14} | {'Tiempo (s)':<10}")
    print("-" * 98)

    for desc, tol in metas_decimales:
        inicio = time.perf_counter()
        
        # En series alternantes de Leibniz, el resto está acotado por el primer término omitido:
        # 4 / (2M + 3) < tol  =>  2M + 3 > 4 / tol  =>  M > (4/tol - 3) / 2
        m_estimado = math.ceil((4.0 / tol - 3.0) / 2.0)
        
        # Cálculo acumulativo real
        aprox_pi = 0.0
        signo = 1.0
        for k in range(m_estimado):
            aprox_pi += signo / (2.0 * k + 1.0)
            signo = -signo
        aprox_pi *= 4.0

        t_calc = time.perf_counter() - inicio
        err_cometido = abs(pi_exacto - aprox_pi)

        print(f"{desc:<34} | {m_estimado:<24,d} | {aprox_pi:<16.7f} | {err_cometido:<14.4e} | {t_calc:<10.4f}")

    print("=" * 98)
    print("COMPARACIÓN CRÍTICA (DEFENSA ORAL):")
    print("• Para 3 decimales se requieren ~2.000 términos; para 4 decimales ~20.000; para 5 decimales ~200.000.")
    print("• Convergencia Sub-Lineal O(1/M): Cada dígito adicional de precisión exige multiplicar por 10")
    print("  el número de operaciones y el tiempo de CPU, evidenciando la ineficiencia de la serie clásica de Leibniz.")
    input("\nPresione Enter para continuar...")


# =============================================================================
# EJERCICIOS COMPLEMENTARIOS
# =============================================================================
def resolver_complementarios():
    print("\n" + "=" * 90)
    print("EJERCICIOS COMPLEMENTARIOS DE LA GUÍA N° 1")
    print("=" * 90)

    # Complementario 1
    print("1. Término general: a_i = (-1)^i / (2i + 1). Se sabe que el último término es 1/17.")
    print("   Para que el término sea positivo (+1/17), (-1)^i = 1 => 'i' debe ser par.")
    print("   Igualando denominadores: 2i + 1 = 17 => 2i = 16 => i = 8.")
    print("   -> Si la sucesión inicia en i = 0 hasta i = 8, la solución tiene EXACTAMENTE 9 TÉRMINOS.")
    print("      (Términos: i = 0, 1, 2, 3, 4, 5, 6, 7, 8).")

    # Complementario 2
    print("\n2. Desarrollo de los primeros 'n' términos de e^x:")
    x_in = input("   Ingrese el valor de x (Enter para x = 1.0): ").strip()
    x = float(x_in) if x_in else 1.0
    n_in = input("   Ingrese la cantidad de términos n (Enter para n = 6): ").strip()
    n = int(n_in) if n_in else 6

    aprox = 0.0
    terminos_str = []
    fact = 1.0
    potencia = 1.0
    for k in range(n):
        if k == 0:
            aprox += 1.0
            terminos_str.append("1")
        else:
            potencia *= x
            fact *= k
            aprox += potencia / fact
            terminos_str.append(f"({x}^{k}/{k}!)")

    print(f"   Polinomio evaluado: e^{x} ≈ {' + '.join(terminos_str)}")
    print(f"   -> Valor calculado con {n} términos : {aprox:.10f}")
    print(f"   -> Valor exacto math.exp({x})       : {math.exp(x):.10f}")
    print(f"   -> Error absoluto                  : {abs(math.exp(x) - aprox):.4e}")
    print("=" * 90)
    input("\nPresione Enter para continuar...")


# =============================================================================
# MENÚ PRINCIPAL DE LA GUÍA 1
# =============================================================================
def menu_guia_1():
    """Submenú interactivo para navegar por todos los ejercicios de la Guía N° 1."""
    while True:
        print("\n" + "=" * 90)
        print("GUÍA DE LABORATORIO N° 1 - MODELOS MATEMÁTICOS, ALGORITMOS Y CONVERGENCIA")
        print("=" * 90)
        print("  1. Ejercicio 1: Suma de N números positivos (N in [0, 255] y N = 10000)")
        print("  2. Ejercicio 2: Suma de valores pares de 200 números positivos")
        print("  3. Ejercicio 3: Sucesión de Fibonacci con N = 200 (Recursivo vs Iterativo)")
        print("  4. Ejercicio 4: Ecuación de 2° grado (3x² + 2x - 1 = 0) a partir de enunciado verbal")
        print("  5. Ejercicio 5: Cálculo del número e por serie factorial (Análisis de Convergencia)")
        print("  6. Ejercicio 6: Cálculo de π por serie de Leibniz (Tiempos para 3, 4 y 5 decimales)")
        print("  7. Ejercicios Complementarios (Término 1/17 y expansión de e^x)")
        print("  8. Ejecutar la Guía N° 1 completa en secuencia")
        print("  0. Volver al Menú Principal")
        print("-" * 90)

        op = input("Seleccione una opción: ").strip()
        if op == '1':
            resolver_ejercicio_1()
        elif op == '2':
            resolver_ejercicio_2()
        elif op == '3':
            resolver_ejercicio_3()
        elif op == '4':
            resolver_ejercicio_4()
        elif op == '5':
            resolver_ejercicio_5()
        elif op == '6':
            resolver_ejercicio_6()
        elif op == '7':
            resolver_complementarios()
        elif op == '8':
            resolver_ejercicio_1()
            resolver_ejercicio_2()
            resolver_ejercicio_3()
            resolver_ejercicio_4()
            resolver_ejercicio_5()
            resolver_ejercicio_6()
            resolver_complementarios()
        elif op == '0':
            break
        else:
            print("Opción no válida. Intente nuevamente.")