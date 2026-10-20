"""
Módulo: metodos_aproximacion.py
Descripción: Implementación modular de los algoritmos de aproximación de raíces:
             1. Método de Interpolación Lineal (Regula Falsi).
             2. Método de Steffensen (Punto Fijo con aceleración Delta^2 de Aitken).
Estándar de estilo: PEP 8.
"""

import time
import math


def validar_parametros_entrada(tol, max_iter):
    """
    Valida que los hiperparámetros numéricos de parada sean consistentes.

    Parámetros:
        tol (float): Cota de error máximo admisible (debe ser > 0).
        max_iter (int): Número máximo de iteraciones permitidas (debe ser > 0).

    Retorna:
        tuple: (tol_validada, max_iter_validado)
    """
    tol_ok = float(tol) if (tol is not None and float(tol) > 0) else 0.001
    iter_ok = int(max_iter) if (max_iter is not None and int(max_iter) > 0) else 100
    return tol_ok, iter_ok


def ejecutar_interpolacion_lineal(f, a, b, tol=0.001, max_iter=100):
    """
    Aproxima la raíz de una ecuación no lineal f(x) = 0 en el intervalo [a, b]
    mediante el Método de Interpolación Lineal (Regula Falsi).

    Fundamento matemático:
        Traza la recta secante entre (a, f(a)) y (b, f(b)) y calcula su intersección
        con el eje de abscisas: x_i = b - f(b) * (b - a) / (f(b) - f(a)).
        Actualiza el subintervalo preservando la condición de encierro de Bolzano.

    Parámetros:
        f (callable): Función continua f(x) a evaluar.
        a (float): Límite inferior del intervalo inicial.
        b (float): Límite superior del intervalo inicial.
        tol (float): Tolerancia de error exigida E.
        max_iter (int): Límite de seguridad de iteraciones.

    Retorna:
        tuple: (diccionario_metricas, lista_historial_estados)
    """
    tol, max_iter = validar_parametros_entrada(tol, max_iter)

    # Validación de orden de los extremos del intervalo
    if a > b:
        a, b = b, a
    elif abs(b - a) < 1e-14:
        raise ValueError(f"Intervalo degenerado: los extremos a={a} y b={b} son idénticos.")

    inicio_cpu = time.perf_counter()
    fa = f(a)
    fb = f(b)

    # Validación de existencia de raíz según el Teorema de Bolzano
    if math.isnan(fa) or math.isnan(fb) or math.isinf(fa) or math.isinf(fb):
        raise ValueError(f"La función no está definida en los extremos del intervalo [{a}, {b}].")

    if fa * fb > 0:
        print(f"\n[Error de Validación] El intervalo [{a:.4f}, {b:.4f}] no cumple la condición "
              f"de cambio de signo de Bolzano: f(a)={fa:.4f}, f(b)={fb:.4f}.")
        return None, []

    historial = []

    print("\n" + "=" * 88)
    print("--- MÉTODO 1: INTERPOLACIÓN LINEAL / REGULA FALSI (GRILLA DE RESULTADOS) ---")
    print("=" * 88)
    print(f"{'i':<5} {'[a, b]':<22} {'x_i':<14} {'f(x_i)':<15} {'Error':<15} {'Tiempo (s)':<12}")
    print("-" * 88)

    x_prev = a
    x_actual = a
    error_estimado = abs(b - a)

    for i in range(1, max_iter + 1):
        denominador = fb - fa

        # Prevención de cancelación catastrófica por denominador nulo
        if abs(denominador) < 1e-15 or math.isnan(denominador):
            x_actual = (a + b) / 2.0
        else:
            x_actual = b - (fb * (b - a)) / denominador

        fx_actual = f(x_actual)

        # Respaldo por bisección si la evaluación cae en una singularidad
        if math.isnan(fx_actual) or math.isinf(fx_actual):
            x_actual = (a + b) / 2.0
            fx_actual = f(x_actual)

        # En la primera iteración el error se acota por la amplitud del intervalo
        error_estimado = abs(b - a) if i == 1 else abs(x_actual - x_prev)
        tiempo_actual = time.perf_counter() - inicio_cpu

        intervalo_str = f"[{a:.5f}, {b:.5f}]"
        print(f"{i:<5} {intervalo_str:<22} {x_actual:<14.6f} {fx_actual:<15.6e} "
              f"{error_estimado:<15.6e} {tiempo_actual:<12.6f}")

        historial.append({
            'iter': i,
            'a': a,
            'b': b,
            'fa': fa,
            'fb': fb,
            'x': x_actual,
            'fx': fx_actual,
            'error': error_estimado,
            'tiempo': tiempo_actual
        })

        # Criterio de parada dual: por diferencia de aproximaciones sucesivas o residuo nulo
        if (error_estimado < tol and i > 1) or abs(fx_actual) < 1e-15:
            break

        # Reasignación de extremos conservando el cambio de signo (Bolzano)
        if fa * fx_actual < 0:
            b = x_actual
            fb = fx_actual
        else:
            a = x_actual
            fa = fx_actual

        x_prev = x_actual

    tiempo_total = time.perf_counter() - inicio_cpu
    print("=" * 88)
    print(f"RESULTADO INTERPOLACIÓN LINEAL -> Raíz x = {x_actual:.6f} | "
          f"Iteraciones: {len(historial)} | Error: {error_estimado:.6e} | Tiempo: {tiempo_total:.6f} s")

    metricas = {
        'metodo': 'Interpolación Lineal (Regula Falsi)',
        'raiz': x_actual,
        'f_raiz': f(x_actual),
        'iteraciones': len(historial),
        'error': error_estimado,
        'tiempo': tiempo_total
    }
    return metricas, historial


