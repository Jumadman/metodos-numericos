"""
Módulo: guia_3.py
Descripción: Contiene los modelos matemáticos y la resolución guiada e interactiva
             de los Ejercicios 1, 2 y 3 de la Guía de Laboratorio N° 3 (2026),
             reutilizando Tanteo.py, metodos_aproximacion.py y visualizador.py.
"""

import math
from Tanteo import metodo_tanteo_optimizado
from metodos_aproximacion import (
    ejecutar_biseccion,
    ejecutar_interpolacion_lineal,
    ejecutar_newton_raphson,
    ejecutar_iteracion_simple,
    ejecutar_steffensen
)
from visualizador import mostrar_visualizador, graficar_inspeccion_inicial


# =============================================================================
# MODELOS MATEMÁTICOS DE LA GUÍA DE LABORATORIO N° 3
# =============================================================================
class Ejercicio1TanqueEsferico:
    """
    Ejercicio 1: Tanque esférico V = pi * h^2 * (3R - h) / 3 con R = 3 m, V = 30 m^3.
    Dominio físico del tanque: [0, 2R] = [0, 6] metros.
    """
    def __init__(self, R=3.0, V=30.0):
        self.R = R
        self.V = V
        self.H_max = 2.0 * R
        self.val_min = 0.0
        self.nombre = f"Ej. 1 Tanque Esférico: f(h) = π·h²·(3·{R:.0f} - h)/3 - {V:.0f}"
        self.etiqueta_x = "Profundidad del agua h [metros]"
        self.dominio_sugerido = (0.0, 6.0)
        self.paso_sugerido = 0.5
        self.tol_sugerida = 0.001
        self.tiene_restriccion_fisica = True

    def f(self, h):
        return math.pi * (h ** 2) * ((3.0 * self.R - h) / 3.0) - self.V

    def df(self, h):
        return math.pi * h * (2.0 * self.R - h)

    def d2f(self, h):
        return 2.0 * math.pi * (self.R - h)

    def g(self, h):
        denom = math.pi * (self.R - (h / 3.0))
        return math.sqrt(self.V / denom) if denom > 0 else h

    def calibrar_g(self, x0):
        pass

    def validar_intervalo_fisico(self, a, b):
        if a >= 0.0 and b <= self.H_max:
            return True, f"VÁLIDA FÍSICAMENTE (Dentro del tanque [0, {self.H_max}m])"
        return False, f"DESCARTADA (Fuera de los límites físicos [0, {self.H_max}m])"


class Ejercicio2PuntoEquilibrio:
    """
    Ejercicio 2: Utilidad mensual por venta de impresoras:
    P(x) = 8x + 0.3x^2 - 0.0013x^3 - 372 = 0. Existen dos puntos de equilibrio.
    Intervalos iniciales de análisis de Fourier: [24, 26] y [250, 252].
    """
    def __init__(self):
        self.H_max = 300.0
        self.val_min = 0.0
        self.nombre = "Ej. 2 Punto de Equilibrio: P(x) = 8x + 0.3x² - 0.0013x³ - 372"
        self.etiqueta_x = "Cantidad de impresoras mensuales (x)"
        self.dominio_sugerido = (0.0, 300.0)
        self.paso_sugerido = 25.0
        self.tol_sugerida = 0.001
        self.tiene_restriccion_fisica = True

    def f(self, x):
        return 8.0 * x + 0.3 * (x ** 2) - 0.0013 * (x ** 3) - 372.0

    def df(self, x):
        return 8.0 + 0.6 * x - 0.0039 * (x ** 2)

    def d2f(self, x):
        return 0.6 - 0.0078 * x

    def g(self, x):
        df_val = self.df(x)
        return x - (self.f(x) / df_val) if abs(df_val) > 1e-12 else x

    def calibrar_g(self, x0):
        pass

    def validar_intervalo_fisico(self, a, b):
        if a >= 0.0:
            return True, "VÁLIDA FÍSICAMENTE (Producción positiva x >= 0)"
        return False, "DESCARTADA (Producción negativa)"


