import math
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np

# Datos del problema
R = 3.0   # Radio en metros
V = 30.0  # Volumen en m3

def f(x):
    """Ecuación del volumen del tanque esférico: f(x) = 0"""
    return math.pi * (x**2) * ((3.0 * R - x) / 3.0) - V

def metodo_tanteo_detallado(x_inicio=-6.0, x_fin=8.0):
    """Método de Tanteo evaluado desde x = -6 a x = 8 con paso configurable."""
    print("\n" + "=" * 80)
    print("--- MÉTODO DE TANTEO: EVALUACIÓN PASO A PASO ---")
    print("=" * 80)
    
    try:
        step = float(input("Ingrese el valor del incremento (paso Δx, ej. 0.5 o 1.0): "))
    except (ValueError, EOFError):
        step = 1.0
        print("Entrada no válida; se usará paso Δx = 1.0 por defecto.")

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

def metodo_biseccion_aitken(a, b, tol=0.001, max_iter=100):
    """
    Método de Intervalo Medio acelerado con el proceso Delta^2 de Aitken.
    Muestra tanto los valores estándar de bisección como la secuencia acelerada x_hat.
    """
    inicio = time.perf_counter()
    
    fa = f(a)
    fb = f(b)
    
    if fa * fb >= 0:
        print("\nEl intervalo no cumple con el cambio de signo f(a)*f(b) < 0.")
        return

    print("\n" + "=" * 95)
    print("--- MÉTODO DE INTERVALO MEDIO CON ACELERACIÓN DE AITKEN (Δ²) ---")
    print("=" * 95)
    print(f"{'i':<4} {'[a, b]':<20} {'x_bisecc':<12} {'x_aitken':<12} {'f(x_aitken)':<14} {'error_aitken':<14} {'t(s)':<10}")
    print("-" * 95)
    
    puntos_x = []
    x_hat_prev = None
    raiz_final = None
    iteraciones_totales = 0
    error_final = None

    for i in range(1, max_iter + 1):
        x = (a + b) / 2.0
        fx = f(x)
        puntos_x.append(x)
        
        tiempo_actual = time.perf_counter() - inicio
        intervalo_str = f"[{a:.4f}, {b:.4f}]"
        
        # Aitken requiere al menos 3 puntos (x_{k-2}, x_{k-1}, x_k)
        if len(puntos_x) >= 3:
            x0 = puntos_x[-3]
            x1 = puntos_x[-2]
            x2 = puntos_x[-1]
            
            denominador = (x2 - 2 * x1 + x0)
            if abs(denominador) > 1e-12:
                x_hat = x0 - ((x1 - x0) ** 2) / denominador
            else:
                x_hat = x2
                
            fx_hat = f(x_hat)
            error_aitken = abs(x_hat - x_hat_prev) if x_hat_prev is not None else abs(x_hat - x)
            x_hat_str = f"{x_hat:.6f}"
            fx_hat_str = f"{fx_hat:.4e}"
            err_str = f"{error_aitken:.4e}"
            
            print(f"{i:<4} {intervalo_str:<20} {x:<12.6f} {x_hat_str:<12} {fx_hat_str:<14} {err_str:<14} {tiempo_actual:<10.6f}")
            
            # Condición de corte con error acelerado
            if error_aitken < tol and i > 3:
                raiz_final = x_hat
                iteraciones_totales = i
                error_final = error_aitken
                break
                
            x_hat_prev = x_hat
        else:
            print(f"{i:<4} {intervalo_str:<20} {x:<12.6f} {'---':<12} {'---':<14} {'---':<14} {tiempo_actual:<10.6f}")

        # Actualización de extremos para bisección
        if fa * fx < 0:
            b = x
            fb = fx
        else:
            a = x
            fa = fx

    tiempo_total = time.perf_counter() - inicio
    if raiz_final is None:
        raiz_final = puntos_x[-1]
        iteraciones_totales = max_iter
        error_final = abs(b - a)

    print("=" * 95)
    print("RESULTADOS FINALES (CONVERGENCIA AITKEN):")
    print(f"- Profundidad calculada (x) : {raiz_final:.6f} metros")
    print(f"- Iteraciones requeridas    : {iteraciones_totales}")
    print(f"- Error final aproximado    : {error_final:.6e}")
    print(f"- Tiempo de ejecución total : {tiempo_total:.6f} segundos\n")


