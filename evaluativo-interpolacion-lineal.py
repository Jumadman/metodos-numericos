import math
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np

# Datos del problema
R = 3.0  # Radio en metros
V = 30.0 # Volumen en m3

def f(x):
    """Ecuación del volumen del tanque esférico: f(x) = 0"""
    return math.pi * (x**2) * ((3*R - x) / 3.0) - V

def metodo_tanteo_detallado(x_inicio=-6.0, x_fin=8.0):
    """
    1. Método de Tanteo evaluado desde x = -6 a x = 8
    e identifica todos los cambios de signo f(x_k) * f(x_k+1) <= 0.
    """
    print("\n" + "="*80)
    print("--- MÉTODOS DE TANTEO: EVALUACIÓN PASO A PASO (PUNTOS Y CAMBIOS DE SIGNO) ---")
    print("="*80)
    
    try:
        step = float(input("Ingrese el valor del incremento (paso Δx, ej. 0.5 o 1.0): "))
    except (ValueError, EOFError):
        step = 1.0
        print("Entrada no válida o por defecto, se usará paso Δx = 1.0")

    print(f"\nEvaluando intervalo [{x_inicio}, {x_fin}] con paso Δx = {step}:")
    print(f"{'i':<5} {'x_k':<10} {'f(x_k)':<15} {'Signo':<10} {'Estado / Cambio de Signo':<30}")
    print("-" * 80)

    intervalos_raiz = []
    x_curr = x_inicio
    i = 1
    
    while x_curr < x_fin:
        x_next = x_curr + step
        fx_curr = f(x_curr)
        fx_next = f(x_next)
        
        signo_curr = "+" if fx_curr > 0 else "-"
        
        if fx_curr * fx_next <= 0:
            intervalos_raiz.append((x_curr, x_next))
            estado = f"CAMBIO DE SIGNO -> Raíz en [{x_curr:.2f}, {x_next:.2f}]"
        else:
            estado = "Sin cambio de signo"
            
        print(f"{i:<5} {x_curr:<10.2f} {fx_curr:<15.4f} {signo_curr:<10} {estado}")
        
        x_curr = x_next
        i += 1

    fx_final = f(x_fin)
    signo_final = "+" if fx_final > 0 else "-"
    print(f"{i:<5} {x_fin:<10.2f} {fx_final:<15.4f} {signo_final:<10} Fin del intervalo")
    print("-" * 80)
    
    print("\nRESUMEN DE INTERVALOS DETECTADOS POR TANTEO:")
    for idx, (a, b) in enumerate(intervalos_raiz, 1):
        es_fisico = " ( VÁLIDO FÍSICAMENTE EN EL TANQUE )" if (a >= 0 and b <= 6) else " ( Raíz Matemática fuera del tanque )"
        print(f" Raíz {idx}: Intervalo [{a:.2f}, {b:.2f}]{es_fisico}")
        
    return intervalos_raiz

def metodo_interpolacion_lineal(a, b, tol=0.001, max_iter=100):
    """
    2. Método de Interpolación Lineal (Regula Falsi): Imprime la grilla de salida
    sin barras '|'.
    """
    inicio = time.perf_counter()
    
    fa = f(a)
    fb = f(b)
    
    if fa * fb >= 0:
        print("\nEl intervalo no cumple con el cambio de signo f(a)*f(b) < 0.")
        return

    print("\n" + "="*80)
    print("--- MÉTODOS DE INTERPOLACIÓN LINEAL (GRILLA DE RESULTADOS) ---")
    print("="*80)
    print(f"{'i':<5} {'[a,b]':<22} {'f(x)':<16} {'error':<16} {'tiempo de ejecucion (s)':<22}")
    print("-" * 80)
    
    x_prev = a
    for i in range(1, max_iter + 1):
        x = b - (fb * (b - a)) / (fb - fa)
        fx = f(x)
        
        error = abs(b - a) if i == 1 else abs(x - x_prev)
        tiempo_actual = time.perf_counter() - inicio
        intervalo_str = f"[{a:.5f}, {b:.5f}]"
        
        print(f"{i:<5} {intervalo_str:<22} {fx:<16.6e} {error:<16.6e} {tiempo_actual:<22.6f}")
        
        if error < tol:
            break
            
        if fa * fx < 0:
            b = x
            fb = fx
        else:
            a = x
            fa = fx
            
        x_prev = x

    tiempo_total = time.perf_counter() - inicio
    print("=" * 80)
    print("RESULTADOS FINALES:")
    print(f"- Profundidad aproximada (x) : {x:.6f} metros")
    print(f"- Cantidad de iteraciones (i): {i}")
    print(f"- Error final                : {error:.6e}")
    print(f"- Tiempo de ejecución total  : {tiempo_total:.6f} segundos\n")

