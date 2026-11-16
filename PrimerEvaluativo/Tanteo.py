import math

def derivada_numerica(f, x, h=1e-5):
    """Calcula f'(x) por diferencias finitas centrales de forma segura."""
    f_mas = f(x + h)
    f_menos = f(x - h)
    if math.isnan(f_mas) or math.isnan(f_menos) or math.isinf(f_mas) or math.isinf(f_menos):
        return float('nan')
    return (f_mas - f_menos) / (2.0 * h)

def es_discontinuidad_o_asintota(f, a, b):
    """
    Verifica si el cambio de signo o comportamiento entre 'a' y 'b'
    se debe a una asíntota vertical (divergencia) en lugar de una raíz continua.
    """
    medio = (a + b) / 2.0
    fa, fb, fm = f(a), f(b), f(medio)

    if any(math.isinf(val) or math.isnan(val) for val in (fa, fb, fm)):
        return True

    # Si el punto medio diverge abruptamente respecto a los extremos, es asíntota
    if abs(fm) > max(abs(fa), abs(fb)) * 5.0 and abs(fm) > 50.0:
        return True

    return False

def metodo_tanteo_optimizado(problema, x_inicio=None, x_fin=None):
    f = problema.f
    if x_inicio is None or x_fin is None:
        x_inicio, x_fin = getattr(problema, 'dominio_sugerido', (-6.0, 6.5))
    paso_defecto = getattr(problema, 'paso_sugerido', 2.5)

    print("\n" + "=" * 95)
    print("--- MÉTODO DE TANTEO: DETECCIÓN Y DESCARTE DE RAÍCES ---")
    print("=" * 95)

    try:
        entrada = input(f"Ingrese el incremento de exploración (paso Δx, Enter para {paso_defecto}): ").strip()
        step = float(entrada) if entrada else paso_defecto
        if step <= 0:
            step = paso_defecto
    except (ValueError, EOFError):
        step = paso_defecto
        print(f"Entrada no válida; se utilizará paso Δx = {paso_defecto} por defecto.")

    print(f"\nExplorando dominio [{x_inicio}, {x_fin}] con paso Δx = {step}:")
    print(f"{'i':<4} {'Subintervalo':<18} {'f(x_k)':<14} {'f(x_k+1)':<14} {'Diagnóstico del Segmento':<40}")
    print("-" * 95)

    hallazgos = []
    intervalos_validos = []
    x_curr = x_inicio
    i = 1

    while x_curr < x_fin - 1e-9:
        x_next = min(x_curr + step, x_fin)
        fx_curr = f(x_curr)
        fx_next = f(x_next)
        df_curr = derivada_numerica(f, x_curr)
        df_next = derivada_numerica(f, x_next)

        sub_str = f"[{x_curr:.2f}, {x_next:.2f}]"

        # Manejo de segmentos fuera del dominio matemático (ej. logaritmo negativo)
        if math.isnan(fx_curr) or math.isnan(fx_next):
            estado_seg = "Fuera del dominio real (NaN)"
            fx_c_str = "Indef (NaN)" if math.isnan(fx_curr) else f"{fx_curr:.4f}"
            fx_n_str = "Indef (NaN)" if math.isnan(fx_next) else f"{fx_next:.4f}"
            print(f"{i:<4} {sub_str:<18} {fx_c_str:<14} {fx_n_str:<14} {estado_seg:<40}")
            x_curr = x_next
            i += 1
            continue

        estado_seg = "Sin cambio de signo"

        # 1. Criterio de Bolzano (cambio de signo)
        if fx_curr * fx_next <= 0:
            if es_discontinuidad_o_asintota(f, x_curr, x_next):
                estado_seg = "DESCARTADO -> Asíntota / Discontinuidad"
                hallazgos.append((x_curr, x_next, False, "Asíntota Vertical / Discontinuidad"))
            else:
                es_valido, motivo = problema.validar_intervalo_fisico(x_curr, x_next)
                estado_seg = f"RAÍZ DETECTADA -> {motivo}"
                hallazgos.append((x_curr, x_next, es_valido, motivo))
                if es_valido:
                    intervalos_validos.append((x_curr, x_next))

        # 2. Criterio de Derivada (raíz tangencial de multiplicidad par)
        elif (not math.isnan(df_curr) and not math.isnan(df_next) and
              df_curr * df_next <= 0 and not es_discontinuidad_o_asintota(f, x_curr, x_next)):
            x_med = (x_curr + x_next) / 2.0
            fx_med = f(x_med)
            if not math.isnan(fx_med) and abs(fx_med) < 1e-2:
                es_valido, motivo = problema.validar_intervalo_fisico(x_curr, x_next)
                estado_seg = f"RAÍZ TANGENCIAL -> {motivo}"
                hallazgos.append((x_curr, x_next, es_valido, motivo))
                if es_valido:
                    intervalos_validos.append((x_curr, x_next))

        print(f"{i:<4} {sub_str:<18} {fx_curr:<14.4f} {fx_next:<14.4f} {estado_seg:<40}")

        x_curr = x_next
        i += 1

    print("-" * 95)
    print("\nRESUMEN DE CLASIFICACIÓN Y DESCARTES DEL TANTEO:")
    if not hallazgos:
        print(" No se registraron singularidades ni raíces en el rango explorado.")
    else:
        for idx, (a, b, valido, motivo) in enumerate(hallazgos, 1):
            estado_tag = "[ACEPTADA]" if valido else "[DESCARTADA]"
            print(f" {idx}. Intervalo [{a:.2f}, {b:.2f}] -> {estado_tag} {motivo}")

    return intervalos_validos, hallazgos