import math

class ProblemaManning:
    """Modelo matemático del canal trapezoidal con validación estricta de parámetros."""
    def __init__(self, Q=45.0, B=1.5, z=3.5, S0=0.0008, n=0.028, H_max=5.0):
        # Validación de seguridad para evitar divisiones por cero o geometrías nulas
        self.Q = Q if Q > 0 else 45.0
        self.B = B if B > 0 else 1.5
        self.z = z if z >= 0 else 3.5
        self.S0 = S0 if S0 > 0 else 0.0008
        self.n = n if n > 0 else 0.028
        self.H_max = H_max if H_max > 0 else 5.0

        self.K = math.sqrt(self.S0) / self.n
        self.factor_talud = math.sqrt(1.0 + self.z**2)

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
                    print(f"  [Aviso] El valor debe ser > 0. Se usará el valor por defecto: {valor_defecto}")
                    return valor_defecto
                elif not estricto_positivo and val < 0:
                    print(f"  [Aviso] El valor no puede ser negativo. Se usará el valor por defecto: {valor_defecto}")
                    return valor_defecto
                return val
            except ValueError:
                print(f"  [Aviso] Entrada inválida. Se usará el valor por defecto: {valor_defecto}")
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
        area = self.B * x + self.z * (x**2)
        perimetro = self.B + 2.0 * x * self.factor_talud

        if abs(perimetro) < 1e-12:
            return float('inf')

        num = math.copysign(abs(area)**(5.0 / 3.0), area)
        den = (abs(perimetro))**(2.0 / 3.0)
        return self.K * (num / den) - self.Q

    def g(self, x):
        """Función de punto fijo x = g(x)."""
        perimetro = self.B + 2.0 * x * self.factor_talud
        denominador_area = self.B + self.z * x

        if perimetro <= 0 or abs(denominador_area) < 1e-12:
            return x

        termino_caudal = (self.Q / self.K) * (perimetro**(2.0 / 3.0))
        area_requerida = termino_caudal**(3.0 / 5.0)
        return area_requerida / denominador_area

    def validar_intervalo_fisico(self, a, b):
        if a >= 0.0 and b <= self.H_max:
            return True, "VÁLIDA FÍSICAMENTE (Tirante admisible)"
        elif b <= 0.0 or a < 0.0:
            return False, "DESCARTADA (Tirante negativo)"
        else:
            return False, f"DESCARTADA (Desborde > {self.H_max}m)"