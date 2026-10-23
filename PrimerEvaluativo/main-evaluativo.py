"""
Módulo: main-evaluativo.py
Descripción: Menú interactivo principal del sistema sin bloqueo de consola.
"""

from controlador_funciones import ProblemaManning, ProblemaPersonalizado
from Tanteo import metodo_tanteo_optimizado
from metodos_aproximacion import (
    ejecutar_biseccion,
    ejecutar_interpolacion_lineal,
    ejecutar_newton_raphson,
    ejecutar_iteracion_simple,
    ejecutar_steffensen
)
from visualizador import mostrar_visualizador, graficar_inspeccion_inicial
from guia_3 import menu_guia_3, imprimir_tabla_comparativa
from guia_2 import menu_guia_2
from guia_1 import menu_guia_1

def seleccionar_intervalo(intervalos_validos):
    if not intervalos_validos:
        print("\n[Aviso] No se detectaron raíces con el paso actual.")
        try:
            a = float(input("Ingrese manualmente el extremo izquierdo 'a' (Enter para 1.0): ").strip() or 1.0)
            b = float(input("Ingrese manualmente el extremo derecho 'b' (Enter para 2.5): ").strip() or 2.5)
            return a, b
        except ValueError:
            return 1.0, 2.5

    if len(intervalos_validos) == 1:
        a_init, b_init = intervalos_validos[0]
        print(f"\n-> Intervalo válido seleccionado automáticamente: [{a_init:.4f}, {b_init:.4f}]")
        return a_init, b_init

    print("\nSe detectaron múltiples intervalos válidos con raíz:")
    for idx, (a, b) in enumerate(intervalos_validos, 1):
        print(f"  {idx}. [{a:.4f}, {b:.4f}]")
    try:
        elec = int(input(f"Seleccione el intervalo a aproximar (1-{len(intervalos_validos)}, Enter para 1): ").strip() or 1)
        if 1 <= elec <= len(intervalos_validos):
            return intervalos_validos[elec - 1]
    except ValueError:
        pass
    return intervalos_validos[0]


def ejecutar_flujo_evaluativo_manning():
    problema = ProblemaManning.configurar_desde_consola()
    x_ini, x_fin = problema.dominio_sugerido
    intervalos_validos, hallazgos_tanteo = metodo_tanteo_optimizado(problema, x_inicio=x_ini, x_fin=x_fin)
    a_init, b_init = seleccionar_intervalo(intervalos_validos)

    tol_in = input("\nIngrese la tolerancia de error E (Enter para 0.001): ").strip()
    tol = float(tol_in) if tol_in and float(tol_in) > 0 else 0.001

    m_interp, hist_interp = ejecutar_interpolacion_lineal(problema.f, a_init, b_init, tol=tol)

    semilla_x0 = (a_init + b_init) / 2.0
    m_stef, hist_stef = ejecutar_steffensen(problema.f, problema.g, semilla_x0, tol=tol)

    imprimir_tabla_comparativa([m_interp, m_stef])

    while True:
        print("\nMENÚ DE VISUALIZACIÓN GRÁFICA (CASO MANNING):")
        print("  1. Ver Slideshow de Interpolación Lineal (Regula Falsi)")
        print("  2. Ver Slideshow de Método de Steffensen (Aitken Δ² + Diagrama de Telaraña)")
        print("  3. Ver Gráfico estático de inspección general de raíces")
        print("  0. Volver al Menú Principal")
        op = input("Seleccione una opción: ").strip()

        if op == '1' and hist_interp:
            mostrar_visualizador(problema, hist_interp, hallazgos_tanteo, modo='interpolacion')
        elif op == '2' and hist_stef:
            mostrar_visualizador(problema, hist_stef, hallazgos_tanteo, modo='steffensen')
        elif op == '3':
            graficar_inspeccion_inicial(problema, raices_destacadas=[m_stef['raiz']])
        elif op == '0':
            break
        else:
            print("Opción no válida.")


