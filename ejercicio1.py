import math
from orquestador import iniciar_resolucion

def f_tanque(h, R, V_objetivo):
    """
    Función objetivo del tanque esférico.
    f(h) = Volumen_calculado - V_objetivo
    """
    return math.pi * (h**2) * ((3 * R - h) / 3.0) - V_objetivo

def main():
    print("=== GUÍA PRÁCTICA: PROBLEMA DEL TANQUE ===")
    
    # Pedido de constantes del problema (fuera de la lógica del método)
    R_tanque = float(input("Ingresa el Radio del tanque (m): "))
    V_deseado = float(input("Ingresa el Volumen deseado (m^3): "))
    
    # Iniciar la resolución orquestada
    iniciar_resolucion(
        f_tanque,           
        R_tanque,           
        V_deseado,          
        titulo="Cálculo de Profundidad - Tanque Esférico"
    )
    
    input("\nPresiona Enter para finalizar...")

if __name__ == "__main__":
    main()