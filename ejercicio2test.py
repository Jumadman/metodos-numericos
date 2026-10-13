import time
import threading
import matplotlib.pyplot as plt
import numpy as np

# Función de Utilidad P(x)
def P(x):
    return -0.0013 * x**3 + 0.3 * x**2 + 8 * x - 372

# Primera derivada P'(x)
def dP(x):
    return -0.0039 * x**2 + 0.6 * x + 8

# Segunda derivada P''(x)
def ddP(x):
    return -0.0078 * x + 0.6

# Verificación completa de las 4 Condiciones de Fourier/Convergencia
def verificar_convergencia_completa(a, b, x0):
    print(f"--- Evaluación de Condiciones de Convergencia en [{a}, {b}] con x0 = {x0} ---")
    
    # Condición 1: P(a) * P(b) < 0
    pa, pb = P(a), P(b)
    cond1 = (pa * pb) < 0
    print(f"1. Cambio de signo P(a)*P(b) < 0: P({a})={pa:.4f}, P({b})={pb:.4f} -> {'CUMPLE' if cond1 else 'NO CUMPLE'}")

    # Condición 2: P'(x) != 0 en todo x in [a, b]
    # Muestreamos el intervalo para verificar que no haya raíces de la derivada primera
    puntos_intervalo = np.linspace(a, b, 100)
    derivadas_primeras = dP(puntos_intervalo)
    cond2 = np.all(derivadas_primeras != 0) and np.all(derivadas_primeras > 0) or np.all(derivadas_primeras < 0)
    print(f"2. P'(x) != 0 en [{a}, {b}]: min|P'| = {np.min(np.abs(derivadas_primeras)):.4f} -> {'CUMPLE' if cond2 else 'NO CUMPLE'}")

    # Condición 3: P''(x) conserva el signo en [a, b]
    derivadas_segundas = ddP(puntos_intervalo)
    cond3 = np.all(derivadas_segundas > 0) or np.all(derivadas_segundas < 0)
    print(f"3. P''(x) signo constante en [{a}, {b}]: -> {'CUMPLE' if cond3 else 'NO CUMPLE'}")

    # Condición 4: P(x0) * P''(x0) > 0
    px0 = P(x0)
    ddpx0 = ddP(x0)
    cond4 = (px0 * ddpx0) > 0
    print(f"4. Elección de x0: P({x0})*P''({x0}) = {px0 * ddpx0:.4f} > 0 -> {'CUMPLE' if cond4 else 'NO CUMPLE'}")

    convergencia_garantizada = cond1 and cond2 and cond3 and cond4
    print(f"--> RESULTADO: {'CONVERGENCIA GARANTIZADA' if convergencia_garantizada else 'NO SE GARANTIZA CONVERGENCIA'}\n")
    return convergencia_garantizada

# Algoritmo de Newton-Raphson
def newton_raphson(x0, a_init, b_init, tol=1e-3, max_iter=100):
    verificar_convergencia_completa(a_init, b_init, x0)

    inicio = time.perf_counter()
    
    x_curr = x0
    i = 0
    error_rel = float('inf')
    a, b = float(a_init), float(b_init)
    
    print(f"Newton-Raphson (x0 = {x0}, Intervalo inicial [{a_init}, {b_init}]):")
    print(f"{'i':<5} | {'x':<12} | {'[a,b]':<22} | {'error relativo':<15}")
    print("-" * 62)
    
    while error_rel > tol and i < max_iter:
        i += 1
        fx = P(x_curr)
        dfx = dP(x_curr)
        
        if dfx == 0:
            print("Derivada nula. El método se detuvo.")
            return
            
        x_next = x_curr - fx / dfx
        
        # Error relativo
        error_rel = abs(x_next - x_curr) / abs(x_next) if x_next != 0 else abs(x_next - x_curr)
            
        # Actualización de cotas del intervalo
        if P(a) * P(x_next) <= 0:
            b = x_next
        else:
            a = x_next
            
        intervalo_str = f"[{a:.5f}, {b:.5f}]"
        print(f"{i:<5} | {x_curr:<12.6f} | {intervalo_str:<22} | {error_rel:<15.6e}")
        x_curr = x_next

    fin = time.perf_counter()
    tiempo_ejecucion = fin - inicio
    
    print("=" * 62)
    print("RESULTADOS:")
    print(f"- Cantidad de iteraciones : {i}")
    print(f"- Valor de x              : {x_curr:.6f}")
    print(f"- Intervalo final [a,b]   : [{a:.6f}, {b:.6f}]")
    print(f"- Error relativo final    : {error_rel:.6e}")
    print(f"- Tiempo de ejecución     : {tiempo_ejecucion:.8f} segundos\n")

# Hilo secundario para cálculos
def ejecutar_calculos():
    time.sleep(0.5)
    newton_raphson(x0=26.0, a_init=24.0, b_init=26.0, tol=1e-3)
    newton_raphson(x0=252.0, a_init=250.0, b_init=252.0, tol=1e-3)

# Hilo principal para gráfico interactivo en Matplotlib
def mostrar_grafico():
    x = np.linspace(0, 270, 1000)
    y = P(x)
    
    plt.figure(figsize=(11, 6))
    plt.plot(x, y, label='P(x) = -0.0013x³ + 0.3x² + 8x - 372', color='blue', linewidth=1.5)
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    
    # Resaltar e identificar intervalos
    plt.axvspan(24, 26, color='green', alpha=0.3, label='Intervalo 1: [24, 26]')
    plt.axvspan(250, 252, color='orange', alpha=0.3, label='Intervalo 2: [250, 252]')
    
    # Puntos de equilibrio
    plt.plot(25.2335, 0, 'ro', label='Punto de Equilibrio 1 (~25.23)')
    plt.plot(250.7593, 0, 'ro', label='Punto de Equilibrio 2 (~250.76)')

    plt.title('Gráfico de Utilidad P(x) - Intervalos y Puntos de Equilibrio')
    plt.xlabel('Cantidad de Impresoras (x)')
    plt.ylabel('Utilidad P(x)')
    plt.grid(True)
    plt.legend(loc='upper right')
    
    plt.show()

if __name__ == "__main__":
    hilo_calculos = threading.Thread(target=ejecutar_calculos)
    hilo_calculos.start()

    mostrar_grafico()

    hilo_calculos.join()