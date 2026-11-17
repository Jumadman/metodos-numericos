"""
Módulo: controlador_funciones.py
Descripción: Contiene el modelo del Trabajo Evaluativo (Canal Hidráulico de Manning)
             y la clase ProblemaPersonalizado para evaluar cualquier función ingresada por teclado.
"""

import math


class ProblemaManning:
    """Modelo matemático del canal trapezoidal con validación estricta de parámetros."""
    def __init__(self, Q=45.0, B=1.5, z=3.5, S0=0.0008, n=0.028, H_max=5.0):
        self.Q = Q if Q > 0 else 45.0
        self.B = B if B > 0 else 1.5
        self.z = z if z >= 0 else 3.5
        self.S0 = S0 if S0 > 0 else 0.0008
        self.n = n if n > 0 else 0.028
        self.H_max = H_max if H_max > 0 else 5.0
        self.val_min = 0.0

        self.K = math.sqrt(self.S0) / self.n
        self.factor_talud = math.sqrt(1.0 + self.z ** 2)

        self.nombre = "Ecuación de Manning"
        self.etiqueta_x = "Tirante de agua x [m]"
        self.dominio_sugerido = (-6.0, 6.5)
        self.paso_sugerido = 2.5
        self.tol_sugerida = 0.001
        self.tiene_restriccion_fisica = True

    @classmethod
    def configurar_desde_consola(cls):
        print("\n" + "=" * 80)
        print("CONFIGURACIÓN DE PARÁMETROS - CANAL HIDRÁULICO DE MANNING")
        print("(Presione Enter para usar valores por defecto. Valores <= 0 no son válidos)")
        print("=" * 80)

        def pedir_positivo(mensaje, valor_defecto, estricto=True):
            ent = input(f"{mensaje} (defecto {valor_defecto}): ").strip()
            if not ent:
                return valor_defecto
            try:
                v = float(ent)
                if (estricto and v <= 0) or (not estricto and v < 0):
                    print(f"  [Aviso] Valor fuera de rango. Se usará el defecto: {valor_defecto}")
                    return valor_defecto
                return v
            except ValueError:
                print(f"  [Aviso] Entrada inválida. Se usará el defecto: {valor_defecto}")
                return valor_defecto

        return cls(
            Q=pedir_positivo("Caudal objetivo Q [m^3/s]", 45.0),
            B=pedir_positivo("Ancho de base B [m]", 1.5),
            z=pedir_positivo("Talud lateral z", 3.5, estricto=False),
            S0=pedir_positivo("Pendiente longitudinal S0", 0.0008),
            n=pedir_positivo("Rugosidad de Manning n", 0.028),
            H_max=pedir_positivo("Altura máxima H_max [m]", 5.0)
        )

    def f(self, x):
        try:
            area = self.B * x + self.z * (x ** 2)
            perimetro = self.B + 2.0 * x * self.factor_talud
            if abs(perimetro) < 1e-12:
                return float('inf')
            num = math.copysign(abs(area) ** (5.0 / 3.0), area)
            den = (abs(perimetro)) ** (2.0 / 3.0)
            return self.K * (num / den) - self.Q
        except Exception:
            return float('nan')

    def g(self, x):
        try:
            perimetro = self.B + 2.0 * x * self.factor_talud
            den_area = self.B + self.z * x
            if perimetro <= 0 or abs(den_area) < 1e-12:
                return x
            termino_caudal = (self.Q / self.K) * (perimetro ** (2.0 / 3.0))
            return (termino_caudal ** (3.0 / 5.0)) / den_area
        except Exception:
            return x

    def calibrar_g(self, x0):
        pass

    def validar_intervalo_fisico(self, a, b):
        if a >= 0.0 and b <= self.H_max:
            return True, "VÁLIDA FÍSICAMENTE (Tirante admisible)"
        elif b <= 0.0 or a < 0.0:
            return False, "DESCARTADA (Tirante negativo)"
        return False, f"DESCARTADA (Desborde > {self.H_max}m)"


