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

        self.K = math.sqrt(self.S0) / self.n
        self.factor_talud = math.sqrt(1.0 + self.z**2)

        # Metadatos para el visualizador y el tanteo
        self.nombre = "Ecuación de Manning"
        self.etiqueta_x = "Tirante x (m)"
        self.dominio_sugerido = (-6.0, 6.5)
        self.paso_sugerido = 2.5
        self.tiene_restriccion_fisica = True

    @classmethod
    def configurar_desde_consola(cls):
        print("\n" + "=" * 80)
        print("CONFIGURACIÓN DE PARÁMETROS - CANAL HIDRÁULICO DE MANNING")
        print("(Presione Enter para usar valores por defecto. Valores <= 0 no son válidos)")
        print("=" * 80)

        def pedir_positivo(mensaje, valor_defecto, estricto_positivo=True):
            entrada = input(f"{mensaje} (defecto {valor_defecto}): ").strip()
            if not entrada:
                return valor_defecto
            try:
                val = float(entrada)
                if estricto_positivo and val <= 0:
                    print(f"  [Aviso] El valor debe ser > 0. Se usará el defecto: {valor_defecto}")
                    return valor_defecto
                elif not estricto_positivo and val < 0:
                    print(f"  [Aviso] El valor no puede ser negativo. Se usará el defecto: {valor_defecto}")
                    return valor_defecto
                return val
            except ValueError:
                print(f"  [Aviso] Entrada inválida. Se usará el defecto: {valor_defecto}")
                return valor_defecto

        q = pedir_positivo("Caudal objetivo Q [m^3/s]", 45.0)
        b = pedir_positivo("Ancho de base B [m]", 1.5)
        z = pedir_positivo("Talud lateral z", 3.5, estricto_positivo=False)
        s0 = pedir_positivo("Pendiente longitudinal S0", 0.0008)
        n = pedir_positivo("Rugosidad de Manning n", 0.028)
        h_max = pedir_positivo("Altura máxima H_max [m]", 5.0)

        return cls(Q=q, B=b, z=z, S0=s0, n=n, H_max=h_max)

    def f(self, x):
        """Ecuación f(x) = Q_calculado - Q_objetivo = 0."""
        try:
            area = self.B * x + self.z * (x**2)
            perimetro = self.B + 2.0 * x * self.factor_talud

            if abs(perimetro) < 1e-12:
                return float('inf')

            num = math.copysign(abs(area)**(5.0 / 3.0), area)
            den = (abs(perimetro))**(2.0 / 3.0)
            return self.K * (num / den) - self.Q
        except Exception:
            return float('nan')

    def g(self, x):
        """Función de punto fijo x = g(x)."""
        try:
            perimetro = self.B + 2.0 * x * self.factor_talud
            denominador_area = self.B + self.z * x

            if perimetro <= 0 or abs(denominador_area) < 1e-12:
                return x

            termino_caudal = (self.Q / self.K) * (perimetro**(2.0 / 3.0))
            area_requerida = termino_caudal**(3.0 / 5.0)
            return area_requerida / denominador_area
        except Exception:
            return x

    def calibrar_g(self, x0):
        """Manning ya posee su despeje analítico g(x), no requiere autocalibración."""
        pass

    def validar_intervalo_fisico(self, a, b):
        if a >= 0.0 and b <= self.H_max:
            return True, "VÁLIDA FÍSICAMENTE (Tirante admisible)"
        elif b <= 0.0 or a < 0.0:
            return False, "DESCARTADA (Tirante negativo)"
        else:
            return False, f"DESCARTADA (Desborde > {self.H_max}m)"


