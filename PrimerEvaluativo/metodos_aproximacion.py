"""
Módulo: metodos_aproximacion.py
Descripción: Contiene los 4 métodos numéricos dinámicos exigidos por la cátedra:
             1. Intervalo Medio (Bisección) con cálculo de iteraciones teóricas.
             2. Interpolación Lineal (Regula Falsi).
             3. Newton-Raphson con análisis automático de Condiciones de Fourier.
             4. Iteración de Punto Fijo (Simple y con Aceleración de Aitken/Steffensen).
"""

import time
import math


def validar_parametros(tol, max_iter):
    tol_ok = float(tol) if (tol is not None and float(tol) > 0) else 0.001
    iter_ok = int(max_iter) if (max_iter is not None and int(max_iter) > 0) else 100
    return tol_ok, iter_ok


def derivada_numerica(func, x, h=1e-5):
    """Aproxima f'(x) por diferencias finitas centrales O(h^2)."""
    f_mas, f_menos = func(x + h), func(x - h)
    if any(math.isnan(v) or math.isinf(v) for v in (f_mas, f_menos)):
        return 0.0
    return (f_mas - f_menos) / (2.0 * h)


def segunda_derivada_numerica(func, x, h=1e-4):
    """Aproxima f''(x) por diferencias finitas centrales O(h^2)."""
    f_mas, f_cen, f_menos = func(x + h), func(x), func(x - h)
    if any(math.isnan(v) or math.isinf(v) for v in (f_mas, f_cen, f_menos)):
        return 0.0
    return (f_mas - 2.0 * f_cen + f_menos) / (h ** 2)


# =============================================================================
# 1. MÉTODO DE INTERVALO MEDIO (BISECCIÓN)
# =============================================================================
def ejecutar_biseccion(f, a, b, tol=0.001, max_iter=100):
    """Ejecuta el Método de Intervalo Medio informando las iteraciones teóricas necesarias."""
    tol, max_iter = validar_parametros(tol, max_iter)
    if a > b:
        a, b = b, a

    fa, fb = f(a), f(b)
    if math.isnan(fa) or math.isnan(fb) or fa * fb > 0:
        print(f"\n[Error Bolzano] El intervalo [{a:.4f}, {b:.4f}] no presenta cambio de signo.")
        return None, []

    inicio = time.perf_counter()
    n_teorico = math.ceil((math.log(b - a) - math.log(tol)) / math.log(2.0)) if (b - a) > 0 else 1

    print("\n" + "=" * 90)
    print("--- MÉTODO DE INTERVALO MEDIO (BISECCIÓN) ---")
    print(f"Intervalo: [{a:.4f}, {b:.4f}] | Tolerancia E < {tol} | Iteraciones teóricas necesarias: {n_teorico}")
    print("=" * 90)
    print(f"{'i':<5} {'[a, b]':<24} {'x_i (Medio)':<15} {'f(x_i)':<15} {'Error Cota':<15} {'Tiempo (s)':<10}")
    print("-" * 90)

    historial = []
    c = (a + b) / 2.0
    cota_error = (b - a) / 2.0

    for i in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = f(c)
        cota_error = (b - a) / 2.0
        t_act = time.perf_counter() - inicio

        intervalo_str = f"[{a:.5f}, {b:.5f}]"
        print(f"{i:<5} {intervalo_str:<24} {c:<15.6f} {fc:<15.6e} {cota_error:<15.6e} {t_act:<10.6f}")

        historial.append({
            'iter': i, 'a': a, 'b': b, 'fa': fa, 'fb': fb,
            'x': c, 'fx': fc, 'error': cota_error, 'tiempo': t_act
        })

        if cota_error < tol or abs(fc) < 1e-15:
            break

        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

    t_tot = time.perf_counter() - inicio
    print("=" * 90)
    print(f"RESULTADO INTERVALO MEDIO -> Raíz x = {c:.6f} | Iteraciones reales: {len(historial)} "
          f"(Teóricas: {n_teorico}) | Error: {cota_error:.6e} | Tiempo: {t_tot:.6f} s")

    metricas = {
        'metodo': 'Intervalo Medio (Bisección)',
        'raiz': c,
        'f_raiz': f(c),
        'iteraciones': len(historial),
        'iteraciones_teoricas': n_teorico,
        'error': cota_error,
        'tiempo': t_tot
    }
    return metricas, historial


