import matplotlib.pyplot as plt
from modelo_manning import ProblemaManning
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
    print(f"{'Tirante aproximado (x)':<32} | {m_interp['raiz']:<30.6f} | {m_aitken['raiz']:<30.6f}")
    print(f"{'Residuo funcional |f(x)|':<32} | {abs(m_interp['f_raiz']):<30.6e} | {abs(m_aitken['f_raiz']):<30.6e}")
    print(f"{'Iteraciones requeridas':<32} | {m_interp['iteraciones']:<30d} | {m_aitken['iteraciones']:<30d}")
    print(f"{'Error final alcanzado':<32} | {m_interp['error']:<30.6e} | {m_aitken['error']:<30.6e}")
    print(f"{'Tiempo de ejecución CPU (s)':<32} | {m_interp['tiempo']:<30.6f} | {m_aitken['tiempo']:<30.6f}")
    print("=" * 95)

def main():
    # 1. Configurar modelo matemático (admite valores de las docentes en la defensa)
    problema = ProblemaManning.configurar_desde_consola()

    # 2. Separación de raíces y descarte mediante Tanteo Optimizado
    intervalos_validos, hallazgos_tanteo = metodo_tanteo_optimizado(problema, x_inicio=-6.0, x_fin=6.0)

    if intervalos_validos:
        a_init, b_init = intervalos_validos[0]
        print(f"\n-> Intervalo físico seleccionado automáticamente: [{a_init:.4f}, {b_init:.4f}]")
    else:
        a_init, b_init = 1.0, 2.5
        print(f"\n-> Paso de tanteo muy amplio. Se utiliza intervalo físico de respaldo: [{a_init}, {b_init}]")

    try:
        tol_in = input("Ingrese la tolerancia de error E (Enter para 0.001): ").strip()
        tol = float(tol_in) if tol_in else 0.001
    except ValueError:
        tol = 0.001

    # 3. Ejecución del Método 1: Interpolación Lineal (Regula Falsi)
    m_interp, hist_interp = ejecutar_interpolacion_lineal(problema.f, a_init, b_init, tol=tol)

    # 4. Ejecución del Método 2: Iteración de Punto Fijo con Aceleración de Aitken
    semilla_x0 = (a_init + b_init) / 2.0
    m_steffensen, hist_steffensen = ejecutar_steffensen(problema.f, problema.g, semilla_x0, tol=tol)

    # 5. Comparación directa en consola
    imprimir_cuadro_comparativo(m_interp, m_steffensen)

    # 6. Menú de visualización gráfica paso a paso
    while True:
        print("\nMENÚ DE VISUALIZACIÓN GRÁFICA INTERACTIVA:")
        print("  1. Ver Slideshow de Interpolación Lineal (Regula Falsi)")
        print("  2. Ver Slideshow de Iteración con Aceleración de Aitken (Δ²)")
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
        elif opcion == '0':
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()