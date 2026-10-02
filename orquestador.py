from tanteo import ejecutar_tanteo
from interpolacion_lineal import ejecutar_interpolacion_lineal
# En el futuro: from biseccion import ejecutar_biseccion
# En el futuro: from newton_raphson import ejecutar_newton

def iniciar_resolucion(func, *args_func, titulo="Análisis Numérico"):
    """
    Controla el flujo del ejercicio: 
    1. Tanteo obligatorio
    2. Selección de intervalo
    3. Selección de método de cálculo de raíces
    """
    print(f"\n{'='*50}\n{titulo.upper()}\n{'='*50}")
    
    # 1. FASE DE TANTEO OBLIGATORIA
    print("\nFASE 1: Búsqueda de Intervalos (Tanteo)")
    try:
        origen = float(input("Punto de origen de la búsqueda: "))
        radio = float(input("Radio de expansión: "))
        paso = float(input("Tamaño del paso: "))
    except ValueError:
        print("Error: Ingresa solo valores numéricos.")
        return

    intervalos = ejecutar_tanteo(func, args_func, origen, radio, paso, titulo)
    
    if not intervalos:
        print("\nNo se encontraron raíces para analizar. Fin del programa.")
        return

    # 2. SELECCIÓN DE INTERVALO Y MÉTODO
    while True:
        print("\nFASE 2: Aproximación de la Raíz")
        print("Intervalos disponibles:")
        for i, (a, b) in enumerate(intervalos, 1):
            print(f"  {i} = [{a:.4f}, {b:.4f}]")
            
        try:
            opcion_int = int(input("\nElige el número del intervalo a resolver (0 para salir): "))
            if opcion_int == 0:
                break
            if 1 <= opcion_int <= len(intervalos):
                a, b = intervalos[opcion_int - 1]
                
                print("\nMétodos de aproximación disponibles:")
                print("  1. Interpolación Lineal (Regla Falsa)")
                print("  2. Bisección (Próximamente...)")
                # Aquí irás sumando opciones a medida que avances en la cursada
                
                opcion_metodo = input("Elige el método a utilizar: ")
                
                if opcion_metodo == '1':
                    entrada_tol = input("Tolerancia (Enter para 0.001): ")
                    tol = float(entrada_tol) if entrada_tol.strip() else 0.001
                    ejecutar_interpolacion_lineal(func, args_func, a, b, tol)
                else:
                    print("Método no implementado aún o selección inválida.")
            else:
                print("Intervalo fuera de rango.")
        except ValueError:
            print("Entrada inválida.")