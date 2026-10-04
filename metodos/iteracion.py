import math
import time

from .base import Metodo, Contexto, REQUIERE_INTERVALO, REQUIERE_X0
from .tanteo import derivada_numerica

LAM_DEFAULT = 0.1

def construir_g(func, args_func, lam):
    """
    Función de iteración relajada: g(x) = x - lam·f(x).

    Se rearrange la ecuación f(x) = 0 como x = x - lam·f(x). El parámetro lam
    controla la convergencia: el método es estable cuando |g'(x)| < 1, es decir
    |1 - lam·f'(x)| < 1 sobre el intervalo de trabajo.
    """
    return lambda x, *args: x - lam * func(x, *args)

def _resolver_g(func, args_func, g, lam):
    """Devuelve (g, descripción) usando la función dada o la relajada por defecto."""
    if g is not None:
        return g, "g(x) explícita"
    return construir_g(func, args_func, lam), f"g(x) = x - {lam}·f(x)"

def _resolver_derivada_g(func, args_func, g, lam, derivada_g):
    """Devuelve (g', descripción) para verificar la condición de contracción."""
    if derivada_g is not None:
        return derivada_g, "Analítica"
    if g is not None:
        return lambda x, *args: derivada_numerica(lambda xx: g(xx, *args), (), x), "Numérica"
    # g(x) = x - lam·f(x)  =>  g'(x) = 1 - lam·f'(x)
    return lambda x, *args: 1.0 - lam * derivada_numerica(func, args_func, x), "Numérica"

def _formatear(valor, ancho=12, decimales=6):
    return f"{valor:{ancho}.{decimales}f}" if valor is not None else " " * (ancho - 1) + "-"

def ejecutar_iteracion(func, args_func, x0, tol, max_iter=100, lam=LAM_DEFAULT, g=None):
    """
    Iteración de punto fijo: x(n+1) = g(x(n)).

    g es la función de iteración. Si no se entrega, se usa la relajación
    g(x) = x - lam·f(x).
    """
    g, descripcion = _resolver_g(func, args_func, g, lam)
    tiempo_inicio = time.perf_counter()

    print(f"\n--- ITERACIÓN DE PUNTO FIJO ---")
    print(f"Función de iteración: {descripcion}")
    print(f"x0 = {x0:.6f} | f(x0) = {func(x0, *args_func):.6f}")
    print(f"{'i':>4} | {'x':>12} | {'f(x)':>12} | {'Error':>10} | {'Tiempo(s)':>10}")
    print("-" * 66)

    x = x0
    for iteracion in range(1, max_iter + 1):
        x_nuevo = g(x, *args_func)

        if not math.isfinite(x_nuevo):
            print("\n❌ ERROR: la sucesión diverge. Revisa g(x) o el valor inicial.")
            return None

        error = abs(x_nuevo - x)
        tiempo_actual = time.perf_counter() - tiempo_inicio
        print(f"{iteracion:4d} | {x_nuevo:12.6f} | {func(x_nuevo, *args_func):12.6f} | {error:10.6f} | {tiempo_actual:10.6f}")

        if error < tol:
            print(f"\n✅ RESULTADO: x = {x_nuevo:.6f} (Error: {error:.6f} < {tol})")
            return x_nuevo

        x = x_nuevo

    print("\nLímite de iteraciones alcanzado.")
    return x

def _aitken(x0, x1, x2):
    """
    Aceleración Δ² de Aitken sobre tres términos consecutivos.

        x̂ = x0 - (x1 - x0)² / (x2 - 2·x1 + x0)

    Devuelve None si el denominador se anula, lo que ocurre cuando la sucesión
    ya convergió exactamente (o es constante) y Aitken no está definida.
    """
    denominador = x2 - 2 * x1 + x0
    if denominador == 0:
        return None
    return x0 - ((x1 - x0) ** 2) / denominador

