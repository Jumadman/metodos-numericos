"""
Módulo: visualizador.py
Descripción: Graficador universal e interactivo (Slideshow) para cualquier función
             y método (Bisección, Regula Falsi, Newton-Raphson, Iteración Simple y Steffensen).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def _muestrear_funcion_segura(func, x_min, x_max, n_puntos=600):
    """Evalúa una función en [x_min, x_max] filtrando asíntotas y divergencias."""
    x_vals = np.linspace(x_min, x_max, n_puntos)
    raw_y = []
    for v in x_vals:
        try:
            val = float(func(v))
            raw_y.append(np.nan if (np.isinf(val) or np.isnan(val)) else val)
        except Exception:
            raw_y.append(np.nan)

    arr_y = np.array(raw_y, dtype=float)
    finitos = arr_y[np.isfinite(arr_y)]
    if len(finitos) > 10:
        p5, p95 = np.percentile(finitos, [5, 95])
        iqr = max(p95 - p5, 1.0)
        arr_y[(arr_y > p95 + 4.0 * iqr) | (arr_y < p5 - 4.0 * iqr)] = np.nan

    return x_vals, arr_y.tolist()


def graficar_inspeccion_inicial(problema, raices_destacadas=None):
    """Inspección gráfica estática de la función (Equivalente al fplot pedido en la Guía 3)."""
    x_min, x_max = getattr(problema, 'dominio_sugerido', (-6.0, 6.0))
    x_vals, y_vals = _muestrear_funcion_segura(problema.f, x_min, x_max, 1000)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(x_vals, y_vals, color='#1f77b4', linewidth=2.2, label=getattr(problema, 'nombre', 'f(x)'))
    ax.axhline(0, color='red', linestyle='--', linewidth=1.3, label='Eje y = 0 (Raíces)')
    ax.axvline(0, color='black', linestyle=':', linewidth=0.9)

    if raices_destacadas:
        for idx, r in enumerate(raices_destacadas, 1):
            ax.plot(r, 0, 'ro', markersize=8, label=f'Raíz {idx}: x ≈ {r:.4f}')

    ax.set_xlim(x_min, x_max)
    ax.set_title(f"Evaluación Gráfica de Raíces - {getattr(problema, 'nombre', 'f(x)')}",
                 fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel(getattr(problema, 'etiqueta_x', 'x'), fontsize=10)
    ax.set_ylabel('f(x)', fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='best', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.show()


class VisualizadorInteractivo:
    """Slideshow paso a paso interactivo compatible con todos los métodos y modelos."""
    def __init__(self, problema, historial, hallazgos_tanteo=None, modo='interpolacion', dominio_panoramico=None):
        self.problema = problema
        self.f = problema.f
        self.g = getattr(problema, 'g', lambda x: x)
        self.historial = historial or []
        self.hallazgos = hallazgos_tanteo or []
        self.modo = modo
        self.dominio_panoramico = dominio_panoramico or getattr(problema, 'dominio_sugerido', (-6.0, 6.5))
        self.nombre_curva = getattr(problema, 'nombre', 'f(x)')
        self.etiqueta_x = getattr(problema, 'etiqueta_x', 'x')
        self.index = 0

        # Panel doble para métodos de Punto Fijo (Iteración Simple y Steffensen/Aitken)
        if self.modo in ('steffensen', 'aitken', 'iteracion_simple'):
            self.fig, (self.ax, self.ax_cobweb) = plt.subplots(1, 2, figsize=(14, 6))
            plt.subplots_adjust(bottom=0.18, wspace=0.28)
            ax_prev = plt.axes([0.58, 0.04, 0.14, 0.06])
            ax_next = plt.axes([0.74, 0.04, 0.14, 0.06])
        else:
            self.fig, self.ax = plt.subplots(figsize=(11, 6))
            self.ax_cobweb = None
            plt.subplots_adjust(bottom=0.18)
            ax_prev = plt.axes([0.54, 0.04, 0.16, 0.06])
            ax_next = plt.axes([0.72, 0.04, 0.16, 0.06])

        # Guardar referencias de botones en self para que no sean recolectados por el Garbage Collector
        self.btn_prev = Button(ax_prev, '< Anterior', color='#EAECEE', hovercolor='#D5D8DC')
        self.btn_prev.on_clicked(self.prev_step)

        self.btn_next = Button(ax_next, 'Siguiente >', color='#EAECEE', hovercolor='#D5D8DC')
        self.btn_next.on_clicked(self.next_step)

        self.dibujar_paso()

    def dibujar_paso(self):
        self.ax.clear()
        if self.ax_cobweb is not None:
            self.ax_cobweb.clear()

        if not self.historial:
            return

        paso = self.historial[self.index]

        # 1. Definición de ejes (Panorámica en paso 0, Zoom Dinámico en los siguientes)
        if self.index == 0:
            x_min, x_max = self.dominio_panoramico
            x_vals, y_vals = _muestrear_funcion_segura(self.f, x_min, x_max, 1000)
            y_validos = [y for y in y_vals if not np.isnan(y)] or [-10.0, 10.0]

            self.ax.set_xlim(x_min, x_max)
            rango_y = max(max(y_validos) - min(y_validos), 1e-3)
            margen_y = rango_y * 0.10
            self.ax.set_ylim(min(y_validos) - margen_y, max(y_validos) + margen_y)

            if getattr(self.problema, 'tiene_restriccion_fisica', False):
                v_min = getattr(self.problema, 'val_min', 0.0)
                v_max = getattr(self.problema, 'H_max', None)
                if v_min is not None and v_min > x_min:
                    self.ax.axvspan(x_min, v_min, color='gray', alpha=0.12, label=f'Zona Inválida (x < {v_min})')
                if v_min is not None and v_max is not None:
                    self.ax.axvspan(v_min, v_max, color='green', alpha=0.10, label=f'Rango Físico [{v_min}, {v_max}]')

            for a_t, b_t, valido, motivo in self.hallazgos:
                if not valido:
                    self.ax.axvspan(a_t, b_t, color='red', alpha=0.22, label=f'Descarte: {motivo} [{a_t:.1f}, {b_t:.1f}]')

            modo_vista = "VISTA PANORÁMICA"
        else:
            if self.modo in ('biseccion', 'interpolacion'):
                puntos_x = [paso['a'], paso['b'], paso['x']]
                puntos_y_extra = [paso['fa'], paso['fb'], paso['fx'], 0.0]
            elif self.modo == 'newton':
                puntos_x = [paso['x_k'], paso['x']]
                puntos_y_extra = [paso['fx_k'], paso['fx'], 0.0]
            elif self.modo == 'iteracion_simple':
                puntos_x = [paso['x_prev'], paso['x']]
                puntos_y_extra = [self.f(paso['x_prev']), paso['fx'], 0.0]
            else:
                puntos_x = [paso['p0'], paso['p1'], paso['p2'], paso['p_aitken']]
                puntos_y_extra = [paso['fp0'], paso['fp_aitken'], 0.0]

            min_x, max_x = min(puntos_x), max(puntos_x)
            margen_x = max((max_x - min_x) * 0.40, 0.005)
            zoom_x_min, zoom_x_max = min_x - margen_x, max_x + margen_x

            x_vals, y_vals = _muestrear_funcion_segura(self.f, zoom_x_min, zoom_x_max, 500)
            y_extra_limpios = [y for y in puntos_y_extra if y is not None and not np.isnan(y) and not np.isinf(y)]
            y_validos = [y for y in y_vals if not np.isnan(y)] + y_extra_limpios
            if not y_validos:
                y_validos = [-1.0, 1.0]

            min_y, max_y = min(y_validos), max(y_validos)
            margen_y = max((max_y - min_y) * 0.22, 0.05)

            self.ax.set_xlim(zoom_x_min, zoom_x_max)
            self.ax.set_ylim(min_y - margen_y, max(max_y + margen_y, min_y + 0.1))
            modo_vista = "ZOOM DINÁMICO"

        # Trazado de la curva f(x) y ejes
        self.ax.plot(x_vals, y_vals, label=self.nombre_curva, color='#1f77b4', linewidth=2.2)
        self.ax.axhline(0, color='black', linestyle='-', linewidth=1.1, alpha=0.9)
        self.ax.axvline(0, color='black', linestyle=':', linewidth=0.9)

        # 2. Representación geométrica según el método
        if self.modo == 'biseccion':
            a, b, c_k = paso['a'], paso['b'], paso['x']
            fa, fb, fc_k = paso['fa'], paso['fb'], paso['fx']
            self.ax.axvspan(min(a, b), max(a, b), color='cyan', alpha=0.22, label=f'Intervalo [{a:.4f}, {b:.4f}]')
            self.ax.plot([a, b], [fa, fb], 'bo', markersize=7, label='Extremos [a, b]')
            self.ax.axvline(c_k, color='darkorange', linestyle='--', linewidth=1.6, label=f'Punto Medio $c_{{{paso["iter"]}}}$')
            self.ax.plot(c_k, 0, 'go', markersize=9, label=f'Raíz $c = {c_k:.5f}$')
            self.ax.vlines(c_k, 0, fc_k, color='green', linestyle=':', linewidth=1.6)
            self.ax.set_title(f'[{modo_vista}] Intervalo Medio - Paso {paso["iter"]}/{len(self.historial)} | c = {c_k:.5f}', fontsize=10, fontweight='bold')

        elif self.modo == 'interpolacion':
            a, b, x_k = paso['a'], paso['b'], paso['x']
            fa, fb, fx_k = paso['fa'], paso['fb'], paso['fx']
            self.ax.axvspan(min(a, b), max(a, b), color='yellow', alpha=0.28, label=f'Intervalo [{a:.4f}, {b:.4f}]')
            self.ax.plot([a, b], [fa, fb], 'ro', markersize=7, label='Extremos [a, b]')
            self.ax.plot([a, b], [fa, fb], color='red', linestyle='--', linewidth=2.0, label='Recta Secante')
            self.ax.vlines([a, b], 0, [fa, fb], color='red', linestyle=':', alpha=0.4)
            self.ax.plot(x_k, 0, 'go', markersize=9, label=f'Raíz $x = {x_k:.5f}$')
            self.ax.vlines(x_k, 0, fx_k, color='green', linestyle=':', linewidth=1.5)
            self.ax.set_title(f'[{modo_vista}] Interpolación Lineal - Paso {paso["iter"]}/{len(self.historial)} | x = {x_k:.5f}', fontsize=10, fontweight='bold')

        elif self.modo == 'newton':
            xk, fxk, dfxk = paso['x_k'], paso['fx_k'], paso['dfx_k']
            x_sig, fx_sig = paso['x'], paso['fx']
            self.ax.plot(xk, fxk, 'ro', markersize=8, label=f'Punto Tangencia ({xk:.3f}, {fxk:.2f})')
            self.ax.vlines(xk, 0, fxk, color='gray', linestyle=':', linewidth=1.3)
            self.ax.plot([xk, x_sig], [fxk, 0], color='darkorange', linestyle='--', linewidth=2.2, label=f'Tangente ($f\'={dfxk:.2f}$)')
            self.ax.plot(x_sig, 0, 'go', markersize=9, label=f'Corte $x_{{{paso["iter"]}}} = {x_sig:.5f}$')
            self.ax.vlines(x_sig, 0, fx_sig, color='green', linestyle=':', linewidth=1.5)
            self.ax.set_title(f'[{modo_vista}] Newton-Raphson - Paso {paso["iter"]}/{len(self.historial)} | x = {x_sig:.5f}', fontsize=10, fontweight='bold')

        elif self.modo == 'iteracion_simple':
            x_prev, x_act, fx_act = paso['x_prev'], paso['x'], paso['fx']
            self.ax.plot(x_prev, 0, 'mo', markersize=8, label=f'Anterior $x_{{{paso["iter"]-1}}} = {x_prev:.4f}$')
            self.ax.plot(x_act, 0, 'go', markersize=9, label=f'Actual $x_{{{paso["iter"]}}} = {x_act:.5f}$')
            self.ax.vlines(x_act, 0, fx_act, color='green', linestyle='--', linewidth=1.5)
            self.ax.set_title(f'[{modo_vista}] Iteración Simple - Paso {paso["iter"]}/{len(self.historial)}', fontsize=10, fontweight='bold')

            # Gráfico de y = g(x) e y = x juntas en el mismo panel (Requisito Guía 3)
            todos_x = [h['x_prev'] for h in self.historial] + [h['x'] for h in self.historial]
            ancho = max(todos_x) - min(todos_x)
            m_cob = max(ancho * 0.35, 0.5)
            c_min, c_max = min(todos_x) - m_cob, max(todos_x) + m_cob

            cx_vals, cg_vals = _muestrear_funcion_segura(self.g, c_min, c_max, 400)
            self.ax_cobweb.plot(cx_vals, cg_vals, label='Curva $y = g(x)$', color='#d95f02', linewidth=2.2)
            self.ax_cobweb.plot([c_min, c_max], [c_min, c_max], label='Recta $y = x$', color='#7570b3', linestyle='--', linewidth=1.8)

            escalera_x, escalera_y = [], []
            for idx_h in range(self.index + 1):
                xp, xa = self.historial[idx_h]['x_prev'], self.historial[idx_h]['x']
                escalera_x.extend([xp, xp, xa])
                escalera_y.extend([xp, xa, xa])
            self.ax_cobweb.plot(escalera_x, escalera_y, 'm-o', linewidth=1.3, markersize=4, alpha=0.8, label='Trayectoria $x_{k+1}=g(x_k)$')
            self.ax_cobweb.plot(x_act, x_act, 'go', markersize=9, label=f'Punto $x_{{{paso["iter"]}}} = {x_act:.4f}$')
            self.ax_cobweb.set_xlim(c_min, c_max)
            self.ax_cobweb.set_ylim(c_min, c_max)
            self.ax_cobweb.set_title('Espacio de Fase (y = g(x) vs y = x)', fontsize=10, fontweight='bold')
            self.ax_cobweb.set_xlabel('x')
            self.ax_cobweb.set_ylabel('y')
            self.ax_cobweb.grid(True, linestyle=':', alpha=0.6)
            self.ax_cobweb.legend(loc='upper left', fontsize=8.0)

        else:
            p0, p1, p2 = paso['p0'], paso['p1'], paso['p2']
            p_aitken, fp_aitken = paso['p_aitken'], paso['fp_aitken']
            k0, k1, k2, k_acel = paso['k_p0'], paso['k_p1'], paso['k_p2'], paso['k_acel']

            self.ax.axvspan(min(p0, p1, p2), max(p0, p1, p2), color='magenta', alpha=0.10, label='Rango Terna')
            self.ax.plot(p0, 0, 'mo', markersize=8, label=f'Semilla $x_{{{k0}}} = {p0:.4f}$')
            self.ax.plot(p_aitken, 0, 's', color='#2ca02c', markersize=10, markeredgecolor='black', label=f'Aitken $x_{{{k_acel}}} = {p_aitken:.5f}$')
            self.ax.vlines(p_aitken, 0, fp_aitken, color='#2ca02c', linestyle='--', linewidth=1.5)
            self.ax.set_title(f'[{modo_vista}] Steffensen - Ciclo {paso["ciclo"]}/{len(self.historial)}: (x{k0}, x{k1}, x{k2}) -> x{k_acel}', fontsize=10, fontweight='bold')

            ancho_terna = max(p0, p1, p2, p_aitken) - min(p0, p1, p2, p_aitken)
            m_cob = max(ancho_terna * 0.40, 0.05)
            c_min = min(p0, p1, p2, p_aitken) - m_cob
            c_max = max(p0, p1, p2, p_aitken) + m_cob

            cx_vals, cg_vals = _muestrear_funcion_segura(self.g, c_min, c_max, 400)
            self.ax_cobweb.plot(cx_vals, cg_vals, label='Curva $y = g(x)$', color='#d95f02', linewidth=2.2)
            self.ax_cobweb.plot([c_min, c_max], [c_min, c_max], label='Recta $y = x$', color='#7570b3', linestyle='--', linewidth=1.8)

            cobweb_x = [p0, p0, p1, p1, p2]
            cobweb_y = [p0, p1, p1, p2, p2]
            self.ax_cobweb.plot(cobweb_x, cobweb_y, color='magenta', linestyle='-', linewidth=1.4, marker='o', markersize=4, label='Terna')
            self.ax_cobweb.plot(p_aitken, p_aitken, 's', color='#2ca02c', markersize=10, markeredgecolor='black', label=f'Aitken $x_{{{k_acel}}} = {p_aitken:.4f}$')
            self.ax_cobweb.annotate('', xy=(p_aitken, p_aitken), xytext=(p2, p2), arrowprops=dict(arrowstyle="->", color='#2ca02c', lw=1.8, linestyle=':'))
            self.ax_cobweb.set_xlim(c_min, c_max)
            self.ax_cobweb.set_ylim(c_min, c_max)
            self.ax_cobweb.set_title('Espacio de Fase (y = g(x) vs y = x)', fontsize=10, fontweight='bold')
            self.ax_cobweb.set_xlabel('x')
            self.ax_cobweb.set_ylabel('y')
            self.ax_cobweb.grid(True, linestyle=':', alpha=0.6)
            self.ax_cobweb.legend(loc='upper left', fontsize=8.0)

        self.ax.set_xlabel(self.etiqueta_x)
        self.ax.set_ylabel('f(x)')
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.legend(loc='upper left', fontsize=8.5)
        self.fig.canvas.draw_idle()

    def next_step(self, event):
        if self.index < len(self.historial) - 1:
            self.index += 1
            self.dibujar_paso()

    def prev_step(self, event):
        if self.index > 0:
            self.index -= 1
            self.dibujar_paso()


def mostrar_visualizador(problema, historial, hallazgos_tanteo=None, modo='interpolacion', dominio_panoramico=None):
    """Función de entrada limpia para abrir el visualizador sin errores ni hilos problemáticos."""
    visor = VisualizadorInteractivo(
        problema=problema,
        historial=historial,
        hallazgos_tanteo=hallazgos_tanteo,
        modo=modo,
        dominio_panoramico=dominio_panoramico
    )
    plt.show()
    return visor


# Alias de compatibilidad por si algún script viejo todavía lo llama
VisualizadorInteractivoManning = VisualizadorInteractivo