class Ejercicio3UtilidadPublicidad:
    """
    Ejercicio 3: Gasto en publicidad A = 200*ln(400/(500-x)), Utilidad R(x) = 5x - A = 1000.
    Ecuación: f(x) = 5x - 200*ln(400/(500-x)) - 1000 = 0 en un entorno de x = 200.
    Despeje de Punto Fijo: g(x) = 200 + 40*ln(400/(500-x)).
    """
    def __init__(self):
        self.H_max = 450.0
        self.val_min = 0.0
        self.nombre = "Ej. 3 Utilidad y Publicidad: f(x) = 5x - 200·ln(400/(500-x)) - 1000"
        self.etiqueta_x = "Unidades semanales vendidas (x)"
        self.dominio_sugerido = (0.0, 400.0)
        self.paso_sugerido = 20.0
        self.tol_sugerida = 0.0001
        self.tiene_restriccion_fisica = True

    def f(self, x):
        if x >= 500.0:
            return float('nan')
        try:
            return 5.0 * x - 200.0 * math.log(400.0 / (500.0 - x)) - 1000.0
        except Exception:
            return float('nan')

    def df(self, x):
        if x >= 500.0:
            return float('nan')
        return 5.0 - (200.0 / (500.0 - x))

    def d2f(self, x):
        if x >= 500.0:
            return float('nan')
        return -200.0 / ((500.0 - x) ** 2)

    def g(self, x):
        if x >= 500.0:
            return x
        try:
            return 200.0 + 40.0 * math.log(400.0 / (500.0 - x))
        except Exception:
            return x

    def calibrar_g(self, x0):
        pass

    def validar_intervalo_fisico(self, a, b):
        if a >= 0.0 and b < 500.0:
            return True, "VÁLIDA FÍSICAMENTE (0 <= x < 500 unidades)"
        return False, "DESCARTADA (Fuera de dominio x >= 500)"


# =============================================================================
# FUNCIONES AUXILIARES DE COMPARACIÓN Y RESOLUCIÓN
# =============================================================================
def imprimir_tabla_comparativa(lista_metricas):
    """Imprime un cuadro comparativo limpio entre dos o más métodos ejecutados."""
    metricas_validas = [m for m in lista_metricas if m is not None]
    if not metricas_validas:
        return

    print("\n" + "=" * 95)
    print("COMPARACIÓN DE RENDIMIENTO, CONVERGENCIA Y TIEMPO DE PROCESO")
    print("=" * 95)
    print(f"{'Método Numérico':<36} | {'Raíz Aprox.':<14} | {'|f(x)|':<13} | {'Iter/Ciclos':<11} | {'Error Final':<13} | {'Tiempo (s)':<10}")
    print("-" * 95)
    for m in metricas_validas:
        print(f"{m['metodo']:<36} | {m['raiz']:<14.6f} | {abs(m['f_raiz']):<13.4e} | "
              f"{m['iteraciones']:<11d} | {m['error']:<13.4e} | {m['tiempo']:<10.6f}")
    print("=" * 95)


