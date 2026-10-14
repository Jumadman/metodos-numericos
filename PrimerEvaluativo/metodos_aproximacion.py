import time

def ejecutar_interpolacion_lineal(f, a, b, tol=0.001, max_iter=100):
    """Ejecuta Regula Falsi, imprime la grilla reglamentaria y retorna métricas e historial."""
    inicio = time.perf_counter()
    fa, fb = f(a), f(b)
    historial = []

    print("\n" + "=" * 88)
    print("--- MÉTODO 1: INTERPOLACIÓN LINEAL / REGULA FALSI (GRILLA DE RESULTADOS) ---")
    print("=" * 88)
    print(f"{'i':<5} {'[a, b]':<22} {'x_i':<14} {'f(x_i)':<15} {'Error':<15} {'Tiempo (s)':<12}")
    print("-" * 88)

    x_prev = a
    x = a
    error = abs(b - a)

    for i in range(1, max_iter + 1):
        x = b - (fb * (b - a)) / (fb - fa)
        fx = f(x)
        error = abs(b - a) if i == 1 else abs(x - x_prev)
        tiempo_actual = time.perf_counter() - inicio

        intervalo_str = f"[{a:.5f}, {b:.5f}]"
        print(f"{i:<5} {intervalo_str:<22} {x:<14.6f} {fx:<15.6e} {error:<15.6e} {tiempo_actual:<12.6f}")

        historial.append({
            'iter': i, 'a': a, 'b': b,
            'fa': fa, 'fb': fb,
            'x': x, 'fx': fx,
            'error': error, 'tiempo': tiempo_actual
        })

        if error < tol and i > 1:
            break

        if fa * fx < 0:
            b, fb = x, fx
        else:
            a, fa = x, fx
        x_prev = x

    tiempo_total = time.perf_counter() - inicio
    print("=" * 88)
    print(f"RESULTADO INTERPOLACIÓN LINEAL -> Raíz x = {x:.6f} m | Iteraciones: {len(historial)} | Error: {error:.6e} | Tiempo: {tiempo_total:.6f} s")

    metricas = {
        'metodo': 'Interpolación Lineal (Regula Falsi)',
        'raiz': x,
        'f_raiz': f(x),
        'iteraciones': len(historial),
        'error': error,
        'tiempo': tiempo_total
    }
    return metricas, historial


def derivada_numerica(func, x, h=1e-5):
    """Calcula la derivada numérica por diferencias finitas centrales."""
    return (func(x + h) - func(x - h)) / (2.0 * h)

def analizar_convergencia_punto_fijo(g, x0):
    """
    Verifica computacionalmente la condición suficiente de convergencia de Lipschitz:
    |g'(x0)| < 1 en el entorno de la semilla seleccionada.
    """
    dg_val = derivada_numerica(g, x0)
    abs_dg = abs(dg_val)

    print("\n" + "=" * 90)
    print("ANÁLISIS TEÓRICO PREVIO: CONDICIÓN DE CONVERGENCIA DE LIPSCHITZ")
    print("=" * 90)
    print(f"Punto de arranque seleccionado (semilla): x0 = {x0:.6f}")
    print(f"Derivada numérica evaluada en semilla:  g'(x0) = {dg_val:+.6f}")
    print(f"Módulo de la derivada (factor de contracción): |g'(x0)| = {abs_dg:.6f}")

    if abs_dg < 1.0:
        tipo_conv = "Monótona (sin oscilaciones)" if dg_val > 0 else "Oscilante / Alternante (en telaraña)"
        print(f"-> CUMPLE (|g'(x0)| < 1): El proceso iterativo es LOCALMENTE CONVERGENTE.")
        print(f"-> Dinámica teórica del esquema simple: {tipo_conv}.")
        print("-> Aceleración de Steffensen: Activa (extrapola cuadráticamente sobre la dinámica).")
        return True, abs_dg
    else:
        print(f"-> ADVERTENCIA (|g'(x0)| >= 1): El punto fijo simple es DIVERGENTE en este entorno.")
        return False, abs_dg


