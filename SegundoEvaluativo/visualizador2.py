"""
Módulo: visualizador_tp2.py
Descripción: Generador de gráficos con protección frente a asíntotas o valores
             fuera de dominio para Lagrange y Regla de los Trapecios.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from metodos_interpolacion import evaluar_lagrange_puro


def _evaluar_funcion_segura(func, xs):
    """Evalúa una función de usuario sobre una grilla filtrando singularidades."""
    ys = []
    for xi in xs:
        try:
            val = float(func(float(xi)))
            if not math.isfinite(val) or abs(val) > 1e10:
                ys.append(np.nan)
            else:
                ys.append(val)
        except Exception:
            ys.append(np.nan)
    return ys


def graficar_lagrange(x_nodos, y_nodos, puntos_evaluados=None, func_exacta=None, titulo=""):
    """Grafica el polinomio interpolante P_n(x), los nodos de entrada y los puntos evaluados."""
    x_min, x_max = min(x_nodos), max(x_nodos)
    if puntos_evaluados:
        x_min = min(x_min, min(p[0] for p in puntos_evaluados))
        x_max = max(x_max, max(p[0] for p in puntos_evaluados))

    margen = max((x_max - x_min) * 0.08, 0.15)
    x_curva = np.linspace(x_min - margen, x_max + margen, 400)
    y_curva = [evaluar_lagrange_puro(x_nodos, y_nodos, float(xi)) for xi in x_curva]

    fig, ax = plt.subplots(figsize=(10, 5.5))

    if func_exacta is not None:
        y_real = _evaluar_funcion_segura(func_exacta, x_curva)
        ax.plot(x_curva, y_real, color='#2ca02c', linestyle='--', linewidth=1.8,
                alpha=0.85, label='Función exacta $f(x)$')

    ax.plot(x_curva, y_curva, color='#1f77b4', linewidth=2.3,
            label=f'Polinomio de Lagrange $P_{{{len(x_nodos)-1}}}(x)$')
    ax.scatter(x_nodos, y_nodos, color='#d62728', s=65, zorder=5,
               label='Nodos de tabla $(x_i, y_i)$')

    y_finitos = [y for y in y_curva if math.isfinite(y)]
    base_y = min(min(y_finitos, default=0.0), 0.0)

    if puntos_evaluados:
        for idx, (xe, ye) in enumerate(puntos_evaluados, 1):
            ax.scatter([xe], [ye], color='#ff7f0e', marker='D', s=85, zorder=6,
                       edgecolor='black', label=f'Evaluado {idx}: $P({xe:.4g}) = {ye:.6g}$')
            ax.vlines(xe, base_y, ye, color='#ff7f0e', linestyle=':', linewidth=1.4)

    ax.axhline(0, color='black', linewidth=0.9, alpha=0.6)
    ax.set_title(f"Interpolación Polinómica de Lagrange {titulo}".strip(),
                 fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Variable independiente x", fontsize=10)
    ax.set_ylabel("y = P(x)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.65)
    ax.legend(loc='best', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.show()


def graficar_trapecios(x_nodos, y_nodos, area_total, func_exacta=None, titulo=""):
    """Grafica los trapecios rectángulos bajo cada subintervalo [x_i, x_{i+1}]."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    x_suave = np.linspace(min(x_nodos), max(x_nodos), 350)
    if func_exacta is not None:
        y_suave = _evaluar_funcion_segura(func_exacta, x_suave)
        ax.plot(x_suave, y_suave, color='#1f77b4', linewidth=2.0, label='Función exacta $f(x)$')
    elif len(x_nodos) <= 12:
        y_suave = [evaluar_lagrange_puro(x_nodos, y_nodos, float(xi)) for xi in x_suave]
        ax.plot(x_suave, y_suave, color='#1f77b4', linestyle='--', linewidth=1.6,
                alpha=0.8, label='Curva interpolante de referencia')

    for i in range(len(x_nodos) - 1):
        xs = [x_nodos[i], x_nodos[i], x_nodos[i + 1], x_nodos[i + 1]]
        ys = [0, y_nodos[i], y_nodos[i + 1], 0]
        etiqueta = f'Área Trapecios ($n = {len(x_nodos)-1}$)' if i == 0 else None
        ax.fill(xs, ys, color='#ff7f0e', alpha=0.28, edgecolor='#d95f02', linewidth=1.5, label=etiqueta)

    ax.plot(x_nodos, y_nodos, 'o-', color='#d95f02', linewidth=1.8, markersize=6,
            label='Cuerdas secantes (Grado 1)')
    ax.axhline(0, color='black', linewidth=1.0)

    ax.set_title(f"Regla de los Trapecios — Integral Aproximada ≈ {area_total:.6f} {titulo}".strip(),
                 fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("x", fontsize=10)
    ax.set_ylabel("f(x)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.65)
    ax.legend(loc='best', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.show()


def graficar_convergencia_trapecios(pasos_h, errores, func_exacta, a, b):
    """Panel doble: geometría de Trapecios (izquierda) y pendiente O(h^2) log-log (derecha)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    x_demo = np.linspace(a, b, 5)
    y_demo = _evaluar_funcion_segura(func_exacta, x_demo)
    x_fino = np.linspace(a, b, 300)
    y_fino = _evaluar_funcion_segura(func_exacta, x_fino)

    ax1.plot(x_fino, y_fino, color='#1f77b4', linewidth=2.0, label='$f(x) = \\sin(x)$')
    for i in range(4):
        xs = [x_demo[i], x_demo[i], x_demo[i + 1], x_demo[i + 1]]
        ys = [0, y_demo[i], y_demo[i + 1], 0]
        ax1.fill(xs, ys, color='#ff7f0e', alpha=0.28, edgecolor='#d95f02', linewidth=1.4,
                 label='Trapecios ($n=4$)' if i == 0 else None)
    ax1.plot(x_demo, y_demo, 'o-', color='#d95f02', markersize=5)
    ax1.set_title("Discretización Geométrica ($n = 4$)", fontsize=10, fontweight='bold')
    ax1.set_xlabel("x")
    ax1.set_ylabel("f(x)")
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', fontsize=8.5)

    ax2.loglog(pasos_h, errores, 'o-', color='#2ca02c', linewidth=2.2, markersize=7,
               label='Error real $|I - I_{\\mathrm{trap}}|$')
    ref_h2 = [errores[0] * (h / pasos_h[0]) ** 2 for h in pasos_h]
    ax2.loglog(pasos_h, ref_h2, '--', color='#7570b3', linewidth=1.6,
               label='Pendiente teórica $O(h^2)$')
    ax2.set_title("Decaimiento Cuadrático del Error $O(h^2)$", fontsize=10, fontweight='bold')
    ax2.set_xlabel("Paso h (escala log)")
    ax2.set_ylabel("Error Absoluto (escala log)")
    ax2.grid(True, which='both', linestyle=':', alpha=0.6)
    ax2.legend(loc='lower right', fontsize=8.5)

    plt.tight_layout()
    plt.show()