def resolver_ejercicio_1():
    """Flujo completo del Ejercicio 1 (Tanque Esférico) según consignas 1.a, 1.b, 1.c y 1.d."""
    prob = Ejercicio1TanqueEsferico()
    print("\n" + "#" * 90)
    print("EJERCICIO 1: TANQUE ESFÉRICO (R = 3 m, V = 30 m³)")
    print("#" * 90)

    # 1.a Evaluación gráfica inicial
    ver_graf = input("\n1.a) ¿Desea abrir el gráfico inicial de evaluación de raíces? (s/n, Enter=s): ").strip().lower()
    if ver_graf != 'n':
        graficar_inspeccion_inicial(prob)

    # 1.b Separación de raíces por Método de Tanteo
    print("\n1.b) Separación de raíces aplicando el Método de Tanteo:")
    intervalos, hallazgos = metodo_tanteo_optimizado(prob, x_inicio=0.0, x_fin=6.0)
    a_init, b_init = intervalos[0] if intervalos else (2.0, 2.5)
    print(f"-> Subintervalo seleccionado para aproximación: [{a_init:.4f}, {b_init:.4f}]")

    # 1.c Aproximación por Intervalo Medio e Interpolación Lineal
    tol_in = input("\n1.c) Ingrese la cota de error E (Enter para 0.001): ").strip()
    tol = float(tol_in) if tol_in and float(tol_in) > 0 else 0.001

    m_bis, hist_bis = ejecutar_biseccion(prob.f, a_init, b_init, tol=tol)
    m_rf, hist_rf = ejecutar_interpolacion_lineal(prob.f, a_init, b_init, tol=tol)

    # 1.d Comparación de convergencia y tiempos
    imprimir_tabla_comparativa([m_bis, m_rf])

    while True:
        print("\nVISUALIZACIÓN GRÁFICA INTERACTIVA (EJERCICIO 1):")
        print("  1. Ver Slideshow de Intervalo Medio (Bisección)")
        print("  2. Ver Slideshow de Interpolación Lineal (Regula Falsi)")
        print("  0. Volver al menú de la Guía N° 3")
        op = input("Seleccione una opción: ").strip()
        if op == '1' and hist_bis:
            mostrar_visualizador(prob, hist_bis, hallazgos, modo='biseccion')
        elif op == '2' and hist_rf:
            mostrar_visualizador(prob, hist_rf, hallazgos, modo='interpolacion')
        elif op == '0':
            break


def resolver_ejercicio_2():
    """Flujo completo del Ejercicio 2 (Puntos de Equilibrio Impresoras) según 2.a y 2.b."""
    prob = Ejercicio2PuntoEquilibrio()
    print("\n" + "#" * 90)
    print("EJERCICIO 2: PUNTOS DE EQUILIBRIO EN PRODUCCIÓN DE IMPRESORAS")
    print("Ecuación: P(x) = 8x + 0.3x² - 0.0013x³ - 372 = 0")
    print("#" * 90)

    # 2.a Inspección gráfica y Tanteo preliminar
    ver_graf = input("\n2.a) ¿Desea abrir el gráfico inicial de P(x) en [0, 300]? (s/n, Enter=s): ").strip().lower()
    if ver_graf != 'n':
        graficar_inspeccion_inicial(prob)

    print("\nSeparación preliminar de las dos raíces por Método de Tanteo:")
    _, hallazgos = metodo_tanteo_optimizado(prob, x_inicio=0.0, x_fin=300.0)

    # 2.b Análisis de Condiciones de Fourier en [24, 26] y [250, 252] y Newton-Raphson
    tol_in = input("\n2.b) Ingrese la cota de error E para Newton-Raphson (Enter para 0.001): ").strip()
    tol = float(tol_in) if tol_in and float(tol_in) > 0 else 0.001

    print("\n>>> RESOLUCIÓN DEL PRIMER PUNTO DE EQUILIBRIO (Intervalo de consigna [24, 26]):")
    m_nr1, hist_nr1 = ejecutar_newton_raphson(prob, 24.0, 26.0, tol=tol)

    print("\n>>> RESOLUCIÓN DEL SEGUNDO PUNTO DE EQUILIBRIO (Intervalo de consigna [250, 252]):")
    m_nr2, hist_nr2 = ejecutar_newton_raphson(prob, 250.0, 252.0, tol=tol)

    m_nr1['metodo'] = "Newton-Raphson (Equilibrio 1: [24, 26])"
    m_nr2['metodo'] = "Newton-Raphson (Equilibrio 2: [250, 252])"
    imprimir_tabla_comparativa([m_nr1, m_nr2])

    while True:
        print("\nVISUALIZACIÓN GRÁFICA INTERACTIVA (EJERCICIO 2):")
        print("  1. Ver Slideshow de Newton-Raphson en Punto de Equilibrio 1 ([24, 26])")
        print("  2. Ver Slideshow de Newton-Raphson en Punto de Equilibrio 2 ([250, 252])")
        print("  3. Ver Gráfico general con ambas raíces destacadas")
        print("  0. Volver al menú de la Guía N° 3")
        op = input("Seleccione una opción: ").strip()
        if op == '1' and hist_nr1:
            mostrar_visualizador(prob, hist_nr1, hallazgos, modo='newton')
        elif op == '2' and hist_nr2:
            mostrar_visualizador(prob, hist_nr2, hallazgos, modo='newton')
        elif op == '3':
            graficar_inspeccion_inicial(prob, raices_destacadas=[m_nr1['raiz'], m_nr2['raiz']])
        elif op == '0':
            break


