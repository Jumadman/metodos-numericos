import math
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import Tanteo

# Datos del problema
R = 3.0   # Radio en metros
V = 30.0  # Volumen en m3

def f(x):
    """Ecuación del volumen del tanque esférico: f(x) = 0"""
    return math.pi * (x**2) * ((3.0 * R - x) / 3.0) - V

def g(x):
    """Función contractiva de Punto Fijo: x = g(x)"""
    denominador = math.pi * (3.0 - (x / 3.0))
    if denominador <= 0:
        return 0.0
    return math.sqrt(30.0 / denominador)

def metodo_iteracion_aitken(x0, tol=0.001, max_iter=50):
    """
    Método de Iteración de Punto Fijo acelerado con la fórmula Delta^2 de Aitken.
    Imprime en consola la comparativa entre la sucesión simple y la acelerada.
    """
    inicio = time.perf_counter()

    print("\n" + "=" * 98)
    print("--- MÉTODO DE ITERACIÓN DE PUNTO FIJO CON ACELERACIÓN DE AITKEN (Δ²) ---")
    print("=" * 98)
    print(f"{'i':<4} {'x_i':<14} {'g(x_i)':<14} {'x_aitken (x̂)':<16} {'f(x̂)':<14} {'Error':<14} {'Tiempo (s)':<12}")
    print("-" * 98)

    puntos_x = [float(x0)]
    x_hat_prev = None
    raiz_final = x0
    error_final = None
    iteraciones_totales = 0

    for i in range(1, max_iter + 1):
        tiempo_actual = time.perf_counter() - inicio
        x_actual = puntos_x[-1]
        x_siguiente = g(x_actual)
        puntos_x.append(x_siguiente)

        x_hat = None
        fx_hat_str = "---"
        x_hat_str = "---"
        error_str = "---"

        # Aitken requiere al menos 3 valores consecutivos (x_{k-2}, x_{k-1}, x_k)
        if len(puntos_x) >= 3:
            p0 = puntos_x[-3]
            p1 = puntos_x[-2]
            p2 = puntos_x[-1]

            denominador = p2 - 2 * p1 + p0
            if abs(denominador) > 1e-12:
                x_hat = p0 - ((p1 - p0) ** 2) / denominador
            else:
                x_hat = p2

            fx_hat = f(x_hat)
            error_actual = abs(x_hat - x_hat_prev) if x_hat_prev is not None else abs(x_hat - p2)
            
            x_hat_str = f"{x_hat:.6f}"
            fx_hat_str = f"{fx_hat:.4e}"
            error_str = f"{error_actual:.4e}"

            print(f"{i:<4} {x_actual:<14.6f} {x_siguiente:<14.6f} {x_hat_str:<16} {fx_hat_str:<14} {error_str:<14} {tiempo_actual:<12.6f}")

            if error_actual < tol and x_hat_prev is not None:
                raiz_final = x_hat
                error_final = error_actual
                iteraciones_totales = i
                break

            x_hat_prev = x_hat
        else:
            print(f"{i:<4} {x_actual:<14.6f} {x_siguiente:<14.6f} {x_hat_str:<16} {fx_hat_str:<14} {error_str:<14} {tiempo_actual:<12.6f}")

    tiempo_total = time.perf_counter() - inicio
    if error_final is None:
        raiz_final = puntos_x[-1]
        error_final = abs(puntos_x[-1] - puntos_x[-2])
        iteraciones_totales = max_iter

    print("=" * 98)
    print("RESULTADOS FINALES:")
    print(f"- Profundidad calculada (x) : {raiz_final:.6f} metros")
    print(f"- Iteraciones requeridas    : {iteraciones_totales}")
    print(f"- Error final aproximado    : {error_final:.6e}")
    print(f"- Tiempo de ejecución total : {tiempo_total:.6f} segundos\n")

