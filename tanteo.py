import matplotlib.pyplot as plt

def derivada_numerica(func, args_func, x, h=1e-5):
    """Calcula f'(x) mediante diferencias finitas centrales para detectar puntos críticos."""
    return (func(x + h, *args_func) - func(x - h, *args_func)) / (2 * h)

def es_asintota(func, args_func, a, b):
    """
    Filtro de divergencia: Si el punto medio entre 'a' y 'b' tiende al infinito 
    en lugar de acercarse a cero, el cambio de signo es una asíntota, no una raíz.
    """
    medio = (a + b) / 2.0
    f_a = abs(func(a, *args_func))
    f_b = abs(func(b, *args_func))
    f_medio = abs(func(medio, *args_func))
    
    return f_medio > (f_a * 5) and f_medio > (f_b * 5)

def evaluar_segmento(func, args_func, x_ant, x_act, f_ant, f_act, df_ant, df_act, lado):
    """Evalúa un segmento específico aplicando las optimizaciones matemáticas."""
    hallazgo = None
    tipo = ""
    
    # 1. Detección Clásica (Cambio de signo)
    if f_ant * f_act <= 0:
        if es_asintota(func, args_func, x_ant, x_act):
            tipo = "Asíntota Ignorada"
        else:
            hallazgo = tuple(sorted((x_ant, x_act)))
            tipo = "Cruce Simple"
            
    # 2. Detección de Raíz Tangencial (Multiplicidad par)
    # Si la derivada cambia de signo, estamos en un vértice (mínimo o máximo local)
    elif df_ant * df_act <= 0:
        punto_critico = (x_ant + x_act) / 2.0
        f_critico = abs(func(punto_critico, *args_func))
        
        # Si el vértice está extremadamente cerca del eje X, es una raíz que rebotó
        if f_critico < 0.1: 
            hallazgo = tuple(sorted((x_ant, x_act)))
            tipo = "Raíz Tangencial"
            
    if hallazgo:
        print(f"-> {tipo} en lado {lado}: [{hallazgo[0]:.4f}, {hallazgo[1]:.4f}]")
        
    return hallazgo

def ejecutar_tanteo(func, args_func, origen, radio, paso, titulo):
    """
    Motor de búsqueda optimizado con análisis de derivadas y filtrado de discontinuidades.
    """
    print(f"\n--- TANTEO OPTIMIZADO: Origen {origen} | Radio ±{radio} | Paso {paso} ---")
    intervalos_raices = []
    
    # Inicialización en el origen
    x_der = origen
    x_izq = origen
    f_der_ant = func(x_der, *args_func)
    f_izq_ant = func(x_izq, *args_func)
    
    df_der_ant = derivada_numerica(func, args_func, x_der)
    df_izq_ant = derivada_numerica(func, args_func, x_izq)
    
    distancia = paso
    
    while distancia <= radio + 1e-9:
        x_der_nuevo = origen + distancia
        x_izq_nuevo = origen - distancia
        
        # Evaluaciones de la función
        f_der_nuevo = func(x_der_nuevo, *args_func)
        f_izq_nuevo = func(x_izq_nuevo, *args_func)
        
        # Evaluaciones de la derivada
        df_der_nuevo = derivada_numerica(func, args_func, x_der_nuevo)
        df_izq_nuevo = derivada_numerica(func, args_func, x_izq_nuevo)
        
        # Analizar lado derecho
        res_der = evaluar_segmento(
            func, args_func, x_der, x_der_nuevo, 
            f_der_ant, f_der_nuevo, df_der_ant, df_der_nuevo, "Derecho"
        )
        if res_der: intervalos_raices.append(res_der)
            
        # Analizar lado izquierdo
        res_izq = evaluar_segmento(
            func, args_func, x_izq, x_izq_nuevo, 
            f_izq_ant, f_izq_nuevo, df_izq_ant, df_izq_nuevo, "Izquierdo"
        )
        if res_izq: intervalos_raices.append(res_izq)
            
        # Preparar siguiente iteración
        x_der, x_izq = x_der_nuevo, x_izq_nuevo
        f_der_ant, f_izq_ant = f_der_nuevo, f_izq_nuevo
        df_der_ant, df_izq_ant = df_der_nuevo, df_izq_nuevo
        
        distancia += paso

    # Limpiar duplicados y ordenar
    intervalos_raices = sorted(list(set(intervalos_raices)))
    
    # --- RENDERIZADO GRÁFICO ---
    limite_inf, limite_sup = origen - radio, origen + radio
    x_vals, fx_vals = [], []
    x_temp = limite_inf
    
    while x_temp <= limite_sup + 1e-9:
        x_vals.append(x_temp)
        fx_vals.append(func(x_temp, *args_func))
        x_temp += (limite_sup - limite_inf) / 300 # Mayor resolución gráfica
        
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, fx_vals, color='blue', label="f(x)")
    plt.axhline(0, color='black', linestyle='-', linewidth=1)
    
    for idx, (a, b) in enumerate(intervalos_raices, 1):
        plt.axvspan(a, b, color='red', alpha=0.3, label=f'Intervalo {idx}' if idx==1 else "")
        
    plt.title(titulo)
    plt.grid(True, alpha=0.4, linestyle='--')
    
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if by_label: plt.legend(by_label.values(), by_label.keys())
    
    plt.show(block=False)
    plt.pause(0.1)
    
    return intervalos_raices