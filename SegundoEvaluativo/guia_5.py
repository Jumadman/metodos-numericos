"""
Módulo: guia_5.py
Descripción: Contiene los modelos matemáticos y la resolución guiada e interactiva
             de los Ejercicios 1, 2, 3 y 4 de la Guía de Laboratorio N° 5 (2026).
"""

import math
from SegundoEvaluativo.metodos_interpolacion import lagrange 

#ejercicio 2
x = [1940, 1950, 1960, 1970, 1980, 1990]
y = [132165, 151326, 179323, 203302, 226542, 249633]
input("Presione Enter para ejecutar la interpolación de Lagrange para el año 1965...")
result=lagrange(x, y, 1965)
exacto= 189703
errorP= abs(exacto-result['valor_interpolado'])/exacto*100

print(f"Interpolación de Lagrange para el año 1965: {result['valor_interpolado']:.2f}")
print(f"Error porcentual: {errorP:.2f}%")
print(f"Tiempo de ejecución: {result['tiempo_ejecucion']:.6f} segundos")