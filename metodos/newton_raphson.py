import math
import time
from .base import Metodo, Contexto, REQUIERE_INTERVALO, REQUIERE_X0
from .tanteo import derivada_numerica

def segunda_derivada_numerica(func, args_func, x, h=1e-4):
    """Calcula f''(x) mediante diferencias finitas centrales de f'(x)."""
    return (derivada_numerica(func, args_func, x + h) - derivada_numerica(func, args_func, x - h)) / (2 * h)

def _muestrear_derivadas(func, args_func, a, b, derivada, segunda, muestras):
    """Evalúa f en los extremos y f', f'' en los extremos y en una malla interna de [a, b]."""
    puntos = [a + (b - a) * i / muestras for i in range(muestras + 1)]
    return (
        func(a, *args_func),
        func(b, *args_func),
        [derivada(x, *args_func) for x in puntos],
        [segunda(x, *args_func) for x in puntos],
    )

def _cambia_de_signo(valores):
    return any(v1 * v2 < 0 for v1, v2 in zip(valores, valores[1:]))

def analizar_convergencia(func, args_func, a, b, derivada=None, segunda=None, muestras=50, imprimir=True):
    """
    Verifica las condiciones suficientes de convergencia de Newton-Raphson en [a, b]:
      1. f(a)·f(b) < 0            -> existencia de al menos una raíz en el intervalo
      2. f'(x) no cambia de signo -> la función es monótona en el intervalo
      3. f''(x) no cambia de signo-> no hay punto de inflexión en el intervalo
      4. existe x0 con f(x0)·f''(x0) > 0 -> elección segura del valor inicial

    Imprime el diagnóstico (imprimir=False para consultarlo en silencio) y
    devuelve un diccionario con el detalle numérico.
    'x0_sugerido' es el extremo recomendado por la condición 4, o None si ninguno la cumple.
    'cumple' indica si se verifican las cuatro condiciones.
    """
    if derivada is None:
        derivada = lambda x, *args: derivada_numerica(func, args_func, x)
    if segunda is None:
        segunda = lambda x, *args: segunda_derivada_numerica(func, args_func, x)

    fa, fb, dfs, d2fs = _muestrear_derivadas(func, args_func, a, b, derivada, segunda, muestras)

    diagnostico = {
        "fa": fa,
        "fb": fb,
        "raiz_existe": fa * fb < 0,
        "df_cambia": _cambia_de_signo(dfs),
        "d2f_cambia": _cambia_de_signo(d2fs),
        "df_min": min(dfs),
        "df_max": max(dfs),
        "d2f_min": min(d2fs),
        "d2f_max": max(d2fs),
        "x0_sugerido": None,
        "cumple": False,
    }

    # Condición 4: el extremo cuyo producto f·f'' es positivo garantiza convergencia monotónica
    if fa * d2fs[0] > 0:
        diagnostico["x0_sugerido"] = a
    elif fb * d2fs[-1] > 0:
        diagnostico["x0_sugerido"] = b

    diagnostico["cumple"] = (
        diagnostico["raiz_existe"]
        and not diagnostico["df_cambia"]
        and not diagnostico["d2f_cambia"]
        and diagnostico["x0_sugerido"] is not None
    )

    if not imprimir:
        return diagnostico

    x0 = diagnostico["x0_sugerido"]
    detalle_4 = "Ninguno de los extremos cumple f(x0)·f''(x0) > 0" if x0 is None else f"x0 = {x0:.4f} cumple f(x0)·f''(x0) > 0"

    print(f"\n--- ANÁLISIS DE CONVERGENCIA EN [{a:.4f}, {b:.4f}] ---")
    print(f"{'Condición':<44} | {'Estado':<8} | Detalle")
    print("-" * 92)
    print(f"{'1. f(a)·f(b) < 0 (existe raíz)':<44} | {'OK' if diagnostico['raiz_existe'] else 'FALLA':<8} | f(a)={fa:.6f}, f(b)={fb:.6f}, producto={fa * fb:.6e}")
    print(f"{'2. f\'(x) no cambia de signo (monotonía)':<44} | {'OK' if not diagnostico['df_cambia'] else 'FALLA':<8} | f\'(x) en [{diagnostico['df_min']:.6f}, {diagnostico['df_max']:.6f}]")
    print(f"{'3. f\'\'(x) no cambia de signo (sin inflexión)':<44} | {'OK' if not diagnostico['d2f_cambia'] else 'FALLA':<8} | f\'\'(x) en [{diagnostico['d2f_min']:.6f}, {diagnostico['d2f_max']:.6f}]")
    print(f"{'4. existe x0 con f(x0)·f\'\'(x0) > 0':<44} | {'OK' if x0 is not None else 'FALLA':<8} | {detalle_4}")

    if not diagnostico["cumple"]:
        print("\n⚠️  No se cumplen todas las condiciones suficientes. Newton-Raphson puede no converger.")
        return diagnostico

    print("\n✅ Convergencia garantizada: la sucesión x_{n+1} = x_n - f(x_n)/f'(x_n) es monótona y acotada.")
    return diagnostico