# =============================================================================
# 2. MÉTODO DE INTERPOLACIÓN LINEAL (REGULA FALSI)
# =============================================================================
def ejecutar_interpolacion_lineal(f, a, b, tol=0.001, max_iter=100):
    """Ejecuta el Método de Interpolación Lineal (Regula Falsi)."""
    tol, max_iter = validar_parametros(tol, max_iter)
    if a > b:
        a, b = b, a

    fa, fb = f(a), f(b)
    if math.isnan(fa) or math.isnan(fb) or fa * fb > 0:
        print(f"\n[Error Bolzano] El intervalo [{a:.4f}, {b:.4f}] no presenta cambio de signo.")
        return None, []

    inicio = time.perf_counter()
    historial = []

    print("\n" + "=" * 90)
    print("--- MÉTODO DE INTERPOLACIÓN LINEAL (REGULA FALSI) ---")
    print(f"Intervalo: [{a:.4f}, {b:.4f}] | Tolerancia E < {tol}")
    print("=" * 90)
    print(f"{'i':<5} {'[a, b]':<24} {'x_i (Secante)':<15} {'f(x_i)':<15} {'Error':<15} {'Tiempo (s)':<10}")
    print("-" * 90)

    x_prev = a
    x = a
    error = abs(b - a)

    for i in range(1, max_iter + 1):
        denom = fb - fa
        x = (a + b) / 2.0 if abs(denom) < 1e-15 else b - (fb * (b - a)) / denom
        fx = f(x)

        if math.isnan(fx) or math.isinf(fx):
            x = (a + b) / 2.0
            fx = f(x)

        error = abs(b - a) if i == 1 else abs(x - x_prev)
        t_act = time.perf_counter() - inicio

        intervalo_str = f"[{a:.5f}, {b:.5f}]"
        print(f"{i:<5} {intervalo_str:<24} {x:<15.6f} {fx:<15.6e} {error:<15.6e} {t_act:<10.6f}")

        historial.append({
            'iter': i, 'a': a, 'b': b, 'fa': fa, 'fb': fb,
            'x': x, 'fx': fx, 'error': error, 'tiempo': t_act
        })

        if (error < tol and i > 1) or abs(fx) < 1e-15:
            break

        if fa * fx < 0:
            b, fb = x, fx
        else:
            a, fa = x, fx
        x_prev = x

    t_tot = time.perf_counter() - inicio
    print("=" * 90)
    print(f"RESULTADO INTERPOLACIÓN LINEAL -> Raíz x = {x:.6f} | Iteraciones: {len(historial)} "
          f"| Error: {error:.6e} | Tiempo: {t_tot:.6f} s")

    metricas = {
        'metodo': 'Interpolación Lineal (Regula Falsi)',
        'raiz': x,
        'f_raiz': f(x),
        'iteraciones': len(historial),
        'error': error,
        'tiempo': t_tot
    }
    return metricas, historial