def derivada_numerica(func, x, h=1e-5):
    """
    Aproxima la derivada primera f'(x) mediante el esquema de diferencias finitas
    centrales de orden O(h^2): f'(x) ≈ [f(x + h) - f(x - h)] / (2h).
    """
    f_mas = func(x + h)
    f_menos = func(x - h)
    if math.isnan(f_mas) or math.isnan(f_menos) or math.isinf(f_mas) or math.isinf(f_menos):
        return 0.0
    return (f_mas - f_menos) / (2.0 * h)


def analizar_convergencia_punto_fijo(g, x0):
    """
    Verifica numéricamente el Teorema de Punto Fijo (condición de contractividad de
    Lipschitz |g'(x0)| < 1) en el entorno de la semilla inicial seleccionada.
    """
    dg_val = derivada_numerica(g, x0)
    abs_dg = abs(dg_val)

    print("\n" + "=" * 95)
    print("ANÁLISIS TEÓRICO PREVIO: CONDICIÓN DE CONVERGENCIA DE LIPSCHITZ")
    print("=" * 95)
    print(f"Punto inicial (semilla):               x1 = {x0:.6f}")
    print(f"Derivada numérica evaluada en semilla: g'(x1) = {dg_val:+.6f}")
    print(f"Factor asintótico de contracción:      |g'(x1)| = {abs_dg:.6f}")

    if abs_dg < 1.0:
        tipo_conv = "Monótona unilateral" if dg_val >= 0 else "Oscilante / Alternante (en espiral)"
        print("-> CUMPLE (|g'(x1)| < 1): Esquema de punto fijo LOCALMENTE CONVERGENTE.")
        print(f"-> Dinámica teórica del esquema simple: {tipo_conv}.")
        print("-> Aceleración de Steffensen: Activa (extrapolación cuadrática por ciclos).")
        return True, abs_dg
    else:
        print("-> ADVERTENCIA (|g'(x1)| >= 1): El esquema simple diverge; Steffensen aplicará corrección.")
        return False, abs_dg


