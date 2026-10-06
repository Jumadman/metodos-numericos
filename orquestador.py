import consola  # Configura stdout a UTF-8 al importarse

from metodos import Contexto, ejecutar_tanteo, ejecutar as ejecutar_metodo, listar as listar_metodos

def _pedir_datos_del_metodo(metodo, contexto):
    """
    Completa el contexto con los datos que el método declara en `requiere`.

    Cada método pide únicamente lo que necesita: los de bracketsación toman el
    intervalo, Newton-Raphson además necesita un valor inicial. Cualquier valor
    opcional se toma presionando Enter.
    """
    if metodo.pide_x0:
        # Cada método decide si propone un valor inicial y por qué
        x0_sugerido, motivo = metodo.proponer_x0(contexto)
        if x0_sugerido is None:
            x0_sugerido = (contexto.a + contexto.b) / 2.0

        entrada = input(f"Valor inicial x0 (Enter para {x0_sugerido:.4f} - {motivo}): ")
        contexto = Contexto(
            contexto.func, contexto.args_func, contexto.a, contexto.b,
            float(entrada) if entrada.strip() else x0_sugerido
        )

    entrada_tol = input("Tolerancia (Enter para 0.001): ")
    tol = float(entrada_tol) if entrada_tol.strip() else 0.001
    return contexto, tol

def _mostrar_menu_metodos(contexto):
    """
    Arma el menú a partir del catálogo, marcando qué métodos pueden aplicarse al
    intervalo elegido sin pedir datos adicionales.
    """
    print("\nMétodos disponibles:")
    for indice, metodo in listar_metodos():
        cumple, _ = metodo.condiciones_previas(contexto)
        if cumple:
            estado = "✅ condiciones satisfechas"
        else:
            estado = "⚠️  condiciones no satisfechas"
        print(f"  {indice}. {metodo.nombre:<32} {estado}")

def _seleccionar_metodo(contexto):
    """Muestra el menú y devuelve (metodo, contexto_completo, tol), o None si se cancela."""
    while True:
        _mostrar_menu_metodos(contexto)
        print("  0. Volver a elegir intervalo")

        try:
            opcion = int(input("\nElige el método a utilizar: "))
        except ValueError:
            print("Entrada inválida.")
            continue

        if opcion == 0:
            return None

        metodos = dict(listar_metodos())
        if opcion not in metodos:
            print("Opción fuera de rango.")
            continue

        metodo = metodos[opcion]
        contexto, tol = _pedir_datos_del_metodo(metodo, contexto)

        # Verificación final con los datos ya elegidos (incluido x0 si aplica)
        cumple, mensajes = metodo.comprobar(contexto)
        print(f"\n--- CONDICIONES DE {metodo.nombre.upper()} ---")
        for mensaje in mensajes:
            print(f"  • {mensaje}")

        if cumple:
            if not mensajes:
                print("  • Todas las condiciones de aplicación se verifican.")
            print("  ✅ El método puede aplicarse sobre los datos elegidos.")
        else:
            print(f"  ❌ El método no puede aplicarse con seguridad.")
            if input("\n¿Ejecutarlo de todos modos? (s/N): ").strip().lower() != 's':
                print("Método descartado.")
                continue

        return metodo, contexto, tol

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
            if not (1 <= opcion_int <= len(intervalos)):
                print("Intervalo fuera de rango.")
                continue

            a, b = intervalos[opcion_int - 1]
            contexto = Contexto(func, args_func, a, b)

            seleccion = _seleccionar_metodo(contexto)
            if seleccion is None:
                continue

            metodo, contexto, tol = seleccion
            ejecutar_metodo(metodo, contexto, tol)
        except ValueError:
            print("Entrada inválida.")