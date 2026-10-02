import matplotlib.pyplot as plt

def ejecutar_tanteo(func, args_func, origen, radio, paso, titulo):
    """Escanea la función hacia ambos lados del origen buscando cambios de signo."""
    print(f"\n--- TANTEO: Evaluando origen {origen} con radio ±{radio} ---")
    intervalos_raices = []
    
    x_der = origen
    x_izq = origen
    f_der_ant = func(x_der, *args_func)
    f_izq_ant = func(x_izq, *args_func)
    
    distancia = paso
    
    while distancia <= radio + 1e-9:
        x_der_nuevo = origen + distancia
        x_izq_nuevo = origen - distancia
        
        f_der_nuevo = func(x_der_nuevo, *args_func)
        f_izq_nuevo = func(x_izq_nuevo, *args_func)
        
        if f_der_ant * f_der_nuevo <= 0:
            intervalos_raices.append((x_der, x_der_nuevo))
            print(f"-> Raíz detectada en la derecha: [{x_der:.2f}, {x_der_nuevo:.2f}]")
            
        if f_izq_ant * f_izq_nuevo <= 0:
            intervalos_raices.append((x_izq_nuevo, x_izq))
            print(f"-> Raíz detectada en la izquierda: [{x_izq_nuevo:.2f}, {x_izq:.2f}]")
            
        x_der, x_izq = x_der_nuevo, x_izq_nuevo
        f_der_ant, f_izq_ant = f_der_nuevo, f_izq_nuevo
        distancia += paso

    intervalos_raices.sort()
    
    # Renderizado de gráfica
    limite_inf, limite_sup = origen - radio, origen + radio
    x_vals = []
    fx_vals = []
    x_temp = limite_inf
    
    while x_temp <= limite_sup + 1e-9:
        x_vals.append(x_temp)
        fx_vals.append(func(x_temp, *args_func))
        x_temp += (limite_sup - limite_inf) / 200
        
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, fx_vals, color='blue')
    plt.axhline(0, color='black', linestyle='--')
    for a, b in intervalos_raices:
        plt.axvspan(a, b, color='red', alpha=0.3)
    plt.title(titulo)
    plt.grid(True, alpha=0.5)
    plt.show(block=False)
    plt.pause(0.1)
    
    return intervalos_raices