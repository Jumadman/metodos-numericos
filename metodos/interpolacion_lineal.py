import time

from .base import Metodo, Contexto, REQUIERE_INTERVALO

def ejecutar_interpolacion_lineal(func, args_func, a, b, tol, max_iter=100):
    """Calcula la raíz exacta mediante el método de Interpolación Lineal."""
    c_viejo = a
    tiempo_inicio = time.perf_counter()
    
    print(f"\n--- INTERPOLACIÓN LINEAL (Regla Falsa) ---")
    print(f"{'i':>4} | {'x':>12} | {'Error':>10} | {'Tiempo(s)':>10}")
    print("-" * 45)
    
    for iteracion in range(1, max_iter + 1):
        fa = func(a, *args_func)
        fb = func(b, *args_func)
        
        # Denominador de la secante: si se anula, la técnica no está definida
        if fa - fb == 0:
            print("\n❌ ERROR: f(a) = f(b), la recta secante es horizontal y no corta el eje X.")
            return None
        
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

def comprobar_interpolacion_lineal(contexto):
    """
    Condiciones de aplicación de la Regla Falsa:
      1. Cambio de signo en el intervalo: f(a)·f(b) < 0.
      2. f(a) != f(b): si ambos extremos tienen el mismo valor, la secante es
         horizontal, el denominador se anula y la fórmula queda indefinida.
      3. f continua en [a, b].

    A diferencia de la Bisección, no exige monotonía: solo la bracketsación.
    Su debilidad es que un extremo puede quedar congelado y la convergencia
    ser lineal en lugar de geométrica.
    """
    mensajes = []
    cumple = True
    fa = contexto.func(contexto.a, *contexto.args_func)
    fb = contexto.func(contexto.b, *contexto.args_func)

    if fa == 0:
        mensajes.append(f"f(a) = 0: el extremo a = {contexto.a:.6f} ya es una raíz exacta.")
    elif fb == 0:
        mensajes.append(f"f(b) = 0: el extremo b = {contexto.b:.6f} ya es una raíz exacta.")
    elif fa * fb > 0:
        mensajes.append(
            f"No hay cambio de signo en el intervalo: f(a) = {fa:.6f} y f(b) = {fb:.6f} "
            "tienen el mismo signo."
        )
        cumple = False

    if fa == fb and fa != 0:
        mensajes.append("f(a) = f(b): la recta secante sería horizontal y el denominador se anula.")
        cumple = False

    mensajes.append("Se asume que f es continua en el intervalo (no verificable numéricamente).")
    return cumple, mensajes

METODO = Metodo(
    clave="regla_falsa",
    nombre="Interpolación Lineal (Regla Falsa)",
    ayuda="Aproxima la raíz por la intersección de la secante con el eje X. Rápida, pero sin convergencia garantizada.",
    requiere=(REQUIERE_INTERVALO,),
    ejecutar=ejecutar_interpolacion_lineal,
    comprobar=comprobar_interpolacion_lineal,
)