def resolver_ejercicio_3():
    """Flujo completo del Ejercicio 3 (Utilidad y Publicidad) en entorno de x = 200."""
    prob = Ejercicio3UtilidadPublicidad()
    print("\n" + "#" * 90)
    print("EJERCICIO 3: UTILIDAD NETA Y GASTO SEMANAL EN PUBLICIDAD")
    print("Ecuación: R(x) = 5x - 200·ln(400/(500 - x)) = 1000  |  Entorno inicial: x0 = 200")
    print("#" * 90)

    x0_in = input("\nIngrese el valor inicial x0 (Enter para 200.0 según consigna): ").strip()
    x0 = float(x0_in) if x0_in else 200.0

    tol_in = input("Ingrese la cota de error E (Enter para 0.0001 = 1e-4 según consigna): ").strip()
    tol = float(tol_in) if tol_in and float(tol_in) > 0 else 0.0001

    print("\nSeleccione modalidad de resolución del Método de Iteración (Requisito 1.a):")
    print("  1. Ejecutar sólo Método de Iteración Simple")
    print("  2. Ejecutar conjuntamente con la Aceleración Δ² de Aitken (Steffensen)")
    print("  3. Ejecutar AMBOS métodos para compararlos directamente (Recomendado)")
    mod = input("Opción (Enter para 3): ").strip() or '3'

    m_simp, hist_simp = None, None
    m_ait, hist_ait = None, None

    if mod in ('1', '3'):
        m_simp, hist_simp = ejecutar_iteracion_simple(prob.f, prob.g, x0, tol=tol, mostrar_lipschitz=True)

    if mod in ('2', '3'):
        m_ait, hist_ait = ejecutar_steffensen(prob.f, prob.g, x0, tol=tol, mostrar_lipschitz=(mod == '2'))

    if m_simp and m_ait:
        imprimir_tabla_comparativa([m_simp, m_ait])

    while True:
        print("\nVISUALIZACIÓN GRÁFICA (Curvas y = g(x) e y = x en un mismo gráfico):")
        if hist_simp:
            print("  1. Ver Slideshow de Iteración Simple (con gráfico conjunto y = g(x) vs y = x)")
        if hist_ait:
            print("  2. Ver Slideshow de Iteración + Aceleración de Aitken (con gráfico conjunto y = g(x) vs y = x)")
        print("  0. Volver al menú de la Guía N° 3")
        op = input("Seleccione una opción: ").strip()
        if op == '1' and hist_simp:
            mostrar_visualizador(prob, hist_simp, modo='iteracion_simple')
        elif op == '2' and hist_ait:
            mostrar_visualizador(prob, hist_ait, modo='steffensen')
        elif op == '0':
            break


