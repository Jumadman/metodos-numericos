"""
Módulo: aritmetica_flotante.py
Descripción: Emulador de aritmética de punto flotante en base 10 con k dígitos
             significativos normalizados (redondeo simétrico y truncamiento).
             Herramienta base para la Guía de Laboratorio N° 2.
"""

import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN


def error_absoluto(p_exacto, p_aprox):
    """Calcula el error absoluto: E_abs = |p - p*|."""
    return abs(p_exacto - p_aprox)


def error_relativo(p_exacto, p_aprox):
    """Calcula el error relativo: E_rel = |p - p*| / |p|."""
    if abs(p_exacto) < 1e-15:
        return float('inf') if abs(p_aprox) > 1e-15 else 0.0
    return abs(p_exacto - p_aprox) / abs(p_exacto)


def normalizar_k_digitos(numero, k_digitos=3, modo='redondeo'):
    """
    Representa un número en punto flotante normalizado a k dígitos:
        +/- 0.d1 d2 ... dk * 10^n  (con d1 != 0)
    Aplica redondeo (ROUND_HALF_UP) o truncamiento (ROUND_DOWN).
    """
    if numero == 0 or math.isnan(numero) or math.isinf(numero):
        return float(numero)

    signo = -1 if numero < 0 else 1
    num_abs = abs(numero)

    # Determinar el exponente decimal n tal que 0.1 <= mantisa < 1.0
    # Ejemplo: 133.921 -> exponente n = 3 -> mantisa = 0.133921
    exp_n = math.floor(math.log10(num_abs)) + 1
    mantisa_exacta = num_abs / (10 ** exp_n)

    # Escalar la mantisa para aislar los k dígitos significativos
    factor_k = Decimal(str(10 ** k_digitos))
    mantisa_dec = Decimal(str(mantisa_exacta)) * factor_k

    modo_round = ROUND_HALF_UP if modo == 'redondeo' else ROUND_DOWN
    mantisa_acotada = mantisa_dec.quantize(Decimal('1'), rounding=modo_round)

    resultado = float(mantisa_acotada / factor_k) * (10 ** exp_n) * signo
    return resultado


def operar_flotante(operando1, operando2, operacion, k_digitos=3, modo='redondeo', normalizar_entradas=True):
    """
    Realiza una operación aritmética (+, -, *, /) simulando registros de k dígitos:
    1. Normaliza los operandos de entrada (si normalizar_entradas=True).
    2. Ejecuta la operación elemental.
    3. Normaliza y acota el resultado intermedio a k dígitos.
    """
    op1 = normalizar_k_digitos(operando1, k_digitos, modo) if normalizar_entradas else operando1
    op2 = normalizar_k_digitos(operando2, k_digitos, modo) if normalizar_entradas else operando2

    if operacion == '+':
        res_crudo = op1 + op2
    elif operacion == '-':
        res_crudo = op1 - op2
    elif operacion == '*':
        res_crudo = op1 * op2
    elif operacion == '/':
        if abs(op2) < 1e-15:
            raise ZeroDivisionError("División por cero en aritmética de punto flotante.")
        res_crudo = op1 / op2
    else:
        raise ValueError(f"Operación no válida: {operacion}")

    return normalizar_k_digitos(res_crudo, k_digitos, modo)