import time

def ejecutar_interpolacion_lineal(func, args_func, a, b, tol, max_iter=100):
    """Calcula la raíz exacta mediante el método de Interpolación Lineal."""
    c_viejo = a
    tiempo_inicio = time.perf_counter()
    
    print(f"\n--- INTERPOLACIÓN LINEAL ---")
    print(f"{'Iter':>4} | {'x':>12} | {'Error':>10} | {'Tiempo(s)':>10}")
    print("-" * 45)
    
    for iteracion in range(1, max_iter + 1):
        fa = func(a, *args_func)
        fb = func(b, *args_func)
        
        c = b - (fb * (a - b)) / (fa - fb)
        fc = func(c, *args_func)
        error = abs(c - c_viejo)
        tiempo_actual = time.perf_counter() - tiempo_inicio
        
        print(f"{iteracion:4d} | {c:12.6f} | {error:10.6f} | {tiempo_actual:10.6f}")
        
        if error < tol and iteracion > 1:
            print(f"\n✅ RESULTADO: x = {c:.6f} (Error: {error:.6f} < {tol})")
            return c
            
        if fa * fc < 0:
            b = c  
        else:
            a = c  
        c_viejo = c
        
    print("\nLímite de iteraciones alcanzado.")
    return c