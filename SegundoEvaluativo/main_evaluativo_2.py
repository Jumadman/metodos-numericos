"""
Módulo: main_evaluativo_2.py
Descripción: Punto de entrada principal del 2° Trabajo de Evaluación (UNNE - FaCENA 2026).
             Métodos asignados: Polinomio Interpolador de Lagrange y Regla de los Trapecios.
"""

from controlador_tp2 import ControladorTP2


def main():
    controlador = ControladorTP2()

    while True:
        print("\n" + "=" * 98)
        print("2° TRABAJO DE EVALUACIÓN — MÉTODOS COMPUTACIONALES (UNNE FaCENA 2026)")
        print("Métodos Asignados: Polinomio Interpolador de Lagrange y Regla de los Trapecios")
        print("=" * 98)
        print(f"[Estado en Memoria: {controlador.resumen_estado()}]")
        print("-" * 98)
        print("  1. Ingresar / Modificar datos por teclado (Listas, Pares o Función f(x) con validación)")
        print("  2. Ejecutar Polinomio Interpolador de Lagrange sobre los datos activos")
        print("  3. Ejecutar Regla de los Trapecios sobre los datos activos")
        print("  4. Ejemplos Concretos de Cátedra, Convergencia O(h²) y Pruebas de Casos No Solubles")
        print("  0. Salir del programa")
        print("-" * 98)

        op = input("Seleccione una opción: ").strip()

        if op == '0':
            print("\nPrograma finalizado correctamente.")
            break
        elif op == '1':
            controlador.cargar_datos_teclado()
        elif op == '2':
            controlador.ejecutar_lagrange()
        elif op == '3':
            controlador.ejecutar_trapecios()
        elif op == '4':
            controlador.ejecutar_ejemplos_concretos()
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main() 