class BiseccionAitkenInteractive:
    """Visualizador paso a paso que contrasta el punto medio vs. la extrapolación de Aitken."""
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
        
        ax_next = plt.axes([0.72, 0.04, 0.16, 0.06])
        self.btn_next = Button(ax_next, 'Siguiente >')
        self.btn_next.on_clicked(self.next_step)
        
        ax_prev = plt.axes([0.54, 0.04, 0.16, 0.06])
        self.btn_prev = Button(ax_prev, '< Anterior')
        self.btn_prev.on_clicked(self.prev_step)
        
        self.dibujar_paso()

    def precalcular_pasos(self):
        a, b = float(self.a_init), float(self.b_init)
        fa, fb = f(a), f(b)
        puntos_x = []
        x_hat_prev = None
        
        for i in range(1, self.max_iter + 1):
            x = (a + b) / 2.0
            fx = f(x)
            puntos_x.append(x)
            
            x_hat = None
            fx_hat = None
            error_aitken = None
            
            if len(puntos_x) >= 3:
                x0, x1, x2 = puntos_x[-3], puntos_x[-2], puntos_x[-1]
                den = (x2 - 2 * x1 + x0)
                x_hat = x0 - ((x1 - x0) ** 2) / den if abs(den) > 1e-12 else x2
                fx_hat = f(x_hat)
                error_aitken = abs(x_hat - x_hat_prev) if x_hat_prev is not None else abs(x_hat - x)
                x_hat_prev = x_hat
                
            self.pasos.append({
                'iter': i,
                'a': a, 'b': b,
                'fa': fa, 'fb': fb,
                'x': x, 'fx': fx,
                'x_hat': x_hat, 'fx_hat': fx_hat,
                'error': error_aitken
            })
            
            if error_aitken is not None and error_aitken < self.tol and i > 3:
                break
                
            if fa * fx < 0:
                b, fb = x, fx
            else:
                a, fa = x, fx

    def dibujar_paso(self):
        self.ax.clear()
        paso = self.pasos[self.index]
        a, b, x_k = paso['a'], paso['b'], paso['x']
        fa, fb, fx_k = paso['fa'], paso['fb'], paso['fx']
        x_hat = paso['x_hat']
        
        x_vals = np.linspace(-6.0, 8.0, 1000)
        y_vals = [f(v) for v in x_vals]
        
        self.ax.plot(x_vals, y_vals, label=r'$f(x) = \pi x^2 \frac{9-x}{3} - 30$', color='#1f77b4', linewidth=2.5)
        self.ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.8)
        self.ax.axvline(0, color='gray', linestyle=':', linewidth=0.8)
        
        # Rango físico admisible (0 <= x <= 6m)
        self.ax.axvspan(0, 6, color='green', alpha=0.1, label='Rango Físico (0m a 6m)')
        self.ax.axvspan(a, b, color='orange', alpha=0.3, label=f'Intervalo [{a:.4f}, {b:.4f}]')
        
        self.ax.plot([a, b], [fa, fb], 'ro', markersize=7)
        self.ax.plot(x_k, 0, 'mo', markersize=8, label=f'Bisección $x_{{{paso["iter"]}}} = {x_k:.4f}$')
        self.ax.vlines(x_k, 0, fx_k, color='magenta', linestyle=':', linewidth=1.2)
        
        # Marcar punto acelerado de Aitken si está disponible
        if x_hat is not None:
            self.ax.plot(x_hat, 0, 's', color='#2ca02c', markersize=10, label=f'Aitken $\\hat{{x}} = {x_hat:.4f}$')
            
        self.ax.set_xlim(-6.0, 8.0)
        aitken_info = f" | Aitken: {x_hat:.5f}" if x_hat is not None else ""
        self.ax.set_title(
            f'Paso {paso["iter"]}/{len(self.pasos)} | Subintervalo: [{a:.5f}, {b:.5f}] | x_bis = {x_k:.5f}{aitken_info}',
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
    intervalos = metodo_tanteo_detallado(x_inicio=-6.0, x_fin=8.0)
    
    intervalo_valido = None
    for a, b in intervalos:
        if a >= 0 and b <= 6:
            intervalo_valido = (a, b)
            break
            
    if intervalo_valido:
        metodo_biseccion_aitken(intervalo_valido[0], intervalo_valido[1], tol=0.001)
    else:
        metodo_biseccion_aitken(2.0, 2.5, tol=0.001)

if __name__ == "__main__":
    hilo_consola = threading.Thread(target=ejecutar_consola)
    hilo_consola.start()

    app = BiseccionAitkenInteractive(a_init=2.0, b_init=2.5, tol=0.001)
    try:
        plt.show()
    except KeyboardInterrupt:
        print("\nVentana gráfica cerrada.")

    hilo_consola.join()