"""
Módulo: metodos_interpolacion.py
Descripción: Polinomio Interpolador de Lagrange con validación de dominio,
             desglose de numeradores/denominadores y medición de tiempo de CPU.
"""

import time
import math
import numpy as np


def validar_nodos_interpolacion(x_puntos, y_puntos):
    """
    Verifica que los vectores X e Y sean válidos, finitos y sin abscisas duplicadas.
    """
    if x_puntos is None or y_puntos is None:
        raise ValueError("No se han proporcionado datos de entrada.")
    if len(x_puntos) != len(y_puntos):
        raise ValueError(f"Dimensión incompatible: len(X)={len(x_puntos)} != len(Y)={len(y_puntos)}.")
    if len(x_puntos) < 2:
        raise ValueError("Se requieren como mínimo 2 puntos para interpolar.")

    x_arr = np.array(x_puntos, dtype=float)
    y_arr = np.array(y_puntos, dtype=float)

    if not (np.all(np.isfinite(x_arr)) and np.all(np.isfinite(y_arr))):
        raise ValueError("La tabla contiene valores indefinidos (NaN) o infinitos (Inf). Función no soluble en esos nodos.")

    # Verificar abscisas repetidas (causan división por cero en L_i)
    for i in range(len(x_arr)):
        for j in range(i + 1, len(x_arr)):
            if abs(x_arr[i] - x_arr[j]) < 1e-14:
                raise ValueError(f"Problema no soluble por Lagrange: Nodos X duplicados (x[{i}] = x[{j}] = {x_arr[i]}).")

    return x_arr.tolist(), y_arr.tolist()


def evaluar_lagrange_puro(x_puntos, y_puntos, x_eval):
    """
    Evalúa rápidamente P_n(x_eval) para trazado de curvas.
    Retorna NaN si ocurre desbordamiento numérico.
    """
    try:
        n = len(x_puntos)
        suma_total = 0.0
        for i in range(n):
            l_i = 1.0
            xi = x_puntos[i]
            for j in range(n):
                if j != i:
                    l_i *= (x_eval - x_puntos[j]) / (xi - x_puntos[j])
            suma_total += y_puntos[i] * l_i
        return float(suma_total) if math.isfinite(suma_total) else float('nan')
    except Exception:
        return float('nan')


def construir_polinomio_lagrange(x_puntos, y_puntos):
    """Construye los coeficientes algebraicos del polinomio P_n(x)."""
    n = len(x_puntos)
    polinomio_total = np.poly1d([0.0])

    for i in range(n):
        base_li = np.poly1d([1.0])
        for j in range(n):
            if j != i:
                denom = x_puntos[i] - x_puntos[j]
                base_li *= np.poly1d([1.0, -x_puntos[j]]) / denom
        polinomio_total += y_puntos[i] * base_li

    return polinomio_total


def formatear_polinomio(coeficientes):
    """Da formato algebraico legible al vector de coeficientes del polinomio."""
    grado = len(coeficientes) - 1
    finitos = [abs(c) for c in coeficientes if math.isfinite(c)]
    max_c = max(finitos, default=1.0)
    umbral = max_c * 1e-13

    terminos = []
    for idx, coef in enumerate(coeficientes):
        potencia = grado - idx
        if not math.isfinite(coef) or (abs(coef) <= umbral and len(coeficientes) > 1):
            continue

        signo = " + " if (coef >= 0 and terminos) else (" - " if coef < 0 else "")
        val = abs(coef)
        val_str = f"{val:.4e}" if (val < 1e-3 or val >= 1e5) else f"{val:.6g}"

        if potencia == 0:
            terminos.append(f"{signo}{val_str}")
        elif potencia == 1:
            terminos.append(f"{signo}{val_str}·x")
        else:
            terminos.append(f"{signo}{val_str}·x^{potencia}")

    return "".join(terminos) if terminos else "0"


def lagrange(x_puntos, y_puntos, x_eval):
    """
    Calcula el Polinomio Interpolador de Lagrange en x_eval registrando todos
    los cálculos intermedios (numeradores, denominadores, bases L_i, aportes y tiempo CPU).
    """
    x_val, y_val = validar_nodos_interpolacion(x_puntos, y_puntos)
    if not math.isfinite(x_eval):
        raise ValueError("El punto x* a evaluar no es un número finito válido.")

    inicio_cpu = time.perf_counter()
    n = len(x_val)

    # Determinar si los nodos son equidistantes para informarlo
    difs = np.diff(x_val)
    es_equidistante = bool(np.allclose(difs, difs[0], atol=1e-6))
    paso_h = float(difs[0]) if es_equidistante else None

    # Clasificar si es Interpolación o Extrapolación
    x_min, x_max = min(x_val), max(x_val)
    es_extrapolacion = (x_eval < x_min) or (x_eval > x_max)

    resultado = 0.0
    detalles_nodos = []
    bases_li = []

    for i in range(n):
        numerador = 1.0
        denominador = 1.0
        for j in range(n):
            if j != i:
                numerador *= (x_eval - x_val[j])
                denominador *= (x_val[i] - x_val[j])

        if abs(denominador) < 1e-15:
            raise ZeroDivisionError(f"Denominador nulo en la base L_{i}(x). Nodos demasiado próximos.")

        l_i = numerador / denominador
        aporte_i = y_val[i] * l_i
        resultado += aporte_i

        bases_li.append(l_i)
        detalles_nodos.append({
            'i': i,
            'x_i': x_val[i],
            'y_i': y_val[i],
            'numerador': numerador,
            'denominador': denominador,
            'L_i': l_i,
            'aporte': aporte_i
        })

    tiempo_cpu = time.perf_counter() - inicio_cpu

    # Construcción simbólica (solo si el grado es razonable para evitar inestabilidad en poly1d)
    if n <= 15:
        poli_obj = construir_polinomio_lagrange(x_val, y_val)
        poli_str = formatear_polinomio(poli_obj.coefficients)
    else:
        poli_obj = None
        poli_str = "[Grado > 14: Se omite expansión simbólica para evitar pérdida de precisión en punto flotante]"

    return {
        'metodo': 'Polinomio Interpolador de Lagrange',
        'grado': n - 1,
        'n_puntos': n,
        'equidistante': es_equidistante,
        'h': paso_h,
        'x_eval': float(x_eval),
        'es_extrapolacion': es_extrapolacion,
        'valor_interpolado': float(resultado),
        'coeficientes_L': bases_li,
        'suma_bases_L': float(sum(bases_li)),
        'detalles_nodos': detalles_nodos,
        'polinomio_str': poli_str,
        'tiempo_cpu': tiempo_cpu
    }