def ejecutar_newton_raphson(func, args_func, x0, tol, max_iter=100, derivada=None):
    """
    Calcula la raíz mediante el método de Newton-Raphson.

    derivada: función f'(x, *args_func). Si se omite, se estima el Jacobiano
    con diferencias finitas centrales (derivada_numerica).
    """
    tiempo_inicio = time.perf_counter()
    
    if derivada is None:
        derivada = lambda x, *args: derivada_numerica(func, args_func, x)
        metodo_derivada = "Numérica (dif. finitas)"
    else:
        metodo_derivada = "Analítica"
    
    print(f"\n--- NEWTON-RAPHSON ---")
    print(f"Derivada: {metodo_derivada}")
    print(f"x0 = {x0:.6f} | f(x0) = {func(x0, *args_func):.6f}")
    print(f"{'i':>4} | {'x':>12} | {'f(x)':>12} | {'Error':>10} | {'Tiempo(s)':>10}")
    print("-" * 66)
    
    # Cada fila muestra el iterado YA calculado a partir del anterior,
    # por lo que el error siempre compara dos puntos distintos.
    x = x0
    
    for iteracion in range(1, max_iter + 1):
        fx = func(x, *args_func)
        dfx = derivada(x, *args_func)
        
        # El Jacobiano se anula: la tangente es horizontal y no hay intersección
        if dfx == 0:
            print("\n❌ ERROR: f'(x) = 0. Elige otro valor inicial.")
            return None
        
        # x_{n+1} = x_n - f(x_n) / f'(x_n)
        x_nuevo = x - fx / dfx
        
        # Un x0 mal elegido puede hacer divergir la sucesión hacia el infinito
        if not math.isfinite(x_nuevo):
            print("\n❌ ERROR: la sucesión diverge. Elige un x0 más cercano a la raíz.")
            return None
        
        fx_nuevo = func(x_nuevo, *args_func)
        error = abs(x_nuevo - x)
        tiempo_actual = time.perf_counter() - tiempo_inicio
        
        print(f"{iteracion:4d} | {x_nuevo:12.6f} | {fx_nuevo:12.6f} | {error:10.6f} | {tiempo_actual:10.6f}")
        
        if fx_nuevo == 0:
            print(f"\n✅ RESULTADO: x = {x_nuevo:.6f} (f(x) = 0 exacto)")
            return x_nuevo
        
        if error < tol:
            print(f"\n✅ RESULTADO: x = {x_nuevo:.6f} (Error: {error:.6f} < {tol})")
            return x_nuevo
        
        x = x_nuevo
    
    print("\nLímite de iteraciones alcanzado.")
    return x

def comprobar_newton_raphson(contexto):
    """
    Condiciones de aplicación de Newton-Raphson.

    A diferencia de los métodos de bracketsación, no exige cambio de signo en
    un intervalo: necesita un valor inicial x0 del que depende toda la
    convergencia. Se verifican las condiciones suficientes sobre el contexto
    (intervalo y x0 ya elegidos por el usuario):

      1. f(a)·f(b) < 0            -> existe raíz en el intervalo
      2. f'(x) no cambia de signo -> f es monótona en el intervalo
      3. f''(x) no cambia de signo-> no hay inflexión que rompa la monotonía
      4. f(x0)·f''(x0) > 0        -> x0 está del lado correcto de la raíz
      5. f'(x0) != 0              -> la tangente inicial debe cortar el eje X
      6. x0 pertenece a [a, b]   -> el análisis del intervalo solo garantiza la
                                     convergencia hacia la raíz de ese intervalo

    Devuelve (cumple, mensajes). La tabla de diagnóstico ya la imprime
    analizar_convergencia, así que aquí solo se arma el resumen.
    """
    mensajes = []

    if contexto.x0 is None:
        return False, ["Falta el valor inicial x0, imprescindible para Newton-Raphson."]

    diagnostico = analizar_convergencia(contexto.func, contexto.args_func, contexto.a, contexto.b, imprimir=False)

    if diagnostico["df_cambia"]:
        mensajes.append("f'(x) cambia de signo dentro del intervalo: hay un punto crítico y la convergencia no está garantizada.")
    if diagnostico["d2f_cambia"]:
        mensajes.append("f''(x) cambia de signo dentro del intervalo: hay una inflexión que puede romper la monotonía.")
    if diagnostico["x0_sugerido"] is None:
        mensajes.append("Ningún extremo cumple f(x0)·f''(x0) > 0: la elección de x0 es delicada.")

    # El análisis se hizo sobre [a, b]: un x0 fuera de él puede apuntar a otra raíz
    x0_en_intervalo = contexto.a <= contexto.x0 <= contexto.b
    if not x0_en_intervalo:
        mensajes.append(
            f"x0 = {contexto.x0:.6f} está fuera del intervalo [{contexto.a:.6f}, {contexto.b:.6f}]. "
            "Las condiciones verificadas no cubren ese punto: la iteración puede converger a otra raíz."
        )

    derivada_en_x0 = derivada_numerica(contexto.func, contexto.args_func, contexto.x0)
    if derivada_en_x0 == 0:
        mensajes.append("f'(x0) = 0: la tangente inicial es horizontal y el método no puede avanzar.")

    cumple = diagnostico["cumple"] and derivada_en_x0 != 0 and x0_en_intervalo
    return cumple, mensajes

def sugerir_x0_newton(contexto):
    """
    Recomienda el extremo del intervalo que cumple f(x0)·f''(x0) > 0, que es
    el punto desde el cual la sucesión de Newton converge a la raíz de ese
    intervalo. Si ningún extremo sirve, devuelve None y el orquestador propone
    el punto medio.
    """
    diagnostico = analizar_convergencia(contexto.func, contexto.args_func, contexto.a, contexto.b)
    x0 = diagnostico["x0_sugerido"]

    if x0 is None:
        return None, "punto medio: ningún extremo cumple f(x0)·f''(x0) > 0"
    return x0, "extremo con f(x0)·f''(x0) > 0"

METODO = Metodo(
    clave="newton_raphson",
    nombre="Newton-Raphson",
    ayuda="Alinea la tangente con el eje X. Muy rápido (cuadrática), pero exige un buen valor inicial.",
    requiere=(REQUIERE_INTERVALO, REQUIERE_X0),
    ejecutar=ejecutar_newton_raphson,
    comprobar=comprobar_newton_raphson,
    sugerir_x0=sugerir_x0_newton,
)