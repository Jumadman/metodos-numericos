import os
import time
from typing import Callable
import numpy as np
import matplotlib.pyplot as plt

EcuacionEDO = Callable[[float, float], float]


def metodo_euler(
    f: EcuacionEDO, x0: float, y0: float, xf: float, h: float, verbose: bool = True, var_x: str = "x", var_y: str = "y"
):
    """Método de Euler genérico para y' = f(x, y)."""
    pasos = int(round((xf - x0) / h))
    xs, ys = [x0], [y0]
    x, y = x0, y0

    if verbose:
        print(f"\n=== MÉTODO DE EULER (h = {h}) ===")
        print(f"i = 0 | {var_x}_0 = {x:.2f} | {var_y}_0 = {y:.6f} | {var_y}'_0 = {f(x, y):.6f}")

    for i in range(pasos):
        yp = f(x, y)
        y = y + yp * h
        x = round(x + h, 10)
        xs.append(x)
        ys.append(y)
        if verbose:
            print(f"i = {i+1} | {var_x}_{i+1} = {x:.2f} | {var_y}_{i+1} = {y:.6f} | {var_y}'_{i+1} = {f(x, y):.6f}")

    return np.array(xs), np.array(ys)


def metodo_euler_hasta_cero(
    f: EcuacionEDO, t0: float, y0: float, h: float, verbose: bool = True
):
    """Método de Euler con condición de parada cuando y <= 0 (vaciado/agotamiento)."""
    ts, ys = [t0], [y0]
    t, y = t0, y0
    i = 0

    if verbose:
        print(f"\n=== MÉTODO DE EULER HASTA VACIADO (h = {h}) ===")
        print(f"i = 0   | t_0   = {t:6.2f} min | y_0   = {y:.6f} m | y'_0   = {f(t, y):.6f}")

    while y > 0:
        yp = f(t, y)
        y_sig = y + yp * h
        t_sig = round(t + h, 10)
        i += 1

        if y_sig <= 0:
            t_cruce = t - y / yp
            ts.append(t_sig)
            ys.append(y_sig)
            if verbose:
                print(
                    f"i = {i:<3} | t_{i:<3} = {t_sig:6.2f} min | y_{i:<3} = {y_sig:.6f} m "
                    f"(Se vacía en este paso -> t_cruce ≈ {t_cruce:.4f} min)"
                )
            break

        t, y = t_sig, y_sig
        ts.append(t)
        ys.append(y)

        if verbose and (i <= 5 or i % 10 == 0):
            print(f"i = {i:<3} | t_{i:<3} = {t:6.2f} min | y_{i:<3} = {y:.6f} m | y'_{i:<3} = {f(t, y):.6f}")

    return np.array(ts), np.array(ys)


def metodo_euler_modificado(
    f: EcuacionEDO, x0: float, y0: float, xf: float, h: float, tol: float = 0.001, verbose: bool = True
):
    """Método Modificado de Euler (Predictor-Corrector iterativo)."""
    pasos = int(round((xf - x0) / h))
    xs, ys = [x0], [y0]
    x, y = x0, y0

    if verbose:
        print(f"\n=== MÉTODO MODIFICADO DE EULER (h = {h}, E < {tol}) ===")
        print(f"i = 0 | x_0 = {x:.2f} | y_0 = {y:.6f}")

    for i in range(pasos):
        x_sig = round(x + h, 10)
        yp_i = f(x, y)
        y_ant = y + yp_i * h

        if verbose:
            print(f"\n--- Intervalo [{x:.2f}, {x_sig:.2f}] (Calculando y_{i+1}) ---")
            print(f"  Predictor P(y_{i+1})   = {y_ant:.6f}")

        k = 1
        while True:
            yp_sig = f(x_sig, y_ant)
            y_corr = y + ((yp_i + yp_sig) / 2.0) * h
            error = abs(y_corr - y_ant)
            if verbose:
                etiqueta = f"C(y_{i+1})" if k == 1 else f"C^{k-1}(y_{i+1})"
                print(f"  Corrector {etiqueta:<10} = {y_corr:.6f} | Error = {error:.6f}")

            if error < tol:
                break
            y_ant = y_corr
            k += 1

        x, y = x_sig, y_corr
        xs.append(x)
        ys.append(y)

    return np.array(xs), np.array(ys)


def metodo_rk2(f: EcuacionEDO, x0: float, y0: float, xf: float, h: float, verbose: bool = True):
    """Método de Runge-Kutta de 2do Orden."""
    pasos = int(round((xf - x0) / h))
    xs, ys = [x0], [y0]
    x, y = x0, y0

    if verbose:
        print(f"\n=== MÉTODO DE RUNGE-KUTTA 2° ORDEN (h = {h}) ===")
        print(f"i = 0 | x_0 = {x:.2f} | y_0 = {y:.6f}")

    for i in range(pasos):
        k1 = h * f(x, y)
        k2 = h * f(x + h, y + k1)
        y = y + 0.5 * (k1 + k2)
        x = round(x + h, 10)
        xs.append(x)
        ys.append(y)

        if verbose:
            print(f"i = {i+1} | x_{i+1} = {x:.2f} | k1 = {k1:.6f}, k2 = {k2:.6f} | y_{i+1} = {y:.6f}")

    return np.array(xs), np.array(ys)