# =============================================================================
# 3. MÉTODO DE NEWTON-RAPHSON Y CONDICIONES DE FOURIER
# =============================================================================
def analizar_condiciones_fourier(problema, a, b):
    """
    Evalúa y muestra en consola las 4 condiciones de convergencia de Fourier
    en el intervalo [a, b], determinando el punto de arranque x0 seguro.
    """
    f = problema.f
    df = getattr(problema, 'df', lambda val: derivada_numerica(f, val))
    d2f = getattr(problema, 'd2f', lambda val: segunda_derivada_numerica(f, val))

    if a > b:
        a, b = b, a

    fa, fb = f(a), f(b)
    dfa, dfb = df(a), df(b)
    d2fa, d2fb = d2f(a), d2f(b)

    # Muestreo interior para verificar invarianza de signos de f'(x) y f''(x)
    n_muestras = 30
    xs = [a + (b - a) * k / n_muestras for k in range(n_muestras + 1)]
    df_vals = [df(v) for v in xs]
    d2f_vals = [d2f(v) for v in xs]

    c1_bolzano = (fa * fb < 0)
    c2_monotonia = (all(v > 1e-12 for v in df_vals) or all(v < -1e-12 for v in df_vals))
    c3_concavidad = (all(v > 1e-12 for v in d2f_vals) or all(v < -1e-12 for v in d2f_vals))

    print("\n" + "=" * 92)
    print(f"ANÁLISIS DE CONDICIONES DE CONVERGENCIA DE FOURIER EN [{a:.4f}, {b:.4f}]")
    print("=" * 92)
    print(f"1. Condición de Bolzano [f(a)*f(b) < 0]:")
    print(f"   f({a:.4f}) = {fa:+.4e} | f({b:.4f}) = {fb:+.4e} -> {'CUMPLE' if c1_bolzano else 'NO CUMPLE'}")

    print(f"2. Monotonía [f'(x) != 0 y conserva signo en el intervalo]:")
    print(f"   f'({a:.4f}) = {dfa:+.4e} | f'({b:.4f}) = {dfb:+.4e} -> {'CUMPLE' if c2_monotonia else 'NO CUMPLE'}")

    print(f"3. Concavidad constante [f''(x) != 0 sin puntos de inflexión]:")
    print(f"   f''({a:.4f}) = {d2fa:+.4e} | f''({b:.4f}) = {d2fb:+.4e} -> {'CUMPLE' if c3_concavidad else 'NO CUMPLE'}")

    prod_a = fa * d2fa
    prod_b = fb * d2fb
    print(f"4. Selección del extremo inicial x0 tal que f(x0)*f''(x0) > 0:")
    print(f"   En a={a:.4f}: f(a)*f''(a) = {prod_a:+.4e} | En b={b:.4f}: f(b)*f''(b) = {prod_b:+.4e}")

    if prod_a > 0:
        x0_optimo = a
        c4_x0 = True
        print(f"   -> CUMPLE en extremo izquierdo: Se selecciona x0 = {x0_optimo:.6f}")
    elif prod_b > 0:
        x0_optimo = b
        c4_x0 = True
        print(f"   -> CUMPLE en extremo derecho: Se selecciona x0 = {x0_optimo:.6f}")
    else:
        x0_optimo = (a + b) / 2.0
        c4_x0 = False
        print(f"   -> Ningún extremo verifica estrictamente; se adopta punto medio x0 = {x0_optimo:.6f}")

    cumple_todo = c1_bolzano and c2_monotonia and c3_concavidad and c4_x0
    print("-" * 92)
    if cumple_todo:
        print("CONCLUSIÓN FOURIER: Se satisfacen las 4 hipótesis. Convergencia monótona garantizada.")
    else:
        print("CONCLUSIÓN FOURIER: Condiciones parciales; se procederá monitoreando la derivada.")
    print("=" * 92)

    return x0_optimo, cumple_todo


def ejecutar_newton_raphson(problema, a, b, tol=0.001, max_iter=100, x0_manual=None):
    """
    Aplica las condiciones de Fourier en [a, b] y ejecuta el Método de Newton-Raphson:
    x_{k+1} = x_k - f(x_k) / f'(x_k).
    """
    tol, max_iter = validar_parametros(tol, max_iter)
    f = problema.f
    df = getattr(problema, 'df', lambda val: derivada_numerica(f, val))

    x0_fourier, _ = analizar_condiciones_fourier(problema, a, b)
    x_actual = float(x0_manual) if x0_manual is not None else x0_fourier

    inicio = time.perf_counter()
    historial = []

    print("\n" + "=" * 92)
    print(f"--- MÉTODO DE NEWTON-RAPHSON (Arranque x0 = {x_actual:.6f} | Tolerancia E < {tol}) ---")
    print("=" * 92)
    print(f"{'i':<5} {'x_k':<15} {'x_{k+1}':<15} {'f(x_k)':<15} {'f\'(x_k)':<15} {'Error':<15} {'Tiempo (s)':<10}")
    print("-" * 92)

    error = abs(b - a)
    for i in range(1, max_iter + 1):
        fx = f(x_actual)
        dfx = df(x_actual)

        if abs(dfx) < 1e-14 or math.isnan(dfx):
            print(f"[Aviso] Derivada nula o indefinida en x = {x_actual:.6f}. Se detiene el proceso.")
            break

        x_sig = x_actual - (fx / dfx)
        fx_sig = f(x_sig)
        error = abs(x_sig - x_actual)
        t_act = time.perf_counter() - inicio

        print(f"{i:<5} {x_actual:<15.6f} {x_sig:<15.6f} {fx:<15.6e} {dfx:<15.6e} {error:<15.6e} {t_act:<10.6f}")

        historial.append({
            'iter': i,
            'a': min(a, b), 'b': max(a, b),
            'x_k': x_actual, 'fx_k': fx, 'dfx_k': dfx,
            'x': x_sig, 'fx': fx_sig,
            'error': error, 'tiempo': t_act
        })

        x_actual = x_sig
        if error < tol or abs(fx_sig) < 1e-15:
            break

    t_tot = time.perf_counter() - inicio
    print("=" * 92)
    print(f"RESULTADO NEWTON-RAPHSON -> Raíz x = {x_actual:.6f} | Iteraciones: {len(historial)} "
          f"| Error: {error:.6e} | Tiempo: {t_tot:.6f} s")

    metricas = {
        'metodo': 'Newton-Raphson (con Fourier)',
        'raiz': x_actual,
        'f_raiz': f(x_actual),
        'iteraciones': len(historial),
        'error': error,
        'tiempo': t_tot
    }
    return metricas, historial


