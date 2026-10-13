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
        
        # CORREGIDO: Puntos evaluados exactamente de -6.0 a 8.0
        x_vals = np.linspace(-6.0, 8.0, 1000)
        y_vals = [f(v) for v in x_vals]
        self.ax.plot(x_vals, y_vals, label=r'Función $f(x) = \pi x^2 \frac{9-x}{3} - 30$', color='#1f77b4', linewidth=2.5)
        
        self.ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.8)
        self.ax.axvline(0, color='gray', linestyle=':', linewidth=0.8)
        
        # Rango físico real del tanque (0 <= x <= 6m)
        self.ax.axvspan(0, 6, color='green', alpha=0.1, label='Rango Físico del Tanque (0m a 6m)')
        
        # Intervalo sombreado actual
        self.ax.axvspan(a, b, color='yellow', alpha=0.4, label=f'Intervalo [{a:.4f}, {b:.4f}]')
        
        # Puntos extremos y recta secante actual
        self.ax.plot([a, b], [fa, fb], 'ro', markersize=8)
        self.ax.plot([a, b], [fa, fb], color='red', linestyle='-', linewidth=2, label=f'Recta Secante (Paso {paso["iter"]})')
        
        # Aproximación de la raíz
        self.ax.plot(x_k, 0, 'go', markersize=9, label=f'Raíz aprox. $x_{paso["iter"]} = {x_k:.4f}$')
        self.ax.vlines(x_k, 0, fx_k, color='green', linestyle=':', linewidth=1.5)
        
        # CORREGIDO: Fijar explícitamente el rango horizontal de -6 a 8
        self.ax.set_xlim(-6.0, 8.0)
        
        self.ax.set_title(
            f'Paso {paso["iter"]} de {len(self.pasos)}  |  Intervalo Actual: [{a:.5f}, {b:.5f}]  |  Aproximación x = {x_k:.5f}',
            fontsize=11, fontweight='bold'
        )
        self.ax.set_xlabel('Profundidad x (metros)', fontsize=11)
        self.ax.set_ylabel('f(x)', fontsize=11)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
        
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