def laboratorio_dinamico_guia_3():
    """Permite aplicar cualquiera de los 4 métodos a cualquiera de los 3 ejercicios de la Guía 3."""
    print("\n--- MODO DINÁMICO: PROBAR CUALQUIER MÉTODO EN CUALQUIER EJERCICIO DE LA GUÍA 3 ---")
    print("  1. Ejercicio 1 (Tanque Esférico)")
    print("  2. Ejercicio 2 (Puntos de Equilibrio de Impresoras)")
    print("  3. Ejercicio 3 (Utilidad y Costo de Publicidad)")
    ej = input("Seleccione el ejercicio (1-3): ").strip()

    if ej == '1':
        prob = Ejercicio1TanqueEsferico()
    elif ej == '2':
        prob = Ejercicio2PuntoEquilibrio()
    elif ej == '3':
        prob = Ejercicio3UtilidadPublicidad()
    else:
        return

    x_ini, x_fin = prob.dominio_sugerido
    intervalos, hallazgos = metodo_tanteo_optimizado(prob, x_inicio=x_ini, x_fin=x_fin)
    if not intervalos:
        a, b = 1.0, 3.0
    elif len(intervalos) == 1:
        a, b = intervalos[0]
    else:
        for idx, (ia, ib) in enumerate(intervalos, 1):
            print(f"  {idx}. Intervalo [{ia:.4f}, {ib:.4f}]")
        sel = int(input("Elija el número de intervalo (Enter=1): ").strip() or 1)
        a, b = intervalos[sel - 1] if 1 <= sel <= len(intervalos) else intervalos[0]

    tol = float(input(f"Ingrese tolerancia E (Enter para {prob.tol_sugerida}): ").strip() or prob.tol_sugerida)

    print("\nSeleccione el Método Numérico a ejecutar:")
    print("  1. Intervalo Medio (Bisección)")
    print("  2. Interpolación Lineal (Regula Falsi)")
    print("  3. Newton-Raphson (con condiciones de Fourier)")
    print("  4. Iteración de Punto Fijo Simple")
    print("  5. Iteración con Aceleración de Aitken (Steffensen)")
    met = input("Opción (1-5): ").strip()

    hist, modo_vis = None, 'interpolacion'
    if met == '1':
        _, hist = ejecutar_biseccion(prob.f, a, b, tol=tol)
        modo_vis = 'biseccion'
    elif met == '2':
        _, hist = ejecutar_interpolacion_lineal(prob.f, a, b, tol=tol)
        modo_vis = 'interpolacion'
    elif met == '3':
        _, hist = ejecutar_newton_raphson(prob, a, b, tol=tol)
        modo_vis = 'newton'
    elif met == '4':
        _, hist = ejecutar_iteracion_simple(prob.f, prob.g, (a + b) / 2.0, tol=tol)
        modo_vis = 'iteracion_simple'
    elif met == '5':
        _, hist = ejecutar_steffensen(prob.f, prob.g, (a + b) / 2.0, tol=tol)
        modo_vis = 'steffensen'

    if hist:
        ver = input("\n¿Desea abrir el visualizador interactivo para este resultado? (s/n, Enter=s): ").strip().lower()
        if ver != 'n':
            mostrar_visualizador(prob, hist, hallazgos, modo=modo_vis)


def menu_guia_3():
    """Submenú interactivo principal de la Guía de Laboratorio N° 3."""
    while True:
        print("\n" + "=" * 90)
        print("GUÍA DE LABORATORIO N° 3 - RAÍCES DE ECUACIONES")
        print("=" * 90)
        print("  1. Ejecutar Ejercicio 1 (Tanque Esférico: Gráfica, Tanteo, Intervalo Medio vs Regula Falsi)")
        print("  2. Ejecutar Ejercicio 2 (Equilibrio Impresoras: Gráfica, Tanteo, Fourier y Newton-Raphson)")
        print("  3. Ejecutar Ejercicio 3 (Utilidad y Publicidad: Iteración Simple vs Aceleración de Aitken)")
        print("  4. Laboratorio Dinámico (Probar cualquiera de los 4 métodos en cualquier ejercicio)")
        print("  0. Volver al Menú Principal del Sistema")
        print("-" * 90)

        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            resolver_ejercicio_1()
        elif opcion == '2':
            resolver_ejercicio_2()
        elif opcion == '3':
            resolver_ejercicio_3()
        elif opcion == '4':
            laboratorio_dinamico_guia_3()
        elif opcion == '0':
            break
        else:
            print("Opción no válida. Intente nuevamente.")