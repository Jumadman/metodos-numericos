import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class VisualizadorInteractivoManning:
    """
    Slideshow interactivo para Interpolación Lineal y Steffensen.
    Para Steffensen incluye vista combinada: f(x) = 0 y Diagrama de Telaraña y = g(x) vs y = x.
    """
    def __init__(self, problema, historial, hallazgos_tanteo, modo='interpolacion', dominio_panoramico=(-6.0, 6.5)):
        self.problema = problema
        self.f = problema.f
        self.g = problema.g
        self.historial = historial
        self.hallazgos = hallazgos_tanteo
        self.modo = modo
        self.dominio_panoramico = dominio_panoramico
        self.index = 0

        # Crear lienzo: panel simple para interpolación, panel doble para Steffensen
        if self.modo == 'interpolacion':
            self.fig, self.ax = plt.subplots(figsize=(11, 6))
            self.ax_cobweb = None
            plt.subplots_adjust(bottom=0.18)
            ax_prev = plt.axes([0.54, 0.04, 0.16, 0.06])
            ax_next = plt.axes([0.72, 0.04, 0.16, 0.06])
        else:
            self.fig, (self.ax, self.ax_cobweb) = plt.subplots(1, 2, figsize=(14, 6))
            plt.subplots_adjust(bottom=0.18, wspace=0.28)
            ax_prev = plt.axes([0.58, 0.04, 0.14, 0.06])
            ax_next = plt.axes([0.74, 0.04, 0.14, 0.06])

        self.btn_prev = Button(ax_prev, '< Anterior')
        self.btn_prev.on_clicked(self.prev_step)
        self.btn_next = Button(ax_next, 'Siguiente >')
        self.btn_next.on_clicked(self.next_step)

        self.dibujar_paso()

    def _evaluar_curva_segura(self, func, x_min, x_max, n_puntos=500):
        x_vals = np.linspace(x_min, x_max, n_puntos)
        y_vals = []
        for v in x_vals:
            val = func(v)
            if abs(val) > 200.0 or np.isinf(val) or np.isnan(val):
                y_vals.append(np.nan)
            else:
                y_vals.append(val)
        return x_vals, y_vals

    def dibujar_paso(self):
        self.ax.clear()
        if self.ax_cobweb is not None:
            self.ax_cobweb.clear()

        paso = self.historial[self.index]

        # =====================================================================
        # PANEL 1: ECUACIÓN DEL CANAL f(x) = 0
        # =====================================================================
        if self.index == 0:
            x_min, x_max = self.dominio_panoramico
            x_vals, y_vals = self._evaluar_curva_segura(self.f, x_min, x_max, 1000)
            y_validos = [y for y in y_vals if not np.isnan(y)]

            self.ax.set_xlim(x_min, x_max)
            rango_y = max(y_validos) - min(y_validos)
            margen_y = rango_y * 0.10
            self.ax.set_ylim(min(y_validos) - margen_y, max(y_validos) + margen_y)

            self.ax.axvspan(x_min, 0, color='gray', alpha=0.12, label='Zona Descartada (x < 0)')
            self.ax.axvspan(0, self.problema.H_max, color='green', alpha=0.12, label=f'Rango Físico (0 a {self.problema.H_max}m)')

            for a_t, b_t, valido, motivo in self.hallazgos:
                if not valido:
                    self.ax.axvspan(a_t, b_t, color='red', alpha=0.25, label=f'Descarte: {motivo} [{a_t:.1f}, {b_t:.1f}]')

            modo_vista = "PANORÁMICA"
        else:
            if self.modo == 'interpolacion':
                puntos_x = [paso['a'], paso['b'], paso['x']]
                puntos_y_extra = [paso['fa'], paso['fb'], paso['fx'], 0.0]
            else:
                puntos_x = [paso['p0'], paso['p1'], paso['p2']]
                puntos_y_extra = [paso['fp0'], 0.0]
                if paso['p_aitken'] is not None:
                    puntos_x.append(paso['p_aitken'])
                    puntos_y_extra.append(paso['fp_aitken'])

            min_x, max_x = min(puntos_x), max(puntos_x)
            margen_x = max((max_x - min_x) * 0.35, 0.01)
            zoom_x_min, zoom_x_max = min_x - margen_x, max_x + margen_x

            x_vals, y_vals = self._evaluar_curva_segura(self.f, zoom_x_min, zoom_x_max, 500)
            y_validos = [y for y in y_vals if not np.isnan(y)] + puntos_y_extra

            min_y, max_y = min(y_validos), max(y_validos)
            margen_y = max((max_y - min_y) * 0.20, 0.05)

            self.ax.set_xlim(zoom_x_min, zoom_x_max)
            self.ax.set_ylim(min_y - margen_y, max_y + margen_y)
            modo_vista = "ZOOM DE CONVERGENCIA"

        self.ax.plot(x_vals, y_vals, label=r'Manning $f(x)$', color='#1f77b4', linewidth=2.2)
        self.ax.axhline(0, color='black', linestyle='-', linewidth=1.1, alpha=0.9)
        self.ax.axvline(0, color='black', linestyle=':', linewidth=0.9)

        if self.modo == 'interpolacion':
            a, b, x_k = paso['a'], paso['b'], paso['x']
            fa, fb, fx_k = paso['fa'], paso['fb'], paso['fx']

            self.ax.axvspan(min(a, b), max(a, b), color='yellow', alpha=0.3, label=f'Intervalo [{a:.4f}, {b:.4f}]')
            self.ax.plot([a, b], [fa, fb], 'ro', markersize=7)
            self.ax.plot([a, b], [fa, fb], color='red', linestyle='--', linewidth=2, label='Secante')
            self.ax.vlines([a, b], 0, [fa, fb], color='red', linestyle=':', alpha=0.4)
            self.ax.plot(x_k, 0, 'go', markersize=9, label=f'Raíz $x = {x_k:.5f}$')
            self.ax.vlines(x_k, 0, fx_k, color='green', linestyle=':', linewidth=1.5)

            self.ax.set_title(f'[{modo_vista}] Regula Falsi - Paso {paso["iter"]}/{len(self.historial)} | Err: {paso["error"]:.2e}', fontsize=10, fontweight='bold')
            self.ax.set_xlabel('Tirante x (m)')
            self.ax.set_ylabel('f(x)')
            self.ax.grid(True, linestyle=':', alpha=0.6)
            self.ax.legend(loc='upper left', fontsize=8.5)
        else:
            p0, p1, p2 = paso['p0'], paso['p1'], paso['p2']
            p_aitken, fp_aitken = paso['p_aitken'], paso['fp_aitken']
            k0, k1, k2, k_acel = paso['k_p0'], paso['k_p1'], paso['k_p2'], paso['k_acel']

            # Panel 1: Curva f(x) = 0
            self.ax.axvspan(min(p0, p1, p2), max(p0, p1, p2), color='magenta', alpha=0.10, label='Rango de la Terna')
            self.ax.plot(p0, 0, 'mo', markersize=8, label=f'Semilla $x_{{{k0}}} = {p0:.4f}$')
            self.ax.plot(p_aitken, 0, 's', color='#2ca02c', markersize=10, markeredgecolor='black', label=f'Acelerado $x_{{{k_acel}}} = {p_aitken:.5f}$')
            self.ax.vlines(p_aitken, 0, fp_aitken, color='#2ca02c', linestyle='--', linewidth=1.5)

            err_txt = f" | Err: {paso['error']:.2e}" if paso['error'] is not None else ""
            self.ax.set_title(f'[{modo_vista}] Steffensen - Ciclo {paso["ciclo"]}/{len(self.historial)}: (x{k0}, x{k1}, x{k2}) -> x{k_acel}{err_txt}', fontsize=10, fontweight='bold')
            self.ax.set_xlabel('Tirante x (m)')
            self.ax.set_ylabel('f(x)')
            self.ax.grid(True, linestyle=':', alpha=0.6)
            self.ax.legend(loc='upper left', fontsize=8.5)

            # Panel 2: Diagrama de Telaraña (Cobweb)
            ancho_terna = max(p0, p1, p2, p_aitken) - min(p0, p1, p2, p_aitken)
            m_cob = max(ancho_terna * 0.40, 0.05)
            c_min = min(p0, p1, p2, p_aitken) - m_cob
            c_max = max(p0, p1, p2, p_aitken) + m_cob

            cx_vals, cg_vals = self._evaluar_curva_segura(self.g, c_min, c_max, 400)
            self.ax_cobweb.plot(cx_vals, cg_vals, label='Curva $y = g(x)$', color='#d95f02', linewidth=2.0)
            self.ax_cobweb.plot([c_min, c_max], [c_min, c_max], label='Diagonal $y = x$', color='#7570b3', linestyle='--', linewidth=1.8)

            cobweb_x = [p0, p0, p1, p1, p2]
            cobweb_y = [p0, p1, p1, p2, p2]
            self.ax_cobweb.plot(cobweb_x, cobweb_y, color='magenta', linestyle='-', linewidth=1.4, marker='o', markersize=4, label=f'Terna ($x_{{{k0}}} \\to x_{{{k1}}} \\to x_{{{k2}}}$)')

            self.ax_cobweb.plot(p_aitken, p_aitken, 's', color='#2ca02c', markersize=10, markeredgecolor='black', label=f'Salto Steffensen $x_{{{k_acel}}} = {p_aitken:.4f}$')
            self.ax_cobweb.annotate('', xy=(p_aitken, p_aitken), xytext=(p2, p2),
                                    arrowprops=dict(arrowstyle="->", color='#2ca02c', lw=1.8, linestyle=':'))

            self.ax_cobweb.set_xlim(c_min, c_max)
            self.ax_cobweb.set_ylim(c_min, c_max)
            self.ax_cobweb.set_title(f'Espacio de Fase: Terna (x{k0}, x{k1}, x{k2}) y Salto a x{k_acel}', fontsize=10, fontweight='bold')
            self.ax_cobweb.set_xlabel('x')
            self.ax_cobweb.set_ylabel('y')
            self.ax_cobweb.grid(True, linestyle=':', alpha=0.6)
            self.ax_cobweb.legend(loc='upper left', fontsize=8.0)

        self.fig.canvas.draw_idle()

    def next_step(self, event):
        if self.index < len(self.historial) - 1:
            self.index += 1
            self.dibujar_paso()

    def prev_step(self, event):
        if self.index > 0:
            self.index -= 1
            self.dibujar_paso()