def ejecutar_flujo_modo_libre():
    problema = ProblemaPersonalizado.configurar_desde_consola()
    x_ini, x_fin = problema.dominio_sugerido
    intervalos_validos, hallazgos_tanteo = metodo_tanteo_optimizado(problema, x_inicio=x_ini, x_fin=x_fin)
    a_init, b_init = seleccionar_intervalo(intervalos_validos)

    tol_in = input("\nIngrese la tolerancia de error E (Enter para 0.001): ").strip()
    tol = float(tol_in) if tol_in and float(tol_in) > 0 else 0.001

    semilla_x0 = (a_init + b_init) / 2.0
    problema.calibrar_g(semilla_x0)

    print("\nSeleccione qué métodos desea ejecutar sobre la función ingresada:")
    print("  1. Métodos Asignados del Evaluativo (Regula Falsi vs Steffensen/Aitken)")
    print("  2. Batería Completa (Bisección, Regula Falsi, Newton, Iteración y Steffensen)")
    elec_met = input("Opción (Enter para 1): ").strip() or '1'

    resultados_graficos = []

    if elec_met == '2':
        m_bis, h_bis = ejecutar_biseccion(problema.f, a_init, b_init, tol=tol)
        m_rf, h_rf = ejecutar_interpolacion_lineal(problema.f, a_init, b_init, tol=tol)
        m_nr, h_nr = ejecutar_newton_raphson(problema, a_init, b_init, tol=tol)
        m_it, h_it = ejecutar_iteracion_simple(problema.f, problema.g, semilla_x0, tol=tol)
        m_st, h_st = ejecutar_steffensen(problema.f, problema.g, semilla_x0, tol=tol, mostrar_lipschitz=False)

        imprimir_tabla_comparativa([m_bis, m_rf, m_nr, m_it, m_st])
        resultados_graficos = [
            ("Intervalo Medio (Bisección)", h_bis, 'biseccion'),
            ("Interpolación Lineal (Regula Falsi)", h_rf, 'interpolacion'),
            ("Newton-Raphson (Tangentes)", h_nr, 'newton'),
            ("Iteración Simple (Punto Fijo)", h_it, 'iteracion_simple'),
            ("Steffensen (Aceleración de Aitken)", h_st, 'steffensen')
        ]
    else:
        m_rf, h_rf = ejecutar_interpolacion_lineal(problema.f, a_init, b_init, tol=tol)
        m_st, h_st = ejecutar_steffensen(problema.f, problema.g, semilla_x0, tol=tol)
        imprimir_tabla_comparativa([m_rf, m_st])
        resultados_graficos = [
            ("Interpolación Lineal (Regula Falsi)", h_rf, 'interpolacion'),
            ("Steffensen (Aceleración de Aitken)", h_st, 'steffensen')
        ]

    while True:
        print("\nMENÚ DE VISUALIZACIÓN GRÁFICA (MODO LIBRE):")
        for idx, (nombre_m, _, _) in enumerate(resultados_graficos, 1):
            print(f"  {idx}. Ver Slideshow de {nombre_m}")
        print("  0. Volver al Menú Principal")
        op = input("Seleccione una opción: ").strip()
        if op == '0':
            break
        try:
            idx_sel = int(op) - 1
            if 0 <= idx_sel < len(resultados_graficos):
                _, hist_sel, modo_sel = resultados_graficos[idx_sel]
                if hist_sel:
                    mostrar_visualizador(problema, hist_sel, hallazgos_tanteo, modo=modo_sel)
        except ValueError:
            print("Opción no válida.")


def main():
    while True:
        print("\n" + "=" * 90)
        print("SISTEMA INTEGRAL DE MÉTODOS COMPUTACIONALES - UNNE FaCENA (2026)")
        print("=" * 90)
        print("  1. 1° TRABAJO EVALUATIVO: Canal Hidráulico de Manning (Regula Falsi vs Steffensen)")
        print("  2. MODO LIBRE: Ingresar una función cualquiera por consola (Defensa Oral)")
        print("  3. GUÍA DE LABORATORIO N° 1: Modelos Matemáticos y Algoritmos (Ejercicios 1 a 6)")
        print("  4. GUÍA DE LABORATORIO N° 2: Aproximaciones Numéricas y Errores (Ejercicios 1 a 5)")
        print("  5. GUÍA DE LABORATORIO N° 3: Raíces de Ecuaciones (Ejercicios 1, 2 y 3)")  
        print("  0. Salir del programa")
        print("-" * 90)

        opcion = input("Seleccione una opción (Enter para 1): ").strip() or '1'

        if opcion == '1':
            ejecutar_flujo_evaluativo_manning()
        elif opcion == '2':
            ejecutar_flujo_modo_libre()
        elif opcion == '3':
            menu_guia_1()
        elif opcion == '4':
            menu_guia_2()
        elif opcion == '5':
            menu_guia_3()  
        elif opcion == '0':
            print("\nPrograma finalizado correctamente.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()