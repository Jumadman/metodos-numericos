"""
Módulo: metodos_integracion.py
Descripción: Regla de los Trapecios (Compuesta y Generalizada) y Reglas de Simpson
             con desglose completo de parámetros (h, E, P, I), subintervalos y tiempos de CPU.
"""

import time
import numpy as np


def validar_datos_integracion(x, y):
    """
    Valida que los vectores X e Y sean finitos, tengan al menos 2 puntos
    y que las abscisas X sean estrictamente crecientes.
    """
    if x is None or y is None:
        raise ValueError("No hay datos cargados para integrar.")
    if len(x) != len(y):
        raise ValueError(f"Longitud desigual: len(X)={len(x)} vs len(Y)={len(y)}.")
    if len(x) < 2:
        raise ValueError("Se necesitan al menos 2 nodos (1 subintervalo) para integrar.")

    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)

    if not (np.all(np.isfinite(x_arr)) and np.all(np.isfinite(y_arr))):
        raise ValueError("Integral no soluble numéricamente: Existen valores NaN o Infinitos (asíntota/fuera de dominio).")

    difs = np.diff(x_arr)
    if np.any(difs <= 1e-15):
        raise ValueError("Los nodos X deben ser estrictamente crecientes y sin valores repetidos.")

    equidistante = bool(np.allclose(difs, difs[0], atol=1e-6))
    h = float(difs[0]) if equidistante else None
    return x_arr, y_arr, equidistante, h


# =============================================================================
# 1. REGLA DE LOS TRAPECIOS COMPUESTA (PASO CONSTANTE h)
# =============================================================================
def trapecios_compuesto(x, y):
    """
    Fórmula de los Trapecios Compuesta según Hoja de Fórmulas:
        A ≈ (h / 2) * (E + 2P + 2I)
    Retorna todos los cálculos intermedios y el tiempo de ejecución.
    """
    x_arr, y_arr, equidist, h = validar_datos_integracion(x, y)
    if not equidist:
        raise ValueError("La fórmula compuesta (h/2)*(E + 2P + 2I) requiere paso h constante.")

    inicio_cpu = time.perf_counter()
    n = len(y_arr) - 1

    # Desglose de ordenadas según la cátedra
    y_extremos = [float(y_arr[0]), float(y_arr[-1])]
    y_impares = y_arr[1:-1:2].tolist()  # y_1, y_3, y_5...
    y_pares = y_arr[2:-1:2].tolist()    # y_2, y_4, y_6...

    E = float(y_arr[0] + y_arr[-1])
    I = float(np.sum(y_arr[1:-1:2]))
    P = float(np.sum(y_arr[2:-1:2]))

    suma_ponderada = E + 2.0 * P + 2.0 * I
    area_total = (h / 2.0) * suma_ponderada

    # Detalle de cada trapecio individual
    subintervalos = []
    for i in range(n):
        base_prom = 0.5 * (y_arr[i] + y_arr[i + 1])
        area_i = h * base_prom
        subintervalos.append({
            'i': i + 1,
            'a_i': float(x_arr[i]),
            'b_i': float(x_arr[i + 1]),
            'h_i': h,
            'y_izq': float(y_arr[i]),
            'y_der': float(y_arr[i + 1]),
            'altura_media': float(base_prom),
            'area_i': float(area_i)
        })

    tiempo_cpu = time.perf_counter() - inicio_cpu

    return {
        'metodo': 'Regla de los Trapecios Compuesta',
        'equidistante': True,
        'a': float(x_arr[0]),
        'b': float(x_arr[-1]),
        'h': h,
        'intervalos_n': n,
        'E': E,
        'P': P,
        'I': I,
        'dos_P': 2.0 * P,
        'dos_I': 2.0 * I,
        'y_impares': y_impares,
        'y_pares': y_pares,
        'suma_ponderada': float(suma_ponderada),
        'subintervalos': subintervalos,
        'integral': float(area_total),
        'tiempo_cpu': tiempo_cpu
    }


# =============================================================================
# 2. REGLA DE LOS TRAPECIOS GENERALIZADA (PASO VARIABLE h_i)
# =============================================================================
def trapecios_generalizado(x, y):
    """
    Calcula la integral por suma de trapecios cuando los nodos no son equidistantes:
        A ≈ sum_{i=0}^{n-1} (h_i / 2) * (y_i + y_{i+1})
    """
    x_arr, y_arr, _, _ = validar_datos_integracion(x, y)
    inicio_cpu = time.perf_counter()
    n = len(x_arr) - 1

    subintervalos = []
    area_total = 0.0
    pasos_hi = []

    for i in range(n):
        h_i = float(x_arr[i + 1] - x_arr[i])
        pasos_hi.append(h_i)
        base_prom = 0.5 * float(y_arr[i] + y_arr[i + 1])
        area_i = h_i * base_prom
        area_total += area_i
        subintervalos.append({
            'i': i + 1,
            'a_i': float(x_arr[i]),
            'b_i': float(x_arr[i + 1]),
            'h_i': h_i,
            'y_izq': float(y_arr[i]),
            'y_der': float(y_arr[i + 1]),
            'altura_media': base_prom,
            'area_i': area_i
        })

    tiempo_cpu = time.perf_counter() - inicio_cpu

    return {
        'metodo': 'Regla de los Trapecios Generalizada (Paso Variable)',
        'equidistante': False,
        'a': float(x_arr[0]),
        'b': float(x_arr[-1]),
        'h': None,
        'h_min': min(pasos_hi),
        'h_max': max(pasos_hi),
        'intervalos_n': n,
        'subintervalos': subintervalos,
        'integral': float(area_total),
        'tiempo_cpu': tiempo_cpu
    }


# =============================================================================
# 3. REGLAS DE SIMPSON (PARA CONTRASTE EN CONSOLA Y PRÁCTICOS)
# =============================================================================
def simpson_1_3_compuesto(x, y):
    """Fórmula de Simpson 1/3: A ≈ (h/3)*(E + 2P + 4I). Exige n par."""
    x_arr, y_arr, equidist, h = validar_datos_integracion(x, y)
    n = len(x_arr) - 1
    if not equidist or n % 2 != 0:
        raise ValueError(f"Simpson 1/3 compuesto requiere paso constante y n PAR (actual n={n}).")

    inicio_cpu = time.perf_counter()
    E = float(y_arr[0] + y_arr[-1])
    I = float(np.sum(y_arr[1:-1:2]))
    P = float(np.sum(y_arr[2:-1:2]))
    area = (h / 3.0) * (E + 2.0 * P + 4.0 * I)
    tiempo_cpu = time.perf_counter() - inicio_cpu

    return {
        'metodo': 'Simpson 1/3 Compuesto',
        'h': h, 'intervalos_n': n, 'E': E, 'P': P, 'I': I,
        'integral': float(area), 'tiempo_cpu': tiempo_cpu
    }