def ejecutar_iteracion_aitken(func, args_func, x0, tol, max_iter=100, lam=LAM_DEFAULT, g=None):
    """
    Iteración de punto fijo acelerada con Aitken.

    Se genera la sucesión de punto fijo completa y, sobre cada terna
    consecutiva, se aplica la aceleración Δ². El objetivo es comparar cuantas
    iteraciones necesita cada secuencia para alcanzar la misma tolerancia.
    """
    g, descripcion = _resolver_g(func, args_func, g, lam)
    tiempo_inicio = time.perf_counter()

    print(f"\n--- ITERACIÓN DE PUNTO FIJO + ACELERACIÓN DE AITKEN ---")
    print(f"Función de iteración: {descripcion}")
    print(f"x0 = {x0:.6f} | f(x0) = {func(x0, *args_func):.6f}")
    print(f"{'i':>4} | {'x':>12} | {'Error':>10} | {'x Aitken':>12} | {'Error':>10} | {'Tiempo(s)':>10}")
    print("-" * 90)

    xs = [x0]
    aitken_anterior = None
    error_aitken_anterior = None
    resultado_simple = None
    resultado_aitken = None
    iteracion_simple = None
    iteracion_aitken = None

    for iteracion in range(1, max_iter + 1):
        xs.append(g(xs[-1], *args_func))
        x_actual = xs[iteracion]

        if not math.isfinite(x_actual):
            print("\n❌ ERROR: la sucesión diverge. Revisa g(x) o el valor inicial.")
            break

        error_simple = abs(x_actual - xs[iteracion - 1])

        # Aitken necesita tres términos: (x_{n-2}, x_{n-1}, x_n)
        acelerado = None
        error_acelerado = None
        if iteracion >= 2:
            acelerado = _aitken(xs[iteracion - 2], xs[iteracion - 1], x_actual)
            if acelerado is not None:
                error_acelerado = (
                    abs(acelerado - aitken_anterior) if aitken_anterior is not None else None
                )

        tiempo_actual = time.perf_counter() - tiempo_inicio
        print(
            f"{iteracion:4d} | {x_actual:12.6f} | {error_simple:10.6f} | "
            f"{_formatear(acelerado)} | {_formatear(error_acelerado, 10)} | {tiempo_actual:10.6f}"
        )

        if error_simple < tol and resultado_simple is None:
            resultado_simple = x_actual
            iteracion_simple = iteracion

        if acelerado is not None and error_acelerado is not None and error_acelerado < tol and resultado_aitken is None:
            resultado_aitken = acelerado
            iteracion_aitken = iteracion

        aitken_anterior = acelerado if acelerado is not None else aitken_anterior

        # Se sigue hasta que ambas secuencias convergedieron: la comparación
        # final necesita saber cuántas iteraciones requería cada una.
        if resultado_simple is not None and resultado_aitken is not None:
            break

    print("\n--- COMPARACIÓN ---")
    if resultado_simple is not None:
        print(f"Punto fijo simple : x = {resultado_simple:.6f} en {iteracion_simple} iteraciones (E < {tol})")
    else:
        print("Punto fijo simple : no alcanzó la tolerancia.")

    if resultado_aitken is not None:
        print(f"Con Aitken        : x = {resultado_aitken:.6f} en {iteracion_aitken} iteraciones (E < {tol})")
        if iteracion_simple is not None:
            reduccion = 100 * (1 - iteracion_aitken / iteracion_simple)
            print(f"Reducción de iteraciones: {reduccion:.1f} %")
    else:
        print("Con Aitken        : no alcanzó la tolerancia.")

    if resultado_simple is not None and resultado_aitken is not None:
        diferencia = abs(resultado_simple - resultado_aitken)
        print(f"Discrepancia entre ambas aproximaciones: {diferencia:.3e}")

    return resultado_aitken if resultado_aitken is not None else resultado_simple

def _evaluar_contraccion(contexto, derivada_g, etiqueta):
    """Muestrea g' en el intervalo para verificar |g'| < 1."""
    puntos = [contexto.a + (contexto.b - contexto.a) * i / 50 for i in range(51)]
    valores = [derivada_g(x, *contexto.args_func) for x in puntos]

    maximo = max(abs(v) for v in valores)
    if maximo >= 1:
        return False, f"{etiqueta}: |g'(x)| alcanza {maximo:.6f} ≥ 1 en [{contexto.a:.4f}, {contexto.b:.4f}]. La iteración puede divergir."
    return True, f"{etiqueta}: |g'(x)| ≤ {maximo:.6f} < 1 en todo el intervalo: hay contracción y la convergencia está garantizada."