def ejecutar_steffensen(f, g, x0, tol=0.001, max_ciclos=30):
    """
    Método de Steffensen: Algoritmo de aceleración Delta^2 de Aitken con reinicio activo.
    Genera ternas (p0, p1, p2), interpola el punto límite y reinicia la semilla.
    """
    # 1. Chequeo de convergencia previo
    es_convergente, factor_k = analizar_convergencia_punto_fijo(g, x0)

    inicio = time.perf_counter()
    historial = []

    print("\n" + "=" * 115)
    print("--- MÉTODO 2: MÉTODO DE STEFFENSEN (AITKEN POR CICLOS CON REINICIO) ---")
    print("=" * 115)
    print(f"{'Ciclo':<6} | {'Puntos (k)':<12} | {'p0 (Semilla)':<14} | {'p1 = g(p0)':<14} | {'p_aitken (p̂)':<16} | {'f(p̂)':<14} | {'Error':<12}")
    print("-" * 115)

    p0 = float(x0)
    p_aitken_prev = None
    raiz_final = p0
    error_final = None
    contador_puntos = 0

    for ciclo in range(1, max_ciclos + 1):
        tiempo_actual = time.perf_counter() - inicio

        # Terna del ciclo
        contador_puntos += 1
        k1 = contador_puntos
        p1 = g(p0)

        contador_puntos += 1
        k2 = contador_puntos
        p2 = g(p1)

        # Extrapolación de Aitken sobre la terna (p0, p1, p2)
        denominador = p2 - 2.0 * p1 + p0
        if abs(denominador) > 1e-14:
            p_aitken = p0 - ((p1 - p0) ** 2) / denominador
        else:
            p_aitken = p2

        contador_puntos += 1
        k_aitken = contador_puntos
        fp_aitken = f(p_aitken)

        if p_aitken_prev is not None:
            error_actual = abs(p_aitken - p_aitken_prev)
            error_str = f"{error_actual:.4e}"
        else:
            error_actual = abs(p_aitken - p0)
            error_str = "---"

        pasos_str = f"x{k1}, x{k2} -> x{k_aitken}"
        print(f"{ciclo:<6} | {pasos_str:<12} | {p0:<14.6f} | {p1:<14.6f} | {p_aitken:<16.6f} | {fp_aitken:<14.4e} | {error_str:<12}")

        historial.append({
            'ciclo': ciclo,
            'p0': p0,
            'p1': p1,
            'p2': p2,
            'fp0': f(p0),
            'p_aitken': p_aitken,
            'fp_aitken': fp_aitken,
            'error': error_actual,
            'tiempo': tiempo_actual
        })

        if p_aitken_prev is not None and error_actual < tol:
            raiz_final = p_aitken
            error_final = error_actual
            break

        p_aitken_prev = p_aitken
        p0 = p_aitken

    tiempo_total = time.perf_counter() - inicio
    if error_final is None:
        raiz_final = p_aitken
        error_final = error_actual

    print("=" * 115)
    print(f"RESULTADOS FINALES STEFFENSEN:")
    print(f"- Solución aproximada (p)      : {raiz_final:.6f}")
    print(f"- Ciclos ejecutados            : {len(historial)}")
    print(f"- Evaluaciones de g(x) totales : {len(historial) * 2}")
    print(f"- Puntos totales generados     : {contador_puntos}")
    print(f"- Error final aproximado       : {error_final:.6e}")
    print(f"- Tiempo de CPU total          : {tiempo_total:.6f} s\n")

    metricas = {
        'metodo': 'Método de Steffensen (Aitken Reiniciado)',
        'raiz': raiz_final,
        'f_raiz': f(raiz_final),
        'iteraciones': len(historial),
        'evaluaciones_g': len(historial) * 2,
        'pasos_totales': contador_puntos,
        'error': error_final,
        'tiempo': tiempo_total
    }
    return metricas, historial