# =============================================================================
# 4. MÉTODO DE ITERACIÓN (PUNTO FIJO SIMPLE Y ACELERACIÓN DE AITKEN)
# =============================================================================
def analizar_convergencia_punto_fijo(g, x0):
    """Evalúa la condición suficiente de convergencia |g'(x0)| < 1."""
    dg_val = derivada_numerica(g, x0)
    abs_dg = abs(dg_val)

    print("\n" + "=" * 92)
    print("ANÁLISIS DE CONVERGENCIA DE PUNTO FIJO (CONDICIÓN DE LIPSCHITZ)")
    print("=" * 92)
    print(f"Punto inicial x0 = {x0:.6f} | Derivada g'(x0) = {dg_val:+.6f} | |g'(x0)| = {abs_dg:.6f}")

    if abs_dg < 1.0:
        tipo = "Monótona unilateral (escalera)" if dg_val >= 0 else "Oscilante / Alternante (espiral)"
        print(f"-> CUMPLE (|g'(x0)| < 1): El esquema iterativo CONVERGE localmente ({tipo}).")
    else:
        print("-> ADVERTENCIA (|g'(x0)| >= 1): El punto fijo simple no es contractivo en x0.")
    print("=" * 92)
    return abs_dg < 1.0, abs_dg


def ejecutar_iteracion_simple(f, g, x0, tol=0.001, max_iter=100, mostrar_lipschitz=True):
    """Ejecuta el Método de Iteración Funcional Simple: x_{k+1} = g(x_k)."""
    tol, max_iter = validar_parametros(tol, max_iter)
    if mostrar_lipschitz:
        analizar_convergencia_punto_fijo(g, x0)

    inicio = time.perf_counter()
    historial = []

    print("\n" + "=" * 92)
    print(f"--- MÉTODO DE ITERACIÓN FUNCIONAL SIMPLE (Semilla x0 = {x0:.6f} | E < {tol}) ---")
    print("=" * 92)
    print(f"{'i':<5} {'x_{i-1}':<16} {'x_i = g(x_{i-1})':<18} {'f(x_i)':<16} {'Error':<15} {'Tiempo (s)':<10}")
    print("-" * 92)

    x_act = float(x0)
    error = 1.0

    for i in range(1, max_iter + 1):
        x_sig = g(x_act)
        fx_sig = f(x_sig)
        error = abs(x_sig - x_act)
        t_act = time.perf_counter() - inicio

        print(f"{i:<5} {x_act:<16.6f} {x_sig:<18.6f} {fx_sig:<16.6e} {error:<15.6e} {t_act:<10.6f}")

        historial.append({
            'iter': i,
            'x_prev': x_act,
            'x': x_sig,
            'fx': fx_sig,
            'error': error,
            'tiempo': t_act
        })

        x_act = x_sig
        if error < tol or abs(fx_sig) < 1e-15:
            break

    t_tot = time.perf_counter() - inicio
    print("=" * 92)
    print(f"RESULTADO ITERACIÓN SIMPLE -> Raíz x = {x_act:.6f} | Iteraciones: {len(historial)} "
          f"| Error: {error:.6e} | Tiempo: {t_tot:.6f} s")

    metricas = {
        'metodo': 'Iteración Simple (Punto Fijo)',
        'raiz': x_act,
        'f_raiz': f(x_act),
        'iteraciones': len(historial),
        'error': error,
        'tiempo': t_tot
    }
    return metricas, historial


