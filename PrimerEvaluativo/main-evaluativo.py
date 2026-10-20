import matplotlib.pyplot as plt
from controlador_funciones import ProblemaManning, ProblemaPersonalizado
from Tanteo import metodo_tanteo_optimizado
from metodos_aproximacion import ejecutar_interpolacion_lineal, ejecutar_steffensen
from visualizador import VisualizadorInteractivoManning

def imprimir_cuadro_comparativo(m_interp, m_aitken):
    """Imprime la tabla comparativa exigida en el Punto 4 de la consigna."""
    print("\n" + "=" * 95)
    print("CUADRO COMPARATIVO DE CONVERGENCIA Y RENDIMIENTO COMPUTACIONAL")
    print("=" * 95)
    print(f"{'Métrica de Evaluación':<32} | {m_interp['metodo']:<30} | {m_aitken['metodo']:<30}")
    print("-" * 95)
    print(f"{'Raíz aproximada (x)':<32} | {m_interp['raiz']:<30.6f} | {m_aitken['raiz']:<30.6f}")
    print(f"{'Residuo funcional |f(x)|':<32} | {abs(m_interp['f_raiz']):<30.6e} | {abs(m_aitken['f_raiz']):<30.6e}")
    print(f"{'Iteraciones / Ciclos requeridos':<32} | {m_interp['iteraciones']:<30d} | {m_aitken['iteraciones']:<30d}")
    print(f"{'Error final alcanzado':<32} | {m_interp['error']:<30.6e} | {m_aitken['error']:<30.6e}")
    print(f"{'Tiempo de ejecución CPU (s)':<32} | {m_interp['tiempo']:<30.6f} | {m_aitken['tiempo']:<30.6f}")
    print("=" * 95)

def seleccionar_intervalo(intervalos_validos):
    """Permite seleccionar qué intervalo resolver si el tanteo detecta múltiples raíces."""
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
        elec = int(input(f"Seleccione el número de intervalo a aproximar (1-{len(intervalos_validos)}, Enter para 1): ").strip() or 1)
        if 1 <= elec <= len(intervalos_validos):
            return intervalos_validos[elec - 1]
    except ValueError:
        pass
    return intervalos_validos[0]

def main():
    while True:
        print("\n" + "=" * 85)
        print("SISTEMA MODULAR DE MÉTODOS NUMÉRICOS - 1° TRABAJO EVALUATIVO")
        print("=" * 85)
        print("  1. Resolver Problema Hidráulico de Manning (Caso de Estudio del Informe)")
        print("  2. Ingresar una Función Cualquiera por Consola (Modo Libre / Defensa)")
        print("  0. Salir del programa")
        modo_prob = input("\nSeleccione una opción (Enter para 1): ").strip() or '1'

        if modo_prob == '0':
            break
        elif modo_prob == '2':
            problema = ProblemaPersonalizado.configurar_desde_consola()
        else:
            problema = ProblemaManning.configurar_desde_consola()

        # 2. Separación de raíces y descarte mediante Tanteo Optimizado
        x_ini, x_fin = problema.dominio_sugerido
        intervalos_validos, hallazgos_tanteo = metodo_tanteo_optimizado(problema, x_inicio=x_ini, x_fin=x_fin)

        a_init, b_init = seleccionar_intervalo(intervalos_validos)

        try:
            tol_in = input("\nIngrese la tolerancia de error E (Enter para 0.001): ").strip()
            tol = float(tol_in) if tol_in and float(tol_in) > 0 else 0.001
        except ValueError:
            tol = 0.001

        # 3. Ejecución del Método 1: Interpolación Lineal (Regula Falsi)
        m_interp, hist_interp = ejecutar_interpolacion_lineal(problema.f, a_init, b_init, tol=tol)

        # 4. Ejecución del Método 2: Método de Steffensen (Aitken por ciclos)
        semilla_x0 = (a_init + b_init) / 2.0
        problema.calibrar_g(semilla_x0)
        m_steffensen, hist_steffensen = ejecutar_steffensen(problema.f, problema.g, semilla_x0, tol=tol)

        # 5. Comparación directa en consola
        imprimir_cuadro_comparativo(m_interp, m_steffensen)

        # 6. Menú de visualización gráfica paso a paso
        while True:
            print("\nMENÚ DE VISUALIZACIÓN GRÁFICA INTERACTIVA:")
            print("  1. Ver Slideshow de Interpolación Lineal (Regula Falsi)")
            print("  2. Ver Slideshow de Método de Steffensen (Aitken Δ² + Telaraña)")
            print("  3. Volver al menú principal (Cargar otra función o parámetros)")
            print("  0. Finalizar programa")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == '1':
                visor = VisualizadorInteractivoManning(
                    problema, hist_interp, hallazgos_tanteo, modo='interpolacion'
                )
                plt.show()
            elif opcion == '2':
                visor = VisualizadorInteractivoManning(
                    problema, hist_steffensen, hallazgos_tanteo, modo='steffensen'
                )
                plt.show()
            elif opcion == '3':
                break
            elif opcion == '0':
                return
            else:
                print("Opción no válida.")

if __name__ == "__main__":
    main()