class ProblemaPersonalizado:
    """Permite ingresar por consola cualquier función f(x) y opcionalmente g(x)."""
    ENTORNO = {
        'math': math, 'sin': math.sin, 'sen': math.sin, 'cos': math.cos, 'tan': math.tan,
        'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'exp': math.exp,
        'ln': math.log, 'log': math.log, 'log10': math.log10, 'sqrt': math.sqrt,
        'abs': abs, 'pi': math.pi, 'e': math.e,
        'cbrt': lambda u: math.copysign(abs(u) ** (1.0 / 3.0), u)
    }

    def __init__(self, expr_f, expr_g='', x_min=-10.0, x_max=10.0, paso=1.0, val_min=None, val_max=None):
        self.expr_f = expr_f.replace('^', '**').strip()
        self.expr_g = expr_g.replace('^', '**').strip() if expr_g.strip() else ''
        self.nombre = f"f(x) = {expr_f}"
        self.etiqueta_x = "Variable x"
        self.dominio_sugerido = (x_min, x_max)
        self.paso_sugerido = paso
        self.tol_sugerida = 0.001
        self.val_min, self.val_max = val_min, val_max
        self.tiene_restriccion_fisica = (val_min is not None) or (val_max is not None)
        self.H_max = val_max if val_max is not None else x_max
        self.alfa_auto = -0.1

    @classmethod
    def configurar_desde_consola(cls):
        print("\n" + "=" * 85)
        print("MODO LIBRE: CARGA DE FUNCIÓN PERSONALIZADA POR CONSOLA")
        print("Operadores: +, -, *, /, ^, sqrt(x), cbrt(x), ln(x), exp(x), sin(x), cos(x), pi, e")
        print("=" * 85)
        while True:
            ef = input("1. Ingrese f(x) = 0 (Enter para x^3 - x - 1): ").strip() or "x^3 - x - 1"
            try:
                compile(ef.replace('^', '**'), "<string>", "eval")
                break
            except SyntaxError:
                print("   [Error de sintaxis] Revise paréntesis y multiplicaciones (ej. 2*x).")

        eg = input("2. Ingrese g(x) para Punto Fijo/Aitken (Enter = autocalibrar): ").strip()
        xmin = float(input("3. Límite inferior x_inicio (Enter = -10.0): ").strip() or -10.0)
        xmax = float(input("4. Límite superior x_fin (Enter = 10.0): ").strip() or 10.0)
        paso_def = round(max((xmax - xmin) / 10.0, 0.5), 2)
        paso = float(input(f"5. Incremento Δx para Tanteo (Enter = {paso_def}): ").strip() or paso_def)
        vmin_s = input("6. Mínimo admisible físico (Enter = sin límite): ").strip()
        vmax_s = input("7. Máximo admisible físico (Enter = sin límite): ").strip()
        return cls(ef, eg, xmin, xmax, paso, float(vmin_s) if vmin_s else None, float(vmax_s) if vmax_s else None)

    def f(self, x):
        try:
            r = eval(self.expr_f, {'__builtins__': {}}, dict(self.ENTORNO, x=float(x)))
            return float('nan') if isinstance(r, complex) else float(r)
        except ZeroDivisionError:
            return float('inf')
        except Exception:
            return float('nan')

    def calibrar_g(self, x0):
        if not self.expr_g:
            h = 1e-5
            df = (self.f(x0 + h) - self.f(x0 - h)) / (2.0 * h)
            if not math.isnan(df) and abs(df) > 1e-10:
                self.alfa_auto = 0.5 / df
                print(f"\n[Autocalibración Punto Fijo] Se construyó g(x) = x - ({self.alfa_auto:.6g}) * f(x)")

    def g(self, x):
        if self.expr_g:
            try:
                r = eval(self.expr_g, {'__builtins__': {}}, dict(self.ENTORNO, x=float(x)))
                return float(x) if isinstance(r, complex) or math.isnan(r) else float(r)
            except Exception:
                return float(x)
        fx = self.f(x)
        return float(x) if math.isnan(fx) or math.isinf(fx) else float(x) - self.alfa_auto * fx

    def validar_intervalo_fisico(self, a, b):
        if self.val_min is not None and b <= self.val_min:
            return False, f"DESCARTADA (x < {self.val_min})"
        if self.val_max is not None and a >= self.val_max:
            return False, f"DESCARTADA (x > {self.val_max})"
        return True, "RAÍZ VÁLIDA"