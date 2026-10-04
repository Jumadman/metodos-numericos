from orquestador import iniciar_resolucion
from metodos.newton_raphson import ejecutar_newton_raphson, analizar_convergencia

# --- Definición matemática del problema (fuera de la lógica del método) ---
# Utilidad total: P(x) = 8x + 0.3x^2 - 0.0013x^3 - 372
# El equilibrio (ni pierde ni gana) ocurre donde P(x) = 0

def f_utilidad(x):
    """Función objetivo: utilidad total menos el costo fijo."""
    return 8 * x + 0.3 * x**2 - 0.0013 * x**3 - 372

def df_utilidad(x):
    """P'(x) = 8 + 0.6x - 0.0039x^2"""
    return 8 + 0.6 * x - 0.0039 * x**2

def d2f_utilidad(x):
    """P''(x) = 0.6 - 0.0078x"""
    return 0.6 - 0.0078 * x

# Intervalos iniciales exigidos por la consigna del punto b
INTERVALOS = [(24.0, 26.0), (250.0, 252.0)]
TOLERANCIA = 1e-3

def parte_a():
    """Punto 1.a: hallazgo de las raíces en forma gráfica mediante el motor de tanteo."""
    print("\n" + "=" * 60)
    print("PARTE A - BÚSQUEDA GRÁFICA DE LAS RAÍCES (TANTEO)")
    print("=" * 60)
    print("Se graficará P(x) y el motor de tanteo marcará los intervalos con cambio de signo.")
    print("Valores recomendados -> Origen: 140 | Radio: 150 | Paso: 2")
    print("(esa cobertura alcanza a las dos raíces y acota los intervalos [24, 26] y [250, 252],")
    print(" que son los intervalos iniciales exigidos por la consigna del punto b)")

    iniciar_resolucion(f_utilidad, titulo="Punto de Equilibrio - Utilidad de la Companhia")

def parte_b():
    """Punto 1.b: Newton-Raphson con E < 10^-3 sobre los intervalos dados."""
    print("\n" + "=" * 60)
    print("PARTE B - NEWTON-RAPHSON CON ANÁLISIS DE CONVERGENCIA")
    print("=" * 60)

    resultados = []

    for a, b in INTERVALOS:
        print(f"\n>>> Intervalo inicial [{a:g}, {b:g}]")

        diagnostico = analizar_convergencia(
            f_utilidad, (), a, b,
            derivada=df_utilidad,
            segunda=d2f_utilidad
        )
        x0 = diagnostico["x0_sugerido"]

        if x0 is None:
            print("\nIntervalo descartado: las condiciones de convergencia no se cumplen.")
            continue

        print(f"\nValor inicial elegido por la condición f(x0)·f''(x0) > 0: x0 = {x0:.6f}")

        raiz = ejecutar_newton_raphson(
            f_utilidad, (), x0, TOLERANCIA,
            derivada=df_utilidad
        )

        if raiz is not None:
            resultados.append((a, b, raiz))

    if not resultados:
        print("\nNo se obtuvo ninguna raíz por Newton-Raphson.")
        return

    print("\n" + "=" * 60)
    print("RESUMEN DE PUNTOS DE EQUILIBRIO")
    print("=" * 60)
    for a, b, r in resultados:
        print(f"  Intervalo [{a:g}, {b:g}] -> x = {r:.6f} impresoras | P(x) = {f_utilidad(r):.3e} pesos")

    # Para no perder dinero hay que producir al menos la primera raíz (la más cercana al origen)
    critica = min(r for _, _, r in resultados)
    print(f"\nProducción mínima sin pérdidas: {critica:.4f} impresoras/mes -> {round(critica)} impresoras/mes")
    print(f"Producción máxima sin pérdidas: {max(r for _, _, r in resultados):.4f} impresoras/mes")
    print("Fuera del intervalo entre ambas raíces la compañía pierde dinero.")

def main():
    print("=== GUÍA PRÁCTICA: PUNTO DE EQUILIBRIO DE LA COMPAÑÍA ===")
    print("P(x) = 8x + 0.3x² - 0.0013x³ - 372")

    while True:
        print("\nOpciones:")
        print("  1. Parte A - Hallazgo gráfico de las raíces")
        print("  2. Parte B - Newton-Raphson con E < 10⁻³")
        print("  3. Ejecutar ambas partes")
        print("  0. Salir")

        opcion = input("\nElige una opción: ").strip()

        if opcion == '1':
            parte_a()
        elif opcion == '2':
            parte_b()
        elif opcion == '3':
            parte_a()
            parte_b()
        elif opcion == '0':
            print("\nHasta luego.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()