class IteracionAitkenInteractive:
    """
    Visualización Interactiva para Iteración con aceleración de Aitken.
    - Paso 1: Panorámica completa de -6 a 8 con rango físico del tanque.
    - Pasos siguientes: Zoom dinámico sobre la raíz, comparando x_k vs el salto de Aitken.
    """
    def __init__(self, x0_init, tol=0.001, max_iter=20):
        self.x0_init = float(x0_init)
        self.tol = tol
        self.max_iter = max_iter
        
        self.pasos = []
        self.precalcular_pasos()
        self.index = 0

        self.fig, self.ax = plt.subplots(figsize=(11, 6))
        plt.subplots_adjust(bottom=0.18)

        ax_next = plt.axes([0.72, 0.04, 0.16, 0.06])
        self.btn_next = Button(ax_next, 'Siguiente >')
        self.btn_next.on_clicked(self.next_step)

        ax_prev = plt.axes([0.54, 0.04, 0.16, 0.06])
        self.btn_prev = Button(ax_prev, '< Anterior')
        self.btn_prev.on_clicked(self.prev_step)

        self.dibujar_paso()

    def precalcular_pasos(self):
        puntos = [self.x0_init]
        x_hat_prev = None

        for i in range(1, self.max_iter + 1):
            xk = puntos[-1]
            xk_sig = g(xk)
            puntos.append(xk_sig)

            x_hat = None
            fx_hat = None
            error = None

            if len(puntos) >= 3:
                p0, p1, p2 = puntos[-3], puntos[-2], puntos[-1]
                den = p2 - 2 * p1 + p0
                x_hat = p0 - ((p1 - p0) ** 2) / den if abs(den) > 1e-12 else p2
                fx_hat = f(x_hat)
                error = abs(x_hat - x_hat_prev) if x_hat_prev is not None else abs(x_hat - p2)
                x_hat_prev = x_hat

            self.pasos.append({
                'iter': i,
                'xk': xk,
                'fxk': f(xk),
                'xk_sig': xk_sig,
                'x_hat': x_hat,
                'fx_hat': fx_hat,
                'error': error
            })

            if error is not None and error < self.tol and i >= 3:
                break

    def dibujar_paso(self):
        self.ax.clear()
        paso = self.pasos[self.index]
        xk = paso['xk']
        fxk = paso['fxk']
        xk_sig = paso['xk_sig']
        x_hat = paso['x_hat']

        # 1. Escala: Panorámica en el primer paso, zoom progresivo en los siguientes
        if self.index == 0:
            zoom_x_min, zoom_x_max = -6.0, 8.0
            x_vals = np.linspace(zoom_x_min, zoom_x_max, 1000)
            y_vals = [f(v) for v in x_vals]
            
            self.ax.set_xlim(-6.0, 8.0)
            
            # Margen aditivo: garantiza espacio libre arriba y abajo sin recortar negativos
            rango_y = max(y_vals) - min(y_vals)
            margen_y = rango_y * 0.08
            self.ax.set_ylim(min(y_vals) - margen_y, max(y_vals) + margen_y)
            
            self.ax.axvspan(0, 6, color='green', alpha=0.1, label='Rango Físico del Tanque (0m a 6m)')
            modo_vista = "VISTA PANORÁMICA"
        else:
            puntos_x = [xk, xk_sig]
            if x_hat is not None:
                puntos_x.append(x_hat)

            min_x, max_x = min(puntos_x), max(puntos_x)
            margen_x = max((max_x - min_x) * 0.4, 0.005)
            zoom_x_min, zoom_x_max = min_x - margen_x, max_x + margen_x

            x_vals = np.linspace(zoom_x_min, zoom_x_max, 500)
            y_vals = [f(v) for v in x_vals]

            todos_y = y_vals + [fxk, 0]
            if paso['fx_hat'] is not None:
                todos_y.append(paso['fx_hat'])
            min_y, max_y = min(todos_y), max(todos_y)
            margen_y = max((max_y - min_y) * 0.25, 0.05)

            self.ax.set_xlim(zoom_x_min, zoom_x_max)
            self.ax.set_ylim(min_y - margen_y, max_y + margen_y)
            modo_vista = "ZOOM PROGRESIVO"

        # 2. Curva f(x) y ejes coordenados
        self.ax.plot(x_vals, y_vals, label=r'$f(x) = \pi x^2 \frac{9-x}{3} - 30$', color='#1f77b4', linewidth=2.5)
        self.ax.axhline(0, color='black', linestyle='-', linewidth=1.2, alpha=0.9)
        self.ax.axvline(0, color='gray', linestyle=':', linewidth=0.8)

        # 3. Punto actual de la iteración simple
        self.ax.plot(xk, 0, 'mo', markersize=8, label=f'Iteración $x_{{{paso["iter"]}}} = {xk:.4f}$')
        self.ax.vlines(xk, 0, fxk, color='magenta', linestyle=':', linewidth=1.3)

        # 4. Punto acelerado con Aitken
        if x_hat is not None:
            self.ax.plot(x_hat, 0, 's', color='#2ca02c', markersize=10, markeredgecolor='black', label=f'Aitken $\\hat{{x}} = {x_hat:.5f}$')
            fx_hat = paso['fx_hat']
            self.ax.vlines(x_hat, 0, fx_hat, color='#2ca02c', linestyle='--', linewidth=1.5)

        # 5. Títulos y leyendas
        aitken_info = f" | Aitken: {x_hat:.5f}" if x_hat is not None else ""
        err_info = f" | Err: {paso['error']:.2e}" if paso['error'] is not None else ""
        
        self.ax.set_title(
            f'[{modo_vista}] Paso {paso["iter"]}/{len(self.pasos)} | x = {xk:.5f}{aitken_info}{err_info}',
            fontsize=10, fontweight='bold', pad=12
        )
        self.ax.set_xlabel('Profundidad x (metros)', fontsize=11)
        self.ax.set_ylabel('f(x)', fontsize=11)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)

        self.fig.canvas.draw_idle()

    def next_step(self, event):
        if self.index < len(self.pasos) - 1:
            self.index += 1
            self.dibujar_paso()

    def prev_step(self, event):
        if self.index > 0:
            self.index -= 1
            self.dibujar_paso()

def ejecutar_consola():
    time.sleep(0.5)
    # Llamada al módulo externo Tanteo.py
    try:
        intervalos = Tanteo.metodo_tanteo_detallado(f, x_inicio=-6.0, x_fin=8.0)
    except TypeError:
        intervalos = Tanteo.metodo_tanteo_detallado(x_inicio=-6.0, x_fin=8.0)

    # Identificar la raíz admisible dentro del tanque físico (0 a 6m)
    x0_seleccionado = 2.0
    for a, b in intervalos:
        if a >= 0 and b <= 6:
            x0_seleccionado = (a + b) / 2.0
            break

    print(f"\nSemilla inicial seleccionada a partir del tanteo: x0 = {x0_seleccionado:.4f}")
    metodo_iteracion_aitken(x0=x0_seleccionado, tol=0.001)

if __name__ == "__main__":
    hilo_consola = threading.Thread(target=ejecutar_consola)
    hilo_consola.start()

    # Inicia la interfaz con la semilla inicial del tanteo en el tanque
    app = IteracionAitkenInteractive(x0_init=2.0, tol=0.001)
    try:
        plt.show()
    except KeyboardInterrupt:
        print("\nVentana gráfica cerrada.")

    hilo_consola.join()