import time

from .base import Metodo, Contexto, REQUIERE_INTERVALO

def ejecutar_biseccion(func, args_func, a, b, tol, max_iter=100):
    """Calcula la raíz mediante el método de Bisección."""
    tiempo_inicio = time.perf_counter()
    
    fa = func(a, *args_func)
    fb = func(b, *args_func)
    
    print(f"\n--- BISECCIÓN ---")
    print(f"{'i':>4} | {'x':>12} | {'f(x)':>12} | {'Error':>10} | {'Tiempo(s)':>10}")
    print("-" * 66)
    
    if fa * fb > 0:
        print(f"\n❌ ERROR: f(a) y f(b) tienen el mismo signo ({fa:.6f}, {fb:.6f}).")
        print("   Elige un intervalo válido obtenido en el tanteo.")
        return None
    
    # El punto medio inicial no debe declarar convergencia en la iteración 1
    c_viejo = (a + b) / 2.0
    
    for iteracion in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = func(c, *args_func)
        error = abs(c - c_viejo)
        tiempo_actual = time.perf_counter() - tiempo_inicio
        
        print(f"{iteracion:4d} | {c:12.6f} | {fc:12.6f} | {error:10.6f} | {tiempo_actual:10.6f}")
        
        # Se exige iteracion > 1 para que 'error' compare contra un punto medio real
        if error < tol and iteracion > 1:
            print(f"\n✅ RESULTADO: x = {c:.6f} (Error: {error:.6f} < {tol})")
            return c
        
        # Mantener el subintervalo que contiene la raíz
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        
        c_viejo = c
    
    print("\nLímite de iteraciones alcanzado.")
    return c_viejo

def comprobar_biseccion(contexto):
    """
    Condiciones de aplicación de la Bisección:
      1. El intervalo debe ser válido (a != b).
      2. Debe existir cambio de signo: f(a)·f(b) < 0.
      3. f debe ser continua en [a, b] (no verificable numéricamente).

    La técnica solo converge si el cambio de signo está garantizado, de ahí la
    exigencia del punto 2 frente a otros métodos.
    """
    mensajes = []
    cumple = True
    fa = contexto.func(contexto.a, *contexto.args_func)
    fb = contexto.func(contexto.b, *contexto.args_func)

    if contexto.a == contexto.b:
        mensajes.append("El intervalo es degenerado: a == b.")
        cumple = False

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

    mensajes.append("Se asume que f es continua en el intervalo (no verificable numéricamente).")
    return cumple, mensajes

METODO = Metodo(
    clave="biseccion",
    nombre="Bisección",
    ayuda="Parte el intervalo a la mitad. Robusto y de convergencia garantizada, pero lento (log₂).",
    requiere=(REQUIERE_INTERVALO,),
    ejecutar=ejecutar_biseccion,
    comprobar=comprobar_biseccion,
)