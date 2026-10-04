import math

from metodos.base import Contexto
from metodos.iteracion import (
    LAM_DEFAULT,
    comprobar_iteracion,
    comprobar_iteracion_aitken,
    ejecutar_iteracion,
    ejecutar_iteracion_aitken,
)

# --- Definición matemática del problema (fuera de la lógica del método) ---
# Costo semanal de publicidad: A(x) = 200·ln(400/(500 - x))
# Precio de venta: $5 por unidad
# Utilidad neta: R(x) = 5x - A(x) = 5x - 200·ln(400/(500 - x))
# El equilibrio R(x) = 1000 se obtiene resolviendo f(x) = R(x) - 1000 = 0
#
# Dominio: x < 500, porque ln exige 500 - x > 0

X0 = 200.0          # "en un entorno de x = 200"
TOLERANCIA = 1e-4   # E < 10⁻⁴
INTERVALO = (200.0, 220.0)  # bracket de la raíz cercana a 200

def f_utilidad(x):
    """f(x) = R(x) - 1000. La raíz es la producción con utilidad neta de $1000."""
    return 5 * x - 200 * math.log(400 / (500 - x)) - 1000

def df_utilidad(x):
    """f'(x) = 5 - 200/(500 - x)"""
    return 5 - 200 / (500 - x)

def verificar_dominio(x0):
    """La iteración no puede abandonar x < 500: allí el logaritmo no existe."""
    if x0 >= 500:
        print(f"\n❌ ERROR: x0 = {x0:.4f} está fuera del dominio (x < 500).")
        return False
    return True

def _contexto(x0, lam):
    # 'extra' lleva el λ elegido para que las condiciones se verifiquen sobre la
    # misma iteración que luego se ejecuta, y no sobre el λ por defecto.
    return Contexto(f_utilidad, (), INTERVALO[0], INTERVALO[1], x0, {"lam": lam})

def analizar_parametros(x0, lam):
    """
    Justifica el valor de λ antes de iterar.

    Se usa la relajación g(x) = x - λ·f(x), cuya derivada es g'(x) = 1 - λ·f'(x).
    El punto fijo converge si |g'(x)| < 1, es decir si 0 < λ < 2/|f'(x)|.
    """
    print(f"\n--- ANÁLISIS DE CONVERGENCIA DE LA ITERACIÓN ---")
    print(f"x0 = {x0:.4f} | f(x0) = {f_utilidad(x0):.6f} | f'(x0) = {df_utilidad(x0):.6f}")
    print(f"λ = {lam}")
    print(f"g(x) = x - {lam}·f(x)  ->  g'(x0) = 1 - {lam}·f'(x0) = {1 - lam * df_utilidad(x0):.6f}")

    limite = 2 / abs(df_utilidad(x0))
    print(f"Rango admisible para λ: 0 < λ < {limite:.6f}")

    cumple, mensajes = comprobar_iteracion(_contexto(x0, lam))
    for mensaje in mensajes:
        print(f"  • {mensaje}")

    cumple_aitken, mensajes_aitken = comprobar_iteracion_aitken(_contexto(x0, lam))
    for mensaje in mensajes_aitken:
        if mensaje not in mensajes:
            print(f"  • {mensaje}")

    if not cumple:
        print("\n⚠️  Elegí un λ dentro del rango o la iteración puede divergir.")
    return cumple and cumple_aitken

def parte_simple(x0, lam):
    """Punto a, primer apartado: iteración de punto fijo con E < 10⁻⁴."""
    print("\n" + "=" * 60)
    print("ITERACIÓN DE PUNTO FIJO")
    print("=" * 60)
    return ejecutar_iteracion(f_utilidad, (), x0, TOLERANCIA, lam=lam)

def parte_aitken(x0, lam):
    """Punto a, segundo apartado: el mismo método con aceleración de Aitken."""
    print("\n" + "=" * 60)
    print("ITERACIÓN DE PUNTO FIJO CON ACELERACIÓN DE AITKEN")
    print("=" * 60)
    return ejecutar_iteracion_aitken(f_utilidad, (), x0, TOLERANCIA, lam=lam)

def resumen(resultado):
    """Cierra el ejercicio con la interpretación económica del resultado."""
    if resultado is None:
        print("\nNo se obtuvo una aproximación válida.")
        return

    unidades = round(resultado)
    print("\n" + "=" * 60)
    print("RESULTADO")
    print("=" * 60)
    print(f"Producción que equilibra la utilidad en $1000: x = {resultado:.6f} unidades/semana")
    print(f"Redondeando a unidades enteras: {unidades} unidades/semana")
    print(f"Comprobación: f({resultado:.6f}) = {f_utilidad(resultado):.3e}")

    print("\nObservación sobre la segunda raíz:")
    print("  R(x) tiene su máximo en x = 460 (donde R'(x) = 0), con R(460) ≈ $1839.")
    print("  Por eso R(x) = 1000 tiene DOS soluciones: una cerca de 213 y otra cerca de 499.78.")
    print("  La segunda queda al borde del dominio (x < 500) y allí f'(x) ≈ -900, por lo que")
    print("  g'(x) = 1 - λ·f'(x) se dispara muy por encima de 1: la iteración de punto fijo")
    print("  NO puede alcanzarla. Por eso la consigna acota la búsqueda 'en un entorno de x=200'.")

def main():
    print("=== GUÍA PRÁCTICA: EQUILIBRIO CON PUBLICIDAD VARIABLE ===")
    print("R(x) = 5x - 200·ln(400/(500 - x))     con dominio x < 500")
    print("Se busca R(x) = 1000  ->  f(x) = 5x - 200·ln(400/(500 - x)) - 1000 = 0")

    entrada_x0 = input(f"\nValor inicial x0 (Enter para {X0:g}): ")
    x0 = float(entrada_x0) if entrada_x0.strip() else X0
    if not verificar_dominio(x0):
        return

    entrada_lam = input(f"Parámetro λ de la relajación g(x) = x - λ·f(x) (Enter para {LAM_DEFAULT}): ")
    lam = float(entrada_lam) if entrada_lam.strip() else LAM_DEFAULT
    if lam <= 0:
        print("λ debe ser positivo. Fin del programa.")
        return

    if not analizar_parametros(x0, lam):
        if input("\n¿Seguir adelante de todos modos? (s/N): ").strip().lower() != 's':
            return

    while True:
        print("\nOpciones:")
        print("  1. Iteración de punto fijo (E < 10⁻⁴)")
        print("  2. Punto fijo + Aceleración de Aitken (E < 10⁻⁴)")
        print("  3. Ambas, con comparación de iteraciones")
        print("  0. Salir")

        opcion = input("\nElige una opción: ").strip()

        if opcion == '1':
            resumen(parte_simple(x0, lam))
        elif opcion == '2':
            resumen(parte_aitken(x0, lam))
        elif opcion == '3':
            parte_simple(x0, lam)
            resumen(parte_aitken(x0, lam))
        elif opcion == '0':
            print("\nHasta luego.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()