def metodo_rk4(f: EcuacionEDO, x0: float, y0: float, xf: float, h: float, verbose: bool = True):
    """Método de Runge-Kutta de 4to Orden."""
    pasos = int(round((xf - x0) / h))
    xs, ys = [x0], [y0]
    x, y = x0, y0

    if verbose:
        print(f"\n=== MÉTODO DE RUNGE-KUTTA 4° ORDEN (h = {h}) ===")
        print(f"i = 0 | x_0 = {x:.2f} | y_0 = {y:.6f}")

    for i in range(pasos):
        k1 = h * f(x, y)
        k2 = h * f(x + h / 2.0, y + k1 / 2.0)
        k3 = h * f(x + h / 2.0, y + k2 / 2.0)
        k4 = h * f(x + h, y + k3)
        y = y + (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        x = round(x + h, 10)
        xs.append(x)
        ys.append(y)

        if verbose:
            print(
                f"i = {i+1} | x_{i+1} = {x:.2f} | "
                f"k1={k1:.6f}, k2={k2:.6f}, k3={k3:.6f}, k4={k4:.6f} | y_{i+1} = {y:.6f}"
            )

    return np.array(xs), np.array(ys)


def metodo_milne(
    f: EcuacionEDO, x_init: np.ndarray, y_init: np.ndarray, xf: float, h: float, verbose: bool = True
):
    """Método Predictor-Corrector de Milne (requiere 4 puntos iniciales equidistantes)."""
    if len(x_init) < 4 or len(y_init) < 4:
        raise ValueError("El Método de Milne requiere al menos 4 puntos iniciales (i=0, 1, 2, 3).")

    xs = [float(x) for x in x_init]
    ys = [float(y) for y in y_init]
    yps = [f(x, y) for x, y in zip(xs, ys)]

    pasos = int(round((xf - xs[-1]) / h))

    if verbose:
        print(f"\n=== MÉTODO DE MILNE (h = {h}) ===")
        print("Puntos iniciales de arranque:")
        for idx, (x, y, yp) in enumerate(zip(xs, ys, yps)):
            print(f"  i = {idx} | x_{idx} = {x:.2f} | y_{idx} = {y:.6f} | y'_{idx} = {yp:.6f}")

    for _ in range(pasos):
        i = len(xs) - 1
        x_sig = round(xs[i] + h, 10)

        # Predictor: P(y_{i+1}) = y_{i-3} + (4/3)*h*(2*y'_i - y'_{i-1} + 2*y'_{i-2})
        y_pred = ys[i - 3] + (4.0 / 3.0) * h * (2.0 * yps[i] - yps[i - 1] + 2.0 * yps[i - 2])
        yp_pred = f(x_sig, y_pred)

        # Corrector: C(y_{i+1}) = y_{i-1} + (h/3)*(y'_{i-1} + 4*y'_i + P(y'_{i+1}))
        y_corr = ys[i - 1] + (h / 3.0) * (yps[i - 1] + 4.0 * yps[i] + yp_pred)
        yp_corr = f(x_sig, y_corr)

        if verbose:
            print(f"\n--- Paso i = {i} -> i+1 = {i+1} (x_{i+1} = {x_sig:.2f}) ---")
            print(f"  Predictor P(y_{i+1}) = {y_pred:.6f} | P(y'_{i+1}) = {yp_pred:.6f}")
            print(f"  Corrector C(y_{i+1}) = {y_corr:.6f} | C(y'_{i+1}) = {yp_corr:.6f}")

        xs.append(x_sig)
        ys.append(y_corr)
        yps.append(yp_corr)

    return np.array(xs), np.array(ys), np.array(yps)


def referencia_rk4(f: EcuacionEDO, x0: float, y0: float, xf: float, h_fino: float = 0.0001):
    """Calcula una solución de referencia muy precisa usando RK4 con paso fino."""
    return metodo_rk4(f, x0, y0, xf, h_fino, verbose=False)


def medir_tiempo(func: Callable, *args, **kwargs) -> float:
    """Ejecuta una función sin imprimir y devuelve el tiempo en microsegundos (µs)."""
    t0 = time.perf_counter()
    func(*args, verbose=False, **kwargs)
    return (time.perf_counter() - t0) * 1e6


def mostrar_y_limpiar_grafico(fig, ruta_imagen: str = "grafico_temp.png"):
    """Guarda temporalmente el gráfico, lo muestra y lo elimina al cerrar la ventana."""
    try:
        plt.tight_layout()
        plt.savefig(ruta_imagen, dpi=150)
        plt.show()
    finally:
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)