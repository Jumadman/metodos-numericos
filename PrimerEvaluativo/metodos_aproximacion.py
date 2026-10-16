import time
import math

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
        denom = fb - fa
        if abs(denom) < 1e-15 or math.isnan(denom):
            x = (a + b) / 2.0
        else:
            x = b - (fb * (b - a)) / denom

        fx = f(x)
        if math.isnan(fx) or math.isinf(fx):
            x = (a + b) / 2.0
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

        if (error < tol and i > 1) or abs(fx) < 1e-15:
            break

        if fa * fx < 0:
            b, fb = x, fx
        else:
            a, fa = x, fx
        x_prev = x

    tiempo_total = time.perf_counter() - inicio
    print("=" * 88)
    print(f"RESULTADO INTERPOLACIÓN LINEAL -> Raíz x = {x:.6f} | Iteraciones: {len(historial)} | Error: {error:.6e} | Tiempo: {tiempo_total:.6f} s")

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
    f_mas = func(x + h)
    f_menos = func(x - h)
    if math.isnan(f_mas) or math.isnan(f_menos) or math.isinf(f_mas) or math.isinf(f_menos):
        return 0.0
    return (f_mas - f_menos) / (2.0 * h)


def analizar_convergencia_punto_fijo(g, x0):
    """Verifica computacionalmente la condición de Lipschitz |g'(x0)| < 1."""
    dg_val = derivada_numerica(g, x0)
    abs_dg = abs(dg_val)

    print("\n" + "=" * 95)
    print("ANÁLISIS TEÓRICO PREVIO: CONDICIÓN DE CONVERGENCIA DE LIPSCHITZ")
    print("=" * 95)
    print(f"Punto inicial (semilla):               x1 = {x0:.6f}")
    print(f"Derivada numérica evaluada en semilla: g'(x1) = {dg_val:+.6f}")
    print(f"Factor asintótico de contracción:      |g'(x1)| = {abs_dg:.6f}")

    if abs_dg < 1.0:
        tipo_conv = "Monótona" if dg_val >= 0 else "Oscilante / Alternante (en telaraña)"
        print(f"-> CUMPLE (|g'(x1)| < 1): Esquema de punto fijo LOCALMENTE CONVERGENTE.")
        print(f"-> Dinámica del punto fijo simple: {tipo_conv}.")
        print("-> Aceleración de Steffensen: Lista para proyectar cuadráticamente sobre la terna.")
        return True, abs_dg
    else:
        print(f"-> ADVERTENCIA (|g'(x1)| >= 1): El punto fijo simple es inestable; Steffensen intentará estabilizarlo.")
        return False, abs_dg


def ejecutar_steffensen(f, g, x0, tol=0.001, max_ciclos=30):
    """
    Método de Steffensen: Proceso Delta^2 de Aitken aplicado por ciclos con reinicio.
    """
    analizar_convergencia_punto_fijo(g, x0)

    inicio = time.perf_counter()
    historial = []

    print("\n" + "=" * 115)
    print("--- MÉTODO 2: MÉTODO DE STEFFENSEN (AITKEN POR CICLOS CON REINICIO) ---")
    print("=" * 115)
    print(f"{'Ciclo':<6} | {'Terna Utilizada':<18} | {'Punto Acelerado':<18} | {'f(x_acel)':<14} | {'Error Estimado':<14} | {'Tiempo (s)':<10}")
    print("-" * 115)

    semilla_ciclo = float(x0)
    p_aitken_prev = None
    raiz_final = semilla_ciclo
    error_final = 0.0
    k_contador = 1

    for ciclo in range(1, max_ciclos + 1):
        tiempo_actual = time.perf_counter() - inicio

        k_p0 = k_contador
        p0 = semilla_ciclo

        k_p1 = k_contador + 1
        p1 = g(p0)

        k_p2 = k_contador + 2
        p2 = g(p1)

        # Extrapolación de Aitken sobre la terna (p0, p1, p2)
        denominador = p2 - 2.0 * p1 + p0
        if abs(denominador) > 1e-14 and not math.isnan(denominador):
            p_aitken = p0 - ((p1 - p0) ** 2) / denominador
        else:
            p_aitken = p2

        # Protección si el salto cae temporalmente fuera del dominio de f(x)
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
        print(f"{ciclo:<6} | {terna_txt:<18} | {acel_txt:<18} | {fp_aitken:<14.4e} | {error_str:<14} | {tiempo_actual:<10.6f}")

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

        if (p_aitken_prev is not None and error_actual < tol) or abs(fp_aitken) < 1e-15:
            raiz_final = p_aitken
            error_final = error_actual
            break

        p_aitken_prev = p_aitken
        semilla_ciclo = p_aitken
        k_contador = k_acelerado

    tiempo_total = time.perf_counter() - inicio
    if error_final == 0.0 and error_actual is not None:
        raiz_final = p_aitken
        error_final = error_actual

    print("=" * 115)
    print(f"RESULTADOS FINALES STEFFENSEN:")
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