class ProblemaPersonalizado:
    """
    Permite ingresar por consola cualquier función f(x) y opcionalmente g(x),
    evaluándolas de forma segura sin errores de dominio o desbordamiento.
    """
    ENTORNO_MATEMATICO = {
        'math': math,
        'sin': math.sin, 'sen': math.sin,
        'cos': math.cos, 'tan': math.tan,
        'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
        'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        'exp': math.exp, 'ln': math.log, 'log': math.log, 'log10': math.log10,
        'sqrt': math.sqrt, 'abs': abs,
        'pi': math.pi, 'e': math.e,
        'cbrt': lambda u: math.copysign(abs(u)**(1.0 / 3.0), u)
    }

    def __init__(self, expr_f, expr_g="", x_min=-10.0, x_max=10.0, paso=1.0, val_min=None, val_max=None):
        self.expr_f_original = expr_f
        self.expr_f = self._limpiar_expresion(expr_f)
        self.expr_g_original = expr_g.strip()
        self.expr_g = self._limpiar_expresion(expr_g) if self.expr_g_original else ""

        self.nombre = f"f(x) = {expr_f}"
        self.etiqueta_x = "Variable x"
        self.dominio_sugerido = (x_min, x_max)
        self.paso_sugerido = paso

        self.val_min = val_min
        self.val_max = val_max
        self.tiene_restriccion_fisica = (val_min is not None) or (val_max is not None)
        self.H_max = val_max if val_max is not None else x_max

        # Parámetro de relajación automático en caso de que el usuario no ingrese g(x)
        self.alfa_auto = -0.1

    @staticmethod
    def _limpiar_expresion(expr):
        """Convierte notación matemática común (^) a sintaxis válida de Python (**)."""
        return expr.replace("^", "**").strip()

    @classmethod
    def configurar_desde_consola(cls):
        print("\n" + "=" * 85)
        print("CARGA DE FUNCIÓN PERSONALIZADA POR CONSOLA")
        print("Operadores admitidos: +, -, *, /, ^ (potencia), sqrt(x), cbrt(x), ln(x), exp(x),")
        print("                      sin(x), cos(x), tan(x), pi, e")
        print("Ejemplos:")
        print("  • Tanque esférico : pi * x^2 * (9 - x)/3 - 30")
        print("  • Impresoras      : 8*x + 0.3*x^2 - 0.0013*x^3 - 372")
        print("  • Utilidad (Ej.3) : 5*x - 200*ln(400/(500 - x)) - 1000")
        print("=" * 85)

        while True:
            expr_f = input("\n1. Ingrese la expresión de f(x) = 0: ").strip()
            if not expr_f:
                expr_f = "x^3 - x - 1"
                print(f"   -> Se usará función de ejemplo: f(x) = {expr_f}")
            
            # Prueba de sintaxis
            instancia_prueba = cls(expr_f)
            try:
                compile(instancia_prueba.expr_f, "<string>", "eval")
                break
            except SyntaxError:
                print("   [Error de sintaxis] Verifique paréntesis y operadores (ej. use 3*x en lugar de 3x).")

        print("\n2. Función de Punto Fijo x = g(x) para el Método de Steffensen:")
        print("   (Opcional: presione Enter para generar una función g(x) contractiva automática)")
        expr_g = input("   Ingrese g(x): ").strip()
        if expr_g:
            try:
                compile(cls._limpiar_expresion(expr_g), "<string>", "eval")
            except SyntaxError:
                print("   [Aviso] Sintaxis inválida en g(x). Se utilizará generación automática.")
                expr_g = ""

        print("\n3. Configuración del dominio de exploración para Tanteo:")
        try:
            in_xmin = input("   Límite inferior de búsqueda x_inicio (Enter para -10.0): ").strip()
            x_min = float(in_xmin) if in_xmin else -10.0

            in_xmax = input("   Límite superior de búsqueda x_fin (Enter para 10.0): ").strip()
            x_max = float(in_xmax) if in_xmax else 10.0
            if x_max <= x_min:
                x_max = x_min + 10.0

            ancho = x_max - x_min
            paso_def = round(max(ancho / 10.0, 0.5), 2)
            in_paso = input(f"   Incremento sugerido Δx (Enter para {paso_def}): ").strip()
            paso = float(in_paso) if in_paso and float(in_paso) > 0 else paso_def
        except ValueError:
            x_min, x_max, paso = -10.0, 10.0, 1.0

        print("\n4. Restricción de dominio válido / físico (para descarte de raíces):")
        print("   (Presione Enter en ambos si desea aceptar todas las raíces reales sin descarte)")
        val_min, val_max = None, None
        try:
            in_vmin = input("   Mínimo valor admisible de x (ej. 0 para magnitudes positivas, Enter = sin límite): ").strip()
            if in_vmin:
                val_min = float(in_vmin)
            in_vmax = input("   Máximo valor admisible de x (Enter = sin límite): ").strip()
            if in_vmax:
                val_max = float(in_vmax)
        except ValueError:
            val_min, val_max = None, None

        return cls(expr_f, expr_g, x_min, x_max, paso, val_min, val_max)

    def f(self, x):
        """Evalúa f(x) de manera segura capturando errores de dominio matemático."""
        entorno = dict(self.ENTORNO_MATEMATICO)
        entorno['x'] = float(x)
        try:
            res = eval(self.expr_f, {"__builtins__": {}}, entorno)
            if isinstance(res, complex):
                return float('nan')
            return float(res)
        except ZeroDivisionError:
            return float('inf')
        except (ValueError, OverflowError, Exception):
            return float('nan')

    def calibrar_g(self, x0):
        """
        Si el usuario no proporcionó g(x), calibra g(x) = x - alfa * f(x)
        alrededor de la semilla x0 para garantizar |g'(x0)| ≈ 0.5 < 1.
        """
        if not self.expr_g:
            h = 1e-5
            f_mas = self.f(x0 + h)
            f_menos = self.f(x0 - h)
            if not (math.isnan(f_mas) or math.isnan(f_menos) or math.isinf(f_mas) or math.isinf(f_menos)):
                df_x0 = (f_mas - f_menos) / (2.0 * h)
                if abs(df_x0) > 1e-10:
                    # Con alfa = 0.5 / f'(x0), la derivada g'(x0) = 1 - alfa*f'(x0) = 0.5 (< 1)
                    self.alfa_auto = 0.5 / df_x0
                    print(f"\n[Autocalibración Punto Fijo] Se construyó g(x) = x - ({self.alfa_auto:.6g}) * f(x)")

    def g(self, x):
        """Evalúa g(x) definida por el usuario o la fórmula de relajación autocalibrada."""
        if self.expr_g:
            entorno = dict(self.ENTORNO_MATEMATICO)
            entorno['x'] = float(x)
            try:
                res = eval(self.expr_g, {"__builtins__": {}}, entorno)
                if isinstance(res, complex) or math.isnan(res) or math.isinf(res):
                    return float(x)
                return float(res)
            except Exception:
                return float(x)
        else:
            fx = self.f(x)
            if math.isnan(fx) or math.isinf(fx):
                return float(x)
            return float(x) - self.alfa_auto * fx

    def validar_intervalo_fisico(self, a, b):
        if self.val_min is not None and b <= self.val_min:
            return False, f"DESCARTADA (Menor al límite admisible x < {self.val_min})"
        if self.val_max is not None and a >= self.val_max:
            return False, f"DESCARTADA (Supera el límite admisible x > {self.val_max})"
        return True, "RAÍZ VÁLIDA (Dentro del dominio admisible)"