def _rango_lam(contexto):
    """
    Rango de λ admisible: |1 - λ·f'(x)| < 1 equivale a 0 < λ < 2/max|f'(x)|.

    Se usa para informar qué valor de λ haría converger el método cuando el
    elegido no cumple la condición de contracción.
    """
    puntos = [contexto.a + (contexto.b - contexto.a) * i / 50 for i in range(51)]
    maximo = max(abs(derivada_numerica(contexto.func, contexto.args_func, x)) for x in puntos)

    if maximo == 0:
        return None
    return 2.0 / maximo

def comprobar_iteracion(contexto):
    """
    Condiciones de aplicación de la iteración de punto fijo:

      1. |g'(x)| < 1 en el intervalo -> g es una contracción: existe un único
         punto fijo y cualquier valor inicial del intervalo converge a él.
      2. g debe transformar el intervalo en sí mismo (no verificable aquí).

    g se toma como la relajación g(x) = x - lam·f(x), que es la que reconstruye
    el orquestador al invocar el método desde el menú. El lam evaluado es el que
    el ejercicio guardó en contexto.extra, de modo que la condición se verifica
    sobre la misma iteración que luego se ejecuta.
    """
    lam = contexto.extra.get("lam", LAM_DEFAULT)
    derivada_g, modo = _resolver_derivada_g(contexto.func, contexto.args_func, None, lam, None)
    cumple, mensaje = _evaluar_contraccion(contexto, derivada_g, f"Derivada {modo.lower()} de g con λ={lam}")
    mensajes = [mensaje]

    if not cumple:
        rango = _rango_lam(contexto)
        if rango is not None:
            mensajes.append(
                f"Rango admisible para λ en este intervalo: 0 < λ < {rango:.6f}. "
                f"Probá con λ = {rango / 2:.4f}."
            )

    if contexto.x0 is not None and not (contexto.a <= contexto.x0 <= contexto.b):
        mensajes.append(
            f"x0 = {contexto.x0:.6f} está fuera del intervalo donde se verificó la contracción."
        )

    return cumple, mensajes

def comprobar_iteracion_aitken(contexto):
    """
    Condiciones de la iteración acelerada con Aitken: las de la iteración
    simple y, además, que la convergencia NO sea exacta, porque Aitken se
    indefiniría al anularse el denominador (x2 - 2·x1 + x0 = 0).
    """
    cumple, mensajes = comprobar_iteracion(contexto)
    lam = contexto.extra.get("lam", LAM_DEFAULT)

    derivada_g, _ = _resolver_derivada_g(contexto.func, contexto.args_func, None, lam, None)
    valores = [
        derivada_g(contexto.a + (contexto.b - contexto.a) * i / 50, *contexto.args_func)
        for i in range(51)
    ]

    # Si |g'| == 1 la sucesión converge pero no exactamente: Aitken está definida.
    # Si g' == 1 la sucesión es constante y Aitken no aplica.
    if any(abs(v - 1.0) < 1e-12 for v in valores):
        mensajes.append("g'(x) = 1 en algún punto del intervalo: la sucesión sería constante y Aitken no está definida.")

    return cumple, mensajes

METODO = Metodo(
    clave="punto_fijo",
    nombre="Iteración de punto fijo",
    ayuda="Repite x(n+1) = g(x(n)). Convergencia lineal, se garantiza si |g'(x)| < 1.",
    requiere=(REQUIERE_INTERVALO, REQUIERE_X0),
    ejecutar=ejecutar_iteracion,
    comprobar=comprobar_iteracion,
)

METODO_AITKEN = Metodo(
    clave="punto_fijo_aitken",
    nombre="Punto fijo + Aceleración de Aitken",
    ayuda="La misma sucesión con la aceleración Δ²: alcanza la misma tolerancia con menos iteraciones.",
    requiere=(REQUIERE_INTERVALO, REQUIERE_X0),
    ejecutar=ejecutar_iteracion_aitken,
    comprobar=comprobar_iteracion_aitken,
)