class InterpolacionLinealInteractiveDeMinus6a8:
    """
    3. Visualización Gráfica Interactiva con Matplotlib:
    Dominio expandido de -6 a 8 con botonera para avanzar/retroceder.
    """
    def __init__(self, a_init, b_init, tol=0.001, max_iter=20):
        self.a_init = a_init
        self.b_init = b_init
        self.tol = tol
        self.max_iter = max_iter
        
        self.pasos = []
        self.precalcular_pasos()
        
        self.index = 0
        
        self.fig, self.ax = plt.subplots(figsize=(11, 6))
        plt.subplots_adjust(bottom=0.18)
        
        # Botón "Siguiente >"
        ax_next = plt.axes([0.72, 0.04, 0.16, 0.06])
        self.btn_next = Button(ax_next, 'Siguiente >')
        self.btn_next.on_clicked(self.next_step)
        
        # Botón "< Anterior"
        ax_prev = plt.axes([0.54, 0.04, 0.16, 0.06])
        self.btn_prev = Button(ax_prev, '< Anterior')
        self.btn_prev.on_clicked(self.prev_step)
        
        self.dibujar_paso()
        
    def precalcular_pasos(self):
        a, b = float(self.a_init), float(self.b_init)
        fa, fb = f(a), f(b)
        x_prev = a
        
        for i in range(1, self.max_iter + 1):
            x = b - (fb * (b - a)) / (fb - fa)
            fx = f(x)
            
            error = abs(b - a) if i == 1 else abs(x - x_prev)
            
            self.pasos.append({
                'iter': i,
                'a': a,
                'b': b,
                'fa': fa,
                'fb': fb,
                'x': x,
                'fx': fx,
                'error': error
            })
            
            if error < self.tol:
                break
                
            if fa * fx < 0:
                b, fb = x, fx
            else:
                a, fa = x, fx
            x_prev = x
            
    def dibujar_paso(self):
        self.ax.clear()
        paso = self.pasos[self.index]
        a, b, x_k = paso['a'], paso['b'], paso['x']
        fa, fb, fx_k = paso['fa'], paso['fb'], paso['fx']
        x_hat = paso.get('x_hat', None)
        
        # -------------------------------------------------------------
        # 1. GESTIÓN DE ESCALA Y ZOOM (PANORÁMICA vs ZOOM DINÁMICO)
        # -------------------------------------------------------------
        if self.index == 0:
            # PRIMER FILMINA: Vista panorámica completa del tanteo (-6 a 8)
            zoom_x_min, zoom_x_max = -6.0, 8.0
            x_vals = np.linspace(zoom_x_min, zoom_x_max, 1000)
            y_vals = [f(v) for v in x_vals]
            
            # Límites fijos en Y para apreciar el comportamiento cúbico general
            self.ax.set_xlim(-6.0, 8.0)
            self.ax.set_ylim(min(y_vals) * 0.9, max(y_vals) * 0.9)
            
            # Sombreado del rango físico completo del tanque esférico (0 a 6m)
            self.ax.axvspan(0, 6, color='green', alpha=0.1, label='Rango Físico del Tanque (0m a 6m)')
            
            modo_vista = "VISTA PANORÁMICA (Tanteo)"
        else:
            # FILMINAS SIGUIENTES: Zoom progresivo cerrado alrededor de la raíz
            puntos_en_x = [a, b, x_k]
            if x_hat is not None:
                puntos_en_x.append(x_hat)
                
            min_x, max_x = min(puntos_en_x), max(puntos_en_x)
            ancho_x = max_x - min_x
            
            # Margen proporcional para encuadre nítido
            margen_x = max(ancho_x * 0.25, 0.005)
            zoom_x_min = min_x - margen_x
            zoom_x_max = max_x + margen_x

            x_vals = np.linspace(zoom_x_min, zoom_x_max, 500)
            y_vals = [f(v) for v in x_vals]
            
            # Límites adaptativos en Y para asegurar que el cero y los puntos sean visibles
            todos_y = y_vals + [fa, fb, fx_k, 0]
            if x_hat is not None:
                todos_y.append(paso.get('fx_hat', f(x_hat)))
            min_y, max_y = min(todos_y), max(todos_y)
            rango_y = max_y - min_y
            margen_y = max(rango_y * 0.15, 0.05)
            
            self.ax.set_xlim(zoom_x_min, zoom_x_max)
            self.ax.set_ylim(min_y - margen_y, max_y + margen_y)
            
            modo_vista = "ZOOM PROGRESIVO"

        # -------------------------------------------------------------
        # 2. RENDERIZADO DE LA CURVA Y ELEMENTOS GEOMÉTRICOS
        # -------------------------------------------------------------
        self.ax.plot(x_vals, y_vals, label=r'$f(x) = \pi x^2 \frac{9-x}{3} - 30$', color='#1f77b4', linewidth=2.5)
        self.ax.axhline(0, color='black', linestyle='-', linewidth=1.2, alpha=0.9)
        self.ax.axvline(0, color='gray', linestyle=':', linewidth=0.8)

        # Intervalo actual delimitado por el método
        self.ax.axvspan(min(a, b), max(a, b), color='orange', alpha=0.3, label=f'Intervalo [{a:.4f}, {b:.4f}]')
        
        # Puntos de los extremos
        self.ax.plot([a, b], [fa, fb], 'ro', markersize=7, label='Extremos [a, b]')
        self.ax.vlines([a, b], 0, [fa, fb], color='red', linestyle=':', alpha=0.5)

        # Punto medio calculado por Bisección
        self.ax.plot(x_k, 0, 'mo', markersize=8, label=f'Bisección $x_{{{paso["iter"]}}} = {x_k:.4f}$')
        self.ax.vlines(x_k, 0, fx_k, color='magenta', linestyle='--', linewidth=1.3)
        
        # Punto extrapolado de Aitken (si está disponible a partir del paso 3)
        if x_hat is not None:
            self.ax.plot(x_hat, 0, 's', color='#2ca02c', markersize=9, markeredgecolor='black', label=f'Aitken $\\hat{{x}} = {x_hat:.4f}$')
            fx_hat = paso.get('fx_hat', f(x_hat))
            self.ax.vlines(x_hat, 0, fx_hat, color='#2ca02c', linestyle='-.', linewidth=1.3)

        # -------------------------------------------------------------
        # 3. TÍTULOS Y DETALLES
        # -------------------------------------------------------------
        aitken_txt = f" | Aitken: {x_hat:.5f}" if x_hat is not None else ""
        error_txt = f" | Err: {paso['error']:.2e}" if paso['error'] is not None else ""
        
        self.ax.set_title(
            f'[{modo_vista}] Paso {paso["iter"]}/{len(self.pasos)} | Subintervalo: [{a:.5f}, {b:.5f}] | x: {x_k:.5f}{aitken_txt}{error_txt}',
            fontsize=10, fontweight='bold', pad=12
        )
        self.ax.set_xlabel('Profundidad x (metros)', fontsize=11)
        self.ax.set_ylabel('f(x)', fontsize=11)
        self.ax.grid(True, linestyle=':', alpha=0.7)
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
    # Tanteo amplio de -6 a 8
    intervalos = metodo_tanteo_detallado(x_inicio=-6.0, x_fin=8.0)
    
    intervalo_valido = None
    for a, b in intervalos:
        if a >= 0 and b <= 6:
            intervalo_valido = (a, b)
            break
            
    if intervalo_valido:
        metodo_interpolacion_lineal(intervalo_valido[0], intervalo_valido[1], tol=0.001)
    else:
        metodo_interpolacion_lineal(2.0, 2.5, tol=0.001)

if __name__ == "__main__":
    hilo_consola = threading.Thread(target=ejecutar_consola)
    hilo_consola.start()

    app = InterpolacionLinealInteractiveDeMinus6a8(a_init=2.0, b_init=2.5, tol=0.001)
    try:
        plt.show()
    except KeyboardInterrupt:
        print("\nVentana gráfica cerrada.")

    hilo_consola.join()