def ejecutar_steffensen(f, g, x0, tol=0.001, max_ciclos=30, mostrar_lipschitz=True):
    """
    Ejecuta el Método de Iteración conjuntamente con la Aceleración Delta^2 de Aitken
    por ciclos con reinicio activo (Método de Steffensen).
    """
    tol, max_ciclos = validar_parametros(tol, max_ciclos)
    if mostrar_lipschitz:
        analizar_convergencia_punto_fijo(g, x0)

    inicio = time.perf_counter()
    historial = []

    print("\n" + "=" * 115)
    print(f"--- MÉTODO DE ITERACIÓN CON ACELERACIÓN Δ² DE AITKEN / STEFFENSEN (x1 = {x0:.6f} | E < {tol}) ---")
    print("=" * 115)
    print(f"{'Ciclo':<6} | {'Terna Utilizada':<18} | {'Punto Acelerado':<18} | {'f(x_acel)':<14} | {'Error Estimado':<14} | {'Tiempo (s)':<10}")
    print("-" * 115)

    semilla_ciclo = float(x0)
    p_aitken_prev = None
    raiz_final = semilla_ciclo
    error_final = 0.0
    k_contador = 1

    for ciclo in range(1, max_ciclos + 1):
        t_act = time.perf_counter() - inicio

        k_p0, p0 = k_contador, semilla_ciclo
        k_p1, p1 = k_contador + 1, g(p0)
        k_p2, p2 = k_contador + 2, g(p1)

        denominador = p2 - 2.0 * p1 + p0
        if abs(denominador) > 1e-14 and not math.isnan(denominador):
            p_aitken = p0 - ((p1 - p0) ** 2) / denominador
        else:
            p_aitken = p2

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
            error_str = f"{error_actual:.4e} (*)"

        terna_txt = f"(x{k_p0}, x{k_p1}, x{k_p2})"
        acel_txt = f"x{k_acelerado} = {p_aitken:.6f}"
        print(f"{ciclo:<6} | {terna_txt:<18} | {acel_txt:<18} | {fp_aitken:<14.4e} | {error_str:<14} | {t_act:<10.6f}")

        fp0_val = f(p0)
        historial.append({
            'ciclo': ciclo,
            'k_p0': k_p0, 'p0': p0, 'fp0': 0.0 if (math.isnan(fp0_val) or math.isinf(fp0_val)) else fp0_val,
            'k_p1': k_p1, 'p1': p1,
            'k_p2': k_p2, 'p2': p2,
            'k_acel': k_acelerado,
            'p_aitken': p_aitken,
            'fp_aitken': 0.0 if math.isnan(fp_aitken) else fp_aitken,
            'error': error_actual,
            'tiempo': t_act
        })

        if (p_aitken_prev is not None and error_actual < tol) or abs(fp_aitken) < 1e-15:
            raiz_final = p_aitken
            error_final = error_actual
            break

        # Verificar también mediante un paso de chequeo si ya cumplió la tolerancia en el 1° ciclo
        if abs(g(p_aitken) - p_aitken) < tol:
            raiz_final = p_aitken
            error_final = abs(g(p_aitken) - p_aitken)
            break

        p_aitken_prev = p_aitken
        semilla_ciclo = p_aitken
        k_contador = k_acelerado

    t_tot = time.perf_counter() - inicio
    if error_final == 0.0 and error_actual is not None:
        raiz_final = p_aitken
        error_final = error_actual

    print("=" * 115)
    print(f"RESULTADO AITKEN/STEFFENSEN -> Raíz x = {raiz_final:.6f} | Aplicaciones (Ciclos): {len(historial)} "
          f"| Error: {error_final:.6e} | Tiempo: {t_tot:.6f} s\n")

    metricas = {
        'metodo': 'Iteración + Aitken (Steffensen)',
        'raiz': raiz_final,
        'f_raiz': f(raiz_final),
        'iteraciones': len(historial),
        'evaluaciones_g': len(historial) * 2,
        'pasos_totales': k_contador,
        'error': error_final,
        'tiempo': t_tot
    }
    return metricas, historial