def ejecutar_steffensen(f, g, x0, tol=0.001, max_ciclos=30):
    """
    Aproxima la raíz de f(x) = 0 aplicando el Método de Steffensen (aceleración
    Delta^2 de Aitken con reinicio activo sobre el esquema de punto fijo x = g(x)).

    Fundamento matemático:
        En cada ciclo parte de la semilla p0, genera dos iteraciones simples
        p1 = g(p0) y p2 = g(p1), y extrapola el límite mediante diferencias finitas:
            p_aitken = p0 - (p1 - p0)^2 / (p2 - 2*p1 + p0)
        Reinicia el siguiente ciclo asignando p0_nuevo = p_aitken, logrando orden
        de convergencia cuadrático (p = 2) sin evaluar derivadas analíticas.
    """
    tol, max_ciclos = validar_parametros_entrada(tol, max_ciclos)
    analizar_convergencia_punto_fijo(g, x0)

    inicio_cpu = time.perf_counter()
    historial = []

    print("\n" + "=" * 115)
    print("--- MÉTODO 2: MÉTODO DE STEFFENSEN (AITKEN POR CICLOS CON REINICIO) ---")
    print("=" * 115)
    print(f"{'Ciclo':<6} | {'Terna Utilizada':<18} | {'Punto Acelerado':<18} | "
          f"{'f(x_acel)':<14} | {'Error Estimado':<14} | {'Tiempo (s)':<10}")
    print("-" * 115)

    semilla_ciclo = float(x0)
    p_aitken_prev = None
    raiz_final = semilla_ciclo
    error_final = 0.0
    k_contador = 1

    for ciclo in range(1, max_ciclos + 1):
        tiempo_actual = time.perf_counter() - inicio_cpu

        # Generación de la terna de punto fijo (p0, p1, p2)
        k_p0 = k_contador
        p0 = semilla_ciclo

        k_p1 = k_contador + 1
        p1 = g(p0)

        k_p2 = k_contador + 2
        p2 = g(p1)

        # Operador de segunda diferencia finita hacia adelante: Delta^2(p0) = p2 - 2*p1 + p0
        denominador = p2 - 2.0 * p1 + p0
        if abs(denominador) > 1e-14 and not math.isnan(denominador):
            p_aitken = p0 - ((p1 - p0) ** 2) / denominador
        else:
            p_aitken = p2

        # Validación de pertenencia al dominio real de la función objetivo
        fp_aitken = f(p_aitken)
        if math.isnan(fp_aitken) or math.isinf(fp_aitken):
            p_aitken = p2
            fp_aitken = f(p_aitken)

        k_acelerado = k_contador + 3

        if p_aitken_prev is not None:
            error_actual = abs(p_aitken - p_aitken_prev)
            error_str = f"{error_actual:.4e}"
        else:
            error_actual = abs(p_aitken - p0)
            error_str = "---"

        terna_txt = f"(x{k_p0}, x{k_p1}, x{k_p2})"
        acel_txt = f"x{k_acelerado} = {p_aitken:.6f}"
        print(f"{ciclo:<6} | {terna_txt:<18} | {acel_txt:<18} | {fp_aitken:<14.4e} | "
              f"{error_str:<14} | {tiempo_actual:<10.6f}")

        fp0_val = f(p0)
        if math.isnan(fp0_val) or math.isinf(fp0_val):
            fp0_val = 0.0

        historial.append({
            'ciclo': ciclo,
            'k_p0': k_p0, 'p0': p0, 'fp0': fp0_val,
            'k_p1': k_p1, 'p1': p1,
            'k_p2': k_p2, 'p2': p2,
            'k_acel': k_acelerado,
            'p_aitken': p_aitken,
            'fp_aitken': fp_aitken if not math.isnan(fp_aitken) else 0.0,
            'error': error_actual,
            'tiempo': tiempo_actual
        })

        # Condición de parada por tolerancia entre ciclos acelerados o residuo nulo
        if (p_aitken_prev is not None and error_actual < tol) or abs(fp_aitken) < 1e-15:
            raiz_final = p_aitken
            error_final = error_actual
            break

        # Reinicio activo de Steffensen: el valor extrapolado es la semilla del nuevo ciclo
        p_aitken_prev = p_aitken
        semilla_ciclo = p_aitken
        k_contador = k_acelerado

    tiempo_total = time.perf_counter() - inicio_cpu
    if error_final == 0.0 and error_actual is not None:
        raiz_final = p_aitken
        error_final = error_actual

    print("=" * 115)
    print("RESULTADOS FINALES STEFFENSEN:")
    print(f"- Solución aproximada final    : {raiz_final:.6f}")
    print(f"- Ciclos de Steffensen         : {len(historial)}")
    print(f"- Evaluaciones de g(x) totales : {len(historial) * 2}")
    print(f"- Puntos totales generados     : {k_contador}")
    print(f"- Error final aproximado       : {error_final:.6e}")
    print(f"- Tiempo de CPU total          : {tiempo_total:.6f} s\n")

    metricas = {
        'metodo': 'Método de Steffensen (Aitken Reiniciado)',
        'raiz': raiz_final,
        'f_raiz': f(raiz_final),
        'iteraciones': len(historial),
        'evaluaciones_g': len(historial) * 2,
        'pasos_totales': k_contador,
        'error': error_final,
        'tiempo': tiempo_total
    }
    return metricas, historial