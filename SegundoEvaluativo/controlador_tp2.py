"""
Módulo: controlador_tp2.py
Descripción: Controlador de problemas para el 2° Trabajo de Evaluación.
             Incluye formateo adaptativo de alta precisión y notación científica
             para evitar el truncamiento visual de errores pequeños en consola.
"""

import math
import numpy as np
from metodos_interpolacion import lagrange
from metodos_integracion import (
    validar_datos_integracion,
    trapecios_compuesto,
    trapecios_generalizado,
    simpson_1_3_compuesto
)
from visualizador2 import (
    graficar_lagrange,
    graficar_trapecios,
    graficar_convergencia_trapecios
)


class ControladorTP2:
    """Gestiona los datos activos, validaciones de dominio y reportes en consola."""

    ENTORNO_MAT = {
        'math': math, 'sin': math.sin, 'sen': math.sin, 'cos': math.cos,
        'tan': math.tan, 'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
        'exp': math.exp, 'ln': math.log, 'log': math.log, 'log10': math.log10,
        'sqrt': math.sqrt, 'abs': abs, 'pi': math.pi, 'e': math.e,
        'cbrt': lambda u: math.copysign(abs(u) ** (1.0 / 3.0), u)
    }

    def __init__(self):
        self.x_nodos = None
        self.y_nodos = None
        self.func_exacta = None
        self.origen_str = None

    def tiene_datos(self):
        return self.x_nodos is not None and len(self.x_nodos) >= 2

    def resumen_estado(self):
        if not self.tiene_datos():
            return "Sin datos cargados en memoria"
        _, _, equidist, h = validar_datos_integracion(self.x_nodos, self.y_nodos)
        txt_h = f"Paso constante h = {h:.6g}" if equidist else "Paso variable (No equidistante)"
        return (f"{len(self.x_nodos)} nodos en [{self.x_nodos[0]:.6g}, {self.x_nodos[-1]:.6g}] "
                f"| {txt_h} | Origen: {self.origen_str}")

    # =========================================================================
    # FORMATEADORES DE ALTA PRECISIÓN Y CONTROL DE CONSOLA
    # =========================================================================
    @staticmethod
    def _fmt_val(val):
        """Formatea resultados con 10 decimales o notación científica si es muy pequeño/grande."""
        if val == 0.0:
            return "0.0000000000"
        if abs(val) < 1e-4 or abs(val) >= 1e9:
            return f"{val:.8e}"
        return f"{val:.10f}"

    @staticmethod
    def _fmt_err(err):
        """Formatea errores siempre en notación científica para no ocultar magnitudes < 1e-6."""
        if err == 0.0:
            return "0.000000e+00 (Exacto en precisión de máquina)"
        return f"{err:.6e}"

    @staticmethod
    def _fmt_celda(val, ancho=14):
        """Formatea valores dentro de columnas tabulares sin truncar números chicos a 0."""
        if val == 0.0:
            txt = "0.000000"
        elif abs(val) < 1e-4 or abs(val) >= 1e7:
            txt = f"{val:.4e}"
        else:
            txt = f"{val:.6f}"
        return f"{txt:<{ancho}}"

    @staticmethod
    def _pausa_consola():
        """Detiene el flujo para que la tabla impresa no sea desplazada por el menú."""
        input("\n[ Fin del reporte — Presione Enter para volver al menú... ]")

    @staticmethod
    def _confirmar_grafico(mensaje="¿Desea generar y visualizar el gráfico? (s/n) [Enter = No]: "):
        """Exige confirmación explícita ('s') para no abrir gráficos automáticamente."""
        resp = input(f"\n{mensaje}").strip().lower()
        return resp in ('s', 'si', 'sí', 'y', 'yes')

    def _leer_escalar_seguro(self, prompt, valor_defecto=None):
        """Lee un número real o expresión constante (ej. 'pi', 'pi/2', 'e', '-1.5')."""
        while True:
            raw = input(prompt).strip()
            if raw == '' and valor_defecto is not None:
                return float(valor_defecto)
            try:
                expr = raw.replace('^', '**')
                val = eval(expr, {"__builtins__": {}}, dict(self.ENTORNO_MAT))
                if isinstance(val, complex) or not math.isfinite(float(val)):
                    print("  [Error] El valor debe ser un número real finito.")
                    continue
                return float(val)
            except Exception:
                print("  [Error] Entrada inválida. Ingrese un número o expresión constante (ej. 1.5, pi/2).")

    def _evaluar_punto_seguro(self, func, x_val):
        """Evalúa func(x_val) interceptando divisiones por cero, complejos y desbordamientos."""
        try:
            res = func(float(x_val))
            if isinstance(res, complex):
                return False, float('nan'), f"Resultado complejo fuera del dominio real en x = {x_val:.6g}"
            val = float(res)
            if math.isnan(val):
                return False, float('nan'), f"Indeterminación matemática (NaN) en x = {x_val:.6g}"
            if math.isinf(val) or abs(val) > 1e12:
                return False, float('inf'), f"Asíntota vertical / divergencia a infinito en x = {x_val:.6g}"
            return True, val, ""
        except ZeroDivisionError:
            return False, float('inf'), f"División por cero (singularidad/polo) en x = {x_val:.6g}"
        except ValueError as err:
            return False, float('nan'), f"Fuera de dominio matemático en x = {x_val:.6g} ({err})"
        except OverflowError:
            return False, float('inf'), f"Desbordamiento numérico (Overflow) en x = {x_val:.6g}"
        except Exception as err:
            return False, float('nan'), f"Error al evaluar en x = {x_val:.6g}: {err}"

    def _validar_y_evaluar_funcion_en_nodos(self, func, xs_cand):
        """Evalúa func en todos los nodos y puntos medios para garantizar continuidad en [a, b]."""
        ys_cand = []
        for xi in xs_cand:
            ok, val, msg_err = self._evaluar_punto_seguro(func, xi)
            if not ok:
                print(f"\n  [PROBLEMA NO SOLUBLE EN LOS NODOS DADOS]: {msg_err}.")
                print("  -> La función presenta discontinuidad, asíntota o sale del dominio real.")
                print("  -> Modifique los valores de X o la expresión de f(x).\n")
                return False, []
            ys_cand.append(val)

        for k in range(len(xs_cand) - 1):
            xm = 0.5 * (xs_cand[k] + xs_cand[k + 1])
            ok, _, msg_err = self._evaluar_punto_seguro(func, xm)
            if not ok:
                print(f"\n  [ADVERTENCIA DE SINGULARIDAD INTERNA]: {msg_err}.")
                print("  -> Existe una asíntota o discontinuidad entre dos nodos consecutivos.")
                return False, []

        return True, ys_cand

    def integral_referencia(self, func, a, b):
        """Cuadratura de Gauss-Legendre de 32 puntos como valor exacto de referencia."""
        try:
            nodos, pesos = np.polynomial.legendre.leggauss(32)
            t_nodos = 0.5 * (b - a) * nodos + 0.5 * (a + b)
            suma = 0.0
            for w, ti in zip(pesos, t_nodos):
                ok, val, _ = self._evaluar_punto_seguro(func, float(ti))
                if not ok:
                    return None
                suma += w * val
            res = float(0.5 * (b - a) * suma)
            return res if math.isfinite(res) else None
        except Exception:
            return None

    def mostrar_tabla_activa(self):
        """Imprime en consola la tabla de nodos cargada indicando el espaciamiento h_i."""
        if not self.tiene_datos():
            return
        _, _, equidist, h = validar_datos_integracion(self.x_nodos, self.y_nodos)
        print("\n" + "-" * 84)
        print(f"TABLA DE DATOS ACTIVA ({len(self.x_nodos)} nodos | "
              f"{f'Equidistante h = {h:.8g}' if equidist else 'No equidistante (Paso variable)'}):")
        print("-" * 84)
        print(f"{'Índice i':<10} | {'Abscisa x_i':<20} | {'Paso h_i':<18} | {'Ordenada y_i = f(x_i)':<24}")
        print("-" * 84)
        for i, (xi, yi) in enumerate(zip(self.x_nodos, self.y_nodos)):
            paso_str = "---" if i == 0 else self._fmt_celda(xi - self.x_nodos[i - 1], 18)
            print(f"{i:<10d} | {self._fmt_celda(xi, 20)} | {paso_str:<18} | {self._fmt_celda(yi, 24)}")
        print("-" * 84)

    # =========================================================================
    # 1. INGRESO Y VALIDACIÓN DE DATOS POR TECLADO (4 MODALIDADES)
    # =========================================================================
    def cargar_datos_teclado(self):
        """Permite cargar y validar datos por teclado (Listas, Pares, Función o X personalizado)."""
        print("\n" + "=" * 98)
        print("CARGA Y VALIDACIÓN DE DATOS DE ENTRADA")
        print("=" * 98)
        print("  1. Ingresar listas de X e Y separados por comas (Ej: 0, 0.4, 0.75, 1.5, 2.0)")
        print("  2. Ingresar pares (x_i, y_i) uno por uno")
        print("  3. Evaluar una función f(x) en intervalo [a, b] con n subintervalos (Equidistante)")
        print("  4. Evaluar una función f(x) sobre una lista personalizada de X (No equidistante)")
        print("  0. Cancelar y volver al menú")
        modo = input("\nSeleccione modalidad (Enter para 1): ").strip() or '1'

        if modo == '0':
            return

        if modo == '2':
            while True:
                try:
                    cant = int(input("Cantidad de puntos a ingresar (mínimo 2): ").strip())
                    if cant >= 2:
                        break
                    print("  [Error] Se requieren como mínimo 2 puntos.")
                except ValueError:
                    print("  [Error] Ingrese un número entero válido.")

            x_list, y_list = [], []
            for i in range(cant):
                while True:
                    xi = self._leer_escalar_seguro(f"  Nodo {i} -> Ingrese x_{i}: ")
                    if any(abs(xi - x_prev) < 1e-14 for x_prev in x_list):
                        print(f"  [Error Matemático] La abscisa x = {xi} está duplicada. Deben ser distintas.")
                        continue
                    yi = self._leer_escalar_seguro(f"  Nodo {i} -> Ingrese y_{i}: ")
                    x_list.append(xi)
                    y_list.append(yi)
                    break

            pares = sorted(zip(x_list, y_list))
            self.x_nodos = [p[0] for p in pares]
            self.y_nodos = [p[1] for p in pares]
            self.func_exacta = None
            self.origen_str = "Carga manual por pares"

        elif modo == '3':
            print("\nOperadores admitidos: +, -, *, /, ^, sin(x), cos(x), tan(x), exp(x), ln(x), sqrt(x), cbrt(x), pi, e")
            while True:
                expr_raw = input("Ingrese la función f(x) (ej. sin(x) + 1  o  exp(-x^2)): ").strip() or "sin(x) + 1"
                expr_py = expr_raw.replace('^', '**')
                try:
                    compile(expr_py, "<string>", "eval")
                    func = lambda val, e=expr_py: eval(
                        e, {"__builtins__": {}}, dict(self.ENTORNO_MAT, x=float(val))
                    )
                except SyntaxError:
                    print("  [Error de Sintaxis] Revise paréntesis y operadores (escriba 2*x en lugar de 2x).")
                    continue

                a = self._leer_escalar_seguro("Extremo inferior a (Enter para 0.0): ", 0.0)
                b = self._leer_escalar_seguro("Extremo superior b (Enter para pi): ", math.pi)
                if abs(b - a) < 1e-14:
                    print("  [Error] El intervalo [a, b] es degenerado (a == b). Ingrese límites distintos.")
                    continue
                if a > b:
                    print(f"  [Aviso] Se invirtió el orden para asegurar a < b: [{b}, {a}].")
                    a, b = b, a

                while True:
                    try:
                        n = int(input("Cantidad de subintervalos n (Enter para 4): ").strip() or 4)
                        if n >= 1:
                            break
                        print("  [Error] La cantidad de subintervalos n debe ser >= 1.")
                    except ValueError:
                        print("  [Error] Ingrese un entero válido.")

                xs_cand = np.linspace(a, b, n + 1).tolist()
                ok_tabla, ys_cand = self._validar_y_evaluar_funcion_en_nodos(func, xs_cand)
                if ok_tabla:
                    self.x_nodos = xs_cand
                    self.y_nodos = ys_cand
                    self.func_exacta = lambda v, f=func: float(f(v))
                    self.origen_str = f"f(x) = {expr_raw} en [{a:.4g}, {b:.4g}] (n={n})"
                    break

        elif modo == '4':
            print("\nOperadores admitidos: +, -, *, /, ^, sin(x), cos(x), tan(x), exp(x), ln(x), sqrt(x), cbrt(x), pi, e")
            while True:
                expr_raw = input("1. Ingrese la función f(x) (ej. sqrt(x + 1)  o  sin(x)): ").strip() or "sqrt(x + 1)"
                expr_py = expr_raw.replace('^', '**')
                try:
                    compile(expr_py, "<string>", "eval")
                    func = lambda val, e=expr_py: eval(
                        e, {"__builtins__": {}}, dict(self.ENTORNO_MAT, x=float(val))
                    )
                except SyntaxError:
                    print("  [Error de Sintaxis] Revise paréntesis y operadores (escriba 2*x en lugar de 2x).")
                    continue

                while True:
                    raw_x = input("2. Ingrese lista personalizada de nodos X separados por coma (ej. 0, 0.4, 0.75, 1.5, 2.0): ").strip()
                    try:
                        xs = []
                        for item in raw_x.split(','):
                            if item.strip():
                                val_x = eval(item.strip().replace('^', '**'), {"__builtins__": {}}, dict(self.ENTORNO_MAT))
                                if isinstance(val_x, complex) or not math.isfinite(float(val_x)):
                                    raise ValueError("Nodo no real o infinito")
                                xs.append(float(val_x))

                        if len(xs) < 2:
                            print("  [Error] Debe ingresar como mínimo 2 nodos en X.")
                            continue

                        xs_sort = sorted(xs)
                        if any(abs(xs_sort[k + 1] - xs_sort[k]) < 1e-14 for k in range(len(xs_sort) - 1)):
                            print("  [Error Matemático] Existen abscisas X repetidas. No es soluble por Lagrange.")
                            continue
                        break
                    except Exception:
                        print("  [Error de Formato] Ingrese números o expresiones válidas separadas por coma.")

                ok_tabla, ys_cand = self._validar_y_evaluar_funcion_en_nodos(func, xs_sort)
                if ok_tabla:
                    self.x_nodos = xs_sort
                    self.y_nodos = ys_cand
                    self.func_exacta = lambda v, f=func: float(f(v))
                    self.origen_str = f"f(x) = {expr_raw} sobre X personalizado ({len(xs_sort)} nodos)"
                    break

        else:
            while True:
                try:
                    raw_x = input("Valores de X separados por coma: ").strip()
                    raw_y = input("Valores de Y separados por coma: ").strip()
                    xs = [float(v.strip()) for v in raw_x.split(',') if v.strip()]
                    ys = [float(v.strip()) for v in raw_y.split(',') if v.strip()]
                    if len(xs) < 2 or len(xs) != len(ys):
                        print(f"  [Error] Se requieren al menos 2 nodos e igual cantidad en X ({len(xs)}) e Y ({len(ys)}).")
                        continue
                    if any(not (math.isfinite(vx) and math.isfinite(vy)) for vx, vy in zip(xs, ys)):
                        print("  [Error] Los datos contienen valores no finitos.")
                        continue
                    xs_sort = sorted(xs)
                    if any(abs(xs_sort[k + 1] - xs_sort[k]) < 1e-14 for k in range(len(xs_sort) - 1)):
                        print("  [Error Matemático] Existen valores de X repetidos. No es soluble como función.")
                        continue

                    pares = sorted(zip(xs, ys))
                    self.x_nodos = [p[0] for p in pares]
                    self.y_nodos = [p[1] for p in pares]
                    self.func_exacta = None
                    self.origen_str = "Listas manuales por teclado"
                    break
                except ValueError:
                    print("  [Error de Formato] Use punto para decimales (ej. 2.5) y comas para separar.")

        self.mostrar_tabla_activa()
        self._pausa_consola()

    # =========================================================================
    # 2. EJECUCIÓN DETALLADA DE LAGRANGE
    # =========================================================================
    def ejecutar_lagrange(self):
        """Ejecuta el Polinomio Interpolador de Lagrange mostrando todos los cálculos y errores."""
        if not self.tiene_datos():
            print("\n[Aviso] Primero debe cargar una tabla de datos.")
            self.cargar_datos_teclado()
            if not self.tiene_datos():
                return

        self.mostrar_tabla_activa()

        if len(self.x_nodos) > 12:
            print("\n[Advertencia Numérica]: La tabla tiene más de 12 nodos (Grado > 11).")
            print("En grados altos con nodos equidistantes puede presentarse el Fenómeno de Runge.")

        puntos_evaluados = []
        while True:
            print("\n" + "=" * 102)
            print(f"EJECUCIÓN: POLINOMIO INTERPOLADOR DE LAGRANGE (Grado n = {len(self.x_nodos) - 1})")
            print("=" * 102)
            x_medio = 0.5 * (self.x_nodos[0] + self.x_nodos[-1])
            entrada = input(f"Ingrese el valor x* a interpolar (Enter para {x_medio:.6g}, o 'fin' para salir): ").strip()

            if entrada.lower() in ('fin', 'salir') and puntos_evaluados:
                break
            elif entrada == '':
                x_star = x_medio
            else:
                try:
                    expr_x = entrada.replace('^', '**')
                    val_x = eval(expr_x, {"__builtins__": {}}, dict(self.ENTORNO_MAT))
                    x_star = float(val_x)
                    if isinstance(val_x, complex) or not math.isfinite(x_star):
                        print("  [Error] Ingrese un número real finito.")
                        continue
                except Exception:
                    print("  [Error] Entrada inválida. Ingrese un valor numérico o expresión constante.")
                    continue

            try:
                res = lagrange(self.x_nodos, self.y_nodos, x_star)
            except Exception as err:
                print(f"\n[ERROR EN CÁLCULO DE LAGRANGE]: {err}")
                self._pausa_consola()
                return

            tipo_op = "EXTRAPOLACIÓN (Fuera del rango de la tabla - Mayor riesgo de error)" if res['es_extrapolacion'] else "INTERPOLACIÓN (Dentro del dominio [x_0, x_n])"
            txt_paso = f"Equidistante (h = {res['h']:.8g})" if res['equidistante'] else "No equidistante (Paso variable)"

            print("\n1. PARÁMETROS DEL PROBLEMA:")
            print(f"   • Cantidad de nodos conocidos : {res['n_puntos']} puntos (x_0 = {self.x_nodos[0]:.6g} ... x_{res['grado']} = {self.x_nodos[-1]:.6g})")
            print(f"   • Grado máximo del polinomio  : n = {res['grado']}")
            print(f"   • Espaciamiento de abscisas   : {txt_paso}")
            print(f"   • Punto de evaluación         : x* = {x_star:.8g} -> [{tipo_op}]")
            print(f"   • Polinomio P_{res['grado']}(x) expandido  : P(x) = {res['polinomio_str']}")

            print("\n2. TABLA DE CÁLCULOS INTERMEDIOS (BASES CARDINALES L_i(x*) Y APORTES):")
            print("   Fórmula: L_i(x*) = Prod_{j != i} (x* - x_j) / Prod_{j != i} (x_i - x_j)")
            print("-" * 102)
            print(f"{'i':<4} | {'x_i':<12} | {'y_i':<14} | {'Numerador Prod':<16} | {'Denominador Prod':<16} | {'Base L_i(x*)':<15} | {'y_i * L_i(x*)':<15}")
            print("-" * 102)
            for d in res['detalles_nodos']:
                print(f"{d['i']:<4d} | {self._fmt_celda(d['x_i'], 12)} | {self._fmt_celda(d['y_i'], 14)} | "
                      f"{d['numerador']:<16.6e} | {d['denominador']:<16.6e} | "
                      f"{self._fmt_celda(d['L_i'], 15)} | {self._fmt_celda(d['aporte'], 15)}")
            print("-" * 102)

            terminos_suma = " + ".join(f"({d['y_i']:.4g})*({d['L_i']:.4g})" for d in res['detalles_nodos'][:6])
            if len(res['detalles_nodos']) > 6:
                terminos_suma += " + ..."

            print("\n3. RESULTADOS, VERIFICACIÓN Y TIEMPO DE PROCESO:")
            print(f"   • Sustitución en sumatoria    : P({x_star:.6g}) = {terminos_suma}")
            print(f"   • Propiedad suma de bases     : sum L_i(x*) = {res['suma_bases_L']:.12f}  (Valor teórico exacto = 1.0)")
            print(f"   • VALOR INTERPOLADO FINAL     : P_{res['grado']}({x_star:.6g}) = {self._fmt_val(res['valor_interpolado'])}")
            print(f"   • Tiempo de ejecución CPU     : {res['tiempo_cpu']:.4e} s ({res['tiempo_cpu'] * 1e6:.2f} µs)")

            if self.func_exacta is not None:
                ok_ex, v_real, msg_ex = self._evaluar_punto_seguro(self.func_exacta, x_star)
                if ok_ex:
                    err_abs = abs(v_real - res['valor_interpolado'])
                    err_rel = (err_abs / abs(v_real)) * 100.0 if abs(v_real) > 1e-15 else 0.0
                    print(f"   • Valor Exacto f({x_star:.6g})    : {self._fmt_val(v_real)}")
                    print(f"   • Error Absoluto |f - P|      : {self._fmt_err(err_abs)}")
                    print(f"   • Error Relativo Porcentual   : {self._fmt_err(err_rel)} %")
                else:
                    print(f"   • [Aviso Función Exacta]      : {msg_ex}")
            print("=" * 102)

            puntos_evaluados.append((x_star, res['valor_interpolado']))

            seguir = input("\n¿Desea interpolar otro punto x* sobre esta misma tabla? (s/n) [Enter = No]: ").strip().lower()
            if seguir not in ('s', 'si', 'sí'):
                break

        if puntos_evaluados and self._confirmar_grafico():
            graficar_lagrange(self.x_nodos, self.y_nodos, puntos_evaluados=puntos_evaluados,
                              func_exacta=self.func_exacta)

        self._pausa_consola()

    # =========================================================================
    # 3. EJECUCIÓN DETALLADA DE LA REGLA DE LOS TRAPECIOS
    # =========================================================================
    def ejecutar_trapecios(self):
        """Ejecuta la Regla de los Trapecios detallando h, E, P, I, subintervalos, errores y tiempos."""
        if not self.tiene_datos():
            print("\n[Aviso] Primero debe cargar una tabla de datos.")
            self.cargar_datos_teclado()
            if not self.tiene_datos():
                return

        self.mostrar_tabla_activa()

        try:
            _, _, equidist, _ = validar_datos_integracion(self.x_nodos, self.y_nodos)
            if equidist:
                res = trapecios_compuesto(self.x_nodos, self.y_nodos)
            else:
                res = trapecios_generalizado(self.x_nodos, self.y_nodos)
        except Exception as err:
            print(f"\n[PROBLEMA NO SOLUBLE EN INTEGRACIÓN]: {err}")
            self._pausa_consola()
            return

        print("\n" + "=" * 102)
        print(f"EJECUCIÓN: {res['metodo'].upper()}")
        print("=" * 102)

        print("1. PARÁMETROS GEOMÉTRICOS DE LA PARTICIÓN:")
        print(f"   • Intervalo de integración [a, b] : [{res['a']:.8g}, {res['b']:.8g}] (Amplitud total = {res['b'] - res['a']:.8g})")
        print(f"   • Cantidad de subintervalos (n)   : {res['intervalos_n']} trapecios ({len(self.x_nodos)} nodos)")
        if res['equidistante']:
            print(f"   • Tamaño de paso constante (h)    : h = ({res['b']:.6g} - {res['a']:.6g}) / {res['intervalos_n']} = {self._fmt_val(res['h'])}")
        else:
            print(f"   • Tamaño de paso variable (h_i)   : h_min = {res['h_min']:.8g} | h_max = {res['h_max']:.8g}")

        print("\n2. TABLA DE ÁREAS PARCIALES POR SUBINTERVALO:")
        print("   Fórmula elemental por tramo: A_i = (h_i / 2) * (y_i + y_{i+1})")
        print("-" * 102)
        print(f"{'Trapecio':<10} | {'Subintervalo [x_i, x_{i+1}]':<26} | {'Paso h_i':<14} | {'y_i':<14} | {'y_{i+1}':<14} | {'Área Parcial A_i':<16}")
        print("-" * 102)
        for s in res['subintervalos']:
            tramo_str = f"[{s['a_i']:.4g}, {s['b_i']:.4g}]"
            print(f"{s['i']:<10d} | {tramo_str:<26} | {self._fmt_celda(s['h_i'], 14)} | "
                  f"{self._fmt_celda(s['y_izq'], 14)} | {self._fmt_celda(s['y_der'], 14)} | {self._fmt_celda(s['area_i'], 16)}")
        print("-" * 102)

        if res['equidistante']:
            print("\n3. DESGLOSE DE LA FÓRMULA COMPUESTA DE CÁTEDRA:  A ≈ (h / 2) * (E + 2P + 2I)")
            print(f"   • Extremos (E = y_0 + y_{res['intervalos_n']})        : {self.y_nodos[0]:.8g} + {self.y_nodos[-1]:.8g} = {self._fmt_val(res['E'])}")
            print(f"   • Impares  (I = sum y_{{2k+1}})         : {self._fmt_val(res['I'])}  ->  2*I = {self._fmt_val(res['dos_I'])}")
            print(f"   • Pares    (P = sum y_{{2k}})           : {self._fmt_val(res['P'])}  ->  2*P = {self._fmt_val(res['dos_P'])}")
            print(f"   • Suma ponderada (E + 2P + 2I)        : {self._fmt_val(res['suma_ponderada'])}")
            print(f"   • Sustitución final                   : A = ({res['h']:.8g} / 2) * ({res['suma_ponderada']:.8g}) = {self._fmt_val(res['integral'])}")

        print("\n4. RESULTADOS FINALES, ERRORES Y RENDIMIENTO COMPUTACIONAL:")
        print(f"   • INTEGRAL APROXIMADA (TRAPECIOS)     : A ≈ {self._fmt_val(res['integral'])}")
        print(f"   • Tiempo de ejecución CPU             : {res['tiempo_cpu']:.4e} s ({res['tiempo_cpu'] * 1e6:.2f} µs)")

        if res['equidistante'] and res['intervalos_n'] % 2 == 0:
            res_simp = simpson_1_3_compuesto(self.x_nodos, self.y_nodos)
            dif_st = abs(res['integral'] - res_simp['integral'])
            print(f"   • Referencia Simpson 1/3 (n={res['intervalos_n']} par)    : A ≈ {self._fmt_val(res_simp['integral'])}")
            print(f"   • Diferencia |Trapecios - Simpson|    : {self._fmt_err(dif_st)}")

        if self.func_exacta is not None:
            i_exacta = self.integral_referencia(self.func_exacta, res['a'], res['b'])
            if i_exacta is not None:
                err_abs = abs(i_exacta - res['integral'])
                err_rel = (err_abs / abs(i_exacta)) * 100.0 if abs(i_exacta) > 1e-15 else 0.0
                print(f"   • INTEGRAL EXACTA DE REFERENCIA       : I = {self._fmt_val(i_exacta)}")
                print(f"   • Error Absoluto |I - A|              : {self._fmt_err(err_abs)}")
                print(f"   • Error Relativo Porcentual           : {self._fmt_err(err_rel)} %")
            else:
                print("   • [Aviso] No es posible calcular la integral exacta de referencia por singularidad interna.")
        print("=" * 102)

        if self._confirmar_grafico():
            graficar_trapecios(self.x_nodos, self.y_nodos, res['integral'], func_exacta=self.func_exacta)

        self._pausa_consola()

    # =========================================================================
    # 4. EJEMPLOS CONCRETOS Y DEMOSTRACIONES (CON PAUSA Y GRÁFICO OPCIONAL)
    # =========================================================================
    def ejecutar_ejemplos_concretos(self):
        """Submenú de ejemplos de las Guías 5 y 6 con salidas de alta precisión."""
        while True:
            print("\n" + "#" * 102)
            print("EJEMPLOS CONCRETOS DE CÁTEDRA Y DEMOSTRACIÓN DE CONVERGENCIA")
            print("#" * 102)
            print("  1. Lagrange (Guía 5 - Ej. 2): Censo de EE.UU. 1940-1990 (Estimar año 1965 y medir error)")
            print("  2. Lagrange (Guía 5 - Ej. 3): Tabla no equidistante en [0, 2] (Interpolar x=1 y x=0.45)")
            print("  3. Lagrange (Guía 5 - Ej. 4): Densidad experimental del Sodio a T = 275°C")
            print("  4. Trapecios (Guía 6 - Ej. 2 y 3): Integrales de tablas discretas con desglose de E, P, I")
            print("  5. Estudio de Convergencia O(h²) de Trapecios: Integrar f(x) = sin(x) en [0, π]")
            print("  6. Demostración de Validación ante Problemas No Solubles (Singularidades y Nodos Duplicados)")
            print("  0. Volver al Menú Principal")
            print("-" * 102)
            op = input("Seleccione un caso (0-6): ").strip()

            if op == '0':
                break

            elif op == '1':
                self.x_nodos = [1940.0, 1950.0, 1960.0, 1970.0, 1980.0, 1990.0]
                self.y_nodos = [132165.0, 151326.0, 179323.0, 203302.0, 226542.0, 249633.0]
                self.func_exacta = None
                self.origen_str = "Guía 5 Ej. 2 (Censo EE.UU.)"

                self.mostrar_tabla_activa()
                res = lagrange(self.x_nodos, self.y_nodos, 1965.0)
                pob_real = 189703.0
                err_abs = abs(pob_real - res['valor_interpolado'])
                err_rel = (err_abs / pob_real) * 100.0

                print("\nDESGLOSE DE INTERPOLACIÓN DE LAGRANGE EN x* = 1965:")
                for d in res['detalles_nodos']:
                    print(f"  Nodo {d['i']} (Año {d['x_i']:.0f}): y_i = {d['y_i']:10.2f} | "
                          f"L_{d['i']}(1965) = {d['L_i']:+12.8f} | Aporte = {d['aporte']:+14.4f}")
                print("-" * 85)
                print(f"• Suma de control de bases sum(L_i)  : {res['suma_bases_L']:.12f}")
                print(f"• Población interpolada (1965)       : {res['valor_interpolado']:,.4f} miles de hab.")
                print(f"• Población real censada (1965)      : {pob_real:,.4f} miles de hab.")
                print(f"• Error Absoluto                     : {self._fmt_err(err_abs)} miles de hab.")
                print(f"• Error Relativo Porcentual          : {self._fmt_err(err_rel)} %")
                print(f"• Tiempo de ejecución CPU            : {res['tiempo_cpu']:.4e} s ({res['tiempo_cpu']*1e6:.2f} µs)")

                if self._confirmar_grafico():
                    graficar_lagrange(self.x_nodos, self.y_nodos,
                                      puntos_evaluados=[(1965.0, res['valor_interpolado'])],
                                      titulo="- Censo EE.UU. (Año 1965)")
                self._pausa_consola()

            elif op == '2':
                self.x_nodos = [0.0, 0.4, 0.75, 1.5, 2.0]
                self.y_nodos = [1.0, 1.63246, 1.86603, 2.22474, 2.41421]
                self.func_exacta = None
                self.origen_str = "Guía 5 Ej. 3 (No equidistante)"

                self.mostrar_tabla_activa()
                r1 = lagrange(self.x_nodos, self.y_nodos, 1.0)
                r2 = lagrange(self.x_nodos, self.y_nodos, 0.45)

                print(f"\nPolinomio Interpolante: P_4(x) = {r1['polinomio_str']}")
                print(f"\nInciso 3.a) Evaluación en x* = 1.00:")
                for d in r1['detalles_nodos']:
                    print(f"  i={d['i']} (x={d['x_i']:<4.2f}): L_{d['i']}(1.00) = {d['L_i']:+12.8f} -> Aporte = {d['aporte']:+12.8f}")
                print(f"  -> Resultado P_4(1.00) = {self._fmt_val(r1['valor_interpolado'])} | CPU: {r1['tiempo_cpu']*1e6:.2f} µs")

                print(f"\nInciso 3.b) Evaluación en x* = 0.45:")
                for d in r2['detalles_nodos']:
                    print(f"  i={d['i']} (x={d['x_i']:<4.2f}): L_{d['i']}(0.45) = {d['L_i']:+12.8f} -> Aporte = {d['aporte']:+12.8f}")
                print(f"  -> Resultado P_4(0.45) = {self._fmt_val(r2['valor_interpolado'])} | CPU: {r2['tiempo_cpu']*1e6:.2f} µs")

                if self._confirmar_grafico():
                    graficar_lagrange(self.x_nodos, self.y_nodos,
                                      puntos_evaluados=[(1.0, r1['valor_interpolado']), (0.45, r2['valor_interpolado'])],
                                      titulo="- Guía 5 Ej. 3")
                self._pausa_consola()

            elif op == '3':
                self.x_nodos = [102.0, 245.0, 327.0, 423.0, 565.0]
                self.y_nodos = [0.564642, 0.644218, 0.717356, 0.783327, 0.853329]
                self.func_exacta = None
                self.origen_str = "Guía 5 Ej. 4 (Densidad del Sodio)"

                self.mostrar_tabla_activa()
                res = lagrange(self.x_nodos, self.y_nodos, 275.0)
                print(f"\nPolinomio P_4(T) = {res['polinomio_str']}\n")
                for d in res['detalles_nodos']:
                    print(f"  Nodo {d['i']} (T={d['x_i']:5.1f}°C): y_i={d['y_i']:.6f} | L_{d['i']}(275)={d['L_i']:+12.8f} | Aporte={d['aporte']:+12.8f}")
                print("-" * 85)
                print(f"• Densidad interpolada a T = 275°C : {self._fmt_val(res['valor_interpolado'])}")
                print(f"• Suma de bases sum(L_i)           : {res['suma_bases_L']:.12f}")
                print(f"• Tiempo de ejecución CPU          : {res['tiempo_cpu']:.4e} s ({res['tiempo_cpu']*1e6:.2f} µs)")

                if self._confirmar_grafico():
                    graficar_lagrange(self.x_nodos, self.y_nodos,
                                      puntos_evaluados=[(275.0, res['valor_interpolado'])],
                                      titulo="- Densidad del Sodio a 275°C")
                self._pausa_consola()

            elif op == '4':
                t_ej2 = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
                y_ej2 = [0.0, 0.15, 0.30, 0.55, 0.73, 0.81]
                r_ej2 = trapecios_compuesto(t_ej2, y_ej2)

                print("\n" + "=" * 95)
                print("CASO A: GUÍA 6 - EJERCICIO 2 (Tabla en [0.0, 0.5] con paso h = 0.1, n = 5)")
                print("=" * 95)
                print(f"• Extremos E = {r_ej2['E']:.6f} | Pares P = {r_ej2['P']:.6f} (2P = {r_ej2['dos_P']:.6f}) | Impares I = {r_ej2['I']:.6f} (2I = {r_ej2['dos_I']:.6f})")
                print(f"• Sustitución: A = (0.1 / 2) * ({r_ej2['E']:.6f} + {r_ej2['dos_P']:.6f} + {r_ej2['dos_I']:.6f}) = {self._fmt_val(r_ej2['integral'])}")
                print(f"• Tiempo CPU : {r_ej2['tiempo_cpu']:.4e} s ({r_ej2['tiempo_cpu']*1e6:.2f} µs)")

                x_ej3 = [12.0, 13.0, 14.0, 15.0, 16.0, 17.0]
                y_ej3 = [0.96262, 0.94718, 0.93108, 0.92221, 0.91181, 0.90151]
                r_ej3 = trapecios_compuesto(x_ej3, y_ej3)

                print("\n" + "=" * 95)
                print("CASO B: GUÍA 6 - EJERCICIO 3 (Tabla en [12.0, 17.0] con paso h = 1.0, n = 5)")
                print("=" * 95)
                print(f"• Extremos E = {r_ej3['E']:.6f} | Pares P = {r_ej3['P']:.6f} (2P = {r_ej3['dos_P']:.6f}) | Impares I = {r_ej3['I']:.6f} (2I = {r_ej3['dos_I']:.6f})")
                print(f"• Sustitución: A = (1.0 / 2) * ({r_ej3['E']:.6f} + {r_ej3['dos_P']:.6f} + {r_ej3['dos_I']:.6f}) = {self._fmt_val(r_ej3['integral'])}")
                print(f"• Tiempo CPU : {r_ej3['tiempo_cpu']:.4e} s ({r_ej3['tiempo_cpu']*1e6:.2f} µs)")

                self.x_nodos, self.y_nodos, self.func_exacta = x_ej3, y_ej3, None
                self.origen_str = "Guía 6 Ej. 3"

                if self._confirmar_grafico("¿Desea visualizar el gráfico de Trapecios del Ejercicio 3? (s/n) [Enter = No]: "):
                    graficar_trapecios(x_ej3, y_ej3, r_ej3['integral'], titulo="- Guía 6 Ej. 3")
                self._pausa_consola()

            elif op == '5':
                print("\n" + "=" * 105)
                print("ESTUDIO DE CONVERGENCIA O(h²): INTEGRAL DE f(x) = sin(x) EN [0, π] (Valor Exacto = 2.0000000000)")
                print("=" * 105)
                print(f"{'n (Trapecios)':<14} | {'Paso h':<12} | {'Aprox. Trapecios':<16} | {'Error Absoluto':<15} | {'Error Rel (%)':<15} | {'Reducción':<10} | {'CPU (µs)':<10}")
                print("-" * 105)

                err_prev = None
                pasos_h, errores = [], []
                for n in (2, 4, 8, 16, 32, 64, 128):
                    xs = np.linspace(0.0, math.pi, n + 1).tolist()
                    ys = [math.sin(xi) for xi in xs]
                    res = trapecios_compuesto(xs, ys)
                    err_abs = abs(2.0 - res['integral'])
                    err_rel = (err_abs / 2.0) * 100.0
                    ratio = f"{err_prev / err_abs:.2f}x" if (err_prev is not None and err_abs > 0) else "---"
                    t_us = res['tiempo_cpu'] * 1e6
                    print(f"{n:<14d} | {res['h']:<12.6f} | {res['integral']:<16.10f} | {err_abs:<15.6e} | {err_rel:<15.6e} | {ratio:<10} | {t_us:<10.2f}")
                    pasos_h.append(res['h'])
                    errores.append(err_abs)
                    err_prev = err_abs

                print("=" * 105)
                print("FUNDAMENTO TEÓRICO: El error global de Trapecios es E_T = -((b-a)/12) * h² * f''(ξ).")
                print("Al duplicar n (reducir h a la mitad), el error se divide por 2² = 4.00x en cada fila.")

                if self._confirmar_grafico("¿Desea abrir el gráfico de convergencia O(h²)? (s/n) [Enter = No]: "):
                    graficar_convergencia_trapecios(pasos_h, errores, math.sin, 0.0, math.pi)
                self._pausa_consola()

            elif op == '6':
                print("\n" + "=" * 95)
                print("PRUEBA DE ROBUSTEZ ANTE CASOS NO SOLUBLES O MAL CONDICIONADOS")
                print("=" * 95)

                print("\n[Caso 1] Intento de interpolar por Lagrange con abscisas repetidas X = [1.0, 2.0, 2.0, 4.0]:")
                try:
                    lagrange([1.0, 2.0, 2.0, 4.0], [3.0, 5.0, 8.0, 10.0], 2.5)
                except Exception as e:
                    print(f"  -> Capturado correctamente: {e}")

                print("\n[Caso 2] Intento de integrar f(x) = 1/x en [0, 2] (Asíntota vertical en x = 0):")
                ok, _, msg = self._evaluar_punto_seguro(lambda x: 1.0 / x, 0.0)
                if not ok:
                    print(f"  -> Capturado correctamente: {msg}")

                print("\n[Caso 3] Intento de evaluar f(x) = sqrt(x) en x = -2.0 (Dominio complejo):")
                ok, _, msg = self._evaluar_punto_seguro(lambda x: math.sqrt(x), -2.0)
                if not ok:
                    print(f"  -> Capturado correctamente: {msg}")

                print("=" * 95)
                self._pausa_consola()
            else:
                print("Opción no válida.")